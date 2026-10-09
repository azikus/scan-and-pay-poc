import SwiftUI

struct PaymentConfirmation: View {
  let draft: PaymentDraft
  let cancel: () -> Void
  let confirm: () -> Void
  var body: some View {
    VStack(alignment: .leading, spacing: 0) {
      HStack {
        Image(systemName: "arrow.up.right").font(.system(size: 24, weight: .medium))
          .frame(width: 56, height: 56).background(Brand.ice, in: Circle()).foregroundStyle(
            Brand.ink)
        Spacer()
        Button(action: cancel) { Image(systemName: "xmark").frame(width: 44, height: 44) }
          .accessibilityLabel("Cancel payment")
      }.padding(.bottom, 28)
      Text("Confirm payment").font(Brand.font(30, .semibold))
      ScrollView {
        VStack(alignment: .leading, spacing: 22) {
          Text(draft.summaryAmount).font(Brand.font(46, .semibold)).minimumScaleFactor(0.6)
            .lineLimit(2).padding(.top, 26)
          Text(draft.summaryRecipient).font(Brand.font(21, .semibold))
          Divider()
          ForEach(
            draft.visibleFields.filter {
              $0.id.contains("/destination/") || $0.id.hasSuffix("/remittance/reference")
            }
          ) { field in
            VStack(alignment: .leading, spacing: 6) {
              Text(field.label).font(Brand.font(12)).foregroundStyle(.secondary)
              Text(field.value ?? "").font(Brand.font(17)).textSelection(.enabled)
            }
          }
          if !draft.paymentIssues.isEmpty {
            VStack(alignment: .leading, spacing: 9) {
              Label("Details to note", systemImage: "exclamationmark.circle").font(
                Brand.font(15, .semibold))
              ForEach(draft.paymentIssues, id: \.self) { Text($0).font(Brand.font(14)) }
            }.padding(18).frame(maxWidth: .infinity, alignment: .leading)
              .background(Color.orange.opacity(0.12), in: RoundedRectangle(cornerRadius: 18))
          }
        }.frame(maxWidth: .infinity, alignment: .leading)
      }
      VStack(spacing: 8) {
        Button(action: confirm) {
          HStack {
            Text("Confirm")
            Image(systemName: "checkmark")
          }.frame(maxWidth: .infinity)
        }.buttonStyle(PrimaryButton()).accessibilityIdentifier("confirm-pay")
        Button("Keep editing", action: cancel).font(Brand.font(16)).frame(
          maxWidth: .infinity, minHeight: 48
        )
        .accessibilityIdentifier("cancel-pay")
      }.padding(.top, 18)
    }.padding(24).background(Color(uiColor: .systemBackground)).tint(.primary)
  }
}

private struct CompletionCheck: Shape {
  func path(in rect: CGRect) -> Path {
    var path = Path()
    path.move(to: CGPoint(x: rect.width * 0.19, y: rect.height * 0.51))
    path.addLine(to: CGPoint(x: rect.width * 0.42, y: rect.height * 0.73))
    path.addLine(to: CGPoint(x: rect.width * 0.83, y: rect.height * 0.29))
    return path
  }
}

struct CompletionCelebration: View {
  let dismiss: () -> Void
  @Environment(\.accessibilityReduceMotion) private var reduceMotion
  @State private var reveal = false
  @State private var burst = false
  @State private var draw = false
  var body: some View {
    ZStack {
      Brand.ink.ignoresSafeArea()
      VStack(spacing: 32) {
        Spacer()
        ZStack {
          if !reduceMotion {
            ForEach(0..<2) { index in
              Circle().stroke(Brand.ice.opacity(burst ? 0 : 0.65), lineWidth: 1.5)
                .frame(width: 150, height: 150).scaleEffect(burst ? 2.4 + Double(index) * 0.3 : 0.8)
                .animation(.easeOut(duration: 1.35).delay(Double(index) * 0.16), value: burst)
            }
            ForEach(0..<32) { index in
              let angle = Double(index) * .pi * 2 / 32
              let distance = burst ? 120.0 + Double((index * 17) % 70) : 40
              Capsule().fill(index.isMultiple(of: 3) ? Color.white : Brand.ice)
                .frame(
                  width: index.isMultiple(of: 3) ? 4 : 3, height: index.isMultiple(of: 3) ? 12 : 6
                )
                .rotationEffect(.degrees(burst ? Double(index * 37) : 0))
                .offset(x: cos(angle) * distance, y: sin(angle) * distance + (burst ? 24 : 0))
                .opacity(burst ? 0 : 1)
                .animation(.easeOut(duration: 1.4).delay(Double(index % 4) * 0.04), value: burst)
            }
          }
          Circle().fill(Brand.ice).frame(width: 144, height: 144)
            .scaleEffect(reveal ? 1 : reduceMotion ? 1 : 0.65)
            .shadow(color: Brand.ice.opacity(0.15), radius: 45)
          CompletionCheck().trim(from: 0, to: draw ? 1 : 0)
            .stroke(Brand.ink, style: StrokeStyle(lineWidth: 7, lineCap: .round, lineJoin: .round))
            .frame(width: 75, height: 75)
        }.frame(height: 210).accessibilityHidden(true)
        Text("Complete").font(Brand.font(42, .semibold)).foregroundStyle(.white)
          .opacity(reveal ? 1 : 0).offset(y: reveal || reduceMotion ? 0 : 12)
          .accessibilityIdentifier("complete")
        Spacer()
        Button("Scan another", action: dismiss).font(Brand.font(17, .semibold))
          .foregroundStyle(Brand.ice).frame(minHeight: 48).padding(.bottom, 34)
          .accessibilityIdentifier("scan-another")
      }
    }.task {
      UINotificationFeedbackGenerator().notificationOccurred(.success)
      withAnimation(
        reduceMotion ? .easeOut(duration: 0.15) : .spring(response: 0.55, dampingFraction: 0.65)
      ) { reveal = true }
      try? await Task.sleep(for: .milliseconds(200))
      guard !Task.isCancelled else { return }
      withAnimation(.easeOut(duration: reduceMotion ? 0.1 : 0.45)) { draw = true }
      burst = true
      try? await Task.sleep(for: .seconds(3))
      if !Task.isCancelled { dismiss() }
    }
  }
}
