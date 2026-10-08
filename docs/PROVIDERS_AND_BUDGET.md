# Provider shortlist and experiment budget

Research baseline 1 October 2026; hosting scope and Mistral candidates corrected 5 October after the user clarified that provider-hosted open-weight models are welcome. This shortlist includes planned profiles; actual implemented/live-tested status is recorded in IMPLEMENTATION_STATUS.md. Inclusion is not a measured ranking. Prices are public USD list rates unless stated otherwise; the project budget is EUR. Do not equate currencies or omit VAT, FX, minimums, retries and account-specific terms. Recheck before dispatch.

## 1. Selection model

The planned M2 registry extension separates component (OCR, document extraction, model, rules) from profile (a sequence of components); the current implementation has two fixed profiles. Compare already supports selected or all enabled compatible profiles independently. Extract selects one profile. Several models from a provider are allowed; no cost-efficient/strong pair is mandated.

Keep planned/configured/live-validated status, exact requested/returned model version, input support, structured-output mode, language/script coverage, actual endpoint/account/region configuration and pricing source. Missing pricing means unknown, not zero. No supplier name is a performance result.

## 2. Direct-image model candidates

The first pass deliberately includes smaller models. Stronger models are comparison controls, not assumed winners or compulsory fallbacks. Additional rows are planned, not live-validated; verify access, image input, output-schema support and current tariff before enabling.

| Provider | Model ID | Standard USD input/output per million tokens | Role |
| --- | --- | --- | --- |
| OpenAI | gpt-6-luna | $0.10 / $0.50 | First small-model integration candidate. |
| OpenAI | gpt-5.4-nano | $0.20 / $1.25 | Small extraction baseline. |
| OpenAI | gpt-4.1-mini | $0.40 / $1.60 | Non-reasoning comparison baseline. |
| OpenAI | gpt-6.1-sol | $2 / $10 | Stronger control. |
| OpenAI | gpt-6-astra | $10 / $50 | Optional high-capability control on informative failures. |
| Mistral hosted API | mistral-small-2603 | $0.15 / $0.60 | Small 4: planned lower-cost hosted open-weight comparison. |
| Mistral hosted API | ministral-8b-2512 | $0.15 / $0.15 | Ministral 3 8B: optional small vision baseline via hosted API. |
| Mistral hosted API | mistral-medium-3-5 | $1.50 / $7.50 | Medium 3.5: planned hosted open-weight control. |
| Mistral hosted API | mistral-large-2512 | $0.50 / $1.50 | Large 3: optional hosted multimodal control. |
| Anthropic | claude-haiku-4-5-20251001 | $1 / $5 | Smaller vision baseline. |
| Anthropic | claude-sonnet-5-5 | $2 / $10 | Broader comparison. |
| Anthropic | claude-opus-5-5 | $4 / $20 | Optional stronger control. |
| Anthropic | claude-fable-5-1 | $10 / $50 | Optional expensive control, not a default. |
| Google | gemini-3.5-flash-lite | $0.30 / $2.50 | Smaller vision baseline. |
| Google | gemini-3.8-flash | $0.75 / $3.75 through 31 Dec 2026 | Published change to $1.50 / $7.50 on 1 Jan 2027; recheck at run time. |
| xAI | grok-4.7 | $2 / $6 | Optional proprietary vision comparison. |

Public documentation snapshot: 1 October 2026 for the original rows; added Mistral rows checked 5 October 2026. Token rates are not price per invoice. Record reasoning/detail settings, usage categories, actual image rendition, retries and requested/returned model versions. An older model is not necessarily cheaper. Only the two Milestone 1 starter profiles have actual runs; no reviewed accuracy ranking exists. This dated shortlist is not proof of current account availability or pricing and was not re-researched during the 6 October handoff refresh.

Sources: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-5.4 nano](https://developers.openai.com/api/docs/models/gpt-5.4-nano), [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [OpenAI model comparison](https://developers.openai.com/api/docs/models/compare), [OpenAI pricing](https://developers.openai.com/api/docs/pricing), [Claude catalogue](https://platform.claude.com/docs/en/models/overview), [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [Grok 4.7](https://docs.x.ai/developers/models/grok-4.7).

### Selection and rollout

5 October priority update: the user wants all shortlisted provider families added as soon as possible, alongside OCR improvements. The latest instruction requires **all credentials upfront before Phase 2 implementation or testing**, using [PHASE2_ACCESS.md](PHASE2_ACCESS.md). [Phase 2 rollout](PHASE2_ROLLOUT.md) is the current queue and requires all samples in every provider evaluation batch. Once the gate is satisfied, do not postpone new families until the first rules pipeline is fully tuned. Stronger/extra model runs remain selected and bounded, and commercial access remains conditional on actual account terms. The earlier per-provider credential order below records the completed Milestone 1 only.

6 October checkpoint: the complete requested access set is supplied. M2 in [ROADMAP.md](ROADMAP.md) now targets representative coverage across every requested provider family, including xAI and Together; additional expensive model variants remain optional/bounded. The active roster is in PHASE2_ACCESS.md. Mindee uses its Invoice model; current inference evidence is recorded in IMPLEMENTATION_STATUS.md. Verify account-specific product, billing, retention and processing settings before calls.

1. Milestone 1: GPT-6 Luna direct image and Mistral OCR 4.1 plus local rules. Configure only the first provider when needed; offline work needs no key. If inaccessible, explicitly record another supported small-model/service choice rather than silently substituting.
2. First wider comparison: GPT-5.4 nano, GPT-4.1 mini, Claude Haiku and Gemini Flash-Lite, plus selected Sol/Sonnet/Flash controls. Do not require every row to run.
3. Add Opus/Fable/Astra/xAI where a concrete question justifies the cost; choose freely per provider.
4. Run direct-image and OCR-text-to-model profiles separately; an image-plus-OCR profile is another experiment, not the same baseline.

5 October user clarification: **open-weight models are welcome when a provider operates inference; self-hosted models are excluded**. The earlier blanket restriction was a mistaken interpretation and is superseded throughout the project. Keep GPT-5.4 nano, GPT-4.1 mini and a selected Sol control in the next bounded matrix, alongside Anthropic candidates. Add Mistral's hosted Small 4 and Medium 3.5; Ministral 3 8B and Large 3 are optional comparisons, not compulsory pairs. Mistral OCR/rules and document annotations remain distinct profiles.

Mistral sources checked 5 October: [Small 4](https://docs.mistral.ai/models/mistral-small-4-0-26-03), [Ministral 3 8B](https://docs.mistral.ai/models/ministral-3-8b-25-12), [Medium 3.5](https://docs.mistral.ai/models/mistral-medium-3-5-26-04), [Large 3](https://docs.mistral.ai/models/mistral-large-3-25-12), [hosted API pricing](https://docs.mistral.ai/inference/pricing). Medium 3.5's open weights do not disqualify its hosted API. Medium 3.1 remains unsuitable for a new baseline because it is deprecated. Verify exact account access, image/schema support, limits, data terms and pricing before dispatch; none of these added profiles has run yet.

Provider-hosted Llama, Qwen, Gemma and other open-weight models are also eligible. Select a concrete managed endpoint and compatible version before adding a profile; availability, modality, retention and price depend on the hosting provider. Record both model identity and actual recipient. No self-hosted model inference on local machines or project-operated cloud/GPU servers, no weight downloads, and no model-serving deployments. Native platform OCR remains a later mobile experiment.

## 3. OCR and document APIs: core comparisons

| Service/profile | Why test it | Price basis and qualification |
| --- | --- | --- |
| Azure Document Intelligence Read | Cloud OCR text/boxes → rules or LLM | F0 advertises 500 pages/month. Paid web rates did not resolve in the retrieved page; use configured tenant/region calculator, not an invented quote. |
| Azure prebuilt Invoice | Structured fields and OCR, raw mapping then augmentation | Same need to verify tier/region price. Published schema includes bank-account/IBAN/SWIFT fields but no dedicated sort-code field in the reviewed list. |
| Google Enterprise Document OCR | Cloud text/layout baseline | $1.50 per 1,000 pages at the published base paid tier. |
| Google Invoice Parser | Prebuilt invoice fields, including supplier IBAN/reference | $0.10 per document of 1–10 pages: one JPEG/PNG document costs $0.10, not $0.01. Separate OCR or augmentation stages may add charges. |
| Mistral OCR 4.1 | OCR text/layout; separate schema annotation profile | Published $4 per 1,000 OCR pages; $5 per 1,000 annotated pages. Record the selected operation and actual billing, not an assumed sum. Annotations include a semantic-model stage and are not an OCR/rules-only baseline. |
| AWS Textract AnalyzeExpense | Prebuilt invoice/receipt extraction | Official US West (Oregon) example: $0.01/page in the first volume tier. This is not a London-region quote. Verify chosen region. |

JPEG/PNG-only application inputs can still be billed as pages by the supplier. Keep the application image-only regardless of the billing unit.

Sources: [Azure invoice model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/invoice?view=doc-intel-4.0.0), [Azure schema](https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/invoice.md), [Azure pricing](https://azure.microsoft.com/en-gb/pricing/details/document-intelligence/), [Google prices](https://cloud.google.com/products/document-ai/pricing), [Google fields/languages](https://docs.cloud.google.com/document-ai/docs/processors-list), [Mistral OCR 4.1 pricing](https://docs.mistral.ai/models/ocr-4-1), [Mistral annotations](https://docs.mistral.ai/studio/document-processing/annotations), [Textract prices](https://aws.amazon.com/textract/pricing/), [AnalyzeExpense API](https://docs.aws.amazon.com/textract/latest/APIReference/API_AnalyzeExpense.html).

Prebuilt “invoice” coverage is not complete payment coverage. Map missing sort codes, Croatian model/reference and absent banking data as missing, then evaluate OCR/rules/LLM augmentation separately. Supported languages vary by processor; general OCR support is not proof of invoice-parser support.

## 4. Commercial extraction and payment products

- **Mindee:** additional invoice/document extraction API candidate. Credit-based plans and overage terms should be confirmed for the selected product/account. The fetched pricing page did not establish an unambiguous currency for every plan figure, so no EUR monthly quote is asserted. [Pricing](https://www.mindee.com/pricing).

The client-owned offering remains meaningful as integration, controllable routing, evidence and deployment choices. It is not a claim that photo-payment is new, every SaaS costs ten cents, or public list rates reflect bank enterprise contracts.

## 5. Local rules and later device processing

Open-source application code and SDKs remain allowed. Local deterministic UK/HR rules, image preparation and supported barcode parsing do not require open-weight inference. invoice2data may be a separately labelled maintained-template comparison over managed OCR text, with AI fallback and model downloads disabled.

Self-hosted PaddleOCR/Docling model pipelines remain excluded. A suitable provider-operated OCR or open-weight-model API may be evaluated after capability, data-term and budget checks. Historical research remains in RESEARCH_AND_AUDIT.md; a shortlist entry does not enable an unimplemented profile. Later iOS platform OCR and mobile quality signals remain planned after design agreement.

## 6. Handoff €500 allocation

A [separate per-option cost report](COST_REPORT_PLAN.md) is required in addition to the findings report. These dated shortlist prices are inputs to verify, not measured per-document costs. Report exact products/models/profiles, account pricing conditions, billing units/minimums, stages/retries, trial credits versus gross usage and unknown charges. Start with M2 evidence, deliver with M4 and refresh for M8.

| Envelope | EUR cap | Purpose |
| --- | --- | --- |
| Direct and hybrid LLM calls | 240 | OpenAI, Claude, Gemini, optional xAI; OCR text/image supplements and rereads. |
| OCR/document services | 130 | Azure, Google, Mistral, Textract, including document minimums. |
| Commercial evaluation | 50 | Trial top-ups only if useful/available; verify the selected product and account terms. |
| Reserve | 80 | VAT/FX, retries, unknown charges and informative reruns. |
| **Total** | **500** | A budget allocation, not a predicted invoice. |

Start with **up to €30 of smoke tests**, drawn from these envelopes, not added on top. Check actual billed usage and adjust the matrix before spending more. Paid commercial subscriptions are not automatically approved; prefer free evaluations and request a choice if entry pricing exceeds the envelope. Self-hosted inference and project GPU rental are outside this PoC. Hosted open-weight calls use the existing LLM or OCR/document envelope as appropriate; the €500 total and €30 first tranche do not increase.

Guardrails: snapshot enabled profiles; show images × variants × profiles × repeats; cap calls/output and concurrency; reserve worst-case estimates where available; reconcile provider dashboards; stop before uncertain charges could exhaust the remaining budget. Estimates alone cannot guarantee the final supplier invoice. Free quota may be shared or exhausted.

For illustration only: 13 documents × 3 image variants × 8 profiles × 3 repeats = 936 profile runs, not necessarily 936 API calls. A profile can have several stages/retries; the independence of the original documents still needs verification. Do not turn this illustration into a compulsory matrix.

## 7. Why image size matters

Visual-token billing is model-specific: dimensions, detail and resize/patch/tile policies matter. JPEG byte size alone is not the bill. OCR text, output/reasoning, crops and rereads also count. A lower-resolution image can save tokens but lose a payment digit; test both outcomes. Document services may instead charge a page/image or document minimum.

Store rendition dimensions/bytes/hash, detail mode and actual usage. As a purely hypothetical calculation, 4,000 input tokens plus 1,000 output tokens at $2/$10 per million is $0.018; this is not a measured invoice-scan cost and excludes other stages/retries. [OpenAI image cost guide](https://developers.openai.com/api/docs/guides/image-cost-calculator).

## 8. Data destination and access checks

For every stage record provider/service, endpoint host, configured account/region, payload (image/crop/text/boxes/fields), input hash, request ID and local artifact location. Do not equate a regional endpoint with a verified end-to-end residency guarantee. Display unknown when unknown.

Cloud OCR sends images; OCR-plus-cloud-LLM can send text/layout instead of or alongside the image; multi-vendor profiles disclose every recipient. Text can still include personal/banking data. Local processing requires checking that no remote fallback is enabled.

The user permits sample testing. Before live calls, verify account-specific data-use/retention settings and paid/free tier differences—for example Gemini's published page distinguishes these tiers. Do not promise universal no-training/no-retention. Keep credentials server-side and do not use provider responses or document text as instructions.
