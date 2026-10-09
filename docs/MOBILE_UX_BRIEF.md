# Mobile app brief — first iOS iteration

**9 October agreement:** Markus selected the image-led sheet, shimmer for every displayable field, omission of null result rows, and Pay / Complete labels with simulation disclosure. He also requested formatted nullable JSON and a private inspector for original JSON plus mobile edits. Native implementation is now authorized and present; [MOBILE_IMPLEMENTATION.md](MOBILE_IMPLEMENTATION.md) is the current status. The original handoff below is historical.

Recorded 8 October 2026 from Markus's handoff instructions. This is the starting direction for M5 design discussion and M6 implementation in the next chat. The loader and bottom sheet are proposals to iterate on, not approved final designs. No mobile code or paid calls are part of preparing this handoff.

## What Markus wants

A really modern UI, with a simple manual flow for now: **capture → crop/edit → Send → process on the local Mac backend → review extracted data → fake payment → capture again**.

Paper detection and a live outline would be desirable later. Markus has no invoices nearby right now. Keep this as a TODO for the next morning, **9 October 2026**, when real invoices are available; it must not block the manual flow. This is a planning note, not a scheduled reminder or authorization for automatic work at that time.

## Proposed first design

Use a camera-first screen with generous spacing, crisp typography, one prominent capture control and restrained motion. Azikus's near-black, white and ice-blue palette can give it a contemporary appearance: dark camera controls, a clean light review surface, blue used sparingly for emphasis. Avoid dense dashboards, decorative metrics and provider/model details in the customer flow. Choose final light/dark treatment together during M5.

Use the installed `azikus-brand` skill when making actual designs. Its working palette is near-black `#0A0A0A`, white `#FFFFFF`, ice blue `#CFE2F6`, muted blue `#9BB0CB` and slate `#3E4855`. ABC Monument Grotesk is the official font but usable font files are not supplied; Hanken Grotesk is a disclosed fallback with its licence retained if bundled. Typography and motion must remain legible with accessibility settings. These interaction proposals are app choices, not official brand rules.

| State | Proposed interaction | Completion / recovery |
| --- | --- | --- |
| Capture | Camera preview, large capture button; a secondary image-import action is useful for development while invoices are unavailable. | Capture freezes one image. Camera permission denial has a usable explanation and import/settings route. |
| Crop and preview | Adjustable manual crop, zoom/pan as needed, rotate, Retake and a clear Send button. Show what will actually be sent. | No provider request before Send. Cropping happens locally; encode the resulting oriented image as JPEG/PNG. Keep enough detail to read small payment digits. |
| Sending / reading | Keep the captured image visible, with a compact processing panel and subtle shimmer on empty field placeholders. | Use Uploading while submitting, then Reading payment details after acceptance. No invented percentage, pretend field values or artificial delay. Prevent duplicate sends. |
| Review | Present an expandable bottom sheet over the captured image. Show recipient and amount/currency prominently, followed by destination and payment reference; keep the image accessible for comparison. | All displayed payment values are editable. Expand/scroll for keyboard, long names and multiple candidates. Keep missing/uncertain field warnings close to their fields. |
| Demo Pay | A prominent **Demo Pay** action, with an unobtrusive statement that no money will move. | On tap, dismiss the sheet, clear the current draft/crop and re-enable capture. Optional brief haptic/toast: Demo complete — no payment sent. No payment API, bank integration or fabricated receipt. |
| Failure / no usable data | Clear inline or sheet error, with retained image and explicit recovery actions. | Resume/poll an accepted scan without sending again. Offer recrop/retake or a deliberate new attempt; do not silently create another paid call. |

The recommended loader is **shimmer on a few empty field rows**, followed by a smooth reveal of the real result in the same panel. It suggests an incoming draft without implying that a specific field has already been recognized. Keep it subtle; respect Reduce Motion with static placeholders and a simple progress indicator. Accessibility announcements should describe the actual state. Show a useful waiting/recovery message for long requests rather than looping decorative motion indefinitely.

The bottom sheet is the first proposal. Compare it with a full-screen review if the keyboard, long payment identifiers or accessibility text sizes make editing cramped. Begin with recipient, amount/currency, bank destination and payment reference; tuck optional invoice metadata behind expansion. Preserve leading zeros and decimal strings. Do not force provider diagnostics into this screen.

All drafts require user review, even when extraction reports success. Missing fields should look intentionally empty and actionable, not like zero values. Approved cosmetic name variants should not block the user. Discuss the exact Demo Pay enablement and sheet-dismiss behavior during design iteration; the proposed behavior is to ask the user to complete/review necessary payment fields first. Dismissing a sheet is not evidence that a payment happened.

## First iteration boundaries

- Manual capture and crop first; no automatic capture or paper detection prerequisite.
- Crop before upload. Mobile edits never rewrite immutable backend extraction or benchmark evidence.
- Send only the final JPEG/PNG to the existing backend and selected OpenAI profile. No new OCR dependency or provider tournament.
- Once processing or review is active, prevent another capture/send from overlapping the current UI flow. After Demo Pay, resume the camera only when the app is foregrounded and permission allows it.
- Keep result polling tied to the active scan ID. A late response from an old scan must not reopen a dismissed sheet or overwrite the next scan.
- Demo Pay clears the mobile UI state; it does not silently delete backend evidence or cancel a request already sent to a provider.
- Real camera validation is deferred until invoices are available. Clearly label fixture/mock/replay previews; do not present them as live extraction.

## Paper detection TODO — next morning with invoices

- [ ] Confirm that invoices are available before starting physical-document testing.
- [ ] Propose and implement paper-edge detection with a stable live outline; retain manual capture/crop when no page is detected.
- [ ] Test outline stability and framing with actual invoices under glare, shadows, skew and partial page visibility.
- [ ] Verify crop/perspective behavior preserves small printed amounts, references and bank digits; inspect the image that reaches the backend.
- [ ] Decide whether perspective correction or automatic capture adds enough value; neither is required for the first manual iteration.

Paper-edge detection is a capture aid. It does not introduce QR/barcode decoding, which remains outside the PoC.

## Next-chat sequence and acceptance

First propose one coherent visual direction and a small set of screen/state sketches or mockups covering capture, crop, processing, review and reset. Refine the loader, sheet behavior and Demo Pay semantics with Markus before native implementation. Do useful project/toolchain inspection in parallel with the design discussion, but do not interpret this brief as final screen approval.

After design agreement, implement the native iOS flow against the existing API. A physical iPhone connects to a configurable reachable Mac URL, not the phone's localhost. See CHAT4_HANDOFF.md for credentials, profile, API and spending controls. Any new paid scan testing needs a bounded plan against the preserved ledger; mock/offline integration can proceed without inference.

The first slice is complete when a chosen/captured image can be cropped, explicitly sent, processed, reviewed and edited, and Demo Pay dismisses the sheet and allows another capture. Check orientation, small-field legibility, permission failure, missing/ambiguous fields, transport/provider failures, duplicate taps, background/foreground transitions and late polling responses. Measure capture-to-review latency on the device once real tests are possible. Paper detection remains a separate TODO, not a reason to hold up this slice.
