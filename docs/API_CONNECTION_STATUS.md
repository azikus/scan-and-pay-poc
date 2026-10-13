# Provider API status — 13 October 2026

**Main integration — 13 October:** Latest `main` is merged into this provider branch, retaining PR #8’s glass/hotspot/Send changes and PR #7’s European endpoint support and approved removal of local spending/cumulative-call enforcement. Legacy budget-plan/cost records below remain historical evidence; they do not control admission in the updated source. This integration does not restart the live service, alter private configuration/selection or authorize provider retries.


The current criterion is whether an API request completes, independently of extraction completeness or correctness. **31 profiles remain enabled/configured across 10 providers:** 27 completed their latest tested request without API errors, two retain an unresolved last-request failure, and two AWS profiles have verified authentication but untested processing. Fireworks and Cohere Aya were removed at Markus’s request; their historical results remain recorded separately.

## Remaining request failures

| Profile | Last result | Interpretation |
| --- | --- | --- |
| Claude Haiku 4.5 | `provider_unavailable`, 62.578 seconds | Upstream availability or connection failure. No HTTP status/raw response retained for that failure, so exact cause unknown. Haiku 5.5 completed with the same provider access; not evidence of a broken Anthropic account. |
| Mistral Large 4 | `provider_timeout`, 90.005 seconds | Request exceeded the bounded stage timeout; not evidence of bad credentials. Other Mistral profiles completed. |

Both remain enabled. Neither was retried after the failed request. These are dated observed failures, not proof that the provider is currently down.

## Resolved and untested access

Google Document AI OCR and Invoice both passed exact runtime authentication/resource checks and subsequently completed actual processing requests on the approved invoice, in 7.059 and 8.207 seconds. Both produced incomplete drafts requiring review; these are successful API requests. No code or replacement credentials were needed; the earlier pre-dispatch authentication failure’s cause remains unknown. See [Google verification](GOOGLE_VERIFICATION_2026-10-13.md).

AWS’s `scanpay` SDK profile now uses the access key that Markus configured. Read-only STS verified `scanpay-local` in `eu-central-1`. Textract Text and Expense were previously skipped at his request; neither has a new processing result. Authentication success does not establish Textract permissions, processing compatibility or invoice extraction success. The subsequent env-credential follow-up verified the same AWS identity with explicit .env keys and both Google processor versions using inline credential JSON, with native auth-store lookup blocked. Legacy SDK fallback is retained only if explicit env credentials are absent; see [env authentication](ENV_CLOUD_CREDENTIALS.md).

## Latest evidence for every current profile

“Completed without API error” includes incomplete drafts; all drafts need review. These are one-invoice compatibility observations, not correctness or reliability benchmarks. Most results are from the 12 October catalogue run; Google’s follow-up and AWS’s read-only authentication were verified on 13 October. Older failures and retired profiles remain in [the historical catalogue report](ALL_CATALOGUE_LIVE_2026-10-12.md).

| Provider | Profile | Requested model/processor | Latest API evidence |
| --- | --- | --- | --- |
| openai | `openai-luna-vision` | `gpt-6-luna` | Completed without API error; draft marked `success` |
| mistral | `mistral-ocr-rules` | `mistral-ocr-4-1` | Completed without API error; incomplete draft |
| openai | `openai-mini-image-roles-v3` | `gpt-4.1-mini-2025-04-14` | Completed without API error; incomplete draft |
| gemini | `gemini-flash-lite-image-roles-v3` | `gemini-3.5-flash-lite` | Completed without API error; incomplete draft |
| mistral | `mistral-small-image-roles-v3` | `mistral-small-2603` | Completed without API error; incomplete draft |
| anthropic | `anthropic-haiku-image-roles-v3` | `claude-haiku-4-5-20251001` | Last request failed: `provider_unavailable` |
| together | `together-qwen-image-roles-v3` | `Qwen/Qwen3.5-9B` | Completed without API error; incomplete draft |
| mistral | `mistral-ocr-rules3-draft-v1` | `mistral-ocr-4-1` | Completed without API error; incomplete draft |
| openai | `openai-luna-expanded` | `gpt-6-luna` | Completed without API error; draft marked `success` |
| openai | `openai-sol-expanded` | `gpt-6.1-sol` | Completed without API error; draft marked `success` |
| openai | `openai-astra-expanded` | `gpt-6-astra` | Completed without API error; draft marked `success` |
| gemini | `gemini-flash-expanded` | `gemini-3.8-flash` | Completed without API error; draft marked `success` |
| gemini | `gemini-pro-expanded` | `gemini-3.1-pro-preview` | Completed without API error; incomplete draft |
| anthropic | `anthropic-haiku-expanded` | `claude-haiku-5-5` | Completed without API error; draft marked `success` |
| anthropic | `anthropic-sonnet-expanded` | `claude-sonnet-5-5` | Completed without API error; draft marked `success` |
| anthropic | `anthropic-opus-expanded` | `claude-opus-5-5` | Completed without API error; draft marked `success` |
| mistral | `mistral-medium-expanded` | `mistral-medium-2604` | Completed without API error; incomplete draft |
| mistral | `mistral-large-expanded` | `mistral-large-4` | Last request failed: `provider_timeout` |
| mistral | `mistral-ministral-expanded` | `ministral-8b-2512` | Completed without API error; incomplete draft |
| together | `together-kimi-expanded` | `moonshotai/Kimi-K3` | Completed without API error; draft marked `success` |
| together | `together-minimax-expanded` | `MiniMaxAI/MiniMax-M3` | Completed without API error; incomplete draft |
| google_documentai | `google-ocr-rules` | `pretrained-ocr-v2.1-2024-08-07` | Completed without API error; incomplete draft |
| aws | `aws-text-rules` | `DetectDocumentText` | Authentication verified; processing untested |
| aws | `aws-expense` | `AnalyzeExpense` | Authentication verified; processing untested |
| mindee | `mindee-invoice` | `invoice-custom-20261006` | Completed without API error; incomplete draft |
| azure | `azure-read-rules-paced` | `prebuilt-read` | Completed without API error; incomplete draft |
| azure | `azure-invoice-paced` | `prebuilt-invoice` | Completed without API error; incomplete draft |
| google_documentai | `google-invoice-mapping-v2` | `pretrained-invoice-v2.0-2023-12-06` | Completed without API error; incomplete draft |
| mistral | `mistral-annotations-compact-v5` | `mistral-ocr-4-1` | Completed without API error; incomplete draft |
| xai | `xai-grok-image-roles-v3-cost-reported` | `grok-4.7` | Completed without API error; draft marked `success` |
| Mistral → OpenAI | `mistral-ocr-openai-text-roles-v3` | `gpt-4.1-mini-2025-04-14` | Completed without API error; incomplete draft |

## Preservation and validation

Historical provider-verification snapshot (before context migration and later user scans): **2,342 reservations, 2,340 dispatched / EUR369.60 held**. Legacy plan metadata remains **2,350 reservations / EUR370.40**, with the historical eight-reservation/EUR0.80 difference. The merged source does not enforce these figures; this source integration does not restart the active process. Holds are not actual provider bills. Selected profile at that checkpoint was `openai-mini-image-roles-v3@2-5094b6dc13ef5718`; standard context later migrated it to `@2-85c414059effa4ad` (see CURRENT_STATUS.md). there were no active jobs at the documentation snapshot.

This documentation update made no inference calls, runtime/configuration changes or ledger edits. Original private evidence stays ignored. The earlier status-only update used the 715-test checkpoint. After integrating latest main, the combined source passed **730 offline backend/evaluation tests**, **96.09% statement / 91.41% branch coverage**, and **27 native unit/recovery plus four synthetic UI tests**. Static, schema, packaging and presentation checks passed. No paid calls ran during integration. Do not automatically retry failed profiles, resume stopped historical comparisons or change private accounting records.
