# Providers and extraction profiles

A profile is a versioned processing recipe: provider/model or processor, request options, prompt/schema, mapping/rules, review policy and accounting/data-destination metadata. Multiple models from one provider remain distinct choices. The live catalogue is authoritative for currently configured/enabled choices; a name in source is not an account-access guarantee.

## Implemented integrations

| Provider | Available integration families |
| --- | --- |
| OpenAI | Direct image models; OCR-text interpretation |
| Gemini | Direct image models |
| Mistral | Direct image models, OCR + rules, OCR/schema annotations; OCR stage for hybrids |
| Anthropic | Direct image models |
| Together | Hosted open-weight vision models |
| xAI | Direct image models with separately recorded reported charges |
| Google Document AI | OCR and Invoice Parser |
| Azure Document Intelligence | Read and Invoice |
| AWS Textract | Text and Expense |
| Mindee | Structured invoice extraction |

Fireworks and Cohere Aya are not supported by the active implementation. Example presets are in `providers.example.json` and `providers.expanded.example.json`; they contain no configured credentials and do not enable themselves.

## Selection and request snapshots

The admin and SUNMI **Next scan** controls share the same persisted selection. A new phone Send reads its exact profile ID/version, verifies readiness and freezes that reference with the request. Existing scans and pending recovery do not adopt a new default.

Extract runs one profile. Compare resolves explicit profile IDs or `all_enabled` into an immutable eligible roster. Disabled, missing, unconfigured or image-incompatible explicit choices fail before dispatch. Compare returns independent results, with no vote or automatic winning result. No provider fallback or substitution is hidden in a method.

Compatible compact LLM definitions include document country/language context as standard. Account-country evidence and actual payment-route guidance remain separate. Local rules decide field applicability; model explanations are labelled claims, not independent verification.

## Readiness and endpoints

Enablement requires supported configuration, credentials, model/resource access and recorded account/data-terms checks. Pricing dates/per-call ceilings are optional accounting metadata. Local spending/cumulative-call limits are not enforced. Queue capacity, authentication, supported endpoints and idempotency still apply.

Supported OpenAI hosts include `api.openai.com`, `eu.api.openai.com` and `us.api.openai.com`; Mistral supports `api.mistral.ai` and `api.eu.mistral.ai`. Regional routes are explicitly configured, not selected automatically. Google Document AI uses the processor's configured location/version. Providers can reject requests for account or model reasons; the backend preserves that failure without switching endpoints.

A regional hostname, account headquarters or open-weight licence does not establish processing residency. Unknown residency remains unknown. Account retention/training controls must be checked for the exact service; `store=false` on supported OpenAI requests is not a universal zero-retention guarantee. Credentials are described in [setup](SETUP.md).

## Results and failures

| Result | Meaning |
| --- | --- |
| `success` | Useful draft passed the selected completeness/review policy; factual accuracy still needs review |
| `incomplete` | Request produced recoverable fields with missing/uncertain requirements |
| `error` | No usable invoice/payment fields or failed processing; OCR text alone is insufficient |
| Provider error code | Authentication, quota, timeout, refusal, availability or output failure recorded for that run |

API completion, draft completeness and extraction correctness are different measurements. A timeout does not establish bad credentials or prove upstream processing stopped. Invalid individual fields can be quarantined while recoverable observations remain visible under the selected partial-field policy.

Existing evidence gaps, not newly tested in this guide: Haiku 4.5 has a retained availability/connection failure, Mistral Large 4 has a retained timeout, and two AWS processing profiles have authenticated but untested processing. These are latest recorded outcomes, not claims of current provider outage. Google OCR/Invoice have completed processing evidence.

## Accounting and destinations

Each external stage records the actual recipient, configured/verified region, payload class, requested/returned model, timing, usage and request identifier where available. Hybrids record each stage separately and add their costs/latencies.

Use provider-reported charges where supported, otherwise explicit saved tariffs and observed usage. Missing usage/pricing/failure charges remain unknown; do not convert them to zero. Internal conservative holds are not provider invoices, and tax/FX/account credits require separate evidence. Grok's opt-in reported-cost profile uses `cost_in_usd_ticks / 10^10`; missing ticks means unknown and malformed values fail rather than double-count reasoning.

Fresh provider runs need a saved complete input/profile/repeat plan, new stable keys and explicit outcome coverage. See [evaluation](EVALUATION.md).
