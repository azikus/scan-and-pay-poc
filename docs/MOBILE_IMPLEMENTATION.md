# Mobile implementation — 9 October 2026

> Historical scope/checkpoint: retain the dated evidence below. Current scope, runtime and acceptance are in [CURRENT_STATUS.md](CURRENT_STATUS.md), [CODING_HANDOFF.md](CODING_HANDOFF.md) and [ROADMAP.md](ROADMAP.md). Android/final presentation are skipped; mobile/backend/SUNMI and successful phone Send are accepted. Old next-task wording, worktree paths, provider selections and financial admission limits are not current instructions.

**Current continuation — 12 October 2026:** the initial presentation is delivered and its source is in [presentation/](../presentation/README.md). [CURRENT_STATUS.md](CURRENT_STATUS.md) owns the latest operational snapshot and authorized allowance. The dated checkpoints below retain their original values and verification evidence; they do not override the current handoff.

## Latest sheet update — 9 October 2026

The review and Pay confirmation sheets now show every non-null extracted selected-payment/invoice field, grouped into Payment details and Invoice details. Untouched inferred/derived values and recipient-role fallbacks stay out of new mobile confirmations; explicit edits remain visible and marked Edited. Original JSON and already-frozen confirmation retries are preserved. See [CONFIRMATION_SHEETS.md](CONFIRMATION_SHEETS.md) for implementation, migration and verification (23 native unit/recovery tests and 2 UI tests). No backend/admin implementation changed.

The approved next task is the initial presentation together in a new chat, using [the comprehensive handoff](PRESENTATION_HANDOFF.md). [ROADMAP.md](ROADMAP.md) records the full agreed order through Android as the final development milestone and the final presentation/embeddable HTML afterward. Older iterations below remain dated history.

## Current checkpoint and next work

Markus confirmed on 9 October that real-invoice iPhone testing is complete. The current iOS/admin slice is accepted for this PoC checkpoint. Device acceptance is no longer pending; hotspot/address-change testing and automatic discovery remain separate open improvements. Current admin selection is Mistral Small, and the original ledger is 2,201 dispatches / €336.45 held. These are current observations, superseding historical selection/budget statements below.

The mobile/admin checkpoint merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2). The native project now lives in `ios/`, admin source in `frontend/admin/`, Python in `backend/`, and `android/` contains only a future-work README. See [reorganization checks and PR](REPOSITORY_REORGANIZATION_HANDOFF.md). Next: presentation together with Markus → mobile and backend improvements → Android last. No paid calls occur during cleanup. See [checkpoint](MOBILE_CHECKPOINT.md) and [coding handoff](CODING_HANDOFF.md).

## Historical implementation and verification notes

The dated records below explain earlier decisions and checks; older statements about pending device acceptance, zero allowance or OpenAI being currently selected are superseded above.

## Admin method choice

Markus chose the admin as the place to select the next scan's method. The always-visible **Next scan** form has a **Method** dropdown (Image → LLM, Image → OCR → rules, Image → OCR → LLM), a **Model / provider** dropdown filtered to usable profiles, and an explicit **Use for next scan** button. The earlier display-only method guide and benchmark table were removed from the admin after Markus found them confusing; saved benchmark evidence remains available for the presentation. Each saved scan shows its own actual stages/model/version and backend duration. The static aggregate catalogue contains no sample contents, raw responses or credentials and is served behind the existing token.

Seven exact tested profiles are enabled under the unchanged bounded mobile allowance: OpenAI mini, Gemini Flash-Lite, Mistral Small, Claude Haiku, Together Qwen, Mistral OCR/rules and Mistral OCR → OpenAI. Other integrations remain visible in the guide. OpenAI stays selected. Selection persists separately in SQLite and does not send an image. The phone reads the selection only for a new explicit Send, saves its exact version with the pending upload, and preserves the original selection during recovery. Older saved OpenAI drafts remain compatible. Interruption during the pre-upload method lookup returns to the unsent preview.

Verification: 665 backend tests pass; 12 iOS unit/recovery tests cover selection changes, stale-version refusal, frozen upload recovery and pre-upload interruption. Signed device build installed. Browser checks exercised selecting Gemini then restoring OpenAI without inference. The original ledger remained 2,199 dispatches / €336.25 after the user's two scans. See the scope amendment in MOBILE_LIVE_TESTING.md; no paid calls were made for implementation or validation.

**Latest continuation:** [Mobile live testing](MOBILE_LIVE_TESTING.md) records the newly authorized 20-call / €2.00 allowance, local connection setup and removal of unnecessary UI labels. The zero-allowance statements below describe the initial implementation checks.

Markus selected the **image-led sheet**, shimmer for every displayable field, omission of null-valued result rows, and **Pay / Complete** wording. The action remains simulated in code. He requested formatted nullable JSON on mobile and a private admin frontend, and confirmed **original JSON + mobile edits**. This agreement supersedes the earlier documentation-only/no-mobile handoff gate for this implementation. No new chat was created.

At the original checkpoint the project was under `apps/ios/`; it now lives at `ios/ScanAndPay.xcodeproj`. Current setup and behavior are documented in [the iOS README](../ios/README.md). M5’s direction is agreed. M6’s first implementation is present; its physical-device acceptance is still open. No real invoice capture or camera-to-review latency is claimed.

## Latest UI iteration — 9 October

**Reconnect** is available on capture, in Connection settings, and in the scan menu. It checks the saved USB address before the saved Wi-Fi address, shows the successful route, persists the addresses, and never initiates an upload or confirmation. A persisted backend UUID added to authenticated `/v1/profiles` lets a pending draft safely change transport addresses without changing its image/options/key/edits/confirmation. Legacy accepted scans require matching scan ID and original-image SHA-256; legacy uncertain uploads cannot move to an unverified address. Drafts remain intact on failures and backend mismatch. Saved addresses are explicit; changing USB IPs are not automatically discovered.

Reconnect verification: 16 native unit/recovery tests and both existing simulator UI tests pass; signed device build succeeds. Tests cover USB priority, Wi-Fi fallback, all-route failure, preserved confirmations, backend mismatch, and same-key recovery after a read-only reconnect. The backend identity persists across process restarts and its read endpoints do not dispatch provider work. The full backend suite passed (671 tests before the new identity case), plus all 15 focused admin/identity tests. Physical-device route verification is recorded in MOBILE_LIVE_TESTING.md.

The inspector also exposes **Provider output** and, for mobile scans only, **Sent image**. Provider output reads the saved response JSON before field mapping; hybrid records offer each OCR/LLM stage separately, including retained OCR text/layout and the exact interpretation input. Original JSON remains the normalized backend result. The image is the original uploaded file, with its recorded hash checked before serving. These authenticated reads do not dispatch extraction. Outputs load on demand, image blobs are released on selection/disconnect, and a stage with no retained response is shown explicitly.

Verification for this addition: 671 offline backend tests pass, 95.06% statement / 90.31% branch coverage, Ruff and strict mypy pass. Tests cover multi-stage/poll ordering, legacy association, missing/corrupt responses, authentication, symlink confinement, deletion, exact original image bytes and mobile-only image access. Saved live mobile outputs and image hashes were checked without provider calls; the ledger remains 2,199 / €336.25.

The inspector now uses one compact list at every width and filters Mobile/Automated at the API before pagination. Mobile submissions carry an explicit source header; source metadata is separate from immutable extraction JSON. The existing phone scan was identified by its pending upload key and image hash and backfilled as mobile. Historical evaluation records remain automated. Original JSON can load independently if the mobile-review endpoint fails.

The mobile JSON viewer uses a width-constrained, selectable `UITextView` with line wrapping. It preserves the full original response and explicit nullable mobile values without horizontal scrolling. A checked, selected, useful draft can now open Pay's confirmation sheet even with unresolved destination details; the summary shows those omissions, amount, recipient and available destination/reference fields. Confirm is the only action that saves. On successful save, a haptic and checkmark/rings/particles sequence appears; reduced motion removes the movement. The original extraction review status remains unchanged.

Verification: 663 offline backend tests pass, with 94.83% statements / 90.17% branches across the measured backend/evaluation scope; Ruff and strict mypy pass. Ten native unit/recovery tests and two simulator UI tests pass. The UI flow exercises both JSON tabs, cancellation, confirmation and completion; a clean runner rebuild resolved a stale old test artifact during screenshot capture. Browser checks confirm both filters, a single list at 402 px, valid original JSON and no page-width overflow. Current phone draft and edits were byte-for-byte preserved through installation. The updated normal app launched on the phone. A further read-only UI check on the actual draft was cancelled because the phone locked before Xcode could start it; that specific hardware check is not claimed. No new inference calls were made by this iteration.

## Delivered behavior

Capture/import → manual crop/rotate → exact final image preview → explicit Send → queued/reading placeholders → editable expandable sheet → review confirmation → simulated Pay → Complete/reset. Camera denial offers import and system Settings. The image is accessible throughout review. Dynamic Type, keyboard expansion and Reduce Motion are accommodated. Null rows are omitted after the response, with missing-field entry available separately. Warnings and linked options remain intact.

The mobile JSON viewer preserves the original response and nulls; edited scalar values form a separate snapshot. No original bank/reference/amount string is silently converted to a number. The app verifies the selected profile version, retains a stable upload key and original PNG bytes for uncertain-upload recovery, polls accepted scan IDs without resubmitting, and ignores old results after reset. Mobile recovery state survives app restart.

The private **`/admin` inspector** is served by the existing FastAPI process. Its shell has no private data; a bearer token is required for all data. Enter the existing backend token from the root `.env` locally; it stays in page memory and is cleared on disconnect. Inspect original GET-scan JSON, nulls, warnings and linked candidates, then switch to mobile confirmations to compare extracted and confirmed values. Polling is read-only. The inspector never initiates extraction or executes payment. It labels synthetic fixture records separately from saved live extraction.

Mobile edits are recorded **when Pay confirms the draft**, not on every keystroke. The API stores these snapshots separately from extraction/benchmark records, with a client-generated idempotent review UUID. A failed save keeps the draft and offers recovery. Repeated saves of the same UUID/body return the same record; a different body with that UUID returns 409. See [API contract](API_CONTRACT.md).

## Verification and boundaries

Backend checks: 662 offline tests; 95.72% domain/orchestration statement coverage and 91.07% branch coverage; Ruff and strict mypy pass. OpenAPI regenerated; the original result schema is unchanged. Local Chrome checks passed for formatted nulls, original/edit separation, leading zeros, responsive layout at 402 px, disconnect clearing and no JavaScript errors. Screenshots and synthetic-only preview data are private under `.local/`.

Native simulator verification and any remaining issues are recorded in the final check section below. Unit/network tests use local fixtures or URLProtocol stubs, not live providers. Markus connected the physical iPhone 16 Pro (iOS 26.6.1), with Developer Mode enabled. The app was signed with the existing Azikus development identity, installed, and the synthetic UI test passed on the device. The normal camera screen was then launched. Real-photo/LAN extraction acceptance remains open; a synthetic on-device flow is not extraction or camera-quality validation.

No paid inference, subscription, evaluation rerun or budget/configuration change occurred. The preserved ledger remains **2,197 dispatches / €336.05 allowance**, under the €500 cap, with **zero additional allowance**. A bounded mobile plan and account-readiness check are required before real provider scans. Paper detection/live outlines, QR decoding, Android and final findings are not included in this slice.

## Continuation

1. The signed app is installed and open on the connected iPhone. Allow camera access locally if prompted.
2. Check camera permission, rotation/crop detail, Photos import, keyboard, large text, Reduce Motion and reset on actual hardware.
3. Arrange a reachable private Mac URL and bounded test allowance before live extraction. Measure actual capture-to-review latency, and retain device/photo provenance separately from prior evaluation.
4. Test real invoices before deciding on paper-edge detection/perspective correction. Keep the current manual flow usable.

## Final checks for this slice

- Xcode 26.3 simulator and signed device builds succeeded.
- Nine native unit/recovery tests plus the full UI-flow test passed on iPhone 16 Pro simulators running iOS 18.6 and 26.2. A second UI regression verifies that a formerly null due-date field can be added without losing keyboard focus. Comma-decimal keyboard input is normalized to the wire decimal string and covered by the unit suite.
- The same UI-flow test passed on the physical iPhone 16 Pro running iOS 26.6.1, with screenshots inspected in its dark appearance.
- The private inspector is running on `http://127.0.0.1:8000/admin` against the original saved backend records. Read-only authentication and unchanged cumulative limits (2,197 / €336.05) were checked without exposing credentials or payment data. Use the existing `SCANPAY_TOKEN` locally to connect. The process binds loopback; physical-phone extraction still needs a deliberate LAN session and bounded allowance.
- Backend wheel packaging includes the inspector assets and font license and excludes test support. No provider call, configuration selection change, commit, push or publication was performed.
- The 24 pre-existing changed/untracked handoff files were backed up byte-for-byte under `.local/m5-start-2026-10-08/`. Current-status updates were added to five of them; all other pre-existing file hashes remain unchanged.
