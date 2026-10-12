# LLM expansion — 12 October 2026

Markus requested broader LLM coverage and more choices from existing providers in a separate worktree. Implementation is isolated on `codex/llm-provider-expansion`, based on the merged presentation checkpoint `75c8cd0`. The separate uncommitted iOS work remains in its original checkout. No inference, runtime restart, private configuration change, selection change, subscription or deployment is part of this task.

## What was missing

The retained direct-image comparison covers OpenAI GPT-4.1 mini, Gemini Flash-Lite, Mistral Small, Claude Haiku, Together Qwen and xAI Grok. These are six model choices, not exhaustive coverage of those suppliers. Stronger controls, newer small models and additional model families are worthwhile candidates; documentation cannot establish which reads our invoices best or fastest.

The existing option registry already supports multiple independently versioned models per provider. The admin automatically lists enabled/configured profiles, with no seven-profile hard limit. New generic labels show the actual hosting provider even when two hosts serve the same model family. Existing drafts and accepted uploads continue to retain their original profile snapshots.

## Prepared choices

[providers.expanded.example.json](../providers.expanded.example.json) originally supplied **14 disabled profiles**; it now retains those and adds the Kimi K3 preset described below. All example entries remain disabled and use the existing compact typed extraction, partial-field and recipient-role policies:

| Recipient | Model IDs | Purpose |
| --- | --- | --- |
| OpenAI | `gpt-6-luna`, `gpt-6.1-sol`, `gpt-6-astra` | Efficient current model, balanced control, stronger control |
| Google Gemini | `gemini-3.8-flash`, `gemini-3.1-pro-preview` | Broader Flash and Pro coverage |
| Anthropic | `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5` | Current small, medium and stronger choices |
| Mistral | `ministral-8b-2512`, `mistral-medium-2604`, `mistral-large-4` | Smaller hosted model, medium control, larger control |
| Together | `moonshotai/Kimi-K3`, `MiniMaxAI/MiniMax-M3` | Two previously uncovered vision model families through an existing recipient |
| Fireworks | `accounts/fireworks/models/kimi-k2p5` | New hosted recipient; separate Kimi model/version |

This is a candidate menu, not a ranking or measured benchmark. Gemini Pro is a preview; Mistral Large 4 is a public preview. Several model identifiers are provider aliases rather than immutable snapshots. Confirm any available snapshot and returned-model identity before live acceptance; model drift cannot be frozen by the local profile hash alone.

Our proposed first evaluation priorities are Kimi/MiniMax for family diversity, Gemini Flash and Claude Sonnet for plausible speed/quality tradeoffs, then Mistral Medium/Large and OpenAI Sol/Astra as stronger controls. These priorities are an engineering judgment, not measured performance. Keep the historical exact tested profiles alongside new IDs rather than editing them.

GLM, DeepSeek, Llama, Cohere Aya and direct Alibaba/Moonshot access are potential later candidates. Do not classify a text-only endpoint as direct vision merely because its family has a multimodal variant. Together's current documented vision table lists Qwen 3.5 9B, Kimi K3 and MiniMax M3; it does not establish image support for its listed GLM/DeepSeek chat endpoints. The current OCR→LLM implementation deliberately supports only OpenAI interpretation, so adding text-only families would require a separate hybrid extension. OpenRouter routing would also require explicitly frozen recipients and fallback handling before invoice use.

## Adapter behavior

Fireworks uses fixed `api.fireworks.ai` and `/inference/v1/chat/completions`, with `FIREWORKS_API_KEY` in root `.env`. It sends the canonical PNG as an inline base64 image and copies the schema into the prompt, using Fireworks' documented JSON-schema envelope. Images whose base64 encoding is at least 10 MB are rejected before dispatch. No new SDK dependency is needed.

Each profile retains a single bounded inference attempt, no redirect, retry, tools or fallback. Usage uses the existing token accounting path; absent tariffs remain unknown. Every draft requires review. Returned model changes, malformed output, refusal and truncated output remain explicit failures.

Current Claude models can return thinking blocks. New profiles explicitly set `reasoning: adaptive`; only those profiles may ignore known `thinking`/`redacted_thinking` blocks while parsing text. Tool and unknown blocks still fail. Older Claude profiles preserve their prior behavior. OpenAI Sol/Astra use supported `low` reasoning, Luna uses `none`; Gemini and Together presets leave model-specific thinking controls at provider defaults. An 8,000-token output ceiling and 90-second stage timeout may need separately versioned tuning after live compatibility checks.

## Making models selectable

The worktree has no private credentials, ledger or scan data. Do not start it against the live database. The presets deliberately have no account approval, tariff, cost ceiling or default selection.

After reviewing this implementation, prepare an additive private configuration from the existing `.local/providers.json`: copy chosen entries from the expanded example into `options` under their new IDs, preserving every existing option, hybrid, budget plan and default. Reuse a provider's existing key through root `.env`; Fireworks needs its own key. Check account model access, terms, processing region and current pricing per choice, record the checks in that option's `config`, set an appropriate conservative `max_call_eur`, and supply an exact tariff only where accounting is understood. Then enable the chosen options. Do not copy approval/price values blindly from another model.

The authenticated `/v1/profiles` response reports unavailable reasons until these checks are supplied. Once enabled/configured in an approved idle runtime update, each choice appears under admin **Method → Model / provider → Use for next scan**. Choosing a profile performs no inference. Existing drafts keep their original selections. Adding choices does not extend the cumulative allowance, and an agent experiment still needs a newly authorized bounded full-corpus plan; the interrupted 9 October comparison stays stopped. xAI's documented unresolved accounting limitation stays unchanged.

## Sources checked

Official documentation checked on 12 October; account availability, residency and tariff activation were not checked and no live model request was made.

- [OpenAI model catalogue](https://developers.openai.com/api/docs/models), [Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol), [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).
- [Gemini Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [Gemini Pro preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview).
- [Claude overview](https://platform.claude.com/docs/en/models/overview), [Sonnet](https://platform.claude.com/docs/en/models/sonnet-5-5/overview), [Haiku](https://platform.claude.com/docs/en/models/haiku-5-5/overview), [Opus](https://platform.claude.com/docs/en/models/opus-5-5/overview).
- [Mistral catalogue](https://docs.mistral.ai/models), [Medium](https://docs.mistral.ai/models/mistral-medium-3-5-26-04), [Large](https://docs.mistral.ai/models/mistral-large-4-0), [Ministral](https://docs.mistral.ai/models/ministral-3-8b-25-12).
- [Together serverless catalogue](https://docs.together.ai/docs/serverless/models).
- [Fireworks vision](https://docs.fireworks.ai/guides/querying-vision-language-models), [structured output](https://docs.fireworks.ai/structured-responses/structured-response-formatting).

## Verification

Completed in this isolated worktree: **720 offline tests passed**; domain/orchestration **96.09% statement / 91.43% branch coverage** (operational CLI/export/reporting entry points separately excluded by the existing gate). Ruff lint/format, strict mypy on 43 source files, JavaScript syntax, provider-aware admin label assertions, diff checks and contract regeneration passed. Generated contracts are unchanged. The suite blocks socket connections and uses synthetic mock transports/temp databases. Run it from the worktree with `python -m pytest` so the shared editable environment imports this checkout.

Tests cover all 14 presets through configured profile selection and one mocked extraction; Fireworks authentication/path/schema and pre-dispatch image boundary; new-recipient refusal/error/truncation/model/usage handling; opt-in Claude thinking and tool rejection; disabled presets and preservation of existing profile snapshots. Synthetic responses demonstrate application compatibility, not real API availability, invoice accuracy or latency. The original checkout's pending iOS files, private state and historical evidence were not edited.

## Access activation authorized — 12 October

Markus subsequently requested the missing-access list and enabling models from existing providers. Read-only authenticated metadata checks succeeded for all 13 new choices on OpenAI, Gemini, Anthropic, Mistral and Together. Fireworks requires its own `FIREWORKS_API_KEY` in the original root `.env`; no key needs replacing for the other providers. Metadata access does not establish successful invoice extraction, remaining provider credit or account-specific throughput. Mistral Medium uses its listed dated ID `mistral-medium-2604` instead of the moving family alias.

Private additive configuration, pricing records, authorization amendment and backups live under the original checkout's `.local/llm-expansion-2026-10-12/`. Activation is limited to explicit mobile Sends within the existing 2,286 calls / EUR353.25 limits. New profiles remain `live_validated: false`; the original selected GPT-4.1 mini profile/version and existing option snapshots stay intact. This authorizes an idle backend restart from this worktree's source with the original private state, not a branch merge or model experiment. Never archive this worktree while the private launcher refers to it. Activation completed after two idle checks. The original private launcher now explicitly loads root `.env`, runs this worktree's backend/admin source and keeps root `.local/backend/` and `.local/providers.json`. Authenticated profile/connection reads and the admin returned 200. There are **20 usable profiles**: the previous seven plus the 13 additions. The original default/profile version is unchanged. Every SQLite table's ordered row count/hash matched the pre-activation snapshot, including scans, reviews, identity, selections and all **2,273 dispatched reservations / EUR351.95 held**. Cumulative caps remain 2,286 / EUR353.25. No inference ran.

The root `.env` now contains a blank `FIREWORKS_API_KEY=` entry. Obtain a serverless API key from the [Fireworks dashboard](https://app.fireworks.ai/) and fill that entry locally. No replacement key is needed for the other providers. Fireworks remains disabled until its key, account/model access, terms and pricing are checked; no account/subscription or recharge setting was created. Read-only catalogue checks do not establish available credit or successful inference.

New per-call EUR holds are conservative operator reservations, not actual provider billing caps: Luna/Haiku/Ministral/MiniMax 0.10, Gemini Flash 0.15, Mistral Large 0.20, Sonnet/Mistral Medium 0.25, Gemini Pro 0.30, Opus/Kimi 0.40, Sol 0.50 and Astra 1.25. Larger choices consume more of the existing remaining EUR1.30 allowance; this activation adds no money or calls. New profile tariffs were independently checked; Haiku/Gemini Pro use upper context-tier rates and Mistral Large uses the non-sale rate for conservative estimates. Account data-control observations retain their original dates and uncertainty. Recheck Gemini Flash's promotional tariff before 1 January 2027.

The metadata-driven Mistral ID change passed 27 targeted offline tests; the preceding implementation checkpoint retains its 720-test verification. Source remains on the separate branch; it has not been merged into the original iOS checkout.

## Fireworks key supplied — 12 October

The new Fireworks key authenticated read-only metadata requests successfully. The original Kimi K2.5 candidate has `supportsImageInput: true` but `supportsServerless: false`; the earlier generic vision-documentation example did not establish current serverless availability. It remains disabled, and no on-demand deployment is authorized or created. A distinct fifteenth preset, `fireworks-kimi3-expanded`, requests `accounts/fireworks/models/kimi-k3`. Its authenticated metadata reports READY, image input and serverless support. The 14 original candidate records are retained rather than silently changing Kimi K2.5's model/version.

[Serverless pricing](https://docs.fireworks.ai/serverless/pricing) lists Kimi K3 Standard at USD3 input / USD0.30 cached input / USD15 output per million tokens. Its private configuration uses gross uncached input and a EUR0.40 conservative reservation, within the unchanged cumulative caps. [Published data handling](https://docs.fireworks.ai/guides/security_compliance/data_handling) states default zero persistent prompt/generation retention for open-model inference absent opt-in; metadata is logged and prompt caches can exist in volatile memory. Account opt-ins, actual processing region, remaining credit and successful inference are not verified by metadata access. The adapter uses chat completions with native JSON schema and no tools, retries or fallback.

Activation evidence, metadata responses and the pre-change profile/state snapshots are private under the original checkout's `.local/fireworks-activation-2026-10-12/`. Activation completed after idle checks. Fireworks Kimi K3 is enabled/configured and appears in the authenticated profile menu, which now has **21 usable profiles**. Kimi K2.5 remains disabled. Loopback admin/profile reads and hotspot authenticated profiles returned 200. All SQLite table row hashes/counts matched the pre-restart snapshot; the current selection remained GPT-4.1 mini at its original exact version. At this activation the live ledger contained **2,275 dispatches / EUR352.15 held**, reflecting two intervening user scans; those records were preserved. Caps remain 2,286 / EUR353.25. No agent inference or deployment ran, and Kimi K3 stays `live_validated: false`. The additional preset passed the existing parameterized offline checks: **28 targeted tests passed**. All new credential access is now present; future credit/quota or inference failures remain explicit provider errors.

## PR verification — 12 October

Final branch verification before PR creation: **721 offline tests passed**, domain/orchestration **96.09% statement / 91.43% branch coverage**, Ruff lint/format and strict mypy passed, JavaScript syntax/label checks passed, generated contracts remained unchanged, and diff checks passed. This source-only PR does not include private activation configuration or evidence and does not claim successful invoice extraction with the new models.

## Paid invoice follow-up — 12 October

Markus requested a paid single-invoice run across all enabled LLMs and approved the corrected allowance after the documented source-image mistake. The completed run attempted all 19 direct-image models once: 13 successful drafts, four incomplete drafts and two timeouts. See [live smoke evidence](LLM_LIVE_SMOKE_2026-10-12.md) for timing, the limited reviewed field, all 26 accounted calls including seven earlier non-invoice calls, and preserved private state. No timeout retry or historical batch resumption is authorized by this completed run.
