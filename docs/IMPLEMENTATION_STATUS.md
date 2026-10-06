# Backend implementation and acceptance record

Started 2 October 2026 on explicit kickoff. The handoff remains the scope authority.

## Current checkpoint — 6 October 2026

The user requested a codebase cleanup, a separate report on the cost of every option, updated documentation, a push to private `main` and a fresh local implementation chat. Broader provider integration remains the next chat's M2 work, with useful M3 regressions alongside it.

- Moved the synthetic fixture adapter from production runtime into test support; the built runtime wheel excludes tests. Removed redundant fixture initialization and moved a repeated import to module scope.
- Fixed concurrent health readiness checks sharing one probe filename. A controlled overlap regression fails with `FileNotFoundError` against the original implementation and passes with unique probe names.
- Preserved the unused original architecture bitmap in the private pre-main backup; the active architecture uses its existing editable Mermaid diagram. No private samples, labels, results, credentials or historical reference code were pruned.
- Added [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md) and reconciled roadmap, evaluation, budget, operations and handoff. The standalone cost report begins with M2 evidence, is an M4 acceptance deliverable and is refreshed for M8, independently of HTML findings.
- **184 offline tests passed** on Python 3.12.5. Domain/orchestration: **1,271 / 1,287 statements = 98.76%; 331 / 348 branches = 95.11%**. The denominator decreased because test-only adapter code moved out of production; no production module was newly excluded. Lint, format, strict types and schema export passed; exported v1 JSON files are byte-identical to the pre-cleanup versions. The runtime wheel built successfully and contains no tests or private files. No dependency versions changed. One existing Starlette/TestClient deprecation warning remains; it does not fail the suite.
- The existing `.env` is unchanged. No cloud/account mutation or paid inference occurred; the twelve prior dispatches/€12 holds remain. Privacy/link/contract checks and before/after regression evidence are recorded under `.local/main-checkpoint-2026-10-06/`.
- Local branch is `main`; the target was rechecked private and empty before this checkpoint. Commit/push are explicitly authorized, without force. Git log/status and origin refs are the authority for the published revision. The next chat uses this folder and starts new implementation on a `codex/` branch after inspection.

Historical access preparation and Milestone 1 measurements below retain their original dates; they are not additional provider calls or repeat benchmarks.

## Plan

Next-stage priority: [Phase 2 rollout](PHASE2_ROLLOUT.md) records broader LLM/OCR/document coverage alongside OCR fixes, explicit code boundaries and full-corpus testing. **The complete upfront credential/resource set was supplied on 6 October; the user's gate is now satisfied**, as recorded in [PHASE2_ACCESS.md](PHASE2_ACCESS.md). All project access fields use the existing private `.env`, with cloud authentication kept in SDK-managed stores; future-provider fields remain unwired until their integrations are implemented. Offline adapter/registry work may resume. Terms, pricing, processing location and actual inference access still require integration checks before a new bounded full-corpus batch. No new adapter, runtime change or paid call has been made during access preparation. The Milestone 1 evidence below is unchanged.

Google access preparation, 6 October: following the user's explicit request for a new dedicated project, created it under the existing organization, linked the existing billing account and enabled Document AI. Local Application Default Credentials use that project's quota. Enterprise OCR and Invoice Parser resources in `eu` both report `ENABLED`, with their default versions `DEPLOYED`; authenticated management reads succeeded. Saved the four connection settings in `.env`, preserving every unrelated value and mode 0600. Private management responses, processor versions and setup evidence are in `.local/google-documentai-setup/`. This verifies resource access only: no document processing, adapter implementation or extraction validation occurred.

AWS access preparation, 6 October: the user created an account; a dedicated IAM user and validated policy restrict Textract to synchronous OCR/invoice operations in Frankfurt and permit temporary local sign-in. No access keys were created. After the user's password setup, IAM console login and `aws login` completed. STS verified `scanpay-local` through profile `scanpay`, region `eu-central-1`; temporary credentials remain SDK-managed. Private identity/setup evidence is in `.local/aws-textract-setup/`. Textract processing remains untested. The earlier root session was signed out and never authorized for programmatic access.

Latest access follow-up, 6 October: the user narrowed the provider roster; only the services listed in PHASE2_ACCESS.md remain prerequisites. All 18 required environment fields are populated, including Mindee key/model ID and Together/Azure settings. Nanonets' originally saved key failed workflow management authentication; the existing key from its signed-in workflow product succeeds. Created a v4 workflow and verified a generic 12-field invoice/payment schema plus five table headers. Its documented Invoice-template request returned an empty `Instant Learning Model`, so evidence identifies this as a configured custom workflow, not a verified prebuilt invoice model. Saved its matching key/ID in `.env`, preserving unrelated settings and mode 0600. No samples or training examples were uploaded; processing readiness remains an integration check. The unused commercial outreach draft was trashed without sending and its project references removed. Private access responses, initial failures and schema metadata remain under `.local/provider-access-2026-10-06/`.

Access acceptance: AWS CLI identity verified; Nanonets management authentication and exact configured fields read back; all required environment values present; `.env` and private evidence ignored by Git. Setup made zero inference calls and left the twelve prior dispatches/holds unchanged. No implementation tests were rerun for this documentation/resource-setup-only change; the 183-test Milestone 1 result below was the baseline at that point; current cleanup verification is above.

New-chat handoff, 6 October: reconciled the active documentation with the completed backend/access state, replaced the original start-from-zero kickoff, and added [ROADMAP.md](ROADMAP.md). The four existing phases now map to explicit M1–M8 checkpoints; M2 provider coverage/tooling is next, with useful M3 interpretation work alongside it. [CODING_HANDOFF.md](CODING_HANDOFF.md) records the read order, private evidence paths, known access/product caveats, preserved budget and exact continuation prompt. Earlier documentation is backed up privately. That earlier update changed documentation only: no adapters, tests, credentials, model settings, paid calls, commits, pushes or new chat were created. [Handoff verification](HANDOFF_VERIFICATION.md) records the final consistency checks.

- [x] Read required handoff documents; preserve existing files.
- [x] Recheck remote: azikus/scan-and-pay-poc is private and empty.
- [x] A: typed contract, synthetic tests, safe image pipeline, persistence, bounded workers, API and CLI.
- [x] B implementation: OpenAI Responses / GPT-6 Luna adapter and synthetic HTTP fixtures.
- [x] B live checkpoint: exact model access verified; revised vision profile completed both starter images on 5 October, with mandatory review and preserved evidence/usage.
- [x] C implementation: Mistral OCR 4.1 and general local UK/HR rules, independent comparisons and synthetic HTTP fixtures.
- [x] C live acceptance: both UK/HR OCR runs completed after explicitly approved API billing activation, followed by a successful HR two-provider comparison. Earlier UK partial-failure comparison remains preserved.
- [x] Export contracts, verify fresh installation, measure coverage and update acceptance evidence.

**Milestone 1 is complete. A, B and C have acceptance evidence.** Both exact starter models completed real UK/HR runs and a successful comparison through the v1 API. Twelve requests retain €12 in conservative budget holds. Shared `review@2` removes false bank-field ambiguity: OpenAI HR is `ready_for_review`; UK remains `needs_review` for the invoice-total amount role. Mistral OCR/rules drafts are incomplete and reviewable, with the raw OCR and rules limitations preserved. All drafts require confirmation. API pay-as-you-go was activated with explicit approval; training remains off. Processing residency, retention and billing overrides remain unknown. No commits or pushes had been made at that Milestone 1 checkpoint.

## Acceptance evidence — through 5 October 2026

| Acceptance | Evidence/status |
| --- | --- |
| Fresh local setup | Hash-locked dependencies installed into a separate new `.local/setup-check-venv`; editable install and `pip check` pass. No global install. |
| Actual server startup | One Uvicorn process on `127.0.0.1:8765`; real multipart CLI submissions and polling completed. Health returned `status=ok`. Both current starter profiles reported live-validated after successful runs. Temporary servers stopped cleanly; no startup/provider probes. |
| JPEG/PNG and persistence | Tests cover decode failure, unsupported/animated input, EXIF orientation, stripped metadata, original/canonical hashes, private files and completed-result retrieval after restart. |
| Recovery | Nonterminal jobs become interrupted without replay. Completed comparison drafts survive interruption of later profiles. Dispatched uncertain cost holds remain. |
| Extract/compare | Actual UK partial-failure comparison and final successful HR comparison. Each provider keeps its own draft/error; `final_result_id` stays null in compare. No majority merge or automatic fallback. |
| Idempotency/deletion | Offline concurrent submissions produce one job/call; changed options conflict, all-enabled snapshot reuse does not re-resolve, terminal deletion retains a tombstone and returns 410 on reuse; active deletion is 409. Live same-key resubmission reused the final HR comparison and kept the budget at twelve dispatches. The original UK result survived multiple server restarts. |
| Payment-critical rules | Leading zeroes, linked options, separate supplier/payee/holder, HR model/reference, amounts versus totals/credits, unknown/inferred/conflicting currency, missing/ambiguous fields, IBAN checks, explicit country conflicts, no banking-digit repair, preserved reference punctuation and mandatory review. |
| Provider safety | Mocked SDK/HTTPX responses cover success, refusal, auth/quota/unavailable, actual transport timeout, invalid schema/evidence/metadata, wrong returned model, no usage, no tools/URL execution/redirect following or automatic retries. Raw data stays private; unsafe serialization warnings are suppressed. |
| Runtime/budget | Entire comparison reserved atomically or rejected, call cap, bounded queue, 90-second timeout logic, 240-second queue-inclusive deadline, single owner lock, local storage errors and partial comparison recovery. |
| Destination ledger | External image recipient and local OCR/rules stages, UTC stage records, canonical/text hashes, account/region metadata, request IDs, monotonic timings and per-currency costs. Residency remains unknown without evidence. |
| Real UK/HR provider runs | Both exact profiles completed both images. Vision: HR `ready_for_review`, UK amount-role `needs_review`, no false bank ambiguity. OCR/rules: incomplete `needs_review` drafts with separate external OCR and local rule stages. Two earlier OCR HTTP 429 attempts remain recorded. |
| Reference labels | Private draft labels unchanged and unscored. No correctness, savings or camera claims. |
| Git/privacy | Remote private/empty rechecked, local `codex/backend-foundation` initialized. Ignore checks cover samples, labels, raw/results, reference, reports, credentials, environments and databases. No real data/credentials staged or committed. |

## Measured verification — 5 October 2026

- **183 offline tests passed** on Python 3.12.5; socket connections are prohibited by the suite.
- `ruff check`, `ruff format --check`, strict `mypy`, schema export and dependency checks pass.
- Domain/orchestration (including API, configuration, models, image validation, registry, rules, storage, runtime and provider adapters): **1,288 / 1,304 statements = 98.77%; 335 / 352 branches = 95.17%**. Targets are 90%/85% respectively.
- Full coverage report includes CLI, export and the coverage-check command separately. Those operational entry points do not inflate the domain gate. Generated schemas, tests and third-party libraries are excluded. The latest machine-readable coverage is `.local/coverage.json` (now the 6 October run); the counts above retain the 5 October measurement. There is no claim that untested branches passed.
- TestClient currently emits one dependency deprecation warning about its HTTPX integration. It does not affect the passing API tests or runtime client; no provider-data warning remains.

## Live smoke record — 5 October 2026

| Request | Outcome | Provider duration | Cost evidence |
| --- | --- | --- | --- |
| UK vision, original profile | Completed; needs review | 13.39 s | Reported token categories, USD estimate |
| HR vision, original profile | Invalid provider output: amount formatting violated v1 | 13.55 s | Token usage and billed-cost estimate preserved despite failure |
| UK Mistral OCR/rules | HTTP 429 / `provider_quota`; no OCR draft | 0.54 s | Unknown charge; €1 hold retained |
| HR vision, revised profile | Completed; needs review, unresolved IBAN ambiguity | 13.72 s | Reported token categories, USD estimate |
| UK vision, revised profile | Completed; needs review, unresolved amount role/fields | 10.87 s | Reported token categories, USD estimate |
| UK Mistral OCR/rules after funding/opt-out | HTTP 429 / `rate_limited`, provider code `1300` | 0.45 s | Unknown charge; €1 hold retained |
| UK vision, `review@2`, same comparison | Completed; only amount-role review remains | 12.23 s | Reported token categories, USD estimate |
| HR vision, `review@2` | Completed; ready for review, no unresolved-field reasons | 13.08 s | Reported token categories, USD estimate |
| UK OCR/rules after API activation | Completed; incomplete draft needs review | 2.25 s | 1 page, USD $0.004 estimate |
| HR OCR/rules after API activation | Completed; incomplete draft needs review | 1.84 s | 1 page, USD $0.004 estimate |
| HR OCR/rules, final comparison | Completed; incomplete draft needs review | 2.99 s | 1 page, USD $0.004 estimate |
| HR vision, final comparison | Completed; ready for review | 13.29 s | Reported token categories, USD estimate |

The first revised vision profile was `1-c31963e9e0c08917`, with `payment-image@2`; current `review@2` is `1-92d607e6c085e779`. It makes v1 amount formatting explicit in the prompt and strict output schema, retaining original text as evidence. No failed output was silently repaired or replaced. The earlier failure remains immutable; validation used deliberate new runs. OpenAI cache-write usage/pricing was corrected before any paid call. HTTP error bodies are now retained privately for future diagnosis without appearing in API responses or logs; the first Mistral error predates that change, so quota versus rate-limit cause cannot be narrowed from its recorded HTTP status alone.

Seven OpenAI calls total **USD $0.008467925** and three successful OCR pages **USD $0.012**, for **USD $0.020467925 in usage-based estimates**. Both failed OCR charges remain unknown. This is not a reconciled provider invoice or EUR conversion. Twelve €1 reservations remain in the persistent ledger. No automatic retries or substituted models. API pay-as-you-go activation was explicitly authorized. Recipients were `api.openai.com` and `api.mistral.ai`; successful OCR runs each record a separate local rules stage.

Private evidence: `.local/live-2026-10-05/{plan,evidence,api-checks,openai-access,mistral-access}.json`; full results in `.local/client/` and raw bodies/images/SQLite stage timestamps under `.local/backend/`. Labels were not opened, changed or scored. These inputs are rasterized references, not camera photos.

Reproduce offline verification using README's commands. The first signed-in Admin inspection identified incomplete billing as a likely blocker; its historical findings remain in `.local/live-2026-10-05/mistral-admin-check.json`. The follow-up below supersedes its account-state observations. Every earlier hold is preserved; remaining first-tranche reservation headroom is €18. The twelve-call starter cap is exhausted, so any later experiment needs a newly recorded bounded plan.

### Shared normalization and billing resolution

`review@2` strips only a matching leading bank-field label when comparing raw and extracted values, preserves original text and significant banking characters, and maps explicit country names/codes through ISO data without inferring from addresses/language. `schwifty` already supplies IBAN structure, country-length and checksum validation in the shared layer. Synthetic regressions cover changed digits, wrong labels, multiple values and real country conflicts. Earlier results are immutable; separately labelled offline replays are not new provider evidence.

The user funded Mistral and disabled API training. Signed-in checks verified API training and Labs off before further images. Credit alone did not resolve HTTP 429: the Subscription page still showed API pay-as-you-go disabled. The user explicitly selected **Activate pay-as-you-go**; the agent accepted terms and submitted activation. Admin then showed Active, training was rechecked off, and subsequent UK/HR OCR runs succeeded. Auto-recharge stayed disabled. No extra top-up or key rotation was performed. [Mistral's limits guidance](https://help.mistral.ai/en/articles/698531-why-am-i-hitting-api-rate-limits-and-how-do-i-increase-them) explains that credit top-ups do not raise rate limits.

Private account checks/screenshots, approval/activation evidence and each bounded plan revision are in `.local/live-2026-10-05/`. The earlier automatic approval rejection of a training-setting change remains historical evidence; the user resolved that setting themselves. Ten stored scans (twelve runs) pass Pydantic and generated JSON-schema validation. `.local/live-2026-10-05/final-api-checks.json` records both live-validation flags, successful comparison, persisted old results and unchanged dispatch count after same-key resubmission.

### Observed baseline limitations and next experiments

- The UK vision draft preserves the printed gross total, without promoting it to amount due. Bank fields no longer carry false ambiguity.
- Mistral's UK raw OCR contains the account name, both bank fields and gross amount. Blank paragraphs cause the initial rules to split the bank fields into two incomplete candidates, and the multi-column amount table is not parsed.
- Mistral's HR raw OCR contains the IBAN, due date, amount, HR model and reference. Rules extract the IBAN/due date but miss the multi-column amount, prose reference and beneficiary association.
- These are local rules/association gaps, not missing OCR text. Retain this versioned baseline. Follow-up rules need synthetic layout/pairing regressions and an explicitly labelled offline replay before further paid tests; annotations or OCR-to-LLM are separate profiles.
- Wider OpenAI/Anthropic, hosted Mistral vision and Mistral annotation comparisons remain next-stage work, with access/licence/pricing checks and a new bounded matrix. No accuracy score until critical labels are verified.

Private image and extraction views (including raw OCR text) are under `.local/review/` and queued to open beside the source images in Codex. The temporary server is stopped. No mobile apps, browser product UI, HTML report, public artifact or payment execution was built.

### Hosting-scope clarification — 5 October 2026

The user corrected the earlier interpretation: provider-hosted open-weight models are allowed; self-hosted inference is excluded. AGENTS.md, the handoff, architecture, context, decisions, backend/evaluation plans and shortlist now use that boundary. Hosted Mistral Small 4 and Medium 3.5 are planned next, with optional Ministral/Large controls and other hosted open-weight APIs. No new adapters or paid runs were added by this documentation correction; Milestone 1 evidence, twelve holds and earlier results remain unchanged. Documentation consistency and source inspection found no backend weight-licence exclusion to remove.
