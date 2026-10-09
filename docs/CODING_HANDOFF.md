# Coding handoff — continue here

## Current state and authority — 9 October 2026

Read [mobile checkpoint](MOBILE_CHECKPOINT.md) first. Native iOS and the admin inspector are implemented, and Markus confirmed his real-invoice device testing is complete. The current mobile/admin changes are authorized for review, checks, commit/push, PR and merge. A second, separate chat is explicitly authorized to reorganize the repository, verify it, update status/documentation, and create/merge its own PR. Routine decisions are autonomous; do not repeat confirmation gates from historical handoffs.

After those two steps, **the presentation must be created together with Markus when he returns**. Then improve the mobile client, work on the backend, and implement Android last. Do not start later features or paid experiments during repository cleanup. Keep experimental method switching for the client demonstration.

## Immediate continuation

1. Review/check/merge the current mobile/admin checkpoint, including status/docs. Use the actual Git/PR state to establish completion; never infer a merge from a planned task.
2. Start the explicitly requested separate local chat from the merged checkpoint. Its scope is [repository reorganization](REPOSITORY_REORGANIZATION_HANDOFF.md): root `backend/`, `frontend/`, `ios/`, `android/`, with backend/frontend allowed to remain one deployment. Android gets documentation only, not implementation.
3. Verify builds, tests, packaging, paths, private-state preservation and the local inspector; then create and merge the refactor PR after checks. Update the status/handoff with concrete results and PR links. No force push or branch-protection bypass.
4. Leave the project ready for the joint presentation. Networking reliability, paper detection, native OCR and new backend functionality are later improvements.

## Runtime, data and operational facts

- Repository: `/Users/markusi/Developer/Azikus/scan-and-pay`; private remote `git@github.com:azikus/scan-and-pay-poc.git`. Preserve existing files and inspect active branches before edits.
- Current iOS code is `apps/ios/`; current frontend assets are `backend/admin_assets/`. The upcoming refactor changes these paths. The exact app bundle ID is `com.azikus.scanpay.poc`; preserve it and on-device data. Xcode signing is supplied locally, not committed.
- The one-process FastAPI backend and inspector run on the Mac with SQLite/private artifacts in `.local/backend/`. Private launcher/PID/log paths are `.local/mobile-live-2026-10-09/serve.py`, `server.pid`, and `server.log`. Do not start a second owner or stop an active job. If moves require a restart, first verify zero queued/running jobs and retain the same settings/data directory.
- Current selected profile is persisted separately in SQLite. At this checkpoint it is `mistral-small-image-roles-v3@2-b292ba761e512607`; do not reset it to the historical OpenAI baseline. Seven exact tested profiles are available via the admin's Next scan form. Pending scans retain their original choice.
- Ledger: **2,201 dispatches / €336.45 held** at checkpoint; unchanged cumulative mobile caps 2,217 / €338.05. No paid calls during PR preparation or refactor. Never rerun completed provider evaluations or reset the ledger.
- Reconnect tries saved USB then Wi-Fi addresses. Latest phone result: USB failed, Wi-Fi connected. Hotspot testing/automatic discovery remain open. Physical-device localhost is not the Mac.
- Root `.env` owns existing credentials and connection settings. Provider keys stay on the Mac, the local client token stays in Keychain, and all source invoices/labels/raw responses/results remain ignored. Preserve SDK-managed cloud authentication stores.

## Verification and limits

Final checkpoint checks: 672 offline backend/evaluation tests; 95.92% statement / 91.20% branch domain/orchestration coverage; Ruff lint/format, strict mypy, contract generation and JS syntax pass. All 16 native unit/recovery and 2 simulator UI tests pass; signed device build succeeds. The user completed real-invoice testing, but no new whole-invoice accuracy or camera-to-review timing claim is made.

Every draft still requires review. Pay only records a simulated confirmation and resets the capture flow. Original extraction JSON is immutable; confirmed mobile values are separate. Preserve amount/reference/destination associations, exact digits, nulls, warnings and outcome semantics. Provider/scan text remains untrusted. No public publication, subscriptions or live payment integration.

## Read order and ownership

Read AGENTS.md, this file, MOBILE_CHECKPOINT.md, REPOSITORY_REORGANIZATION_HANDOFF.md, README.md, ROADMAP.md, IMPLEMENTATION_STATUS.md, MOBILE_IMPLEMENTATION.md and MOBILE_LIVE_TESTING.md. Then consult API_CONTRACT.md, ARCHITECTURE.md, OPERATIONS.md and the iOS README for the files affected by the refactor.

API_CONTRACT.md owns wire semantics; this handoff owns current continuation scope; ROADMAP.md owns milestone names and current sequence. PHASE2_CLOSEOUT.md and CHAT4_HANDOFF.md preserve prior checkpoints; their older no-mobile, no-PR, default-profile and budget gates are historical. Existing Python/FastAPI/Pydantic/SQLite architecture, provider-hosted inference and immutable evidence remain settled.
