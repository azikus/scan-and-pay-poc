import Foundation
import Security

final class NoRedirects: NSObject, URLSessionTaskDelegate {
  func urlSession(
    _ session: URLSession, task: URLSessionTask,
    willPerformHTTPRedirection response: HTTPURLResponse, newRequest request: URLRequest,
    completionHandler: @escaping (URLRequest?) -> Void
  ) { completionHandler(nil) }
}

struct BackendClient {
  static let profile = "openai-mini-image-roles-v3"
  static let version = "2-5094b6dc13ef5718"
  let baseURL: URL
  let token: String
  let session: URLSession
  init(address: String, token: String, session: URLSession? = nil) throws {
    guard let url = URL(string: address.trimmingCharacters(in: .whitespacesAndNewlines)),
      ["http", "https"].contains(url.scheme?.lowercased() ?? ""), let host = url.host,
      !host.isEmpty,
      url.user == nil, url.password == nil, url.query == nil, url.fragment == nil,
      url.path.isEmpty || url.path == "/", !token.isEmpty
    else { throw ClientFailure("Enter a Mac base URL and local access token.") }
    if url.scheme?.lowercased() == "http" && !Self.isLocal(host) {
      throw ClientFailure("Use HTTPS, or a local Mac address on your private network.")
    }
    #if !targetEnvironment(simulator)
      if ["localhost", "127.0.0.1", "::1", "[::1]"].contains(host) {
        throw ClientFailure(
          "On your iPhone, use your Mac’s LAN address. Localhost points to the phone.")
      }
    #endif
    self.baseURL = url
    self.token = token
    if let session {
      self.session = session
    } else {
      let config = URLSessionConfiguration.ephemeral
      config.urlCache = nil
      config.requestCachePolicy = .reloadIgnoringLocalCacheData
      config.timeoutIntervalForRequest = 20
      config.timeoutIntervalForResource = 45
      self.session = URLSession(configuration: config, delegate: NoRedirects(), delegateQueue: nil)
    }
  }
  static func isLocal(_ raw: String) -> Bool {
    let host = raw.lowercased().trimmingCharacters(in: CharacterSet(charactersIn: "[]"))
    if host == "localhost" || host.hasSuffix(".local") || host == "::1" || host.hasPrefix("fe80:")
      || host.hasPrefix("fc") && host.contains(":") || host.hasPrefix("fd") && host.contains(":")
    {
      return true
    }
    let octets = host.split(separator: ".").compactMap { Int($0) }
    guard octets.count == 4, octets.allSatisfy({ (0...255).contains($0) }) else { return false }
    return octets[0] == 10 || octets[0] == 127 || octets[0] == 192 && octets[1] == 168
      || octets[0] == 172 && (16...31).contains(octets[1]) || octets[0] == 169 && octets[1] == 254
  }
  func request(
    _ path: String, method: String = "GET", body: Data? = nil, headers: [String: String] = [:]
  ) async throws -> (JSONValue, Data) {
    var request = URLRequest(url: baseURL.appending(path: path))
    request.httpMethod = method
    request.httpBody = body
    request.setValue("Bearer " + token, forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Accept")
    for (key, value) in headers { request.setValue(value, forHTTPHeaderField: key) }
    let (data, response) = try await session.data(for: request)
    guard let http = response as? HTTPURLResponse else {
      throw ClientFailure("The Mac returned an invalid response.")
    }
    let json = (try? JSONDecoder().decode(JSONValue.self, from: data)) ?? .null
    guard (200..<300).contains(http.statusCode) else {
      let message =
        json["error"]["message"].string
        ?? "The Mac could not complete the request (\(http.statusCode))."
      throw ClientFailure(message)
    }
    guard case .object = json else { throw ClientFailure("The Mac returned unreadable JSON.") }
    return (json, data)
  }
  @discardableResult
  func checkProfile(_ expected: ExtractionProfile? = nil) async throws -> ExtractionProfile {
    try await selection(expected).profile
  }
  func checkConnection() async throws -> String {
    let (result, _) = try await request("v1/profiles")
    guard let id = result["server_id"].string, UUID(uuidString: id) != nil else {
      throw ClientFailure("Update the Mac backend before reconnecting.")
    }
    return id
  }
  func selection(_ expected: ExtractionProfile? = nil) async throws -> (
    profile: ExtractionProfile, serverID: String?
  ) {
    let (result, _) = try await request("v1/profiles")
    let id = expected?.id ?? result["default_extract_profile_id"].string ?? Self.profile
    let version =
      expected?.version ?? result["default_extract_profile_version"].string
      ?? (id == Self.profile ? Self.version : nil)
    guard let version,
      let profile = result["profiles"].array.first(where: { $0["id"].string == id }),
      profile["version"].string == version, profile["enabled"] == .bool(true),
      profile["configured"] == .bool(true)
    else {
      throw ClientFailure(
        "The selected method is unavailable or its version changed. Check Next scan in the admin."
      )
    }
    return (ExtractionProfile(id: id, version: version), result["server_id"].string)
  }
  static func multipart(image: Data, options: Data, boundary: String) -> Data {
    var body = Data()
    func append(_ s: String) { body.append(Data(s.utf8)) }
    append(
      "--\(boundary)\r\nContent-Disposition: form-data; name=\"options\"\r\nContent-Type: application/json\r\n\r\n"
    )
    body.append(options)
    append(
      "\r\n--\(boundary)\r\nContent-Disposition: form-data; name=\"image\"; filename=\"capture.png\"\r\nContent-Type: image/png\r\n\r\n"
    )
    body.append(image)
    append("\r\n--\(boundary)--\r\n")
    return body
  }
  func submit(_ pending: PendingScan) async throws -> String {
    let boundary = "ScanPay-" + UUID().uuidString
    let (response, _) = try await request(
      "v1/scans", method: "POST",
      body: Self.multipart(image: pending.image, options: pending.options, boundary: boundary),
      headers: [
        "Content-Type": "multipart/form-data; boundary=\(boundary)", "Idempotency-Key": pending.key,
        "X-Scanpay-Client": "mobile",
      ].merging(pending.demoHeaders) { _, new in new })
    guard let id = response["scan_id"].string,
      id.range(of: "^scan-[a-zA-Z0-9-]+$", options: .regularExpression) != nil
    else {
      throw ClientFailure(
        "The Mac did not return a valid scan ID. Recover this upload to check acceptance.")
    }
    return id
  }
}

struct ExtractionProfile: Equatable {
  let id: String
  let version: String
}

enum TokenStore {
  private static let service = "com.azikus.scanpay.backend"
  static func read() -> String {
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
      kSecAttrAccount as String: "local-token", kSecReturnData as String: true,
      kSecMatchLimit as String: kSecMatchLimitOne,
    ]
    var result: CFTypeRef?
    guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
      let data = result as? Data
    else { return "" }
    return String(data: data, encoding: .utf8) ?? ""
  }
  static func save(_ token: String) throws {
    let query: [String: Any] = [
      kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
      kSecAttrAccount as String: "local-token",
    ]
    SecItemDelete(query as CFDictionary)
    if token.isEmpty { return }
    var item = query
    item[kSecValueData as String] = Data(token.utf8)
    item[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    guard SecItemAdd(item as CFDictionary, nil) == errSecSuccess else {
      throw ClientFailure("Could not save the local token securely.")
    }
  }
}

struct PendingScan: Codable {
  var key: String
  var scanID: String?
  var address: String
  let image: Data
  let options: Data
  var profileVersion: String?
  var response: Data?
  var selectedCandidateID: String?
  var editedValues: [String: JSONValue]?
  var editedFieldIDs: Set<String>?
  var confirmationID: String?
  var confirmationBody: Data?
  var serverID: String?
  var demoSessionID: String?
  var demoJourneyID: String?
  var demoHeaders: [String: String] {
    guard let sid = demoSessionID, UUID(uuidString: sid) != nil,
          let journey = demoJourneyID, UUID(uuidString: journey) != nil else { return [:] }
    return ["X-Scanpay-Demo-Session": sid, "X-Scanpay-Demo-Journey": journey]
  }
  var extractionProfile: ExtractionProfile? {
    guard let json = try? JSONDecoder().decode(JSONValue.self, from: options),
      let id = json["profiles"].array.first?.string
    else { return nil }
    guard
      let version = profileVersion ?? (id == BackendClient.profile ? BackendClient.version : nil)
    else { return nil }
    return ExtractionProfile(id: id, version: version)
  }
}

enum PendingStore {
  static var file: URL {
    FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appending(
      path: "pending-scan.json")
  }
  static func read(from file: URL = file) -> PendingScan? {
    guard let data = try? Data(contentsOf: file) else { return nil }
    return try? JSONDecoder().decode(PendingScan.self, from: data)
  }
  static func save(_ scan: PendingScan, to file: URL = file) throws {
    try FileManager.default.createDirectory(
      at: file.deletingLastPathComponent(), withIntermediateDirectories: true)
    try JSONEncoder().encode(scan).write(
      to: file, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
    var resource = file
    var values = URLResourceValues()
    values.isExcludedFromBackup = true
    try resource.setResourceValues(values)
  }
  static func clear(at file: URL = file) throws {
    if FileManager.default.fileExists(atPath: file.path) {
      try FileManager.default.removeItem(at: file)
    }
  }
}
