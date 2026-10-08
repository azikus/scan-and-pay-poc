# Delivery roadmap

Phase 2 is closed for the current PoC scope as of 8 October 2026. Markus authorized selecting the best tested pipeline, commit/push and the previously requested checked PR/merge sequence. Direct-image GPT-4.1 mini is selected provisionally for correctness and speed; see [closeout](PHASE2_CLOSEOUT.md). Remaining extraction and label limitations are documented follow-ups, not a production-readiness claim.

The [fourth-chat handoff](CHAT4_HANDOFF.md) awaits additional details from Markus. Do not create that chat or start mobile code yet. M5 design agreement precedes M6 iOS, connecting to the existing Mac backend; Android and M8 findings follow later. Cost remains tracked under the €500 experiment cap and does not determine the pipeline choice.

| Phase | Milestones | Current status |
| --- | --- | --- |
| 1 — Backend foundation and first comparison | M1: service, v1 contract, vision and managed OCR/rules | Complete; measured evidence retained |
| 2 — Provider breadth, extraction quality and evaluation | M2: provider coverage/tooling; M3: better interpretation/hybrids; M4: reviewed comparisons/pipeline selection | M2–M4 closed for current scope; direct-image GPT-4.1 mini selected provisionally |
| 3 — Mobile designs and implementation | M5: agreed designs; M6: iOS; M7: Android | iOS is the next implementation focus in another chat after selection/design; Android follows later |
| 4 — Demonstration and findings | M8: stable demo, attendee companion and final report | Deferred; private progress explainer authorized separately |

Backend managed OCR already shipped in M1. M2 broadens OCR/document providers; M3 improves how their observations become payment candidates. Native platform OCR belongs to mobile work. These are separate capabilities, not conflicting milestone assignments.

## M1 — Backend foundation: complete

Python/FastAPI/Pydantic, private JPEG/PNG processing, SQLite jobs/stages, bounded workers, v1 endpoints, CLI and independent comparison. GPT-6 Luna vision and Mistral OCR 4.1/local rules both have UK/HR runs. Shared review normalization includes IBAN validation and resolves false format-only bank conflicts. Latest cleanup verification on 6 October: 184 offline tests, 98.76% statement/95.11% branch coverage; the concurrency regression passes and production packaging excludes synthetic test support. OCR-rule gaps, legitimate review reasons, prior failures and unverified labels remain visible in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

## M2 — Provider coverage and full-corpus evaluation tooling: complete

Current full-corpus results are recorded in [implementation status](IMPLEMENTATION_STATUS.md). All ten retained provider families have tested adapters, and all fifteen selected methods have complete 31-input attempt records.

Scope:

- Maintain the private source/page/variant manifest for every prepared JPEG/PNG input. Add API-based batch execution and explicit complete/failed/not-run coverage accounting.
- Make models/methods independently selectable, enabled, versioned and costed. Preserve old results/profile snapshots and the current default extract profile.
- Add tested adapters across OpenAI, Mistral hosted vision/OCR/annotations, Anthropic, Gemini, xAI, Together-hosted open-weight models, Azure Document Intelligence, Google Document AI, AWS Textract and Mindee. Existing adapters are extended/reused, not rewritten for each model. No exhaustive Cartesian product of models or mandatory small/large pairs.
- Separate vendor transport/mapping, immutable document observations, extraction methods and shared review. Add per-stage accounting/provenance before multi-call compositions.
- Begin the [separate cost report](COST_REPORT_PLAN.md), with one row per exact option, complete coverage accounting, tariff provenance, observed stage/retry usage and explicit unknowns.
- Perform account-specific capability/terms/region/pricing checks, then bounded compatibility runs over every sample for each selected profile. Preserve the exhausted starter cap and twelve existing holds; record the next cap/plan before dispatch.

Acceptance: meaningful offline tests pass; every corpus input is accounted for; representative compatible profiles cover each requested provider family with full-corpus attempt records. Individual document failures are visible outcomes. Account/product blocks and early stops leave that profile's coverage incomplete, so overall M2 remains partial until resolved or explicitly removed from scope by the user. No accuracy ranking is required or allowed from unverified labels. Unsupported fields must remain missing.

## M3 — Better extraction and separately measured hybrids: current scope complete

Versioned rules/dictionary, field recovery, recipient-role prompting and separately measured OCR → LLM are implemented and evaluated. See [closeout](PHASE2_CLOSEOUT.md), [interpretation](M3_INTERPRETATION.md) and [provider results](M3_DIRECT_PROVIDER_RESULTS.md). The selected direct-image profile outperformed the measured hybrids on reviewed critical fields and total latency. Remaining role/reference/amount errors and generalization checks are retained follow-ups.

Can overlap M2; broad integration must not wait for perfect rules. Add synthetic regressions first for bank-section association, multi-column amount roles, Croatian model/reference instructions, multiple payment options and conflicting evidence. Improve general rules without supplier/sample lookup tables. Keep shared `schwifty` validation; UK modulus validation is an optional, separately justified library/table check with licence/version handling, not account ownership verification.

Add selected OCR → LLM, schema-annotation and document-augmentation profiles; preserve raw document mappings and direct-image baselines. Measure methods independently, retaining source spans, actual recipients, stage costs and failure behavior.

Acceptance: failure-class regressions and counterexamples pass; private saved-response replay covers all available corpus recordings with explicit gaps; promising methods have separately labelled full-corpus fresh evaluations. Old results remain immutable. No test expectations are weakened to force completion/readiness, and no hybrid is assumed better in advance.

## M4 — Reviewed comparison and provisional pipeline selection: complete for current scope

Completed: imported the usable human review with source/image hashes and explicit field-level exclusions; selected `openai-mini-image-roles-v3@2-5094b6dc13ef5718`. The rationale and portable/private configurations are in PHASE2_CLOSEOUT.md. Ongoing evaluation principles: Keep unresolved, disputed and unreadable fields unscored; preserve held-out groups. Compare field/record correctness, critical errors, missing/ambiguous outcomes, median/p95 total latency and coverage. Record cost separately, but choose for correctness and speed regardless of price. A focused three-method experiment supports comparison of those methods only, not a claim that its winner beats every available provider. Select with Markus and freeze a versioned profile; test any bounded fallback separately.

Acceptance: reproducible measurements, a Markdown experiment record and the separate per-option cost report support the selection and its limitations. The cost report includes comparable per-attempt/document/corpus costs and explicit unknowns; cost per correct result requires reviewed labels. Checked labels underpin every accuracy claim; camera claims require actual camera inputs. Freeze a versioned profile/configuration suitable for mobile integration, with genuine review/retake paths. Final HTML remains in M8.

## M5 — Agree the mobile experience

Later scope: capture/import, actual processing, editable review, missing-field/retake, provider failure and explicit demo confirmation. Use the same payment contract, preserve leading zeroes and distinguish review from executing a payment. Minor approved name variations are nonblocking. An unresolved amount stays empty with a needs-input warning, while other extracted fields remain visible; do not blank all amounts merely because a draft is incomplete. Apply Azikus styling to designed artifacts, never invoice originals.

Acceptance: Markus agrees the screens/states and API mapping before mobile code. Phase 3 may begin after that explicit scope/design agreement and a stable backend; it need not wait for every optional model comparison in Phase 2.

## M6 — iOS mobile app

In another chat, implement capture/import → JPEG/PNG upload → processing → editable review using the existing backend: `POST /v1/scans`, then poll `GET /v1/scans/{scan_id}`. Connect to a configurable backend URL on Markus's Mac. A physical iPhone's `localhost` is the phone itself, so use the Mac's reachable LAN address with deliberate development network configuration; simulator loopback can reach the host setup. Keep provider credentials on the backend and the client API token in secure device storage. Do not expose the backend publicly as part of this work.

Test on Markus's device: orientation/compression, upload, polling, edits, incomplete/error states, cancellation/interruption and network recovery. Measure actual capture-to-review latency. Native OCR/quality signals are optional later experiments, not a dependency of this first image-upload flow. Every payment draft requires explicit review/confirmation; the app does not execute payments.

Acceptance: a real photograph produces a reviewable draft on-device; missing/ambiguous data and errors are usable; device observations carry provenance and are independently evaluated. Native OCR does not silently replace backend evidence.

## M7 — Android mobile app

Implement the agreed contract/journey on Android after iOS. Evaluate suitable native OCR/ML Kit capabilities and script support rather than assuming parity. Exercise the shared fixtures plus actual capture, interruption/retry and network conditions.

Acceptance: both apps implement the same field/review semantics with measured platform differences and no provider credentials on the phones.

## M8 — Stable demonstration and findings

Freeze the demonstration configuration; test fresh photographs, laptop/device networking, failure recovery and any clearly labelled replay. Build the separate attendee companion from actual processing events with masked details. Produce the Azikus HTML findings report and substantiated external summary from the measured evidence. Refresh and link the separate cost report using the final configuration; keep it a standalone deliverable.

Acceptance: dependable end-to-end demonstration, reproducible evidence, visible limitations and recovery instructions. Public materials use separately approved sanitised data. No publication, live payment execution or production-validation claim is implied.

## Sequence and authority

Fresh evaluation, reviewed-subset scoring and provisional selection are complete. Commit/push and checked PR merge close this checkpoint. Finalize the fourth-chat brief when Markus supplies it, agree mobile screens, then implement iOS in that chat. Pending labels limit correctness claims but do not block mobile design. No additional inference or new chat is authorized by handoff preparation.

Detailed execution: [coding handoff](CODING_HANDOFF.md), [Phase 2 rollout](PHASE2_ROLLOUT.md), [evaluation plan](EVALUATION_PLAN.md) and [backend plan](BACKEND_PLAN.md). Latest user instructions override this proposed breakdown. The €500 total, included ≤€30 first tranche, mandatory review, full-corpus batches and hosting/privacy boundaries apply throughout.

## Future improvement outside the PoC

On 8 October the user explicitly deferred payment-barcode/QR decoding and payload interpretation beyond this PoC. It is not required for M3, mobile work or final PoC acceptance. Mention it later as a potential improvement in the final findings. Continue extracting printed payment references and identifiers through OCR/document/vision methods; barcode presence in an image does not expand scope. Existing contract fields and historical evidence remain unchanged.
