#if DEBUG
  import Foundation

  /// One-time setup copied by Xcode into this app's container. Never bundled with the app.
  struct DevelopmentConnection: Decodable {
    let addresses: [String]
    let token: String
    static var setupFile: URL {
      FileManager.default.temporaryDirectory.appending(path: "connection-setup.json")
    }
    static var resultFile: URL {
      PendingStore.file.deletingLastPathComponent().appending(path: "connection-check.json")
    }
    static func consume() throws -> Self? {
      guard FileManager.default.fileExists(atPath: setupFile.path) else { return nil }
      let data = try Data(contentsOf: setupFile)
      try FileManager.default.removeItem(at: setupFile)
      let setup = try JSONDecoder().decode(Self.self, from: data)
      guard !setup.addresses.isEmpty else { throw ClientFailure("Missing Mac address.") }
      for address in setup.addresses { _ = try BackendClient(address: address, token: setup.token) }
      return setup
    }
    @MainActor func apply(to model: ScanSession) async {
      do {
        guard let address = addresses.first(where: ScanSession.isHotspotAddress) else {
          throw ClientFailure("Missing hotspot address.")
        }
        try model.configureHotspot(address: address, token: token)
        await model.reconnect()
        let report: [String: Any] = [
          "selected_address": model.address, "attempts": model.connectionAttempts,
          "checked_at": ISO8601DateFormatter().string(from: Date()),
        ]
        try FileManager.default.createDirectory(
          at: Self.resultFile.deletingLastPathComponent(), withIntermediateDirectories: true)
        try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
          .write(
            to: Self.resultFile,
            options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
      } catch { model.message = "Connection setup could not be saved. Open Connection settings." }
    }
  }
#endif
