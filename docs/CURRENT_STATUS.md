# Current project status — 13 October 2026

## SUNMI PR closeout — 13 October

Markus authorized creating and merging the completed SUNMI branch and archiving this chat. Scope includes live-only dual-display telemetry, circular component animations, title transitions, provider choice for the next individual scan, right-hand live scan insights, completion styling and the installed mobile dark theme. Requested footer/completion labels are removed. Running every model for a selected method was estimated only and is not implemented or enabled.

Final checks: 775 offline backend tests; domain/orchestration coverage 96.27% statements / 91.42% branches; 32 native unit/recovery tests; seven frontend tests; Ruff, strict mypy, unchanged generated contracts, normal Android build, and wheel asset/privacy checks. The preceding visual pass also verified four native UI flows, isolated browser layouts and reduced motion. No paid inference or live provider selection change was made during closeout.

Keep the SUNMI worktree at `/Users/markusi/.codex/worktrees/sunmi-live-companion/scan-and-pay`: the existing private backend launcher still serves its source. Archiving the chat must not remove that checkout or stop the running app. Separate PR #11 retains later country-evaluation source/documentation changes not incorporated into this SUNMI branch; its earlier invoice-context implementation was integrated to preserve the installed runtime. Phone foregrounding and real confirmation-animation acceptance remain user checks.

## Display motion and mobile dark mode — 13 October

The live SUNMI views now animate outgoing/incoming titles, enlarge the circular component illustrations, and show an animated active component in the center. A right-hand panel shows the actual providers/models, observed backend elapsed time and four recent journey events. Heartbeat repetitions are coalesced; prior journeys are excluded; terminal backend timings stop and disconnected timings freeze. The customer view uses one large active illustration. Saved confirmation triggers a drawn checkmark, two expanding rings and 32 particles matching the mobile celebration; provider responses and failures cannot trigger it. Reduced Motion removes spatial/repeating effects. No synthetic playback or new data endpoint was added.

The native app now uses dark glass across capture, crop, preview, review, confirmation, settings and completion. Semantic text colours and the reversed Azikus mark preserve contrast; source document pixels are unchanged. The signed update was installed in place on the existing paired iPhone 16 Pro and the SUNMI companion was relaunched. Existing tokens, selected provider and stored drafts are retained. No backend restart or agent inference was needed.

Verification: seven frontend projection/selection/timing tests, isolated browser checks at 1280 × 720, 1280 × 800 and 1920 × 1080 (including hybrid stages, completion and reduced motion), and all four existing offline native UI flows pass. Native review/completion screenshots were inspected. Real-device confirmation animation acceptance remains for Markus’s next scan; no live confirmation was submitted by the agent.

## Live-only SUNMI display — 13 October

Markus confirmed the feature works and requested removing demo code. Synthetic replay/fabricated state, the standalone rehearsal server, the offline display-test source/app and Android development bootstrap/capture hooks are removed. The rebuilt companion is non-debuggable and installed with its existing saved connection and screen mode. Live circular animations, idle QR, provider selection, reconnect and privacy masking remain. `/demo` and `/v1/demo/*` are retained as compatibility names for actual live telemetry; the existing mobile toggle and separate simulated payment confirmation are unchanged. Six frontend tests and 23 backend review/demo tests passed. Earlier replay/setup references below are historical. See [current setup](../sunmi/companion/README.md#live-only-deployment--13-october).


## SUNMI visual and provider controls update — 13 October

Markus requested improved animations, illustrated components around a circular path with arrows, and next-scan provider selection within the display app. These are implemented and installed on the connected SUNMI. Controls reuses the existing exact-profile selection endpoint, applies only to new Sends, and is disabled in synthetic replay. The original selection was preserved; isolated fake-provider writes verified saving and refresh persistence. Six frontend checks and 23 backend review/demo tests passed. App-owned captures verified actual WebView layout and provider controls; the saved Scan & Pay two-screen mode is restored. See [display details](../frontend/demo/README.md#circular-journey-and-next-scan-controls--13-october). No paid inference, provider/configuration change or backend restart was performed.


## SUNMI installation — 13 October

Markus authorized and received the connected-device installation. Current main, invoice-context changes and explicit cloud credentials were integrated into the SUNMI worktree before deployment. The original private launcher now runs this worktree’s source while retaining the original environment/database. The existing mobile app was upgraded, Demo displays enabled, and the new SUNMI companion installed beside AirScreen. Real device rendering verifies the connected idle QR; Markus confirmed the screen followed his real scan and returned to the QR after he dismissed the result. All 2,379 original reservations, all 32 profiles, prior reviews, backend identity and the selected OpenAI mini definition were preserved; the user’s single scan brought the reservation count to 2,380. Root environment and provider configuration hashes are unchanged. Pay confirmation and live mode-switch/headset continuity remain unverified in this installation rehearsal. Checks passed: 775 backend tests, 32 native unit/recovery tests, four frontend projection tests, signed device builds. See [installation and launch instructions](../sunmi/companion/README.md#physical-installation--13-october). The earlier “not installed / runtime unchanged” paragraph below records the prior source-only checkpoint. Keep this worktree available while the live backend uses it.


## SUNMI worktree continuation — 13 October

Markus approved starting the SUNMI implementation in a separate worktree. `codex/sunmi-live-companion` starts from iOS commit `e76e303`; the original checkout and live runtime remain unchanged. The first source implementation adds sanitized backend snapshots/SSE, actual transport events, optional iPhone lifecycle telemetry, three Azikus display views with idle website QR, and a separate Android display host with manual Vision Pro / Scan & Pay modes. The approved deck and external static website remain unchanged.

Offline checks passed: 698 backend tests (backend 96.53% statements / 90.91% branches), 29 native unit/recovery tests, four existing native UI tests, four frontend projection tests, static checks, Android build/signature and installed-wheel assets. Browser checks cover both target display sizes, explicit replay and authenticated synthetic idle updates. See [setup and remaining physical checks](../sunmi/companion/README.md) and the [approved plan](SUNMI_DEMO_IMPLEMENTATION_PLAN.md).

This networked package has not yet replaced the accepted offline test on the SUNMI. Physical installation/mode switching, live iPhone/WebView integration and measured display latency remain open. No paid calls, primary-checkout edits, phone migration, live runtime restart or changes to the original ledger/selection were made. The previous AirScreen plus offline-companion hardware acceptance is retained as a separate result.



## Invoice context follow-up — 13 October

The separately requested [invoice context implementation](INVOICE_CONTEXT.md) starts from merged PR #9. One opt-in extraction call adds issuer/language explanations; backend route rules distinguish missing required fields from optional/not-applicable fields. Admin adds country flags/evidence and System/Light/Dark themes; iOS uses the applicability guidance while preserving original JSON and recovery.

Fresh authorized testing covered all 37 distinct images once: zero API errors, two success/35 incomplete drafts, 76/102 accepted readable reviewed fields (historical same-model baseline 79/102). The new prompt is separately selectable and is not promoted as an accuracy improvement. Original selection remains unchanged; 32 profiles are now configured. Ledger is 2,379 reservations after exactly 37 additions, with all original rows preserved. Service source is this invoice-context worktree. Checks: 752 backend tests, 30 native unit/recovery plus four UI tests, and browser theme/responsive checks. See the linked record for costs, latency, caveats and private evidence locations. This current scope supersedes the completed integration-only restrictions below.

**Cloud credentials — 13 October:** Markus requested AWS and Google credentials directly in root `.env`, with no interactive setup. Explicit `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (optional `AWS_SESSION_TOKEN`) now override AWS profile lookup. `GOOGLE_CREDENTIALS_JSON` loads authorized-user or service-account credentials in memory and overrides ADC/file lookup. Google Document AI uses OAuth identity credentials, not a Gemini-style API key. Existing credentials were migrated without generating new keys or changing identities; exact profile versions and private accounting/selection were preserved. Legacy SDK fallback remains only when explicit env credentials are absent. See [ENV_CLOUD_CREDENTIALS.md](ENV_CLOUD_CREDENTIALS.md).


## Combined integration verification — 13 October

Markus requested latest `main` merged into this branch, checked, and PR #9 merged. Integrated base: `08de9e15c20e468ea87caf0a5df9132b845c8486` (PR #7), which includes PR #8’s native glass/hotspot/Send changes. Only AGENTS.md and CODING_HANDOFF.md conflicted; both scopes were retained. No application conflict required a code change.

The combined source passed **730 offline backend/evaluation tests**, with domain/orchestration **96.09% statement / 91.41% branch coverage**. Ruff lint/format, strict mypy, coverage gate, unchanged generated API contracts, admin JavaScript syntax, resolved diff checks, wheel/sdist builds and package privacy checks passed. The 25-slide presentation build/check passed with notes/assets intact and private gallery excluded.

On a newly created isolated iPhone 16 Pro / iOS 26.2 simulator, **27 unit/recovery tests and all four synthetic UI tests passed** (31 total, zero failures/skips). Swift formatting passed. Private native logs/result bundle are under this worktree’s `.local/merge-main-2026-10-13/`; no phone installation, live service restart, invoice inference or private configuration/selection change occurred. Main’s approved removal of local financial admission limits and European endpoint support are retained; legacy accounting records are unchanged.


**Main integration — 13 October:** Latest `main` is merged into this provider branch, retaining PR #8’s glass/hotspot/Send changes and PR #7’s European endpoint support and approved removal of local spending/cumulative-call enforcement. Legacy budget-plan/cost records below remain historical evidence; they do not control admission in the updated source. This integration does not restart the live service, alter private configuration/selection or authorize provider retries.


**Current provider request status — 13 October:** 31 enabled/configured profiles remain after Fireworks/Aya removal. Latest processing evidence: **27 profiles completed without API errors**, **two retain last-request failures** (Haiku 4.5 availability/connection error; Mistral Large 4 timeout), and **two AWS profiles have verified authentication but untested processing**. Google OCR and Invoice processing now pass. Incomplete drafts are successful requests requiring review, not API failures. See [API_CONNECTION_STATUS.md](API_CONNECTION_STATUS.md) for every current profile and [LLM_EXPANSION.md](LLM_EXPANSION.md) for implementation scope. No new inference/runtime/configuration change is part of this documentation closeout.

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

Read-only snapshot on 13 October: **2,342 reservations, 2,340 dispatched / €369.60 held**. The retained legacy plan records **2,350 reservations / €370.40**, with a historical difference of **eight reservations / €0.80**. Updated source does not enforce these values; the existing process was not restarted during integration. These conservative holds are not actual provider bills; stage counts and legacy ceilings remain accounting metadata, not admission rules in the updated source.

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
