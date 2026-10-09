# Scan & Pay — iOS

Native SwiftUI app for iPhone, iOS 18+. The first design targets iPhone 16 Pro. It uses AVFoundation capture, PhotosPicker import, manual pixel-preserving crop/rotate, an explicit final-image Send action, and the existing Mac API. No third-party mobile SDK is required.

Open `ScanAndPay.xcodeproj` in Xcode. `project.yml` is the source for regenerating it with `xcodegen generate --spec apps/ios/project.yml` from the repository root. Build the `ScanAndPay` scheme. For a physical phone, select the intended signing team in Xcode, connect/unlock/trust the phone, enable Developer Mode, and select it as the run destination. No team ID, provisioning profile or signing credential is committed. The initial build was signed locally with the existing Azikus development identity and installed on the connected iPhone 16 Pro; its synthetic UI flow passed on iOS 26.6.1.

## Connection

**Reconnect:** tap the circular arrow on the capture screen, Reconnect in Connection settings, or Reconnect in the current scan's menu. The app tries the saved USB address first, then Wi-Fi, with short bounded checks and a visible `Connected via USB` / `Connected via Wi-Fi` result. Both addresses are editable and survive app restarts. A USB address can change after unplugging; if its saved address stops working, Wi-Fi is the fallback. This is saved-address checking, not automatic network discovery. The backend must listen at the current Mac addresses.

Reconnect performs authenticated reads only. It does not send a new image, recover an uncertain upload automatically, or confirm a draft. Draft fields, image, profile, idempotency key and pending confirmation are preserved. New uploads retain the backend's stable `server_id`; reconnect refuses a different backend. Older accepted drafts are verified by scan ID and uploaded-image hash before changing their address. An older uncertain upload without either identity stays on its original address until recovered. Reconnect is disabled while uploading, polling or saving; late/backgrounded checks cannot overwrite newer session state.

**Method selection:** In the local admin’s **Next scan** form, choose **Method**, choose **Model / provider**, and press **Use for next scan**. A new Send reads the advertised profile ID/version and freezes both for that upload. Switching the admin choice does not change a saved draft or its recovery path. OpenAI is the initial selection; older saved OpenAI drafts remain compatible. The seven configured choices and unchanged call/spending limits are recorded in [mobile live testing](../../docs/MOBILE_LIVE_TESTING.md). The fixed-profile setup described below is the initial baseline, superseded by this selection flow.

In the app’s Connection settings, enter the Mac’s reachable base URL and the existing `SCANPAY_TOKEN` from the private root `.env`. The token is stored in this device’s Keychain. Provider credentials stay on the Mac. Physical phones reject localhost; use a Mac `.local` hostname or private LAN address, on the same trusted network. Allow local-network access when iOS prompts.

The existing backend startup command in the root README binds loopback for desktop inspection. For an explicitly arranged device session, bind that same service to the Mac’s private LAN interface (for example `--host 192.168.1.10`, replacing that example with the actual address), and allow the connection through the Mac firewall. Do not run a second backend against the same data directory. Do not expose it publicly. HTTP is allowed only for local development addresses; public hosts require HTTPS, and the client does not follow redirects.

No scan request leaves the app before Send. The client verifies `openai-mini-image-roles-v3@2-5094b6dc13ef5718`, then uploads one oriented PNG tagged `X-Scanpay-Client: mobile` and polls its scan ID. The configured profile uses direct-image `gpt-4.1-mini-2025-04-14`; the app never calls a provider. The authorized [9 October mobile test plan](../../docs/MOBILE_LIVE_TESTING.md) permits at most **20 additional calls / €2.00**, with cumulative limits **2,217 calls / €338.05**. Preserve the original ledger; do not raise these limits automatically.

## Review and JSON

- The image stays behind the expandable review sheet and can be opened at full size. Editing expands the sheet. Accessibility text sizes use the large detent.
- Every displayable field has a shimmer placeholder while extraction is pending; Reduce Motion uses static placeholders. The API returns fields together. A ready result is shown immediately and null-valued result rows are omitted.
- Missing values remain in JSON and are available under **Add missing details**, with the backend’s warnings retained. Leading zeros and decimal strings remain strings; comma-decimal input is normalized to the wire decimal point; selecting another candidate keeps its destination, amount and reference together.
- **Scan options → View JSON** displays the complete original response and a separate mobile-values snapshot, both pretty-printed with explicit nulls in a selectable, vertically scrolling UIKit text view that wraps long lines. Edits do not rewrite original observations or evidence.
- Checking the review box enables **Pay** for a selected, reviewable draft. Pay opens a summary with **Confirm** and **Keep editing**. Missing/invalid payment fields are listed in that summary and remain advisory for this PoC; empty/error results or no selected candidate still block confirmation. Confirm saves the separate simulated review to the Mac, then shows a checkmark/ring/particle celebration and returns to capture. Reduce Motion uses a brief static reveal. There is no payment integration, payment verification or receipt.

## Interruption behavior

The pending image bytes, options, idempotency key, accepted scan ID and edits are stored atomically in Application Support, protected until first device unlock and excluded from backups. Reset removes this mobile record; it does not delete backend evidence or cancel accepted work. An interrupted accepted scan resumes polling. An uncertain upload is recovered explicitly with the same bytes/options/key. It never silently starts a new paid scan.

Confirmations use a persisted UUID and frozen JSON body. Retrying a save or reopening the app retains that same confirmation ID and body. Edits are locked until its outcome is resolved or the draft is explicitly cleared. Backgrounding stops camera/mobile network work; generation checks keep late responses from reopening a discarded scan.

## Offline verification

Add `-synthetic-preview` to the scheme’s launch arguments for a clearly labeled local fixture flow. It makes no network requests and uses only bundled synthetic data. Remove the argument for normal capture/networking. Fixture timing is not extraction performance.

From the repository root, using an installed iPhone simulator:

```sh
xcodebuild -project apps/ios/ScanAndPay.xcodeproj -scheme ScanAndPay \
  -destination 'platform=iOS Simulator,name=iPhone 16 Pro,OS=18.6' \
  -derivedDataPath .local/ios-build CODE_SIGNING_ALLOWED=NO test
```

Unit tests cover JSON/null/string preservation, linked candidates, crop pixels/orientation, profile mismatch, duplicate sends, interrupted upload recovery, accepted-scan polling, persisted confirmation recovery, empty outcomes and stale-result isolation. UI tests exercise capture, crop, Send, review, JSON, confirmation and reset. Real camera quality, LAN permissions and device capture-to-review timing remain physical-device checks.

Azikus uses the supplied original logo/mark artwork. Bundled Hanken Grotesk is the licensed fallback for ABC Monument Grotesk, whose deployable font files were not supplied; its OFL is retained in Resources. Status colors and motion are app choices.
