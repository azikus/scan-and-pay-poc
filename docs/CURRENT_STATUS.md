# Current project status — 12 October 2026

**Latest scope — 13 October:** Markus requested complete Fireworks removal and removal of Cohere Aya Vision. Their adapters, provider registration, admin labels, credential placeholders and six presets are removed; the private live catalogue has **31 enabled/configured profiles**. Existing ledger rows, selected exact profile, backend identity, budget caps and all remaining profile metadata were verified unchanged after an idle restart. No paid inference ran. Claude Haiku 4.5’s dated provider_unavailable result is an availability/connection failure, not evidence of unsuccessful Anthropic setup; Haiku 5.5 succeeded with the same provider access. The old baseline remains independently versioned alongside 5.5. This supersedes previous all-37-enabled scope; dated results below remain historical evidence.


**Latest all-catalogue scope — 12 October:** Markus subsequently requested “enable everything and run it, don’t disable anything”, supplied Cohere access and authorized a fresh one-invoice run. All **37 catalogue profiles across 12 providers** are enabled/configured in the original private runtime, including restored cloud/document services, Grok, Aya Vision, DeepSeek, GLM, Llama, Kimi K2.5 and both legacy profiles. Individual failures do not disable entries. See [ALL_CATALOGUE_LIVE_2026-10-12.md](ALL_CATALOGUE_LIVE_2026-10-12.md). The fresh plan permits up to 38 stage calls / EUR10.55 holds, cumulative caps 2,350 / EUR370.40. Completed 35 profiles: 12 success / 15 incomplete / 8 error; AWS’s two profiles were skipped at Markus’s request and remain enabled. Latest ledger: 2,340 reservations / 2,338 dispatched, EUR369.30 held; caps 2,350 / EUR370.40. Original rows, selection and identity preserved. Preserve actual selection, all ledger rows and stopped historical comparisons. No subscription, deployment or automatic retry is authorized. Earlier disabled/no-inference notes below describe prior checkpoints.


**Latest paid LLM follow-up — 12 October:** the user-requested single-invoice run is complete; see [LLM_LIVE_SMOKE_2026-10-12.md](LLM_LIVE_SMOKE_2026-10-12.md). All 19 enabled direct-image models were attempted once, with 13 successful drafts, four incomplete drafts and two timeouts; seven earlier mistaken non-invoice calls are separately accounted. Original rows/selection preserved. Latest snapshot: 2,303 / EUR358.95 held, caps 2,312 / EUR359.85, leaving nine calls / EUR0.90 for explicit mobile Sends. No new agent run/retry or historical comparison resumption is authorized.

**Separate provider work — 12 October:** Markus requested broader LLM/model support in an isolated worktree. See [LLM_EXPANSION.md](LLM_EXPANSION.md) for scope, disabled presets and verification. Markus subsequently authorized activation for existing providers: 14 new options are enabled with read-only account checks, including Fireworks Kimi K3 after its key was supplied; the original Fireworks Kimi K2.5 preset remains disabled because it lacks serverless availability. The private launcher runs this worktree against the original private state. Default/ledger/caps are unchanged; do not resume the interrupted comparison.

This file supersedes prospective wording and operational snapshots in the dated 8–9 October handoffs. Historical experiment evidence remains unchanged.

## Code and presentation

- Application code through PRs [#2](https://github.com/azikus/scan-and-pay-poc/pull/2), [#3](https://github.com/azikus/scan-and-pay-poc/pull/3), [#4](https://github.com/azikus/scan-and-pay-poc/pull/4) and [#5](https://github.com/azikus/scan-and-pay-poc/pull/5) is merged. The last application commit is `57fa993cfd01e7533a6140d1c7a5d71f96289293`.
- The native capture/review/confirmation flow, admin inspector and automatic Mac network listeners are implemented. Android remains a README only. Source folders are `backend/`, `frontend/admin/`, `ios/` and `android/`.
- The initial presentation was created with Markus and revised on 9 October. Its approved version has **25 slides**, English slides, Croatian notes and approximately **19–20 minutes** including the live demo. The old “presentation not started” instructions are historical.
- The 12 October repository import places editable HTML, theme, motion, reviewed assets and reproducible build/serve/export tooling under [presentation/](../presentation/README.md). The normal build excludes the real invoice gallery; a separate ignored local edition preserves it. The original external deck is untouched.
- [PRESENTATION_CONTENT.md](PRESENTATION_CONTENT.md) is generated from the HTML source. [PRESENTATION_EVIDENCE.md](PRESENTATION_EVIDENCE.md) records authoring sources and revisions. Both belong in Git alongside the deck. No later application development is part of this import.

## Current private state

Read-only snapshot on 12 October: **2,273 dispatched reservations / €351.95 held**. The current cumulative limits are **2,286 calls / €353.25**, leaving at most **13 calls / €1.30** at this snapshot, within the **€500 project cap**. These conservative holds are not actual provider bills; method-specific stage counts and ceilings determine how many scans fit.

Markus explicitly requested another allowance on 9 October after exhausting the prior 2,266 / €351.25 limits. The extension added **20 API calls / €2.00**, with the plan, prior configuration, original budget rows and verification under `.local/mobile-allowance-extension-00_zmrsg/`. Its scope is explicit mobile Sends. It does not authorize agents to run experiments or automatically extend limits.

The current persisted choice is **OpenAI GPT-4.1 mini**, `openai-mini-image-roles-v3@2-5094b6dc13ef5718`. This is a live selection snapshot, not a new benchmark result. Read the admin or SQLite for subsequent changes; do not reset selection to match a document.

A separately authorized comparison run on 9 October was stopped at Markus's explicit request so the phone could reconnect. Completed responses and remaining-not-run records were preserved in `.local/all-approaches-repeat-2026-10-09/`, including `user-stop-request.json` and `restore.json`. Do not resume that interrupted run without renewed authorization. The presentation's retained comparison tables remain the original dated studies and do not claim that this interrupted repeat finished.

## Device and runtime

The managed launcher is `.venv/bin/scanpay-serve`; the private `serve.py` delegates to it. It follows local interface changes automatically while keeping a single backend owner. The app uses saved editable URLs, not automatic discovery. Do not restart an active extraction job or launch a second owner against the same database.

Physical-phone checks on 9 October verified USB at 11:17:20 UTC, hotspot Wi-Fi at 11:21:41 UTC, and ordinary Wi-Fi at 18:18:55 UTC. The last saved phone URL was `http://192.168.1.134:8000`. These are dated successful checks, not a guarantee of today's connectivity or IP address. Evidence is under `.local/phone-reconnect-2026-10-09/` and `.local/phone-wifi-reconnect-w0txfh0w/`. The later idle restart applied the authorized allowance; loopback and Wi-Fi authenticated reads returned 200.

Root `.env`, SDK credentials, `.local/providers.json`, SQLite, original ledger, scan artifacts, saved edits and device data remain private. Repository/presentation housekeeping must make no inference calls or change these records.

## Verification and next milestones

The last application verification remains the PR #5 checkpoint: **690 offline backend tests**, **96.03% statements / 91.25% branches**, static/contract/package checks and listener/browser checks. The sheet checkpoint had **23 native unit/recovery and 2 UI tests**. Those dated results are not claimed as new application tests during this presentation-only import. Presentation build, asset/export checks and browser verification are recorded with this change.

Initial presentation delivered → agree remaining **iOS improvements and real-invoice testing** → backend/admin work and integration testing → Android and both-platform testing as the last development milestone → comprehensive final presentation and embeddable website HTML. The initial reveal.js deck is separate from that final website deliverable. No later milestone starts automatically.
