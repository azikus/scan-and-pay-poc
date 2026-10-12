# Handoff verification

**Current continuation — 12 October 2026:** the initial presentation is delivered and its source is in [presentation/](../presentation/README.md). [CURRENT_STATUS.md](CURRENT_STATUS.md) owns the latest operational snapshot and authorized allowance. The dated checkpoints below retain their original values and verification evidence; they do not override the current handoff.

## Current checkpoint — 9 October 2026

Native iOS and the authenticated admin inspector are implemented, and Markus confirmed his real-invoice testing is complete. Current acceptance, scope and limitations are recorded in [mobile checkpoint](MOBILE_CHECKPOINT.md). Reorganization checks: **672 offline backend/evaluation tests; 95.92% statement / 91.15% branch coverage; 16 native unit/recovery and 2 simulator UI tests**, with lint/format/types/contracts/JS, installed-wheel serving and source-distribution rebuild checks passing. Signed device build and installation belong to the prior mobile checkpoint; this folder move leaves the installed phone app untouched.

The current ledger is **2,201 dispatches / €336.45 held** under the unchanged 2,217 / €338.05 mobile caps. Persisted admin selection is Mistral Small. The latest hardware reconnect tried USB first, then connected over Wi-Fi; hotspot discovery remains unverified. No paid calls are part of this checkpoint or refactor.

The mobile/admin checkpoint merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2). The source layout is now `backend/`, `frontend/`, `ios/` and `android/` (README only); shared contracts/docs/evaluation and private storage remain in place. See the [reorganization record](REPOSITORY_REORGANIZATION_HANDOFF.md) for current checks and its PR. Next: **presentation together with Markus → mobile improvements → backend work → Android last**. See [coding handoff](CODING_HANDOFF.md).

## Historical checkpoints

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Latest six-provider direct-image comparison (8 October): all 102 calls are accounted for. OpenAI has 79/102 accepted readable fields and 51/63 critical matches; Gemini has 80/102 and 50/63, with eight additional matching-but-inferred values kept separate. See [direct-provider results](M3_DIRECT_PROVIDER_RESULTS.md) for every provider, failures, timing, cost and limitations. The key/prompts stayed fixed, original evidence is preserved, and no pipeline/default was selected. Ledger now 2,197 dispatched reservations / €336.05 allowance; backend stopped. PR/merge still waits for Markus’s confirmation.

Recipient-role continuation (8 October): the separately versioned correction and two complete 17-image × 2-method evaluations are recorded in [recipient-role results](M3_RECIPIENT_ROLES.md). Latest direct image matches 76/102 readable fields at median 4.17 s (baseline 68/102 at 4.97 s); hybrid falls to 63/102 and retains role/option errors. Direct image now identifies the co-owners community, with a remaining name-format mismatch; no answer-key changes. Prompt mitigation is implemented, full reliability is not established, and no pipeline/default is selected. 644 offline tests pass. Ledger: 2,095 dispatched reservations / €323.30 allowance, not cash billed; prior evidence preserved. Server stopped. Markus's results-confirmation gate before PR creation/merging remains in force.

Earlier verification snapshot:

## Current checkpoint verification — 8 October 2026

Fresh M3 evaluation and partial reviewed scoring are complete; see [results](M3_REVIEWED_RESULTS.md). 605 offline tests pass, 95.44% statement / 90.66% branch coverage; lint/format/type checks and all three unchanged contract exports pass. All 1,924 prior ledger rows and 2,094 baseline files are unchanged. New ledger: 1,992 dispatched reservations / €313.00 retained allowance; this is not cash billed. No default/credential change or public publication occurred. Server stopped. Results await Markus's confirmation before PR creation/merging and preparation of the next-chat handoff. The sections below retain earlier verification snapshots.

Current implementation verification and live acceptance are in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), [M2_OPERATIONS.md](M2_OPERATIONS.md) and [M2_INTEGRATIONS.md](M2_INTEGRATIONS.md).

## M3 implementation continuation — 8 October 2026

Rules 3, the versioned multilingual label dictionary and OCR → OpenAI text composition are implemented and offline-tested. See [M3 interpretation](M3_INTERPRETATION.md) for 485 tests, 95.21% statements / 89.59% branches, the complete 372-recording replay and explicit remaining work. New private evidence is `.local/m3-interpretation-2026-10-08/`; prior handover/replay evidence remains unchanged. No provider calls, dependency changes, commits or pushes occurred.

## M3 chat handover — 8 October 2026

The user requested a new chat to reduce context size and continue M3 interpretation. [M3_HANDOFF.md](M3_HANDOFF.md) records the current code, exact private assets, result-state semantics, remaining M3 work and later M4–M8 scope. Existing branch and all uncommitted/untracked work stay in the same checkout. No commit/push or provider calls are part of this handover.

Latest implementation checks remain 406 passing offline tests; 94.93% statement / 88.57% branch coverage, lint/format/type checks and contract exports pass. This documentation-only handover does not rerun inference or claim new live validation. Latest offline replay preserved 2,041 source result/raw files and all 45 batch files, credentials, original profile versions and the ledger. At handoff there are zero active jobs and 1,924 dispatched reservations / €306.20 retained allowance; this is not actual cash spend. The inference server remains stopped.

Private handover verification: `.local/m3-handoff-2026-10-08/verification.json` records maintained-file hashes and checks of source preservation and links. Historical verification below remains historical; it must not restart completed work or override current instructions.

## Main checkpoint preparation — 6 October 2026

Milestone 1 is complete and the full upfront credential/resource set is supplied. The user then authorized codebase cleanup, documentation, a separate cost report, push to private `main` and creation of a new local implementation chat. ROADMAP.md defines M1–M8; CODING_HANDOFF.md starts M2 with useful M3 work alongside it.

- Reviewed active Markdown documentation and production code, preserving wire semantics and private evidence. Added COST_REPORT_PLAN.md and reconciled affected status, scope, read-order and acceptance references. The final HTML report and mobile/display implementation remain deferred.
- Backed up publishable code/docs privately under `.local/archive/pre-main-*/` before cleanup. The original unused architecture PNG remains there; active docs use the existing Mermaid diagram. Earlier handoff documentation is preserved under `.local/archive/handoff-before-20261006T105048Z/`.
- Moved synthetic adapters into tests and excluded test support from the runtime wheel. Fixed shared readiness-probe filenames with a regression verified to fail against the original implementation and pass after the fix.
- 184 offline tests pass; domain/orchestration coverage is 1,271/1,287 statements (98.76%) and 331/348 branches (95.11%). Lint, formatting, strict typing, schema export and wheel-content checks pass. V1 JSON exports are unchanged. Production coverage exclusions are unchanged; the test-only adapter no longer contributes to its denominator.
- Checked relative documentation links, handoff evidence paths, private ignore rules, environment preservation and configured-secret absence from the intended Git contents. Private machine-readable evidence and publication checks are under `.local/main-checkpoint-2026-10-06/`.
- Target remote `git@github.com:azikus/scan-and-pay-poc.git` was rechecked private and empty on 6 October; local branch renamed to `main` for the explicitly requested checkpoint. Use Git log/status and remote refs for the exact committed/pushed revision; no force push or PR is part of this request.
- Continuation prompt preserves full-corpus evaluation, offline-first adapters, separate extraction methods, standalone cost reporting, mandatory review, unverified labels, SDK-managed authentication and the existing budget ledger. It requests neither a replacement environment nor repeated account creation.
- No paid calls, new dependencies or account/credential changes during cleanup/handoff. Existing source samples, labels, raw/results and historical reference code remain private and unchanged. One pre-existing Starlette/TestClient deprecation warning remains visible in the suite.

Not claimed: every new provider works, current tariffs for every option are verified, labels are correct, full-corpus inference is complete, the separate cost comparison is already populated, or a pipeline winner is established. The new chat starts only after the parent's checkpoint publication is verified.

## Historical preparation — 1 October 2026

Documentation/evaluation preparation only; no backend implementation or extraction benchmark at that time.

Checked during preparation:

- Both complete synthetic responses validate against JSON Schema 2020-12 using an existing AJV validator; four negative checks reject unknown root fields and disabled confirmation.
- Evidence IDs, image IDs, stage IDs and selected-candidate references are internally consistent. Fixture timings remain null and execution is explicitly synthetic.
- Relative Markdown/image links resolve in the prepared pack.
- Both starter image hashes match their private manifest entries; UK rendering and existing Croatian image were visually inspected.
- Draft labels are explicitly unverified and scoring_allowed=false. Source-text cross-checking is label preparation, not OCR/extraction performance.
- Checked private payment strings are absent from tracked Markdown/JSON. Synthetic examples contain no copied sample payment details.
- Git ignore checks cover samples, labels, results, reference files, reports, environment secrets, virtual environments and SQLite files. Current contract/examples are not ignored.
- Architecture image visually inspected for readability and clipping, using Azikus colours and the supplied Hanken Grotesk fallback.
- Previous planning files were checked for concurrent changes before replacement and backed up under .local/archive/handoff-before-2026-10-01. Original sample files and historical benchmark code/config/tests are preserved.

Not claimed: exhaustive secret scanning, new-backend test coverage, real provider compatibility, invoice extraction accuracy, production safety, camera performance or public-demo permission. No model calls, new dependencies, Git initialization, commits or pushes were performed. The earlier 15 offline tests belong to the historical CLI, not this service.

The old HTML/preview are recoverable under .local/archive/exploration-html-2026-10-01. They are not active specifications or measured findings. Final HTML reporting remains deferred.
