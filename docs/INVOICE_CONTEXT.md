# Invoice context and applicable fields — 13 October 2026

Markus requested implementation in a separate worktree/PR from latest main, including country explanations/flags and admin light/dark appearance. He explicitly authorized fresh paid calls for every available image. Base: `aabad9f7c64e6bcb3247d0a86bd89114c41313b0` (merged PR #9). The earlier no-inference/handoff restrictions do not apply to this bounded request. The stopped 9 October comparison is untouched.

Before PR creation, main advanced to `814a1f176141335b7a7bec7c624e882fb457e6ab` (PR #10, explicit cloud credentials). That change is merged here. Only the three status/instruction documents conflicted; both scopes were retained. The integrated backend was rechecked and loaded with an idle service restart; every profile version is unchanged. Paid results below remain pinned to the original extraction profile and were not rerun for this integration.

## Extraction and review policy

One model request extracts payment data **and** document context. There is no preliminary classification call or second country-specific extraction. `context_policy: "invoice_v1"` adds a versioned instruction/schema section to compact protocol 5/6 profiles with `field_policy: "partial_v1"`. This is opt-in; default serialization omits it, preserving historical prompts, profile versions and saved results. Image and annotation adapters support the extension; fresh paid verification below covers direct OpenAI only.

The model returns separate language and issuer-country readings, a short evidence summary and printed supporting excerpts. These are extractor claims, not verified geography or a reasoning transcript. A language, customer address, missing field or IBAN prefix cannot establish issuer country. Unsupported/contradictory context stays unknown/ambiguous. Malformed context does not discard recoverable payment fields. Extractor text remains untrusted and is rendered as text.

The backend determines field requirements from each extracted payment route and remittance instructions. Issuer country, language and bank-account country are separate. A UK sort-code/account route requires that pair; an IBAN route requires IBAN and treats BIC as optional for this PoC. Other-route fields are not applicable. A printed required reference remains required; an uncertain reference requirement remains unresolved. A printed/unreadable Croatian model stays relevant, but a missing model never invents HR00. An unresolved route remains a review warning. Country labels never override populated bank fields, resolve a destination, or verify ownership.

Authenticated scan reads add `review_guidance` with policy `invoice-fields@1`, context hints, per-candidate JSON-pointer field rules and warnings. This is a deep-copy projection; persisted extraction, original null values, outcome, evidence and confirmations are unchanged. Legacy results receive route guidance with explicit missing-explanation text. The projection does not reclassify historical extraction outcomes or rerun inference.

## Client behavior

- Admin shows issuer country with a flag and claim status, explanation and expandable supporting text, plus document language and each candidate's route/account country. Field requirements and existing warnings remain inspectable. A zero missing-required count does not imply correctness or an executable payment.
- System/Light/Dark appearance applies before CSS, follows system changes when selected, and persists only the appearance preference. Credentials remain memory-only. Country disclosures retain their state during unchanged polling. The new profile is labelled `Invoice context` in model selection.
- The mobile review sheet shows required blank fields and labels only those as missing. Optional empty fields are under **Add other details**. Populated, edited and uncertain readings remain visible, with a conservative fallback for older servers/saved drafts. Review and confirmation display issuer/language context; confirmation retains selected-candidate warnings. Existing original JSON, edit persistence, frozen retries, hotspot connection and Liquid Glass behavior remain.

## Fresh paid verification

Private evidence: `.local/invoice-context-2026-10-13/` in the original checkout. `plan.json` records image/source/page/variant mappings, exact endpoint/profile, one-attempt keys and authorization. `state.json` and image-hash result files retain all outcomes. The union of prepared corpus manifests and supplied JPEG/PNG files contains **37 distinct image byte sequences across 48 file paths**. Identical-byte copies share one result; all distinct variants and supporting pages were processed. The current reviewed 17-image masked subset is scored separately through a SHA-verified saved-response projection; no additional inference was used for scoring.

| Item | Result |
| --- | --- |
| Profile | `openai-mini-image-context-v1@2-85c414059effa4ad` |
| Requested model / recipient | `gpt-4.1-mini-2025-04-14` / `api.openai.com` |
| Fresh external requests | 37; one per distinct image, zero retries/fallbacks |
| Processing | 37 completed; zero API errors/timeouts |
| Draft outcomes | 2 success, 35 incomplete; outcomes are not accuracy |
| Total backend latency, 37 images | median 6.69 s, p95 25.29 s |
| Provider latency, 37 images | median 6.61 s, p95 25.25 s |
| Total backend latency, reviewed 17 | median 5.39 s, p95 20.75 s |
| Estimated provider charges | USD 0.0945568 across 37 stages; not a cash bill |
| Readable reviewed fields | 74 exact + 2 accepted name variants = **76/102 (74.51%)** |
| Critical readable fields | 47 exact + 1 accepted name variant = 48/63 (76.19%) |
| Reviewed absences | 85/98 correct; separate from readable accuracy |

The frozen `reviewed-key-r4.json` excludes 146 fields, including 92 pending labels. This is partial development-corpus scoring, not whole-invoice accuracy. Context countries have no separate human-adjudicated accuracy score. Latencies exclude mobile capture/upload/review and p95 is descriptive for this small sample.

The historical same-model profile scored 79/102 accepted readable fields on the reviewed subset. This new run scores three fewer. It is **not an extraction-accuracy improvement**: 11 readable values mismatch, 12 are missing and three remain uncertain. No fuzzy matching or country-based field filling is used. The new profile remains separately selectable; the user's existing selected `openai-mini-image-roles-v3@2-5094b6dc13ef5718` is preserved.

The Croatian example raised by Markus returns issuer HR and an IBAN candidate; sort code is explicitly `not_applicable`. Across all 37 images, context suggestions were IT 17, GR 8, GB 5, ES 2, SK 2, CY 1, HR 1 and unknown 1. Forty candidates include 31 unresolved routes, four IBAN and five UK domestic; unresolved references/supporting pages are not silently treated as payable bank routes.

## Preservation and runtime

The private provider config gained only the new profile; the original 31 profile versions remain unchanged (32 enabled/configured total). The managed service was restarted only while idle and now loads this worktree through the existing private launcher. Credentials, original state directory and backend identity are preserved. Do not archive this worktree while that launcher points to it. A future source handoff should repoint the launcher only after checking idle state.

Ledger audit: 2,342 → 2,379 reservations, exactly 37 additions. Every pre-existing ledger row is unchanged, as are persisted selection, backend identity, confirmed client reviews and prior stage reservations. Private config/launcher backups and hashes are retained. Legacy holds are accounting metadata under main's approved removal of financial admission limits; they are not invoices or new enforcement gates. No historical batch was resumed, and no completed input is to be retried automatically.

## Checks

- 767 backend/evaluation tests pass after integrating PR #10 (752 before integration); domain/orchestration coverage 96.08% statements / 91.49% branches. New cases cover one-call context, invalid/ambiguous context, route-versus-country separation, optional/reference requirements, legacy read immutability and unchanged historical profiles across six direct adapters.
- 30 native unit/recovery tests and all four existing synthetic UI tests pass on an isolated iPhone 16 Pro / iOS 26.2 simulator. The first parallel Xcode runner stalled after compilation and was stopped; a serial run completed with zero failures. No physical-phone installation or acceptance claim.
- Admin browser checks cover both appearances, persistence after reload, supporting text, zero console warnings/errors, and 390 px layout with no horizontal overflow. Screenshots use a synthetic invoice fixture, not private invoice data.
- Ruff, mypy, generated schemas, Swift format, JavaScript syntax and package/privacy checks are recorded with the PR. Raw images, label keys, results, screenshots and test artifacts stay private/ignored.

This PR is for review; merge, Android, hosting and presentation changes are outside this task.
