# Coding handoff — continue here

**Current provider request status — 13 October:** 31 enabled/configured profiles remain after Fireworks/Aya removal. Latest processing evidence: **27 profiles completed without API errors**, **two retain last-request failures** (Haiku 4.5 availability/connection error; Mistral Large 4 timeout), and **two AWS profiles have verified authentication but untested processing**. Google OCR and Invoice processing now pass. Incomplete drafts are successful requests requiring review, not API failures. See [API_CONNECTION_STATUS.md](API_CONNECTION_STATUS.md) for every current profile and [LLM_EXPANSION.md](LLM_EXPANSION.md) for implementation scope. No new inference/runtime/configuration change is part of this documentation closeout.

## Current scope — 13 October 2026

Read [CURRENT_STATUS.md](CURRENT_STATUS.md) first. Application PRs #2–#5 are merged. The initial presentation was delivered and revised with Markus on 9 October; it is now maintained in [presentation/](../presentation/README.md). Earlier instructions to start a presentation chat or treat the deck as unstarted are historical.

Markus authorized the repository import and the separately requested provider expansion, removal, Google verification and documentation commit/push. Current provider implementation and live status are in LLM_EXPANSION.md and API_CONNECTION_STATUS.md. Preserve the approved 25-slide story, English slides, Croatian notes and dated evaluation evidence. The editable source is `presentation/index.html`; `npm run content` regenerates `docs/PRESENTATION_CONTENT.md`. Keep `docs/PRESENTATION_EVIDENCE.md` as the authoring record. Build outputs, dependencies and optional private invoice assets stay ignored. No backend or mobile feature work, paid inference, experiment rerun or public deployment is part of this cleanup.

## What comes next

The initial presentation is available for review and use. Agree the remaining iOS improvements and real-invoice testing with Markus before starting them. Then continue backend/admin work and integration testing, Android and both-platform testing as the final development milestone, and finally the comprehensive final presentation plus embeddable website HTML. See [ROADMAP.md](ROADMAP.md). Do not create another chat automatically.

## Runtime and preservation

- The private remote is `git@github.com:azikus/scan-and-pay-poc.git`. Inspect current branches and preserve existing files. No force push or public publication.
- Source layout: `backend/`, `frontend/admin/`, `ios/`, README-only `android/`, and `presentation/`. Shared contracts/evaluation/docs remain at the root. The backend wheel bundles frontend assets internally as `backend/admin_assets/`.
- The one-process backend uses `.local/backend/`. Start with `.venv/bin/scanpay-serve` from the root. Existing private launcher/PID/log remain `.local/mobile-live-2026-10-09/serve.py`, `server.pid`, `server.log`. Verify actual owner and idle state before any restart. It follows private local addresses automatically; the phone still uses explicit saved URLs.
- [Current status](CURRENT_STATUS.md) records the latest read-only ledger, budget-plan reference, selected exact profile and dated phone checks. Read actual live state before operations. Do not reset the admin selection or credentials to an older document snapshot.
- The 9 October allowance extension authorizes only explicit mobile Sends, within its cumulative limits and the EUR500 project cap. The separately interrupted comparison run was stopped by Markus; it must not resume without renewed authorization.
- Preserve root `.env`, SDK credential stores, private provider configuration, original ledger, raw responses, samples, labels, scan artifacts and confirmed edits. Never commit them. The normal presentation build excludes real invoice pixels; the explicit private build is local only.
- Preserve iOS bundle ID `com.azikus.scanpay.poc`, Keychain token and draft recovery data. Reconnect uses authenticated reads and does not dispatch a scan. Every draft requires review; Pay records a simulated confirmation and resets capture, with no payment execution.

## Evidence and verification

The application checks in [CONNECTION_SETUP.md](CONNECTION_SETUP.md) and [CONFIRMATION_SHEETS.md](CONFIRMATION_SHEETS.md) are dated implementation evidence, not new tests from this presentation import. The deck uses retained comparisons, including their incomplete labels and development-sample caveats. Budget reservations are not billed charges; backend-stage latency is not camera-to-review latency. Do not infer whole-invoice accuracy or production readiness.

## Read order

AGENTS.md → CURRENT_STATUS.md → this handoff → ROADMAP.md → presentation/README.md → PRESENTATION_CONTENT.md and PRESENTATION_EVIDENCE.md. For application changes also consult README, IMPLEMENTATION_STATUS, API_CONTRACT, ARCHITECTURE, OPERATIONS and the affected platform README. PRESENTATION_HANDOFF and PRESENTATION_PROMPT now support continuing the existing deck. Historical Phase 2 records retain their original scope and results.
