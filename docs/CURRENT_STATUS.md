# Current project status — 12 October 2026

This file supersedes prospective wording and operational snapshots in the dated 8–9 October handoffs. Historical experiment evidence remains unchanged.

## Latest follow-up

Markus requested the bounded iOS Liquid Glass/motion update and hotspot/hosting assessment. See [implementation and connection evidence](IOS_GLASS_AND_MOTION.md). Markus clarified that scan-screen glass should replace the large black header/footer; the scan screen uses light glass panels. The subsequent live-preview framing fix fits the complete camera frame between them, avoiding aspect-fill zoom before capture. The glass treatment now extends through Adjust image, Ready to send, review, confirmation and completion, with matching light settings/document viewers. A shared Azikus / Scan & Pay header now gives each screen its own subtitle. Markus then narrowed connectivity to the working hotspot only: one saved Mac address, no USB fallback or hosted endpoint selection. This begins iOS polish without starting cloud deployment, new inference, Android or the final website milestone.

## Code and presentation

The latest iOS follow-up addresses Send remaining on Ready to send: the preview no longer intercepts taps, primary actions have explicit hit areas, and photo encoding runs off the UI thread with immediate progress. See the Send section in [IOS_GLASS_AND_MOTION.md](IOS_GLASS_AND_MOTION.md) for verification and the outstanding physical-device acceptance. No paid extraction was run by the agent.

- Application code through PRs [#2](https://github.com/azikus/scan-and-pay-poc/pull/2), [#3](https://github.com/azikus/scan-and-pay-poc/pull/3), [#4](https://github.com/azikus/scan-and-pay-poc/pull/4) and [#5](https://github.com/azikus/scan-and-pay-poc/pull/5) is merged. The last application commit is `57fa993cfd01e7533a6140d1c7a5d71f96289293`.
- The native capture/review/confirmation flow, admin inspector and automatic Mac network listeners are implemented. Android remains a README only. Source folders are `backend/`, `frontend/admin/`, `ios/` and `android/`.
- The initial presentation was created with Markus and revised on 9 October. Its approved version has **25 slides**, English slides, Croatian notes and approximately **19–20 minutes** including the live demo. The old “presentation not started” instructions are historical.
- The 12 October repository import merged in [PR #6](https://github.com/azikus/scan-and-pay-poc/pull/6), commit `75c8cd0`. It places editable HTML, theme, motion, reviewed assets and reproducible build/serve/export tooling under [presentation/](../presentation/README.md). The normal build excludes the real invoice gallery; a separate ignored local edition preserves it. The original external deck is untouched.
- [PRESENTATION_CONTENT.md](PRESENTATION_CONTENT.md) is generated from the HTML source. [PRESENTATION_EVIDENCE.md](PRESENTATION_EVIDENCE.md) records authoring sources and revisions. Both belong in Git alongside the deck. No later application development is part of this import.

## Source follow-up — 12 October

PR #7 supports operator-selected European OpenAI/Mistral endpoints while keeping global profiles usable without verified regional approval. Supplier controls and dated checks are documented in [EUROPEAN_DATA_POLICY.md](EUROPEAN_DATA_POLICY.md). Markus explicitly approved removal of local spending/cumulative-call enforcement and accepted its risk. This source no longer requires a matching financial plan or pricing/ceiling metadata for readiness or request admission. Existing private records and profile serialization are retained. Authentication, queue capacity and idempotent recovery still apply. These source changes do not automatically redeploy the running service or modify its private configuration. The operational snapshot below is dated history, not a limit imposed by the updated source.

Source verification: **705 offline backend/evaluation tests pass**, with **96.05% statement / 91.28% branch** domain coverage. Ruff lint/format, strict mypy, unchanged generated API contracts, admin JavaScript syntax and package builds pass. Regressions cover missing cost metadata, comparisons and both hybrid stages above prior limits, legacy configuration compatibility, preserved existing records and evaluation continuation. Production source has no reads of the old cumulative limits or local-limit rejection/stop conditions. No provider inference, service restart or deployment ran for this revision.

Pre-merge integration: latest `main` at `fdfc3bb` (PR #8, Liquid Glass/hotspot and Send updates) merged cleanly into PR #7. The integrated source passes the same 705 backend/evaluation tests, all **27 native unit/recovery tests and 4 synthetic UI flows** on an isolated iPhone 16 Pro / iOS 26.2 simulator, Swift formatting checks, static/schema/package checks and the 25-slide presentation build/check. Private logs and the native result bundle are under `.local/privacy-review/`. The existing phone, simulators, service and private configuration were preserved.

## Current private state

Read-only snapshot on 12 October: **2,273 dispatched reservations / €351.95 held**. The current cumulative limits are **2,286 calls / €353.25**, leaving at most **13 calls / €1.30** at this snapshot, within the **€500 project cap**. These conservative holds are not actual provider bills; method-specific stage counts and ceilings determine how many scans fit.

Markus explicitly requested another allowance on 9 October after exhausting the prior 2,266 / €351.25 limits. The extension added **20 API calls / €2.00**, with the plan, prior configuration, original budget rows and verification under `.local/mobile-allowance-extension-00_zmrsg/`. Its scope is explicit mobile Sends. It does not authorize agents to run experiments or automatically extend limits.

The current persisted choice is **OpenAI GPT-4.1 mini**, `openai-mini-image-roles-v3@2-5094b6dc13ef5718`. This is a live selection snapshot, not a new benchmark result. Read the admin or SQLite for subsequent changes; do not reset selection to match a document.

A separately authorized comparison run on 9 October was stopped at Markus's explicit request so the phone could reconnect. Completed responses and remaining-not-run records were preserved in `.local/all-approaches-repeat-2026-10-09/`, including `user-stop-request.json` and `restore.json`. Do not resume that interrupted run without renewed authorization. The presentation's retained comparison tables remain the original dated studies and do not claim that this interrupted repeat finished.

## Device and runtime

The managed launcher is `.venv/bin/scanpay-serve`; the private `serve.py` delegates to it. It follows local interface changes automatically while keeping a single backend owner. The app now uses one saved editable hotspot address, not automatic discovery. The hotspot-only build authenticated on the physical iPhone at 21:31:30 UTC on 12 October using `http://172.20.10.2:8000`; 24 offline native unit/recovery tests passed. Do not restart an active extraction job or launch a second owner against the same database.

Physical-phone checks on 9 October verified USB at 11:17:20 UTC, hotspot Wi-Fi at 11:21:41 UTC, and ordinary Wi-Fi at 18:18:55 UTC. The last saved phone URL was `http://192.168.1.134:8000`. These are dated successful checks, not a guarantee of today's connectivity or IP address. Evidence is under `.local/phone-reconnect-2026-10-09/` and `.local/phone-wifi-reconnect-w0txfh0w/`. The later idle restart applied the authorized allowance; loopback and Wi-Fi authenticated reads returned 200.

Root `.env`, SDK credentials, `.local/providers.json`, SQLite, original ledger, scan artifacts, saved edits and device data remain private. Repository/presentation housekeeping must make no inference calls or change these records.

## Verification and next milestones

The last application verification remains the PR #5 checkpoint: **690 offline backend tests**, **96.03% statements / 91.25% branches**, static/contract/package checks and listener/browser checks. The sheet checkpoint had **23 native unit/recovery and 2 UI tests**. Those dated results are not claimed as new application tests during this presentation-only import. Presentation build, asset/export checks and browser verification are recorded with this change.

Initial presentation delivered → agree remaining **iOS improvements and real-invoice testing** → backend/admin work and integration testing → Android and both-platform testing as the last development milestone → comprehensive final presentation and embeddable website HTML. The initial reveal.js deck is separate from that final website deliverable. No later milestone starts automatically.
