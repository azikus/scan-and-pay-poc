# Scan & Pay — iOS

Native SwiftUI app for iPhone, iOS 18+. The first design targets iPhone 16 Pro. It uses Apple Vision document detection with automatic AVFoundation capture, PhotosPicker import, manual crop/rotate, an explicit final-image Send action, and the existing Mac API. No third-party mobile SDK is required.

**Automatic document scan:** point the camera at the paper and hold steady. The area outside the detected paper turns grey; the app captures and straightens the document, then opens **Adjust image**. Crop/rotate, Retake and explicit Send work as before. **Auto / Manual** toggles automatic capture, and the shutter and Import remain available. Detection runs on the phone. See [scanning behavior and verification](../docs/IOS_DOCUMENT_SCANNING.md).

The 13 October [invoice-context update](../docs/INVOICE_CONTEXT.md) shows issuer/language context and backend field applicability in review. Required blank fields are visible; optional empty fields are under **Add other details**. Populated/edited/uncertain fields and selected-candidate warnings stay visible. Older saved responses use route-based fallback rules. Original JSON, confirmation values and recovery remain separate from presentation guidance.

Open `ScanAndPay.xcodeproj` in Xcode. `project.yml` is the source for regenerating it with `xcodegen generate --spec ios/project.yml` from the repository root. Build the `ScanAndPay` scheme. For a physical phone, select the intended signing team in Xcode, connect/unlock/trust the phone, enable Developer Mode, and select it as the run destination. No team ID, provisioning profile or signing credential is committed. The initial build was signed locally with the existing Azikus development identity and installed on the connected iPhone 16 Pro; its synthetic UI flow passed on iOS 26.6.1.

## Connection

**Hotspot:** connect the Mac to this iPhone’s Personal Hotspot and keep the Mac awake. In the Mac admin, expand **Connection**, copy the Mac address into the app’s **Connection → Hotspot → Mac address**, and tap **Reconnect**. There is one saved address and a `Connected via hotspot` result. The capture arrow and scan-menu Reconnect use that same address, with no alternate-route fallback. The address survives restarts; update it from the admin if it changes. Existing local Wi-Fi settings migrate automatically, and old USB settings are removed. See [connection setup](../docs/CONNECTION_SETUP.md).

Reconnect performs authenticated reads only. It does not send a new image, recover an uncertain upload automatically, or confirm a draft. Draft fields, image, profile, idempotency key and pending confirmation are preserved. New uploads retain the backend's stable `server_id`; reconnect refuses a different backend. Older accepted drafts are verified by scan ID and uploaded-image hash before changing their address. An older uncertain upload without either identity stays on its original address until recovered. Reconnect is disabled while uploading, polling or saving; late/backgrounded checks cannot overwrite newer session state.

**Method selection:** Country context is standard for supported LLM methods; there is no separate old/context choice. In the local admin’s **Next scan** form, choose **Method**, choose **Model / provider**, and press **Use for next scan**. A new Send reads the advertised profile ID/version and freezes both for that upload. Switching the admin choice does not change a saved draft or its recovery path. The latest selection and runtime snapshot is in [current status](../docs/CURRENT_STATUS.md); saved drafts retain their original profile. The live catalogue lists current configured choices; [API status](../docs/API_CONNECTION_STATUS.md) records dated provider evidence. The seven-choice mobile test configuration is historical.

In the app’s Connection settings, enter the Mac’s reachable base URL and the existing `SCANPAY_TOKEN` from the private root `.env`. The token is stored in this device’s Keychain. Provider credentials stay on the Mac. Use the Mac’s local HTTP address while it is connected to the iPhone hotspot. Physical phones reject localhost. Allow local-network access when iOS prompts.

The running backend uses the stable source archive recorded in [current status](../docs/CURRENT_STATUS.md); preserve it and its private launcher. For a fresh, stopped setup, start one backend with `.venv/bin/scanpay-serve` from the repository root. It keeps loopback available and follows active private/link-local IPv4 addresses on physical Mac interfaces. Use `http://127.0.0.1:8000/admin` on the Mac and its Connection section to find the phone URL. Do not run a second backend against the same data directory. Plain Uvicorn remains a manual alternative without automatic updates. The settings accept a local HTTP address; USB and hosted endpoints are no longer offered. The client does not follow redirects.

No scan request leaves the app before Send. The client verifies the advertised exact profile/version, uploads one oriented PNG tagged `X-Scanpay-Client: mobile` and polls its scan ID; the app never calls a provider. [Current status](../docs/CURRENT_STATUS.md) records the latest source and dated runtime evidence. Local spending/cumulative-call enforcement is removed from the updated backend; existing records remain private and preserved. Reconnect and UI checks make no paid calls.

Send immediately shows **Preparing image…** while encoding the PNG off the UI thread. Repeated taps cannot submit a second scan. The preview image does not intercept touches before sending, and the full primary-button surface accepts taps. Failed preparation retains the image with an error; backgrounding before preparation finishes cancels submission. Permission prompts do not count as backgrounding. An unsent capture remains in memory only and must be retaken after an app relaunch.

## Appearance and motion

As of 13 October, the app uses dark mode throughout, with semantic foreground colours, the reversed Azikus mark, dark document backdrops and ice-blue completion accents. Document images retain their original pixels. The signed build is installed on the paired iPhone 16 Pro; all four offline native UI flows pass.

Every screen shares the Azikus mark and **Scan & Pay** title, with a subtitle for the current screen or processing state. Header actions move to a separate row at accessibility text sizes.

The scan screen shows the complete camera frame between dark Liquid Glass header and capture panels. Aspect-fit keeps the full live field of view visible, with the detected-paper mask aligned to it. Automatic scans are straightened from the full-resolution photo before adjustment; manual shutter and imported images retain the complete original for cropping. Adjust image, Ready to send, review, confirmation and completion share the glass treatment; settings, JSON navigation and the image viewer use the same dark appearance. Documents and JSON remain sharp and readable. Native Liquid Glass controls are used on iOS 26, with material/solid accessibility fallbacks on older systems. Capture, crop and preview transition together; crop rotation/reset animate and the image carries between crop and preview. Reduce Motion avoids spatial animation. See [behavior, hotspot verification](../docs/IOS_GLASS_AND_MOTION.md).

## Optional demo displays

**Connection → Demo displays** enables a best-effort sanitized lifecycle channel. Select the matching short phone session ID in the SUNMI companion. The setting defaults off. Enabled telemetry sends phase/journey identifiers and foreground heartbeats, never invoice pixels, payment fields, edits or credentials in event bodies. Capture/crop/preview, actual upload, review, confirmation-sheet activity, reset and backgrounding are observed. A backend-confirmed save drives completion; a button tap does not.

Pending uploads freeze optional demo session/journey IDs alongside their existing key/options/profile; recovery retains those headers. Legacy pending records still decode. The observer has independent short timeouts and failures do not change extraction, review or confirmation. The `-synthetic-preview` fixture remains entirely offline, even when the setting is enabled. See [SUNMI setup and testing](../sunmi/companion/README.md).

## Review and JSON

- The image stays behind the expandable review sheet and can be opened at full size. Editing expands the sheet. Accessibility text sizes use the large detent.
- Review and confirmation group all extracted fields into **Payment details** and **Invoice details**, with amount/recipient prominent in confirmation. A new draft accepts observed document values, including normalizations of printed text, and omits untouched inference/derived hints and recipient-role fallbacks. This is based on recorded provenance, not independent proof of correctness. User additions/corrections are marked **Edited**. See [sheet behavior and checks](../docs/CONFIRMATION_SHEETS.md).
- Every displayable field has a shimmer placeholder while extraction is pending; Reduce Motion uses static placeholders. The API returns fields together. A ready result is shown immediately; empty and untouched inferred rows are omitted.
- Missing values remain in JSON and are available under **Add missing details**, with the backend’s warnings retained. Leading zeros and decimal strings remain strings; comma-decimal input is normalized to the wire decimal point; selecting another candidate keeps its destination, amount and reference together.
- **Scan options → View JSON** displays the complete original response and a separate mobile-values snapshot, both pretty-printed with explicit nulls in a selectable, vertically scrolling UIKit text view that wraps long lines. Edits do not rewrite original observations or evidence.
- Checking the review box enables **Pay** for a selected, reviewable draft. Pay opens a summary with **Confirm** and **Keep editing**. Missing/invalid payment fields are listed in that summary and remain advisory for this PoC; empty/error results or no selected candidate still block confirmation. Confirm saves the separate simulated review to the Mac, then shows a checkmark/ring/particle celebration and returns to capture. Reduce Motion uses a brief static reveal. There is no payment integration, payment verification or receipt.

## Interruption behavior

The pending image bytes, options, idempotency key, accepted scan ID, edits and optional edited-field IDs are stored atomically in Application Support, protected until first device unlock and excluded from backups. Reset removes this mobile record; it does not delete backend evidence or cancel accepted work. An interrupted accepted scan resumes polling. An uncertain upload is recovered explicitly with the same bytes/options/key. It never silently starts a new paid scan.

Confirmations use a persisted UUID and frozen JSON body. Retrying a save or reopening the app retains that same confirmation ID and body. Edits are locked until its outcome is resolved or the draft is explicitly cleared. Mobile values shows the actual frozen payload during recovery; no historical confirmation is rewritten by the new extraction-only display policy. Backgrounding stops camera/mobile network work; generation checks keep late responses from reopening a discarded scan.

## Offline verification

Add `-synthetic-preview` to the scheme’s launch arguments for a clearly labeled local fixture flow. It makes no network requests and uses only bundled synthetic data. Remove the argument for normal capture/networking. Fixture timing is not extraction performance.

From the repository root, using an installed iPhone simulator:

```sh
xcodebuild -project ios/ScanAndPay.xcodeproj -scheme ScanAndPay \
  -destination 'platform=iOS Simulator,id=A01D44F3-7512-4AED-BD55-5B5688DB2015' \
  -derivedDataPath .local/ios-build CODE_SIGNING_ALLOWED=NO test
```

Unit tests cover JSON/null/string preservation, linked candidates, crop pixels/orientation, profile mismatch, duplicate sends, interrupted upload recovery, accepted-scan polling, persisted confirmation recovery, empty outcomes and stale-result isolation. UI tests exercise capture, crop, Send, review, JSON, confirmation and reset. Markus accepted real-camera capture, overall integration and explicit phone Send on 13 October. No measured device capture-to-review timing study is claimed.

The simulator ID above is the verified local destination; use `xcrun simctl list devices available` to choose an installed simulator on another Mac. The folder move preserves the app bundle ID, project-relative source/resource references and on-device recovery format. It requires no physical-phone reinstall or unlock. See [reorganization verification](../docs/REPOSITORY_REORGANIZATION_HANDOFF.md).

Azikus uses the supplied original logo/mark artwork. Bundled Hanken Grotesk is the licensed fallback for ABC Monument Grotesk, whose deployable font files were not supplied; its OFL is retained in Resources. Status colors and motion are app choices.
