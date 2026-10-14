import Foundation

// The complete wire response stays intact. This value type preserves explicit JSON nulls.
indirect enum JSONValue: Codable, Equatable {
  case object([String: JSONValue])
  case array([JSONValue])
  case string(String)
  case number(Decimal)
  case bool(Bool)
  case null
  init(from decoder: Decoder) throws {
    let c = try decoder.singleValueContainer()
    if c.decodeNil() {
      self = .null
    } else if let v = try? c.decode(Bool.self) {
      self = .bool(v)
    } else if let v = try? c.decode(String.self) {
      self = .string(v)
    } else if let v = try? c.decode(Decimal.self) {
      self = .number(v)
    } else if let v = try? c.decode([String: JSONValue].self) {
      self = .object(v)
    } else {
      self = .array(try c.decode([JSONValue].self))
    }
  }
  func encode(to encoder: Encoder) throws {
    var c = encoder.singleValueContainer()
    switch self {
    case .null: try c.encodeNil()
    case .object(let v): try c.encode(v)
    case .array(let v): try c.encode(v)
    case .string(let v): try c.encode(v)
    case .number(let v): try c.encode(v)
    case .bool(let v): try c.encode(v)
    }
  }
  subscript(_ key: String) -> JSONValue {
    if case .object(let v) = self { return v[key] ?? .null }
    return .null
  }
  var string: String? {
    if case .string(let v) = self { return v }
    return nil
  }
  var array: [JSONValue] {
    if case .array(let v) = self { return v }
    return []
  }
  var object: [String: JSONValue] {
    if case .object(let v) = self { return v }
    return [:]
  }
  var pretty: String {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys, .withoutEscapingSlashes]
    return (try? String(data: encoder.encode(self), encoding: .utf8)) ?? "null"
  }
}

struct DraftField: Identifiable, Equatable {
  let id: String
  let label: String
  let original: String?
  let observation: JSONValue
  var value: String?
  var isEdited = false
  var isAmount: Bool { id.hasSuffix("/amount/value") }
  var numeric: Bool { isAmount || id.hasSuffix("/sort_code") || id.hasSuffix("/account_number") }
}

struct DraftSection: Identifiable {
  let id: String
  let title: String
  let fields: [DraftField]
}

struct PaymentDraft {
  let response: JSONValue
  let run: JSONValue
  let payment: JSONValue
  var selectedID: String?
  private(set) var values: [String: JSONValue] = [:]
  private(set) var editedFieldIDs = Set<String>()
  static let documentKeys = [
    "supplier_name", "invoice_number", "customer_number", "description", "due_date",
  ]
  static let labels = [
    "supplier_name": "Supplier", "invoice_number": "Invoice number",
    "customer_number": "Customer number", "description": "Description", "due_date": "Due date",
    "beneficiary_name": "Recipient", "account_holder_name": "Account holder",
    "account_country": "Account country", "value": "Amount", "currency": "Currency",
    "sort_code": "Sort code", "account_number": "Account number", "iban": "IBAN", "bic": "BIC",
    "reference": "Payment reference", "model": "Payment model", "purpose_code": "Purpose code",
    "scheme": "Biller scheme", "biller_code": "Biller code",
    "language": "Document language",
    "option_label": "Payment option", "payment_condition": "When to use this payment",
    "notice_number": "pagoPA notice number", "creditor_tax_code": "Creditor tax code",
    "bill_reference": "CBILL bill reference",
    "issuer_country": "Issuer country",
  ]
  init(response: JSONValue) throws {
    guard let finalID = response["final_result_id"].string,
      let run = response["runs"].array.first(where: { $0["id"].string == finalID }),
      case .object = run["payment"]
    else { throw ClientFailure("This scan has no reviewable payment details.") }
    self.response = response
    self.run = run
    self.payment = run["payment"]
    selectedID = payment["selected_candidate_id"].string
    if let selectedID,
      !payment["candidates"].array.contains(where: { $0["id"].string == selectedID })
    {
      throw ClientFailure("The result refers to an unknown payment option.")
    }
    resetValues()
  }
  var candidates: [JSONValue] { payment["candidates"].array }
  var candidateIndex: Int? {
    candidates.firstIndex { $0["id"].string == selectedID && selectedID != nil }
  }
  var candidate: JSONValue { candidateIndex.map { candidates[$0] } ?? .null }
  var prefix: String { "/candidates/\(candidateIndex ?? -1)" }
  var guidance: JSONValue { run["review_guidance"] }
  var candidateGuidance: JSONValue {
    guidance["candidates"].array.first { $0["candidate_id"].string == selectedID } ?? .null
  }
  var reasons: [JSONValue] {
    payment["review"]["reasons"].array.filter {
      if $0["code"].string == "payment_option_required" && candidateIndex != nil { return false }
      let path = $0["path"].string ?? ""
      return !path.hasPrefix("/candidates/") || candidateIndex == nil
        || path.hasPrefix(prefix + "/")
    }
  }
  var paymentChannelSummary: String? {
    let channels = candidateGuidance["payment_channels"].array.compactMap { $0.string }
    let note = candidateGuidance["payment_note"].string
    let title =
      channels.isEmpty ? nil : "Payment service: " + channels.joined(separator: ", ")
    let condition = values[prefix + "/payment_condition"]?.string.map { "When to use: " + $0 }
    let parts = [condition, title, note].compactMap { $0 }
    return parts.isEmpty ? nil : parts.joined(separator: ". ")
  }
  var contextSummary: String? {
    let country = guidance["issuer_country"]
    let language = guidance["language"]
    var parts: [String] = []
    if let name = country["label"].string {
      parts.append("Issuer: \(name)\(country["status"].string == "observed" ? "" : " (suggested)")")
    }
    if let name = language["label"].string { parts.append("Language: \(name)") }
    return parts.isEmpty ? nil : parts.joined(separator: " · ")
  }
  var outcome: String {
    if let value = run["outcome"].string { return value }
    let useful = Self.observations(payment, path: "").filter {
      !$0.0.hasPrefix("/document_context/")
    }
    if !useful.contains(where: {
      $0.1["value"].string != nil || $0.1["raw_text"].string != nil
        || !$0.1["alternatives"].array.isEmpty
    }) {
      return "error"
    }
    return payment["review"]["state"].string == "ready_for_review" ? "success" : "incomplete"
  }
  static func observations(_ node: JSONValue, path: String) -> [(String, JSONValue)] {
    if node["state"].string != nil && node.object.keys.contains("value") { return [(path, node)] }
    switch node {
    case .object(let dict):
      return dict.keys.sorted().flatMap { observations(dict[$0]!, path: path + "/" + $0) }
    case .array(let array):
      return array.enumerated().flatMap { observations($0.element, path: path + "/\($0.offset)") }
    default: return []
    }
  }
  var relevantObservations: [(String, JSONValue)] {
    Self.observations(payment, path: "").filter { path, _ in
      !path.hasPrefix("/candidates/") || (candidateIndex != nil && path.hasPrefix(prefix + "/"))
    }
  }
  static func isExtracted(_ observation: JSONValue) -> Bool {
    // A copied supplier/account-holder observation still has document provenance,
    // but the draft policy inferred its role as the payment recipient.
    observation["state"].string == "observed"
      && observation["origin"].string == "document"
      && !observation["normalization"].array.contains {
        $0.string?.hasPrefix("draft_beneficiary_from_") == true
      }
  }
  mutating func resetValues() {
    editedFieldIDs = []
    values = Dictionary(
      uniqueKeysWithValues: relevantObservations.map {
        ($0.0, Self.isExtracted($0.1) ? $0.1["value"] : .null)
      })
  }
  mutating func restore(
    values saved: [String: JSONValue], selectedID: String?, editedFieldIDs: Set<String>?
  ) {
    self.selectedID = selectedID
    resetValues()
    for (path, observation) in relevantObservations {
      guard let value = saved[path], value == .null || value.string != nil else { continue }
      // Legacy snapshots saved every value; only a difference proves an edit in those drafts.
      let edited = editedFieldIDs.map { $0.contains(path) } ?? (value != observation["value"])
      if Self.isExtracted(observation) || edited {
        values[path] = value
        if edited { self.editedFieldIDs.insert(path) }
      }
    }
  }
  mutating func select(_ id: String) {
    selectedID = id
    resetValues()
  }
  func field(_ path: String, observation: JSONValue) -> DraftField {
    let key = path.split(separator: "/").last.map(String.init) ?? path
    let scheme = candidate["destination"]["scheme"]["value"].string?.lowercased() ?? ""
    let label =
      key == "biller_code" && ["pagopa", "cbill"].contains(scheme)
      ? "CBILL organisation code" : Self.labels[key] ?? key
    return DraftField(
      id: path, label: label, original: observation["value"].string,
      observation: observation, value: values[path]?.string,
      isEdited: editedFieldIDs.contains(path))
  }
  var fields: [DraftField] {
    let order =
      [
        "beneficiary_name", "value", "currency", "iban", "sort_code", "account_number", "reference",
        "model", "account_holder_name", "bic", "purpose_code", "scheme", "notice_number",
        "creditor_tax_code", "biller_code", "bill_reference",
        "account_country",
      ] + Self.documentKeys + ["language", "issuer_country"]
    return relevantObservations.map { field($0.0, observation: $0.1) }.sorted {
      (order.firstIndex(of: $0.id.split(separator: "/").last.map(String.init) ?? "") ?? 99)
        < (order.firstIndex(of: $1.id.split(separator: "/").last.map(String.init) ?? "") ?? 99)
    }
  }
  var visibleFields: [DraftField] { fields.filter { $0.value != nil } }
  func requirement(for path: String) -> String {
    let rule =
      path.hasPrefix("/candidates/")
      ? candidateGuidance["fields"][path] : guidance["document_fields"][path]
    if let requirement = rule["requirement"].string { return requirement }
    // Old saved drafts and older servers retain a conservative route-based fallback.
    let required = ["/beneficiary_name", "/amount/value", "/amount/currency"]
    if required.contains(where: { path == prefix + $0 }) { return "required" }
    let kind = candidate["destination"]["kind"].string
    if kind == "uk_domestic"
      && ["/destination/sort_code", "/destination/account_number"].contains(where: {
        path == prefix + $0
      })
    {
      return "required"
    }
    if kind == "iban" && path == prefix + "/destination/iban" { return "required" }
    if kind == "biller_reference" {
      let scheme = candidate["destination"]["scheme"]["value"].string?.lowercased()
      let names =
        scheme == "pagopa"
        ? ["scheme", "notice_number", "creditor_tax_code"]
        : scheme == "cbill"
          ? ["scheme", "biller_code", "bill_reference"] : ["scheme", "biller_code"]
      if names.contains(where: { path == prefix + "/destination/" + $0 }) { return "required" }
    }
    if path == prefix + "/remittance/reference" {
      switch candidate["remittance"]["reference_requirement"].string {
      case "required": return "required"
      case "not_stated": return "optional"
      default: return "unresolved"
      }
    }
    if path == prefix + "/remittance/model"
      && candidate["remittance"]["model"]["state"].string != "missing"
    {
      return "required"
    }
    return "optional"
  }
  var missingFields: [DraftField] {
    fields.filter { $0.value == nil && requirement(for: $0.id) == "required" }
  }
  var optionalFields: [DraftField] {
    fields.filter { $0.value == nil && requirement(for: $0.id) == "optional" }
  }
  func shouldShow(_ field: DraftField, optional: Bool) -> Bool {
    if field.value != nil || field.isEdited { return true }
    if ["unreadable", "ambiguous", "unsupported"].contains(field.observation["state"].string ?? "")
    {
      return true
    }
    let requirement = requirement(for: field.id)
    return requirement == "required" || requirement == "unresolved"
      || (optional && requirement == "optional")
  }
  func sections(for fields: [DraftField]) -> [DraftSection] {
    [
      DraftSection(
        id: "payment", title: "Payment details",
        fields: fields.filter { $0.id.hasPrefix("/candidates/") }),
      DraftSection(
        id: "invoice", title: "Invoice details",
        fields: fields.filter { !$0.id.hasPrefix("/candidates/") }),
    ].filter { !$0.fields.isEmpty }
  }
  var amountField: DraftField? { visibleFields.first { $0.id == prefix + "/amount/value" } }
  var currencyField: DraftField? { visibleFields.first { $0.id == prefix + "/amount/currency" } }
  var recipientField: DraftField? { visibleFields.first { $0.id == prefix + "/beneficiary_name" } }
  var confirmationSections: [DraftSection] {
    let highlighted = Set(
      [recipientField?.id, amountField?.id, amountField == nil ? nil : currencyField?.id]
        .compactMap { $0 })
    return sections(for: visibleFields.filter { !highlighted.contains($0.id) })
  }
  func optionLabel(at index: Int) -> String {
    let amount = candidates[index]["amount"]
    let value = Self.isExtracted(amount["value"]) ? amount["value"]["value"].string : nil
    let currency = Self.isExtracted(amount["currency"]) ? amount["currency"]["value"].string : nil
    let label = candidates[index]["option_label"]["value"].string ?? "Option \(index + 1)"
    let due = candidates[index]["due_date"]["value"].string.map { " · Due \($0)" } ?? ""
    return "\(label) · \(value ?? "Amount unknown") \(currency ?? "")\(due)"
      .trimmingCharacters(in: .whitespaces)
  }
  mutating func edit(_ path: String, value: String) {
    guard values.keys.contains(path) else { return }
    // Decimal keyboards can emit a comma; the wire amount remains a decimal string.
    let value =
      path.hasSuffix("/amount/value") ? value.replacingOccurrences(of: ",", with: ".") : value
    values[path] =
      value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? .null : .string(value)
    editedFieldIDs.insert(path)
  }
  var canConfirm: Bool {
    candidateIndex != nil && outcome != "error"
      && visibleFields.contains { !$0.id.hasPrefix("/document_context/") }
  }
  var paymentIssues: [String] {
    guard candidateIndex != nil else { return ["Choose a payment option."] }
    func v(_ key: String) -> String { values[prefix + key]?.string ?? "" }
    var issues: [String] = []
    if v("/beneficiary_name").isEmpty { issues.append("Recipient is missing.") }
    if let amount = Decimal(string: v("/amount/value"), locale: Locale(identifier: "en_US_POSIX")),
      amount > 0,
      v("/amount/value").range(of: "^[0-9]+\\.[0-9]{2}$", options: .regularExpression) != nil
    {
    } else {
      issues.append("Enter an amount greater than zero with two decimal places.")
    }
    if v("/amount/currency").range(of: "^[A-Z]{3}$", options: .regularExpression) == nil {
      issues.append("Currency is missing or invalid.")
    }
    switch candidate["destination"]["kind"].string {
    case "uk_domestic":
      if v("/destination/sort_code").range(of: "^[0-9]{6}$", options: .regularExpression) == nil {
        issues.append("Sort code needs six digits.")
      }
      if v("/destination/account_number").range(of: "^[0-9]{8}$", options: .regularExpression)
        == nil
      {
        issues.append("Account number needs eight digits.")
      }
    case "iban":
      if v("/destination/iban").isEmpty { issues.append("IBAN is missing.") }
    case "biller_reference":
      let scheme = v("/destination/scheme").trimmingCharacters(in: .whitespacesAndNewlines)
        .lowercased()
      func checkIdentifier(_ name: String, _ pattern: String, _ message: String) {
        let raw = v("/destination/" + name)
        let value =
          name == "bill_reference"
          ? raw.trimmingCharacters(in: .whitespacesAndNewlines)
          : raw.components(separatedBy: .whitespacesAndNewlines).joined().uppercased()
        if value.range(of: pattern, options: .regularExpression) == nil { issues.append(message) }
      }
      if scheme == "pagopa" {
        checkIdentifier("notice_number", "^[0-9]{18}$", "pagoPA notice number needs 18 digits.")
        if !v("/destination/creditor_tax_code").isEmpty || v("/destination/biller_code").isEmpty {
          checkIdentifier(
            "creditor_tax_code", "^[0-9]{11}$",
            "Provide the creditor tax code or CBILL organisation code.")
        }
        if !v("/destination/biller_code").isEmpty {
          checkIdentifier(
            "biller_code", "^[A-Z0-9]{5}$", "CBILL organisation code needs five letters or digits.")
        }
      } else if scheme == "cbill" {
        checkIdentifier(
          "biller_code", "^[A-Z0-9]{5}$", "CBILL organisation code needs five letters or digits.")
        checkIdentifier("bill_reference", "^.+$", "CBILL bill reference is missing.")
      } else {
        issues.append("Biller payment scheme needs review.")
      }
    default: issues.append("Bank destination was not identified.")
    }
    if candidate["remittance"]["reference_requirement"].string == "required"
      && v("/remittance/reference").isEmpty
    {
      issues.append("Payment reference is missing.")
    }
    return issues
  }
  var summaryAmount: String {
    let amount = values[prefix + "/amount/value"]?.string ?? "—"
    let currency = values[prefix + "/amount/currency"]?.string ?? ""
    return "\(amount) \(currency)".trimmingCharacters(in: .whitespaces)
  }
  var summaryRecipient: String {
    values[prefix + "/beneficiary_name"]?.string ?? "Recipient not identified"
  }
  var confirmation: JSONValue {
    .object([
      "schema_version": .string("1.0"), "run_id": run["id"],
      "selected_candidate_id": selectedID.map(JSONValue.string) ?? .null,
      "event": .string("review_confirmed"), "simulated": .bool(true), "values": .object(values),
    ])
  }
}

struct ClientFailure: LocalizedError {
  let message: String
  init(_ message: String) { self.message = message }
  var errorDescription: String? { message }
}
