# LLM expansion — current scope, 13 October 2026

**Current provider request status — 13 October:** 31 enabled/configured profiles remain after Fireworks/Aya removal. Latest processing evidence: **27 profiles completed without API errors**, **two retain last-request failures** (Haiku 4.5 availability/connection error; Mistral Large 4 timeout), and **two AWS profiles have verified authentication but untested processing**. Google OCR and Invoice processing now pass. Incomplete drafts are successful requests requiring review, not API failures. See [API_CONNECTION_STATUS.md](API_CONNECTION_STATUS.md) for every current profile. No new inference/runtime/configuration change is part of this documentation closeout.


**Google verification — 13 October:** Markus requested fixing Google Document AI. Both exact runtime authentication/processor-version preflights passed, followed by the first actual processing dispatch for each Google profile on the previously approved invoice: OCR 7.059s / Invoice Parser 8.207s, both completed with incomplete review drafts. No code/credential replacement was needed; the precise earlier authentication failure remains unknown. Two dispatches / EUR0.30 holds fit existing caps and preserve eight reservations/EUR0.80 mobile headroom. Ledger now 2,342 reservations / 2,340 dispatched / EUR369.60 holds; caps remain 2,350 / EUR370.40. Every prior ledger row, selection, identity and private configuration was verified unchanged. AWS access-key authentication also passed as `scanpay-local`; no AWS processing ran. See [GOOGLE_VERIFICATION_2026-10-13.md](GOOGLE_VERIFICATION_2026-10-13.md).


Markus requested broader models in a separate worktree, then requested complete Fireworks removal and removal of Cohere Aya Vision. The implementation remains on `codex/llm-provider-expansion` in [PR #9](https://github.com/azikus/scan-and-pay-poc/pull/9). The original checkout’s separate iOS/presentation work is preserved.

## Available models

[providers.expanded.example.json](../providers.expanded.example.json) supplies **13 opt-in presets** alongside existing tested profiles. Multiple models from a provider remain independently versioned choices; the admin displays their actual hosting provider.

| Provider | New model choices |
| --- | --- |
| OpenAI | `gpt-6-luna`, `gpt-6.1-sol`, `gpt-6-astra` |
| Gemini | `gemini-3.8-flash`, `gemini-3.1-pro-preview` |
| Anthropic | `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5` |
| Mistral | `ministral-8b-2512`, `mistral-medium-2604`, `mistral-large-4` |
| Together | `moonshotai/Kimi-K3`, `MiniMaxAI/MiniMax-M3` |

Example presets deliberately contain no credentials or approval/tariff values and default to disabled. The original private runtime has **31 enabled/configured profiles** after removing the five Fireworks profiles and Aya. Restored Google Document AI, AWS Textract, Azure, Mindee, Mistral annotations, Grok, OCR/rules, legacy profiles and the OCR→OpenAI hybrid remain present. AWS was explicitly skipped in the last paid batch; access-key authentication now passes, while processing remains untested.

Fireworks and Cohere adapter branches, provider registration, admin labels, example credential placeholders and presets are removed entirely. DeepSeek, GLM and Llama therefore have no current profile after removal of their Fireworks host. Together’s Kimi K3 remains a separate provider choice. Existing raw responses, drafts, snapshots and ledger rows remain private and unchanged; retired-provider results remain accessible as historical evidence. Existing external provider keys were not revoked or published.

## Adapter behavior

Each selected profile has one bounded attempt, no provider redirects/tools/retries/fallback, local typed validation and mandatory review. Compact profiles retain partial-field recovery and recipient-role policies. An 8,000-token output ceiling and 90-second stage timeout are current bounded controls; schema readiness does not verify extraction correctness or payment ownership.

New Claude profiles explicitly opt into adaptive thinking; only these profiles may ignore known thinking/redacted-thinking blocks while parsing text. Tool and unknown blocks still fail. Old profiles preserve their original behavior and hashes. OpenAI Luna uses `none` reasoning, Sol/Astra use `low`; Gemini/Together presets retain model-specific defaults.

Grok has a new independently versioned reported-cost profile. With opt-in `xai-ticks-v1`, charge is `usage.cost_in_usd_ticks / 10^10` USD, including reasoning, as documented by [xAI](https://docs.x.ai/developers/cost-tracking). Missing charge means unknown; malformed ticks fail rather than estimate or double-count reasoning. Historic configurations/results remain immutable.

## Claude Haiku clarification

Claude Haiku 4.5 is the retained exact baseline (`claude-haiku-4-5-20251001`), established before the newer expansion. Haiku 5.5 was added and enabled separately to preserve reproducibility of existing results/drafts. Neither replaces the selected OpenAI GPT-4.1 mini default.

In the dated 12 October all-catalogue run, Haiku 4.5 returned `provider_unavailable` after 62.578 seconds. This code can represent an upstream server error or connection failure; no raw response/status was retained for that failure, so the precise cause is unknown. It does not establish a bad key, permission issue or broken Anthropic integration. Haiku 5.5 returned a successful draft in 11.474 seconds using the same provider access. Neither timing establishes a reliability ranking from one invoice. No automatic retry occurred.

## Live evidence and preservation

The completed [19-model invoice run](LLM_LIVE_SMOKE_2026-10-12.md) and subsequent [all-catalogue run](ALL_CATALOGUE_LIVE_2026-10-12.md) retain their original dated rosters and accounting, including retired providers. They are single-invoice compatibility studies, separate from the historical stopped comparison. No paid test was repeated during removal.

The removal backed up private configuration/profile metadata and every ledger row under `.local/provider-removal-2026-10-13/` in the original checkout. The existing single backend owner was restarted only while idle. Authenticated profile reads verified exactly six entries removed, all remaining profile metadata/versions identical, current selection and identity unchanged, and every budget row byte-for-byte equivalent in its recorded values. Caps remain 2,350 reservations / EUR370.40; dated ledger snapshot remains 2,340 reservations / 2,338 dispatched / EUR369.30 held. These holds differ from actual bills. Do not archive the worktree while the private launcher uses it.

Root `.env`, SDK-managed credentials, original invoices, raw responses and private evidence remain ignored. Configured API keys stay in their existing private store; AWS uses the `scanpay` SDK profile in `eu-central-1`. Preserve subsequent user scans/selection rather than resetting them to this snapshot.

## Verification

After removal, **715 offline tests passed**. Domain/orchestration coverage: **96.07% statements / 91.37% branches**. Ruff lint/format, strict mypy, coverage gate, JavaScript syntax, generated contracts and diff checks passed. Tests cover all 13 retained presets, exact profile preservation, adaptive Claude thinking, Grok reported costs and rejection of removed provider configuration. Private live verification made **zero inference calls**.
