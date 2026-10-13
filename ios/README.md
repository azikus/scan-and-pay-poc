# Native iPhone app

SwiftUI app for iOS 18+, bundle ID `com.azikus.scanpay.poc`. The [product guide](../README.md#the-mobile-experience) shows the flow/screenshots; this file covers building and native behavior.

## Build

Open `ScanAndPay.xcodeproj` and build scheme `ScanAndPay`. `project.yml` is the source for regeneration from the repository root:

```sh
xcodegen generate --spec ios/project.yml
```

For a physical phone, select the supplied signing team, connect/unlock/trust the phone and enable Developer Mode. Upgrade in place; preserve bundle ID, Keychain and Application Support. Team/provisioning credentials are not committed.

For simulator tests, select an available destination:

```sh
xcrun simctl list devices available
xcodebuild -project ios/ScanAndPay.xcodeproj -scheme ScanAndPay \
  -destination 'platform=iOS Simulator,id=SIMULATOR_UUID' \
  -derivedDataPath .local/ios-build CODE_SIGNING_ALLOWED=NO test
```

## Capture and presentation

AVFoundation supplies full-frame preview/capture. Apple Vision document detection masks the surrounding area, waits for stable paper geometry, then captures and straightens the document. Auto/Manual, shutter and import preserve manual fallback. Crop/rotate/Edit crop/Reset crop retain the full original photo. Lifetime checks discard late detections/photos after capture ends.

Dark Liquid Glass spans capture, crop, preview, review, confirmation and settings. Semantic colors, material/solid fallbacks, accessibility sizing and Reduce Motion retain legibility. Document pixels and selectable wrapped JSON stay readable.

No request leaves before explicit Send. PNG preparation runs off the UI thread with immediate progress and duplicate-tap guards. Backgrounding before preparation completes cancels submission; an unsent capture remains in memory only.

## Connection and selection

Connect the Mac to this iPhone's Personal Hotspot. Enter the advertised Mac address and local API token in Connection, then Reconnect. One saved private address is exposed; there is no USB/cloud selector or automatic discovery. The token lives in Keychain. Provider credentials stay on the backend. See [setup](../docs/SETUP.md).

New Send reads/freezes the shared exact profile ID/version. Reconnect performs authenticated reads and checks stable backend identity, preserving frozen pending requests. A changed admin default never updates an existing upload or draft.

## Review and recovery

The expandable sheet exposes document/payment fields, required blanks, candidate warnings and explicit edits. Optional blanks sit under Add other details. Untouched inferred/derived values are not promoted into new confirmed values. Review guidance is read-only; original JSON and evidence remain intact.

Checking the review box enables Pay for a selected usable draft. Pay opens the summary; Confirm saves the separate simulated review, celebrates and resets. Missing/invalid fields are advisory for useful incomplete PoC drafts. Empty/error/unselected drafts cannot confirm. No funds move.

Pending bytes/options/key/profile, accepted scan ID, edits and confirmation UUID/frozen body are stored atomically in Application Support, protected until first unlock and excluded from backups. Accepted work resumes polling; uncertain uploads recover explicitly with the same request. An unresolved confirmation keeps values locked. Reset removes the mobile draft, not backend evidence. Late responses cannot reopen a discarded journey.

## Optional live displays and fixtures

Connection → Demo displays publishes sanitized phase/journey/sequence snapshots and heartbeats. Pending requests freeze optional session/journey IDs. Observer failures do not affect extraction or confirmation; synthetic-preview remains offline. See [display frontend](../frontend/demo/README.md).

`-synthetic-preview` provides bundled synthetic UI fixtures without network calls. Remove the argument for real operation. Tests exercise field/candidate/null preservation, geometry/orientation, document stability/correction, selection mismatch, duplicates, interrupted requests, frozen confirmations and stale-result isolation. Fixture timing is not provider latency.

Resources contain original Azikus artwork and licensed Hanken Grotesk, the disclosed fallback for ABC Monument Grotesk.
