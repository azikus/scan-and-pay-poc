# Evaluation and measurements

Evaluation asks three separate questions: did the provider request complete, did the draft contain the required fields, and were the extracted values correct? Report each independently. A structurally valid or reviewable draft is not a verified payment.

## Running a fresh comparison

Use `evaluation/` tooling with a private manifest that covers every agreed JPEG/PNG fixture, source/page/variant grouping and image hash. Freeze exact profile definitions and request options, the complete input roster and repeat count before dispatch. Use fresh stable keys for a new run; preserve failed/completed/stopped jobs and never resume a stopped experiment automatically.

The approved roster is `.local/evaluation/active-inventory.json` (17 images across 17 source pages). Use its inputs, variant selections and explicit source-hash/page or image-hash exclusions when preparing runs or rendering variants. Six pages use their existing QR/2D-barcode-masked copies; never reintroduce their barcode-visible variants from source PDFs or other manifests. Its source mapping distinguishes original page numbers from the trimmed sample PDF; exclusions must use source identity rather than renumbered pages. The roster is an inventory, not a dispatch authorization. Saved manifests and completed plans are immutable and may refer to files outside the approved roster.

Every input/profile/repeat gets a completed, failed or explicit not-run record. Do not silently drop files, substitute providers, narrow to an unannounced subset or hide timeouts. Fresh inference and saved-response replay are different operations; label them separately.

The tracked `evaluation/approved-inventory.json` pins the count and an order-independent SHA-256 fingerprint of the approved image hashes; it contains no invoices, paths or labels. `evaluation.approved.load_inputs(Path.cwd())` loads and validates the private active roster. Extra, missing, duplicate, replaced or modified images fail validation. Freeze those inputs in a fresh manifest with `kind=approved_inventory`, unique input IDs and `status=prepared`, then create a new `evaluation.batch.new_batch` state for each repeat with the selected profile's exact version. Run with `python -m evaluation.batch --manifest <private-manifest> --state <new-private-state> --url <existing-api-url>`. This paid CLI requires the approval lock, checks bytes again immediately before each POST, and refuses to resume/replay a started approved batch. Missing files fail closed; it never discovers replacements. Updating the approved set requires explicit user selection and a reviewed lock change. The guard governs evaluation dispatch, not ordinary mobile capture; arbitrary custom scripts must not bypass it.

All original images, manifests, reviewed keys, raw responses and reports stay in ignored private storage. Synthetic unit/contract tests are separate from provider evaluation and make no live calls.

## Scoring

- Bind labels to source/image identity and the exact result being scored. Leave unreviewed, unreadable or disputed values unscored.
- Compare bank digits, amount, currency and references exactly under the frozen normalization rules. Never fuzzy-match critical payment values.
- Count approved name variants separately from exact matches. Inferred matching values do not automatically earn observed-field credit.
- Report denominators, excluded fields, confirmed absences, critical-field scores and failed input coverage. Never call a field score whole-invoice accuracy.
- Keep issuer country, document language, bank-account country and route applicability separate. User-approved model suggestions are not blind independent labels.

## Benchmark measurements

Each study is bound to its input inventory, profile and frozen labels. Source reports retain exact dates, request identities and accounting. Prompts were developed on the same small corpus; inputs include related pages and a duplicate. Only partially reviewed fields are scored, so the results do not establish production generalization.

### Six direct-image models

Seventeen inputs per model; 102 readable reviewed fields and 63 critical fields per model. Accepted scores include separately recorded approved name variants.

| Model | Readable accepted /102 | Critical accepted /63 | Backend median / p95 | Timeouts /17 |
| --- | ---: | ---: | --- | ---: |
| OpenAI `gpt-4.1-mini-2025-04-14` | 79 | 51 | 4.02 / 9.43 s | 0 |
| Gemini `gemini-3.5-flash-lite` | 80 | 50 | 3.31 / 5.00 s | 0 |
| Together `Qwen/Qwen3.5-9B` | 69 | 47 | 9.41 / 22.67 s | 0 |
| Mistral `mistral-small-2603` | 71 | 43 | 2.99 / 5.78 s | 0 |
| Anthropic `claude-haiku-4-5-20251001` | 65 | 42 | 5.64 / 11.14 s | 0 |
| xAI `grok-4.7` | 16 | 10 | 90.06 / 90.13 s | 14 |

The exact OpenAI profile was `openai-mini-image-roles-v3@2-5094b6dc13ef5718`; the private saved reports retain every prompt/configuration version. Scores cover 13 of the 17 entries, with 146 excluded fields including 92 pending labels, and 98 confirmed-absence checks reported separately. Grok's missing outputs include capacity/timeout failures; they are not all transcription mistakes. One-field differences do not establish statistical superiority. Results apply only to the recorded profile definitions.

The reviewed OCR → OpenAI comparisons used the same frozen key, with both fresh stages included: draft-1 hybrid scored 71/102 readable and 44/63 critical fields at 6.58 / 11.14 s median/p95; roles-3 hybrid scored 64/102 and 37/63 at 6.02 / 8.47 s. These were separate 17-input batches, not additional rows from the six-model run, and do not prove all possible hybrids are inferior.

### Country-aware OpenAI mini

Model `gpt-4.1-mini-2025-04-14`, context definition hash `2-85c414059effa4ad`. Thirty-seven distinct images, one fresh request per image: zero API errors/timeouts, two success and 35 incomplete drafts. On the fixed reviewed 17-entry subset (16 distinct hashes), 76/102 readable fields were accepted: 74 exact and two approved name variants; 48/63 critical fields were accepted. The direct-image study of the same model scored 79/102 readable fields; no accuracy-improvement claim follows.

Country guidance agreed with 17/17 user-approved suggestions, compared with 13/17 for the direct-image study output. This is agreement with user-approved suggestions, not a blind country benchmark. Both runs omitted 51 inapplicable fields correctly.

Backend latency: reviewed subset median 5.39 s / p95 20.75 s; full batch median 6.69 s / p95 25.29 s. Estimated token-based cost was USD 0.0945568 for the batch; settled bill/tax/FX/credits remain unknown.

### Country-context repeatability

Profile `openai-mini-image-roles-v3@2-85c414059effa4ad` used `gpt-4.1-mini-2025-04-14` with country context. All 37 distinct JPEG/PNG image hashes from the prepared PDF pages, image variants and samples were submitted five times: **185 fresh requests**, two concurrent requests, no retries or reused provider responses. Exact-byte aliases share results; the private plan retains every source/page/variant reference.

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

**Repeatability and failure pattern.** Only 32/63 reviewed critical field positions were accepted in all five runs; 22 passed in some runs and nine never passed. Values or observation states varied at 24/63 critical positions, including beneficiary, reference, amount, currency and one sort-code/account-number pair. On one multi-option example, the fifth output retained one candidate instead of the four or five returned in the other repeats, leaving three reviewed options unmatched; that example's readable acceptance fell from 17/21 in repeats 1, 2 and 4 to 4/21 in repeat 5. This accounts for 13 of the 18 accepted-field drop between repeats 4 and 5. Successful transport therefore does not ensure stable option coverage.

Across the full 37-image set, four images had identical payment fingerprints across all five runs. This strict comparison includes linked candidates, selected candidate, observation values/states/origins, unresolved readings and review state; it ignores generated IDs, evidence and explanatory prose. Agreement is not correctness, and differences are not automatically transcription errors. Country guidance agreed with user-approved suggestions in 84/85 benchmark entries (17, 17, 16, 17 and 17 per repeat); these remain correlated agreement checks, not a blind country benchmark.

**Latency and accounting.** Total backend latency over all 185 requests was **5.63 s median / 8.41 s p95**, maximum 15.25 s; provider-stage latency was 5.58 / 8.31 s. The p95 uses nearest rank, and timings exclude mobile capture/upload/review. All 185 external stages had token-based cost estimates totalling **USD 0.4724944**; no stage charge was unestimated. Settled billing, tax, FX and credits remain unknown. Costs count each fresh request once, without double-counting the duplicate entry used in scoring.

These repeats expose substantial field and option variability despite reliable API completion. They do not establish an accuracy improvement over the single-pass studies. Every draft still needs review; no best-of-five or majority-vote result was selected.

### Field-policy repeatability

The field-policy study uses `openai-mini-image-roles-v3@2-5454a65805fbdae9` and the same 37-image inventory as the country-context study: five repeats, 185 fresh requests, two concurrent requests and no retries. Its rules treat empty unsupported optional remittance fields as absent, accept explicit currency words and whole-unit amounts, confine the model field to printed Croatian remittance instructions and distinguish named biller schemes from bank routes.

| Measurement | Country-context study | Field-policy study |
| --- | ---: | ---: |
| Completed API requests | 185/185 | 185/185 |
| Complete / incomplete / no usable data | 7 / 178 / 0 | 34 / 148 / 3 |
| Readable accepted, repeated observations | 374/510 (73.3%) | 378/510 (74.1%) |
| Critical accepted, repeated observations | 240/315 (76.2%) | 244/315 (77.5%) |
| Critical field positions accepted in all five | 32/63 | 31/63 |
| Backend median / p95 | 5.63 / 8.41 s | 5.02 / 7.56 s |
| Estimated USD cost | 0.4724944 | 0.4966892 |

The field-policy readable score comprises 366 exact matches plus 12 approved name variants; critical scoring comprises 237 exact matches plus seven approved name variants. Per-repeat readable acceptance was **70, 85, 71, 71, 81 /102**; critical acceptance was **43, 57, 45, 45, 54 /63**. Correct confirmed absences were 435/490; country agreement with user-approved suggestions remained 84/85. The same 146 excluded fields per repeat remain unscored. These repeated observations include the duplicate entry in the 17-entry reviewed benchmark and do not establish improved generalization or stable extraction.

**UK fixture.** The reviewed UK example has no Croatian-model warning and is complete in all five runs. Its eight reviewed fields score 8, 8, 7, 7 and 7: two runs omit the optional account-holder name, and one supplier-name reading does not match the reviewed name. Completeness is therefore still distinct from exact field correctness.

**Incomplete outcomes.** Among incomplete runs, 99 report an unsupported payment route, 49 a missing required field, 20 multiple candidates requiring a choice, 16 an uncertain reference requirement and 14 inferred currency. Reasons overlap. Two runs still contain invalid remittance-model claims, one a bank-format issue and six an IBAN-checksum failure. These warnings are preserved rather than erased to increase the success count. The study includes no bank/biller resolver, barcode decoding or real payment integration.

All requests completed with zero transport errors/timeouts. Three no-usable-data outcomes occurred on the same information-only PDF page in repeats 2, 4 and 5. Visual inspection found legal/contact text without a payment amount or bank details; this observation does not change reviewed labels or remove those cells. All 185 external stages have cost estimates; settled billing/tax/FX/credits remain unknown. Maximum backend elapsed time was 46.46 s; median/p95 use all 185 measurements and nearest-rank p95, excluding mobile capture/upload/review.

A separate **local interpretation replay** applies the field-policy rules to all 185 country-context study responses without provider calls or changes to source responses. It produces 17 complete and 168 incomplete drafts, compared with seven complete and 178 incomplete under the country-context rules. This isolates deterministic interpretation from provider variability. The aggregate scores and all-five critical consistency do not establish reliable extraction.

### Payment-route audit

The route audit covers the field-policy study's 37-image corpus. It is a qualitative inspection, not an approved field-label set. Filtering saved results to defined subsets gives the following completeness counts; these are offline scope filters, not separate provider runs or accuracy measurements.

| Input scope | Requests | Country-context complete / incomplete / no usable data | Field-policy complete / incomplete / no usable data |
| --- | ---: | --- | --- |
| 36-image subset excluding the information-only page | 180 | 7 / 173 / 0 | 34 / 146 / 0 |
| 32-image subset with municipal pages 1, 5 and 7 | 160 | 7 / 153 / 0 | 33 / 127 / 0 |

The information-only page is outside the reviewed field benchmark, so its exclusion does not affect field-score denominators. These subsets are distinct from the approved 17-image dispatch roster.

Visual inspection of every source page associated with `unsupported_payment_route` found **99 flagged responses across 23 image variants**. Each response is counted once below, even if it contains several candidates. Categories describe the source page, not verified correctness of every extracted identifier.

| Source-page category | Flagged responses | Interpretation |
| --- | ---: | --- |
| PagoPA/CBILL notices and payment summaries | 30 | The evaluated profile does not support these biller routes; notice number, creditor fiscal code, channel and instalment association affect draft completeness. One summary lacks the creditor fiscal code printed on the full notice. |
| RF bill-payment codes, including postal-slip variants | 30 | Printed electronic-payment identifiers are not IBANs. Preserve them as bill-payment destinations; do not invent transfer accounts. |
| Automatic-debit invoices | 15 | A mandate reference describes collection, not a new outgoing bank transfer. Recognize the collection instruction. |
| Automatic collection with issuer-portal instructions | 5 | Customer/bill identifiers do not identify a bank-transfer destination. |
| Municipal collection form | 5 | Issuer/reference/collection barcode are present, without an IBAN; the specific collection integration remains unverified. |
| Partial/information pages | 13 | These are not complete standalone payment instructions. Missing context should be distinguished from an unsupported scheme. |
| Blank page with fabricated provider fields | 1 | This is a grounding failure, not a payment integration gap. |

The blank page produced unrelated supplier claims in all five attempts, with IBAN claims in three; only one of those attempts had the unsupported-route reason. All five were incomplete. Source/result hashes match, so these cannot be treated as real printed payment routes. The blank page is outside the approved input roster. Other information-only pages are identified in the private audit.

The evaluated policy groups unimplemented biller schemes and unresolved destinations under the same review reason. Extraction completeness, route capability and payment execution are separate concepts. Automatic-debit instructions and conditional fallback notices require explicit interpretation. Live payment execution is outside the PoC scope.

The private route audit contains per-image observations, flagged scan IDs and repeat associations. These observations are not approved field labels. The approved dispatch roster contains 17 distinct source pages, with the barcode-masked copy selected for each of the six pages that have paired variants. Source mappings and exclusion rules are recorded in the private active inventory.

### Approved roster: field-policy study

The guarded runner submitted exactly the selected **17 image hashes twice**, using 34 unique fresh keys and scan IDs, with two concurrent requests and no retries. The profile is `openai-mini-image-roles-v3@2-5454a65805fbdae9` (`gpt-4.1-mini-2025-04-14`). All 34 API requests completed; there were **10 complete drafts, 24 incomplete drafts, zero errors and zero timeouts**. Twenty responses had the unsupported-route review reason, ten per pass. Every draft still requires human review.

| Pass | Complete / incomplete | Readable accepted /96 | Critical accepted /60 |
| --- | ---: | ---: | ---: |
| 1 | 4 / 13 | 65 | 42 |
| 2 | 6 / 11 | 79 | 53 |

Readable acceptance totals **144/192 (75.0%)**, comprising 142 exact matches and two approved name variants. Critical acceptance totals **95/120 (79.2%)**, comprising 93 exact matches and two approved variants. Fifteen images have matching frozen label records; two remain unlabelled. Each pass excludes 123 fields, including 74 pending labels. The pending duplicate entry is omitted by canonical source identity, without changing any label. Confirmed absences are correct in 145/180 repeated checks. The 17-image roster and the 102/63-field benchmark have different input scopes; these are not directly comparable whole-corpus accuracy measurements. Four of 17 images have identical payment fingerprints across both passes; agreement does not establish correctness.

Backend total latency across 34 requests was **6.00 s median / 15.11 s p95**, with an 81.99 s maximum; p95 uses nearest rank. The slow request completed without retry. All 34 external stages have estimates totalling **USD 0.1052000**; settled billing, tax, FX and credits remain unknown.

### Approved roster: payment-option revision

The shared extraction definition handles every country in the approved roster, including Italian bill-payment notices, without a separate country choice. This study evaluates per-option printed labels, dates and conditions; exact duplicate-notice evidence merging; and the `payment_option_required` reason for distinct pagoPA notices. It uses `openai-mini-image-roles-v3@2-80e48b9875949eb2` with `gpt-4.1-mini-2025-04-14` on the same approved 17 images and frozen labels as the field-policy study (`2-5454a65805fbdae9`). Two passes use separate storage, with no retries or provider/model substitutions. All **34 requests completed, with zero errors, zero timeouts and zero not-run rows**.

| Measure | Field-policy study | Payment-option revision |
| --- | ---: | ---: |
| Complete drafts (`success`, still requiring review) | 10/34 (29.4%) | 14/34 (41.2%) |
| Incomplete drafts | 24/34 | 20/34 |
| Readable fields accepted | 144/192 (75.0%) | 161/192 (83.9%) |
| Critical readable fields accepted | 95/120 (79.2%) | 112/120 (93.3%) |
| Confirmed absences handled correctly | 145/180 | 173/180 |
| Backend latency median / nearest-rank p95 | 6.00 / 15.11 s | 5.92 / 11.18 s |

Each payment-option pass produced **7 complete / 10 incomplete** drafts. Readable acceptance was **81/96** and **80/96**; critical acceptance was **56/60** in both passes. Aggregate accepted counts comprise 159 readable exact matches plus two approved name variants, and 110 critical exact matches plus two approved variants. Fifteen images have frozen labels; Milan page 7 and A2A page 2 remain unlabelled. Notice/tax/reference/condition/date fields do not have approved labels and are not included in these correctness scores. Two correlated passes provide descriptive evidence, not a statistically established improvement or proof of correct whole invoices.

The difference in complete-draft counts involves the Slovak school invoice, two UK pages and the Croatian invoice. **No Italian example produced a complete draft in these runs.** There were **zero choice-only incomplete runs**: every incomplete extraction also had a route, missing-field, uncertainty or format issue. Exact duplicate merging deliberately did not erase conflicting provider readings.

Manual inspection of the Italian outputs against the retained images found:

- **Milan page 5:** both runs returned two candidates, mislabelling the repeated postal representation as private CBILL. The candidates also differed in recipient/remittance details; one run misused a non-CBILL identifier as its organisation code. These are extraction errors, so the backend retained review warnings rather than silently discarding a candidate.
- **Milan page 7:** both runs retained exactly three instalments with their respective printed amounts and dates. One run left the route unresolved; the other marked pagoPA as inferred despite the printed logo. Its notice choices were recognized, but scheme evidence still required review. This qualitative check is unscored.
- **Milan page 1:** both retained four options and their dates, but the page lacks the creditor identifiers needed for a self-contained bank draft. One run also left its routes unresolved. No identifiers were copied from another page.
- **TIM page 2:** both preserved the full failed-direct-debit condition, including checking the debit status with the bank first. Both nevertheless classified the notice as private CBILL instead of pagoPA, leading to a missing private bill-reference warning. The printed condition and pagoPA logo demonstrate a remaining provider classification problem; the condition is present in both outputs.
- **A2A page 2:** both stayed incomplete with no supported payment route. This page is a bill breakdown; a details QR does not supply payment instructions.

Across the remaining incomplete images, Greek RF and other unsupported routes remain outside this implementation; missing or inferred currency/identifiers are still explicit. Five of 17 payment fingerprints matched between repeats; agreement is not correctness. Fingerprint comparisons include the per-option fields and therefore have a broader scope than those in the field-policy study.

The 34 external stages have **USD 0.1083088 estimated cost**; unknown stage-charge count is zero, while settled billing, taxes, credits and FX remain unknown. Maximum backend latency was 12.08 s, with all 34 timing samples present.

### Approved roster: five-pass repeatability

Five fresh passes on 14 October 2026 use the same shared `openai-mini-image-roles-v3@2-80e48b9875949eb2` definition and `gpt-4.1-mini-2025-04-14` model as the payment-option study. All supported countries and routes use that definition, including Italian notices; no country-specific profile selection is required. The guarded runner validates the approved 17-image roster and exact bytes before dispatch. Each pass has new keys and scan IDs: **85 fresh requests**, at most two concurrent requests, no retries, reused responses or provider substitutions. An isolated API data directory keeps the live service, saved selection, server identity and reviews intact. The earlier 34-request study remains separate.

**Execution and completeness.** All **85/85 requests complete**, with **34 complete drafts (40.0%), 51 incomplete drafts, zero errors, zero timeouts and zero not-run cells**. Complete drafts still require human review; API completion and draft completeness do not establish correct fields.

| Pass | Complete / incomplete | Readable accepted /96 | Critical accepted /60 | Backend median / p95 (17 samples) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 6 / 11 | 78 | 50 | 7.47 / 30.80 s |
| 2 | 8 / 9 | 68 | 44 | 6.74 / 28.92 s |
| 3 | 6 / 11 | 69 | 44 | 5.33 / 27.48 s |
| 4 | 7 / 10 | 80 | 56 | 5.43 / 33.01 s |
| 5 | 7 / 10 | 72 | 48 | 5.60 / 10.19 s |

**Reviewed field correctness.** Readable acceptance is **367/480 (76.5%)**: 363 exact matches plus four approved name variants. Critical acceptance is **242/300 (80.7%)**: 238 exact matches plus four approved variants. Confirmed absences are correct in **431/450** checks, reported separately. The frozen key and canonical image/source bindings match the preceding two-pass study. Fifteen images have matching label records; two remain unlabelled. Each pass excludes 123 fields, including 74 pending labels; notice/tax/reference/condition/date fields without approved labels remain unscored. These denominators are correlated repeated field observations, not independent fields or whole-invoice accuracy.

The earlier two-pass sample scores 161/192 readable fields (83.9%) and 112/120 critical fields (93.3%) under the same definition. The lower five-pass scores expose sample variability; they do not measure a code regression or establish either sample as representative production accuracy.

**Repeatability.** Of 60 reviewed critical field positions, **39 are accepted in all five passes**, 18 in some passes and three in none. Values or observation states vary at 21/60 positions. None of the 17 images has the same payment fingerprint in all five passes; one image has a varying candidate count. The fingerprint preserves linked payment options, selected option, field values/states/origins, unresolved readings, option labels/dates/conditions and review state, while ignoring generated IDs, evidence and explanatory prose. It excludes document-level fields. Differences are not automatically transcription errors, and agreement is not correctness. No best-of-five or majority-vote result is selected.

**Latency and accounting.** Pooled backend latency over all **85 timing samples** is **5.79 s median / 25.95 s p95**, with a **33.01 s maximum**. Provider-stage median/p95 is **5.74 / 25.79 s**. The p95 uses nearest rank over individual request timings, rather than averaging pass percentiles; with 17 samples, each pass's p95 equals its maximum. Backend timings include queue, preprocessing, provider and postprocessing, and exclude mobile capture/upload/review/rendering. Timeout rate is **0/85**. All **85 external stages** have token-based estimates totalling **USD 0.2732056**, with zero unestimated stage charges. Settled billing, tax, FX and credits remain unknown. Each fresh request is counted once.

## Timing and costs

Record total backend elapsed time, queue/provider/local-stage breakdown, sample count, p95 method and timeout rate. Hybrids include all stages. Provider/backend timing excludes capture, upload, user review and rendering; no measured capture-to-review study is claimed. Include failed/timeout observations when explaining latency coverage.

Costs identify exact model/processor/profile/prompt versions, full input coverage, every stage and retry, and known/estimated/unknown charges. Saved OCR reuse must not count its original charge twice. Selected profiles are operational choices, not automatic benchmark winners.

## Limits

Recipient-role mistakes, amount/reference confusion, missing bank fields and variation between repeated runs remain possible. Format/checksum validation cannot verify correctness or account ownership. Functional mobile/display acceptance does not establish accuracy on an independently scored camera dataset or production reliability.

## Private source map

Reports retain exact dates, profile definitions, source hashes, labels, request identities and stage accounting. They contain private real-document evidence and stay ignored.

| Evidence | Private location |
| --- | --- |
| Frozen reviewed key (`reviewed-fields@2`) | `.local/m3-name-review-2026-10-08/reviewed-key-r4.json` |
| Direct-image studies and cost audit | `.local/m3-direct-six-2026-10-08/` |
| Country-context study | `.local/invoice-context-2026-10-13/` |
| Country-context repeatability | `.local/paid-repeat-2026-10-13-fcb4f68f/` |
| Field-policy repeatability, local replay and scope filters | `.local/paid-review-fixes-2026-10-13-27da0194/` |
| Payment-route audit | `.local/paid-review-fixes-2026-10-13-27da0194/route-audit.json` |
| Approved-roster field-policy study | `.local/paid-approved-2026-10-13-4be9019b/` |
| Approved-roster payment-option study | `.local/paid-bill-options-2026-10-14-d35bc0ca/` |
| Approved-roster five-pass repeatability | `.local/paid-five-pass-2026-10-14-17022aef/` |
| Approved source/page/variant mappings and exclusions | `.local/evaluation/active-inventory.json` |
