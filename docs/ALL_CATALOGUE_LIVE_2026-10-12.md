# All catalogue profiles — 12 October 2026

Markus requested every supported entry enabled and run on the verified barcode-free Croatian invoice. The private runtime has **37 enabled/configured profiles across 12 providers**. No profile is disabled because a request fails. Source example presets remain credential-free opt-in templates; their defaults do not represent the enabled private runtime.

This is a fresh one-invoice compatibility run, separate from the stopped 9 October comparison and the completed 19-model run. Input is the inspected full-resolution invoice; metadata-free PNG reencoding preserves every RGB pixel. Evidence and frozen keys/snapshots are private under `.local/all-catalogue-2026-10-12/run-20261012T224905Z/` in the original checkout. No raw invoices, banking data or credentials belong in Git.

## Restored and added choices

Restored: Google Document AI OCR and Invoice, AWS Textract text and Expense, Azure Read and Invoice, Mindee Invoice, Mistral annotations, Grok, the OCR→OpenAI hybrid and two legacy built-in profiles. Existing profiles and the selected exact GPT-4.1 mini profile are retained. New presets add Fireworks DeepSeek V4.1 Flash, GLM 5.3 Flash and Llama 4 Maverick, plus Cohere Aya Vision 32B.

The authenticated Fireworks catalogue reports image input and serverless support for DeepSeek/GLM. Llama and Kimi K2.5 report image input but no serverless support: entries remain enabled and gateway failures are retained; no dedicated deployment, subscription or GPU service is created. Account/model readiness is distinct from the local enabled/configured flags.

Cohere uses fixed `api.cohere.com/v2/chat`, the root `COHERE_API_KEY`, inline image input and prompt-contained compact schema, with local typed validation. Aya native schema support is not assumed. Refusal, tools, unknown content and incomplete generation fail explicitly. Cohere price accounting uses `usage.billed_units`; total token counters stay separate. Aya's account-specific tariff, training setting and residency remain unknown. [Cohere's data commitments](https://cohere.com/enterprise-data-commitments) explain dashboard opt-out and normal 30-day prompt/generation retention with exceptions; no account-specific ZDR is claimed.

Grok has a new opt-in accounting profile, leaving historic configurations and results immutable. Its USD charge uses `usage.cost_in_usd_ticks / 10^10`, as documented by [xAI](https://docs.x.ai/developers/cost-tracking), which includes reasoning charges. Missing ticks mean unknown cost; reasoning tokens are not charged twice. Invalid ticks fail validation. No estimate silently replaces a missing reported charge.

## Bounds and execution

At the final preparation snapshot the original ledger contained 2,304 dispatched reservations / EUR359.05 holds, including an intervening mobile scan. The new plan adds up to **38 stage calls / EUR10.55**: one request per profile, with two external stages for the hybrid. Cumulative limits are **2,350 calls / EUR370.40**, below EUR500. The eight-call/EUR0.80 headroom at that final snapshot was preserved; skipped AWS reservations remain unused. Holds are conservative ceilings, not actual provider bills. Unknown deployment/model prices and timeout charges remain unknown.

Stable keys and frozen versions are persisted before each submission. Two independent jobs run concurrently; each stage has a 90-second timeout. Provider failures remain independent; local authentication, budget or uncertain submission/polling stops dispatch. No inference retry/fallback or historical batch resumption. Markus subsequently requested skipping AWS for now. Both AWS profiles remain enabled and were explicitly skipped before any submission. For a future run, renew the existing `scanpay` session with `aws login --profile scanpay --region eu-central-1`; the IAM username recorded and previously verified by STS is `scanpay-local`.

## Verification

**747 offline tests passed**. Domain/orchestration coverage: **96.09% statements / 91.53% branches**. Ruff lint/format, strict mypy, coverage gate and generated-contract checks passed. New tests cover Cohere requests/parsing/billed units and xAI reported ticks, malformed/missing charge handling, zero charges and reasoning double-count prevention. Synthetic tests establish code behavior; live compatibility and extraction outcomes are recorded separately below. No aggregate accuracy claim is warranted by a single invoice.

## Live outcomes

**Completed: 35 profiles attempted; AWS’s two entries skipped at Markus’s request.** Outcomes: **12 success, 15 incomplete, 8 error**. Success is schema/review readiness, not verified invoice accuracy. All 37 catalogue flags remain enabled/configured. No accepted/completed request was resubmitted when AWS was excluded; accepted jobs were recovered by GET before continuing only unsent profiles.

There were **34 external dispatches** and **36 budget reservations / EUR10.25 holds**. The hybrid has two external stages. Google’s two authentication failures happened before dispatch; their conservative reservations remain in the ledger. Accounting includes stage-suffixed hybrid budget keys. The final snapshot has **2,340 reservations, 2,338 dispatched / EUR369.30 held**; caps 2,350 / EUR370.40 leave 10 reservations / EUR1.10. Every original ledger row, persisted selection and backend identity matched the pre-run snapshot.

Known list-price estimates total **USD0.39105568**; Grok separately reports **USD0.02706**. Actual aggregate provider billing is unknown, including timeout/availability failures and options without verified tariffs. Cohere failed as provider_unavailable; Llama/Kimi K2.5 returned HTTP404. Both Google entries failed pre-dispatch authentication, although a later read-only credential refresh succeeded; they were not resubmitted. All failures remain enabled and recorded.

Backend stage totals below have n=1 per profile and exclude mobile capture/upload/rendering. Do not infer median/p95 or a correctness ranking from this compatibility run.

| Profile/model | Outcome | Backend seconds | Error |
| --- | --- | ---: | --- |

| `gpt-6-luna` | success | 12.283 | — |
| `mistral-ocr-rules` | incomplete | 3.845 | — |
| `gpt-4.1-mini-2025-04-14` | incomplete | 13.501 | — |
| `gemini-3.5-flash-lite` | incomplete | 5.922 | — |
| `mistral-small-2603` | incomplete | 5.379 | — |
| `claude-haiku-4-5-20251001` | error | 62.578 | provider_unavailable |
| `Qwen/Qwen3.5-9B` | incomplete | 8.892 | — |
| `mistral-ocr-rules3-draft-v1` | incomplete | 4.678 | — |
| `gpt-6-luna` | success | 5.469 | — |
| `gpt-6.1-sol` | success | 10.144 | — |
| `gpt-6-astra` | success | 8.953 | — |
| `gemini-3.8-flash` | success | 33.017 | — |
| `gemini-3.1-pro-preview` | incomplete | 23.011 | — |
| `claude-haiku-5-5` | success | 11.474 | — |
| `claude-sonnet-5-5` | success | 7.311 | — |
| `claude-opus-5-5` | success | 7.369 | — |
| `mistral-medium-2604` | incomplete | 7.827 | — |
| `mistral-large-4` | error | 90.005 | provider_timeout |
| `ministral-8b-2512` | incomplete | 10.626 | — |
| `moonshotai/Kimi-K3` | success | 50.0 | — |
| `MiniMaxAI/MiniMax-M3` | incomplete | 7.099 | — |
| `accounts/fireworks/models/kimi-k2p5` | error | 1.218 | invalid_provider_output |
| `accounts/fireworks/models/kimi-k3` | error | 90.001 | provider_timeout |
| `google-ocr-rules` | error | 0.0 | provider_auth |
| `aws-text-rules` | skipped | — | user_requested_aws_skip |
| `aws-expense` | skipped | — | user_requested_aws_skip |
| `mindee-invoice` | incomplete | 6.274 | — |
| `azure-read-rules-paced` | incomplete | 13.023 | — |
| `azure-invoice-paced` | incomplete | 74.057 | — |
| `google-invoice-mapping-v2` | error | 0.0 | provider_auth |
| `mistral-annotations-compact-v5` | incomplete | 8.258 | — |
| `grok-4.7` | success | 30.827 | — |
| `accounts/fireworks/models/deepseek-v4p1-flash` | success | 28.494 | — |
| `accounts/fireworks/models/glm-5p3-flash` | success | 60.904 | — |
| `accounts/fireworks/models/llama4-maverick-instruct-basic` | error | 1.088 | invalid_provider_output |
| `c4ai-aya-vision-32b` | error | 75.206 | provider_unavailable |
| `gpt-4.1-mini-2025-04-14` | incomplete | 6.071 | — |
