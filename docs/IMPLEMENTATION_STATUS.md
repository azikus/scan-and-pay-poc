# Implementation status

## Current checkpoint — 9 October 2026

The only new implementation is the extracted-field review/confirmation sheet change, with supporting draft persistence and regression tests. **23 native unit/recovery and 2 simulator UI tests pass**, with existing confirmation API checks and inspected synthetic screenshots. Original extraction and frozen pending confirmation bodies remain intact. See [sheet checkpoint](CONFIRMATION_SHEETS.md) for precise behavior and verification.

The accepted iOS/admin implementation merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2), followed by root `backend/`, `frontend/`, `ios/`, `android/` reorganization in [PR #3](https://github.com/azikus/scan-and-pay-poc/pull/3). Android is a README only. Baseline checks were 672 backend/evaluation tests, 95.92% statement / 91.15% branch coverage, lint/format/types/contracts/JS and installed-wheel/source-distribution validation. A later merged-main rebuild/install passed while preserving phone data; phone launch was blocked by lock. Distinguish this from the user's earlier real-invoice acceptance and USB-failed/Wi-Fi-connected result.

Ledger remains **2,202 dispatches / €336.55 held**, within 2,217 / €338.05 mobile caps; persisted admin selection is Gemini Flash-Lite. No paid calls, experiment reruns or other features are part of this sheet/documentation checkpoint.

Next is the **initial presentation together with Markus in a new chat**. [Presentation handoff](PRESENTATION_HANDOFF.md) is the comprehensive source pack, with a [copyable prompt](PRESENTATION_PROMPT.md). [Roadmap](ROADMAP.md) records the agreed order: presentation → iOS improvements/testing → backend/admin/integration → Android and both-platform testing, the final development milestone → comprehensive final presentation and embeddable website HTML. Later work is not started.

## Historical checkpoints

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.


**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Latest closeout verification: **651 tests passed, 95.57% statement / 90.85% branch coverage**; lint, formatting and strict typing pass. The selected OpenAI configuration matches its paid snapshot exactly. No inference occurred during closeout.

## Historical implementation and evaluation checkpoints

Latest six-provider direct-image comparison (8 October): all 102 calls are accounted for. OpenAI has 79/102 accepted readable fields and 51/63 critical matches; Gemini has 80/102 and 50/63, with eight additional matching-but-inferred values kept separate. See [direct-provider results](M3_DIRECT_PROVIDER_RESULTS.md) for every provider, failures, timing, cost and limitations. The key/prompts stayed fixed, original evidence is preserved, and no pipeline/default was selected. Ledger now 2,197 dispatched reservations / €336.05 allowance; backend stopped. PR/merge still waits for Markus’s confirmation.

Latest label adjudication: accepted short-name/accent variants now count separately as correct (`reviewed-fields@2`), giving latest direct image 79/102 accepted (76 exact + 3 variants), with no new inference. Key and rescoring evidence: `.local/m3-name-review-2026-10-08/`. Historical exact-only tables remain unchanged. Amount 89.02 reconfirmed; wrong observed amounts are not automatically detected or nulled. See M3_RECIPIENT_ROLES.md.

Recipient-role continuation (8 October): the separately versioned correction and two complete 17-image × 2-method evaluations are recorded in [recipient-role results](M3_RECIPIENT_ROLES.md). Latest direct image matches 76/102 readable fields at median 4.17 s (baseline 68/102 at 4.97 s); hybrid falls to 63/102 and retains role/option errors. Direct image now identifies the co-owners community, with a remaining name-format mismatch; no answer-key changes. Prompt mitigation is implemented, full reliability is not established, and no pipeline/default is selected. 644 offline tests pass. Ledger: 2,095 dispatched reservations / €323.30 allowance, not cash billed; prior evidence preserved. Server stopped. Markus's results-confirmation gate before PR creation/merging remains in force.

Baseline before the recipient-role continuation (8 October): the fresh masked-image comparison is complete: **17 images × 3 methods, 51 results, 68 calls**, without retries. Step 5's import/scoring is complete for the usable review subset: **102 readable fields and 98 confirmed absences** scored; 92 pending, 2 unreadable, 5 disputed and 47 unsupported/free-text fields remain excluded. Direct image matches 68/102 readable fields at median 4.97 s; hybrid matches 70/102 at 6.58 s; OCR/rules matches 25/102 at 3.48 s. These are partial normalized field matches, not whole-invoice accuracy. Both LLM methods have recipient-role errors, so no pipeline is selected. See [fresh results and reviewed scoring](M3_REVIEWED_RESULTS.md) for evidence, limitations and continuation. Original labels/prompts/results/defaults are preserved. Wait for Markus's confirmation before creating or merging project PRs, then prepare the next-chat handoff.

8 October 2D-code masking update: all 17 retained images were visually inspected. Ten 2D symbols on seven images are covered with solid white pixels in the current evaluation copies; the other ten copies are byte-identical. Every pixel outside the mask rectangles was checked unchanged, and all seven edited images were visually checked. Originals and the pre-mask v3 manifest remain preserved. The active labels are `.local/evaluation/m3-expected-fields-2026-10-08/expected-fields-masked.json`; the existing `review.html` now embeds the masked copies and includes field definitions and the actual current LLM prompts. Linear barcodes and nearby printed identifiers remain visible. New variant IDs and image hashes distinguish these inputs from historical results: saved pre-mask OCR/model output must not be reported as evaluation of the masked images. At the masking step no fresh inference or scoring occurred. The HTML retains the earlier prompt audit snapshot. The separately versioned draft policy is now implemented; see M3_DRAFT_POLICY.md. Fresh inference and partial reviewed scoring are now complete; see M3_REVIEWED_RESULTS.md.


Latest answer-key preparation (8 October): the user excluded Milan page 7, leaving 17 active images in `.local/evaluation/m3-no2d-2026-10-08/manifest.json`. Private manual field drafts and an image review page are in `.local/evaluation/m3-expected-fields-2026-10-08/`. All labels remain unverified and unscored; no fresh inference or results replay was performed for this preparation. Original evidence and previous selections remain unchanged.

Updated 8 October 2026. **M1 and M2 are complete for the retained ten-provider scope.** All 15 selected methods now have three full 31-image runs. M2 establishes integration and evaluation tooling; it does not establish verified accuracy or production readiness.

The earlier offline M3 implementation added rules 3, a versioned English/Croatian/selected-Italian label dictionary and a separately versioned OCR → OpenAI text composition. See [M3 interpretation](M3_INTERPRETATION.md). Replay of all 372 retained OCR recordings changes 132 zero-field records to incomplete drafts (195 incomplete / 177 empty); this is not accuracy. That offline step passed 485 tests at 95.21% statement / 89.59% branch coverage, without paid calls; current verification and fresh evidence supersede its status. Fresh hybrid evaluation is now recorded in M3_REVIEWED_RESULTS.md. Payment-barcode/QR decoding is outside this PoC, per the 8 October scope clarification, and is not a milestone completion requirement.

The backend accepts one JPEG/PNG image and returns a payment draft for review. Compare mode runs selected methods independently. The default extraction profile is unchanged. OCR → OpenAI text composition has fresh 17-image evidence; interpretation failures remain before pipeline selection.

## Current result states

New runs expose **success / incomplete / error** separately from execution status. Success is complete enough for review, not verified correct. Incomplete preserves extracted fields and uncertain alternatives. Error includes transport/response failure and zero invoice/payment fields; OCR text alone is not a populated draft.

The seven selected compact image/annotation profiles now use versioned `partial-fields@1`: one invalid field produces a warning and retains unrelated fields. Contradictory bank readings remain uncertain, never accepted digits. Other OCR/document mappings are unchanged. Original strict profiles and the M1 default remain available under their original versions; the inference server is stopped.

Offline replay covered **all 1,395 recorded outcomes**: **11 success / 953 incomplete / 431 error**. All **12** malformed-output failures recovered as incomplete drafts. All **1,378** previously accepted payment structures are unchanged. Errors comprise **426 empty field results**, four timeouts and one HTTP 503. Many empty OCR/rules results contain recognized text that the current rules did not turn into fields; this is an interpretation limitation, not proof the provider read nothing. These counts are not accuracy scores.

Private replay/configuration: `.local/m3-partial-2026-10-08/summary.md`, `replay.json`, `providers-current.json`. No new provider calls occurred. Source timings/charges remain provenance; local replay duration is recorded separately. Original results, 45 batches, profile identities, credentials and ledger are preserved.

## Historical three-run processing results

The approved repeatability check completed all **930 fresh attempts: 920 accepted and 10 failed**. With the preserved baseline, that is **1,378 accepted / 17 failed out of 1,395 attempts**, with no skipped inputs or automatic retries. Configurations, image hashes and recipients match the baselines.

**Accepted** means the output fits the common structure and consistency checks; fields may still be wrong or missing. The historical strict policy rejected invalid model output, and a timeout means no usable response arrived within 90 seconds. Labels remain unverified, so these are processing results, not accuracy scores.

| Method | Run 1 /31 | Run 2 /31 | Run 3 /31 | Failures /93 | Total median | Total p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OpenAI · GPT-4.1 mini | 31 | 30 | 31 | 1 | 4.2s | 9.0s |
| Anthropic · Haiku 4.5 | 30 | 30 | 31 | 2 | 5.7s | 10.1s |
| Gemini 3.5 Flash-Lite | 31 | 31 | 31 | 0 | 3.1s | 5.0s |
| Mistral Small 2603 | 27 | 30 | 30 | 6 | 3.4s | 6.2s |
| xAI · Grok 4.7 | 31 | 31 | 30 | 1 | 25.5s | 50.4s |
| Together · Qwen 3.5 9B | 30 | 30 | 28 | 5 | 8.8s | 23.9s |
| Mistral OCR 4.1 | 31 | 31 | 31 | 0 | 3.0s | 6.5s |
| Google OCR | 31 | 31 | 31 | 0 | 2.1s | 2.7s |
| Azure Read | 31 | 31 | 31 | 0 | 6.0s | 11.2s |
| AWS Text | 31 | 31 | 31 | 0 | 2.5s | 4.4s |
| Azure Invoice | 31 | 31 | 31 | 0 | 11.1s | 16.7s |
| Google Invoice | 31 | 31 | 31 | 0 | 4.1s | 5.3s |
| AWS Expense | 31 | 31 | 31 | 0 | 2.9s | 4.0s |
| Mindee Invoice | 31 | 31 | 31 | 0 | 5.3s | 6.6s |
| Mistral annotations | 30 | 31 | 30 | 2 | 11.3s | 29.7s |

Timing includes queue, preparation, provider/polling and local validation, including failed attempts. Mobile upload/rendering is excluded. p95 describes this small sample, not a service guarantee. Per-round timing, maximum latency, failure causes and normalized payment consistency are in the concise private report: `reports/repeatability-2026-10-07/index.html`. The earlier backend explainer remains at `reports/overview-2026-10-07/index.html`.

Output consistency compares linked payment fields, uncertainty, candidate selection and review state; generated IDs, prose and invoice headers are excluded. Only images accepted in all three runs enter its denominator. Consistently missing fields also count as stable. Agreement is not correctness.

## Compatibility fixes before repeatability

- **Vision/annotations:** a compact provider-facing schema asks for printed readings and typed destinations. The backend generates evidence IDs and review states. This removes unnecessary model-generated bookkeeping and coordinates without weakening the public contract. Excerpts remain unverified model claims.
- **Together:** explicit thinking-off configuration and the smaller schema reduced the earlier timeout problem (27 timeouts in the old batch). Its first compact run accepted 30/31, with median 8.9 seconds versus 90 seconds previously; the three-run limitations are recorded above. This is a measured configuration improvement, not proof that one setting caused the entire gain.
- **Gemini:** native output constraints replace unreliable prompt-only formatting. The latest revision expresses fixed destination tags as supported single-value enums. Original requests/results remain unchanged.
- **Google Invoice:** currency mapping 2 preserves the raw token while mapping explicit € / £ to EUR / GBP. The refreshed login and new full batch produced 31/31 accepted outputs.

Across all three runs, failures comprise 12 malformed outputs, four timeouts and one HTTP 503. Mistral Small repeated the same unreadable/value IBAN contradiction on image 9 in all three runs. Other failed method–image pairs failed once each.

The three-run failures are diagnosed in `.local/m2-repeatability-2026-10-07/failure-diagnosis.json`: contradictory unreadable/value claims, blank field readings, timeouts and service errors. Repeated inference can succeed on a previously failed image and fail on another; no successful rerun erases earlier evidence. No automatic retries or hidden fallback were added.

## Samples and replay

The corpus contains 31 prepared images: 27 page images and four supplied images. Source/page/variant and duplicate relationships remain in the private manifest; 14 groups are organizational groupings, not verified invoice counts.

Replay means running saved OCR output through local rules again, without another provider call. Rules 1/2 were compared on 31 recordings each from Mistral, Google, AWS and Azure: 124 recordings total. Payment structures changed for 6, 1, 1 and 0 inputs respectively. Changed does not mean improved; checked expected answers are needed. Original results remain unchanged.

## Current next steps

Finalize CHAT4_HANDOFF.md after Markus supplies its additional brief, then proceed to M5 design agreement and M6 iOS in the next chat. PHASE2_CLOSEOUT.md records selection and follow-ups. Additional label adjudication can rescore saved responses offline; no new provider tournament is required to begin mobile design.

## Historical verification and operation

605 offline synthetic tests pass. Domain/orchestration coverage including evaluation is 95.44% statements / 90.66% branches. Current checks are in `.local/m3-scored-2026-10-08/tests-final.log`. Lint, formatting and strict type checks pass. Public v1 schema exports add the optional outcome field; original examples, profile versions, credentials, corpus hashes and saved batch keys remain unchanged. No real invoice contents are in maintained code or tests.

Fresh per-option expenses: `.local/m3-scored-2026-10-08/costs.md`; historical table: `reports/cost-comparison/2026-10-07/repeatability.md`. An internal reservation is an allowance counted against the spending limit, not a provider charge or card hold. All uncertain dispatched charges remain recorded.

Fresh tested configuration: `.local/m3-draft-policy-2026-10-08/fresh/providers-planned.json` (three focused profiles; not the default). Broader offline replay catalogue: `.local/m3-partial-2026-10-08/providers-current.json`. Historical strict configuration: `.local/m2-compat-2026-10-07/providers-current.json`. Historical evidence: the compatibility directory plus earlier `.local/m2-2026-10-06/` and `.local/m2-followup-2026-10-07/`. Repeatability evidence and the frozen evaluation configuration are under `.local/m2-repeatability-2026-10-07/`. All 30 new batch identities and the 15 baseline batches are preserved. The inference server is stopped; a new paid experiment needs a new bounded plan against the existing ledger. Work remains on `codex/m2-provider-coverage`; no commit or push was made. See [operations](M2_OPERATIONS.md) and [integration evidence](M2_INTEGRATIONS.md).
