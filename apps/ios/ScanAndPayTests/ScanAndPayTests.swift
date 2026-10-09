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
    XCTAssertFalse(draft.missingFields.isEmpty)
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
}
