import XCTest

final class ScanAndPayUITests: XCTestCase {
  func testCaptureCropReviewAndReset() throws {
    let app = XCUIApplication()
    app.launchArguments = ["-synthetic-preview"]
    app.launch()
    XCTAssertTrue(app.staticTexts["Synthetic preview"].waitForExistence(timeout: 10))
    app.buttons["capture"].tap()
    app.buttons["use-crop"].tap()
    XCTAssertTrue(app.buttons["send-image"].exists)
    app.buttons["send-image"].tap()
    XCTAssertTrue(app.staticTexts["Review details"].waitForExistence(timeout: 10))
    let review = XCTAttachment(screenshot: app.screenshot())
    review.name = "iPhone 16 Pro review sheet"
    review.lifetime = .keepAlways
    add(review)
    XCTAssertFalse(app.textFields["/due_date"].exists)
    app.buttons["Scan options"].tap()
    app.buttons["View JSON"].tap()
    XCTAssertTrue(app.staticTexts["Structured output"].waitForExistence(timeout: 5))
    let original = app.textViews.firstMatch
    XCTAssertTrue(original.waitForExistence(timeout: 5))
    XCTAssertTrue((original.value as? String)?.contains("final_result_id") == true)
    XCTAssertLessThanOrEqual(original.frame.maxX, app.frame.maxX + 1)
    app.buttons["Mobile values"].tap()
    XCTAssertTrue((original.value as? String)?.contains("review_confirmed") == true)
    app.buttons["Original JSON"].tap()
    XCTAssertTrue((original.value as? String)?.contains("final_result_id") == true)
    app.buttons["Done"].tap()
    XCTAssertFalse(app.buttons["pay"].isEnabled)
    app.switches["review-confirmation"].tap()
    XCTAssertTrue(app.buttons["pay"].isEnabled)
    do {
      app.buttons["pay"].tap()
      XCTAssertTrue(app.buttons["confirm-pay"].waitForExistence(timeout: 5))
      let confirmation = XCTAttachment(screenshot: app.screenshot())
      confirmation.name = "Payment confirmation"
      confirmation.lifetime = .keepAlways
      add(confirmation)
      let confirmationScroll = app.scrollViews["confirmation-details"]
      for _ in 0..<5 {
        if app.staticTexts["confirmation-field-/invoice_number"].isHittable { break }
        confirmationScroll.swipeUp()
      }
      XCTAssertEqual(app.staticTexts["confirmation-field-/invoice_number"].label, "DEMO-UK-42")
      XCTAssertTrue(app.staticTexts["Invoice details"].exists)
      XCTAssertFalse(app.staticTexts["confirmation-field-/due_date"].exists)
      let invoice = XCTAttachment(screenshot: app.screenshot())
      invoice.name = "Confirmation invoice details"
      invoice.lifetime = .keepAlways
      add(invoice)
      app.buttons["cancel-pay"].tap()
      XCTAssertTrue(app.buttons["pay"].waitForExistence(timeout: 5))
      app.buttons["pay"].tap()
      app.buttons["confirm-pay"].tap()
      XCTAssertTrue(app.staticTexts["complete"].waitForExistence(timeout: 5))
      let celebration = XCTAttachment(screenshot: app.screenshot())
      celebration.name = "Completion animation"
      celebration.lifetime = .keepAlways
      add(celebration)
      if app.buttons["scan-another"].exists { app.buttons["scan-another"].tap() }
      XCTAssertTrue(app.buttons["capture"].exists)
    }
    let attachment = XCTAttachment(screenshot: app.screenshot())
    attachment.name = "iPhone review flow"
    attachment.lifetime = .keepAlways
    add(attachment)
  }
  func testMissingFieldCanBeAddedWithoutLosingKeyboardFocus() {
    let app = XCUIApplication()
    app.launchArguments = ["-synthetic-preview"]
    app.launch()
    app.buttons["capture"].tap()
    app.buttons["use-crop"].tap()
    app.buttons["send-image"].tap()
    XCTAssertTrue(app.staticTexts["Review details"].waitForExistence(timeout: 10))
    let scroll = app.scrollViews.firstMatch
    for _ in 0..<8 {
      if app.buttons["missing-details"].isHittable { break }
      scroll.swipeUp()
    }
    app.buttons["missing-details"].tap()
    let due = app.textFields["/due_date"]
    for _ in 0..<8 {
      if due.isHittable { break }
      scroll.swipeUp()
    }
    XCTAssertTrue(due.isHittable)
    due.tap()
    due.typeText("2026-10-31")
    XCTAssertEqual(due.value as? String, "2026-10-31")
    // Dismiss the keyboard, then confirm the added field remains visible and marked as edited.
    scroll.swipeDown()
    app.switches["review-confirmation"].tap()
    app.buttons["pay"].tap()
    XCTAssertTrue(app.buttons["confirm-pay"].waitForExistence(timeout: 5))
    let confirmation = app.scrollViews["confirmation-details"]
    let added = app.staticTexts["confirmation-field-/due_date"]
    for _ in 0..<8 {
      if added.isHittable { break }
      confirmation.swipeUp()
    }
    XCTAssertTrue(added.isHittable)
    XCTAssertEqual(added.label, "2026-10-31")
    XCTAssertTrue(app.staticTexts["Edited"].exists)
    let attachment = XCTAttachment(screenshot: app.screenshot())
    attachment.name = "Edited invoice detail confirmation"
    attachment.lifetime = .keepAlways
    add(attachment)
  }

}
