# iOS Liquid Glass, motion and connectivity — 12 October 2026

Markus requested native Liquid Glass, screen transitions (especially cropping), a review of client connectivity/hosting options, and a working hotspot connection. This starts the scoped iOS polish work after the initial presentation; it does not authorize cloud deployment or another provider experiment.

## UI changes

**Scan-screen refinement:** Markus clarified that Liquid Glass should replace the large black scan-screen backgrounds, not only style individual buttons. Capture now shows the camera edge to edge behind a floating light glass header and capture/import panel. These use native iOS 26 glass, regular material on older systems, and opaque light surfaces with Reduce Transparency. Controls inside each panel remain plain to avoid stacking glass layers. The original dark Azikus mark is used on the light header. Crop and document-review backgrounds remain unchanged; capture pixels and upload behavior are unchanged.

- Native iOS 26 `glassEffect` on secondary controls and tinted primary actions. iOS 18–25 uses material secondary controls and a solid ice-blue primary action. Reduce Transparency uses solid surfaces. The Azikus artwork and existing Hanken Grotesk fallback remain unchanged.
- Capture/crop/document transitions use a brief spring with a shared document frame between crop and preview. Review/confirmation retain native sheet presentation. Processing fields animate into the ready review.
- Crop rotation animates one quarter-turn, fits the rotated image inside its canvas, then commits the same pixel-preserving rotation. Actions wait until that transition finishes. Reset eases back to the full image; a rule-of-thirds guide appears while adjusting the crop.
- Reduce Motion replaces spatial transitions with a short fade and performs crop rotation/reset immediately. Existing shimmer and completion reduced-motion behavior remains.
- Extraction, confirmation, persistence, idempotency, review rules and payment simulation are unchanged. Nothing is sent before explicit Send.

## Current connectivity

**Latest decision:** Markus requested only the working iPhone Personal Hotspot solution. The app now has one **Hotspot → Mac address** field and Reconnect checks that address only. USB configuration/fallback and hosted endpoint selection are removed from the current setup. Existing saved local Wi-Fi addresses migrate to the hotspot setting; obsolete USB/Wi-Fi keys are removed. Public HTTPS and link-local URLs are rejected by the new setting. Low-level URL support remains for safely recovering existing saved drafts, without offering other connection methods.

The app cannot identify whether a private address belongs to a hotspot or another local network. It accepts a private IPv4 address or `.local` hostname; connect the Mac to this iPhone’s Personal Hotspot before using it. There is no automatic phone discovery. The Mac launcher still follows local interface changes, and the admin hides link-local/USB choices. Draft identity checks, frozen requests and saved confirmation values remain intact.

On 12 October, the running backend authenticated over loopback and `http://172.20.10.2:8000`. The phone was configured for this hotspot route and reported **Wi-Fi connected at 21:04:02 UTC / 22:04:02 London time**. This was an authenticated profile read, not an invoice submission. Its diagnostic contains only connection information at `.local/ios-glass-2026-10-12/phone-hotspot-check.json`. Phone invoice/draft files were not copied or cleared. This dated verification preceded the hotspot-only UI simplification.

Addresses may change after reconnecting. Use the admin Connection panel to obtain the current URL and update the phone when necessary. Keep the Mac awake during the demo. The existing backend process and private state remain in place.

## Hosting deferred

Keep using the hotspot and local Mac backend. The earlier Railway/Hostinger assessment is deferred; no hosting account, subscription, endpoint, data migration or deployment was created. Revisit hosting as a separate task if independent phone use is needed.

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
