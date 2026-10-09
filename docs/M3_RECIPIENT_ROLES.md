# Payment-recipient role correction — 8 October 2026

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Later human adjudication: Markus accepts the A2A short name and Greek accent omission as correct, with traceable minor variation. The new `reviewed-fields@2` key is `.local/m3-name-review-2026-10-08/reviewed-key-r4.json`; it keeps the original expected strings and adds three explicitly reviewed field aliases. Latest direct image is **79/102 accepted (76 exact + 3 accepted name variants; 77.5%)**. Earlier roles-2 direct is 80/102 (78 exact + 2 accepted). This is saved-response rescoring, not improved extraction or new inference; every old comparison reproduces identically with its original key. The historical table below remains unchanged.

Product distinction: `success` means complete enough for user review, not agreement with a private answer key or verified payment correctness. All drafts still require user confirmation. Approved cosmetic name differences are evaluation annotations, not runtime blocking failures. Runtime cannot necessarily recognize an abbreviation or accent omission when it has no authoritative full name to compare against. Do not introduce an issuer-name lookup table or fuzzy bank/reference matching.

Markus reconfirmed the Protergia amount as **89.02**; the returned **54.99** remains an error. For mobile review, unresolved or conflicting amounts should have a null selected value and an explicit needs-input warning, while other usable fields survive. The existing ambiguous/missing observation representation supports this. A model can still return a wrong amount as observed: this sample did so, and no runtime detector currently proves it wrong. Do not hide every incomplete draft's amount, silently replace it with answer-key data, or hardcode this sample to null. General amount-selection/uncertainty detection remains the next extraction issue; no mobile code or amount-policy change was made in this adjudication.

This continuation addresses a measured confusion between the person receiving a notice and the person receiving its payment. It does not change the answer key, rename model outputs after scoring, or execute payments.

## Implementation

The opt-in `interpretation_policy=draft_v4` uses `payment-party-roles@3`. It keeps the existing compact response shape and `payment-draft@1` review behavior, but replaces the ambiguous recipient paragraph and adds definitions at the three relevant schema fields. Code: `backend/recipient_roles.py`, request adapters, profile registry and runtime provenance.

The instructions distinguish:

- **Beneficiary/payee/creditor:** recipient of the money for that linked payment option.
- **Notice addressee/customer/payer:** recipient of the invoice or payment notice. In an Italian notice, `Destinatario` does not mean payment beneficiary; `Ente creditore` identifies the creditor.
- **Recipient bank-account holder:** explicitly named owner of the destination bank account, distinct from a utility/customer contract holder and from the bank institution.
- **Supplier/manager/agent:** preserved independently; an explicitly named third-party beneficiary takes precedence. Supplier fallback remains permitted where the payee is unstated.

Generic, fictional role examples cover a creditor/addressee pair, customer versus bank versus supplier, and a manager versus owners community. No real names, account numbers, supplier lookups or sample-specific replacement rules were added. Refund/reversed-payment instructions preserve a customer or bank as a legitimate payee when explicitly receiving money. Personal names are not automatically classified as payers.

Revision 3 also reads represented-issuer wording in the invoice body (issuer X represented by agent Y), preserves managers as legitimate creditors for their own fees, and keeps every linked payment option even when its name is uncertain. A printed creditor role is observed evidence, not an unsupported inference merely because the label was interpreted. Bank-transfer preference must not delete alternative extracted options.

Other instructions remain unchanged: printed text only, no barcode decoding, no inferred currency, linked amounts/accounts/references, no invented bank digits, invoice totals allowed, and mandatory review. Uncertain roles remain empty/ambiguous. This is a prompting mitigation, not a deterministic ownership validator or guarantee against every future model error.

## Version and compatibility history

`draft_v1` and all old prompt/schema definitions and results remain unchanged. The first role revision, `draft_v2` / `payment-party-roles@1`, was rejected by OpenAI with HTTP 400 because it placed `description` beside `$ref`. The batch stopped after that one request; its failure and 33 not-run cells remain recorded. No extraction was returned.

The schema-compatible revision 2 inlines the identical field shape with its description, preserving the response contract. It has new profile versions and a new complete matrix. The old failed schema remains reconstructible for provenance; do not use it for new evaluation. A synthetic compatibility regression now rejects `$ref` siblings in the corrected request schema and checks both valid and invalid response types.

No existing completed batch was rerun or relabelled. Tests cover revision isolation across six model providers, annotation and hybrid transport, strict defaults, unchanged output validation and cumulative-budget enforcement. The 51 prior saved payment mappings are identical under the old and corrected review policy. This replay is an invariance check, not a test of the new prompt.

Revision 2 improved recipient selection, but its hybrid output omitted three instalment options on one input. The direct-image output also retained the prior manager-for-community error. Revision 3 adds general represented-issuer and field-local uncertainty instructions, with separate profile versions and another bounded full-corpus comparison. Both earlier revisions remain reconstructible and their outcomes remain available; no sample-specific name replacement was added.

## Bounded evaluation

Fresh comparison: 17 unchanged masked inputs for direct GPT-4.1 mini and 17 for independent Mistral OCR → GPT-4.1 mini text. Same model snapshots and frozen partial reviewed key as the baseline in M3_REVIEWED_RESULTS.md. Do not infer population accuracy or repeatability from this one round; the corpus has been used to diagnose the issue and is a development evaluation.

Latest configuration: `.local/m3-recipient-roles-2026-10-08/revision-3/providers.json`. Exact profiles: `openai-mini-image-roles-v3@2-5094b6dc13ef5718` and `mistral-ocr-openai-text-roles-v3@3-bd5bf166a02f97fe`. Revision 2 is retained at `revision-2/` with `openai-mini-image-roles-v2@2-49f79daeebcf8fa1` and `mistral-ocr-openai-text-roles-v2@3-9545dee5091617dd`. The baseline config and default extract profile remain unchanged.

Each successful-schema revision has its own 51-call / €5.10 allowance plan. Across all three role revisions the maximum is 103 calls / €10.30, including the rejected request. The latest cumulative plan is 2,095 calls / €396.30 allowance, within the unchanged €500 project cap. These allowances are not charges. The software's cumulative-history validation ceiling increased from 2,000 to 10,000 because the previous ledger already held 1,992 calls; actual dispatch still requires and enforces an explicit smaller plan. Defaults, old plan caps and all old ledger rows are preserved. This does not authorize dispatching 10,000 calls.

Current access was checked through authenticated read-only catalogues. Prices and earlier same-day terms/privacy evidence remain linked in `.local/m3-recipient-roles-2026-10-08/readiness.json`; residency and account-specific retention remain unknown. No new provider, subscription, hidden retry or shared OCR stage.

## Measured results

Both completed role revisions returned all 34 results (17 images × 2 methods), with 51 calls each, no retries and no timeouts. The table includes the original baseline to avoid hiding the intermediate result. Every metric uses the same frozen partial reviewed key: 102 readable fields, 63 critical readable fields, 98 confirmed absences; 146 excluded fields remain unscored. This is not whole-invoice accuracy.

| Method / revision | Readable matches /102 | Critical matches /63 | Beneficiary exact matches /16 | Confirmed absences /98 | Median / p95 backend total | Complete / incomplete / error |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Direct baseline | 68 | 41 | 9 | 81 | 4.97 / 12.15 s | 0 / 17 / 0 |
| Direct roles 2 | 78 | 52 | 12 | 90 | 4.28 / 7.41 s | 2 / 15 / 0 |
| Direct roles 3 | 76 | 50 | 12 | 85 | 4.17 / 7.82 s | 4 / 13 / 0 |
| Hybrid baseline | 70 | 44 | 5 | 85 | 6.58 / 11.14 s | 7 / 10 / 0 |
| Hybrid roles 2 | 63 | 40 | 9 | 64 | 6.09 / 8.76 s | 3 / 14 / 0 |
| Hybrid roles 3 | 63 | 37 | 7 | 68 | 6.02 / 8.47 s | 3 / 14 / 0 |

Each timing row has 17 observations. Hybrid includes fresh OCR and interpretation; phone capture/upload/review is not measured. These are different prompts, not repetitions establishing stability or a causal latency improvement. “Complete” means ready for human review, not verified correct.

Manual role inspection of the latest direct-image outputs finds that the previously diagnosed customer/bank substitutions are gone: utility examples return creditors, the UK bank-name case returns the supplier, and the Croatian case returns the co-owners community rather than its manager. The community name omits the city from the answer key, so it does not earn an exact match. Several supplier brand/legal-name differences also remain. No labels or accepted aliases were changed to improve scores.

The hybrid remains unsuitable for promotion: both role revisions omit the three linked instalments on the first multi-option input, despite the latest retention instruction. Revision 3 again selects the notice addressee on the Italian telecom sample. Its saved OCR clearly contains both role labels and the creditor name, so that particular error is in interpretation. Earlier revision 2 got that role right; prompt wording alone has not established reliable hybrid behavior. The latest hybrid also returns the community name without its city. No rerun was hidden or discarded.

Scoring detail: when beneficiary is the only reviewed field on an image, a nonmatching name can leave the whole option unmatched; the score then says `missing` even though raw output contains a name. This affects the community example and must not be described as an empty OCR reading. Inspect raw candidates when diagnosing role failures. Supplier fallback retains its provenance and does not turn an inferred role into verified ownership.

The role mitigation is implemented and tested; full recipient reliability and M3 pipeline selection are not complete. Direct image is the more promising direction from this comparison, but revision 3 is not uniformly better than revision 2. Next work should test an independent fast/strong control and resolve reference/model association, then choose for correctness and speed with Markus. Do not promote the revised hybrid or silently change the extract default based on these results.

## Evidence, verification and cost

Private evidence is `.local/m3-recipient-roles-2026-10-08/`: `revision-2/` and `revision-3/` each contain frozen plan/config/batch, results, `comparison.json`, `before-after.json` and `report.json`. The first rejected request remains in the parent batch. Original reviewed key and baseline results remain unchanged.

644 offline tests pass; domain/orchestration plus evaluation coverage is 95.56% statements / 90.81% branches. Lint, format, typing and diff checks pass; all three public schema exports are unchanged. Replay preserves the payment mapping of all 51 baseline results under the old/new review policy. This tests backend invariance, not model accuracy. Hybrid policy selection now uses its named interpreter, independent of unrelated option order, with a regression test; all four historical experiment plans reconstruct identically.

`verification.json` confirms 88 baseline files (including credentials, default config, original prompts, labels and prior results) and all 1,992 prior ledger rows unchanged. Final ledger: **2,095 dispatched reservations / €323.30 retained allowance**, not cash billed. No active jobs; the inference server is stopped. The latest plan has no remaining call allowance. A later experiment needs a new bounded plan against this same ledger; no further calls during handoff preparation.

Published-price estimates per 17-image method: revision 2 direct **$0.0369920**, hybrid **$0.1139168**; revision 3 direct **$0.0386588**, hybrid **$0.1149964**. Combined successful extraction estimates: **$0.3045640**, plus the initial schema-rejected request whose billed charge remains unknown. Tax, FX and account adjustments remain unknown. These estimates use each stage's usage and stored tariff, not the larger safety allowance. Exact model snapshots and current price-readiness sources are recorded privately.

PR creation/merging still waits for Markus's confirmation; this fix request does not supply that separate confirmation. No commit, PR, merge, publication, pipeline selection or mobile implementation occurred.
