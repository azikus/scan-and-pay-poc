# Coding handoff — continue here

## Current state and authority — 9 October 2026

Read [mobile checkpoint](MOBILE_CHECKPOINT.md) first. Native iOS and the admin inspector merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2) at `62ac67da3aefd5817466e326cdd0b362ae58edd1`. Markus confirmed his real-invoice device testing is complete. The separately authorized repository reorganization uses root `backend/`, `frontend/`, `ios/` and `android/`; its validation and PR record are in [repository reorganization](REPOSITORY_REORGANIZATION_HANDOFF.md). Routine cleanup decisions are autonomous; do not repeat confirmation gates from historical handoffs.

The next joint task is **the presentation together with Markus when he returns**. Then improve the mobile client, work on the backend, and implement Android last. Do not start later features or paid experiments during repository cleanup. Keep experimental method switching for the client demonstration.

## Immediate continuation

1. Repository cleanup preserves API behavior, deployment, private evidence, ledger, selected method and the installed phone app. Use the [reorganization record](REPOSITORY_REORGANIZATION_HANDOFF.md) and actual Git/PR state for its verification and merge status.
2. Wait for Markus to build the presentation together. Use retained speed/correctness evidence; do not rerun paid evaluations for it.
3. After the presentation: improve the mobile client, then the backend, then Android. Networking reliability, paper detection and native OCR are later improvements.

## Runtime, data and operational facts

- Repository: `/Users/markusi/Developer/Azikus/scan-and-pay`; private remote `git@github.com:azikus/scan-and-pay-poc.git`. Preserve existing files and inspect active branches before edits.
- Current iOS code is `ios/`; frontend source is `frontend/admin/`. Python stays in `backend/`, with admin assets bundled internally as `backend/admin_assets/` in wheels. `android/` contains only its future-work README. The exact app bundle ID is `com.azikus.scanpay.poc`; preserve it and on-device data. Xcode signing is supplied locally, not committed.
- The one-process FastAPI backend and inspector run on the Mac with SQLite/private artifacts in `.local/backend/`. Private launcher/PID/log paths are `.local/mobile-live-2026-10-09/serve.py`, `server.pid`, and `server.log`. Do not start a second owner or stop an active job. If moves require a restart, first verify zero queued/running jobs and retain the same settings/data directory.
- Current selected profile is persisted separately in SQLite. At this checkpoint it is `mistral-small-image-roles-v3@2-b292ba761e512607`; do not reset it to the historical OpenAI baseline. Seven exact tested profiles are available via the admin's Next scan form. Pending scans retain their original choice.
- Ledger: **2,201 dispatches / €336.45 held** at checkpoint; unchanged cumulative mobile caps 2,217 / €338.05. No paid calls during PR preparation or refactor. Never rerun completed provider evaluations or reset the ledger.
- Reconnect tries saved USB then Wi-Fi addresses. Latest phone result: USB failed, Wi-Fi connected. Hotspot testing/automatic discovery remain open. Physical-device localhost is not the Mac.
- Root `.env` owns existing credentials and connection settings. Provider keys stay on the Mac, the local client token stays in Keychain, and all source invoices/labels/raw responses/results remain ignored. Preserve SDK-managed cloud authentication stores.

## Verification and limits

Reorganization checks: 672 offline backend/evaluation tests; 95.92% statement / 91.15% branch domain/orchestration coverage; Ruff lint/format, strict mypy, unchanged contract generation, JS syntax, installed-wheel serving and source-distribution rebuild pass. All 16 native unit/recovery and 2 simulator UI tests pass from `ios/`. The signed device build/install belongs to PR #2; the folder refactor does not reinstall the phone app. The user completed real-invoice testing, but no new whole-invoice accuracy or camera-to-review timing claim is made.

Every draft still requires review. Pay only records a simulated confirmation and resets the capture flow. Original extraction JSON is immutable; confirmed mobile values are separate. Preserve amount/reference/destination associations, exact digits, nulls, warnings and outcome semantics. Provider/scan text remains untrusted. No public publication, subscriptions or live payment integration.

## Read order and ownership

Read AGENTS.md, this file, MOBILE_CHECKPOINT.md, REPOSITORY_REORGANIZATION_HANDOFF.md, README.md, ROADMAP.md, IMPLEMENTATION_STATUS.md, MOBILE_IMPLEMENTATION.md and MOBILE_LIVE_TESTING.md. Then consult API_CONTRACT.md, ARCHITECTURE.md, OPERATIONS.md and the iOS README for the files affected by the refactor.

API_CONTRACT.md owns wire semantics; this handoff owns current continuation scope; ROADMAP.md owns milestone names and current sequence. PHASE2_CLOSEOUT.md and CHAT4_HANDOFF.md preserve prior checkpoints; their older no-mobile, no-PR, default-profile and budget gates are historical. Existing Python/FastAPI/Pydantic/SQLite architecture, provider-hosted inference and immutable evidence remain settled.
