# Coding handoff — continue here

## Invoice context follow-up — 13 October

Latest user clarification: add country/scheme score breakdowns now and prepare country labels for review. Implemented in `evaluation.country_scores`; review key/form and both saved-response reports are private under `.local/invoice-context-2026-10-13/`. Markus subsequently approved all 17 country suggestions in chat. The private `country-reviewed-markus-2026-10-13.json` records this approval; `old-country-report-reviewed.json` and `new-country-report-reviewed.json` score 13/17 and 17/17 country matches respectively (16 distinct images). These are user-approved model suggestions, not blind independent labels. Preserve the initial pending key/form and earlier reports. Preserve the original extraction benchmark and use a single shared country key across compared profiles. Read the follow-up section in INVOICE_CONTEXT.md. This evaluation-only update adds no paid calls, runtime changes or default promotion.

Read [INVOICE_CONTEXT.md](INVOICE_CONTEXT.md) for the latest separate PR scope, exact new profile, 37 completed paid runs, verification and preservation audit. Source is in the managed `invoice-context-review` worktree on `codex/invoice-context-review`, based on merged PR #9 with main PR #10 integrated before review. The private launcher points there; keep it available. Original selected OpenAI profile remains unchanged. New country/route guidance and admin themes are implemented, with 76/102 reviewed readable fields versus historical 79/102; do not silently promote the context profile, repeat completed calls, or resume the stopped historical comparison. This task authorizes the checked PR, not its merge or later milestones. Older no-inference/31-profile snapshots below belong to completed work.

**Cloud credentials — 13 October:** Markus requested AWS and Google credentials directly in root `.env`, with no interactive setup. Explicit `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (optional `AWS_SESSION_TOKEN`) now override AWS profile lookup. `GOOGLE_CREDENTIALS_JSON` loads authorized-user or service-account credentials in memory and overrides ADC/file lookup. Google Document AI uses OAuth identity credentials, not a Gemini-style API key. Existing credentials were migrated without generating new keys or changing identities; exact profile versions and private accounting/selection were preserved. Legacy SDK fallback remains only when explicit env credentials are absent. See [ENV_CLOUD_CREDENTIALS.md](ENV_CLOUD_CREDENTIALS.md).


## Combined integration verification — 13 October

Markus requested latest `main` merged into this branch, checked, and PR #9 merged. Integrated base: `08de9e15c20e468ea87caf0a5df9132b845c8486` (PR #7), which includes PR #8’s native glass/hotspot/Send changes. Only AGENTS.md and CODING_HANDOFF.md conflicted; both scopes were retained. No application conflict required a code change.

The combined source passed **730 offline backend/evaluation tests**, with domain/orchestration **96.09% statement / 91.41% branch coverage**. Ruff lint/format, strict mypy, coverage gate, unchanged generated API contracts, admin JavaScript syntax, resolved diff checks, wheel/sdist builds and package privacy checks passed. The 25-slide presentation build/check passed with notes/assets intact and private gallery excluded.

On a newly created isolated iPhone 16 Pro / iOS 26.2 simulator, **27 unit/recovery tests and all four synthetic UI tests passed** (31 total, zero failures/skips). Swift formatting passed. Private native logs/result bundle are under this worktree’s `.local/merge-main-2026-10-13/`; no phone installation, live service restart, invoice inference or private configuration/selection change occurred. Main’s approved removal of local financial admission limits and European endpoint support are retained; legacy accounting records are unchanged.


**Current provider request status — 13 October:** 31 enabled/configured profiles remain after Fireworks/Aya removal. Latest processing evidence: **27 profiles completed without API errors**, **two retain last-request failures** (Haiku 4.5 availability/connection error; Mistral Large 4 timeout), and **two AWS profiles have verified authentication but untested processing**. Google OCR and Invoice processing now pass. Incomplete drafts are successful requests requiring review, not API failures. See [API_CONNECTION_STATUS.md](API_CONNECTION_STATUS.md) for every current profile and [LLM_EXPANSION.md](LLM_EXPANSION.md) for implementation scope. No new inference/runtime/configuration change is part of this documentation closeout.


## Latest source follow-up — 12 October

Markus authorized PR #7 to support explicitly configured European OpenAI/Mistral endpoints without blocking profiles for missing regional account approval. Supplier eligibility and training controls are documented in [EUROPEAN_DATA_POLICY.md](EUROPEAN_DATA_POLICY.md). He subsequently explicitly approved removing local spending and cumulative-call enforcement, including configuration-plan matching and pricing/ceiling prerequisites. Legacy configuration and retained accounting records remain compatible, but they do not control request admission. Authentication, explicit operator enablement, queue capacity, supported destinations and one-attempt/idempotency behavior remain. This supersedes earlier financial-limit instructions for this source change. Keep the actual service and private selection intact; the source revision does not deploy itself or authorize restarting interrupted evaluations. Latest `main` at `fdfc3bb` is integrated, retaining PR #8’s native Liquid Glass, Send and hotspot behavior. The combined source passes 705 backend/evaluation tests plus 27 native unit/recovery and four synthetic UI tests, with unchanged wire schemas; see current status for verification.

## Current scope — 13 October 2026

Read [CURRENT_STATUS.md](CURRENT_STATUS.md) first. **Latest follow-up:** Markus authorized the scoped Liquid Glass/motion update and hotspot verification; see [IOS_GLASS_AND_MOTION.md](IOS_GLASS_AND_MOTION.md). The subsequent user decision keeps only hotspot in the client, with one saved Mac address and no USB fallback; hosting is deferred. The previous import-only limits below describe the completed presentation task. Application PRs #2–#5 are merged. The initial presentation was delivered and revised with Markus on 9 October; it is now maintained in [presentation/](../presentation/README.md). Earlier instructions to start a presentation chat or treat the deck as unstarted are historical.

Markus authorized the repository import and the separately requested provider expansion, removal, Google verification and documentation commit/push. Current provider implementation and live status are in LLM_EXPANSION.md and API_CONNECTION_STATUS.md. Preserve the approved 25-slide story, English slides, Croatian notes and dated evaluation evidence. The editable source is `presentation/index.html`; `npm run content` regenerates `docs/PRESENTATION_CONTENT.md`. Keep `docs/PRESENTATION_EVIDENCE.md` as the authoring record. Build outputs, dependencies and optional private invoice assets stay ignored. No backend or mobile feature work, paid inference, experiment rerun or public deployment is part of this cleanup.

## What comes next

The initial presentation is available for review and use. Agree the remaining iOS improvements and real-invoice testing with Markus before starting them. Then continue backend/admin work and integration testing, Android and both-platform testing as the final development milestone, and finally the comprehensive final presentation plus embeddable website HTML. See [ROADMAP.md](ROADMAP.md). Do not create another chat automatically.

## Runtime and preservation

- The private remote is `git@github.com:azikus/scan-and-pay-poc.git`. Inspect current branches and preserve existing files. No force push or public publication.
- Source layout: `backend/`, `frontend/admin/`, `ios/`, README-only `android/`, and `presentation/`. Shared contracts/evaluation/docs remain at the root. The backend wheel bundles frontend assets internally as `backend/admin_assets/`.
- The one-process backend uses `.local/backend/`. Start with `.venv/bin/scanpay-serve` from the root. Existing private launcher/PID/log remain `.local/mobile-live-2026-10-09/serve.py`, `server.pid`, `server.log`. Verify actual owner and idle state before any restart. It follows private local addresses automatically; the phone uses one explicit saved hotspot URL.
- [Current status](CURRENT_STATUS.md) records the latest read-only ledger, budget-plan reference, selected exact profile and dated phone checks. Read actual live state before operations. Do not reset the admin selection or credentials to an older document snapshot.
- The 9 October allowance extension authorizes only explicit mobile Sends, within its cumulative limits and the EUR500 project cap. The separately interrupted comparison run was stopped by Markus; it must not resume without renewed authorization.
- Preserve root `.env`, SDK credential stores, private provider configuration, original ledger, raw responses, samples, labels, scan artifacts and confirmed edits. Never commit them. The normal presentation build excludes real invoice pixels; the explicit private build is local only.
- Preserve iOS bundle ID `com.azikus.scanpay.poc`, Keychain token and draft recovery data. Reconnect uses authenticated reads and does not dispatch a scan. Every draft requires review; Pay records a simulated confirmation and resets capture, with no payment execution.

## Evidence and verification

The application checks in [CONNECTION_SETUP.md](CONNECTION_SETUP.md) and [CONFIRMATION_SHEETS.md](CONFIRMATION_SHEETS.md) are dated implementation evidence, not new tests from this presentation import. The deck uses retained comparisons, including their incomplete labels and development-sample caveats. Budget reservations are not billed charges; backend-stage latency is not camera-to-review latency. Do not infer whole-invoice accuracy or production readiness.

## Read order

AGENTS.md → CURRENT_STATUS.md → this handoff → ROADMAP.md → presentation/README.md → PRESENTATION_CONTENT.md and PRESENTATION_EVIDENCE.md. For application changes also consult README, IMPLEMENTATION_STATUS, API_CONTRACT, ARCHITECTURE, OPERATIONS and the affected platform README. PRESENTATION_HANDOFF and PRESENTATION_PROMPT now support continuing the existing deck. Historical Phase 2 records retain their original scope and results.
