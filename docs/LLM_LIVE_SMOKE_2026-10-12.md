# Paid single-invoice LLM smoke check — 12 October 2026

Markus explicitly requested a paid invoice extraction with all models. The completed corrected run used one visually verified, barcode-free Croatian invoice at its full 2481 × 3508 resolution, with identical pixels across all 19 enabled direct-image LLM profiles. Every model made one external attempt; no retries or fallback ran. OCR/rules, the two-stage hybrid and inactive models were outside this model-only scope. This is a single-invoice compatibility check, not a full-corpus benchmark.

## Outcomes

**13 successful drafts, four incomplete drafts and two provider timeouts.** Seventeen HTTP 200 responses were retained; the two timeouts returned no response within the 90-second boundary. Successful drafts satisfy current backend completeness rules and still require user review; they do not prove correct payment values.

| Recipient | Requested model | Outcome | Provider stage (s) | Reviewed beneficiary matched |
| --- | --- | --- | ---: | --- |
| gemini | `gemini-3.5-flash-lite` | Incomplete | 3.589 | Yes |
| openai | `gpt-4.1-mini-2025-04-14` | Success | 4.711 | No |
| anthropic | `claude-sonnet-5-5` | Success | 5.073 | Yes |
| mistral | `mistral-medium-2604` | Incomplete | 5.198 | No |
| anthropic | `claude-opus-5-5` | Success | 5.948 | Yes |
| openai | `gpt-6-luna` | Success | 6.306 | No |
| mistral | `mistral-small-2603` | Incomplete | 6.572 | No |
| anthropic | `claude-haiku-4-5-20251001` | Success | 7.617 | No |
| together | `MiniMaxAI/MiniMax-M3` | Success | 7.680 | No |
| together | `Qwen/Qwen3.5-9B` | Success | 9.316 | No |
| openai | `gpt-6.1-sol` | Success | 9.469 | Yes |
| openai | `gpt-6-astra` | Success | 10.210 | Yes |
| anthropic | `claude-haiku-5-5` | Success | 11.523 | Yes |
| gemini | `gemini-3.8-flash` | Success | 22.421 | Yes |
| gemini | `gemini-3.1-pro-preview` | Incomplete | 23.536 | No |
| fireworks | `accounts/fireworks/models/kimi-k3` | Success | 75.729 | No |
| together | `moonshotai/Kimi-K3` | Success | 85.614 | Yes |
| mistral | `ministral-8b-2512` | Timeout | 90.001 | — |
| mistral | `mistral-large-4` | Timeout | 90.010 | — |

Each timing has **n=1** and measures the backend provider/adapter stage. It excludes phone capture, upload, queue and UI rendering. Concurrency was bounded to two; no latency distribution or cross-invoice speed ranking follows from this run.

The unchanged human-reviewed r4 key has only **one confirmed field for this invoice: beneficiary name**. Eight models matched that frozen field; 17 pending fields remain excluded for each model. “No” means the linked-option scorer did not establish a match, including unmatched/inferred/ambiguous outputs; it is not a claim that the model omitted all recipient names. No new labels, fuzzy aliases or bank-digit allowances were invented. Do not interpret the successful-draft count as whole-invoice accuracy.

## Accounting and preservation

The correct invoice run made **19 dispatched reservations / EUR5.05 held**. Known gross list-price token estimates total **USD0.51817388**; the two timeout charges remain unknown, so this is not the complete provider bill. Conservative EUR holds and USD estimates are different records.

Before that corrected run, the agent incorrectly assumed the latest mobile upload was an invoice and dispatched seven requests on a desk photograph. Further submissions were stopped once the image was inspected. All seven returned zero usable invoice/payment fields. Those requests remain separately recorded as non-invoice evidence: **seven calls / EUR1.55 held**, known gross token estimates **USD0.11497305**, actual provider bills unknown. They are not counted in the 19-model invoice table. Markus explicitly approved adding seven calls / EUR1.55 to account for this mistake and complete the corrected run while preserving the mobile allowance.

The original ledger rows were compared by ID and full row contents and preserved. The final read-only ledger snapshot is **2,303 dispatched reservations / EUR358.95 held**. User-approved cumulative caps are **2,312 / EUR359.85**, leaving the original explicit-mobile-Send headroom of **nine calls / EUR0.90**. Current GPT-4.1 mini selection and its exact version were preserved. The private backend remains running from the provider worktree. No subscription, deployment, token rotation, original image edit, historical batch resumption or further paid retry occurred.

Private plans, exact profile/version roster, keys, original ledger snapshots, input hashes, all raw/model results and aggregate summary are under the original checkout’s ignored `.local/live-all-models-2026-10-12/`. The first stopped run and corrected run have separate state files and immutable result identities. No invoice pixels or payment values are included in this document.

This paid follow-up supersedes the earlier offline-only scope for this completed bounded run. Remaining allowance is for explicit mobile Sends; another agent run or timeout retry needs new authorization.
