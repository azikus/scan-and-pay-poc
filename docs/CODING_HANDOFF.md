# Coding handoff — continue here

Phase 2 is closed for the current PoC scope. Read [Phase 2 closeout](PHASE2_CLOSEOUT.md) first: it owns the selected pipeline, measured tradeoff, remaining limitations and preserved evidence. The [fourth-chat handoff](CHAT4_HANDOFF.md) is a prepared technical baseline; Markus will provide its remaining brief later. Do not create that chat or begin mobile implementation during closeout.

## Current decision and scope

Select direct-image `gpt-4.1-mini-2025-04-14`, profile `openai-mini-image-roles-v3@2-5094b6dc13ef5718`, using the current role prompt, partial-field recovery and shared review contract. The active private `.local/providers.json` now selects it; its predecessor is preserved in `.local/phase2-closeout-2026-10-08/providers-before-selection.json`. No hybrid or fallback runs automatically. Compare mode remains an explicit evaluation tool.

Latest measured accepted field scores: OpenAI 79/102 readable and 51/63 critical at median 4.02 seconds; Gemini 80/102 and 50/63 at 3.31 seconds. The best reviewed hybrid has 71/102 and 44/63 at 6.58 seconds, counting both calls. These are partial development-corpus scores, not verified-invoice rates or universal provider rankings. Cost is recorded but did not determine selection.

Markus's request to wrap the phase, select a pipeline and commit/push confirms this checkpoint and permits the previously requested PR/merge sequence after checks. There were no pending project PRs at closeout inspection. Preserve the active `codex/m2-provider-coverage` branch; inspect current Git/remote state for the completed merge before starting new implementation. No force push or public publication.

## Next work

1. Add Markus's remaining brief to CHAT4_HANDOFF.md when supplied; do not invent requirements or start another chat yet.
2. In the next chat, agree M5 capture/import, processing, editable draft, missing-field/retake, error and confirmation designs before mobile code.
3. Implement M6 iOS against the existing Mac backend with a configurable reachable URL. A physical device cannot use its own localhost for the Mac. Keep provider credentials server-side and test image orientation, polling, idempotent recovery and partial fields.
4. Android follows as M7. Native OCR is an optional later experiment; barcode decoding is outside this PoC. M8 final HTML findings and the attendee display remain deferred.

Every draft needs confirmation. `success` means complete enough for review, not objectively correct. Preserve invoice totals, supported supplier/account-holder fallback, bank-transfer preference and explicit recipient distinctions. Missing/conflicting amounts are null with a warning; a wrong observed amount may evade detection. Never hide all fields because one is incomplete, invent bank digits, infer currency from an address, or use answer-key values in extraction.

## Workspace, operation and evidence

Use `/Users/markusi/Developer/Azikus/scan-and-pay`, remote `git@github.com:azikus/scan-and-pay-poc.git`. Inspect status and retain all existing private files. No paid calls during handoff. Latest ledger: **2,197 dispatches / €336.05 retained allowance**; the selected configuration has no additional call allowance. A new bounded mobile-test plan must precede future inference under the same €500 cap. Never reset the ledger or rerun completed evaluation batches to verify a handoff.

- Latest six-direct comparison: `.local/m3-direct-six-2026-10-08/`.
- Original fresh baseline: `.local/m3-draft-policy-2026-10-08/fresh/`; recipient-role revisions: `.local/m3-recipient-roles-2026-10-08/`.
- Current reviewed key and consistent rescoring: `.local/m3-name-review-2026-10-08/`. Only explicitly approved name aliases count; unresolved labels remain unscored.
- Active 17 masked-image corpus: `.local/evaluation/m3-no2d-2026-10-08/manifest.json`; original samples and historical selections stay unchanged.
- Closeout profile backup and verification: `.local/phase2-closeout-2026-10-08/`.
- All original jobs, stage artifacts and ledger: `.local/backend/`.
- Historical M2 evidence: `.local/m2-2026-10-06/`, `.local/m2-compat-2026-10-07/`, `.local/m2-repeatability-2026-10-07/`. The old 31-input runs establish integration/repeatability, not current masked-corpus accuracy.
- Credentials and connection settings remain in root `.env`; SDK-managed cloud credentials stay in their existing stores. No secrets, real banking data or sample labels enter Git.

The backend is stopped. Startup/health/profile inspection does not call providers. README and OPERATIONS.md document offline verification and local startup. Latest checks: 651 tests; 95.57% statement / 90.85% branch coverage. Keep these gates for domain/orchestration/evaluation and use synthetic offline fixtures.

## Read order and authority

Read AGENTS.md, PHASE2_CLOSEOUT.md, CHAT4_HANDOFF.md, README.md and this file. Then read:

1. ROADMAP.md, IMPLEMENTATION_STATUS.md, PHASE2_ACCESS.md and PHASE2_ROLLOUT.md.
2. DECISIONS.md, CONTEXT.md, API_CONTRACT.md and docs/examples/README.md.
3. ARCHITECTURE.md and BACKEND_PLAN.md.
4. EVALUATION_PLAN.md, COST_REPORT_PLAN.md, STARTER_EVALUATION.md, PROVIDERS_AND_BUDGET.md and RESEARCH_AND_AUDIT.md.
5. OPERATIONS.md, INTEGRATIONS.md, M2_OPERATIONS.md, M2_INTEGRATIONS.md and HANDOFF_VERIFICATION.md.
6. M3_DIRECT_PROVIDER_RESULTS.md and M3_RECIPIENT_ROLES.md when inspecting experimental evidence. M3_HANDOFF.md preserves the earlier continuation baseline and must not restart completed work.

Latest user instructions win. API_CONTRACT.md owns wire semantics; this file owns continuation scope; ROADMAP.md owns milestones. Historical status and earlier approval gates do not override the current closeout. Keep existing Python/FastAPI/Pydantic/SQLite architecture, image-only API, provider-hosted inference, bounded workers and immutable evidence.
