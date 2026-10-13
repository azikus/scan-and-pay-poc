# Phase 2 rollout: provider breadth and extraction quality

> Historical scope/checkpoint: retain the dated evidence below. Current scope, runtime and acceptance are in [CURRENT_STATUS.md](CURRENT_STATUS.md), [CODING_HANDOFF.md](CODING_HANDOFF.md) and [ROADMAP.md](ROADMAP.md). Android/final presentation are skipped; mobile/backend/SUNMI and successful phone Send are accepted. Old next-task wording, worktree paths, provider selections and financial admission limits are not current instructions.

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Implementation update, 7 October: M2 adapters, full-corpus tooling and attempt records are complete for the ten retained provider families. See [M2 operations](M2_OPERATIONS.md), [integration checks](M2_INTEGRATIONS.md) and [current acceptance status](IMPLEMENTATION_STATUS.md). The readiness/workstream descriptions below preserve the pre-implementation plan; they are not current live-validation claims.

Priority recorded 5 October 2026 from the user's follow-up: add the other LLMs, managed OCR services and document APIs as soon as possible, alongside improving OCR interpretation. Do not finish tuning the first two providers before integrating the rest. The historical work order and queue below describe the original plan; current results take precedence.

Milestone 1 remains complete. Its two profiles, historical results and cost ledger remain the baseline. The [provider shortlist](PROVIDERS_AND_BUDGET.md) supplies candidate versions and pricing references; recheck them at integration time rather than treating this plan as current account-access evidence.

**Latest user instructions, 5 October:** collect all credentials upfront and pause Phase 2 implementation/refactoring/provider tests until the complete set is supplied. [PHASE2_ACCESS.md](PHASE2_ACCESS.md) is the request checklist. Every provider evaluation batch must use the full sample corpus. These instructions supersede the earlier per-provider credential timing and two-image smoke subsets.

**Access checkpoint, 6 October:** the full requested credential/resource set is supplied and the upfront gate is satisfied. AWS temporary IAM authentication completed without processing samples. Resume with offline adapter/registry tests; per-provider terms, pricing, region and processing readiness remain pre-inference checks.

[ROADMAP.md](ROADMAP.md) maps this phase to M2 provider coverage/tooling, M3 extraction improvements/hybrids and M4 reviewed comparison/pipeline selection. M2 is complete; M3 interpretation/hybrids and M4 reviewed comparisons remain. [CODING_HANDOFF.md](CODING_HANDOFF.md) supplies the current read order and kickoff prompt; mobile and final presentation work remain deferred.

## Work order

1. Access collection is complete. Re-establish the offline baseline and inventory the full corpus, then extend profile configuration so each model/method can be selected, enabled, versioned and costed independently. Adding a model must not automatically enable it, inherit an unrelated model's tariff, or invalidate old job snapshots. Keep the existing default extract profile until evidence supports changing it.
2. Add the next OpenAI models and Mistral hosted vision/annotation methods and the other provider adapters against synthetic HTTP fixtures. Breadth remains the priority after the credential gate; no provider can be silently waived to start sooner.
3. Improve OCR structure/association from saved responses with offline regressions. This work is independent of additional provider integrations; a new adapter need not wait for the rules to extract every field.
4. Finish the private full-corpus manifest/renditions and API batch tooling begun in step 1; run every sample for every profile under test, including the initial live compatibility batch. Record a bounded batch and call cap before dispatch; the original twelve-call cap is exhausted. A failure or stop leaves explicit incomplete coverage; it does not turn a partial run into a full-corpus result.
5. Use reviewed labels and held-out document/layout groups for quality comparisons. Prioritize further model variants, hybrid methods and targeted rereads using observed failures, latency and cost. The objective is broad method coverage before extensive tuning of individual models.

## Original integration queue

Rows are workstreams, not a requirement to finish one row before starting the next after the upfront credential gate. All shortlist families remain in scope. A missing credential blocks Phase 2 under the user's latest instruction; only the user can explicitly waive a provider.

| Family | Profiles to add | Access needed for live testing | Current evidence |
| --- | --- | --- | --- |
| OpenAI | Additional shortlisted small models and Sol control; Astra as a selected stronger comparison | Existing local key; check each model's access, parameters and tariff | Luna alone implemented/live-tested |
| Mistral hosted LLMs | Small 4, Medium 3.5, Ministral 3 8B and Large 3 candidates | Existing local key; verify model/image/schema support | Vision adapters planned |
| Mistral document processing | Schema annotations; OCR-to-LLM as a separate composition | Existing local key; verify annotation schema and billing | OCR/rules alone implemented/live-tested |
| Anthropic | Haiku, Sonnet and selected Opus/Fable controls from the shortlist | Local API key and account checks | Planned |
| Google Gemini | Flash-Lite and Flash candidates | Local API credentials and paid/free-tier data-use checks | Planned |
| xAI | Shortlisted vision model | Local API key and account checks | Planned |
| Azure Document Intelligence | Read-to-rules; unaugmented Invoice mapping; separately labelled augmentation | Resource endpoint, region, credentials and tier/pricing | Planned |
| Google Document AI | Enterprise OCR-to-rules; unaugmented Invoice Parser; separately labelled augmentation | Project/location, processor IDs/versions, local authentication and billing | Dedicated project, EU OCR/Invoice resources, local ADC and management reads verified; adapter/inference validation pending |
| AWS Textract | AnalyzeExpense mapping; OCR baseline if useful to isolate recognition | Local credential mechanism, region, permissions and pricing | Temporary IAM profile/STS identity verified; policy restricts the two operations to Frankfurt; no Textract processing yet |
| Other hosted open-weight models | Suitable image/text models at a concrete managed endpoint; verify each model rather than assume every family is available | Together key supplied; exact model/version, modality, terms and price checks remain | Host credentials configured; adapter and concrete model selection next |

The entire credential/resource set is recorded through [PHASE2_ACCESS.md](PHASE2_ACCESS.md), using local configuration. Do not assume keys for one Google product configure another, or cloud credentials establish the required processor/resource. Preserve unknown region/retention/cost fields. Hosted open-weight inference is allowed; self-hosted inference remains excluded.

## Different extraction paths, one payment contract

| Path | Method-specific work | Shared output and checks |
| --- | --- | --- |
| Direct-image LLM | Image and common task schema; provider-specific image/schema parameters; preserve model claims and alternatives | Typed payment candidates, linked evidence, shared bank/amount/reference normalization and mandatory review |
| Managed OCR → rules | Immutable text/layout → normalized lines, tables and sections → field/role extraction → conservative candidate association | Same contract and validation; missing fields and ambiguous associations remain explicit |
| OCR → LLM | Text/layout-only interpretation; image-plus-OCR is a separate profile | Same contract; preserve OCR source and every external recipient |
| Prebuilt document API | Map actual returned fields, roles and evidence without filling unsupported fields | Same contract; supplier, account holder and beneficiary remain distinct |
| Document API/annotations → augmentation | Explicit rules or semantic-model stage, separately named and measured | Same contract; do not attribute augmented results to the unaugmented service |

Reuse common schema, normalization and review code. Keep recognition, semantic extraction and association independently testable. A shared internal OCR representation should retain source span IDs, reading order, table cells and genuine coordinates when present; do not fabricate layout or flatten everything into unrelated strings. Introduce only the abstractions required by implemented adapters, not an arbitrary workflow engine.

## Current code and planned organisation

Today `providers.py` contains both vendor adapters, the vision prompt/schema and provider-specific cost calculations. `MistralAdapter` runs OCR followed by `ocr_rules.py`; it retains the full raw response but passes only Markdown into those rules. `profiles.py` registers two fixed profiles. Both adapters return `Extraction`, and `runtime.py` applies the same `review.py` checks before persistence. There is no OCR-to-LLM or document-API adapter yet. This is a working first slice, not already a general composition framework.

M2 boundaries (implemented status and remaining live blockers are tracked separately):

| Code area | Responsibility |
| --- | --- |
| `backend/adapters/` | One vendor module each: authentication/transport, request/response mapping, capabilities, usage and pricing. A vendor can expose vision, OCR and document operations without mixing them together |
| `backend/documents.py` | Immutable internal OCR/document observations: lines, reading order, tables, real boxes, source IDs and provider provenance |
| `backend/extraction/` | Explicit method functions/classes: direct vision, OCR/rules, OCR/LLM, document mapping and augmented document extraction. These compose adapter operations and return the existing typed extraction result |
| `backend/prompts/` | Versioned common semantic instructions plus method-specific image/text inputs and provider schema adaptations |
| `backend/profiles.py` and configuration | Declarative model/method selection, capabilities, exact component versions, destinations and independent enablement. Models are configuration within a compatible adapter, not copied pipelines |
| Existing `models.py`, `review.py`, `images.py` | Shared v1 contract, bank/amount/reference normalization and review, canonical image preparation |
| Existing `runtime.py`, `store.py`, `api.py` | Bounded jobs, persisted stages, failures, idempotency and API; extend accounting/provenance for multiple external stages while preserving v1 behavior |
| `evaluation/` | Full-corpus manifest, API-based batch runner, private saved-response replay and scoring. Ground-truth labels never enter extraction code |

For example, Mistral OCR → rules and Mistral OCR → Anthropic interpretation share the OCR adapter and document representation, while selecting different extraction methods. A prebuilt invoice API first maps its own fields; augmentation is another profile. All methods converge on the same typed payment/evidence and review layer.

The current context attributes external stages to one profile config, saves raw output per run and counts a dispatched run as one call. Before multi-provider/multi-call composition, make recipient identity, immutable raw artifacts, reservations and actual dispatch accounting stage-specific. Reserve the full profile cost before accepting it, retain charged/uncertain failed stages and test partial pipeline failures. Shared OCR/replays must disclose reused inputs and distinguish fresh recognition from interpretation-only timing/cost. Preserve old job snapshots/results throughout migration.

## Full-corpus testing policy

The prepared corpus contains 31 images and retains original source/page/variant grouping. Preserve the originals and duplicate relationships. The API accepts a single JPEG/PNG, and image-only methods receive only that image.

- Every provider evaluation, smoke batch and repeat covers the full prepared sample manifest for each profile being tested. Do not silently pick the two starter images or omit barcode-only, paid, difficult or incomplete documents. Missing bank details can be a legitimate expected outcome.
- Decoder/provider incompatibility and failed attempts remain explicit per-input results. Auth/quota/budget failure can stop dispatch safely; mark the remaining inputs not run and the batch incomplete. Do not shrink the corpus to make a run fit or look successful.
- Split work into bounded profile batches if needed, preserving all samples within each. Before a batch, count all samples × selected profiles × repeats × external stages against the existing budget/ledger. If insufficient, report the constraint rather than spend beyond the cap.
- Ordinary unit/contract tests remain offline with synthetic fixtures. Evaluation regressions replay the full corpus of saved provider observations where available; missing recordings remain a coverage gap until a complete live batch supplies them. A code-only replay is explicitly labelled and never claimed as a fresh paid provider run.
- Keep all source-related variants in one development/holdout group. Running all samples does not authorize tuning on held-out labels; freezes and label access still distinguish development from evaluation.

## Generalizing the observed OCR failures

The M1 cleanup baseline had 184 passing tests; current M2 checks are recorded in IMPLEMENTATION_STATUS.md. These tests do not establish invoice accuracy and missed important layout cases. Add failing synthetic regressions before changing the rules. Do not alter expected payment values or force `ready_for_review` to make the suite green.

- Bank details split by blank lines: associate within a justified payment section, with explicit boundaries for another account, scheme, currency or payment option. Include counterexamples where nearby sort codes and account numbers must remain separate.
- Multi-column totals: identify label/value/currency cells and distinguish amount due from invoice total, subtotal and tax. Blank cells and reordered columns must not change that meaning.
- Croatian payment instructions: recognize general model/reference instruction patterns and preserve punctuation/leading zeroes. Invoice and customer IDs must not become payment references without supporting instructions.
- Vary synthetic names, digits, amounts, labels, ordering and layout. Include negative/ambiguous cases, multiple routes and unrelated footer text. No supplier-name or sample-hash lookup tables.
- Replay saved private OCR through the new version locally, recording source run/hash and parser version. Preserve the original result; label the replay explicitly and do not count it as another live OCR run or fresh OCR cost.
- Keep legitimate review reasons, including an unresolved payee role or an invoice total that is not established as amount due. Test abstention as well as successful extraction.

## Acceptance and evidence

Updated against M2 implementation on 6 October. Checked coverage-accounting items include precise early-stop blockers and do not make those profiles full-corpus complete. The separate M2 completion gate in ROADMAP.md still applies.

- [x] User's breadth priority and distinct extraction paths recorded; all shortlisted families represented in the queue.
- [x] Upfront access gate, complete credential request and full-corpus policy recorded.
- [x] Google access preparation: dedicated project, existing billing, local ADC and two enabled EU processors; private management evidence retained, no documents processed.
- [x] Full credential/resource set supplied, with explicit scope change recorded; upfront gate satisfied on 6 October. AWS STS is access evidence, not extraction evidence.
- [x] Registry supports independent model/method configuration with immutable snapshots and no implicit enablement.
- [x] Each new adapter passes meaningful offline mapping, malformed-output, refusal/auth/quota/timeout, provenance and cost tests; applicable polling is bounded.
- [x] Separate cost-report inputs and preliminary rows account for each selected option, stage, retry, unknown charge and incomplete corpus run; see COST_REPORT_PLAN.md.
- [x] OCR regressions cover the observed failure classes and counterexamples; private offline replay is preserved separately.
- [x] Each configured profile has a bounded full-corpus API evaluation with coverage accounting, or a precise blocker/incomplete status. Planned and fixture-tested are not live-validated.
- [x] Comparison preserves partial success and independently measured fields, unresolved reasons, stages, requested/returned versions, usage and recipients.
- [ ] Representative source-document groups and checked labels support the first scored comparison; unverified entries remain unscored.
- [x] Domain/orchestration coverage remains at least 90% statements and 85% branches, with all critical scenarios passing.

The [separate cost report](COST_REPORT_PLAN.md) is a required evaluation output, begun during M2 and completed for M4 independently of the later HTML findings. Record each exact option, coverage, stage/retry costs, tariff provenance and unknown charges.

The existing €500 total and included €30 first tranche remain unchanged. Twelve earlier dispatches retain €12 in holds; neither the recorded USD estimates nor prepaid credit release those reservations. New bounded batches must use the same ledger and record any applicable cap/tranche transition. Do not run every model × document × variant × repeat automatically. No mobile app, browser customer UI or final HTML findings are part of this rollout. The private progress explainer requested on 7 October is a separate, current deliverable.

This document retains the original rollout work order. Completed implementation and measured acceptance evidence are maintained in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).
