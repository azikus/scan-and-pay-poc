# Coding handoff — continue here

## Current state and authority — 9 October 2026

Read [mobile checkpoint](MOBILE_CHECKPOINT.md) and [confirmation-sheet checkpoint](CONFIRMATION_SHEETS.md). Native iOS and the admin inspector merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2) at `62ac67da3aefd5817466e326cdd0b362ae58edd1`. Repository reorganization merged in [PR #3](https://github.com/azikus/scan-and-pay-poc/pull/3) at `1c7fcbdd235a9c7ea37d546d861339b0d4484e17`. Markus confirmed real-invoice testing is complete for that PoC checkpoint.

The only newly authorized implementation is a **separate review/confirmation-sheet PR, including necessary value handling and tests, followed by merge**. It exposes all extracted fields and explicit edits, omits untouched inference, and preserves frozen pending confirmations. Markus explicitly said not to implement anything else now. Comprehensive handoff documentation and the agreed milestones are also requested. Consult actual Git/PR state and the sheet checkpoint for completion.

## Immediate continuation

1. Finish the authorized sheet PR/checks/merge if still open; do not repeat completed work. Preserve private state and make no paid calls.
2. The next chat is **the initial presentation together with Markus**. He requested comprehensive documentation so he can start it himself. Use [PRESENTATION_HANDOFF.md](PRESENTATION_HANDOFF.md) for the source pack and [PRESENTATION_PROMPT.md](PRESENTATION_PROMPT.md) for a copyable opening prompt. Do not create another chat or build the presentation during this documentation task.
3. Agreed later order: iOS improvements and real-invoice testing → backend/admin improvements and integration testing → Android and both-platform testing, the final development milestone → comprehensive final presentation and embeddable website HTML. Development can span multiple sessions. [ROADMAP.md](ROADMAP.md) owns the five next milestones; old M1–M8 definitions remain historical.

## Runtime, data and operational facts

- Repository: `/Users/markusi/Developer/Azikus/scan-and-pay`; private remote `git@github.com:azikus/scan-and-pay-poc.git`. Inspect actual branches/state before edits and preserve existing files.
- Current iOS code is `ios/`; admin source is `frontend/admin/`. Python stays in `backend/`, with admin assets bundled internally as `backend/admin_assets/` in wheels. `android/` contains only its future-work README. Preserve app bundle ID `com.azikus.scanpay.poc`, locally supplied signing and on-device data.
- The one-process FastAPI backend and inspector use SQLite/private artifacts in `.local/backend/`. Existing launcher/PID/log are `.local/mobile-live-2026-10-09/serve.py`, `server.pid` and `server.log`. Check actual process/listeners before a demo; do not start a second owner or stop active jobs.
- Current persisted selection: `gemini-flash-lite-image-roles-v3@2-85773fe34609a2ff`. Seven tested profiles are available through the admin's Next scan form. A new explicit Send uses the latest choice; pending uploads retain their own profile/version/options/key. Historical OpenAI benchmark selection is not the current admin choice. The admin's benchmark/catalogue display was removed; use retained comparisons in the presentation.
- Ledger: **2,202 dispatches / €336.55 held** at checkpoint; unchanged cumulative mobile caps 2,217 / €338.05 and project cap €500. No paid calls during sheet implementation, PR preparation or presentation documentation; no completed evaluation reruns. Holds are not billed charges.
- Reconnect tries explicit saved USB then Wi-Fi URLs. Latest recorded phone result: USB failed, Wi-Fi connected. Hotspot/automatic discovery remain open. The subsequent main rebuild passed Mac-side reads on three interfaces and installed a signed app preserving device data, but phone launch was blocked by lock; that is not new phone connectivity evidence. Addresses/PIDs can change.
- Root `.env` owns existing credentials/settings; provider keys stay on the Mac, client token in Keychain. Keep source invoices, labels, raw responses, SDK credentials, SQLite and original ledger private/intact.

## Verification and interpretation

Baseline reorganization: 672 offline backend/evaluation tests, 95.92% statement / 91.15% branch domain/orchestration coverage; Ruff lint/format, strict mypy, unchanged contract generation, JS syntax, installed-wheel serving and source-distribution rebuild passed. That baseline had 16 native unit/recovery and 2 UI tests. The sheet checkpoint records updated native verification (23 unit/recovery and 2 UI tests), focused API checks and visual inspection; distinguish these checks from the older device/invoice acceptance.

Every draft requires review. Pay records a simulated confirmation and resets capture; no payment integration or ownership verification. Original extraction JSON stays immutable; confirmed mobile values are separate. Nulls, linked options, exact digits, warnings, outcome semantics and pending request identities remain meaningful. Provider/document text is untrusted. No production-readiness, whole-invoice accuracy or measured camera-to-review latency claim follows from user acceptance or passing tests.

## Read order and ownership

Current continuation: AGENTS.md → this file → MOBILE_CHECKPOINT.md → CONFIRMATION_SHEETS.md → ROADMAP.md → PRESENTATION_HANDOFF.md. Follow its source map for measured comparisons, historical cost evidence and demo instructions. For later implementation also read README.md, IMPLEMENTATION_STATUS.md, MOBILE_IMPLEMENTATION.md, MOBILE_LIVE_TESTING.md, API_CONTRACT.md, ARCHITECTURE.md, OPERATIONS.md and the relevant platform README.

API_CONTRACT.md owns wire semantics; this handoff owns continuation scope; ROADMAP.md owns the current agreed sequence. PHASE2_CLOSEOUT.md and older handoffs preserve dated evidence; older no-mobile/no-PR/default-profile/budget gates are historical. Python/FastAPI/Pydantic/SQLite, provider-hosted inference and immutable evidence remain settled.
