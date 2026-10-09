# Mobile and inspector checkpoint — 9 October 2026

**Latest continuation:** [confirmation sheets](CONFIRMATION_SHEETS.md) records the separately authorized extracted-field review change and updated tests. [ROADMAP.md](ROADMAP.md) owns the newly agreed five milestones; [PRESENTATION_HANDOFF.md](PRESENTATION_HANDOFF.md) and [PRESENTATION_PROMPT.md](PRESENTATION_PROMPT.md) prepare the next chat. No other implementation or deck creation now. The acceptance and verification below retain the preceding mobile/refactor checkpoint.

Markus confirmed that his real-invoice iPhone testing is complete and accepted the current PoC flow. He authorized autonomous review, checks, commit/push, PR creation and merge for this checkpoint, followed by a separate repository-reorganization chat and its checked PR/merge. Status and documentation must be updated in both steps.

## Delivered

- Native iOS capture/import, manual crop/rotate and preview, explicit Send, per-field shimmer, an image-led editable review sheet, hidden null display rows, formatted nullable JSON, confirmation and completion animation/reset. Pay records a simulated confirmation; no payment service is integrated.
- Recovery preserves the image, upload key, exact profile/version, original response, edits and pending confirmation. Reconnect tries saved USB then Wi-Fi URLs using authenticated reads; new pending scans pin the backend's stable identity. Legacy accepted drafts are matched by scan ID and image hash before changing transport addresses.
- Authenticated `/admin` inspector: a compact scan list with Mobile/Automated filtering; next-scan method/model selection; original normalized JSON; saved provider responses grouped by run/stage; hybrid OCR text/layout and LLM input; exact uploaded mobile images; separate confirmed mobile edit snapshots.
- Seven exact tested extraction profiles available under the existing bounded mobile allowance. Current persisted choice at checkpoint: `mistral-small-image-roles-v3@2-b292ba761e512607`. The historical Phase 2 selection remains documented separately; selecting a method does not rerun old scans or silently change pending drafts.

## Verification

The folder reorganization reran 672 backend tests (95.92% statements / 91.15% branches), all 16 native unit/recovery and 2 simulator UI tests, and installed-wheel/source-distribution checks. See [full reorganization verification](REPOSITORY_REORGANIZATION_HANDOFF.md). The checks below retain the original mobile PR #2 checkpoint; no device reinstall was performed for the folder move.

- 672 offline backend/evaluation tests pass. Domain/orchestration coverage is **95.92% statements / 91.20% branches** (3,595/3,748 and 1,317/1,444). Ruff lint/format and strict mypy pass; generated contracts and JavaScript syntax were checked.
- 16 native unit/recovery tests and 2 simulator UI tests pass in the final checkpoint run. Signed device build succeeded and the update is installed on the iPhone 16 Pro. Earlier synthetic hardware/UI checks and browser checks are detailed in [mobile implementation](MOBILE_IMPLEMENTATION.md).
- The latest physical reconnect result was **USB failed → Wi-Fi connected**. Do not describe that check as successful USB connectivity. Saved mobile image bytes match their recorded hashes and provider-output inspection makes no new inference call.
- Markus's real-invoice testing is user-confirmed acceptance. It is not an independent full-corpus accuracy measurement or a measured camera-to-review latency study.
- Private final check logs: `.local/mobile-live-2026-10-09/pr-checks-backend.log` and `pr-checks-ios.log`. Before-review source backup and private-state fingerprints: `.local/mobile-pr-checkpoint-2026-10-09/`.

## Preserved state and limits

Original ledger at checkpoint: **2,201 dispatched reservations / €336.45 held**. Existing mobile cumulative limits remain 2,217 / €338.05, leaving at most 16 calls / €1.60 for separately authorized explicit mobile Sends. Reservations are conservative allowances, not actual billed charges. The checkpoint and reorganization make no paid calls or experiment reruns.

Keep root `.env`, SDK credential stores, `.local/providers.json`, `.local/backend/`, all original budget rows, profile snapshots, source invoices, labels and raw responses private and intact. They must not enter Git, even in the private repository. Keep the existing backend selection and device bundle ID. Existing experiment results are not recomputed for the presentation or refactor.

## Known limits and next order

The phone currently uses saved addresses; there is no automatic Mac discovery. Joining a personal hotspot or changing the Mac's IP may require restarting the backend at its current interfaces and updating the saved URLs. The same-iPhone hotspot setup is not yet verified. Hotspot/discovery improvements are later work, not part of the structural refactor.

The mobile/admin checkpoint merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2). The separate [repository reorganization](REPOSITORY_REORGANIZATION_HANDOFF.md) records the new root layout, checks and PR. Next: **initial presentation together with Markus in a new chat** → iOS improvements and real-invoice testing → backend/admin improvements and integration testing → Android and both-platform testing as the final development milestone → comprehensive final presentation and embeddable website HTML. See the agreed roadmap; do not start later work during the sheet/documentation task.

Paper detection, automatic crop, native OCR experiments, Android, final findings and the attendee companion remain later scope. Payment QR/barcode decoding remains outside the PoC. No public publication, production-readiness claim or actual payment execution is authorized by this checkpoint.
