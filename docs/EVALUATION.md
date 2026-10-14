# Evaluation and measurements

Evaluation asks three separate questions: did the provider request complete, did the draft contain the required fields, and were the extracted values correct? Report each independently. A structurally valid or reviewable draft is not a verified payment.

## Running a fresh comparison

Use `evaluation/` tooling with a private manifest that covers every agreed JPEG/PNG fixture, source/page/variant grouping and image hash. Freeze exact profile definitions and request options, the complete input roster and repeat count before dispatch. Use fresh stable keys for a new run; preserve failed/completed/stopped jobs and never resume a stopped experiment automatically.

The current agreed roster is `.local/evaluation/active-inventory.json` (17 images across 17 source pages). Use its inputs, variant selections and explicit source-hash/page or image-hash exclusions when preparing future runs, including newly rendered variants. Six pages use their existing QR/2D-barcode-masked copies; never reintroduce their barcode-visible variants from source PDFs or historical manifests. Its source-revision mapping distinguishes original page numbers from the trimmed sample PDF; never apply historical page exclusions to renumbered pages. It is an inventory, not a dispatch authorization. Historical manifests and completed plans remain immutable and may refer to retired sample files.

Every input/profile/repeat gets a completed, failed or explicit not-run record. Do not silently drop files, substitute providers, narrow to an unannounced subset or hide timeouts. Fresh inference and saved-response replay are different operations; label them separately. The existing stopped comparison remains stopped.

The tracked `evaluation/approved-inventory.json` pins the count and an order-independent SHA-256 fingerprint of the approved image hashes; it contains no invoices, paths or labels. `evaluation.approved.load_inputs(Path.cwd())` loads and validates the private active roster. Extra, missing, duplicate, replaced or modified images fail validation. Freeze those inputs in a fresh manifest with `kind=approved_inventory`, unique input IDs and `status=prepared`, then create a new `evaluation.batch.new_batch` state for each repeat with the selected profile's exact version. Run with `python -m evaluation.batch --manifest <private-manifest> --state <new-private-state> --url <existing-api-url>`. This paid CLI requires the approval lock, checks bytes again immediately before each POST, and refuses to resume/replay a started approved batch. Missing files fail closed; it never discovers replacements. Updating the approved set requires explicit user selection and a reviewed lock change. The guard governs evaluation dispatch, not ordinary mobile capture; arbitrary custom scripts must not bypass it.

All original images, manifests, reviewed keys, raw responses and reports stay in ignored private storage. Synthetic unit/contract tests are separate from provider evaluation and make no live calls.

## Scoring

- Bind labels to source/image identity and the exact result being scored. Leave unreviewed, unreadable or disputed values unscored.
- Compare bank digits, amount, currency and references exactly under the frozen normalization rules. Never fuzzy-match critical payment values.
- Count approved name variants separately from exact matches. Inferred matching values do not automatically earn observed-field credit.
- Report denominators, excluded fields, confirmed absences, critical-field scores and failed input coverage. Never call a field score whole-invoice accuracy.
- Keep issuer country, document language, bank-account country and route applicability separate. User-approved model suggestions are not blind independent labels.

## Retained development measurements

These are dated benchmark results, not a change log or current provider ranking. Prompts were developed on the same small corpus; inputs include related pages and a duplicate. Only partially reviewed fields are scored, so the results do not establish production generalization.

### Six direct-image models · 8 October 2026

Seventeen inputs per model; 102 readable reviewed fields and 63 critical fields per model. Accepted scores include separately recorded approved name variants.

| Model | Readable accepted /102 | Critical accepted /63 | Backend median / p95 | Timeouts /17 |
| --- | ---: | ---: | --- | ---: |
| OpenAI `gpt-4.1-mini-2025-04-14` | 79 | 51 | 4.02 / 9.43 s | 0 |
| Gemini `gemini-3.5-flash-lite` | 80 | 50 | 3.31 / 5.00 s | 0 |
| Together `Qwen/Qwen3.5-9B` | 69 | 47 | 9.41 / 22.67 s | 0 |
| Mistral `mistral-small-2603` | 71 | 43 | 2.99 / 5.78 s | 0 |
| Anthropic `claude-haiku-4-5-20251001` | 65 | 42 | 5.64 / 11.14 s | 0 |
| xAI `grok-4.7` | 16 | 10 | 90.06 / 90.13 s | 14 |

The exact OpenAI profile was `openai-mini-image-roles-v3@2-5094b6dc13ef5718`; the private saved reports retain every prompt/configuration version. Scores cover 13 of the 17 entries, with 146 excluded fields including 92 pending labels, and 98 confirmed-absence checks reported separately. Grok's missing outputs include capacity/timeout failures; they are not all transcription mistakes. One-field differences do not establish statistical superiority. These versions/requests are distinct from subsequently configured model definitions.

The reviewed OCR → OpenAI comparisons used the same frozen key, with both fresh stages included: draft-1 hybrid scored 71/102 readable and 44/63 critical fields at 6.58 / 11.14 s median/p95; roles-3 hybrid scored 64/102 and 37/63 at 6.02 / 8.47 s. These were separate 17-input batches, not additional rows from the six-model run, and do not prove all possible hybrids are inferior.

### Country-aware OpenAI mini · 13 October 2026

Model `gpt-4.1-mini-2025-04-14`, context definition hash `2-85c414059effa4ad`. Thirty-seven distinct images, one fresh request per image: zero API errors/timeouts, two success and 35 incomplete drafts. On the fixed reviewed 17-entry subset (16 distinct hashes), 76/102 readable fields were accepted: 74 exact and two approved name variants; 48/63 critical fields were accepted. The retained same-model baseline scored 79/102 readable fields; no accuracy-improvement claim follows.

Country guidance agreed with 17/17 user-approved suggestions, compared with 13/17 for the previous saved output. This is agreement with user-approved suggestions, not a blind country benchmark. Both runs omitted 51 inapplicable fields correctly.

Backend latency: reviewed subset median 5.39 s / p95 20.75 s; full batch median 6.69 s / p95 25.29 s. Estimated token-based cost was USD 0.0945568 for the batch; settled bill/tax/FX/credits remain unknown.

### Five-repeat current-setup evaluation · 13 October 2026

The unchanged selected profile `openai-mini-image-roles-v3@2-85c414059effa4ad` used `gpt-4.1-mini-2025-04-14` with country context. All 37 distinct JPEG/PNG image hashes from the retained prepared PDF pages, image variants and current samples were submitted five times: **185 fresh requests**, two concurrent requests, no retries or reused provider responses. Exact-byte aliases share results; the private plan retains every source/page/variant reference. The existing backend stayed running and the saved selection, server identity and mobile reviews were unchanged.

**Execution and completeness.** All 185 requests completed, with zero provider errors, timeouts or not-run cells. Seven drafts had `outcome=success`; 178 were incomplete with recoverable fields. These labels describe completeness under the profile's review rules, not field correctness or payment validity.

**Reviewed field correctness.** Each repeat was scored against the same frozen 17-entry benchmark (16 distinct image hashes), with 102 readable fields and 63 critical fields. Accepted name variants remain separate from exact matches.

| Repeat | Readable exact /102 | Approved name variants | Readable accepted /102 | Critical accepted /63 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 75 | 2 | 77 | 50 |
| 2 | 76 | 1 | 77 | 51 |
| 3 | 74 | 2 | 76 | 49 |
| 4 | 79 | 2 | 81 | 53 |
| 5 | 61 | 2 | 63 | 37 |

Across repeated observations, readable acceptance was **374/510 (73.3%)**, comprising 365 exact matches and nine approved name variants. Critical acceptance was **240/315 (76.2%)**, comprising 236 exact matches and four approved name variants. These are repeated field observations on the same small corpus, not 510 independent fields or whole-invoice accuracy. Each repeat excluded 146 unscored fields, including 92 pending labels. Confirmed absences were correct in 419/490 repeated checks, reported separately.

**Repeatability and failure pattern.** Only 32/63 reviewed critical field positions were accepted in all five runs; 22 passed in some runs and nine never passed. Values or observation states varied at 24/63 critical positions, including beneficiary, reference, amount, currency and one sort-code/account-number pair. On one multi-option example, the fifth output retained one candidate instead of the four or five returned earlier, leaving three reviewed options unmatched; that example's readable acceptance fell from 17/21 in repeats 1, 2 and 4 to 4/21 in repeat 5. This accounts for 13 of the 18 accepted-field drop between repeats 4 and 5. Successful transport therefore does not ensure stable option coverage.

Across the full 37-image set, four images had identical payment fingerprints across all five runs. This strict comparison includes linked candidates, selected candidate, observation values/states/origins, unresolved readings and review state; it ignores generated IDs, evidence and explanatory prose. Agreement is not correctness, and differences are not automatically transcription errors. Country guidance agreed with user-approved suggestions in 84/85 benchmark entries (17, 17, 16, 17 and 17 per repeat); these remain correlated agreement checks, not a blind country benchmark.

**Latency and accounting.** Total backend latency over all 185 requests was **5.63 s median / 8.41 s p95**, maximum 15.25 s; provider-stage latency was 5.58 / 8.31 s. The p95 uses nearest rank, and timings exclude mobile capture/upload/review. All 185 external stages had token-based cost estimates totalling **USD 0.4724944**; no stage charge was unestimated. Settled billing, tax, FX and credits remain unknown. Costs count each fresh request once, without double-counting the historical duplicate used in scoring.

These repeats expose substantial field and option variability despite reliable API completion. They do not establish an accuracy improvement over the earlier single-pass results. Every draft still needs review; no best-of-five or majority-vote result was selected.

### Corrected field logic, five-repeat rerun · 13 October 2026

The same model and complete 37-image inventory were rerun five times under `openai-mini-image-roles-v3@2-5454a65805fbdae9`: 185 fresh requests, two concurrent requests, no retries. `review@3` and `invoice-fields@2` no longer demand empty unsupported optional remittance fields; normalization revision 2 accepts explicit currency words and whole-unit amounts without guessing digits or ambiguous separators. The `invoice-context@2` prompt confines the model field to printed Croatian remittance instructions and separates named biller schemes from bank routes. Original requests, outputs, labels and accounting remain unchanged.

| Measurement | Before | Corrected rerun |
| --- | ---: | ---: |
| Completed API requests | 185/185 | 185/185 |
| Complete / incomplete / no usable data | 7 / 178 / 0 | 34 / 148 / 3 |
| Readable accepted, repeated observations | 374/510 (73.3%) | 378/510 (74.1%) |
| Critical accepted, repeated observations | 240/315 (76.2%) | 244/315 (77.5%) |
| Critical field positions accepted in all five | 32/63 | 31/63 |
| Backend median / p95 | 5.63 / 8.41 s | 5.02 / 7.56 s |
| Estimated USD cost | 0.4724944 | 0.4966892 |

The corrected readable score comprises 366 exact matches plus 12 approved name variants; critical scoring comprises 237 exact matches plus seven approved name variants. Per-repeat readable acceptance was **70, 85, 71, 71, 81 /102**; critical acceptance was **43, 57, 45, 45, 54 /63**. Correct confirmed absences were 435/490; country agreement with user-approved suggestions remained 84/85. The same 146 excluded fields per repeat remain unscored. These repeated observations include the historical duplicate in the 17-entry reviewed benchmark and do not establish improved generalization or stable extraction.

**Concrete regression check.** The reviewed UK example discussed with the user no longer has a Croatian-model warning and is complete in all five new runs. Its eight reviewed fields score 8, 8, 7, 7 and 7: two runs omit the optional account-holder name, and one supplier-name reading does not match the reviewed name. Completeness is therefore still distinct from exact field correctness.

**Why 148 remain incomplete.** Among incomplete runs, 99 report an unsupported payment route, 49 a missing required field, 20 multiple candidates requiring a choice, 16 an uncertain reference requirement and 14 inferred currency. Reasons overlap. Two runs still contain invalid remittance-model claims, one a bank-format issue and six an IBAN-checksum failure. These warnings are preserved rather than erased to increase the success count. No bank/biller resolver, barcode decoding or real payment integration was added.

All requests completed with zero transport errors/timeouts. Three no-usable-data outcomes occurred on the same information-only PDF page in repeats 2, 4 and 5. Visual inspection found legal/contact text without a payment amount or bank details; this observation does not change reviewed labels or remove those cells. All 185 external stages have cost estimates; settled billing/tax/FX/credits remain unknown. Maximum backend elapsed time was 46.46 s; median/p95 use all 185 measurements and nearest-rank p95, excluding mobile capture/upload/review.

A separate **local interpretation replay** applied the corrected parser/review logic to all 185 original provider responses, without new calls, altered originals or revised prompting. It changed ten incomplete outcomes to complete, leaving 17 complete and 168 incomplete. This isolates deterministic backend effects from changes in fresh model output. The fresh rerun's small aggregate score increase and worse all-five critical consistency do not support a claim that extraction is now reliable.

Offline verification: 831 synthetic tests passed, with 96.21% domain/orchestration statement coverage and 91.35% branch coverage; lint, formatting, typing and generated contracts passed. The fixed runtime was loaded once while idle, preserving server identity, all prior jobs/accounting/reviews and credentials. The selected model stayed the same and its profile version was explicitly advanced.

### Invoice inventory correction and payment-route audit · 13 October 2026

The user excluded the information-only page responsible for all three no-usable-data outcomes. The active inventory now contains **36 images**; the source page and its derived variants are excluded from future invoice evaluations. Originals, historical results and charges remain preserved. Filtering the existing five-repeat results to this roster gives **34 complete / 146 incomplete / 0 no usable data out of 180**, compared with **7 / 173 / 0** before the logic changes. This is an offline scope correction, not a new run or accuracy improvement. The excluded page was outside the reviewed field benchmark, so its scores and denominators are unchanged.

Visual inspection of every source page associated with `unsupported_payment_route` found **99 flagged responses across 23 image variants**. Each response is counted once below, even if it contains several candidates. Categories describe the source page, not verified correctness of every extracted identifier.

| Source-page category | Flagged responses | Interpretation |
| --- | ---: | --- |
| PagoPA/CBILL notices and payment summaries | 30 | Named biller-route support is missing; notice number, creditor fiscal code, channel and instalment association need explicit handling. One summary lacks the creditor fiscal code printed on the full notice. |
| RF bill-payment codes, including postal-slip variants | 30 | Printed electronic-payment identifiers are not IBANs. Preserve them as bill-payment destinations; do not invent transfer accounts. |
| Automatic-debit invoices | 15 | A mandate reference describes collection, not a new outgoing bank transfer. Recognize the collection instruction. |
| Automatic collection with issuer-portal instructions | 5 | Customer/bill identifiers do not identify a bank-transfer destination. |
| Municipal collection form | 5 | Issuer/reference/collection barcode are present, without an IBAN; the specific collection integration remains unverified. |
| Partial/information pages | 13 | These are not complete standalone payment instructions. Missing context should be distinguished from an unsupported scheme. |
| Blank page with fabricated provider fields | 1 | This is a grounding failure, not a payment integration gap. |

The blank page produced unrelated supplier claims in all five attempts, with IBAN claims in three; only one of those attempts had the unsupported-route reason. All five were incomplete. Source/result hashes match, so these cannot be treated as real printed payment routes. It was initially retained pending a scope decision, then removed by the user's page selection below. Additional information-only pages in other documents are identified in the private audit rather than silently excluded.

The current review policy conflates biller schemes that lack implementation with unresolved destinations. A future change should separate extraction completeness, route capability and execution status, recognize existing automatic-debit instructions, and preserve conditional fallback notices. Supporting a reviewed PagoPA or RF draft does not require executing a payment. Live execution remains outside the accepted PoC scope.

The per-image audit, all flagged scan IDs/repeats and source-page observations are in `.local/paid-review-fixes-2026-10-13-27da0194/route-audit.json`. These observations have not been promoted to approved field labels. No provider requests, application changes or runtime restarts were made for this audit.

**Final user-selected pages, same date.** The municipal sample now retains only original pages **1, 5 and 7**, in that order. Original pages 2, 3, 4, 6 and 8 were removed from the sample PDF and their standalone evaluation images deleted. The three-page PDF now numbers the retained pages 1–3; existing retained image filenames preserve original numbering. The active inventory contains **32 distinct images**, including the retained barcode-masked variant. Filtering existing results to this final roster gives **33 complete / 127 incomplete / 0 no usable data out of 160**, versus **7 / 153 / 0** before the logic changes. Historical jobs, outputs and charges remain unchanged; this is a scope filter, not a new paid run. The private `.local/evaluation/milan-page-selection-2026-10-13.json` audit records old/new source hashes, page mapping and deleted paths. Fresh runs must use the active roster rather than retired historical manifests.

**Further user-selected pages, same date.** The active samples now retain only original page 2 of A2A Energia, original page 2 of TIM, and original pages 1 and 4 of Fysiko Aerio. The source PDFs were trimmed and nine excluded image variants removed, including the masked copy of A2A page 1. There are now **23 image variants across 17 source pages**. Six retained pages have both an original and a QR/2D-barcode-masked copy: municipal page 5, TIM page 2, Protergia, Fysiko Aerio pages 1 and 4, and the `QR code.pdf` sample. These are paired variants, not independent documents. They remain included pending a decision about variant coverage. The private `.local/evaluation/selected-pages-review-2026-10-13.json` records the numbered roster, duplicate pairs, deleted paths and source revisions. All retained PDF pages rendered pixel-identically to the previous evaluation images. No provider calls or runtime changes were made.

**Final variant selection, same date.** The user selected the existing barcode-masked copy wherever both variants existed. The six barcode-visible evaluation images were deleted and removed from the roster, leaving **17 images for 17 distinct source pages**. Barcode-visible images without a masked duplicate remain included. Retained image hashes are unchanged, and the inventory records replacement rules to prevent reintroducing excluded variants. Historical provider jobs, results and charges remain intact. The private `.local/evaluation/barcode-deduplication-2026-10-13.json` records the removed paths and current numbered roster. No new provider calls were made.

## Timing and costs

### Approved 17-image roster, two fresh passes · 13 October 2026

The guarded runner submitted exactly the selected **17 image hashes twice**, using 34 unique fresh keys and scan IDs, with two concurrent requests and no retries. The existing backend and selected `openai-mini-image-roles-v3@2-5454a65805fbdae9` profile (`gpt-4.1-mini-2025-04-14`) stayed unchanged. All 34 API requests completed; there were **10 complete drafts, 24 incomplete drafts, zero errors and zero timeouts**. Twenty responses had the unsupported-route review reason, ten per pass. Every draft still requires human review.

| Pass | Complete / incomplete | Readable accepted /96 | Critical accepted /60 |
| --- | ---: | ---: | ---: |
| 1 | 4 / 13 | 65 | 42 |
| 2 | 6 / 11 | 79 | 53 |

Readable acceptance totals **144/192 (75.0%)**, comprising 142 exact matches and two approved name variants. Critical acceptance totals **95/120 (79.2%)**, comprising 93 exact matches and two approved variants. Fifteen images have matching frozen label records; two remain unlabelled. Each pass excludes 123 fields, including 74 pending labels. The historical pending duplicate is omitted by canonical source identity, without changing any label. Confirmed absences are correct in 145/180 repeated checks. Denominators differ from the earlier 102/63 benchmark because the user changed the roster; these are not directly comparable whole-corpus accuracy measurements. Four of 17 images have identical payment fingerprints across both passes; agreement does not establish correctness.

Backend total latency across 34 requests was **6.00 s median / 15.11 s p95**, with an 81.99 s maximum; p95 uses nearest rank. The slow request completed without retry. All 34 external stages have estimates totalling **USD 0.1052000**; settled billing, tax, FX and credits remain unknown. Selection, server identity, reviews, provider configuration and retained image hashes were preserved. No backend restart or application deployment occurred.

Private plan, immutable results, per-pass reports, exact label bindings and stage accounting are under `.local/paid-approved-2026-10-13-4be9019b/`. The approval guard passed synthetic failure cases for roster changes, missing files, changed bytes, unsafe paths and attempted reruns. Full offline verification passed **847 tests**, **96.16% statement / 91.42% branch coverage**, lint, formatting and typing.

### Measurement conventions

Record total backend elapsed time, queue/provider/local-stage breakdown, sample count, p95 method and timeout rate. Hybrids include all stages. Provider/backend timing excludes capture, upload, user review and rendering; no measured capture-to-review study is claimed. Include failed/timeout observations when explaining latency coverage.

Costs identify exact model/processor/profile/prompt versions, full input coverage, every stage and retry, and known/estimated/unknown charges. Saved OCR reuse must not count its original charge twice. Current selected profiles are operational choices, not automatic benchmark winners.

## Limits

Recipient-role mistakes, amount/reference confusion, missing bank fields and variation between repeated runs remain possible. Format/checksum validation cannot verify correctness or account ownership. Physical mobile/display acceptance establishes that the journey works; it is not an independently scored camera dataset or production reliability study.

## Private source map

The frozen reviewed key is `.local/m3-name-review-2026-10-08/reviewed-key-r4.json` (`reviewed-fields@2`). Full direct results, field-level comparisons and cost audit are under `.local/m3-direct-six-2026-10-08/`; country-context/country-reviewed reports are under `.local/invoice-context-2026-10-13/`. The five-repeat plan, 185 saved results, stage accounting, per-repeat scoring and repeatability reports are under `.local/paid-repeat-2026-10-13-fcb4f68f/`. The corrected rerun, baseline local replay, before/after comparisons and runtime preservation audit are under `.local/paid-review-fixes-2026-10-13-27da0194/`. These paths contain private real-document evidence and stay ignored. They allow reproduction without copying confidential reports into this guide.


### Italian bill-payment draft support — offline validation, 2026-10-13

The new `invoice-context@3` / `review@4` implementation supports complete pagoPA and CBILL drafts using their printed identifiers. A pagoPA notice with a printed CBILL organisation code remains one candidate and exposes both channels in mobile review/confirmation and admin. Distinct notices and instalments keep their own identifiers and still require a choice. Missing, ambiguous, inferred or invalid identifiers remain incomplete; no IBAN, Croatian model, provider verification or payment execution is invented. Original saved results and the paid measurements above are unchanged.

Offline validation passed 879 backend/evaluation tests, including 32 new biller regression cases, with domain/orchestration coverage of 96.24% statements and 91.63% branches. The admin channel rendering has two passing synthetic tests. The iOS suite passed 41 tests; after a final label adjustment, the 16 affected review/recovery tests passed again (a stalled simulator launch was restarted before that final run). This is implementation validation, not evidence of improved provider extraction accuracy; the new notice/tax/bill-reference fields need reviewed labels before field correctness can be scored. No new paid calls were made and the running backend was not restarted.

### Italian payment options — fresh paid comparison, 2026-10-14

Implemented `invoice-context@4`, `review@5` and `invoice-fields@4`: one bank CBILL/pagoPA service description, per-option printed labels/dates/conditions, exact duplicate-notice evidence merging, and a distinct `payment_option_required` reason for different pagoPA notices. A creditor can be identified by its printed tax code or CBILL organisation code; populated uncertain/invalid fields still require review. Instalment amounts remain linked to their own notices. Confirmation remains simulated and printed amounts are not live verified debts. This supersedes the earlier “two channels” UI wording above; dated historical evidence is retained.

Two fresh passes used exactly the same approved 17 images and frozen reviewed labels as the 2026-10-13 approved-inventory baseline, with no retries, provider/model substitutions or live-backend restart. The provider/model remained `openai-mini-image-roles-v3` / `gpt-4.1-mini-2025-04-14`; the new profile revision was `2-80e48b9875949eb2` (baseline `2-5454a65805fbdae9`). An isolated temporary backend used separate storage. All **34 requests completed, with zero errors, zero timeouts and zero not-run rows**.

| Measure | Previous two passes | New two passes |
| --- | ---: | ---: |
| Complete drafts (`success`, still requiring review) | 10/34 (29.4%) | 14/34 (41.2%) |
| Incomplete drafts | 24/34 | 20/34 |
| Readable fields accepted | 144/192 (75.0%) | 161/192 (83.9%) |
| Critical readable fields accepted | 95/120 (79.2%) | 112/120 (93.3%) |
| Confirmed absences handled correctly | 145/180 | 173/180 |
| Backend latency median / nearest-rank p95 | 6.00 / 15.11 s | 5.92 / 11.18 s |

Each new pass produced **7 complete / 10 incomplete** drafts. Readable acceptance was **81/96** and **80/96**; critical acceptance was **56/60** in both passes. Aggregate accepted counts comprise 159 readable exact matches plus two approved name variants, and 110 critical exact matches plus two approved variants. Fifteen images have frozen labels; Milan page 7 and A2A page 2 remain unlabelled. New notice/tax/reference/condition/date fields have not been assigned new approved labels and are not included in these correctness scores. Two correlated passes provide descriptive evidence, not a statistically established improvement or proof of correct whole invoices.

The additional complete drafts came from the Slovak school invoice, two UK pages and the Croatian invoice. **No Italian example became a complete draft in these runs.** There were **zero choice-only incomplete runs**: every incomplete extraction also had a route, missing-field, uncertainty or format issue. Exact duplicate merging deliberately did not erase conflicting provider readings.

Manual inspection of the Italian outputs against the retained images found:

- **Milan page 5:** both runs still returned two candidates, mislabelling the repeated postal representation as private CBILL. The candidates also differed in recipient/remittance details; one run misused a non-CBILL identifier as its organisation code. These are extraction errors, so the backend retained review warnings rather than silently discarding a candidate.
- **Milan page 7:** both runs retained exactly three instalments with their respective printed amounts and dates. One run left the route unresolved; the other marked pagoPA as inferred despite the printed logo. Its notice choices were recognized, but scheme evidence still required review. This qualitative check is not a newly approved score.
- **Milan page 1:** both retained four options and their dates, but the page lacks the creditor identifiers needed for a self-contained bank draft. One run also left its routes unresolved. No identifiers were copied from another page.
- **TIM page 2:** both preserved the full failed-direct-debit condition, including checking the debit status with the bank first. Both nevertheless classified the notice as private CBILL instead of pagoPA, leading to a missing private bill-reference warning. The printed condition and pagoPA logo demonstrate a remaining provider classification problem; the condition is no longer lost.
- **A2A page 2:** both stayed incomplete with no supported payment route. This page is a bill breakdown; a details QR does not supply payment instructions.

Across the remaining incomplete images, Greek RF and other unsupported routes remain outside this implementation; missing or inferred currency/identifiers are still explicit. Five of 17 payment fingerprints matched between repeats; agreement is not correctness. New fields also make fingerprint comparisons broader than the historical ones.

The 34 external stages have **USD 0.1083088 estimated cost**; unknown stage-charge count is zero, while settled billing, taxes, credits and FX remain unknown. Maximum backend latency was 12.08 s, with all 34 timing samples present. The model/provider configuration, live server identity, phone selection, saved reviews and image roster were preserved. The temporary service was shut down after evaluation; the live phone backend still runs its existing source.

Offline validation passed **886 backend/evaluation tests, 42 iOS tests and two admin tests**, with **96.28% statement / 91.62% branch coverage**, lint, formatting, typing and generated-contract checks. Private plan, source snapshot, original results, label bindings, per-image comparison and stage accounting are under `.local/paid-bill-options-2026-10-14-d35bc0ca/`. Neither saved baseline results nor reviewed labels were rewritten. The next extraction issue to address is reliable pagoPA scheme recognition and repeated postal-section association, not relaxing completeness checks or guessing missing identifiers.
