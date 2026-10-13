# M3 interpretation handover

> Historical scope/checkpoint: retain the dated evidence below. Current scope, runtime and acceptance are in [CURRENT_STATUS.md](CURRENT_STATUS.md), [CODING_HANDOFF.md](CODING_HANDOFF.md) and [ROADMAP.md](ROADMAP.md). Android/final presentation are skipped; mobile/backend/SUNMI and successful phone Send are accepted. Old next-task wording, worktree paths, provider selections and financial admission limits are not current instructions.

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Latest six-provider direct-image comparison (8 October): all 102 calls are accounted for. OpenAI has 79/102 accepted readable fields and 51/63 critical matches; Gemini has 80/102 and 50/63, with eight additional matching-but-inferred values kept separate. See [direct-provider results](M3_DIRECT_PROVIDER_RESULTS.md) for every provider, failures, timing, cost and limitations. The key/prompts stayed fixed, original evidence is preserved, and no pipeline/default was selected. Ledger now 2,197 dispatched reservations / €336.05 allowance; backend stopped. PR/merge still waits for Markus’s confirmation.

Latest label adjudication: accepted short-name/accent variants now count separately as correct (`reviewed-fields@2`), giving latest direct image 79/102 accepted (76 exact + 3 variants), with no new inference. Key and rescoring evidence: `.local/m3-name-review-2026-10-08/`. Historical exact-only tables remain unchanged. Amount 89.02 reconfirmed; wrong observed amounts are not automatically detected or nulled. See M3_RECIPIENT_ROLES.md.

Recipient-role continuation (8 October): the separately versioned correction and two complete 17-image × 2-method evaluations are recorded in [recipient-role results](M3_RECIPIENT_ROLES.md). Latest direct image matches 76/102 readable fields at median 4.17 s (baseline 68/102 at 4.97 s); hybrid falls to 63/102 and retains role/option errors. Direct image now identifies the co-owners community, with a remaining name-format mismatch; no answer-key changes. Prompt mitigation is implemented, full reliability is not established, and no pipeline/default is selected. 644 offline tests pass. Ledger: 2,095 dispatched reservations / €323.30 allowance, not cash billed; prior evidence preserved. Server stopped. Markus's results-confirmation gate before PR creation/merging remains in force.

Baseline before the recipient-role continuation (8 October): the fresh masked-image comparison is complete: **17 images × 3 methods, 51 results, 68 calls**, without retries. Step 5's import/scoring is complete for the usable review subset: **102 readable fields and 98 confirmed absences** scored; 92 pending, 2 unreadable, 5 disputed and 47 unsupported/free-text fields remain excluded. Direct image matches 68/102 readable fields at median 4.97 s; hybrid matches 70/102 at 6.58 s; OCR/rules matches 25/102 at 3.48 s. These are partial normalized field matches, not whole-invoice accuracy. Both LLM methods have recipient-role errors, so no pipeline is selected. See [fresh results and reviewed scoring](M3_REVIEWED_RESULTS.md) for evidence, limitations and continuation. Original labels/prompts/results/defaults are preserved. Wait for Markus's confirmation before creating or merging project PRs, then prepare the next-chat handoff.

## Agreed next sequence — 8 October 2026

Finish the bounded fresh 17-image comparison first, then import the usable human review and score correctness (step 5). Unresolved, disputed and unreadable labels stay unscored. Present the concrete results for Markus's confirmation. Only after that confirmation, create the project PR and merge pending PRs in `azikus/scan-and-pay-poc` after review/required checks, then prepare the next-chat handoff. Do not create or merge PRs before that confirmation.

Choose the pipeline with Markus for correctness and total latency, regardless of cost. Continue recording expense and respecting the existing €500 experiment cap. The next implementation focus is the iOS app in another chat, after pipeline selection and agreement on capture/review screens: capture/import an image, send JPEG/PNG to the existing Mac backend, poll and display an editable draft with incomplete/error states. A physical phone needs the Mac's reachable LAN URL, not the phone's `localhost`; make the endpoint configurable. Provider credentials stay on the backend. No mobile implementation or future-chat creation in this chat. Android follows later; barcode decoding remains outside this PoC. See [roadmap](ROADMAP.md).

Prior human-validation snapshot: Markus confirmed the Croatian co-owners community as beneficiary (the manager is not an accepted beneficiary alias for that invoice), and accepted unreadability/incompleteness for Protergia’s tiny identifiers. These field-level decisions are in private labels `expected-fields-draft@3-no2d`; other fields remain unverified. The shareable offline colleague form is `.local/evaluation/m3-expected-fields-2026-10-08/colleague-validation.html`, with all 17 masked images, corrections, per-field decisions, JSON export and saved-HTML continuation. It contains private invoice data and is prepared for the user to send; no external sharing occurred. Returned reviews are annotations, not automatically applied labels: validate the dataset/image hashes and review unresolved/corrected fields before importing or scoring.


8 October 2D-code masking update: all 17 retained images were visually inspected. Ten 2D symbols on seven images are covered with solid white pixels in the current evaluation copies; the other ten copies are byte-identical. Every pixel outside the mask rectangles was checked unchanged, and all seven edited images were visually checked. Originals and the pre-mask v3 manifest remain preserved. The active labels are `.local/evaluation/m3-expected-fields-2026-10-08/expected-fields-masked.json`; the existing `review.html` now embeds the masked copies and includes field definitions and the actual current LLM prompts. Linear barcodes and nearby printed identifiers remain visible. New variant IDs and image hashes distinguish these inputs from historical results: saved pre-mask OCR/model output must not be reported as evaluation of the masked images. At the masking step no fresh inference or scoring occurred. The HTML retains the earlier prompt audit snapshot. The separately versioned draft policy is now implemented; see M3_DRAFT_POLICY.md. Fresh inference and partial reviewed scoring are now complete; see M3_REVIEWED_RESULTS.md.


Latest answer-key preparation (8 October): the user excluded Milan page 7, leaving 17 active images in `.local/evaluation/m3-no2d-2026-10-08/manifest.json`. Private manual field drafts and an image review page are in `.local/evaluation/m3-expected-fields-2026-10-08/`. All labels remain unverified and unscored; no fresh inference or results replay was performed for this preparation. Original evidence and previous selections remain unchanged.

Prepared 8 October 2026 for a new local chat, explicitly requested by Markus. Start implementation from this working tree; this is not a fresh project or an instruction to rerun M2.

## Continuation update

The implementation requested by this handover has started. Read [M3 interpretation](M3_INTERPRETATION.md) for rules 3, the multilingual label dictionary, per-stage OCR → OpenAI text composition, 372-recording replay and 485-test verification. New evidence is `.local/m3-interpretation-2026-10-08/final/`; no old evidence/configuration was overwritten and no inference occurred. The detailed sections below retain the original handover baseline; the continuation update supersedes their unimplemented-status statements. Fresh hybrid evaluation is now recorded in M3_REVIEWED_RESULTS.md. The subsequent 8 October user clarification removes payment-barcode/QR decoding from the entire PoC; it is a future improvement, not an M3 completion requirement.

## Start here

1. Read `AGENTS.md`, this file, `CODING_HANDOFF.md`, `IMPLEMENTATION_STATUS.md`, `M2_OPERATIONS.md`, `M2_INTEGRATIONS.md` and `ROADMAP.md`, then complete the handoff's existing read order before implementation.
2. Inspect Git status. Stay in `/Users/markusi/Developer/Azikus/scan-and-pay`, branch `codex/m2-provider-coverage`. The extensive modified/untracked backend, tests and documents are the completed M2/M3 work, not disposable leftovers. Do not reset, checkout an old revision, create a clean worktree that loses this work, or commit/push without instruction. Remote: `git@github.com:azikus/scan-and-pay-poc.git`.
3. Start with a private diagnosis of the saved OCR observations and zero-field outcomes. Implement general interpretation improvements with synthetic tests, then replay every available input for each changed method. Do not spend time repeating account setup or broad provider compatibility testing.

## What Markus wants

OCR recognition is integrated; interpretation is **not solved**. Existing deterministic rules cover limited cases. General spatial/layout interpretation and multi-call OCR → LLM extraction remain M3 work. Many empty drafts reflect this unfinished layer, not a provider's inability to read the image. M2 completion means integration/evaluation coverage, not useful extraction or verified accuracy.

Keep updates and explanations terse. Priorities are useful extracted data and low latency, with concise per-option expense tracking. Preserve partial fields rather than reject an entire response. No automatic provider substitution, majority voting or paid retries. No self-hosted models. All methods in a provider batch must cover the full corpus, not selected easy images.

The removed provider and cancelled support outreach stay removed; maintain the current ten-provider roster. Maintain the JPEG/PNG-only backend and current documentation scope. No mobile implementation, browser customer flow, attendee companion or final/public report now. The earlier private progress HTML is a separate authorized explainer.

## Implemented and verified

- Backend: FastAPI/Pydantic, SQLite, bounded workers, persistent jobs, immutable provider responses/observations, independent compare, versioned profiles, full-corpus batching/replay, review checks, per-stage recipients, timing and expense records.
- Providers: OpenAI, Anthropic, Gemini, Mistral, xAI, Together, Azure, Google Document AI, AWS and Mindee. Fifteen selected methods each have three 31-image attempt matrices. Together remains active; the compact configuration greatly reduced its earlier timeout problem, but recorded failures remain.
- Rules v2 handles some bank-section associations, markdown label/value tables, amount roles and Croatian references. It consumes text structure, not a general geometry interpretation engine.
- Compact protocols 5/6 preserve typed destinations. The seven selected image/annotation profiles now add `field_policy=partial_v1` / `partial-fields@1`: isolate invalid readings, retain unrelated fields and candidate positions, attach findings and keep rejected exact strings as uncertain alternatives. Invalid JSON/duplicate keys/unrecognizable structures still fail. Bank digits are never repaired or guessed.
- Public v1 adds optional `run.outcome`. Old stored results/examples remain valid and unchanged; pending outcomes are omitted. `state` still describes execution, not result usability.

| Outcome | Meaning |
| --- | --- |
| success | Complete and consistent enough for review; still requires confirmation, not verified correctness. |
| incomplete | Some invoice/payment values, raw field readings or alternatives exist, but completion/correction is needed. |
| error | Execution failure, unusable response or no invoice/payment field data. Language/country and unstructured OCR text alone do not count. |

A valid empty response can have `state=completed`, `outcome=error`, an empty payment draft and validation finding `no_usable_data`; its transport `error` remains null. `final_result_id` does not guarantee a useful draft. Preserve this distinction in API, reports and future UI. Detailed review states remain `ready_for_review`, `needs_review`, `insufficient_data`.

Latest validation: **406 offline tests**, **94.93% statement / 88.57% branch coverage** across domain/orchestration/evaluation; lint, formatting, strict typing and generated contract agreement pass. Logs and coverage are in `.local/m3-partial-2026-10-08/`. A pre-existing Starlette TestClient deprecation warning is not a failing test.

## Evidence and interpretation limits

Corpus: **31 images**, comprising 27 prepared page images and four supplied images. All 12 inventory files are accounted for. Preserve source/page/variant and duplicate groupings. The 14 conservative groups are not verified invoice counts. Labels are unverified; do not claim accuracy or count every page as an invoice expected to contain all payment details.

The original three-run comparison contains **1,395 outcomes: 1,378 accepted / 17 failed** under the strict parser. “Accepted” measured structural processing, not a usable payment draft. The failures were 12 malformed model outputs, four timeouts and one HTTP 503. Mistral Small repeated the same unreadable/value IBAN contradiction for image 9 in all three runs; other failed method/image pairs occurred once. Repeated inference is not a correctness test.

The 8 October offline check reparsed the seven compact methods, retaining source mappings for the other eight. All **12 malformed-output failures recovered as incomplete**; all **1,378 prior accepted payment structures stayed unchanged**. New outcome totals: **11 success / 953 incomplete / 431 error**. Errors are **426 zero-field results + 4 timeouts + 1 service error**. These are method/image/run records, not 426 unique documents or a measured OCR accuracy rate. In particular, the four OCR/rules methods account for 309 zero-field records; many contain recognized text that rules did not map. Inspect saved text/layout and the input before attributing a cause or assuming expected fields exist.

Source timing/costs remain attached to replay results; local replay milliseconds are separate. Reusing saved OCR avoids another OCR charge, but sending its text to an LLM is still paid inference and must be labelled as such. Neither replay nor altered result labels improve recognition by themselves.

## Exact continuation assets

| Asset | Location / purpose |
| --- | --- |
| Prepared corpus | `.local/evaluation/m2-corpus-2026-10-06/manifest.json` |
| Current selected catalogue | `.local/m3-partial-2026-10-08/providers-current.json`; seven new compact policy versions, offline replay verified, not newly live-validated |
| Unchanged M1 default | `.local/providers.json`; preserve it, do not silently replace the default/model |
| Frozen strict catalogue and 45 batch identities | `.local/m2-repeatability-2026-10-07/providers.json` and `plan.json`; plan matrix links 15 baseline batches and 30 fresh repeats |
| Latest private replay | `.local/m3-partial-2026-10-08/replay.json`, `summary.md`, `replay.py`; per-row sources, original/current outcomes, hashes, timings and new runs |
| Original ledger and artifacts | `.local/backend/jobs.sqlite3`; `.local/backend/jobs/<scan_id>/` contains raw responses and `*.document.json` observations |
| Preservation baseline | `.local/m3-partial-2026-10-08/before.json`; old profile versions, 45 batch hashes, credential-file hash and ledger totals |
| Strict failure diagnosis | `.local/m2-repeatability-2026-10-07/failure-diagnosis.json` |
| Historical processing/latency report | `reports/repeatability-2026-10-07/index.html`, `data.json`, `summary.md`; interpret using the newer outcome clarification |
| Earlier architecture explainer | `reports/overview-2026-10-07/index.html` |
| Separate expense summary | `reports/cost-comparison/2026-10-07/repeatability.md` |

Keep new replay outputs in a new directory; do not overwrite these baselines. Full original responses remain private, including retired-provider history. Routine logs/reports must not expose real bank details.

## Implementation entry points

- `backend/document_observations.py`: immutable text, spans, native geometry and layout. Coordinates are provider-native; do not silently treat them as normalized image boxes.
- `backend/ocr_rules.py`, `backend/ocr_rules_v2.py`: existing interpretation versions; retain them unchanged when adding a new rules version.
- `backend/adapters/documents.py`, `mapping.py`: document-service observation/mapping boundaries.
- `backend/adapters/compact.py`, `partial.py`: typed model readings and field-level recovery.
- `backend/models.py`, `review.py`, `runtime.py`: linked candidates, outcomes, review and execution. `review_extraction` merges field findings into review reasons.
- `backend/config.py`, `profiles.py`, `store.py`: versioned options, profile identities and dispatch/ledger accounting. Current single-call assumptions need explicit per-stage work before a hybrid can be safely dispatched.
- `evaluation/replay.py`: complete-corpus saved OCR replay currently compares rules 1/2. Extend/version it for new interpretation without replacing prior evidence. `evaluation/batch.py` and `repeatability.py` own fresh attempt accounting/comparisons.
- Relevant synthetic tests: `test_rules_v2.py`, `test_document_observations.py`, `test_document_mapping.py`, `test_partial.py`, `test_replay.py`, plus runtime/API/contract tests.

## M3 work to complete

1. Diagnose missing-field classes privately: recognized text with no mapping, broken layout/associations, genuinely absent fields, ambiguous claims and actual recognition/transport failures. Keep sample/group provenance and explicit gaps.
2. Add general rules/layout interpretation with synthetic regressions and counterexamples: bank-section boundaries, multi-column amount roles, required references, Croatian model/reference instructions, multiple destinations and contradictory evidence. No supplier names, image hashes or sample-specific lookup tables in rules/tests.
3. Implement a separately versioned OCR → LLM method, with per-stage reservations, dispatches, recipients, evidence, timing and partial-failure behavior. Preserve direct-image and raw document baselines. Additional annotation/document augmentation options only where justified by evidence; existing annotations are already integrated.
4. Replay all available corpus observations for affected rules/mappings, preserve old outputs, and report useful/missing fields rather than just schema acceptance. Fresh evaluation of promising new methods needs a new bounded full-corpus plan and readiness checks. Do not rerun all providers merely because a new chat began.

M3 is complete only when its failure-class tests/counterexamples, full available-corpus replay, explicit gaps and separately labelled fresh evaluations of promising methods support the implementation. Do not weaken review requirements to inflate success counts.

## Access, execution and spending

All initial credentials/resources were supplied; OpenAI funding and AWS paid activation were resolved. Google ADC and AWS login were refreshed for the completed batches, but temporary credentials may later expire. Ask only for a concrete expired/missing access condition; do not request replacement keys or account setup pre-emptively. Keep credentials in the root `.env` and SDK-managed stores; no secret values in chat, docs, logs or Git.

The earlier handoff baseline was 1,924 dispatched reservations / €306.20 allowance. The original fresh M3 batch ended at **1,992 dispatched reservations / €313.00 retained allowance**, not cash billed; its plan caps were 1,992 calls / €386.00. The recipient-role continuation now ends at **2,095 dispatched reservations / €323.30 retained allowance**, with plan caps 2,095 calls / €396.30. There is no unused call allowance in either completed plan. See M3_RECIPIENT_ROLES.md. The €500 project cap remains. Do not perform paid calls while preparing the next handoff. Provider testing is authorized under project rules, but a new experiment requires its own bounded plan against the same ledger before dispatch; do not reset/release uncertain charges or treat creation of this chat as a fresh spending allowance.

There are no queued/running jobs. The inference server is stopped. A loopback report preview may remain on port 8766; inspect before relying on it. Do not start old batch runners. No new dependencies, commits, pushes or public publication are part of this handover.

## Remaining phases after M3

- **Phase 2 / M4:** review critical expected fields and groups with Markus; retain held-out groups, measure correctness/missing data, median/p95 latency and expense, choose a versioned pipeline, evaluate fresh photographs. No accuracy claim before reviewed labels.
- **Phase 3 / M5–M7:** agree capture/review/retake/error designs, then iOS, then Android. Native mobile OCR is a later separately measured experiment. Mobile/display implementation needs the later scope/design agreement.
- **Phase 4 / M8:** stable end-to-end demonstration, attendee companion from actual masked processing events, final findings HTML and refreshed separate cost report. Public sharing and actual payment execution are not implied.

See `ROADMAP.md` for acceptance criteria. Low latency must include every hybrid stage; provider time is not mobile capture-to-review time. Every draft still requires user review and confirmation.
