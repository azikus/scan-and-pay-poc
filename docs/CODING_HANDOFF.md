# Coding handoff — continue here

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


## Latest authorized work — SUNMI companion, 13 October 2026

Continue in the managed `sunmi-live-companion` worktree on `codex/sunmi-live-companion`, based on `e76e303`. Markus explicitly requested this separate worktree after approving the display plan. This authorization supersedes the historical presentation-import-only gate for this scoped companion work. Read [SUNMI implementation plan](SUNMI_DEMO_IMPLEMENTATION_PLAN.md) and [source implementation/setup/evidence](../sunmi/companion/README.md). Backend, iPhone observer, web views and native host are source-implemented and offline-checked; physical live integration remains pending. Preserve the working AirScreen/offline-test baseline, the current iOS UX and live private state. Do not infer paid-call authorization from display testing or launch a second owner against the live database. No separate chat was created.




## Invoice context follow-up — 13 October

Read [INVOICE_CONTEXT.md](INVOICE_CONTEXT.md) for the latest separate PR scope, exact new profile, 37 completed paid runs, verification and preservation audit. Source is in the managed `invoice-context-review` worktree on `codex/invoice-context-review`, based on merged PR #9. The private launcher points there; keep it available. Original selected OpenAI profile remains unchanged. New country/route guidance and admin themes are implemented, with 76/102 reviewed readable fields versus historical 79/102; do not silently promote the context profile, repeat completed calls, or resume the stopped historical comparison. This task authorizes the checked PR, not its merge or later milestones. Older no-inference/31-profile snapshots below belong to completed work.

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
