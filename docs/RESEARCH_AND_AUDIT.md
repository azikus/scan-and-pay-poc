# Research and reference-code audit

Current handoff note, 6 October: the audit/research below is dated evidence about historical code and provider documentation. The new backend's completed Milestone 1 is recorded in IMPLEMENTATION_STATUS.md; the full access set is now supplied. Start M2 from CODING_HANDOFF.md/ROADMAP.md. Recheck specific APIs/models/pricing during integration; do not repeat this entire research round or treat the reference registry as the current backend.

Code audit: 30 September 2026. Provider/framework research refreshed 1 October 2026. User scope clarification, 5 October 2026: Python selected; provider-hosted open-weight and proprietary models allowed; self-hosted inference excluded; HTML report deferred. This is a targeted update for the engineering plan, not a new claim that every competitor, API or model has been tested. Current primary documentation was checked; no invoice was uploaded to an external provider during this review.

## 1. What the reference benchmark actually contains

Inspected `reference/phase1/scan_pay_benchmark.py` (1,551 lines), schema, example provider configuration and tests. It is a CLI experiment runner, not a backend service.

Implemented adapter functions exist for OpenAI Responses, Anthropic Messages, Gemini generateContent, OpenAI-compatible chat completions, Mistral OCR/document annotations, Azure Document Intelligence, Google Document AI and AWS Bedrock Converse. The example configuration includes several model/provider profiles, all disabled by default. The presence of an adapter is not proof that its API/model settings work against today's service.

There is no dedicated AWS Textract, Nanonets, local OCR or Docling adapter in the inspected adapter registry. Bedrock is not Textract. There is no job API, persistent service queue, UK sort-code field or native app in the reference project.

### Reuse candidates

- Input hashing and image-preparation ideas. The new API is JPEG/PNG-only; historical PDF preparation is not a required backend feature.
- Provider request/response mapping scaffolding, after checking current capabilities and writing response-fixture tests.
- Per-run JSONL output, repeated runs, error isolation and CLI reporting concepts.
- Token/page/document usage capture and configurable cost calculation, with more complete accounting.
- Existing offline tests as historical regression examples, not as the new acceptance specification.

### Must change before reuse

| Finding | Consequence for the new plan |
| --- | --- |
| Schema chooses `selectedPaymentIdentifierId` from a flat identifier list | Cannot express a linked UK sort-code/account pair or preserve multiple payment-option associations. Replace with typed destination candidates. |
| Document-service finalizer treats customer accounts/payment references/creditor codes as routable and selects the first one | Wrong for a generic bank-payment service; require route-specific completeness or an explicit biller resolver. |
| Prompt/validator reject paid and scheduled-direct-debit documents; tests enshrine this | Historical policy, not an agreed product requirement. Separate observed wording from extraction success. |
| Azure/Google mapping can label an invoice total as amount due | Retain original field role and evidence; do not silently promote fallback totals to confirmed outstanding amounts. |
| Generic identifier normalization removes punctuation from all types | Keep raw values and use scheme-specific normalization, particularly for references. |
| Receiver scoring accepts substring/fuzzy matches | Report reviewed alias matching as the strict score; keep fuzzy similarity diagnostic only. |
| Prompt tells the model to ignore visible barcodes | Not an isolated non-barcode experiment. Use physically covered/code-free variants. |
| Hand-written partial JSON Schema validator | Replace with a standard validator plus explicit cross-field business rules. |
| Empty strings represent unavailable values | Use explicit null/missing/ambiguous states in the proposed contract. |
| Runs are sequential and have one aggregate latency measurement | Add service/job stages and bounded concurrency; preserve serial runs where needed for controlled timing. |
| Price calculation covers basic token/page/document rates | Add pricing provenance, billing minimums, retries, cached/reasoning categories where applicable and unknown-cost states. |
| Example model names and a `latest` alias are stored in the old config | Revalidate exact models/capabilities; pin versions where possible. Do not treat the old catalogue as current recommendations. |

Audit verification: executed the existing unittest suite offline with Python bytecode writing disabled. **15 tests passed.** The suite tests schema/scoring/normalization/cost helpers and temporary local report output. It does not establish API compatibility, visual extraction performance or UK correctness. No implementation files were changed.

## 2. Historical client response, not a constraint

The mobile code declares `POST api/AircashPay/ReadCode`. Request fields are `data`, `detectedScanType` and optional `rawData`.

The response includes `transactionID`, `codeType`, nullable `amount`, `fee`, `amountWithFee`, `currencyISOCode`, `receiverName` and `description`, plus business-specific card/utility details, verification status, target screen and optional `ibanInvoiceDetails.paymentForm` fields/values.

Inspected locations in the existing repository: `features/aircashpay/.../AircashPayApiService.kt`, `models/ReadCodeRequestBody.kt` and `models/ReadCodeResponse.kt`. This confirms the client-side contract, not the inaccessible server's implementation. It does not establish whether each barcode format is parsed locally or remotely; that full capture-flow audit was not repeated for this backend plan.

The user has explicitly clarified that these references are from the start of the project, not hard guidelines. Use only useful extraction semantics, including UK banking and Croatian remittance fields. Do not make a model manufacture transaction IDs, fees, recipient IDs or dynamic client form definitions. Reusing the sample corpus does not require invoking this client endpoint.

## 3. Current document APIs: useful but not a complete payment contract

### Microsoft Azure Document Intelligence

The official invoice model supports structured extraction from invoice/utility-bill images. Its published 2024-11-30 schema contains PaymentDetails fields including IBAN, SWIFT and bank account number, but no explicit sort-code field in that published list. That does not prove the text cannot be read: OCR/key-value extraction or augmentation may recover it. Score the prebuilt mapping and any augmentation separately. [Model documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/invoice?view=doc-intel-4.0.0), [official field schema](https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/invoice.md).

### Google Document AI

The official Invoice Parser list includes supplier information, totals, `supplier_iban` and `supplier_payment_ref`; it does not list a dedicated UK sort-code field in the reviewed schema. Supported languages/versions are processor-specific; do not assume general OCR language coverage implies invoice-entity extraction coverage, especially for Greek samples. Test raw invoice-parser output first, then custom extraction or OCR-plus-rules/LLM as a separate profile if needed. [Processor catalogue and fields](https://docs.cloud.google.com/document-ai/docs/processors-list).

### AWS Textract

AnalyzeExpense exposes summary fields and line-item groups for invoices/receipts. It is a relevant comparison component, but the historical reference registry has Bedrock rather than Textract; the new backend currently has only OpenAI vision and Mistral OCR/rules. A new mapping and capability check are required before treating Textract as an enabled provider. [Official invoice/receipt documentation](https://docs.aws.amazon.com/textract/latest/dg/invoices-receipts.html).

### Mistral

Document annotations accept a supplied schema and combine OCR output with a model-based extraction step. This is particularly relevant to the proposed hybrid comparisons. Label OCR-only and OCR-plus-annotations separately; they are not the same method or necessarily the same charge. The historical benchmark already has an annotation adapter to reassess. [Annotations](https://docs.mistral.ai/studio/document-processing/annotations), [OCR API](https://docs.mistral.ai/api/endpoint/ocr).

### Nanonets

Keep Nanonets as a commercial comparison candidate, subject to current evaluation access, suitable product scope, sample permissions and pricing. Its inclusion is not a claim of a tested result or a commitment to build around it. Obtain current API documentation from the granted product account before implementation.

A fresh provider/model roster, public tariffs and €500 allocation are in [PROVIDERS_AND_BUDGET.md](PROVIDERS_AND_BUDGET.md). OCR/document APIs are core comparison families, not just optional LLM fallbacks.

## 4. LLMs and model selection

OpenAI's image-input and structured-output documentation supports the direct-image-to-schema experiment; schema conformance does not guarantee correct field values. Keep a nullable/uncertain route through the schema and verify semantics independently. [Image inputs](https://developers.openai.com/api/docs/guides/images-vision), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

Claude vision and Gemini structured outputs are relevant parallel baselines. Image limits and schema support differ by endpoint/model; use a capability record per profile and preserve preprocessing differences. [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision), [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output).

Do not freeze a brand-level ranking or copy old model IDs. Before the first run, verify the chosen model's image support or OCR-text-only role, structured-output mode, region/access, limits, exact version and current pricing. The user can choose several models from one provider; a two-tier pairing is not required.

User clarification, 5 October 2026: provider-hosted open-weight models, including Mistral/Llama/Qwen, are allowed alongside proprietary models. The earlier blanket exclusion was a mistaken interpretation. Self-hosted inference, local weight downloads and project-operated cloud/GPU model servers are excluded. Include smaller hosted models alongside stronger controls; verify model capabilities and actual endpoint access before use. No weights were downloaded.

## 5. Historical component research and hosting boundary

These notes preserve research context, not an instruction to install these pipelines. Self-hosted Docling/PaddleOCR model pipelines are excluded; a provider-operated managed API may be considered after normal capability, terms and cost checks. Open-source SDKs and deterministic rule/template libraries remain allowed.

**Docling** parses documents into a structured representation, supports OCR/layout and local execution, and now documents VLM and service options. It was researched as an input-processing component; running its model pipelines ourselves is outside scope. It does not by itself establish our desired UK payment semantics or reviewed mobile journey. [Official repository](https://github.com/docling-project/docling).

**invoice2data** is worth a maintained-template baseline. Importantly, the current repository also documents optional AI-assisted template creation and runtime AI fallback; describing it as only regex/templates would now be incomplete. Keep its deterministic template path and its AI-enabled path separate in testing, and do not author templates on the holdout invoices then claim unseen-layout generalization. [Official repository](https://github.com/invoice-x/invoice2data).

**PaddleOCR** research considered recognition scripts, model footprint and hardware runtime. Running its inference ourselves remains excluded by the hosting boundary. A provider-operated OCR API is eligible regardless of whether its underlying weights are open; capability, data terms and pricing still need verification. [Official repository](https://github.com/PaddlePaddle/PaddleOCR).

Record exact versions and licences for third-party components and hosted services. Redistributing or serving model weights is outside scope. “Open source” does not mean all bundled models or external services share one unrestricted licence.

## 6. Do we need the mobile apps now?

No for backend cloud APIs, server OCR, deterministic extraction, barcode parsing from still images or photographs taken in the phone's standard camera. These are testable from uploaded files.

Yes for credible measurements of the actual mobile capture pipeline, on-device latency and platform-specific OCR. Agree the mobile designs first, then start with iOS on the user's device. A minimal native harness can test saved images before capture automation. Optional text/boxes/quality observations must identify the exact uploaded image, engine, coordinates and timing. Image-only remains supported. Apple Vision is also available in Apple development environments beyond the phone, but a desktop result is not a substitute for device measurements.

ML Kit's current Text Recognition v2 documentation lists Latin, Chinese, Devanagari, Japanese and Korean scripts. Do not assume Greek coverage merely because the UK/Latin path works. Native OCR results need per-platform/OS/script testing and should not be a compulsory early gate for every document. [ML Kit documentation](https://developers.google.com/ml-kit/vision/text-recognition/v2), [Apple text-recognition documentation](https://developer.apple.com/documentation/vision/recognizing-text-in-images).

## 7. UK semantics worth resolving now

Pay.UK distinguishes name/account checking from simply reading sort code/account details. Some accounts additionally require secondary reference data, such as a roll number. That supports explicitly modelling account-holder name and reference semantics, without pretending the PoC performs Confirmation of Payee. [Pay.UK FAQ](https://www.wearepay.uk/what-we-do/overlay-services/confirmation-of-payee/faqs/).

Vocalink publishes UK modulus-checking guidance/tables. If added, pin the table/rule revision, handle documented exceptions and licence/distribution terms, and distinguish a check failure from an unsupported check. Do not implement a simplistic checksum as proof that an account exists. It is optional for the first extraction slice. [Vocalink modulus checking](https://www.vocalink.com/tools/modulus-checking/).

Earlier research did not identify a universally adopted UK domestic GBP invoice QR payload equivalent to some national payment-slip schemes. That is a qualified research conclusion, not proof that no relevant scheme exists. A detected QR may be a website or provider-specific payment link. EPC QR guidance concerns SEPA credit transfer data and must not be treated as a generic UK sort-code format. [EPC QR guidance](https://www.europeanpaymentscouncil.eu/document-library/guidance-documents/quick-response-code-guidelines-enable-data-capture-initiation).

## 8. Research still needed at implementation time

Actual account/model access and tenant prices/regions; exact SDK licences; account data-use/retention settings; a checked payment-field answer key; supported barcode schemes. Sample-provider testing and the €500 budget are authorised; no separate review team or staffing questionnaire is required. These are explicit checks, not reasons to restart the entire market-research conversation.

Public pricing was refreshed on 1 October and is documented in PROVIDERS_AND_BUDGET.md with billing qualifications. No model accuracy, latency or cost-per-correct-result ranking can be inferred from documentation alone.

## 9. Country-aware interpretation and Croatia

The HUB payment-barcode specification distinguishes recipient IBAN, model, reference, purpose code and description. These are useful semantic fields even for a barcode-free invoice; do not blindly impose the barcode's field-length limits on every invoice. [HUB specification](https://hub.hr/sites/default/files/inline-files/2DBK_EUR_Uputa_1.pdf).

Language/address can help, but an issuer/customer address is not the bank's country. Model language, issuer country, account country and scheme separately. Prefer explicit sort-code/account labels, recognised IBAN structure and Croatian model/poziv na broj labels; keep unknown or conflicting routes open. A valid checksum does not validate ownership or justify silently changing O to 0.

The invoice was subsequently supplied from Desktop on 1 October. Inspected both pages; removed only the first page's separate barcode image object, verified that PDF text and all pixels elsewhere were unchanged, and added its 300-DPI PNG payment page plus a private provenance sidecar. The source PDF stays outside the project. The screenshot remains unavailable and uninspected.

## 10. Frameworks and device processing

FastAPI, ASP.NET Core and Ktor are all capable of this API. Python is now selected. Its existing evaluation tooling and typed API workflow fit the PoC; the earlier local-model rationale is no longer active. No framework automatically improves extraction accuracy. [FastAPI](https://fastapi.tiangolo.com/features/), [ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0), [Ktor](https://ktor.io/docs/server-testing.html).

Backend OCR can be evaluated immediately from JPEG/PNG images. Device OCR may improve capture feedback or provide supplementary evidence, but its quality, script coverage and device cost need real iOS measurements after design agreement. Android follows. Compare image-only against image-plus-device-observations, keeping cost and recognition errors visible.

## 11. Reporting and evidence status

The premature HTML report is archived privately and is not active guidance. The final HTML report follows measured experiments. ARCHITECTURE.md now shows the handoff design/data destinations, not measured behavior. The later attendee companion must show real stages and mask private details.

No external inference, new SDK installation, model download or client-code change was performed for this research update. Historical tests remain distinct from target ≥90% statement/≥85% branch coverage for the new domain/orchestration code.

## Separate cost evidence — 6 October 2026

The required standalone [cost comparison](COST_REPORT_PLAN.md) covers each exact evaluated option. This research/shortlist is not a substitute for measured stage usage, billing minimums, retries, account-specific tariff checks and unknown-charge reporting. Preserve historical research dates; recheck selected APIs/prices at integration rather than claiming this cleanup refreshed them.
