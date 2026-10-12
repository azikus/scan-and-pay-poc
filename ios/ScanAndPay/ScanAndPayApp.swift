import PhotosUI
import SwiftUI

enum Brand {
  static let ink = Color(red: 10 / 255, green: 10 / 255, blue: 10 / 255)
  static let ice = Color(red: 207 / 255, green: 226 / 255, blue: 246 / 255)
  static let slate = Color(red: 62 / 255, green: 72 / 255, blue: 85 / 255)
  static func font(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
    .custom(
      weight == .regular ? "HankenGrotesk-Regular" : "HankenGrotesk-SemiBold", size: size,
      relativeTo: .body)
  }
}
// Glass floats above the camera; document pixels and editable text stay unobstructed.
struct ControlSurface: ViewModifier {
  var prominent = false
  var enabled = true
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  func body(content: Content) -> some View {
    let shape = RoundedRectangle(cornerRadius: 22, style: .continuous)
    if reduceTransparency {
      content.background(
        prominent && enabled ? Brand.ice : Color(uiColor: .secondarySystemBackground), in: shape)
    } else if #available(iOS 26.0, *) {
      content.glassEffect(
        .regular.tint(prominent && enabled ? Brand.ice : nil).interactive(enabled), in: shape)
    } else if prominent && enabled {
      content.background(Brand.ice, in: shape)
    } else {
      content.background(.regularMaterial, in: shape)
        .overlay(shape.strokeBorder(.white.opacity(0.16), lineWidth: 0.5))
    }
  }
}
struct GlassPanel: ViewModifier {
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  func body(content: Content) -> some View {
    let shape = RoundedRectangle(cornerRadius: 30, style: .continuous)
    if reduceTransparency {
      content.background(Color(uiColor: .systemBackground), in: shape)
    } else if #available(iOS 26.0, *) {
      content.glassEffect(.regular, in: shape)
    } else {
      content.background(.regularMaterial, in: shape)
        .overlay(shape.strokeBorder(.white.opacity(0.5), lineWidth: 0.5))
    }
  }
}
/// Shared identity and screen context, with space for each screen's actions.
struct ScreenHeader<Actions: View>: View {
  let subtitle: String
  let detail: String?
  let actions: Actions
  @Environment(\.dynamicTypeSize) private var typeSize
  init(subtitle: String, detail: String? = nil, @ViewBuilder actions: () -> Actions) {
    self.subtitle = subtitle
    self.detail = detail
    self.actions = actions()
  }
  private var identity: some View {
    HStack(spacing: 10) {
      Image("AzikusMarkDark").resizable().scaledToFit()
        .frame(width: 24, height: 24).padding(7).accessibilityLabel("Azikus")
      VStack(alignment: .leading, spacing: 3) {
        Text("Scan & Pay").font(Brand.font(21, .semibold))
        Text(subtitle).font(Brand.font(13)).foregroundStyle(Brand.slate)
          .fixedSize(horizontal: false, vertical: true)
        if let detail {
          Text(detail).font(Brand.font(12)).foregroundStyle(Brand.slate)
            .fixedSize(horizontal: false, vertical: true)
        }
      }
    }.layoutPriority(1)
  }
  var body: some View {
    Group {
      if typeSize.isAccessibilitySize {
        VStack(alignment: .leading, spacing: 8) {
          identity
          HStack {
            Spacer(minLength: 0)
            actions
          }
        }
      } else {
        HStack(spacing: 10) {
          identity
          Spacer(minLength: 0)
          actions
        }
      }
    }.font(Brand.font(15, .semibold)).foregroundStyle(Brand.ink).tint(Brand.ink)
      .buttonStyle(.plain).padding(12).modifier(GlassPanel())
  }
}
/// A soft image-derived backdrop; the foreground document always stays sharp.
struct DocumentBackdrop: View {
  var image: UIImage? = nil
  @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
  var body: some View {
    GeometryReader { geo in
      ZStack {
        Brand.ice
        if let image, !reduceTransparency {
          Image(uiImage: image).resizable().scaledToFill()
            .frame(width: geo.size.width, height: geo.size.height).clipped()
            .blur(radius: 45).opacity(0.22)
        }
      }.frame(width: geo.size.width, height: geo.size.height).clipped()
    }.ignoresSafeArea().allowsHitTesting(false).accessibilityHidden(true)
  }
}
struct GlassControlButton: ButtonStyle {
  @Environment(\.isEnabled) private var enabled
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  func makeBody(configuration: Configuration) -> some View {
    configuration.label.font(Brand.font(15, .semibold)).foregroundStyle(.primary)
      .padding(.horizontal, 14).frame(minHeight: 44)
      .modifier(ControlSurface(enabled: enabled))
      .opacity(enabled ? 1 : 0.45)
      .scaleEffect(configuration.isPressed && !reduceMotion ? 0.96 : 1)
      .animation(reduceMotion ? nil : .smooth(duration: 0.18), value: configuration.isPressed)
  }
}
struct PrimaryButton: ButtonStyle {
  @Environment(\.isEnabled) private var enabled
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  func makeBody(configuration: Configuration) -> some View {
    configuration.label.font(Brand.font(17, .semibold))
      .foregroundStyle(enabled ? Brand.ink : Color.secondary)
      .padding(.vertical, 17).frame(maxWidth: .infinity)
      .modifier(ControlSurface(prominent: true, enabled: enabled))
      .opacity(configuration.isPressed ? 0.8 : 1)
      .scaleEffect(configuration.isPressed && !reduceMotion ? 0.98 : 1)
      .animation(reduceMotion ? nil : .smooth(duration: 0.18), value: configuration.isPressed)
  }
}
struct DocumentContinuity: ViewModifier {
  let namespace: Namespace.ID
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  @ViewBuilder func body(content: Content) -> some View {
    if reduceMotion {
      content
    } else {
      content.matchedGeometryEffect(id: "document", in: namespace, properties: .frame)
    }
  }
}

@main struct ScanAndPayApp: App {
  var body: some Scene { WindowGroup { ScanHome() } }
}

struct ScanHome: View {
  @StateObject private var model = ScanSession(
    fixtureMode: ProcessInfo.processInfo.arguments.contains("-synthetic-preview"))
  @StateObject private var camera = CameraController()
  @Environment(\.scenePhase) private var scenePhase
  @Environment(\.dynamicTypeSize) private var typeSize
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  @Namespace private var documentMotion
  @State private var picked: PhotosPickerItem?
  @State private var settings = false
  @State private var json = false
  @State private var imageViewer = false
  @State private var reviewVisible = false
  @State private var detent: PresentationDetent = .fraction(0.68)
  @State private var discard = false
  @State private var importing = false
  var body: some View {
    NavigationStack {
      ZStack {
        DocumentBackdrop(image: model.originalImage ?? model.image)
        content
          .environment(\.colorScheme, .light)
          .transition(reduceMotion ? .opacity : .opacity.combined(with: .offset(y: 16)))
      }.animation(
        reduceMotion ? .easeOut(duration: 0.15) : .spring(response: 0.46, dampingFraction: 0.9),
        value: screen
      )
      .preferredColorScheme(.light)
      .toolbar(.hidden, for: .navigationBar)
      .sheet(isPresented: $settings) { ConnectionSettings(model: model) }

      .sheet(isPresented: $reviewVisible) {
        ReviewSheet(
          model: model, showImage: $imageViewer, showJSON: $json, expand: { detent = .large }
        )
        .presentationDetents([.fraction(0.42), .fraction(0.68), .large], selection: $detent)
        .presentationDragIndicator(.visible).presentationCornerRadius(30)
        .presentationBackground(.regularMaterial)
        .presentationBackgroundInteraction(.enabled(upThrough: .fraction(0.68)))
        .interactiveDismissDisabled()
      }
      .confirmationDialog("Clear this scan?", isPresented: $discard, titleVisibility: .visible) {
        Button("Clear scan", role: .destructive) { model.reset() }
      } message: {
        Text("This clears the phone’s draft. Processing already accepted by the Mac may continue.")
      }
    }
    .overlay {
      if model.complete { CompletionCelebration { model.complete = false } }
    }
    .onAppear {
      camera.captured = { model.captured($0) }
      reviewVisible = model.processing || [.review, .failed, .recovery].contains(model.phase)
      updateCamera()
    }
    .onChange(of: model.phase) { _, phase in
      reviewVisible = model.processing || phase == .review || phase == .recovery || phase == .failed
      if phase == .review { detent = typeSize.isAccessibilitySize ? .large : .fraction(0.68) }
      updateCamera()
    }
    .onChange(of: scenePhase) { _, phase in
      if phase == .active {
        model.foreground()
        updateCamera()
      } else {
        camera.stop()
        model.background()
      }
    }
    .onChange(of: typeSize) { _, size in if size.isAccessibilitySize { detent = .large } }
    .onChange(of: picked) { _, item in
      guard let item else { return }
      importing = true
      Task {
        defer {
          importing = false
          picked = nil
        }
        do {
          guard let data = try await item.loadTransferable(type: Data.self),
            let image = UIImage(data: data)
          else { throw ClientFailure("Choose a readable image.") }
          model.captured(image)
        } catch { model.message = error.localizedDescription }
      }
    }
  }
  private var screen: String {
    model.phase == .capture ? "capture" : model.phase == .crop ? "crop" : "document"
  }
  @ViewBuilder private var content: some View {
    if model.phase == .capture {
      captureScreen.id(screen)
    } else if model.phase == .crop, let image = model.originalImage {
      ManualCrop(image: image, namespace: documentMotion, use: model.cropped, retake: model.reset)
        .transition(reduceMotion ? .opacity : .opacity.combined(with: .offset(y: 18)))
    } else {
      VStack(spacing: 16) {
        ScreenHeader(subtitle: model.phase == .preview ? "Ready to send" : "Your document") {
          if model.phase == .preview {
            Button("Edit crop", action: model.editCrop).buttonStyle(.plain).frame(minHeight: 44)
          } else {
            Button {
              imageViewer = true
            } label: {
              Label("Image", systemImage: "arrow.up.left.and.arrow.down.right")
            }.font(Brand.font(14))
          }
        }.padding(.horizontal, 16)
        ZStack {
          if let image = model.image {
            Image(uiImage: image).resizable().scaledToFit()
              .modifier(DocumentContinuity(namespace: documentMotion)).padding(.horizontal, 16)
              .frame(maxWidth: .infinity, maxHeight: .infinity)
              .contentShape(Rectangle()).onTapGesture {
                if model.phase != .preview { imageViewer = true }
              }
          }
        }.frame(maxWidth: .infinity, maxHeight: .infinity)
        if model.phase == .preview {
          VStack(spacing: 12) {
            if let message = model.message {
              Text(message).font(Brand.font(14)).foregroundStyle(.orange)
            }
            Button(action: model.send) {
              Label("Send", systemImage: "arrow.up.right").frame(maxWidth: .infinity)
            }.buttonStyle(PrimaryButton()).accessibilityIdentifier("send-image")
          }.padding(22)
        } else {
          HStack {
            Button("Clear scan") { discard = true }
            Spacer()
            if model.response != nil { Button("JSON") { json = true } }
          }.font(Brand.font(14)).tint(Brand.ink).frame(minHeight: 44).padding(16)
            .modifier(GlassPanel()).padding(16)
        }
      }.padding(.top, 8).id(screen).transition(
        reduceMotion ? .opacity : .opacity.combined(with: .offset(y: -12)))
    }
  }
  private var captureScreen: some View {
    ZStack {
      // The preview extends behind both glass panels and the device safe areas.
      GeometryReader { geo in
        ZStack {
          Brand.ice
          if model.fixtureMode {
            Image(uiImage: fixtureImage()).resizable().scaledToFit().padding(28)
          } else if camera.available {
            CameraPreview(session: camera.session)
          }
        }.frame(width: geo.size.width, height: geo.size.height).clipped()
      }.ignoresSafeArea()
      VStack(spacing: 16) {
        captureHeader
        Spacer(minLength: 0)
        if !model.fixtureMode && !camera.available {
          VStack(spacing: 16) {
            Image(systemName: "camera").font(.system(size: 38, weight: .light))
            Text(camera.denied ? "Allow camera access" : "Ready when you are")
              .font(Brand.font(24, .semibold))
            Text(
              camera.denied
                ? "Enable the camera in Settings, or choose an image below."
                : camera.error ?? "Preparing the camera…"
            )
            .font(Brand.font(15)).foregroundStyle(.secondary).multilineTextAlignment(.center)
            if camera.denied {
              Button("Open Settings") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                  UIApplication.shared.open(url)
                }
              }.buttonStyle(.bordered)
            }
          }.padding(24).modifier(GlassPanel())
          Spacer(minLength: 0)
        }
        captureControls
      }.padding(.horizontal, 16).padding(.top, 8).padding(.bottom, 12)
    }.foregroundStyle(Brand.ink).tint(Brand.ink)
  }
  private var captureHeader: some View {
    ScreenHeader(
      subtitle: "Scan a document",
      detail: model.fixtureMode ? "Synthetic preview" : model.connectionStatus
    ) {
      Button {
        Task { await model.reconnect() }
      } label: {
        Group {
          if model.reconnecting { ProgressView() } else { Image(systemName: "arrow.clockwise") }
        }.frame(width: 44, height: 44).contentShape(Rectangle())
      }.accessibilityLabel("Reconnect").accessibilityIdentifier("reconnect")
        .disabled(model.reconnecting || model.fixtureMode)
      Button {
        settings = true
      } label: {
        Image(systemName: "slider.horizontal.3").frame(width: 44, height: 44)
          .contentShape(Rectangle())
      }.accessibilityLabel("Connection settings")
    }
  }
  private var captureControls: some View {
    VStack(spacing: 10) {
      if let message = model.message {
        Text(message).font(Brand.font(14)).foregroundStyle(Brand.slate)
      }
      Text("Start with a document.").font(Brand.font(24, .semibold))
      Text("Take a photo or choose an image.").font(Brand.font(14)).foregroundStyle(.secondary)
      HStack {
        PhotosPicker(selection: $picked, matching: .images, photoLibrary: .shared()) {
          VStack(spacing: 6) {
            Image(systemName: "photo.on.rectangle").font(.system(size: 21))
            Text(importing ? "Opening…" : "Import").font(Brand.font(12))
          }.frame(maxWidth: .infinity, minHeight: 66).contentShape(Rectangle())
        }.buttonStyle(.plain).disabled(importing)
        Button {
          if model.fixtureMode { model.captured(fixtureImage()) } else { camera.capture() }
        } label: {
          Circle().fill(.white).padding(7)
            .overlay(Circle().stroke(Brand.slate.opacity(0.7), lineWidth: 2))
            .frame(width: 78, height: 78)
        }.buttonStyle(.plain)
          .disabled((!camera.available && !model.fixtureMode) || camera.takingPhoto || importing)
          .accessibilityLabel("Capture document").accessibilityIdentifier("capture")
        Color.clear.frame(maxWidth: .infinity, maxHeight: 66)
      }.padding(.top, 8)
    }.padding(22).modifier(GlassPanel())
  }
  private func updateCamera() {
    if scenePhase == .active && model.phase == .capture && !model.fixtureMode {
      camera.start()
    } else {
      camera.stop()
    }
  }
  private func fixtureImage() -> UIImage {
    let format = UIGraphicsImageRendererFormat()
    format.scale = 1
    return UIGraphicsImageRenderer(size: CGSize(width: 780, height: 1000), format: format).image {
      ctx in
      UIColor.white.setFill()
      ctx.fill(CGRect(x: 0, y: 0, width: 780, height: 1000))
      let copy =
        "SYNTHETIC DOCUMENT\n\nExample Utilities Ltd (synthetic)\n\nINVOICE\n\nAmount due  GBP 123.45\n\nSort code  000000\nAccount  00000000\nReference  DEMO-42\n\nNot payable"
      (copy as NSString).draw(
        in: CGRect(x: 60, y: 70, width: 660, height: 860),
        withAttributes: [.font: UIFont.systemFont(ofSize: 30), .foregroundColor: UIColor.black])
    }
  }
}

struct ReviewSheet: View {
  @ObservedObject var model: ScanSession
  @Binding var showImage: Bool
  @Binding var showJSON: Bool
  private func openImage() { showImage = true }
  private func openJSON() { showJSON = true }
  let expand: () -> Void
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  @State private var payConfirmation = false
  @State private var confirmAfterDismiss = false
  @State private var missing = false
  @State private var discard = false
  @FocusState private var focused: String?
  var body: some View {
    VStack(spacing: 0) {
      ScreenHeader(
        subtitle:
          model.processing
          ? model.processingTitle
          : model.phase == .review
            ? "Review details"
            : model.phase == .recovery ? "Connection interrupted" : "Couldn’t read details"
      ) {
        Menu {
          Button("View image", action: openImage)
          if model.response != nil { Button("View JSON", action: openJSON) }
          Button("Reconnect", systemImage: "arrow.clockwise") { Task { await model.reconnect() } }
            .disabled(model.processing || model.saving || model.reconnecting || model.fixtureMode)
          Button("Clear scan", role: .destructive) { discard = true }
        } label: {
          Image(systemName: "ellipsis").font(.system(size: 20)).frame(width: 20, height: 44)
        }.buttonStyle(GlassControlButton()).accessibilityLabel("Scan options")
      }.padding(.horizontal, 14).padding(.top, 14)
      ScrollView {
        VStack(alignment: .leading, spacing: 17) {
          if let status = model.connectionStatus {
            Text(status).font(Brand.font(13)).foregroundStyle(.secondary)
          }
          if model.processing {
            Text(
              model.phase == .queued
                ? "The Mac has accepted your image." : "You’ll review the details before finishing."
            ).font(Brand.font(14)).foregroundStyle(.secondary)
            ForEach(
              [
                "Recipient", "Amount", "Currency", "Account holder", "Sort code", "Account number",
                "IBAN", "BIC", "Payment reference", "Payment model", "Purpose code",
                "Biller scheme", "Biller code", "Supplier", "Invoice number", "Customer number",
                "Due date", "Description", "Account country", "Document language", "Issuer country",
              ], id: \.self
            ) { name in ShimmerField(label: name) }
          } else if model.phase == .review, let draft = model.draft {
            draftContents(draft)
          } else {
            Text(model.message ?? "Your image is still available.").font(Brand.font(16))
              .foregroundStyle(.secondary)
            if model.phase == .recovery {
              Button(
                model.pending?.confirmationBody != nil
                  ? "Save confirmation"
                  : model.pending?.scanID == nil ? "Recover upload" : "Check scan status",
                action: model.recover
              ).buttonStyle(PrimaryButton())
            }
            Button("View image", action: openImage).buttonStyle(.bordered)
            Button("Retake") { discard = true }.buttonStyle(.bordered)
          }
        }.padding(22)
          .animation(reduceMotion ? nil : .easeInOut(duration: 0.24), value: model.processing)
      }.scrollDismissesKeyboard(.interactively).disabled(model.reconnecting)
      if model.phase == .review {
        VStack(spacing: 10) {
          Toggle("I’ve checked these details.", isOn: $model.checked).toggleStyle(CheckboxToggle())
            .font(Brand.font(14)).accessibilityIdentifier("review-confirmation")
          Button {
            focused = nil
            payConfirmation = true
          } label: {
            HStack {
              if model.saving { ProgressView() }
              Text(model.saving ? "Saving…" : "Pay")
              Image(systemName: "arrow.right")
            }.frame(maxWidth: .infinity)
          }.buttonStyle(PrimaryButton()).disabled(
            !model.checked || model.draft?.canConfirm != true || model.saving || model.reconnecting
          ).accessibilityIdentifier("pay")
        }.padding(18).modifier(GlassPanel()).padding(.horizontal, 14).padding(.bottom, 12)
      }
    }.background(DocumentBackdrop()).tint(.primary)
      .sheet(
        isPresented: $payConfirmation,
        onDismiss: {
          if confirmAfterDismiss {
            confirmAfterDismiss = false
            model.confirm()
          }
        }
      ) {
        if let draft = model.draft {
          PaymentConfirmation(
            draft: draft, cancel: { payConfirmation = false },
            confirm: {
              confirmAfterDismiss = true
              payConfirmation = false
            }
          ).presentationDetents([.large]).presentationDragIndicator(.visible)
            .presentationCornerRadius(30).presentationBackground(.regularMaterial)
        }
      }
      .sheet(isPresented: $showJSON) {
        JSONOutput(response: model.response, mobileValues: model.confirmationValues)
      }
      .fullScreenCover(isPresented: $showImage) { DocumentViewer(image: model.image) }
      .onChange(of: focused) { _, value in if value != nil { expand() } }
      .onChange(of: missing) { _, value in if value { expand() } }
      .confirmationDialog("Clear this scan?", isPresented: $discard, titleVisibility: .visible) {
        Button("Clear scan", role: .destructive) { model.reset() }
      } message: {
        Text("This clears the phone’s draft. It does not cancel work on the Mac.")
      }
  }
  @ViewBuilder private func draftContents(_ draft: PaymentDraft) -> some View {
    Text("Check every detail against your document.").font(Brand.font(14)).foregroundStyle(
      .secondary)
    if draft.candidates.count > 1 || draft.selectedID == nil {
      Picker(
        "Payment option",
        selection: Binding(get: { model.draft?.selectedID ?? "" }, set: model.select)
      ) {
        Text("Choose a payment option").tag("")
        ForEach(Array(draft.candidates.enumerated()), id: \.offset) { index, candidate in
          Text(draft.optionLabel(at: index)).tag(candidate["id"].string ?? "")
        }
      }.pickerStyle(.menu).tint(.primary).accessibilityIdentifier("payment-option")
    }
    ForEach(Array(draft.reasons.enumerated()), id: \.offset) { _, reason in
      Label(
        reason["message"].string ?? "Check this field.",
        systemImage: "exclamationmark.circle"
      ).font(Brand.font(13)).foregroundStyle(.orange)
    }
    ForEach(
      draft.sections(
        for: draft.fields.filter {
          $0.value != nil || missing || focused == $0.id
        })
    ) { section in
      Text(section.title).font(Brand.font(17, .semibold)).padding(.top, 8)
      ForEach(section.fields) { field in
        fieldEditor(field)
      }
    }
    if !draft.missingFields.isEmpty || missing {
      Button {
        missing.toggle()
      } label: {
        Label(
          missing
            ? "Hide empty fields" : "Add missing details (\(draft.missingFields.count))",
          systemImage: missing ? "minus.circle" : "plus.circle"
        )
        .font(Brand.font(14)).frame(minHeight: 44)
      }.tint(.primary).accessibilityIdentifier("missing-details")
    }
    if draft.candidateIndex == nil {
      Text("Choose a payment option to continue.").font(Brand.font(13)).foregroundStyle(.secondary)
    }
    ForEach(draft.paymentIssues, id: \.self) { issue in
      Text(issue).font(Brand.font(13)).foregroundStyle(.orange)
    }
    if let message = model.message {
      Text(message).foregroundStyle(.orange).font(Brand.font(13))
    }
  }
  private func fieldEditor(_ field: DraftField) -> some View {
    VStack(alignment: .leading, spacing: 7) {
      HStack {
        Text(field.label).font(Brand.font(12)).foregroundStyle(.secondary)
        if field.value != nil && field.isEdited { EditedValueLabel() }
      }
      TextField(
        "Enter \(field.label.lowercased())",
        text: Binding(
          get: { model.draft?.values[field.id]?.string ?? "" }, set: { model.edit(field.id, $0) }),
        axis: .vertical
      )
      .font(Brand.font(field.isAmount ? 36 : 17, field.isAmount ? .semibold : .regular))
      .keyboardType(field.numeric ? (field.isAmount ? .decimalPad : .numberPad) : .default)
      .autocorrectionDisabled().textInputAutocapitalization(
        field.id.hasSuffix("/currency") ? .characters : .never
      ).focused(
        $focused, equals: field.id
      ).accessibilityLabel(field.label).accessibilityIdentifier(field.id)
      .disabled(model.saving || model.pending?.confirmationBody != nil)
      if PaymentDraft.isExtracted(field.observation) {
        ForEach(Array(field.observation["alternatives"].array.enumerated()), id: \.offset) {
          _, alternative in
          Text("Alternative: \(alternative["value"].string ?? "")").font(Brand.font(12))
            .foregroundStyle(.secondary)
        }
      }
      Divider()
    }
  }
}

struct ShimmerField: View {
  let label: String
  @Environment(\.accessibilityReduceMotion) private var reduce
  @State private var moving = false
  var body: some View {
    VStack(alignment: .leading, spacing: 9) {
      Text(label).font(Brand.font(12)).foregroundStyle(.secondary)
      GeometryReader { geo in
        RoundedRectangle(cornerRadius: 6).fill(Color.secondary.opacity(0.1)).overlay {
          if !reduce {
            LinearGradient(
              colors: [.clear, .white.opacity(0.45), .clear], startPoint: .leading,
              endPoint: .trailing
            ).frame(width: geo.size.width * 0.65).offset(
              x: moving ? geo.size.width : -geo.size.width
            ).animation(.linear(duration: 1.65).repeatForever(autoreverses: false), value: moving)
          }
        }.clipped()
      }.frame(height: label == "Amount" ? 36 : 21)
    }.accessibilityHidden(true).onAppear { moving = true }
  }
}
struct CheckboxToggle: ToggleStyle {
  func makeBody(configuration: Configuration) -> some View {
    Button {
      configuration.isOn.toggle()
    } label: {
      HStack(spacing: 12) {
        Image(systemName: configuration.isOn ? "checkmark.square.fill" : "square").font(
          .system(size: 23))
        configuration.label
        Spacer()
      }.frame(minHeight: 44).contentShape(Rectangle())
    }.buttonStyle(.plain).accessibilityValue(configuration.isOn ? "Checked" : "Unchecked")
  }
}

struct ConnectionSettings: View {
  @ObservedObject var model: ScanSession
  @Environment(\.dismiss) private var dismiss
  @State private var hotspot = ""
  @State private var token = ""
  @State private var message: String?
  private func save() throws { try model.configureHotspot(address: hotspot, token: token) }
  var body: some View {
    NavigationStack {
      Form {
        Section {
          Button {
            do {
              try save()
              message = nil
              Task { await model.reconnect() }
            } catch { message = error.localizedDescription }
          } label: {
            HStack {
              if model.reconnecting { ProgressView() } else { Image(systemName: "arrow.clockwise") }
              Text(model.reconnecting ? "Reconnecting…" : "Reconnect")
            }
          }.disabled(model.reconnecting || model.fixtureMode)
            .accessibilityIdentifier("reconnect-settings")
          if let status = model.connectionStatus { Text(status).font(.subheadline) }
        } footer: {
          Text("Connect the Mac to this iPhone’s Personal Hotspot.")
        }
        Section("Hotspot") {
          TextField("Mac address", text: $hotspot).keyboardType(.URL)
            .textInputAutocapitalization(.never).autocorrectionDisabled()
            .accessibilityIdentifier("hotspot-address")
          SecureField("Access token", text: $token).textInputAutocapitalization(.never)
        }.disabled(model.reconnecting)
        if let message { Text(message).foregroundStyle(.orange) }
      }.scrollContentBackground(.hidden).background(DocumentBackdrop())
        .toolbar(.hidden, for: .navigationBar)
        .safeAreaInset(edge: .top) {
          ScreenHeader(subtitle: "Connection") {
            Button("Done") { dismiss() }.frame(minWidth: 44, minHeight: 44)
            Button("Save") {
              do {
                try save()
                dismiss()
              } catch { message = error.localizedDescription }
            }.frame(minWidth: 44, minHeight: 44).disabled(model.reconnecting)
          }.padding(.horizontal, 16).padding(.top, 12)
        }
    }.onAppear {
      hotspot = model.hotspotAddress
      token = model.token
    }
  }
}
struct JSONOutput: View {
  let response: JSONValue?
  let mobileValues: JSONValue?
  @State private var original = true
  @Environment(\.dismiss) private var dismiss
  var body: some View {
    NavigationStack {
      VStack {
        Picker("Output", selection: $original) {
          Text("Original JSON").tag(true)
          Text("Mobile values").tag(false)
        }.pickerStyle(.segmented).padding()
        JSONTextView(
          text: original
            ? (response?.pretty ?? "No response available.")
            : (mobileValues?.pretty ?? "No mobile values available.")
        )
        .accessibilityIdentifier("json-content")

      }.background(DocumentBackdrop()).toolbar(.hidden, for: .navigationBar)
        .safeAreaInset(edge: .top) {
          ScreenHeader(subtitle: "Structured output") {
            Button("Done") { dismiss() }.frame(minWidth: 44, minHeight: 44)
          }.padding(.horizontal, 16).padding(.top, 12)
        }
    }
  }
}
struct DocumentViewer: View {
  let image: UIImage?
  @Environment(\.dismiss) private var dismiss
  @State private var zoom: CGFloat = 1
  var body: some View {
    NavigationStack {
      ScrollView([.horizontal, .vertical]) {
        if let image {
          Image(uiImage: image).resizable().scaledToFit().frame(
            width: UIScreen.main.bounds.width * zoom
          ).accessibilityLabel("Captured document")
        }
      }.background(DocumentBackdrop(image: image)).toolbar(.hidden, for: .navigationBar)
        .safeAreaInset(edge: .top) {
          ScreenHeader(subtitle: "Your document") {
            Button(zoom == 1 ? "Zoom in" : "Fit") { zoom = zoom == 1 ? 2.5 : 1 }
              .frame(minWidth: 44, minHeight: 44)
            Button("Done") { dismiss() }.frame(minWidth: 44, minHeight: 44)
          }.padding(.horizontal, 16).padding(.top, 8)
        }
    }
  }
}

struct JSONTextView: UIViewRepresentable {
  let text: String
  func makeUIView(context: Context) -> UITextView {
    let view = UITextView()
    view.isEditable = false
    view.isSelectable = true
    view.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
    view.backgroundColor = .secondarySystemBackground
    view.textColor = .label
    view.textContainerInset = UIEdgeInsets(top: 18, left: 16, bottom: 24, right: 16)
    view.textContainer.lineBreakMode = .byCharWrapping
    view.textContainer.widthTracksTextView = true
    view.alwaysBounceHorizontal = false
    view.showsHorizontalScrollIndicator = false
    view.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)
    return view
  }
  func updateUIView(_ view: UITextView, context: Context) {
    if view.text != text {
      view.text = text
      view.setContentOffset(.zero, animated: false)
    }
  }
}
