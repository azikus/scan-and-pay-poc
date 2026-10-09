# Extracted-field review and confirmation sheets — 9 October 2026

Implemented in [PR #4](https://github.com/azikus/scan-and-pay-poc/pull/4). Markus authorized this as a separate checked PR and merge before the initial presentation, then explicitly limited implementation to the confirmation sheets. Scope includes the editable review sheet, Pay confirmation sheet, their value/persistence handling and regression tests. The agreed milestones and comprehensive presentation handoff are documentation only. No other features or presentation artifacts are implemented in this change.

## Behavior

Previously, review showed all non-null observation values, including inferred values with a warning; Pay's confirmation showed amount/recipient and destination/reference only. It omitted other extracted invoice/payment fields.

Now both sheets group fields into **Payment details** and **Invoice details**. Confirmation shows every non-null selected-candidate and document observation: amount/currency and recipient remain prominent, followed by available account holder, bank details, reference/model/purpose, supplier, invoice/customer number, due date, description and explicit document context. Empty rows and empty sections are omitted. Other candidates' fields are never mixed into the selected option.

A new draft is populated only from observations with `state=observed` and `origin=document`, excluding `draft_beneficiary_from_*` role-fallback normalizations. Ordinary normalization of printed values, such as removing sort-code hyphens or normalizing explicit currency, is retained. Inferred, derived, caller-hint, ambiguous, unreadable and unsupported values remain in the original JSON; they do not silently enter the new mobile confirmation. The candidate picker applies the same extraction rule to amount/currency labels.

**Add missing details** permits user input. Added/corrected values are shown with **Edited**, including a deliberate entry matching an originally inferred value. Original observations, evidence, profile choice and benchmark scores remain unchanged. Missing/invalid payment warnings remain; a selected useful incomplete draft can still be confirmed as a simulation. An inference-only/empty draft cannot be confirmed until useful details are entered. The UI relies on recorded provenance; it cannot independently detect every confidently wrong or mislabeled model observation.

## Saved values and compatibility

New mobile review snapshots keep every required JSON pointer and use explicit `null` for hidden untouched inference; they do not omit contract-required paths. The backend and v1 wire schema are unchanged. Every non-null value in a new confirmation is represented on its confirmation sheet, once, including currency-only cases when the amount is missing.

An optional set of edited field IDs is stored in the existing private pending-scan file. Reopening a new draft preserves deliberate entries even if text matches the model's original guess. Older snapshots without edit metadata preserve values that differ from the original as edits and remove untouched inference; an old edit back to exactly the original inferred text cannot be distinguished from an untouched guess. Selecting another candidate keeps the existing reset behavior.

A confirmation already frozen for retry keeps its original UUID/body, including any historical inferred values it contained. Recovery never rewrites a possibly accepted request. The Mobile values JSON tab shows that actual frozen payload during recovery; otherwise it shows the current new confirmation values. Original JSON remains immutable. No existing backend confirmation is migrated.

## Verification

- 23 native unit/recovery tests pass: provenance filtering, role fallbacks, normalized extracted values, exact strings/nulls, all-field display coverage, linked candidates, persistence of explicit edits, legacy drafts and frozen confirmation retries, plus the existing networking/recovery regressions.
- Both simulator UI tests pass on iPhone 16 Pro / iOS 18.6: capture/crop/review, JSON, Pay/cancel/Confirm/reset and missing-field keyboard focus. They additionally verify invoice details, omitted null rows and an edited due date in confirmation.
- Synthetic review, payment, invoice and Edited screenshots were visually inspected. Amount/recipient hierarchy, grouped content, scrolling and pinned actions remain usable.
- All 15 existing backend client-review API tests pass without backend changes. Swift formatting and diff checks are part of the PR closeout.
- Private evidence: `.local/confirmation-sheets-2026-10-09/ios-tests.log`, `ios-tests.xcresult`, `ios-final-unit-tests.log`, `confirmation-api-tests.log` and `screenshots/manifest.json`. Images and tests use synthetic data; no fresh provider call or real-invoice rerun is needed.

The preceding merged-main rebuild at `1c7fcbdd235a9c7ea37d546d861339b0d4484e17` separately passed 672 backend tests and installed its signed app while preserving phone data. That build predates this sheet change. Its launch was blocked by phone lock; do not claim fresh phone extraction or successful USB reconnection from those Mac-side checks. The signed device build for this sheet change also passes; installation evidence is recorded in the closeout below.

## Next chat

Start with [PRESENTATION_HANDOFF.md](PRESENTATION_HANDOFF.md) and [PRESENTATION_PROMPT.md](PRESENTATION_PROMPT.md). The approved order is initial presentation together → iOS improvements/testing → backend/admin improvements/integration → Android and both-platform testing as the last development milestone → comprehensive final presentation and embeddable website HTML. No later milestone starts in this PR.

## Live state preservation

During this task, a new live scan appeared and the persisted selection changed to Gemini Flash-Lite (`gemini-flash-lite-image-roles-v3@2-85773fe34609a2ff`). The current read-only ledger snapshot is **2,202 dispatches / €336.55 held**, with all original 2,201 rows unchanged. Credentials/provider configuration hashes match the preceding main rebuild. Existing caps remain 2,217 / €338.05; no agent inference was performed and the live selection was not reset. Private verification is `preservation.json` alongside the test logs.

## Device closeout

The signed sheet build succeeded and was installed over the existing iPhone app. A before/after comparison verified unchanged preferences and Application Support (no pending scan file was present). Launch was blocked because the phone was locked. Unlock and open the app to inspect the updated sheets; no fresh physical-device extraction or UI acceptance is claimed for this installation. Private evidence: `ios-device-build.log`, `install.json`, `phone-preservation.json` and `launch.json` under the same sheet-check directory.
