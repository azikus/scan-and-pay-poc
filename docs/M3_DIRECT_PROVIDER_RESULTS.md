# M3 direct-image provider comparison — 8 October 2026

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

The user-authorized single repeat is complete: six direct-image providers × all 17 masked inputs = 102 dispatched calls. No completed input was retried, no provider or service tier was substituted, and the reviewed key and prompt semantics stayed fixed. Original profiles/results/ledger entries remain preserved.

Ranks below prioritize accepted critical payment fields, then all accepted readable fields, then total median latency. This is a partial reviewed development-corpus result, not whole-invoice accuracy or a vendor-wide benchmark. The prompt was developed on these samples with OpenAI.

| Rank | Provider / model | Accepted readable /102 | Critical /63 | Median / p95 | Ready / incomplete / error | Timeouts /17 |
| --- | --- | ---: | ---: | --- | --- | ---: |
| 1 | openai · gpt-4.1-mini-2025-04-14 | 79 | 51 | 4.02 / 9.43 s | 2 / 15 / 0 | 0 |
| 2 | gemini · gemini-3.5-flash-lite | 80 | 50 | 3.31 / 5.00 s | 2 / 15 / 0 | 0 |
| 3 | together · Qwen/Qwen3.5-9B | 69 | 47 | 9.41 / 22.67 s | 0 / 17 / 0 | 0 |
| 4 | mistral · mistral-small-2603 | 71 | 43 | 2.99 / 5.78 s | 1 / 16 / 0 | 0 |
| 5 | anthropic · claude-haiku-4-5-20251001 | 65 | 42 | 5.64 / 11.14 s | 4 / 13 / 0 | 0 |
| 6 | xai · grok-4.7 | 16 | 10 | 90.06 / 90.13 s | 2 / 0 / 15 | 14 |

Every provider has 17 timing observations. Timeouts/errors are retained, not excluded to improve scores. The key covers 102 readable fields and 98 confirmed absences, with 146 excluded fields including 92 pending. Only 13 images have scored fields; all 17 contribute processing/timing/cost evidence. The corpus includes related pages and a retained duplicate. Ready means complete enough for review, not verified correct.

Accepted names include only three human-approved field variants. Matching values marked inferred remain separately visible and uncredited under the frozen rules; Gemini has eight such checks. These are not equivalent to differing amounts or bank digits. No labels were rewritten after inspecting this run.

Grok encountered sustained latency and a documented HTTP 429 model-capacity response. The batch paused for a cooldown, then resumed only previously unsent rows with their original keys. The error was provider capacity, not verified account-credit exhaustion. Those unavailable responses limit quality assessment; do not describe them as incorrect OCR readings.

OpenAI used exactly the same profile version as the preceding run. It again scored 79/102 accepted readable fields, but individual outputs changed; see the private repeat-change CSV. Previous paid calls remain useful for regression/consistency analysis, saved-response rescoring, API compatibility and cost evidence, not only timing.

## Private reports

`.local/m3-direct-six-2026-10-08/` contains:

- `REPORT.md`: complete comparison and the first five reviewed cases.
- `provider-ranking.csv`, `field-results.csv`, `failures.csv`, `field-breakdown.csv`: ranked and field-level evidence.
- `inferred-values-for-review.csv`: observations that need inference-policy review.
- `image-outcomes.csv`: all 102 cells with scan IDs, model returns and failures.
- `openai-repeat-changes.csv`: same-profile differences, keeping both runs.
- `comparison.json`, per-provider `*-comparison.json` and `*-measurements.json`: reproducible scoring and measurements.
- `COSTS.md`, `cost-audit.json`: estimates/reported charges and unknowns.
- `plan.json`, `providers.json`, `prompt.txt`, `readiness.json`, `access-summary.json`: frozen scope, budget, models, current access and price checks.
- `capacity-incident.json`, `xai-capacity-stop-batch.json`, `capacity-resume.json`: stop/cooldown/resume provenance.
- `verification.json`: original files and ledger preservation.

The current key remains `.local/m3-name-review-2026-10-08/reviewed-key-r4.json` (`reviewed-fields@2`). Original strict scores and previous snapshots are unchanged. Full real-data reports stay ignored/private; do not commit invoice contents.

## Cost and next checkpoint

Original ledger: 2,095 dispatched reservations / €323.30 allowance. Final: **2,197 / €336.05**, an increase of 102 / €12.75. Allowance is not cash billed. The run cap was 2,197 calls / €409.05 within the €500 project cap; the 102-call allowance for this run is exhausted. No budget reset or subscription.

The xAI responses provide cost_in_usd_ticks. This report uses that provider-reported charge for returned responses and leaves timeout/rejection charges unknown. The original adapter estimate omits separate xAI reasoning output and remains frozen; cost-audit.json records the correction for reporting. Update cost accounting in a separately verified change before relying on future runtime xAI estimates. No provider calls were made to fix cost reporting.

No production extraction/scoring code was changed for this run; the last offline verification remains 651 passing tests, 95.57% statement / 90.85% branch coverage. The temporary backend is stopped and report verification passed. No default, pipeline selection, PR, merge or mobile implementation occurred.

Review the shortlisted fast pipelines and the remaining field failures before selecting the mobile backend. Further human corrections can rescore these responses offline. Any future paid experiment needs a fresh bounded plan against this ledger. Markus’s confirmation remains required before PR creation/merging, followed by the next-chat handoff.
