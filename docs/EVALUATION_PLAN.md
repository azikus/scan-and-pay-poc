# Evaluation plan

Coding baseline, reconciled 1 October 2026; handoff status updated 6 October. STARTER_EVALUATION.md describes the completed Milestone 1 subset only. The next M2 task prepares the full corpus; M3 compares interpretation methods and M4 uses checked labels for selection, as mapped in ROADMAP.md. No provider performance results are asserted by this plan. It defines how to get evidence from the existing backend before selecting a pipeline, which need not be hybrid.

## 1. Questions the experiments should answer

1. Can direct-image LLM extraction produce a correct, complete payment draft from our real photographs?
2. How do OCR/rules and document extraction APIs compare on the same payment fields?
3. Does adding OCR or document-API text/layout to an LLM help, hurt or merely add cost?
4. Which errors are detectable through structural checks or evidence, and which remain confidently wrong?
5. What improves difficult images: preprocessing, another model, a different method, or asking for a better photograph?
6. How do results differ between UK invoices and the original client documents?
7. What does a chosen end-to-end pipeline cost and how long does it take, including failures and fallback?

The research hypothesis is not “hybrid must beat LLM-only.” Keep the direct-vision baseline and accept the measured outcome. A simple method may win on these documents while a more elaborate method provides no demonstrated benefit.

## 2. Dataset unit and manifest

Separate **source document**, **image variant** and **repeated run**. Record source-page provenance for old assets, but upload only JPEG/PNG pixels; no backend page parameter. Ten photographs of one invoice are ten capture conditions, not ten independent supplier/layout examples.

Manifest fields: document ID; cohort; original private source path/hash; provenance and permitted uses/providers; page grouping; language/script and country labels; barcode presence/type where established; image variant ID; capture device/OS and conditions; transformation parameters; ground-truth version/reviewer; split assignment.

Current starting point: eight original files, five independent UK invoices in a print pack and one newly added Croatian invoice payment-page PNG. Verify the original-file grouping before treating this as fourteen independent documents. Some images may show multiple pages; some documents may not contain a visible bank route at all. That is a useful limitation case, not a reason to invent ground truth.

Keep original sources untouched. Store new photos under `samples/photos/` and transformed copies under `samples/variants/`; keep the manifest and labels private under `.local/evaluation/`. Use relative project paths in the manifest, not hard-coded paths into the former project.

## 3. An answer key, distinct from user confirmation

The app user must always review and confirm the extracted details. An **evaluation answer key** is different: it lets us determine whether an experiment read a payment field correctly. No separate human team or two reviewers are required.

The assistant can draft labels from visible images. Markus checks payment-critical values or resolves ambiguities before headline scoring; unverified entries stay explicitly unscored. Preserve raw extraction separately from subsequent corrections. Record:

- Printed payee/supplier and separately named bank account holder, with explicitly accepted aliases.
- Amount due and currency, other plausible totals, and why one is selected or why selection is unresolved.
- Complete destination candidates: linked UK sort code/account number, IBAN or explicitly identified biller scheme/reference.
- Payment reference and whether it is required, including separately observed Croatian model and poziv na broj linked to the destination. Keep invoice/customer numbers distinct.
- Field locations/excerpts where practical, and whether each value is visible, missing, unreadable or ambiguous in that particular image variant.
- Expected review reasons for incomplete or conflicting cases.

Label only what the input makes available. A detail visible in the source PDF but cropped out of a photo cannot be considered observable in that photo. The benchmark can still measure whether the system asks for a better image.

An assistant/provider answer is not automatically an answer key, and provider agreement is not proof. Use checked source evidence; leave unresolved labels unknown. Version corrections to labels and rescore consistently rather than favouring one engine.

Do not use fuzzy name similarity as the headline correctness definition. Score against reviewed aliases with defined normalization; optionally show fuzzy similarity as a separate diagnostic. One wrong account digit is wrong, even when the rest of the record looks excellent.

## 4. Capture protocol without a mobile app

Use the phone's ordinary camera, print the approved invoices, and transfer original photographs to the computer. Avoid messaging apps that silently resize images. Record any export from HEIC to JPEG and keep the original privately where permitted.

Recommended initial image conditions per document:

1. Clean reference image: rasterized PDF page or supplied image, no hidden PDF text sent to the model.
2. Ordinary photo: whole page on a table, normal indoor light, readable framing.
3. Oblique photo: realistic perspective and mild shadow, without deliberately hiding essential fields.
4. Difficult photo: one controlled issue such as blur, glare, folded corner or clipping. Annotate which details are still legible.

Start with Markus's iPhone; add an Android capture subset in the later mobile phase. We do not need a custom app to establish backend performance on their photos. Later repeat the same tests through the real apps because their capture/compression pipeline can change the results.

For non-barcode testing, use documents without codes or physically cover the codes before photographing. Telling a vision model to ignore a visible barcode is not experimental isolation. The new Croatian invoice has been prepared as samples/racun-12793-26-no-barcode.png outside the project and verified before addition: the barcode image object was removed from the PDF, then page one rendered at 300 DPI. All pixels outside that region and all PDF text match the original. Its provenance sidecar identifies this as a digitally prepared reference, not a real camera photo. Supporting page two stays in the external source PDF and is not a separate benchmark document. Keep full-image barcode-assisted tests as a separately labelled condition.

Do not fabricate image edits as “real camera” evidence. Synthetic mutations and transformations are useful robustness tests and must be labelled as such.

## 5. Experiment matrix

Execution priority updated 5 October: expand coverage across the provider/method families alongside the OCR regression work, following [PHASE2_ROLLOUT.md](PHASE2_ROLLOUT.md), **after all upfront credentials are supplied**. Every provider evaluation, including smoke batches and repeats, covers the full prepared sample corpus. Convert source PDF pages into private JPEG/PNG fixtures without adding PDF API support; track related images/pages and every failed/not-run input. The upfront access gate is now satisfied as of 6 October; compatibility tests can proceed before labels are verified, after integration checks and a bounded plan. Accuracy scoring cannot. Do not tune only the starter invoices before adding the other services.

The upfront access gate was satisfied on 6 October. Labels remain unverified; provider terms/prices/access checks and a new bounded batch plan still precede inference. No full-corpus run is claimed by the access/handoff work.

| Profile family | Input to extraction | What it tells us |
| --- | --- | --- |
| Vision-only | Canonical image, common task/schema | Tests the client's initial LLM idea directly. |
| Cloud OCR + rules | Image -> Azure Read / Google OCR / Mistral OCR -> rules | Recognition quality and cloud cost without an LLM semantic step. |
| OCR + LLM | Fixed managed OCR output -> selected provider-hosted model | Separate text/layout-only from image-plus-OCR; test recognition versus interpretation. |
| Document API | Azure Invoice / Google Invoice Parser / Textract AnalyzeExpense | Raw payment-field coverage, including missing UK/HR fields. |
| Schema-driven document extraction | Mistral annotations / commercial extractor | Include OCR, extraction-model and workflow-block costs. |
| Document API + rules/LLM | Structured fields plus OCR/layout -> extra processing | Measures the added value/cost of augmentation. |
| Barcode parser | Supported visible payload -> common contract | Deterministic comparator where applicable, not evidence of non-barcode performance. |
| Template extraction | Known supplier/template -> fields | Measures maintained-layout benefits separately from unseen-layout generalization. |
| On-device observations, later | iOS image-only vs image+OCR/quality vs text-only | Real-device capture and OCR value; Android follows. |
| Country-routing ablation | Generic vs evidence-routed UK/HR logic | Include cross-border/conflicting hints and routing cost. |
| Image/detail ablation | Original, resized, alternate detail, payment crop | Record accuracy, usage and each rendition. |
| Character-ambiguity ablation | Raw OCR vs rules vs targeted second read | O/0 and I/1 handling without invented digits. |

The planned registry covers provider-hosted proprietary and open-weight models; self-hosted inference is excluded. Record both the model identity and the actual hosting provider. Compare may select profiles or **all enabled compatible** profiles, stored as a snapshot. This does not enable every vendor or require a complete Cartesian product. Extract selects one composed profile.

Stages:
1. Completed Milestone 1 history: the two UK/HR reference images established the first vision and OCR/rules integrations. Phase 2 must use all samples from its first provider evaluation; the two-image subset is no longer the testing policy.
2. Method comparison: selected smaller and stronger OpenAI/Claude/Gemini and hosted Mistral models, managed OCR/rules, Azure/Google invoice extraction, Mistral and Textract as access permits. Compose OCR-plus-LLM from these components.
3. Additional controls: xAI, deterministic invoice2data templates over managed OCR text, and commercial Nanonets/Mindee when available. Other provider-hosted open-weight models such as Llama/Qwen are eligible once an appropriate endpoint and capability record are verified. No self-hosted inference. Lack of access is not inaccuracy.
4. Ablations: routing, OCR supplementation, resolution/detail, ambiguous characters and bounded fallback on informative cases.
5. After design agreement and a working backend: iOS/device observations, then Android.

See [provider shortlist and budget](PROVIDERS_AND_BUDGET.md). Request more photographs when a specific failure needs one—a sharper footer, natural oblique view or another lighting condition—not as a blanket prerequisite.

## 6. Fairness and reproducibility

- Store input hash, rendition dimensions, prompt/schema/adapter/preprocessing versions, exact requested and returned model/processor version where available, region, parameters and timestamps.
- Prefer pinned versions for final comparisons. If an alias is unavoidable, preserve returned metadata and call out possible changes between runs.
- Keep the task specification comparable across LLMs while adapting to each provider's supported schema subset. Provider-specific prompt tuning is a separate labelled experiment.
- Compare both the untouched prebuilt API mapping and any enhanced pipeline. Do not supply ground truth, supplier templates or lookup answers to an ostensibly general model.
- Separate cold/warm local runs, retries and explicit caches. Primary inference comparisons should not secretly reuse cached results.
- Select profiles/repeat counts within budget, and use every sample in each repeat rather than a document subset. Temperature settings do not establish determinism across providers. A budget stop leaves an explicitly incomplete batch; never silently reduce corpus coverage.
- Assign all variants of one invoice to the same development/holdout group. Where possible hold out whole suppliers/layouts too. With the tiny initial set, label holdout findings exploratory and do not claim a representative population estimate.
- No PDF/text-layer extraction arm is planned. OCR text must originate from the actual image or documented device observations.
- If OCR is shared across profiles, show shared batch cost and standalone pipeline cost/time separately. Do not count cached OCR as fresh recognition.
- Route using evidence available to that profile, not the answer key. Include routing work and caller hints in provenance.

## 7. Metrics and their denominators

### Correctness

- Exact per-field match after explicitly allowed, type-specific normalization. Report visible expected values as the denominator and separately report correct missing/abstention behaviour.
- Complete-record match: all required fields for the labelled route, including correct pairing/selection and required reference. One incorrect payment-critical field fails the record.
- Completeness/coverage: how often a full draft is produced on documents with sufficient visible information.
- Wrong-ready rate: how often the backend says ready-for-review while a critical selected field is wrong. Report the count and denominator, not just a percentage.
- Unnecessary review/abstention: complete readable documents that the system does not confidently assemble, reported separately from wrong answers.
- Evidence fidelity: is the claimed excerpt/location real and does it support the selected meaning? Not every engine supplies boxes; do not reward invented coordinates.
- Group results by UK versus client cohort, capture condition, language/script, barcode condition and route type. Show per-document failures alongside aggregates.

Do not let one easy amount field dominate a mean score while bank accounts are wrong. Do not allow successful abstention on a paid/direct-debit label to count as correct extraction of all the payment fields.

### Time

Measure request acceptance/upload time where the client can observe it, queue wait, image preprocessing, OCR, provider calls/polling, retries, normalization/validation and end-to-end result availability. Mobile capture-to-review timing is a later separate measurement.

Show per-run values, median and a tail summary with sample count. A p95 from a handful of runs is descriptive, not a reliable SLA. Compare mode wall-clock duration is different from one extraction pipeline's latency.

### Cost

Store provider-reported usage and any reported cost, otherwise a dated estimate with its pricing source, currency, billing unit and confidence/limitations. Missing pricing or usage means unknown, not zero. Include billed page minimums, OCR stages, cached-token categories, reasoning/output usage where available, retries and fallback calls as applicable.

Show cost per attempt, per input document and per correct complete result. Report unknown charges and unsuccessful calls rather than quietly excluding them. For local deterministic rules and later native OCR, API charge may be zero but runtime, hardware and operations are not free; do not claim a full TCO from token prices.

The total experiment cap is €500, covering the active managed-service experiment. Start with a maximum €30 smoke-test tranche within that total, retaining the €80 reserve. Estimate matrix size before execution. Use maximum calls and provider-side limits as well as best-effort spend estimation. The benchmark cannot guarantee an exact invoice total from incomplete billing telemetry.

## 8. Error analysis and regression tests

Classify failures as input quality, OCR transcription, field meaning, amount choice, wrong destination pairing, missing required reference, invented data, unsupported language, invalid schema, provider failure, normalization bug or scoring/label issue. Keep the classification reviewable.

Additional cases: Croatian model/reference versus invoice number; English text with HR IBAN; Croatian text with non-HR account; customer address mistaken for issuer; O/0 and I/1 in numeric and alphanumeric fields; a visually unsupported repair that passes checksum; multiple repairs; device-OCR/image mismatch; resized image losing a footer.

Required fixture cases include: leading-zero account; multiple UK account options; invoice number that looks like an account; supplier versus billed customer; separate account holder; amount due versus VAT/subtotal/balance; decimal comma and thousands separator; ambiguous currency; credit/negative balance; missing sort code; unreadable digit; reference-only bill; IBAN checksum failure; barcode/text disagreement; irrelevant QR URL; instruction-like text inside an invoice; malformed image; rotated image; provider timeout/refusal; job restart; duplicate idempotency key.

Use synthetic fixtures for public unit tests. Do not pad or “repair” banking digits silently to make a fixture pass. Expected unsupported/needs-review outcomes are valid and must be distinguishable from provider crashes.

## 9. What “high confidence” will mean at this stage

Not an arbitrary model-reported 0.99 and not a consensus count. Initially use explicit completeness, evidence and validation signals to choose ready/needs-review/insufficient states, then measure their observed correctness on labelled examples.

If a later calibrated confidence/routing model is desired, it requires a larger independent dataset and calibration evaluation. The initial corpus can expose failures and select a provisional demo pipeline; it cannot establish rare-error safety or universal invoice support.

## 10. Deliverables

Private versioned manifest and labels; adapter fixture tests; JSONL per-run results; a scored JSON/CSV summary once labels are verified; a **separate per-option cost report** with Markdown and JSON/CSV tables as specified in [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md); a final HTML report of approaches, exact field/record outcomes, UK/client differences, failure examples, latency, known/estimated costs and recommended pipeline. Keep responses privately for reproducibility; bespoke automatic expiry is deferred.

Begin the standalone cost report with M2 batches and deliver it with M4 pipeline selection; refresh it in M8. It includes all selected models/processors/methods, failures and unknowns, comparable attempt/document/corpus costs and explicitly qualified volume scenarios. It does not require waiting for the HTML deliverable.

The findings report should explain why an approach is useful, where it fails and what is still untested. It is not a business go/no-go document. The external summary uses Azikus styling and omits private sample details, credentials and unsupported accuracy or savings claims.

## 11. Image size and cost

Image dimensions and visual-detail settings can affect input tokens and price. Compressed JPEG megabytes are not a universal billing unit: changing compression at the same dimensions may save transfer time without lowering visual-token charges, while harming legibility. Count OCR/prompt text, images, output/reasoning, extra crops and retries.

Test a small resolution/detail ladder using the same documents; record dimensions, bytes, hash, legibility, usage and exact-field results. Full resolution is not automatically better, nor is a crop automatically cheaper. Document APIs may bill per page/image or document minimum: Google's Invoice Parser charges $0.10 for a 1–10-page document, so one image is not $0.01. [OpenAI visual-token calculator](https://developers.openai.com/api/docs/guides/image-cost-calculator), [Google pricing](https://cloud.google.com/products/document-ai/pricing).

## 12. Engineering test evidence

Coverage is distinct from model accuracy. Implementation targets: at least 90% statements and 85% branches for our backend domain/orchestration, plus every enumerated payment-critical scenario. Unit tests use synthetic/redacted fixtures, not paid calls or private invoices in Git. Live smoke tests validate account/API compatibility, not general quality.
