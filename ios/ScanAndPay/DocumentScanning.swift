import CoreImage
import SwiftUI
import Vision

/// Vision uses normalized coordinates with the origin at the bottom left.
struct DocumentQuadrilateral: Equatable {
  let topLeft: CGPoint
  let topRight: CGPoint
  let bottomRight: CGPoint
  let bottomLeft: CGPoint
  let confidence: Float

  init(_ observation: VNRectangleObservation) {
    topLeft = observation.topLeft
    topRight = observation.topRight
    bottomRight = observation.bottomRight
    bottomLeft = observation.bottomLeft
    confidence = observation.confidence
  }

  init(
    topLeft: CGPoint, topRight: CGPoint, bottomRight: CGPoint, bottomLeft: CGPoint,
    confidence: Float = 1
  ) {
    self.topLeft = topLeft
    self.topRight = topRight
    self.bottomRight = bottomRight
    self.bottomLeft = bottomLeft
    self.confidence = confidence
  }

  var corners: [CGPoint] { [topLeft, topRight, bottomRight, bottomLeft] }
  var area: CGFloat {
    let pairs = zip(corners, [topRight, bottomRight, bottomLeft, topLeft])
    return abs(pairs.reduce(0) { $0 + $1.0.x * $1.1.y - $1.1.x * $1.0.y }) / 2
  }
  var canCapture: Bool {
    confidence >= 0.6 && area >= 0.18
      && corners.allSatisfy {
        $0.x.isFinite && $0.y.isFinite
          && (0.015...0.985).contains($0.x) && (0.015...0.985).contains($0.y)
      }
  }
  func distance(to other: Self) -> CGFloat {
    zip(corners, other.corners).map { hypot($0.x - $1.x, $0.y - $1.y) }.max() ?? 1
  }
  /// Match the preview layer's aspect-fit image, including its letterboxing.
  func previewCorners(imageSize: CGSize, viewport: CGSize) -> [CGPoint] {
    let scale = min(viewport.width / imageSize.width, viewport.height / imageSize.height)
    let size = CGSize(width: imageSize.width * scale, height: imageSize.height * scale)
    let origin = CGPoint(
      x: (viewport.width - size.width) / 2,
      y: (viewport.height - size.height) / 2)
    return corners.map {
      CGPoint(
        x: origin.x + $0.x * size.width,
        y: origin.y + (1 - $0.y) * size.height)
    }
  }
}

/// One capture per camera run, requiring a continuous, steady view of all four edges.
struct DocumentCaptureGate {
  private var anchor: DocumentQuadrilateral?
  private var began: TimeInterval?
  private var lastSeen: TimeInterval?
  private var samples = 0
  private(set) var fired = false

  mutating func reset() { self = Self() }
  mutating func observe(_ document: DocumentQuadrilateral?, at time: TimeInterval) -> Bool {
    guard !fired else { return false }
    guard let document, document.canCapture else {
      anchor = nil
      began = nil
      lastSeen = nil
      samples = 0
      return false
    }
    if let anchor, let lastSeen, time >= lastSeen, time - lastSeen <= 0.45,
      document.distance(to: anchor) <= 0.018
    {
      samples += 1
    } else {
      anchor = document
      began = time
      samples = 1
    }
    lastSeen = time
    if let began, time - began >= 0.9, samples >= 5 {
      fired = true
      return true
    }
    return false
  }
}

enum DocumentDetector {
  static func detect(in handler: VNImageRequestHandler) throws -> DocumentQuadrilateral? {
    let request = VNDetectDocumentSegmentationRequest()
    try handler.perform([request])
    let document = request.results?.first.map(DocumentQuadrilateral.init)
    if document?.canCapture == true { return document }

    // Segmentation can return the frame boundary on plain paper/backgrounds.
    // Ask the native geometric detector for an interior, confidently bounded page.
    let rectangles = VNDetectRectanglesRequest()
    rectangles.minimumConfidence = 0.8
    rectangles.minimumSize = 0.2
    rectangles.minimumAspectRatio = 0.15
    rectangles.maximumAspectRatio = 1
    rectangles.quadratureTolerance = 25
    rectangles.maximumObservations = 4
    try handler.perform([rectangles])
    return rectangles.results?.map(DocumentQuadrilateral.init)
      .filter(\.canCapture).max(by: { $0.area < $1.area }) ?? document
  }

  /// Re-detect the full-resolution still: video and photo fields of view can differ.
  static func scannedImage(_ image: UIImage, context: CIContext) -> UIImage? {
    guard let cgImage = image.cgImage,
      let document = try? detect(in: VNImageRequestHandler(cgImage: cgImage)),
      document.canCapture
    else { return nil }
    return correctedImage(image, document: document, context: context)
  }

  static func correctedImage(
    _ image: UIImage, document: DocumentQuadrilateral,
    context: CIContext
  ) -> UIImage? {
    guard document.canCapture, let cgImage = image.cgImage else { return nil }
    let input = CIImage(cgImage: cgImage)
    func vector(_ point: CGPoint) -> CIVector {
      CIVector(x: point.x * input.extent.width, y: point.y * input.extent.height)
    }
    // A little margin keeps antialiased ink near the detected paper edge intact.
    let center = CGPoint(
      x: document.corners.map(\.x).reduce(0, +) / 4,
      y: document.corners.map(\.y).reduce(0, +) / 4)
    let points = document.corners.map {
      CGPoint(
        x: min(1, max(0, center.x + ($0.x - center.x) * 1.015)),
        y: min(1, max(0, center.y + ($0.y - center.y) * 1.015)))
    }
    let corrected = input.applyingFilter(
      "CIPerspectiveCorrection",
      parameters: [
        "inputTopLeft": vector(points[0]), "inputTopRight": vector(points[1]),
        "inputBottomRight": vector(points[2]), "inputBottomLeft": vector(points[3]),
      ])
    guard !corrected.extent.isEmpty,
      let result = context.createCGImage(corrected, from: corrected.extent)
    else { return nil }
    return UIImage(cgImage: result)
  }
}

struct DocumentPreviewMask: View {
  let document: DocumentQuadrilateral
  let imageSize: CGSize
  var body: some View {
    GeometryReader { geometry in
      let corners = document.previewCorners(imageSize: imageSize, viewport: geometry.size)
      let paper = Path { path in
        path.addLines(corners)
        path.closeSubpath()
      }
      Path { path in
        path.addRect(CGRect(origin: .zero, size: geometry.size))
        path.addPath(paper)
      }.fill(Color.gray.opacity(0.65), style: FillStyle(eoFill: true))
      paper.stroke(.white.opacity(0.95), lineWidth: 2)
    }.clipped().allowsHitTesting(false).accessibilityHidden(true)
  }
}
