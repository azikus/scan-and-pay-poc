# Phase 2 closeout — 8 October 2026

Markus asked to wrap up the phase, select the best tested provider or hybrid for correctness and speed, commit/push the work and prepare a fourth-chat handoff. This supplies the requested checkpoint confirmation. Phase 2 (M2–M4) is closed for the current PoC scope with a provisional pipeline, not a production-accuracy claim. Additional handoff details will come from Markus later; do not create the next chat yet.

## Selected pipeline

Use **direct-image OpenAI GPT-4.1 mini**, model `gpt-4.1-mini-2025-04-14`, profile `openai-mini-image-roles-v3`, exact tested version `2-5094b6dc13ef5718`. It makes one image call with compact protocol 5, native structured output, `partial_v1` field recovery and `draft_v4` interpretation / `payment-party-roles@3`. Keep the tested 8,000 output-token cap, one attempt and 90-second provider timeout. No OCR prerequisite, automatic retry, second opinion or automatic fallback.

This is a practical selection from the measured configurations. OpenAI has the highest critical-field score in the latest six-provider comparison and retains the explicit recipient-role mitigation. Gemini is a close alternative with better measured latency; the one-field difference is not evidence of statistical superiority. Cost does not determine this choice.

| Measured configuration | Accepted readable /102 | Critical /63 | Backend median / p95 | Inputs |
| --- | ---: | ---: | --- | ---: |
| Selected OpenAI roles 3, latest repeat | 79 | 51 | 4.02 / 9.43 s | 17 |
| Same OpenAI version, preceding run | 79 | 52 | 4.17 / 7.82 s | 17 |
| Gemini 3.5 Flash-Lite, latest | 80 | 50 | 3.31 / 5.00 s | 17 |
| Best reviewed hybrid: Mistral OCR → OpenAI, draft 1 | 71 | 44 | 6.58 / 11.14 s | 17 |
| Latest hybrid, roles 3 | 64 | 37 | 6.02 / 8.47 s | 17 |

All rows use the same reviewed key r4, including approved name variants. Hybrid results include both fresh stages, but came from earlier batches, not the latest six-provider repeat. The earlier direct roles-2 variant scored 80/102 and 53/63, but still misidentified a represented creditor; retain roles 3's more explicit role policy rather than choosing a historical prompt by its highest single aggregate. Roles 3 is not uniformly better, and the retained repeat shows field-level variation.

Gemini's eight matching values marked inferred remain visible separately under the frozen grader; they are not eight differing readings. No grading policy was changed to justify this selection. Historical managed-document integrations establish coverage and processing behavior, not that every possible hybrid has been tested or that this model wins universally.

## Frozen configuration and spending

The active private `.local/providers.json` now selects only the tested OpenAI option and advertises its ID as `default_extract_profile_id`. Its full profile snapshot matches the paid experiment exactly. Existing API callers still pass the profile ID explicitly in `options.profiles`; the advertised default does not change the request contract.

The prior default is preserved byte-for-byte in `.local/phase2-closeout-2026-10-08/providers-before-selection.json`. The selected snapshot and verification are beside it. All experiment configurations, results, manifests, labels and original ledger entries remain intact. The disabled `providers.selected.example.json` is a portable behavior template; readiness/account configuration changes its version, so it does not impersonate the locally verified hash.

No paid inference occurs during closeout. The selected local configuration intentionally has **no additional call allowance**: cumulative cap 2,197 calls / €336.05, equal to the preserved ledger. The project maximum remains €500. Starting the backend for health/profile/result inspection is safe; new mobile test scans need a separately documented bounded plan against this same ledger before dispatch. Do not reset the database or copy an old plan to bypass the cap.

Latest direct-batch cost evidence: known usage estimates/reported charges total $0.28243888, with 15 Grok failed-attempt charges unknown. The selected OpenAI batch estimate is $0.0387228 for 17 images, about $0.00228/image; this excludes tax/FX/account adjustments and is not a settled invoice. [Cost-report guidance](COST_REPORT_PLAN.md) links the private full reports. Keep xAI reasoning-token accounting as an explicit future fix before another xAI experiment; it does not affect the selected OpenAI pipeline.

## Acceptance and known limits

- M2: ten provider families integrated, fifteen methods with complete historical corpus attempt records and visible failures.
- M3: versioned interpretation, multilingual labels, partial-field recovery and OCR → LLM composition implemented; synthetic regressions, full saved-response replays and fresh comparisons completed.
- M4: reviewed-subset scoring, cost/latency reports and provisional selection completed. Remaining labels and generalization studies are follow-up work, not silently verified fields.
- Latest offline validation: **651 tests passed; 95.57% statement / 90.85% branch coverage** in domain/orchestration/evaluation. Lint, formatting and strict typing pass. Contract regeneration and selection smoke checks are recorded in the private closeout verification.

There are 200 eligible checks per provider (102 readable and 98 confirmed absent) and 146 excluded fields, including 92 pending. Only 13 of 17 images contain scored fields; related pages and a duplicate remain. This development corpus was used for prompting, so these scores are neither held-out accuracy nor whole-invoice success. Fresh camera performance and mobile capture-to-review timing remain unmeasured.

Wrong amounts, payment-reference versus invoice-number confusion, missing bank details, recipient variants and unstable readings remain possible. The selected latest run read the previously discussed amount correctly but still confused a payment reference. No validator guarantees detection of a confidently wrong reading. Unresolved fields use null and review reasons; do not blank every amount in an incomplete result. Every draft requires user review and confirmation, and the PoC executes no payment.

## Next phase

Prepare M5 capture/processing/editable-review/error/retake designs, then implement M6 iOS against the existing Mac backend in the fourth chat after Markus supplies the remaining brief. Use a configurable reachable Mac URL for a physical iPhone, with deliberate development network configuration and backend-only provider credentials. Android follows as M7. Native OCR is optional later; barcode decoding remains outside this PoC. M8 final findings and attendee display remain deferred.

Start with [fourth-chat handoff](CHAT4_HANDOFF.md). Do not launch new model tournaments, paid calls, mobile implementation or a new chat during this closeout.
