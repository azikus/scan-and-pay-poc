# Milestone 1 provider checks

Handoff note, 6 October: this file preserves the two implemented providers' measured integration baseline. Broader-provider credential/resource preparation is in [PHASE2_ACCESS.md](PHASE2_ACCESS.md), and the next implementation tasks are in [CODING_HANDOFF.md](CODING_HANDOFF.md). Access preparation does not add live-validated profiles or replace the historical runs below.

Public documentation rechecked 5 October 2026. Both locally configured keys authenticated and the exact requested models were available. Milestone 1 now has real UK/HR runs through both profiles and a successful two-provider comparison. [Implementation status](IMPLEMENTATION_STATUS.md) records all twelve dispatches, including failures. The Mistral billing/privacy checks below were verified separately in the signed-in Admin UI; access checks alone do not establish those settings. Processing residency, retention and negotiated billing remain unknown.

## OpenAI direct image

Requested model is exactly `gpt-6-luna`; no substitution or model auto-selection. Official documentation confirms image input and structured outputs. The adapter uses the official `openai` Python SDK, Responses, a generated strict JSON schema, `store=false`, no tools, `reasoning.effort=none`, high image detail, 12,000 maximum output tokens, 90 seconds and zero automatic retries. Canonical PNG travels to the configured allowlisted OpenAI host. [Model](https://developers.openai.com/api/docs/models/gpt-6-luna), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [image inputs](https://developers.openai.com/api/docs/guides/images-vision).

Published standard rates used for **estimates**: USD $0.10 ordinary input, $0.01 cached input, $0.125 cache writes and $0.50 output per million tokens. Cache-write tokens replace ordinary input billing for those tokens; they are not an additive charge. Prompts over 272K input tokens use twice the input/cache rates and 1.5 times the output rate. The adapter explicitly requests the default service tier, records cache-write usage, and leaves cost unknown when that category is absent. Output includes reasoning tokens when present. No actual invoice amount, tax, negotiated price or FX conversion is claimed. Regional processing premiums are not inferred from an unverified account setting. The documented request limit is 512 MB. [Model pricing](https://developers.openai.com/api/docs/models/gpt-6-luna), [cache usage](https://developers.openai.com/api/docs/guides/prompt-caching).

`store=false` does not establish zero retention. Official data-control documentation describes abuse-monitoring retention and image-specific exceptions; regional eligibility and account controls need verification. Record unknown processing residency as null. No account setting is inferred from the hostname. [Data controls](https://developers.openai.com/api/docs/guides/your-data).

`OPENAI_API_KEY` is now configured privately in `.env`. Exact model access was verified without inference on 5 October, and `.local/providers.json` records the check and public terms/pricing review. Account-specific settings are explicitly unknown. The service does not probe these at startup.

## Mistral OCR and local rules

The documented API identifier is **`mistral-ocr-4-1`**, for OCR 4.1. This clarifies the wire name, not a provider substitution. The adapter posts an inline canonical PNG to `https://api.mistral.ai/v1/ocr` using HTTPX; it does not invoke document annotations or another semantic model. It records OCR text/layout hashes and a separate local rules stage. General UK/HR label and paragraph-position rules preserve linked candidates. OCR paragraph boxes are retained in the raw response but are not invented or treated as verified field boxes in v1. [Model](https://docs.mistral.ai/models/ocr-4-1), [OCR endpoint](https://docs.mistral.ai/api/endpoint/ocr), [image request/response guide](https://docs.mistral.ai/studio/document-processing/basic_ocr).

The published OCR rate is $4 per 1,000 pages; usage-based estimates use $0.004 per reported page and remain USD. The provider documents a 20 MB image limit; it is checked against the canonical rendition before acceptance. No arbitrary application upload cap is introduced. [Pricing](https://docs.mistral.ai/models/ocr-4-1), [platform image limits](https://docs.mistral.ai/resources/known-limitations).

`MISTRAL_API_KEY` is configured locally; the exact OCR model was present in the authenticated catalogue. The user funded the account and disabled API training. Signed-in Admin checks confirmed API training and Labs off, a positive credit balance and auto-recharge disabled. API pay-as-you-go was still disabled despite that credit; after explicit user approval, terms were accepted and activation was submitted. Admin then showed pay-as-you-go Active, and both OCR images succeeded. No further credit purchase or key rotation was needed. Training was rechecked and remained off. Public EU-hosting descriptions allow some subprocessor transfers and do not establish this account's processing residency. Retention and negotiated prices remain unknown. [Training controls](https://help.mistral.ai/en/articles/455207-can-i-opt-out-of-my-input-or-output-data-being-used-for-training), [data hosting](https://help.mistral.ai/en/articles/347629-where-do-you-store-my-data-or-my-organization-s-data).

## Bounded live starter execution — 5 October 2026

The initial plan allowed six calls: individual UK/HR vision and OCR runs, followed by one two-provider comparison. Observed failures paused the affected integration and required explicit new runs after fixes; no automatic retries or substitutions occurred. Subsequent bounded revisions retained the same ledger:

1. Five initial dispatches: four vision attempts (including one v1-format failure) and one OCR HTTP 429.
2. Three follow-up dispatches: UK comparison with OCR HTTP 429 and vision success, then HR vision-only after stopping the OCR batch. The shared `review@2` fix succeeded on both images.
3. Two OCR-only dispatches after authorized API billing activation: UK and HR completed.
4. Two final dispatches in one HR comparison: both profiles completed, independently, with `final_result_id=null`.

**Total: twelve requests, each with one attempt; €12 in retained €1 reservations**, within the initial €30 tranche. Published usage-based estimates total USD $0.020467925: $0.008467925 for seven OpenAI calls and $0.012 for three successful OCR pages. Two failed OCR charges remain unknown. Neither prepaid account credit nor EUR holds are claimed as actual per-request costs or FX conversions. The twelve-call cap is exhausted; record another bounded plan before any further testing. The temporary API was stopped cleanly. Shipped provider examples remain disabled; local starter profiles are configured and live-validated.

The original HR vision failure exposed a mismatch between the provider's generated output schema and the existing v1 amount-format constraint. `payment-image@2` shares that constraint and retains the printed text. `review@2` fixes false ambiguity from bank-field labels and equivalent country formatting, without accepting digit changes. Previous stored results remain immutable.

Both pre-activation Mistral attempts failed with HTTP 429; the second private body reports `rate_limited`, code `1300`. A credit top-up alone does not change API limits. Pay-as-you-go activation resolved the observed blocker for these subsequent runs. [Mistral rate-limit guidance](https://help.mistral.ai/en/articles/698531-why-am-i-hitting-api-rate-limits-and-how-do-i-increase-them). Private account evidence and revised plans remain in `.local/live-2026-10-05/`; no credentials appear in those records.

Inputs: `samples/variants/uk-continental-reference.png` and `samples/racun-12793-26-no-barcode.png`. They are rasterized references, not camera photos. Results stay separate from private draft labels, which remain unscored. OpenAI's HR result is ready for review; UK requires an amount-role decision. Mistral's raw OCR contains payment text, but the initial local rules miss multi-column totals and prose references, and blank paragraphs split the UK bank pair into incomplete candidates. Preserve these baseline gaps for later versioned rules/annotation experiments; no hidden LLM augmentation or model-agreement truth claim.

## Runtime dependency licences

Installed metadata reviewed; exact versions are in `requirements.lock`. No SDK source was copied, no model weights were installed, and historical `reference/phase1` is untouched.

| Dependency | Tested version | Licence |
| --- | --- | --- |
| FastAPI | 0.142.2 | MIT |
| Pydantic | 2.13.5 | MIT |
| Uvicorn | 0.54.0 | BSD-3-Clause |
| Pillow | 12.3.0 | MIT-CMU |
| HTTPX | 0.28.1 | BSD-3-Clause |
| OpenAI SDK | 2.54.0 | Apache-2.0 |
| python-multipart | 0.0.32 | Apache-2.0 |
| python-dotenv | 1.2.4 | BSD-3-Clause |
| schwifty | 2026.7.3 | MIT |
| pycountry | 26.2.16 | LGPL-2.1-only |

schwifty supplies IBAN format/checksum checks only; no bank-ownership, account-existence or Confirmation of Payee claim is made. pycountry supplies ISO currency codes and normalization of explicit country names/codes. Their installed libraries remain separate dependencies, not copied implementation code.

## Cleanup and next evaluation — 6 October 2026

No new inference or account changes occurred during the main-checkpoint cleanup. The two starter integrations and their dated measurements remain the only live-tested profiles. Every new provider evaluation must cover all samples and feed the separate [cost report](COST_REPORT_PLAN.md), with exact product/profile versions, account-specific tariff checks, stage/retry usage and unknown charges. Access preparation is not processing validation.
