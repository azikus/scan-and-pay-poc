# Provider API status — 13 October 2026

The current criterion is whether an API request completes, independently of extraction completeness or correctness. **31 profiles remain enabled/configured across 10 providers:** 27 completed their latest tested request without API errors, two retain an unresolved last-request failure, and two AWS profiles have verified authentication but untested processing. Fireworks and Cohere Aya were removed at Markus’s request; their historical results remain recorded separately.

## Remaining request failures

| Profile | Last result | Interpretation |
| --- | --- | --- |
| Claude Haiku 4.5 | `provider_unavailable`, 62.578 seconds | Upstream availability or connection failure. No HTTP status/raw response retained for that failure, so exact cause unknown. Haiku 5.5 completed with the same provider access; not evidence of a broken Anthropic account. |
| Mistral Large 4 | `provider_timeout`, 90.005 seconds | Request exceeded the bounded stage timeout; not evidence of bad credentials. Other Mistral profiles completed. |

Both remain enabled. Neither was retried after the failed request. These are dated observed failures, not proof that the provider is currently down.

## Resolved and untested access

Google Document AI OCR and Invoice both passed exact runtime authentication/resource checks and subsequently completed actual processing requests on the approved invoice, in 7.059 and 8.207 seconds. Both produced incomplete drafts requiring review; these are successful API requests. No code or replacement credentials were needed; the earlier pre-dispatch authentication failure’s cause remains unknown. See [Google verification](GOOGLE_VERIFICATION_2026-10-13.md).

AWS’s `scanpay` SDK profile now uses the access key that Markus configured. Read-only STS verified `scanpay-local` in `eu-central-1`. Textract Text and Expense were previously skipped at his request; neither has a new processing result. Authentication success does not establish Textract permissions, processing compatibility or invoice extraction success. Credentials stay SDK-managed; root `.env` selects the profile and region.

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

Current read-only snapshot: **2,342 reservations, 2,340 dispatched / EUR369.60 held**. Caps remain **2,350 reservations / EUR370.40**, leaving eight reservations / EUR0.80 in the existing mobile allowance. Holds are not actual provider bills. Selected profile remains `openai-mini-image-roles-v3@2-5094b6dc13ef5718`; there were no active jobs at the documentation snapshot.

This documentation update made no inference calls, runtime/configuration changes or ledger edits. Original private evidence stays ignored. Source checks remain the prior **715 passing offline tests**, **96.07% statement / 91.37% branch coverage**; no code changed or tests reran for this update. Do not automatically retry failed profiles, resume stopped historical comparisons or extend caps.
