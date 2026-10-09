# M3 fresh comparison and reviewed scoring — 8 October 2026

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

This is the preserved baseline report. Subsequent prompt corrections and full comparisons are documented in [recipient-role results](M3_RECIPIENT_ROLES.md); the tables below retain the original measurements.

The fresh masked-image evaluation and step 5's import/scoring work are complete for the usable human-reviewed subset. All 17 images were processed by all three methods, with 51 saved results and 68 external calls. No retry, replacement provider or OCR sharing was used. Full verification of every label remains incomplete: pending/disputed fields are explicitly unscored. No pipeline has been selected, no default changed and no PR created or merged.

## Results

| Method | Matched readable fields /102 | Matched critical payment fields /63 | Complete / incomplete / error (17 images) | Backend total median | Backend total p95 |
| --- | ---: | ---: | --- | ---: | ---: |
| Mistral OCR 4.1 + rules 3 | 25 (24.5%) | 16 (25.4%) | 0 / 11 / 6 | 3.48 s | 7.05 s |
| GPT-4.1 mini direct image | 68 (66.7%) | 41 (65.1%) | 0 / 17 / 0 | 4.97 s | 12.15 s |
| Mistral OCR 4.1 → GPT-4.1 mini text | 70 (68.6%) | 44 (69.8%) | 7 / 10 / 0 | 6.58 s | 11.14 s |

These are normalized field matches on a partial answer key, **not whole-invoice accuracy**. Name mismatches can include valid abbreviations, legal names or aliases that still need adjudication. Critical fields are recipient, amount, currency, bank destination, model and payment reference; supplier headers and dates do not inflate that denominator. Each linked option counts separately. The hybrid's two additional readable matches do not establish superiority: it also gives more differing values, while direct image leaves more uncertainty explicit.

There are 17 timing observations per method, including every measured stage and local work; zero timeouts. Hybrid total includes independent recognition and interpretation calls. Capture/upload/rendering on a mobile app is not measured. This is one small heterogeneous round, including an explicitly retained duplicate and related invoice pages, not a repeatability study or representative latency guarantee.

| Method | Differing readable values | Missing | Uncertain | No usable extraction | Confirmed absences preserved /98 | Unexpected values in confirmed-absent fields |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OCR + rules | 1 | 49 | 1 | 26 | 46 | 0 |
| Direct image | 9 | 12 | 13 | 0 | 81 | 17 |
| OCR → LLM | 17 | 12 | 3 | 0 | 85 | 13 |

The rules method has another 28 absence checks with no matched option and 24 affected by empty/error extraction; neither earns true-negative credit. Its six errors are zero-field product outcomes despite successful OCR execution, not transport failures. A returned response, a valid schema and a complete draft are different measurements.

## What the review and failures establish

- Both LLM methods select the billed customer (or, in one direct-image case, the bank name) instead of the recipient on six reviewed images each. The wrong recipient is already present in the LLM field, without a backend beneficiary-fallback normalization. This is a role-interpretation failure, not proof that OCR cannot read the name. Those cases remain `incomplete`; they are not the seven hybrid results marked complete.
- The hybrid has differing payment references on the two related Greek pages and the Slovak input. Direct image also maps the wrong reference on one Greek page. Preserve model/reference/account associations and diagnose using the saved OCR and response before any new paid experiment.
- Some values appear in fields whose labels confirm absence: customer/recipient roles, non-Croatian tokens in the model field, a currency assumption, invoice identifiers reused as references, and a calculated due date. These require interpretation review; do not call every value an invented string or every disputed name an OCR error.
- Equivalent date, decimal and sort-code formats are not extraction errors. Date scoring accepts the reviewed ISO date, equivalent printed named-month forms and source-adjudicated day/month numeric forms. Calculated dates do not satisfy confirmed absence. No bank digits or leading zeroes are dropped. Account formatting normalizes spaces/hyphens; references normalize whitespace only, preserving punctuation.
- Brand/legal-name variants remain exact-match disagreements, not automatically accepted aliases or definitive wrong-recipient claims. No labels were rewritten to agree with a provider.

Quality and speed do not yet justify freezing either LLM method for mobile integration. Next extraction work should address recipient roles and reference/model association with general synthetic regressions, then compare a separately versioned correction and selected fast/strong controls on all 17 images. Choose with Markus for correctness and latency regardless of price; do not rank untested current profiles using old unmasked measurements.

## Label coverage and safeguards

Marija's recovered HTML is bound to the original dataset, 17 image hashes and 346 field paths. It contains 254 decisions including three prior user locks; 92 entries are still pending. Two marked corrections equal the draft values. Later DMs were reconciled without treating their final acknowledgement as approval of every field.

The separately versioned key scores **102 readable values + 98 confirmed absences = 200 fields**, across images 1–12 and the prior confirmed beneficiary on image 16. It excludes **92 pending, 2 unreadable, 5 disputed recipient-account-holder fields and 47 unsupported/free-text fields**. The last category includes fields the current API cannot represent and free prose needing semantic evaluation; these are visible scope gaps, not correct absences. Candidate-specific dates are mapped to the public document date only for single-option images.

Options match one-to-one using reviewed account/reference anchors before other matches. A provider cannot collect credit by borrowing an amount from one candidate and a reference from another. Unmatched extra candidates remain exposed, but the form did not independently verify completeness of the option inventory, preferred selection or amount-role semantics. Those are not scored as verified facts. Unreadable exact digits, uncertain/pending fields and unsupported inference never become successful readings.

The original labels, returned HTML, old prompts/results/defaults and prior user decisions remain unchanged. Review import is fail-closed on changed dataset/image/field identities, unknown decisions, changed confirmations and overwritten user locks. Scores record missing, differing, uncertain, inferred, absent and run-error cases separately.

## Reproducibility and cost

Verification: **605 offline tests pass**, with **95.44% statement / 90.66% branch** domain/orchestration coverage. Lint, formatting, strict typing, diff whitespace and all three unchanged contract-export checks pass. One pre-existing test-client deprecation warning remains.

Maintained scoring code: `evaluation/reviewed.py`; synthetic regressions: `backend/tests/test_reviewed.py`. Private evidence:

- `.local/m3-draft-policy-2026-10-08/fresh/plan.json`, `providers-planned.json`, `batch.json`, `results/`, `report-r1.json`: pinned plan, three profile identities, all fresh results and stage/latency/cost measurements. The original prepared plan and pre-run report remain historical snapshots; the batch is now complete.
- `.local/m3-human-review-2026-10-08/`: returned HTML, recovered answers, hash validation and linked DM assessment.
- `.local/m3-scored-2026-10-08/reviewed-key-r3.json`, `semantic-holds.json`, `date-format-adjudication.json`, `comparison-r2.json`, `score.py`: final imported key, exclusions/normalization provenance and reproducible scoring. Earlier r1/r2 keys and the r1 comparison are superseded audit records; they omitted candidate-date mapping or counted date-format mismatches.
- `.local/m3-scored-2026-10-08/access-check.json`, `readiness.json`, `preservation.json`, `tests.log`: authenticated model access, current official terms/prices, preservation and offline verification.

Exact methods: `mistral-ocr-rules3-draft-v1@2-4ce2e649ac81058b`, `openai-mini-image-draft-v1@2-c04ed3773c93704d`, `mistral-ocr-openai-text-draft-v1@3-406a5956d06ab7bd`. Requested models are `mistral-ocr-4-1` and `gpt-4.1-mini-2025-04-14`; returned models and every stage's usage are recorded in the private report.

Published-price estimates for the 17-image corpus: OCR/rules **$0.068**, direct image **$0.0330516**, hybrid **$0.1104708**, total **$0.2115224**. These are estimates, not settled cash charges; taxes, exchange rates and account-specific adjustments remain unknown. Current prices were checked against the official model pages, with sources in the readiness record. The existing ledger retains **1,992 dispatched reservations / €313.00 allowance**, an increase of 68 / €6.80. All 1,924 old ledger rows and 2,094 baseline files are unchanged. No subscription, budget reset or public publication occurred. The temporary inference server is stopped.

## Approval and continuation

Present these results to Markus. **Wait for his confirmation before creating the PR or merging any pending PR in this project.** After confirmation, review/check the pending PRs, create the concrete project PR, merge as authorized, and then prepare the next-chat handoff. No merge bypass or force push is implied.

Pipeline choice and agreed capture/review states precede iOS implementation in another chat. The iOS app will send JPEG/PNG images to the existing Mac backend, poll and display an editable draft. A physical iPhone uses the Mac's reachable LAN URL; its own `localhost` cannot reach the Mac. See `ROADMAP.md` for the agreed sequence. Android, final findings and optional native OCR follow later; barcode decoding remains outside this PoC.
