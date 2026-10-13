import UIKit
import XCTest

@testable import ScanAndPay

final class ScanAndPayTests: XCTestCase {
  func fixture() throws -> JSONValue {
    let url = try XCTUnwrap(
      Bundle.main.url(forResource: "uk-extract.synthetic", withExtension: "json"))
    return try JSONDecoder().decode(JSONValue.self, from: Data(contentsOf: url))
  }
  func testNullRoundTripAndLeadingZeros() throws {
    let json = try fixture()
    var draft = try PaymentDraft(response: json)
    let before = json.pretty
    draft.edit("/candidates/0/amount/value", value: "89,02")
    XCTAssertEqual(draft.values["/candidates/0/amount/value"], .string("89.02"))
    XCTAssertTrue(draft.canConfirm)
    XCTAssertFalse(draft.optionalFields.isEmpty)
    XCTAssertTrue(draft.visibleFields.allSatisfy { $0.value != nil })
    let account = try XCTUnwrap(draft.fields.first { $0.id.hasSuffix("/account_number") })
    XCTAssertEqual(account.value, "00000000")
    draft.edit(account.id, value: "00000123")
    XCTAssertEqual(draft.values[account.id]?.string, "00000123")
    draft.edit(account.id, value: "")
    XCTAssertEqual(draft.values[account.id], .null)
    XCTAssertTrue(draft.canConfirm)
    XCTAssertTrue(draft.paymentIssues.contains("Account number needs eight digits."))
    XCTAssertEqual(draft.response.pretty, before)
    let restored = try JSONDecoder().decode(
      JSONValue.self, from: JSONEncoder().encode(draft.confirmation))
    XCTAssertEqual(restored["values"][account.id], .null)
  }
  func testCandidateSwitchDoesNotMixFields() throws {
    let original = try fixture()
    var dict = original.object
    var run = original["runs"].array[0].object
    var payment = run["payment"]!.object
    var one = payment["candidates"]!.array[0].object
    var two = one
    one["id"] = .string("one")
    two["id"] = .string("two")
    var remittance = two["remittance"]!.object
    var reference = remittance["reference"]!.object
    reference["value"] = .string("000999")
    remittance["reference"] = .object(reference)
    two["remittance"] = .object(remittance)
    payment["candidates"] = .array([.object(one), .object(two)])
    payment["selected_candidate_id"] = .null
    run["payment"] = .object(payment)
    dict["runs"] = .array([.object(run)])
    var draft = try PaymentDraft(response: .object(dict))
    XCTAssertNil(draft.selectedID)
    XCTAssertFalse(draft.canConfirm)
    XCTAssertFalse(draft.fields.contains { $0.id.hasPrefix("/candidates/") })
    draft.select("one")
    draft.edit("/candidates/0/remittance/reference", value: "000777")
    draft.select("two")
    XCTAssertEqual(draft.values["/candidates/1/remittance/reference"], .string("000999"))
    XCTAssertFalse(draft.values.keys.contains { $0.hasPrefix("/candidates/0/") })
  }
  func testMultipartStableBytesAndNullJSON() throws {
    let image = Data([0, 1, 2, 3, 255])
    let options = Data("{\"mode\":\"extract\"}".utf8)
    let body = BackendClient.multipart(image: image, options: options, boundary: "boundary")
    XCTAssertNotNil(body.range(of: image))
    XCTAssertNotNil(body.range(of: options))
    XCTAssertNotNil(body.range(of: Data("name=\"image\"; filename=\"capture.png\"".utf8)))
    XCTAssertEqual(
      BackendClient.multipart(image: image, options: options, boundary: "boundary"), body)
    XCTAssertTrue(BackendClient.isLocal("192.168.1.12"))
    XCTAssertTrue(BackendClient.isLocal("my-mac.local"))
    XCTAssertFalse(BackendClient.isLocal("example.com"))
    XCTAssertFalse(BackendClient.isLocal("192.168.1.999"))
    XCTAssertThrowsError(try BackendClient(address: "http://example.com", token: "test"))
    XCTAssertThrowsError(try BackendClient(address: "https://example.com/path", token: "test"))
  }
  func testUnresolvedDestinationCanBeConfirmedWithAnExplicitWarning() throws {
    var response = try fixture().object
    var run = response["runs"]!.array[0].object
    var payment = run["payment"]!.object
    var candidate = payment["candidates"]!.array[0].object
    candidate["destination"] = .object(["kind": .string("unresolved")])
    payment["candidates"] = .array([.object(candidate)])
    run["payment"] = .object(payment)
    response["runs"] = .array([.object(run)])
    let draft = try PaymentDraft(response: .object(response))
    XCTAssertTrue(draft.canConfirm)
    XCTAssertTrue(draft.paymentIssues.contains("Bank destination was not identified."))
    XCTAssertEqual(draft.confirmation["simulated"], .bool(true))
    XCTAssertFalse(draft.values.keys.contains { $0.contains("/destination/iban") })
  }
  func testCropPreservesPixelDimensionsAndOrientation() throws {
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    let image = UIGraphicsImageRenderer(size: CGSize(width: 120, height: 80), format: format).image
    { c in
      UIColor.red.setFill()
      c.fill(CGRect(x: 0, y: 0, width: 120, height: 80))
    }
    let crop = try XCTUnwrap(image.cropped(to: CGRect(x: 0.25, y: 0.25, width: 0.5, height: 0.5)))
    XCTAssertEqual(crop.cgImage?.width, 60)
    XCTAssertEqual(crop.cgImage?.height, 40)
    let rotated = image.rotated()
    XCTAssertEqual(rotated.cgImage?.width, 80)
    XCTAssertEqual(rotated.cgImage?.height, 120)
    XCTAssertEqual(crop.imageOrientation, .up)
  }
  @MainActor func testResetPreventsLateFixtureResult() async throws {
    let model = ScanSession(fixtureMode: true)
    model.loadFixture()
    model.reset()
    try await Task.sleep(for: .milliseconds(700))
    XCTAssertEqual(model.phase, .capture)
    XCTAssertNil(model.draft)
    XCTAssertNil(model.response)
  }
  func testOnlyObservedDocumentValuesPopulateNewDrafts() throws {
    let source = try fixture()
    let path = "/candidates/0/amount/currency"
    let original = try XCTUnwrap(
      PaymentDraft(response: source).relevantObservations.first { $0.0 == path }?.1)
    let cases: [(String, String, [String], Bool)] = [
      ("observed", "document", ["explicit_currency_token"], true),
      ("inferred", "document", [], false),
      ("observed", "derived", [], false),
      ("observed", "caller_hint", [], false),
      ("observed", "barcode", [], false),
      ("ambiguous", "document", [], false),
      ("unreadable", "document", [], false),
      ("unsupported", "document", [], false),
      ("observed", "document", ["draft_beneficiary_from_supplier"], false),
      ("observed", "document", ["draft_beneficiary_from_account_holder"], false),
    ]
    for (state, origin, normalization, extracted) in cases {
      var observation = original.object
      observation["state"] = .string(state)
      observation["origin"] = .string(origin)
      observation["normalization"] = .array(normalization.map(JSONValue.string))
      let response = source.replacingPayment(path, with: .object(observation))
      let draft = try PaymentDraft(response: response)
      XCTAssertEqual(draft.values[path], extracted ? .string("GBP") : .null)
      XCTAssertEqual(draft.confirmation["values"][path], extracted ? .string("GBP") : .null)
      XCTAssertEqual(draft.values.count, draft.relevantObservations.count)
      XCTAssertEqual(draft.response, response)
      XCTAssertEqual(draft.optionLabel(at: 0).contains("GBP"), extracted)
    }
  }
  func testExplicitEditOfInferredValueSurvivesRestorationEvenWhenTextMatches() throws {
    let path = "/candidates/0/amount/currency"
    let source = try fixture().replacingPayment(path + "/state", with: .string("inferred"))
    var draft = try PaymentDraft(response: source)
    XCTAssertNil(draft.currencyField)
    draft.edit(path, value: "GBP")
    var restored = try PaymentDraft(response: source)
    restored.restore(
      values: draft.values, selectedID: draft.selectedID, editedFieldIDs: draft.editedFieldIDs)
    XCTAssertEqual(restored.currencyField?.value, "GBP")
    XCTAssertEqual(restored.currencyField?.isEdited, true)
    XCTAssertEqual(restored.response, source)
    restored.edit(path, value: "")
    XCTAssertNil(restored.currencyField)
    XCTAssertEqual(restored.confirmation["values"][path], .null)
    restored.edit("/not-a-field", value: "ignored")
    XCTAssertNil(restored.values["/not-a-field"])
  }
  func testLegacyDraftDropsUntouchedInferenceButPreservesCorrections() throws {
    let path = "/candidates/0/amount/currency"
    let source = try fixture().replacingPayment(path + "/state", with: .string("inferred"))
    var draft = try PaymentDraft(response: source)
    var legacyValues = Dictionary(
      uniqueKeysWithValues: draft.relevantObservations.map { ($0.0, $0.1["value"]) })
    legacyValues["/invoice_number"] = .string("EDITED-42")
    legacyValues["/candidates/1/beneficiary_name"] = .string("Unselected")
    draft.restore(values: legacyValues, selectedID: draft.selectedID, editedFieldIDs: nil)
    XCTAssertNil(draft.currencyField)
    XCTAssertEqual(draft.values["/invoice_number"], .string("EDITED-42"))
    XCTAssertTrue(draft.editedFieldIDs.contains("/invoice_number"))
    XCTAssertNil(draft.values["/candidates/1/beneficiary_name"])
    legacyValues[path] = .string("EUR")
    draft.restore(values: legacyValues, selectedID: draft.selectedID, editedFieldIDs: nil)
    XCTAssertEqual(draft.currencyField?.value, "EUR")
    XCTAssertEqual(draft.currencyField?.isEdited, true)
  }
  func testConfirmationDisplaysEveryNonNullValueExactlyOnce() throws {
    var draft = try PaymentDraft(response: fixture())
    for (path, value) in [
      "/customer_number": "000123", "/due_date": "2026-10-31",
      "/candidates/0/remittance/model": "HR00", "/candidates/0/remittance/purpose_code": "OTHR",
      "/document_context/language": "en",
    ] { draft.edit(path, value: value) }
    func check(_ draft: PaymentDraft, file: StaticString = #filePath, line: UInt = #line) {
      let hero = [
        draft.amountField, draft.recipientField,
        draft.amountField == nil ? nil : draft.currencyField,
      ].compactMap { $0 }
      let fields = hero + draft.confirmationSections.flatMap(\.fields)
      XCTAssertEqual(fields.count, Set(fields.map(\.id)).count, file: file, line: line)
      XCTAssertEqual(
        Set(fields.map(\.id)), Set(draft.values.filter { $0.value != .null }.keys), file: file,
        line: line)
    }
    check(draft)
    XCTAssertEqual(draft.confirmationSections.map(\.title), ["Payment details", "Invoice details"])
    XCTAssertTrue(draft.confirmationSections[0].fields.contains { $0.label == "Account holder" })
    XCTAssertTrue(draft.confirmationSections[1].fields.contains { $0.label == "Invoice number" })
    draft.edit("/candidates/0/amount/value", value: "")
    check(draft)
    XCTAssertTrue(draft.confirmationSections[0].fields.contains { $0.label == "Currency" })
  }
  func testInferenceOnlyDraftCannotConfirmUntilUserAddsDetails() throws {
    var source = try fixture()
    let baseline = try PaymentDraft(response: source)
    for (path, _) in baseline.relevantObservations {
      source = source.replacingPayment(path + "/state", with: .string("inferred"))
    }
    var draft = try PaymentDraft(response: source)
    XCTAssertTrue(draft.visibleFields.isEmpty)
    XCTAssertFalse(draft.canConfirm)
    XCTAssertEqual(draft.optionLabel(at: 0), "Option 1 · Amount unknown")
    draft.edit("/candidates/0/amount/value", value: "12.34")
    XCTAssertTrue(draft.canConfirm)
    XCTAssertTrue(draft.paymentIssues.contains("Currency is missing or invalid."))
  }

  func testRequiredAndOptionalDetailsForSavedIBANDraft() throws {
    let empty: JSONValue = .object([
      "value": .null, "state": .string("missing"), "origin": .string("document"),
    ])
    let iban: JSONValue = .object([
      "value": .string("HR1210010051863000160"), "state": .string("observed"),
      "origin": .string("document"),
    ])
    let source = try fixture().replacingPayment(
      "/candidates/0/destination",
      with: .object([
        "kind": .string("iban"), "iban": iban, "bic": empty,
      ]))
    var draft = try PaymentDraft(response: source)
    XCTAssertFalse(draft.fields.contains { $0.id.hasSuffix("/sort_code") })
    XCTAssertTrue(draft.optionalFields.contains { $0.id.hasSuffix("/bic") })
    XCTAssertFalse(draft.missingFields.contains { $0.id.hasSuffix("/bic") })
    let bic = try XCTUnwrap(draft.fields.first { $0.id.hasSuffix("/bic") })
    XCTAssertFalse(draft.shouldShow(bic, optional: false))
    XCTAssertTrue(draft.shouldShow(bic, optional: true))
    draft.edit("/candidates/0/destination/iban", value: "")
    XCTAssertTrue(draft.missingFields.contains { $0.id.hasSuffix("/iban") })
    XCTAssertTrue(draft.paymentIssues.contains("IBAN is missing."))
    XCTAssertEqual(draft.confirmation["values"]["/candidates/0/destination/bic"], .null)
  }

  func testBackendGuidanceDoesNotHidePopulatedOrEditedFields() throws {
    var source = try fixture().object
    var run = source["runs"]!.array[0].object
    let payment = run["payment"]!
    let candidateID = payment["candidates"].array[0]["id"]
    let path = "/candidates/0/destination/sort_code"
    run["review_guidance"] = .object([
      "issuer_country": .object(["label": .string("Croatia"), "status": .string("inferred")]),
      "language": .object(["label": .string("English")]),
      "candidates": .array([
        .object([
          "candidate_id": candidateID,
          "fields": .object([path: .object(["requirement": .string("not_applicable")])]),
        ])
      ]),
    ])
    source["runs"] = .array([.object(run)])
    var draft = try PaymentDraft(response: .object(source))
    XCTAssertEqual(draft.contextSummary, "Issuer: Croatia (suggested) · Language: English")
    XCTAssertTrue(
      draft.shouldShow(try XCTUnwrap(draft.fields.first { $0.id == path }), optional: false))
    draft.edit(path, value: "")
    XCTAssertTrue(
      draft.shouldShow(try XCTUnwrap(draft.fields.first { $0.id == path }), optional: false))
    XCTAssertFalse(draft.missingFields.contains { $0.id == path })
    XCTAssertEqual(draft.values[path], .null)
    XCTAssertNotNil(
      draft.response["runs"].array[0]["payment"]["candidates"].array[0]["destination"]["sort_code"][
        "value"
      ].string)
  }

  func testUnreadableOptionalFieldRemainsVisibleForReview() throws {
    let source = try fixture().replacingPayment("/due_date/state", with: .string("unreadable"))
      .replacingPayment("/due_date/value", with: .null)
    let draft = try PaymentDraft(response: source)
    let field = try XCTUnwrap(draft.fields.first { $0.id == "/due_date" })
    XCTAssertTrue(draft.shouldShow(field, optional: false))
    XCTAssertFalse(draft.missingFields.contains { $0.id == field.id })
  }

}

extension JSONValue {
  func replacingPayment(_ path: String, with value: JSONValue) -> JSONValue {
    replacing(["runs", "0", "payment"] + path.split(separator: "/").map(String.init), with: value)
  }
  private func replacing(_ path: [String], with value: JSONValue) -> JSONValue {
    guard let first = path.first else { return value }
    let tail = Array(path.dropFirst())
    switch self {
    case .object(var object):
      object[first] = (object[first] ?? .null).replacing(tail, with: value)
      return .object(object)
    case .array(var array):
      guard let index = Int(first), array.indices.contains(index) else { return self }
      array[index] = array[index].replacing(tail, with: value)
      return .array(array)
    default: return self
    }
  }
}
