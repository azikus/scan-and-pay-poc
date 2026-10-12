import CryptoKit
import SwiftUI

@MainActor final class ScanSession: ObservableObject {
  enum Phase: Equatable {
    case capture, crop, preview, uploading, queued, reading, review, recovery, failed
  }
  @Published var phase: Phase = .capture
  @Published var image: UIImage?
  @Published var originalImage: UIImage?
  @Published var draft: PaymentDraft?
  @Published var response: JSONValue?
  @Published var message: String?
  @Published var checked = false
  @Published var saving = false
  @Published var complete = false
  @Published var address = ""
  @Published var hotspotAddress = ""
  @Published private(set) var reconnecting = false
  @Published private(set) var connectionStatus: String?
  private(set) var connectionAttempts = [[String: String]]()
  @Published var token = TokenStore.read()
  private(set) var pending: PendingScan?
  private var task: Task<Void, Never>?
  private var generation = UUID()
  let fixtureMode: Bool
  private let clientSession: URLSession?
  private let pendingFile: URL
  private let defaults: UserDefaults
  init(
    fixtureMode: Bool = false, clientSession: URLSession? = nil,
    pendingFile: URL = PendingStore.file, defaults: UserDefaults = .standard
  ) {
    self.defaults = defaults
    self.clientSession = clientSession
    self.pendingFile = pendingFile
    self.fixtureMode = fixtureMode
    // Migrate the working Wi-Fi URL, never the former USB or hosted route.
    hotspotAddress =
      ["backendHotspotURL", "backendWiFiURL", "backendURL"]
      .compactMap { defaults.string(forKey: $0) }.first(where: Self.isHotspotAddress) ?? ""
    address = hotspotAddress
    defaults.set(hotspotAddress, forKey: "backendHotspotURL")
    defaults.set(address, forKey: "backendURL")
    defaults.removeObject(forKey: "backendCableURL")
    defaults.removeObject(forKey: "backendWiFiURL")
    if !fixtureMode, let stored = PendingStore.read(from: pendingFile),
      let image = UIImage(data: stored.image)
    {
      pending = stored
      self.image = image
      originalImage = image
      phase = .recovery
      if let data = stored.response,
        let result = try? JSONDecoder().decode(JSONValue.self, from: data)
      {
        accept(result, data: data)
        if let values = stored.editedValues {
          draft?.restore(
            values: values, selectedID: stored.selectedCandidateID,
            editedFieldIDs: stored.editedFieldIDs)
        }
        if stored.confirmationBody != nil {
          phase = .recovery
          message =
            "Retry the original confirmation to finish this scan. Its saved values are unchanged."
        }
      }
    }
    #if DEBUG
      if !fixtureMode {
        do {
          if let setup = try DevelopmentConnection.consume() {
            Task { await setup.apply(to: self) }
          }
        } catch {
          message = "Connection setup could not be read. Open Connection settings."
        }
      }
    #endif
  }
  var processing: Bool { [.uploading, .queued, .reading].contains(phase) }
  var confirmationValues: JSONValue? {
    if let body = pending?.confirmationBody {
      return try? JSONDecoder().decode(JSONValue.self, from: body)
    }
    return draft?.confirmation
  }
  var processingTitle: String {
    phase == .uploading
      ? "Uploading image…" : phase == .queued ? "Waiting to read…" : "Reading payment details…"
  }
  func configure(address: String, token: String) throws {
    _ = try BackendClient(address: address, token: token, session: clientSession)
    try TokenStore.save(token)
    self.address = address
    self.token = token
    defaults.set(address, forKey: "backendURL")
  }
  // The app cannot identify the Wi-Fi SSID. Accept a local Mac address, with one
  // saved endpoint for the Personal Hotspot workflow; no USB/cloud fallback.
  static func isHotspotAddress(_ address: String) -> Bool {
    guard let url = URL(string: address), url.scheme == "http", let host = url.host else {
      return false
    }
    let octets = host.split(separator: ".").compactMap { Int($0) }
    return host.hasSuffix(".local")
      || (octets.count == 4 && octets.allSatisfy { (0...255).contains($0) }
        && (octets[0] == 10 || octets[0] == 192 && octets[1] == 168
          || octets[0] == 172 && (16...31).contains(octets[1])))
  }
  func configureHotspot(address: String, token: String) throws {
    guard !processing, !saving, !reconnecting else { return }
    let address = address.trimmingCharacters(in: .whitespacesAndNewlines)
    guard Self.isHotspotAddress(address) else {
      throw ClientFailure("Enter the Mac’s local HTTP address from the admin Connection panel.")
    }
    try configure(address: address, token: token)
    hotspotAddress = address
    defaults.set(address, forKey: "backendHotspotURL")
    connectionStatus = nil
  }
  func reconnect() async {
    guard !processing, !saving, !reconnecting else { return }
    reconnecting = true
    connectionAttempts = []
    let identity = generation
    defer { reconnecting = false }
    let config = URLSessionConfiguration.ephemeral
    config.urlCache = nil
    config.timeoutIntervalForRequest = 3
    config.timeoutIntervalForResource = 5
    let probe =
      clientSession
      ?? URLSession(configuration: config, delegate: NoRedirects(), delegateQueue: nil)
    defer { if clientSession == nil { probe.invalidateAndCancel() } }
    let routes = Self.isHotspotAddress(hotspotAddress) ? [("hotspot", hotspotAddress)] : []
    var lastError = "Enter the Mac’s hotspot address in Connection settings."
    for (label, route) in routes {
      guard identity == generation, !Task.isCancelled else {
        connectionStatus = nil
        return
      }
      connectionStatus = "Checking \(label)…"
      do {
        let client = try BackendClient(address: route, token: token, session: probe)
        let serverID = try await client.checkConnection()
        var record = pending
        if let saved = record {
          if let expected = saved.serverID {
            guard serverID == expected else {
              throw ClientFailure(
                "This address points to a different backend. Your draft is unchanged.")
            }
          } else if let scanID = saved.scanID {
            let (stored, _) = try await client.request("v1/scans/" + scanID)
            let hash = SHA256.hash(data: saved.image).map { String(format: "%02x", $0) }.joined()
            guard stored["scan_id"].string == scanID,
              stored["input"]["original_sha256"].string == hash
            else {
              throw ClientFailure(
                "The Mac could not verify this draft. Its connection is unchanged.")
            }
          } else if client.baseURL != URL(string: saved.address) {
            throw ClientFailure(
              "This older upload must be recovered at its original address first.")
          }
          record?.address = client.baseURL.absoluteString
          record?.serverID = serverID
        }
        try Task.checkCancellation()
        guard identity == generation else {
          connectionStatus = nil
          return
        }
        if let record, !fixtureMode { try PendingStore.save(record, to: pendingFile) }
        pending = record
        address = client.baseURL.absoluteString
        defaults.set(address, forKey: "backendURL")
        connectionAttempts.append(["address": route, "status": "connected", "route": label])
        connectionStatus = "Connected via \(label)"
        if phase == .recovery { message = "Reconnected. Continue your saved scan when ready." }
        return
      } catch {
        guard identity == generation, !Task.isCancelled else {
          connectionStatus = nil
          return
        }
        lastError = error.localizedDescription
        connectionAttempts.append(["address": route, "status": "failed", "route": label])
      }
    }
    connectionStatus = "Couldn’t reconnect. \(lastError)"
  }
  func captured(_ source: UIImage) {
    guard phase == .capture || phase == .crop || phase == .preview else { return }
    generation = UUID()
    image = source.oriented()
    originalImage = image
    phase = .crop
    complete = false
    message = nil
  }
  func cropped(_ result: UIImage) {
    image = result
    phase = .preview
  }
  func editCrop() {
    guard pending == nil else { return }
    image = originalImage
    phase = .crop
  }
  func reset() {
    do { if !fixtureMode { try PendingStore.clear(at: pendingFile) } } catch {
      message = "Could not clear the local scan. Please try again."
      return
    }
    task?.cancel()
    task = nil
    generation = UUID()
    pending = nil
    draft = nil
    response = nil
    image = nil
    originalImage = nil
    checked = false
    saving = false
    message = nil
    phase = .capture
  }
  func send() {
    guard phase == .preview, pending == nil, !reconnecting, let image else { return }
    if fixtureMode {
      loadFixture()
      return
    }
    do {
      let client = try BackendClient(address: address, token: token, session: clientSession)
      guard let bytes = image.pngData() else { throw ClientFailure("Could not encode this image.") }
      phase = .uploading
      message = nil
      let identity = generation
      task = Task {
        do {
          let selection = try await client.selection()
          let selected = selection.profile
          try Task.checkCancellation()
          guard identity == generation else { return }
          let options = try JSONEncoder().encode(
            JSONValue.object([
              "mode": .string("extract"), "profiles": .array([.string(selected.id)]),
            ]))
          let record = PendingScan(
            key: UUID().uuidString, address: client.baseURL.absoluteString, image: bytes,
            options: options, profileVersion: selected.version, serverID: selection.serverID)
          try PendingStore.save(record, to: pendingFile)
          self.pending = record
          try await uploadAndPoll(client, identity: identity)
        } catch { fail(error, identity: identity) }
      }
    } catch { message = error.localizedDescription }
  }
  func recover() {
    guard let pending, !processing, !saving, !reconnecting else { return }
    task?.cancel()
    generation = UUID()
    phase = pending.scanID == nil ? .uploading : .reading
    saving = pending.confirmationBody != nil
    message = nil
    let identity = generation
    task = Task {
      do {
        let client = try BackendClient(
          address: pending.address, token: token, session: clientSession)
        if pending.confirmationBody != nil {
          try await saveConfirmation(client, identity: identity)
          return
        }
        if pending.scanID != nil {
          phase = .reading
          try await poll(client, identity: identity)
        } else {
          phase = .uploading
          guard let profile = pending.extractionProfile else {
            throw ClientFailure("The saved scan has no valid method. Clear it and capture again.")
          }
          try await client.checkProfile(profile)
          try Task.checkCancellation()
          guard identity == generation else { return }
          try await uploadAndPoll(client, identity: identity)
        }
      } catch { fail(error, identity: identity) }
    }
  }
  private func uploadAndPoll(_ client: BackendClient, identity: UUID) async throws {
    guard let record = pending else { return }
    let id = try await client.submit(record)
    guard identity == generation else { return }
    pending?.scanID = id
    try persist()
    try Task.checkCancellation()
    phase = .reading
    try await poll(client, identity: identity)
  }
  private func poll(_ client: BackendClient, identity: UUID) async throws {
    guard let id = pending?.scanID else { return }
    let start = ContinuousClock.now
    while !Task.isCancelled {
      let (json, data) = try await client.request("v1/scans/" + id)
      try Task.checkCancellation()
      guard identity == generation else { return }
      guard json["scan_id"].string == id else {
        throw ClientFailure("The response belongs to a different scan.")
      }
      if ["queued", "running"].contains(json["state"].string ?? "") {
        phase = json["state"].string == "queued" ? .queued : .reading
        if start.duration(to: .now) > .seconds(240) {
          throw ClientFailure(
            "This scan is taking longer than expected. Check its status again without sending a new scan."
          )
        }
        try await Task.sleep(for: .seconds(1))
      } else {
        pending?.response = data
        try persist()
        accept(json, data: data)
        return
      }
    }
  }
  private func accept(_ json: JSONValue, data: Data) {
    response = json
    do {
      let result = try PaymentDraft(response: json)
      guard result.outcome != "error" else {
        throw ClientFailure(
          "No usable payment fields were found. Your image is still available to check.")
      }
      draft = result
      checked = false
      phase = .review
      message = nil
    } catch {
      phase = .failed
      message =
        json["runs"].array.compactMap { $0["error"]["message"].string }.first
        ?? error.localizedDescription
    }
  }
  private func fail(_ error: Error, identity: UUID) {
    guard identity == generation else { return }
    saving = false
    if error is CancellationError { return }
    phase = pending == nil ? .preview : .recovery
    message = error.localizedDescription
  }
  private func persist() throws {
    if !fixtureMode, let pending { try PendingStore.save(pending, to: pendingFile) }
  }
  func edit(_ path: String, _ value: String) {
    guard !saving, pending?.confirmationBody == nil else { return }
    draft?.edit(path, value: value)
    checked = false
    saveEdits()
  }
  func select(_ id: String) {
    guard !saving, pending?.confirmationBody == nil else { return }
    draft?.select(id)
    checked = false
    saveEdits()
  }
  private func saveEdits() {
    pending?.editedValues = draft?.values
    pending?.editedFieldIDs = draft?.editedFieldIDs
    pending?.selectedCandidateID = draft?.selectedID
    do { try persist() } catch {
      message = "Could not save edits on this phone. Keep this screen open and try again."
    }
  }
  func confirm() {
    guard checked, draft?.canConfirm == true, !saving, !reconnecting, phase == .review else {
      return
    }
    if fixtureMode {
      reset()
      complete = true
      return
    }
    do {
      guard let draft, let pending else { return }
      self.pending?.confirmationID = pending.confirmationID ?? UUID().uuidString
      self.pending?.confirmationBody = try JSONEncoder().encode(draft.confirmation)
      try persist()
      saving = true
      let identity = generation
      task = Task {
        do {
          let client = try BackendClient(
            address: pending.address, token: token, session: clientSession)
          try await saveConfirmation(client, identity: identity)
        } catch { fail(error, identity: identity) }
      }
    } catch { message = error.localizedDescription }
  }
  private func saveConfirmation(_ client: BackendClient, identity: UUID) async throws {
    guard let pending, let scan = pending.scanID, let id = pending.confirmationID,
      let body = pending.confirmationBody
    else { return }
    saving = true
    _ = try await client.request(
      "v1/scans/" + scan + "/reviews/" + id, method: "PUT", body: body,
      headers: ["Content-Type": "application/json"])
    guard identity == generation else { return }
    reset()
    if phase == .capture { complete = true }
  }
  func background() {
    generation = UUID()
    task?.cancel()
    task = nil
    if processing || saving {
      phase = pending == nil ? .preview : .recovery
      saving = false
      message =
        pending == nil
        ? "Ready to send when you return."
        : "Scan paused on this phone. The Mac may still be processing it."
    }
  }
  func foreground() {
    if phase == .recovery, pending?.scanID != nil, pending?.confirmationBody == nil { recover() }
  }
  func loadFixture() {
    guard let url = Bundle.main.url(forResource: "uk-extract.synthetic", withExtension: "json"),
      let data = try? Data(contentsOf: url),
      let json = try? JSONDecoder().decode(JSONValue.self, from: data)
    else { return }
    phase = .reading
    let identity = generation
    task = Task {
      try? await Task.sleep(for: .milliseconds(600))
      guard !Task.isCancelled, identity == generation else { return }
      accept(json, data: data)
    }
  }
}
