# Evaluation and measurements

Evaluation asks three separate questions: did the provider request complete, did the draft contain the required fields, and were the extracted values correct? Report each independently. A structurally valid or reviewable draft is not a verified payment.

## Running a fresh comparison

Use `evaluation/` tooling with a private manifest that covers every agreed JPEG/PNG fixture, source/page/variant grouping and image hash. Freeze exact profile definitions and request options, the complete input roster and repeat count before dispatch. Use fresh stable keys for a new run; preserve failed/completed/stopped jobs and never resume a stopped experiment automatically.

Every input/profile/repeat gets a completed, failed or explicit not-run record. Do not silently drop files, substitute providers, narrow to an unannounced subset or hide timeouts. Fresh inference and saved-response replay are different operations; label them separately. The existing stopped comparison remains stopped.

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

## Timing and costs

Record total backend elapsed time, queue/provider/local-stage breakdown, sample count, p95 method and timeout rate. Hybrids include all stages. Provider/backend timing excludes capture, upload, user review and rendering; no measured capture-to-review study is claimed. Include failed/timeout observations when explaining latency coverage.

Costs identify exact model/processor/profile/prompt versions, full input coverage, every stage and retry, and known/estimated/unknown charges. Saved OCR reuse must not count its original charge twice. Current selected profiles are operational choices, not automatic benchmark winners.

## Limits

Recipient-role mistakes, amount/reference confusion, missing bank fields and variation between repeated runs remain possible. Format/checksum validation cannot verify correctness or account ownership. Physical mobile/display acceptance establishes that the journey works; it is not an independently scored camera dataset or production reliability study.

## Private source map

The frozen reviewed key is `.local/m3-name-review-2026-10-08/reviewed-key-r4.json` (`reviewed-fields@2`). Full direct results, field-level comparisons and cost audit are under `.local/m3-direct-six-2026-10-08/`; country-context/country-reviewed reports are under `.local/invoice-context-2026-10-13/`. These paths contain private real-document evidence and stay ignored. They allow reproduction without copying confidential reports into this guide.
