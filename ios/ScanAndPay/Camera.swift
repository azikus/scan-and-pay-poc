import AVFoundation
import SwiftUI

final class CameraController: NSObject, ObservableObject, AVCapturePhotoCaptureDelegate {
  let session = AVCaptureSession()
  private let queue = DispatchQueue(label: "com.azikus.scanpay.camera")
  private let output = AVCapturePhotoOutput()
  private var configured = false
  private var wantsRunning = false
  private var requested = false
  @Published var available = false
  @Published var denied = false
  @Published var error: String?
  @Published var takingPhoto = false
  var captured: ((UIImage) -> Void)?
  func start() {
    requested = true
    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized: run()
    case .notDetermined:
      AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
        DispatchQueue.main.async {
          if granted { if self?.requested == true { self?.run() } } else { self?.denied = true }
        }
      }
    default: denied = true
    }
  }
  private func run() {
    queue.async { [weak self] in
      guard let self else { return }
      self.wantsRunning = true
      if !self.configured {
        self.session.beginConfiguration()
        self.session.sessionPreset = .photo
        guard
          let device = AVCaptureDevice.default(
            .builtInWideAngleCamera, for: .video, position: .back),
          let input = try? AVCaptureDeviceInput(device: device), self.session.canAddInput(input),
          self.session.canAddOutput(self.output)
        else {
          self.session.commitConfiguration()
          DispatchQueue.main.async {
            self.error = "Camera unavailable. Choose an image to continue."
          }
          return
        }
        self.session.addInput(input)
        self.session.addOutput(self.output)
        if let connection = self.output.connection(with: .video),
          connection.isVideoRotationAngleSupported(90)
        {
          connection.videoRotationAngle = 90
        }
        self.output.maxPhotoQualityPrioritization = .quality
        self.session.commitConfiguration()
        self.configured = true
      }
      if self.wantsRunning && !self.session.isRunning { self.session.startRunning() }
      DispatchQueue.main.async { self.available = self.session.isRunning }
    }
  }
  func stop() {
    requested = false
    available = false
    queue.async { [weak self] in
      self?.wantsRunning = false
      if self?.session.isRunning == true { self?.session.stopRunning() }
    }
  }
  func capture() {
    guard available, !takingPhoto else { return }
    takingPhoto = true
    queue.async { [weak self] in
      guard let self else { return }
      let settings = AVCapturePhotoSettings(format: [AVVideoCodecKey: AVVideoCodecType.jpeg])
      settings.photoQualityPrioritization = .quality
      self.output.capturePhoto(with: settings, delegate: self)
    }
  }
  func photoOutput(
    _ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?
  ) {
    let image = photo.fileDataRepresentation().flatMap { UIImage(data: $0) }
    DispatchQueue.main.async {
      self.takingPhoto = false
      if let image {
        self.captured?(image)
      } else {
        self.error = "The photo couldn’t be captured. Try again or import an image."
      }
    }
  }
}

struct CameraPreview: UIViewRepresentable {
  let session: AVCaptureSession
  final class Preview: UIView {
    override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
    var preview: AVCaptureVideoPreviewLayer { layer as! AVCaptureVideoPreviewLayer }
  }
  func makeUIView(context: Context) -> Preview {
    let view = Preview()
    view.preview.session = session
    // Show the complete photo field of view; filling the tall phone screen
    // hides edges that otherwise reappear after capture in Adjust image.
    view.preview.videoGravity = .resizeAspect
    view.backgroundColor = .clear
    view.preview.backgroundColor = UIColor.clear.cgColor
    return view
  }
  func updateUIView(_ view: Preview, context: Context) {
    if let connection = view.preview.connection, connection.isVideoRotationAngleSupported(90) {
      connection.videoRotationAngle = 90
    }
  }
}

extension UIImage {
  func oriented() -> UIImage {
    let pixels = CGSize(width: size.width * scale, height: size.height * scale)
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    format.opaque = true
    return UIGraphicsImageRenderer(size: pixels, format: format).image { ctx in
      UIColor.white.setFill()
      ctx.fill(CGRect(origin: .zero, size: pixels))
      draw(in: CGRect(origin: .zero, size: pixels))
    }
  }
  func rotated() -> UIImage {
    let source = oriented()
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    format.opaque = true
    let newSize = CGSize(width: source.size.height, height: source.size.width)
    return UIGraphicsImageRenderer(size: newSize, format: format).image { ctx in
      ctx.cgContext.translateBy(x: newSize.width / 2, y: newSize.height / 2)
      ctx.cgContext.rotate(by: .pi / 2)
      source.draw(
        in: CGRect(
          x: -source.size.width / 2, y: -source.size.height / 2, width: source.size.width,
          height: source.size.height))
    }
  }
  func cropped(to unitRect: CGRect) -> UIImage? {
    let source = oriented()
    guard let cg = source.cgImage else { return nil }
    let bounds = CGRect(x: 0, y: 0, width: cg.width, height: cg.height)
    let pixels = CGRect(
      x: unitRect.minX * bounds.width, y: unitRect.minY * bounds.height,
      width: unitRect.width * bounds.width, height: unitRect.height * bounds.height
    ).integral.intersection(bounds)
    guard !pixels.isEmpty, let cropped = cg.cropping(to: pixels) else { return nil }
    return UIImage(cgImage: cropped)
  }
}

struct ManualCrop: View {
  @State var image: UIImage
  let namespace: Namespace.ID
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  @State private var rotation = 0.0
  @State private var rotating = false
  let use: (UIImage) -> Void
  let retake: () -> Void
  @State private var crop = CGRect(x: 0, y: 0, width: 1, height: 1)
  @State private var dragStart: CGRect?
  @State private var error: String?
  var body: some View {
    VStack(spacing: 20) {
      ScreenHeader(subtitle: "Adjust image") {
        Button("Retake", action: retake).frame(minHeight: 44)
      }.padding(.horizontal, 16)
      GeometryReader { geo in
        let factor = min(geo.size.width / image.size.width, geo.size.height / image.size.height)
        let size = CGSize(width: image.size.width * factor, height: image.size.height * factor)
        ZStack {
          Image(uiImage: image).resizable().frame(width: size.width, height: size.height)
            .modifier(DocumentContinuity(namespace: namespace))
          Path { path in
            path.addRect(CGRect(origin: .zero, size: size))
            path.addRect(
              CGRect(
                x: crop.minX * size.width, y: crop.minY * size.height,
                width: crop.width * size.width, height: crop.height * size.height))
          }.fill(.black.opacity(0.55), style: FillStyle(eoFill: true)).allowsHitTesting(false)
          Rectangle().stroke(Brand.slate, lineWidth: 1).contentShape(Rectangle()).frame(
            width: crop.width * size.width, height: crop.height * size.height
          ).position(x: crop.midX * size.width, y: crop.midY * size.height)
            .gesture(
              DragGesture().onChanged { v in
                if dragStart == nil { dragStart = crop }
                guard let start = dragStart else { return }
                crop.origin.x = min(
                  max(0, start.minX + v.translation.width / size.width), 1 - start.width)
                crop.origin.y = min(
                  max(0, start.minY + v.translation.height / size.height), 1 - start.height)
              }.onEnded { _ in dragStart = nil })
          Path { path in
            let rect = CGRect(
              x: crop.minX * size.width, y: crop.minY * size.height,
              width: crop.width * size.width, height: crop.height * size.height)
            for step in 1...2 {
              let fraction = CGFloat(step) / 3
              path.move(to: CGPoint(x: rect.minX + rect.width * fraction, y: rect.minY))
              path.addLine(to: CGPoint(x: rect.minX + rect.width * fraction, y: rect.maxY))
              path.move(to: CGPoint(x: rect.minX, y: rect.minY + rect.height * fraction))
              path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY + rect.height * fraction))
            }
          }.stroke(.white.opacity(0.55), lineWidth: 0.5)
            .opacity(dragStart == nil ? 0 : 1).allowsHitTesting(false)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.16), value: dragStart == nil)
          ForEach(0..<4) { corner in
            let right = corner % 2 == 1
            let bottom = corner >= 2
            RoundedRectangle(cornerRadius: 4).fill(Brand.ice)
              .overlay(RoundedRectangle(cornerRadius: 4).strokeBorder(Brand.slate, lineWidth: 1.5))
              .frame(width: 18, height: 18).frame(
                width: 44, height: 44
              ).contentShape(Rectangle())
              .position(
                x: (right ? crop.maxX : crop.minX) * size.width,
                y: (bottom ? crop.maxY : crop.minY) * size.height
              )
              .gesture(
                DragGesture().onChanged { v in
                  resize(corner, translation: v.translation, size: size)
                }.onEnded { _ in dragStart = nil }
              )
              .accessibilityLabel(
                "Crop \(bottom ? "bottom":"top") \(right ? "right":"left") corner"
              )
              .accessibilityAdjustableAction { direction in
                let delta: CGFloat = direction == .increment ? 0.02 : -0.02
                resize(
                  corner,
                  translation: CGSize(
                    width: (right ? -delta : delta) * size.width,
                    height: (bottom ? -delta : delta) * size.height), size: size)
                dragStart = nil
              }
          }
        }.frame(width: size.width, height: size.height)
          .rotationEffect(.degrees(rotation))
          .scaleEffect(
            rotating ? min(geo.size.width / size.height, geo.size.height / size.width) : 1
          )
          .position(
            x: geo.size.width / 2, y: geo.size.height / 2)
      }.padding(.horizontal, 24)
      VStack(spacing: 10) {
        Text("Drag the corners to keep all payment details.")
          .font(Brand.font(13)).foregroundStyle(.secondary).multilineTextAlignment(.center)
        HStack {
          Button {
            rotate()
          } label: {
            Label("Rotate", systemImage: "rotate.right").frame(minHeight: 44)
          }
          Spacer()
          Button("Reset crop") {
            withAnimation(reduceMotion ? nil : .spring(response: 0.35, dampingFraction: 0.88)) {
              crop = CGRect(x: 0, y: 0, width: 1, height: 1)
            }
          }.frame(minHeight: 44)
        }.buttonStyle(.plain).font(Brand.font(15, .semibold))
      }.padding(.horizontal, 18).padding(.vertical, 12).modifier(GlassPanel())
        .padding(.horizontal, 16)
      if let error { Text(error).foregroundStyle(.orange) }
      Button {
        if let result = image.cropped(to: crop) {
          use(result)
        } else {
          error = "The selected crop couldn’t be prepared."
        }
      } label: {
        Text("Use crop").frame(maxWidth: .infinity)
      }.buttonStyle(PrimaryButton()).padding(.horizontal, 22).accessibilityIdentifier("use-crop")
    }.padding(.top, 8).padding(.bottom, 14).background(DocumentBackdrop(image: image))
      .foregroundStyle(Brand.ink).tint(Brand.ink)
      .disabled(rotating)
  }
  private func rotate() {
    guard !rotating else { return }
    let rotatedImage = image.rotated()
    crop = CGRect(x: 0, y: 0, width: 1, height: 1)
    dragStart = nil
    error = nil
    if reduceMotion {
      image = rotatedImage
      return
    }
    withAnimation(.easeInOut(duration: 0.32), completionCriteria: .logicallyComplete) {
      rotating = true
      rotation = 90
    } completion: {
      var transaction = Transaction()
      transaction.disablesAnimations = true
      withTransaction(transaction) {
        image = rotatedImage
        rotation = 0
        rotating = false
      }
    }
  }
  private func resize(_ corner: Int, translation: CGSize, size: CGSize) {
    if dragStart == nil { dragStart = crop }
    guard let start = dragStart else { return }
    let dx = translation.width / size.width
    let dy = translation.height / size.height
    let left = corner % 2 == 0 ? min(max(0, start.minX + dx), start.maxX - 0.1) : start.minX
    let right = corner % 2 == 1 ? max(min(1, start.maxX + dx), start.minX + 0.1) : start.maxX
    let top = corner < 2 ? min(max(0, start.minY + dy), start.maxY - 0.1) : start.minY
    let bottom = corner >= 2 ? max(min(1, start.maxY + dy), start.minY + 0.1) : start.maxY
    crop = CGRect(x: left, y: top, width: right - left, height: bottom - top)
  }
}
