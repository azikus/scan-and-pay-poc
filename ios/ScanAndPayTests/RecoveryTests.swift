import UIKit
import XCTest

@testable import ScanAndPay

private final class StubProtocol: URLProtocol {
  static var respond: ((URLRequest) throws -> (Int, JSONValue))!
  override class func canInit(with request: URLRequest) -> Bool { true }
  override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
  override func startLoading() {
    do {
      let (status, value) = try Self.respond(request)
      client?.urlProtocol(
        self,
        didReceive: HTTPURLResponse(
          url: request.url!, statusCode: status, httpVersion: "HTTP/1.1",
          headerFields: ["Content-Type": "application/json"])!, cacheStoragePolicy: .notAllowed)
      client?.urlProtocol(self, didLoad: try JSONEncoder().encode(value))
      client?.urlProtocolDidFinishLoading(self)
    } catch { client?.urlProtocol(self, didFailWithError: error) }
  }
  override func stopLoading() {}
}

private final class FakeBackend: @unchecked Sendable {
  private let lock = NSLock()
  private var seen = [URLRequest]()
  var timeoutUpload = false
  var timeoutConfirmation = false
  var correctProfile = true
  var blockedHosts = Set<String>()
  var serverID = "3035118D-6055-44E8-961A-303CCC83D081"
  var selectedProfile = ExtractionProfile(id: BackendClient.profile, version: BackendClient.version)
  let alternateProfile = ExtractionProfile(id: "alternate-image", version: "tested-v2")
  let result: JSONValue
  init(result: JSONValue) { self.result = result }
  var requests: [URLRequest] {
    lock.lock()
    defer { lock.unlock() }
    return seen
  }
  func respond(_ request: URLRequest) throws -> (Int, JSONValue) {
    lock.lock()
    defer { lock.unlock() }
    seen.append(request)
    if blockedHosts.contains(request.url?.host ?? "") { throw URLError(.cannotConnectToHost) }
    switch (request.httpMethod!, request.url!.path) {
    case (_, "/v1/profiles"):
      return (
        200,
        .object([
          "server_id": .string(serverID),
          "default_extract_profile_id": .string(selectedProfile.id),
          "default_extract_profile_version": .string(selectedProfile.version),
          "profiles": .array(
            [
              ExtractionProfile(id: BackendClient.profile, version: BackendClient.version),
              alternateProfile,
            ].map { profile in
              .object([
                "id": .string(profile.id),
                "version": .string(correctProfile ? profile.version : "changed"),
                "enabled": .bool(true), "configured": .bool(true),
              ])
            }),
        ])
      )
    case ("POST", "/v1/scans"):
      if timeoutUpload {
        timeoutUpload = false
        throw URLError(.timedOut)
      }
      return (202, .object(["scan_id": .string("scan-network-test")]))
    case ("PUT", _):
      if timeoutConfirmation {
        timeoutConfirmation = false
        throw URLError(.timedOut)
      }
      return (200, .object(["simulated": .bool(true)]))
    default: return (200, result)
    }
  }
}

@MainActor final class RecoveryTests: XCTestCase {
  func testDemoBindingSurvivesRecoveryAndLegacyPendingStillDecodes() throws {
    let legacy = PendingScan(key: "original", address: "http://192.168.1.2:8000", image: Data(), options: Data())
    let oldData = try JSONEncoder().encode(legacy)
    XCTAssertTrue(try JSONDecoder().decode(PendingScan.self, from: oldData).demoHeaders.isEmpty)
    var bound = legacy
    bound.demoSessionID = UUID().uuidString
    bound.demoJourneyID = UUID().uuidString
    let recovered = try JSONDecoder().decode(PendingScan.self, from: JSONEncoder().encode(bound))
    XCTAssertEqual(recovered.demoHeaders, bound.demoHeaders)
    XCTAssertEqual(recovered.key, "original")
  }
  func testDemoOutageDoesNotBlockReviewOrConfirmation() async throws {
    let (model, backend, _) = try setup()
    model.demoEnabled = true
    model.captured(UIGraphicsImageRenderer(size: CGSize(width: 20, height: 30)).image { ctx in UIColor.white.setFill(); ctx.fill(CGRect(x: 0, y: 0, width: 20, height: 30)) })
    model.cropped(model.image!)
    StubProtocol.respond = { request in
      if request.url!.path.hasPrefix("/v1/demo/") { throw URLError(.cannotConnectToHost) }
      return try backend.respond(request)
    }
    model.send()
    try await wait { model.phase == .review }
    XCTAssertNotNil(model.pending?.demoSessionID)
    XCTAssertNotNil(model.pending?.demoJourneyID)
    model.checked = true
    model.confirm()
    try await wait { model.complete }
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "POST" }.count, 1)
    model.demoEnabled = false
  }
  private func setup(
    empty: Bool = false, result: JSONValue? = nil,
    encodeImage: @escaping (UIImage) async throws -> Data = ScanSession.encodePNG
  ) throws -> (
    ScanSession, FakeBackend, URL
  ) {
    let source = try result ?? ScanAndPayTests().fixture()
    var object = source.object
    object["scan_id"] = .string("scan-network-test")
    if empty {
      var run = source["runs"].array[0].object
      run["outcome"] = .string("error")
      object["runs"] = .array([.object(run)])
    }
    let backend = FakeBackend(result: .object(object))
    StubProtocol.respond = backend.respond
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let session = URLSession(configuration: config)
    let file = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString).appending(
      path: "pending.json")
    let model = ScanSession(
      clientSession: session, pendingFile: file,
      defaults: UserDefaults(suiteName: UUID().uuidString)!, encodeImage: encodeImage)
    model.address = "http://127.0.0.1:8765"
    model.token = "synthetic-only"
    let image = UIGraphicsImageRenderer(size: CGSize(width: 20, height: 30)).image { c in
      UIColor.white.setFill()
      c.fill(CGRect(x: 0, y: 0, width: 20, height: 30))
    }
    model.captured(image)
    model.cropped(image)
    return (model, backend, file)
  }
  private func wait(_ condition: () -> Bool, file: StaticString = #filePath, line: UInt = #line)
    async throws
  {
    for _ in 0..<100 {
      if condition() { return }
      try await Task.sleep(for: .milliseconds(20))
    }
    XCTFail("Expected session state was not reached", file: file, line: line)
  }
  func testSendShowsProgressWhileEncodingAndIgnoresDuplicateTaps() async throws {
    var resume: CheckedContinuation<Data, Error>?
    var encodes = 0
    let (model, backend, file) = try setup { _ in
      encodes += 1
      return try await withCheckedThrowingContinuation { resume = $0 }
    }
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    let image = try XCTUnwrap(model.image)
    model.send()
    XCTAssertEqual(model.phase, .preparing)
    XCTAssertTrue(model.processing)
    XCTAssertEqual(model.processingTitle, "Preparing image…")
    model.send()
    try await wait { resume != nil }
    XCTAssertEqual(encodes, 1)
    XCTAssertTrue(backend.requests.isEmpty)
    resume?.resume(returning: try XCTUnwrap(image.pngData()))
    try await wait { model.phase == .review }
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "POST" }.count, 1)
  }
  func testBackgroundDuringEncodingDoesNotUploadLateResult() async throws {
    var resume: CheckedContinuation<Data, Error>?
    let (model, backend, file) = try setup { _ in
      try await withCheckedThrowingContinuation { resume = $0 }
    }
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    let bytes = try XCTUnwrap(model.image?.pngData())
    model.send()
    try await wait { resume != nil }
    model.background()
    model.foreground()
    resume?.resume(returning: bytes)
    try await Task.sleep(for: .milliseconds(100))
    XCTAssertEqual(model.phase, .preview)
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
    XCTAssertTrue(backend.requests.isEmpty)
  }
  func testEncodingFailureKeepsImageAndExplainsRetry() async throws {
    let (model, backend, file) = try setup { _ in
      throw ClientFailure("Could not encode this image.")
    }
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .preview }
    XCTAssertEqual(model.message, "Could not encode this image.")
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
    XCTAssertTrue(backend.requests.isEmpty)
  }

  func testUncertainUploadReusesKeyAndConfirmedEditsRemainSeparate() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    XCTAssertTrue(backend.requests.isEmpty)
    backend.timeoutUpload = true
    model.send()
    model.send()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(model.pending)
    model.recover()
    model.recover()
    try await wait { model.phase == .review }
    let uploads = backend.requests.filter { $0.httpMethod == "POST" }
    XCTAssertEqual(uploads.count, 2)
    XCTAssertEqual(
      uploads.map { $0.value(forHTTPHeaderField: "Idempotency-Key") }, [frozen.key, frozen.key])
    XCTAssertEqual(model.pending?.image, frozen.image)
    let original = model.response?.pretty
    model.edit("/candidates/0/remittance/reference", "0000123")
    XCTAssertEqual(model.response?.pretty, original)
    model.checked = true
    backend.timeoutConfirmation = true
    model.confirm()
    model.confirm()
    try await wait { model.phase == .recovery }
    let saved = try XCTUnwrap(PendingStore.read(from: file))
    XCTAssertEqual(
      try JSONDecoder().decode(JSONValue.self, from: XCTUnwrap(saved.confirmationBody))["values"][
        "/candidates/0/remittance/reference"], .string("0000123"))
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let restored = ScanSession(clientSession: URLSession(configuration: config), pendingFile: file)
    restored.token = "synthetic-only"
    XCTAssertEqual(restored.phase, .recovery)
    restored.recover()
    restored.recover()
    try await wait { restored.complete }
    let puts = backend.requests.filter { $0.httpMethod == "PUT" }
    XCTAssertEqual(puts.count, 2)
    XCTAssertEqual(puts[0].url, puts[1].url)
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "POST" }.count, 2)
    XCTAssertNil(PendingStore.read(from: file))
    XCTAssertNil(restored.response)
  }
  func testExtractedDraftAndExplicitEditsPersistWithoutSavingHiddenInference() async throws {
    let currency = "/candidates/0/amount/currency"
    let recipient = "/candidates/0/beneficiary_name"
    let source = try ScanAndPayTests().fixture()
      .replacingPayment(currency + "/state", with: .string("inferred"))
      .replacingPayment(
        recipient + "/normalization", with: .array([.string("draft_beneficiary_from_supplier")]))
    let (model, backend, file) = try setup(result: source)
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .review }
    model.edit(currency, "GBP")
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let restored = ScanSession(clientSession: URLSession(configuration: config), pendingFile: file)
    restored.token = "synthetic-only"
    XCTAssertEqual(restored.draft?.currencyField?.isEdited, true)
    XCTAssertEqual(restored.draft?.currencyField?.value, "GBP")
    XCTAssertNil(restored.draft?.recipientField)
    XCTAssertEqual(restored.draft?.editedFieldIDs.contains(recipient), false)
    XCTAssertEqual(restored.response, model.response)
    restored.checked = true
    backend.timeoutConfirmation = true
    restored.confirm()
    try await wait { restored.phase == .recovery }
    let saved = try XCTUnwrap(PendingStore.read(from: file))
    let payload = try JSONDecoder().decode(JSONValue.self, from: XCTUnwrap(saved.confirmationBody))
    XCTAssertEqual(payload["values"][currency], .string("GBP"))
    XCTAssertEqual(payload["values"][recipient], .null)
    XCTAssertEqual(restored.confirmationValues, payload)
  }
  func testLegacyConfirmationRetryKeepsFrozenBodyAndInspectorValues() async throws {
    let currency = "/candidates/0/amount/currency"
    let source = try ScanAndPayTests().fixture()
      .replacingPayment(currency + "/state", with: .string("inferred"))
    let (model, backend, file) = try setup(result: source)
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .review }
    var legacy = try XCTUnwrap(PendingStore.read(from: file))
    let draft = try XCTUnwrap(model.draft)
    legacy.editedValues = Dictionary(
      uniqueKeysWithValues: draft.relevantObservations.map { ($0.0, $0.1["value"]) })
    legacy.editedFieldIDs = nil
    legacy.selectedCandidateID = draft.selectedID
    var body = draft.confirmation.object
    body["values"] = .object(try XCTUnwrap(legacy.editedValues))
    legacy.confirmationBody = try JSONEncoder().encode(JSONValue.object(body))
    legacy.confirmationID = UUID().uuidString
    try PendingStore.save(legacy, to: file)
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let restored = ScanSession(clientSession: URLSession(configuration: config), pendingFile: file)
    restored.token = "synthetic-only"
    XCTAssertEqual(restored.phase, .recovery)
    XCTAssertNil(restored.draft?.currencyField)
    XCTAssertEqual(restored.confirmationValues?["values"][currency], .string("GBP"))
    restored.edit(currency, "EUR")
    XCTAssertEqual(restored.pending?.confirmationBody, legacy.confirmationBody)
    XCTAssertEqual(restored.pending?.confirmationID, legacy.confirmationID)
    restored.recover()
    try await wait { restored.complete }
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "PUT" }.count, 1)
    XCTAssertEqual(backend.requests.last?.url?.lastPathComponent, legacy.confirmationID)
  }
  func testAcceptedScanResumesPollingAfterBackgroundWithoutUpload() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    let image = try XCTUnwrap(model.image?.pngData())
    try PendingStore.save(
      PendingScan(
        key: "accepted-key", scanID: "scan-network-test", address: model.address, image: image,
        options: Data()), to: file)
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let restored = ScanSession(clientSession: URLSession(configuration: config), pendingFile: file)
    restored.token = "synthetic-only"
    restored.foreground()
    restored.foreground()
    try await wait { restored.phase == .review }
    XCTAssertEqual(backend.requests.count, 1)
    XCTAssertEqual(backend.requests[0].httpMethod, "GET")
    restored.background()
    restored.foreground()
    XCTAssertEqual(restored.phase, .review)
  }
  func testWrongProfileNeverUploadsEvenAfterRecovery() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    backend.correctProfile = false
    model.send()
    try await wait { model.phase == .preview }
    XCTAssertNil(model.pending)
    model.send()
    try await wait { model.phase == .preview }
    XCTAssertEqual(backend.requests.count, 2)
    XCTAssertTrue(backend.requests.allSatisfy { $0.url?.path == "/v1/profiles" })
  }
  func testAdminChoiceAppliesOnlyToNewScansAndRecoveryKeepsOriginal() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    let image = try XCTUnwrap(model.image)
    backend.timeoutUpload = true
    model.send()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(PendingStore.read(from: file))
    backend.selectedProfile = backend.alternateProfile
    model.recover()
    try await wait { model.phase == .review }
    XCTAssertEqual(model.pending?.options, frozen.options)
    XCTAssertEqual(model.pending?.key, frozen.key)
    XCTAssertEqual(model.pending?.extractionProfile?.id, BackendClient.profile)
    model.reset()
    model.captured(image)
    model.cropped(image)
    model.send()
    try await wait { model.phase == .review }
    XCTAssertEqual(model.pending?.extractionProfile, backend.alternateProfile)
    XCTAssertNotEqual(model.pending?.key, frozen.key)
  }
  func testEmptyOutcomeKeepsImageAndShowsFailure() async throws {
    let (model, _, file) = try setup(empty: true)
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .failed }
    XCTAssertNil(model.draft)
    XCTAssertNotNil(model.image)
    XCTAssertNotNil(model.response)
    XCTAssertFalse(model.checked)
  }
  func testBackgroundDuringMethodLookupKeepsUnsentPreview() throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    model.background()
    model.foreground()
    XCTAssertEqual(model.phase, .preview)
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
    XCTAssertTrue(backend.requests.isEmpty)
  }
  func testHotspotMigrationPreservesWiFiAndDropsAlternatives() throws {
    let name = "hotspot-migration-" + UUID().uuidString
    let defaults = try XCTUnwrap(UserDefaults(suiteName: name))
    defer { defaults.removePersistentDomain(forName: name) }
    defaults.set("http://169.254.1.2:8000", forKey: "backendURL")
    defaults.set("http://169.254.1.2:8000", forKey: "backendCableURL")
    defaults.set("http://172.20.10.2:8000", forKey: "backendWiFiURL")
    let model = ScanSession(fixtureMode: true, defaults: defaults)
    XCTAssertEqual(model.hotspotAddress, "http://172.20.10.2:8000")
    XCTAssertEqual(model.address, model.hotspotAddress)
    XCTAssertNil(defaults.string(forKey: "backendCableURL"))
    XCTAssertNil(defaults.string(forKey: "backendWiFiURL"))
    XCTAssertEqual(ScanSession(fixtureMode: true, defaults: defaults).address, model.address)
    defaults.removeObject(forKey: "backendHotspotURL")
    defaults.set("https://example.com", forKey: "backendURL")
    XCTAssertTrue(ScanSession(fixtureMode: true, defaults: defaults).address.isEmpty)
    XCTAssertFalse(ScanSession.isHotspotAddress("http://169.254.1.2:8000"))
    XCTAssertFalse(ScanSession.isHotspotAddress("https://example.com"))
  }
  func testReconnectUsesOnlyHotspotAndDoesNotUpload() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.hotspotAddress = "http://172.20.10.2:8000"
    await model.reconnect()
    XCTAssertEqual(model.address, model.hotspotAddress)
    XCTAssertEqual(model.connectionStatus, "Connected via hotspot")
    XCTAssertEqual(backend.requests.map { $0.url?.host }, ["172.20.10.2"])
    XCTAssertTrue(
      backend.requests.allSatisfy { $0.httpMethod == "GET" && $0.url?.path == "/v1/profiles" })
    XCTAssertEqual(model.phase, .preview)
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
  }
  func testReconnectFailureDoesNotTryPreviousAddress() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.hotspotAddress = "http://172.20.10.2:8000"
    await model.reconnect()
    XCTAssertEqual(backend.requests.map { $0.url?.host }, ["172.20.10.2"])
    XCTAssertEqual(model.connectionStatus, "Connected via hotspot")
    XCTAssertEqual(model.address, model.hotspotAddress)
    backend.blockedHosts.insert("172.20.10.2")
    model.address = "http://169.254.1.2:8000"
    await model.reconnect()
    XCTAssertEqual(model.address, "http://169.254.1.2:8000")
    XCTAssertEqual(backend.requests.map { $0.url?.host }, ["172.20.10.2", "172.20.10.2"])
    XCTAssertTrue(model.connectionStatus?.hasPrefix("Couldn’t reconnect") == true)
    XCTAssertFalse(model.reconnecting)
    XCTAssertTrue(backend.requests.allSatisfy { $0.httpMethod == "GET" })
  }
  func testReconnectPreservesPendingConfirmationAndRejectsDifferentBackend() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .review }
    model.edit("/candidates/0/remittance/reference", "0000009")
    model.checked = true
    backend.timeoutConfirmation = true
    model.confirm()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(model.pending)
    let before = backend.requests.count
    model.hotspotAddress = "http://172.20.10.2:8000"
    await model.reconnect()
    let saved = try XCTUnwrap(PendingStore.read(from: file))
    XCTAssertEqual(saved.address, model.hotspotAddress)
    XCTAssertEqual(saved.key, frozen.key)
    XCTAssertEqual(saved.image, frozen.image)
    XCTAssertEqual(saved.options, frozen.options)
    XCTAssertEqual(saved.response, frozen.response)
    XCTAssertEqual(saved.editedValues, frozen.editedValues)
    XCTAssertEqual(saved.confirmationID, frozen.confirmationID)
    XCTAssertEqual(saved.confirmationBody, frozen.confirmationBody)
    XCTAssertEqual(model.phase, .recovery)
    XCTAssertTrue(backend.requests.dropFirst(before).allSatisfy { $0.httpMethod == "GET" })
    backend.serverID = UUID().uuidString
    await model.reconnect()
    XCTAssertTrue(model.connectionStatus?.contains("different backend") == true)
    XCTAssertEqual(PendingStore.read(from: file)?.address, saved.address)
    XCTAssertEqual(PendingStore.read(from: file)?.confirmationBody, saved.confirmationBody)
  }
  func testUncertainUploadReconnectIsReadOnlyAndRecoveryKeepsKey() async throws {
    let (model, backend, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    backend.timeoutUpload = true
    model.send()
    try await wait { model.phase == .recovery }
    let key = model.pending?.key
    model.hotspotAddress = "http://172.20.10.2:8000"
    await model.reconnect()
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "POST" }.count, 1)
    XCTAssertNil(model.pending?.scanID)
    model.recover()
    try await wait { model.phase == .review }
    XCTAssertEqual(model.pending?.key, key)
    XCTAssertEqual(
      backend.requests.filter { $0.httpMethod == "POST" }.last?.value(
        forHTTPHeaderField: "Idempotency-Key"), key)
    XCTAssertEqual(backend.requests.filter { $0.httpMethod == "POST" }.last?.url?.host, "172.20.10.2")
  }
}
