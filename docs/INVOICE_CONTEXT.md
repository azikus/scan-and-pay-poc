# Invoice context and applicable fields — 13 October 2026

Markus requested implementation in a separate worktree/PR from latest main, including country explanations/flags and admin light/dark appearance. He explicitly authorized fresh paid calls for every available image. Base: `aabad9f7c64e6bcb3247d0a86bd89114c41313b0` (merged PR #9). The earlier no-inference/handoff restrictions do not apply to this bounded request. The stopped 9 October comparison is untouched.

Before PR creation, main advanced to `814a1f176141335b7a7bec7c624e882fb457e6ab` (PR #10, explicit cloud credentials). That change is merged here. Only the three status/instruction documents conflicted; both scopes were retained. The integrated backend was rechecked and loaded with an idle service restart; every profile version is unchanged. Paid results below remain pinned to the original extraction profile and were not rerun for this integration.

## Extraction and review policy

One model request extracts payment data **and** document context. There is no preliminary classification call or second country-specific extraction. `context_policy: "invoice_v1"` adds a versioned instruction/schema section to compact protocol 5/6 profiles with `field_policy: "partial_v1"`. Country context is now standard for current compatible compact LLM methods. The registry adds it before generating each current profile snapshot/version; callers cannot select an old/context variant. The legacy option remains readable only for saved-snapshot compatibility, preserving archived prompts/results. OCR/rules and prebuilt document methods retain their existing country evidence handling. Image and annotation adapters support the extension; fresh paid verification below covers direct OpenAI only.

The model returns separate language and issuer-country readings, a short evidence summary and printed supporting excerpts. These are extractor claims, not verified geography or a reasoning transcript. A language, customer address, missing field or IBAN prefix cannot establish issuer country. Unsupported/contradictory context stays unknown/ambiguous. Malformed context does not discard recoverable payment fields. Extractor text remains untrusted and is rendered as text.

The backend determines field requirements from each extracted payment route and remittance instructions. Issuer country, language and bank-account country are separate. A UK sort-code/account route requires that pair; an IBAN route requires IBAN and treats BIC as optional for this PoC. Other-route fields are not applicable. A printed required reference remains required; an uncertain reference requirement remains unresolved. A printed/unreadable Croatian model stays relevant, but a missing model never invents HR00. An unresolved route remains a review warning. Country labels never override populated bank fields, resolve a destination, or verify ownership.

Authenticated scan reads add `review_guidance` with policy `invoice-fields@1`, context hints, per-candidate JSON-pointer field rules and warnings. This is a deep-copy projection; persisted extraction, original null values, outcome, evidence and confirmations are unchanged. Legacy results receive route guidance with explicit missing-explanation text. The projection does not reclassify historical extraction outcomes or rerun inference.

## Client behavior

- Admin shows issuer country with a flag and claim status, explanation and expandable supporting text, plus document language and each candidate's route/account country. Field requirements and existing warnings remain inspectable. A zero missing-required count does not imply correctness or an executable payment.
- System/Light/Dark appearance applies before CSS, follows system changes when selected, and persists only the appearance preference. Credentials remain memory-only. Country disclosures retain their state during unchanged polling. Method/model selection remains, with one configuration per model instead of separate old/context entries. Admin and SUNMI model labels no longer use an `Invoice context` suffix.
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

The frozen `reviewed-key-r4.json` excludes 146 fields, including 92 pending labels. This is partial development-corpus scoring, not whole-invoice accuracy. Issuer-country labels were subsequently approved by Markus; see the country evaluation below. Latencies exclude mobile capture/upload/review and p95 is descriptive for this small sample.

The historical same-model profile scored 79/102 accepted readable fields on the reviewed subset. This new run scores three fewer. It is **not an extraction-accuracy improvement**: 11 readable values mismatch, 12 are missing and three remain uncertain. No fuzzy matching or country-based field filling is used. Markus subsequently chose country context as the standard. The active OpenAI mini ID is `openai-mini-image-roles-v3` with the tested context version `2-85c414059effa4ad`; the duplicate `openai-mini-image-context-v1` entry was removed from active configuration. The dated scores remain attached to their original profile snapshots.

The Croatian example raised by Markus returns issuer HR and an IBAN candidate; sort code is explicitly `not_applicable`. Across all 37 images, context suggestions were IT 17, GR 8, GB 5, ES 2, SK 2, CY 1, HR 1 and unknown 1. Forty candidates include 31 unresolved routes, four IBAN and five UK domestic; unresolved references/supporting pages are not silently treated as payable bank routes.

## Preservation and runtime

At the initial evaluation checkpoint, the private provider config gained only the new profile and retained the other profile versions. The later standard-context promotion below supersedes that active-configuration snapshot. The managed service was restarted only while idle and now loads this worktree through the existing private launcher. Credentials, original state directory and backend identity are preserved. Do not archive this worktree while that launcher points to it. A future source handoff should repoint the launcher only after checking idle state.

Ledger audit: 2,342 → 2,379 reservations, exactly 37 additions. Every pre-existing ledger row is unchanged, as are persisted selection, backend identity, confirmed client reviews and prior stage reservations. Private config/launcher backups and hashes are retained. Legacy holds are accounting metadata under main's approved removal of financial admission limits; they are not invoices or new enforcement gates. No historical batch was resumed, and no completed input is to be retried automatically.

## Checks

- 767 backend/evaluation tests pass after integrating PR #10 (752 before integration); domain/orchestration coverage 96.08% statements / 91.49% branches. New cases cover one-call context, invalid/ambiguous context, route-versus-country separation, optional/reference requirements, legacy read immutability and unchanged historical profiles across six direct adapters.
- 30 native unit/recovery tests and all four existing synthetic UI tests pass on an isolated iPhone 16 Pro / iOS 26.2 simulator. The first parallel Xcode runner stalled after compilation and was stopped; a serial run completed with zero failures. No physical-phone installation or acceptance claim.
- Admin browser checks cover both appearances, persistence after reload, supporting text, zero console warnings/errors, and 390 px layout with no horizontal overflow. Screenshots use a synthetic invoice fixture, not private invoice data.
- Ruff, mypy, generated schemas, Swift format, JavaScript syntax and package/privacy checks are recorded with the PR. Raw images, label keys, results, screenshots and test artifacts stay private/ignored.

This PR is for review; merge, Android, hosting and presentation changes are outside this task.

## Country/scheme evaluation follow-up — 13 October

Markus requested country-based scoring, then chose **add breakdowns now; prepare country labels for review**. `evaluation.country_scores` adds a saved-response report alongside the frozen benchmark. No inference, default change or runtime restart is needed. Both compared profiles use the same country cohort key; the evaluated model cannot change its own cohort or remove an incorrect printed field from its denominator.

The original field answer key has no issuer-country labels. A separate `country-review@1` key binds to its exact digest and image inventory. On 13 October, Markus explicitly approved all 17 country suggestions in chat; no form export was needed. The new private reviewed key records that confirmation and reviewer attribution, retaining the original pending key and reports. Country guidance matches 13/17 approved entries (76.47%) for the old profile and 17/17 (100%) for the new profile. This is agreement with user-approved suggestions on this development set, not a blind independent benchmark. Invalid countries, altered inventories/hashes, missing attribution and a saved result from the wrong image are rejected.

Payment-scheme breakdowns derive from positive **reviewed printed fields**, not predicted country/language: IBAN, linked UK sort/account pair, or biller identifiers; insufficient/conflicting evidence stays unresolved. Correctly absent other-scheme fields are counted separately as not applicable. Other confirmed absences remain separately visible, including unexpected populated values; none contributes to readable-field accuracy. This is an extraction breakdown, not a payment-readiness metric.

| User-approved country cohort | Input entries | Old accepted/readable | New accepted/readable |
| --- | ---: | ---: | ---: |
| Italy | 4 | 33/44 | 29/44 |
| Greece | 3 | 9/18 | 9/18 |
| Slovakia | 1 | 6/7 | 6/7 |
| United Kingdom | 6 | 31/32 | 32/32 |
| Croatia | 1 | 0/1 | 0/1 |
| Cyprus | 1 | unscored | unscored |
| Spain | 1 | unscored | unscored |

Both profiles use the same user-approved country labels. Suggestions originated from the new context profile and were then approved by Markus. Sparse or zero readable labels do not support country-wide accuracy claims. The frozen 17-entry manifest includes one explicit exact-image duplicate (16 distinct image hashes); reports expose both counts and preserve the original field denominator. The fresh all-image batch processed each distinct byte sequence once and reused its result for duplicate manifest entries.

Scheme breakdowns, old → new: UK domestic 17/18 → 18/18; IBAN 6/7 → 6/7; biller-reference 31/49 → 27/49; unresolved 10/11 → 10/11; document fields 15/17 → 15/17. Both runs correctly omit 51 labelled inapplicable fields. The overall readable result remains 79/102 → 76/102; the country view does not erase the four extra-digit references on one Italian invoice or the wrong Greek amount. Two beneficiary checks gained credit. The Greek cohort's unchanged total hides one gain and one loss.

Private artifacts in the original checkout's `.local/invoice-context-2026-10-13/`:

- `country-review.json`: preserved initial pending key, with image paths, suggestions and evidence summaries.
- `country-reviewed-markus-2026-10-13.json`: all 17 countries approved by Markus in chat, with the confirmation provenance.
- `old-country-report-reviewed.json` / `new-country-report-reviewed.json`: saved-response scores using the same approved country key; country matches 13/17 and 17/17 respectively.
- `country-review.html`: local review form with invoice previews and an explicit reviewed-label JSON download; no network submission, provider calls or automatic persistence. The form's links, pending labels and JavaScript syntax were checked. Automated visual preview was unavailable because the in-app browser blocks `file:` URLs.
- `old-country-report-r2.json` / `new-country-report-r2.json`: comparable country/scheme reports, with unchanged original scores.
- `score-audit.json` / `score-audit-changes.json`: same-image/key/model audit and individual changed-field evidence, retained privately.

To create any later saved-response report, run the CLI from the original data root with this worktree on the Python module path: `python -m evaluation.country_scores --manifest ... --batch ... --key ... --context country-reviewed-markus-2026-10-13.json --output NEW_REPORT.json`. Use the same reviewed context file for both batches and a fresh output filename; prior reports are not overwritten. Original reviewed fields/labels remain immutable.

Verification after this evaluation-only follow-up: **784 backend/evaluation tests pass**, including 17 new cases; **95.98% statement / 91.40% branch coverage**. Ruff and strict mypy pass. Native/admin application code and its previously recorded checks are unchanged. No additional paid calls.

The subsequent country approval changed only private labels, saved-response reports and documentation. Both reports validated the key/image bindings; original readable-field scores and pending artifacts were preserved. No application code changed or provider calls were made during this approval update.

## Standard country context — 13 October

Markus explicitly requested country-aware extraction as the default and clarified: **keep method/model choice; country-aware is standard**. Current compatible vision/annotation options always include context; OCR → LLM inherits its interpreter's context. OCR-only/prebuilt methods do not gain a model call. The serialized legacy context flag remains solely to interpret immutable historical requests; setting it to `none` cannot disable context in a new compatible registry definition.

The private migration enabled context on 20 compatible model options, removed the duplicate OpenAI context entry, and advanced the persisted OpenAI mini selection to `openai-mini-image-roles-v3@2-85c414059effa4ad`. Method/model choices remain available in admin and SUNMI. Fresh paid verification still covers OpenAI only; other models have offline transport/schema checks, not a fresh context benchmark. No model request or historical rerun was made during promotion.

PR #12 merged during this update, and its SUNMI worktree was removed while the launcher still referenced it. Latest main (`7d188e7`) is integrated here, preserving SUNMI and mobile dark mode. The launcher was repaired to use this surviving invoice-context worktree; do not archive it while active. Admin and SUNMI assets and authenticated profile reads pass after the idle restart. Existing jobs, idempotency records, ledger, stage reservations, reviews and backend identity were preserved. The selection/version change was explicit and authorized.

Combined checks: **792 backend/evaluation tests and seven SUNMI frontend tests pass**; domain/orchestration coverage **95.45% statements / 90.55% branches**; Ruff, strict mypy and JavaScript syntax checks pass. Native source comes unchanged from merged main; this follow-up did not reinstall the phone. Private migration/repair records and config backup: `.local/invoice-context-2026-10-13/default-promotion/` in the original checkout.
