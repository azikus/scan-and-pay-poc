# iOS Liquid Glass, motion and connectivity — 12 October 2026

Markus requested native Liquid Glass, screen transitions (especially cropping), a review of client connectivity/hosting options, and a working hotspot connection. This starts the scoped iOS polish work after the initial presentation; it does not authorize cloud deployment or another provider experiment.

## UI changes

**Scan-screen refinement:** Markus clarified that Liquid Glass should replace the large black scan-screen backgrounds, not only style individual buttons. The initial refinement showed the camera edge to edge behind floating glass panels; the later framing fix below replaces that zoomed layout with a fully visible camera frame between the panels. These use native iOS 26 glass, regular material on older systems, and opaque light surfaces with Reduce Transparency. Controls inside each panel remain plain to avoid stacking glass layers. The original dark Azikus mark is used on the light header. The subsequent whole-flow refinement below extends this treatment beyond capture; capture pixels and upload behavior are unchanged.

- Native iOS 26 `glassEffect` on secondary controls and tinted primary actions. iOS 18–25 uses material secondary controls and a solid ice-blue primary action. Reduce Transparency uses solid surfaces. The Azikus artwork and existing Hanken Grotesk fallback remain unchanged.
- Capture/crop/document transitions use a brief spring with a shared document frame between crop and preview. Review/confirmation retain native sheet presentation. Processing fields animate into the ready review.
- Crop rotation animates one quarter-turn, fits the rotated image inside its canvas, then commits the same pixel-preserving rotation. Actions wait until that transition finishes. Reset eases back to the full image; a rule-of-thirds guide appears while adjusting the crop.
- Reduce Motion replaces spatial transitions with a short fade and performs crop rotation/reset immediately. Existing shimmer and completion reduced-motion behavior remains.
- Extraction, confirmation, persistence, idempotency, review rules and payment simulation are unchanged. Nothing is sent before explicit Send.

## Glass throughout the flow

Markus then requested the same treatment everywhere, specifically Adjust image and Ready to send. Both now use the shared glass panels and a soft, image-derived backdrop instead of black chrome. The actual document remains sharp and fitted within the available space; the crop mask still darkens only the excluded pixels. Crop handles gain a slate outline for contrast on white paper. Rotation, crop coordinates, pixel output and gestures are unchanged.

Review and Pay confirmation use glass header/action panels with legible fields between them. Connection settings, JSON navigation and the image viewer use the light backdrop and native navigation controls; the selectable JSON text retains an opaque readable surface. Completion uses the same light/glass palette and existing celebration, with reduced-motion behavior intact. The app uses a consistent light appearance. iOS 26 uses native glass, earlier iOS uses regular material, and Reduce Transparency uses solid panels without the blurred document backdrop.

## Camera framing correction

Markus reported that the live preview changed substantially after capture. The edge-to-edge preview used `resizeAspectFill`, which zoomed/cropped a photo-shaped stream into the much taller phone screen; Adjust image correctly displayed the entire captured image. The preview now uses `resizeAspect`, and its viewport sits between the glass header and capture controls so the whole frame is visible. Capture keeps the full-resolution photo; no automatic pixel crop was introduced to conceal the mismatch. Adjust image may display it at a different size because its controls take a different amount of space, but it no longer reveals edges hidden by an aspect-fill preview.

Apple documents the preview layer’s [videoGravity](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer/videogravity) display modes. This fix changes live framing/layout only; manual crop/rotation, saved drafts, Send and backend processing are unchanged.

## Send responsiveness follow-up

Markus reported remaining on Ready to send after tapping Send, while Edit crop still worked and no error was visible. The simulator baseline responded to both side and lower-padding taps, so the exact physical-device failure was not reproduced. The preview's image tap layer is now disabled before Send and clipped to its viewport; primary actions explicitly use their full rounded surface for hit testing. This removes an unnecessary gesture layer from the affected screen without changing image pixels.

Real photo PNG encoding previously ran on the main actor before any progress state. Send now enters **Preparing image…** immediately and encodes off the UI thread, then performs the existing selection/upload sequence. Cancellation and generation checks prevent a completed encoding from uploading after background/reset; duplicate taps cannot start another preparation. Reconnecting is visible on the disabled Send button, and missing-image or unexpected saved-scan guards give an explanation instead of silently returning. Temporary inactive states, such as permission prompts, no longer cancel work; actual backgrounding retains the existing pause/recovery behavior. Saved image bytes, profile choice, idempotency keys and confirmations retain their existing semantics.

Verification/evidence for this follow-up is under `.local/send-fix-2026-10-12/`. The baseline surface-tap test passed before the change and must not be described as a reproduced failure. Unit coverage adds suspended preparation, duplicate taps, encoding failure and background cancellation without requests. Mac loopback and hotspot authenticated profile reads both returned 200; no agent inference or backend restart was performed. Physical Send acceptance still requires a fresh capture after installation; an unsent in-memory preview is not preserved across app relaunch.

All **31 offline tests passed** on iOS 26.2 (27 native unit/recovery tests and four UI flows). Signed build and Swift lint/diff checks passed. The update was installed/opened on the physical iPhone and its authenticated hotspot check succeeded at **22:13:40 UTC / 23:13:40 London time** on 12 October. Stored phone records were not cleared or copied; the unsent preview requires a fresh capture.

## Shared branded header

Markus requested the Azikus logo and Scan & Pay title on each screen, with a changing subtitle. A shared `ScreenHeader` now displays the supplied dark Azikus mark, **Scan & Pay**, and the current context: Scan a document, Adjust image, Ready to send, Your document, the current processing/recovery message, Review details, Confirm payment, Connection, Structured output or Scan complete. Capture keeps its connection status (or synthetic-preview marker) as a separate detail below the subtitle. Existing actions remain in the header, with a separate action row at accessibility text sizes. This is a presentation change only.

## Current connectivity

**Latest decision:** Markus requested only the working iPhone Personal Hotspot solution. The app now has one **Hotspot → Mac address** field and Reconnect checks that address only. USB configuration/fallback and hosted endpoint selection are removed from the current setup. Existing saved local Wi-Fi addresses migrate to the hotspot setting; obsolete USB/Wi-Fi keys are removed. Public HTTPS and link-local URLs are rejected by the new setting. Low-level URL support remains for safely recovering existing saved drafts, without offering other connection methods.

The app cannot identify whether a private address belongs to a hotspot or another local network. It accepts a private IPv4 address or `.local` hostname; connect the Mac to this iPhone’s Personal Hotspot before using it. There is no automatic phone discovery. The Mac launcher still follows local interface changes, and the admin hides link-local/USB choices. Draft identity checks, frozen requests and saved confirmation values remain intact.

On 12 October, the running backend authenticated over loopback and `http://172.20.10.2:8000`. The phone was configured for this hotspot route and reported **Wi-Fi connected at 21:04:02 UTC / 22:04:02 London time**. This was an authenticated profile read, not an invoice submission. Its diagnostic contains only connection information at `.local/ios-glass-2026-10-12/phone-hotspot-check.json`. Phone invoice/draft files were not copied or cleared. This dated verification preceded the hotspot-only UI simplification.

Addresses may change after reconnecting. Use the admin Connection panel to obtain the current URL and update the phone when necessary. Keep the Mac awake during the demo. The existing backend process and private state remain in place.

## Hosting deferred

Keep using the hotspot and local Mac backend. The earlier Railway/Hostinger assessment is deferred; no hosting account, subscription, endpoint, data migration or deployment was created. Revisit hosting as a separate task if independent phone use is needed.

## Camera-framing verification

- Signed build and all **three UI flows passed** after the framing change. The first narrowly selected run executed zero tests; it is not counted. The corrected full UI run is recorded in `ui-tests.log` and synthetic capture screenshots were inspected to confirm all edges remain outside the glass controls.
- Installed/opened on the physical iPhone. The first hotspot read failed; both Mac endpoints subsequently returned 200 with the unchanged token, and the phone retry connected at **22:01:52 UTC / 23:01:52 London time** on 12 October. The agent did not restart the backend or submit an invoice.
- A fresh real-camera capture remains for Markus to validate the live/still field of view; simulator results are not physical-camera acceptance. The full captured photo and manual crop behavior are preserved.
- Private evidence: `.local/camera-framing-2026-10-12/`. Swift lint/diff checks passed. Unrelated workspace files were left untouched.

## Branded-header verification

- All **three UI flows passed** after the header change, covering capture, crop/preview, JSON, editing, confirmation and reset. Synthetic capture, crop and confirmation screenshots were visually checked for logo/title/subtitle layout. Swift lint and diff checks passed.
- Signed build passed and was installed/opened on the physical iPhone. Its authenticated hotspot check succeeded at **21:48:14 UTC / 22:48:14 London time** on 12 October. No agent inference or saved-draft change.
- Private evidence: `.local/branded-headers-2026-10-12/`. The earlier 24 native tests remain the unchanged domain/recovery baseline; this follow-up only reran the affected UI flows.

## Whole-flow glass verification

- **27 tests passed** on iOS 26.2: 24 native unit/recovery tests and all three UI flows. Coverage includes saved-address migration, frozen recovery, crop rotation/reset/retake, JSON, field editing and confirmation/reset.
- Inspected synthetic iOS 26.2 screenshots of Adjust image, review, confirmation and completion; manually checked Adjust image → Ready to send on iOS 18.6 to verify the fallback and sharp document rendering.
- Signed build passed; the app was installed and opened on the physical iPhone. Its authenticated hotspot check succeeded at **21:41:33 UTC / 22:41:33 London time** on 12 October. Existing phone data stayed in place; no agent invoice submission or budget/configuration change.
- Evidence is private under `.local/glass-flow-2026-10-12/`, including the test log, exported screenshots and narrow connection diagnostic. Swift lint and diff checks pass.

## Scan-panel follow-up verification

- All **three existing UI tests passed** on iOS 26.2, including capture → crop → review → confirmation/reset, crop rotation/reset/retake, and editable invoice details. This later run successfully executes the crop test that was blocked by simulator infrastructure during the earlier update.
- Signed build passed and the update was installed/opened on the physical iPhone with its saved data intact. An authenticated hotspot read passed at **21:35:00 UTC / 22:35:00 London time** on 12 October. No invoice was submitted by the agent.
- Synthetic capture screenshots were inspected on iOS 26.2 and iOS 18.6: both floating panels, dark logo, text, shutter and Import fit on the iPhone 16 Pro without the previous black header/footer. Screenshots verify layout/material fallback; live-camera glass appearance remains visible on the installed phone for Markus to assess.
- Private build/test logs, screenshots and the narrow connection diagnostic are in `.local/scan-glass-panels-2026-10-12/`. Swift formatting and diff checks pass.

## Hotspot-only follow-up verification

- All **24 native unit/recovery tests passed** on iOS 26.2, including saved-address migration, removal of old route keys, no fallback after a failed check, preservation of frozen confirmations and rejection of a different backend.
- The signed update was installed and opened on the physical iPhone. It reported a single successful **hotspot** attempt at **21:31:30 UTC / 22:31:30 London time** on 12 October, using `http://172.20.10.2:8000`. Private diagnostic: `.local/hotspot-only-2026-10-12/phone-check.json`.
- Swift formatting, JavaScript syntax and diff checks passed. The running admin serves the updated asset without a backend restart. This follow-up made no inference call and did not change budgets, provider selection or saved draft contents.

## Earlier Liquid Glass verification

- The iOS 26.2 iPhone 16 Pro simulator passed all **23 native unit/recovery tests and both existing UI tests**, including JSON wrapping, editable fields, confirmation/reset and saved-value behavior. Synthetic review/confirmation/capture screenshots were inspected.
- The new crop regression test compiles. Its automated execution and the additional iOS 18 run were blocked before test startup by Xcode simulator service-hub/runner errors. These are not recorded as passing tests. A clean simulator restart allowed direct UI verification of capture → crop → Rotate → Reset crop → Use crop → Edit crop on iOS 26.2; controls re-enabled after rotation and the image stayed in bounds. Screenshot: `manual-crop.png`. Direct iOS 18.6 inspection also verified rotation and the material fallback. A primary-action contrast issue was corrected and visually rechecked in `manual-ios18-final.png`.
- Signed build succeeded and was installed/opened on the physical iPhone 16 Pro (iOS 26.6.1), preserving its existing app data. The final fallback-contrast revision also built, installed and relaunched successfully after Markus unlocked the phone. A fresh authenticated hotspot check reported Wi-Fi connected at 21:26:22 UTC / 22:26:22 London time; diagnostic: `.local/ios-glass-2026-10-12/final-phone-hotspot-check.json`. No live invoice or payment was submitted by the agent. Physical animation feel remains for Markus to assess.
- Swift formatting and `git diff --check` pass. The original budget rows/configuration hashes remain unchanged: **2,273 dispatched reservations / €351.95 held**. The backend was not restarted.
- Private evidence, builds, test logs and screenshots are under `.local/ios-glass-2026-10-12/`. Test exports also retain two UIKit `_UIReparentingView` warnings while presenting the menu; the exercised menu/JSON flow passed.
