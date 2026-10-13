import CoreImage
import SwiftUI
import Vision
import XCTest

@testable import ScanAndPay

final class DocumentScanningTests: XCTestCase {
  @MainActor func testNativeVisionDetectsSyntheticPaperAndRendersMask() throws {
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    let image = UIGraphicsImageRenderer(size: CGSize(width: 600, height: 800), format: format)
      .image { context in
        UIColor.darkGray.setFill()
        context.fill(CGRect(x: 0, y: 0, width: 600, height: 800))
        UIColor.white.setFill()
        context.fill(CGRect(x: 100, y: 80, width: 400, height: 640))
        ("SYNTHETIC DOCUMENT\n\nInvoice\n\nAmount 123.45\n\nNot payable" as NSString).draw(
          in: CGRect(x: 130, y: 120, width: 340, height: 540),
          withAttributes: [.font: UIFont.systemFont(ofSize: 24), .foregroundColor: UIColor.black])
      }
    let document = try XCTUnwrap(
      DocumentDetector.detect(
        in: VNImageRequestHandler(cgImage: XCTUnwrap(image.cgImage))))
    XCTAssertTrue(document.canCapture)
    XCTAssertEqual(document.topLeft.x, 100.0 / 600, accuracy: 0.04)
    XCTAssertEqual(document.topLeft.y, 0.9, accuracy: 0.04)
    let corrected = try XCTUnwrap(DocumentDetector.scannedImage(image, context: CIContext()))
    XCTAssertLessThan(corrected.size.width, image.size.width)
    XCTAssertLessThan(corrected.size.height, image.size.height)
    let renderer = ImageRenderer(
      content: ZStack {
        Image(uiImage: image).resizable().scaledToFit()
        DocumentPreviewMask(document: document, imageSize: image.size)
      }.frame(width: 300, height: 500))
    let mask = try XCTUnwrap(renderer.uiImage)
    for (name, result) in [
      ("Native Vision synthetic paper mask", mask),
      ("Native Vision corrected synthetic paper", corrected),
    ] {
      let attachment = XCTAttachment(image: result)
      attachment.name = name
      attachment.lifetime = .keepAlways
      add(attachment)
    }
  }
  private func paper(dx: CGFloat = 0, confidence: Float = 1) -> DocumentQuadrilateral {
    DocumentQuadrilateral(
      topLeft: CGPoint(x: 0.2 + dx, y: 0.8),
      topRight: CGPoint(x: 0.8 + dx, y: 0.8),
      bottomRight: CGPoint(x: 0.8 + dx, y: 0.2),
      bottomLeft: CGPoint(x: 0.2 + dx, y: 0.2), confidence: confidence)
  }

  func testSteadyDocumentCapturesOnceAndRetakeRearms() {
    var gate = DocumentCaptureGate()
    for time in [0.0, 0.2, 0.4, 0.6, 0.8] {
      XCTAssertFalse(gate.observe(paper(), at: time))
    }
    XCTAssertTrue(gate.observe(paper(), at: 1.0))
    XCTAssertFalse(gate.observe(paper(), at: 1.2))
    XCTAssertFalse(gate.observe(nil, at: 1.4))
    gate.reset()
    for time in [2.0, 2.2, 2.4, 2.6, 2.8] {
      XCTAssertFalse(gate.observe(paper(), at: time))
    }
    XCTAssertTrue(gate.observe(paper(), at: 3.0))
  }

  func testMotionLossAndStalledFramesRestartStability() {
    for interruption in 0..<3 {
      var gate = DocumentCaptureGate()
      for time in [0.0, 0.2, 0.4, 0.6] {
        XCTAssertFalse(gate.observe(paper(), at: time))
      }
      let time = interruption == 2 ? 1.6 : 0.8
      XCTAssertFalse(gate.observe(interruption == 1 ? nil : paper(dx: 0.05), at: time))
      XCTAssertFalse(gate.observe(paper(), at: time + 0.2))
      XCTAssertFalse(gate.observe(paper(), at: time + 0.4))
    }
    // Slow drift must be compared with the original anchor, not only the last frame.
    var gate = DocumentCaptureGate()
    for index in 0..<12 {
      XCTAssertFalse(gate.observe(paper(dx: CGFloat(index) * 0.008), at: Double(index) * 0.2))
    }
  }

  func testSmallClippedAndLowConfidenceDocumentsNeverCapture() {
    let tiny = DocumentQuadrilateral(
      topLeft: CGPoint(x: 0.4, y: 0.6),
      topRight: CGPoint(x: 0.6, y: 0.6),
      bottomRight: CGPoint(x: 0.6, y: 0.4),
      bottomLeft: CGPoint(x: 0.4, y: 0.4))
    for document in [tiny, paper(dx: 0.2), paper(confidence: 0.2)] {
      var gate = DocumentCaptureGate()
      for index in 0..<20 {
        XCTAssertFalse(gate.observe(document, at: Double(index) * 0.2))
      }
    }
  }

  func testPreviewMaskMatchesLetterboxingAndVisionOrigin() {
    let points = paper().previewCorners(
      imageSize: CGSize(width: 300, height: 400),
      viewport: CGSize(width: 300, height: 600))
    XCTAssertEqual(points[0].x, 60, accuracy: 0.01)
    XCTAssertEqual(points[0].y, 180, accuracy: 0.01)
    XCTAssertEqual(points[2].x, 240, accuracy: 0.01)
    XCTAssertEqual(points[2].y, 420, accuracy: 0.01)
    let landscape = paper().previewCorners(
      imageSize: CGSize(width: 400, height: 300),
      viewport: CGSize(width: 600, height: 300))
    XCTAssertEqual(landscape[0].x, 180, accuracy: 0.01)
    XCTAssertEqual(landscape[0].y, 60, accuracy: 0.01)
  }

  func testPerspectiveCorrectionKeepsTopAndBottomInOrder() throws {
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    let image = UIGraphicsImageRenderer(size: CGSize(width: 400, height: 600), format: format)
      .image { context in
        UIColor.red.setFill()
        context.fill(CGRect(x: 0, y: 0, width: 400, height: 300))
        UIColor.blue.setFill()
        context.fill(CGRect(x: 0, y: 300, width: 400, height: 300))
      }
    let scanned = try XCTUnwrap(
      DocumentDetector.correctedImage(
        image, document: paper(),
        context: CIContext()))
    XCTAssertEqual(scanned.imageOrientation, .up)
    XCTAssertEqual(scanned.size.width, 244, accuracy: 3)
    XCTAssertEqual(scanned.size.height, 366, accuracy: 3)
    let cgImage = try XCTUnwrap(scanned.cgImage)
    let pixels = CIImage(cgImage: cgImage)
    var top = [UInt8](repeating: 0, count: 4)
    var bottom = top
    let context = CIContext()
    context.render(
      pixels, toBitmap: &top, rowBytes: 4,
      bounds: CGRect(x: 10, y: cgImage.height - 10, width: 1, height: 1),
      format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())
    context.render(
      pixels, toBitmap: &bottom, rowBytes: 4,
      bounds: CGRect(x: 10, y: 10, width: 1, height: 1),
      format: .RGBA8, colorSpace: CGColorSpaceCreateDeviceRGB())
    XCTAssertGreaterThan(top[0], top[2])
    XCTAssertGreaterThan(bottom[2], bottom[0])
    XCTAssertNil(
      DocumentDetector.correctedImage(
        image, document: paper(dx: 0.3),
        context: context))
  }

  @MainActor func testAutomaticImageEntersAdjustWithoutSendingAndKeepsManualTools() throws {
    let model = ScanSession(fixtureMode: true)
    let image = UIGraphicsImageRenderer(size: CGSize(width: 400, height: 600)).image { context in
      UIColor.white.setFill()
      context.fill(CGRect(x: 0, y: 0, width: 400, height: 600))
    }
    let scanned = try XCTUnwrap(
      DocumentDetector.correctedImage(
        image, document: paper(),
        context: CIContext()))
    var gate = DocumentCaptureGate()
    for index in 0..<7 {
      if gate.observe(paper(), at: Double(index) * 0.2) { model.captured(image, scanned: scanned) }
    }
    XCTAssertEqual(model.phase, .crop)
    XCTAssertNil(model.pending)
    XCTAssertNil(model.response)
    XCTAssertEqual(model.originalImage?.size, image.oriented().size)
    XCTAssertEqual(model.image?.size, scanned.size)
    let crop = try XCTUnwrap(model.image?.cropped(to: CGRect(x: 0, y: 0, width: 0.5, height: 1)))
    model.cropped(crop)
    XCTAssertEqual(model.phase, .preview)
    model.editCrop()
    XCTAssertEqual(model.image?.size, image.oriented().size)
    model.reset()
    XCTAssertEqual(model.phase, .capture)
  }
}
