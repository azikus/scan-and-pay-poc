import Foundation

/// A bounded, optional observer. Its failures never enter the scan's error path.
@MainActor final class DemoTelemetry {
  let sessionID: String
  private let defaults: UserDefaults
  private let session: URLSession
  private var heartbeat: Task<Void, Never>?
  private var sending: Task<Void, Never>?
  private var address = ""
  private var token = ""
  private var phase = "idle"
  private var journey: String?
  private var enabled = false

  init(defaults: UserDefaults, session: URLSession? = nil) {
    self.defaults = defaults
    sessionID = defaults.string(forKey: "demoSessionID") ?? UUID().uuidString.lowercased()
    defaults.set(sessionID, forKey: "demoSessionID")
    if let session { self.session = session } else {
      let config = URLSessionConfiguration.ephemeral
      config.urlCache = nil
      config.timeoutIntervalForRequest = 2
      config.timeoutIntervalForResource = 3
      self.session = URLSession(configuration: config, delegate: NoRedirects(), delegateQueue: nil)
    }
  }
  deinit { heartbeat?.cancel(); sending?.cancel() }

  func update(enabled: Bool, address: String, token: String, phase: String, journey: String?) {
    self.enabled = enabled
    self.address = address
    self.token = token
    self.phase = phase
    self.journey = journey
    heartbeat?.cancel()
    sending?.cancel()
    guard enabled else { return }
    publish()
    guard phase != "paused" else { return }
    heartbeat = Task { [weak self] in
      while !Task.isCancelled {
        do { try await Task.sleep(for: .seconds(8)) } catch { return }
        self?.publish()
      }
    }
  }
  private func publish() {
    guard enabled, let client = try? BackendClient(address: address, token: token, session: session)
    else { return }
    let sequence = defaults.integer(forKey: "demoSequence") + 1
    defaults.set(sequence, forKey: "demoSequence")
    struct Snapshot: Encodable { let sequence: Int; let journey_id: String?; let phase: String }
    guard let body = try? JSONEncoder().encode(Snapshot(sequence: sequence, journey_id: journey, phase: phase)) else { return }
    let path = "v1/demo/sessions/" + sessionID
    sending?.cancel()
    sending = Task {
      _ = try? await client.request(path, method: "PUT", body: body,
                                   headers: ["Content-Type": "application/json"])
    }
  }
}
