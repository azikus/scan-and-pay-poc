# Cost tracking

Latest full six-provider direct comparison: `.local/m3-direct-six-2026-10-08/COSTS.md` and `cost-audit.json`. 102 new dispatched calls, €12.75 retained allowance; current ledger 2,197 / €336.05. Use provider-reported xAI cost ticks where present; original runtime estimates omitted separate reasoning output. Unknown failed-call charges stay unknown. Detailed real-data/stage reports remain private; no new inference is needed to correct cost reporting.

8 October recipient-role follow-up: stage-level reports for both complete 17-image × 2-method matrices are in `.local/m3-recipient-roles-2026-10-08/revision-{2,3}/report.json`. Successful-call list estimates total $0.3045640; the initial schema-rejected request charge remains unknown. Ledger 2,095 dispatched reservations / €323.30 allowance is not billed spend. See [recipient-role evidence](M3_RECIPIENT_ROLES.md); old reports remain unchanged.

Latest fresh M3 evidence (8 October): all 17 masked images per method completed. Published-price corpus estimates are $0.068 OCR/rules, $0.0330516 direct image and $0.1104708 hybrid (both stages included). Compact private table: `.local/m3-scored-2026-10-08/costs.md`. Exact stage/model/usage records are in `.local/m3-draft-policy-2026-10-08/fresh/report-r1.json`; reviewed scoring and caveats are in [M3 reviewed results](M3_REVIEWED_RESULTS.md). Cash/FX/tax remain unknown. The user prioritizes correctness and speed regardless of price; cost is informational, with the existing €500 experiment cap retained. No cost-per-correct-invoice claim is justified by partial field labels.

Updated 7 October 2026 after Markus clarified the intended scope: keep track of how expensive each option is. Cost tracking supports the extraction work; it is not a separate implementation workstream or a reason to delay it.

Keep a compact private table under `reports/cost-comparison/` with one row per tested provider/model/method:

- Exact option and test date.
- Number of attempted images, including failed attempts.
- Estimated or reported cost per image and for the batch, in the original currency.
- Unknown charges and any material free-tier allowance or billing minimum.
- A tariff source/date so estimates can be checked.

Existing detailed stage records remain available for debugging and reproducibility. Do not expand this into financial forecasting, ownership-cost analysis or repeated budget-plan prose unless requested. Multi-service methods record each external call and add their costs; reusing saved OCR output must not count the original charge twice.

Internal spending allowances protect the €500 limit. They are bookkeeping limits, not money charged or held by a provider. Preserve the existing ledger and unresolved charges; do not reset it or buy subscriptions automatically.

Refresh the compact table when new evaluation results are available. Accuracy and cost per correct result require checked answers; until then, show expense without an accuracy ranking.
