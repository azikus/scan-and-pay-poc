# Coding handoff — 13 October 2026

Read [current status](CURRENT_STATUS.md), [roadmap](ROADMAP.md) and `AGENTS.md` first. They supersede historical prospective instructions, budget snapshots and worktree-retention notes.

## Current scope

Markus skipped the Android capture/review PoC and comprehensive final presentation. Keep the delivered initial deck and existing Webflow showcase; do not start replacement deliverables. iOS, automatic document capture, backend/admin integration and SUNMI are accepted for the current PoC. Markus confirmed the repaired backend's explicit phone Send works; no additional Send acceptance gate remains.

Repository cleanup/documentation reconciliation is complete; see REPOSITORY_CLEANUP.md. Additional provider runs are the next task: agree profiles, complete input inventory and repeat count, record a new plan and request keys, then dispatch only that fresh scope. Do not resume stopped historical comparisons or retry failed old jobs. Cleanup makes no inference calls and changes no runtime/private state.

## Source and runtime

- Private remote: `git@github.com:azikus/scan-and-pay-poc.git`; PRs #1–#13 are merged. Start follow-up source work from current main, preserve local files and use checked normal closeout; no force push/public publication.
- Source: `backend/`, `frontend/admin/`, `frontend/demo/`, `ios/`, `sunmi/`, `presentation/`, `website/`. `android/README.md` records the skip. Backend wheels bundle admin and live-display assets.
- Live source is `.local/runtime-source/269e0223580ecba96793d9382c3efcffa77d720e/` in the original checkout, launched via `.local/mobile-live-2026-10-09/serve.py`; data stays in `.local/backend/`. Removed managed worktrees are not required. Keep the stable archive, launcher and one service owner intact.
- No restart, phone reinstall, selection/configuration/accounting edit or inference is needed for cleanup. Before future service operations, inspect actual owner/idle state and preserve pending work.
- Keep root `.env`, SDK credentials, `.local/providers.json`, SQLite, original images/raw responses/labels/keys/reviews/identity and phone Keychain/Application Support private. Explicit AWS keys/Google credential JSON in `.env` override native credential lookup. Never expose credential values.

## Product invariants

Preserve hotspot-only saved-address networking, authenticated reconnect, explicit Send, frozen idempotent recovery, dark glass, automatic scanning/manual fallback/full-photo crop recovery, source/edit separation and late-result isolation. Keep method/model selection and standard country context. Confirmation is simulated; every draft requires review, with useful incomplete fields retained and no invented values. Display observation/reconnect/confirmation must not cause inference. Barcode/QR payload decoding, real payment-service integration and hosted deployment remain outside scope.

## Provider follow-up

Use [API connection evidence](API_CONNECTION_STATUS.md), [LLM expansion](LLM_EXPANSION.md), [invoice context](INVOICE_CONTEXT.md), [evaluation plan](EVALUATION_PLAN.md) and [cost report guidance](COST_REPORT_PLAN.md). Active profiles and readiness must come from actual runtime/configuration, not an older count/selection snapshot. Main no longer enforces local financial/cumulative-call caps; do not reinstate historical gates. Preserve original accounting and distinguish known/estimated/unknown charges.

A fresh repeat gets new plan/keys and complete JPEG/PNG input coverage with failures/not-run records. Keep immutable versions and saved requests; never silently replace providers or change selection. Score only reviewed fields, separately count approved name variants, and report timing with sample/timeout counts and all hybrid stages. Backend latency is not camera-to-review latency; successful API requests are not verified invoices.

## Read map

| Work | Documentation |
| --- | --- |
| Current state/scope/cleanup | CURRENT_STATUS.md, ROADMAP.md, REPOSITORY_CLEANUP.md |
| API/runtime/private setup | README.md, API_CONTRACT.md, ARCHITECTURE.md, OPERATIONS.md, ENV_CLOUD_CREDENTIALS.md |
| Native capture/recovery | ../ios/README.md, IOS_DOCUMENT_SCANNING.md, IOS_GLASS_AND_MOTION.md, CONFIRMATION_SHEETS.md |
| Display companion | ../frontend/demo/README.md, ../sunmi/companion/README.md |
| Existing deck/showcase | ../presentation/README.md, PRESENTATION_EVIDENCE.md, ../website/README.md, ../website/HANDOFF.md |
| Evaluation history | IMPLEMENTATION_STATUS.md, PHASE2_CLOSEOUT.md, M3_DIRECT_PROVIDER_RESULTS.md, INVOICE_CONTEXT.md |

Retain historical evidence and its caveats; older instructions do not reopen completed or skipped tasks. Do not create a new chat or schedule work automatically.
