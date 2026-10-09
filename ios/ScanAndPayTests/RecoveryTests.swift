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

private final class FakeMac: @unchecked Sendable {
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
  private func setup(empty: Bool = false) throws -> (ScanSession, FakeMac, URL) {
    let source = try ScanAndPayTests().fixture()
    var object = source.object
    object["scan_id"] = .string("scan-network-test")
    if empty {
      var run = source["runs"].array[0].object
      run["outcome"] = .string("error")
      object["runs"] = .array([.object(run)])
    }
    let mac = FakeMac(result: .object(object))
    StubProtocol.respond = mac.respond
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubProtocol.self]
    let session = URLSession(configuration: config)
    let file = FileManager.default.temporaryDirectory.appending(path: UUID().uuidString).appending(
      path: "pending.json")
    let model = ScanSession(
      clientSession: session, pendingFile: file,
      defaults: UserDefaults(suiteName: UUID().uuidString)!)
    model.address = "http://127.0.0.1:8765"
    model.token = "synthetic-only"
    let image = UIGraphicsImageRenderer(size: CGSize(width: 20, height: 30)).image { c in
      UIColor.white.setFill()
      c.fill(CGRect(x: 0, y: 0, width: 20, height: 30))
    }
    model.captured(image)
    model.cropped(image)
    return (model, mac, file)
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
  func testUncertainUploadReusesKeyAndConfirmedEditsRemainSeparate() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    XCTAssertTrue(mac.requests.isEmpty)
    mac.timeoutUpload = true
    model.send()
    model.send()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(model.pending)
    model.recover()
    model.recover()
    try await wait { model.phase == .review }
    let uploads = mac.requests.filter { $0.httpMethod == "POST" }
    XCTAssertEqual(uploads.count, 2)
    XCTAssertEqual(
      uploads.map { $0.value(forHTTPHeaderField: "Idempotency-Key") }, [frozen.key, frozen.key])
    XCTAssertEqual(model.pending?.image, frozen.image)
    let original = model.response?.pretty
    model.edit("/candidates/0/remittance/reference", "0000123")
    XCTAssertEqual(model.response?.pretty, original)
    model.checked = true
    mac.timeoutConfirmation = true
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
    let puts = mac.requests.filter { $0.httpMethod == "PUT" }
    XCTAssertEqual(puts.count, 2)
    XCTAssertEqual(puts[0].url, puts[1].url)
    XCTAssertEqual(mac.requests.filter { $0.httpMethod == "POST" }.count, 2)
    XCTAssertNil(PendingStore.read(from: file))
    XCTAssertNil(restored.response)
  }
  func testAcceptedScanResumesPollingAfterBackgroundWithoutUpload() async throws {
    let (model, mac, file) = try setup()
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
    XCTAssertEqual(mac.requests.count, 1)
    XCTAssertEqual(mac.requests[0].httpMethod, "GET")
    restored.background()
    restored.foreground()
    XCTAssertEqual(restored.phase, .review)
  }
  func testWrongProfileNeverUploadsEvenAfterRecovery() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    mac.correctProfile = false
    model.send()
    try await wait { model.phase == .preview }
    XCTAssertNil(model.pending)
    model.send()
    try await wait { model.phase == .preview }
    XCTAssertEqual(mac.requests.count, 2)
    XCTAssertTrue(mac.requests.allSatisfy { $0.url?.path == "/v1/profiles" })
  }
  func testAdminChoiceAppliesOnlyToNewScansAndRecoveryKeepsOriginal() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    let image = try XCTUnwrap(model.image)
    mac.timeoutUpload = true
    model.send()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(PendingStore.read(from: file))
    mac.selectedProfile = mac.alternateProfile
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
    XCTAssertEqual(model.pending?.extractionProfile, mac.alternateProfile)
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
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    model.background()
    model.foreground()
    XCTAssertEqual(model.phase, .preview)
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
    XCTAssertTrue(mac.requests.isEmpty)
  }
  func testReconnectTriesCableFirstAndDoesNotUpload() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.cableAddress = "http://169.254.1.2:8000"
    model.wifiAddress = "http://192.168.1.2:8000"
    await model.reconnect()
    XCTAssertEqual(model.address, model.cableAddress)
    XCTAssertEqual(model.connectionStatus, "Connected via USB")
    XCTAssertEqual(mac.requests.map { $0.url?.host }, ["169.254.1.2"])
    XCTAssertTrue(
      mac.requests.allSatisfy { $0.httpMethod == "GET" && $0.url?.path == "/v1/profiles" })
    XCTAssertEqual(model.phase, .preview)
    XCTAssertNotNil(model.image)
    XCTAssertNil(model.pending)
  }
  func testReconnectFallsBackToWiFiAndFailureKeepsAddress() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.cableAddress = "http://169.254.1.2:8000"
    model.wifiAddress = "http://192.168.1.2:8000"
    mac.blockedHosts = ["169.254.1.2"]
    await model.reconnect()
    XCTAssertEqual(mac.requests.map { $0.url?.host }, ["169.254.1.2", "192.168.1.2"])
    XCTAssertEqual(model.connectionStatus, "Connected via Wi-Fi")
    XCTAssertEqual(model.address, model.wifiAddress)
    mac.blockedHosts.insert("192.168.1.2")
    await model.reconnect()
    XCTAssertEqual(model.address, model.wifiAddress)
    XCTAssertTrue(model.connectionStatus?.hasPrefix("Couldn’t reconnect") == true)
    XCTAssertFalse(model.reconnecting)
    XCTAssertTrue(mac.requests.allSatisfy { $0.httpMethod == "GET" })
  }
  func testReconnectPreservesPendingConfirmationAndRejectsDifferentBackend() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    model.send()
    try await wait { model.phase == .review }
    model.edit("/candidates/0/remittance/reference", "0000009")
    model.checked = true
    mac.timeoutConfirmation = true
    model.confirm()
    try await wait { model.phase == .recovery }
    let frozen = try XCTUnwrap(model.pending)
    let before = mac.requests.count
    model.cableAddress = "http://169.254.1.2:8000"
    model.wifiAddress = "http://192.168.1.2:8000"
    await model.reconnect()
    let saved = try XCTUnwrap(PendingStore.read(from: file))
    XCTAssertEqual(saved.address, model.cableAddress)
    XCTAssertEqual(saved.key, frozen.key)
    XCTAssertEqual(saved.image, frozen.image)
    XCTAssertEqual(saved.options, frozen.options)
    XCTAssertEqual(saved.response, frozen.response)
    XCTAssertEqual(saved.editedValues, frozen.editedValues)
    XCTAssertEqual(saved.confirmationID, frozen.confirmationID)
    XCTAssertEqual(saved.confirmationBody, frozen.confirmationBody)
    XCTAssertEqual(model.phase, .recovery)
    XCTAssertTrue(mac.requests.dropFirst(before).allSatisfy { $0.httpMethod == "GET" })
    mac.serverID = UUID().uuidString
    await model.reconnect()
    XCTAssertTrue(model.connectionStatus?.contains("different backend") == true)
    XCTAssertEqual(PendingStore.read(from: file)?.address, saved.address)
    XCTAssertEqual(PendingStore.read(from: file)?.confirmationBody, saved.confirmationBody)
  }
  func testUncertainUploadReconnectIsReadOnlyAndRecoveryKeepsKey() async throws {
    let (model, mac, file) = try setup()
    defer { try? FileManager.default.removeItem(at: file.deletingLastPathComponent()) }
    mac.timeoutUpload = true
    model.send()
    try await wait { model.phase == .recovery }
    let key = model.pending?.key
    model.cableAddress = "http://169.254.1.2:8000"
    await model.reconnect()
    XCTAssertEqual(mac.requests.filter { $0.httpMethod == "POST" }.count, 1)
    XCTAssertNil(model.pending?.scanID)
    model.recover()
    try await wait { model.phase == .review }
    XCTAssertEqual(model.pending?.key, key)
    XCTAssertEqual(
      mac.requests.filter { $0.httpMethod == "POST" }.last?.value(
        forHTTPHeaderField: "Idempotency-Key"), key)
    XCTAssertEqual(mac.requests.filter { $0.httpMethod == "POST" }.last?.url?.host, "169.254.1.2")
  }
}
