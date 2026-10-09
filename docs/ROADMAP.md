# Delivery roadmap

**Current direction — 9 October 2026:** Phase 2 remains closed for the current PoC scope. M5 is agreed; M6's iOS implementation is complete for this checkpoint and Markus confirmed his real-invoice device testing is done. No universal accuracy or camera-to-review timing claim follows from that acceptance. The inspector supports selectable extraction methods, saved provider outputs/mobile images and separate confirmed edits. See [mobile checkpoint](MOBILE_CHECKPOINT.md).

| Phase | Milestones | Current status |
| --- | --- | --- |
| 1 — Backend foundation | M1: service and v1 contract | Complete |
| 2 — Extraction and evaluation | M2–M4: providers, interpretation, reviewed comparisons | Closed for current scope; original evidence retained |
| 3 — Mobile | M5: design; M6: iOS; M7: Android | M5/M6 accepted for this PoC checkpoint; improvements follow presentation; Android last |
| 4 — Demonstration and findings | M8: presentation, dependable demo, companion and report | Presentation is the next joint task after repository cleanup; final deliverables remain open |

Milestone numbers retain their historical definitions; they do not override Markus's newly agreed execution order. Current work is two checked PRs: mobile/admin checkpoint, then a separate repository-reorganization chat with status/documentation updates. Next: presentation together → mobile-client improvements → backend improvements → Android. Keep experimental method switching for the client demonstration; do not silently freeze or replace the current selection.

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

Agreed scope: modern camera UI → manual capture/import → crop/adjust → explicit Send → processing → editable review → simulated payment/reset. Use field shimmer and the selected image-led expandable bottom sheet. Pay dismisses the sheet, clears the mobile draft and re-enables capture, with no payment execution. Cover missing-field/retake and provider failure states. See MOBILE_UX_BRIEF.md. Use the same payment contract, preserve leading zeroes and distinguish review from executing a payment. Minor approved name variations are nonblocking. An unresolved amount stays empty with a needs-input warning, while other extracted fields remain visible; do not blank all amounts merely because a draft is incomplete. Apply Azikus styling to designed artifacts, never invoice originals.

Acceptance: Markus agrees the screens/states and API mapping before mobile code. Phase 3 may begin after that explicit scope/design agreement and a stable backend; it need not wait for every optional model comparison in Phase 2.

## M6 — iOS mobile app

Implemented and accepted for this PoC checkpoint (Markus confirmed real-invoice testing on 9 October): capture/import → JPEG/PNG upload → processing → editable review using the existing backend: `POST /v1/scans`, then poll `GET /v1/scans/{scan_id}`. Connect to a configurable backend URL on Markus's Mac. A physical iPhone's `localhost` is the phone itself, so use the Mac's reachable LAN address with deliberate development network configuration; simulator loopback can reach the host setup. Keep provider credentials on the backend and the client API token in secure device storage. Do not expose the backend publicly as part of this work.

The first slice has a capture button and manual crop; no paper detection dependency. TODO for 9 October 2026 morning, once invoices are available: test paper-edge detection and a stable live outline, retaining manual fallback. This is a deferred task, not a scheduled automation.

Test on Markus's device: orientation/cropping/compression, upload, polling, edits, incomplete/error states, duplicate taps, late-result isolation, Pay/reset, interruption and network recovery. Measure actual capture-to-review latency. Native OCR/quality signals are optional later experiments, not a dependency of this first image-upload flow. Every payment draft requires explicit review/confirmation; the app does not execute payments.

Acceptance: a real photograph produces a reviewable draft on-device; missing/ambiguous data and errors are usable; device observations carry provenance and are independently evaluated. Native OCR does not silently replace backend evidence.

## M7 — Android mobile app

Implement the agreed contract/journey on Android after iOS. Evaluate suitable native OCR/ML Kit capabilities and script support rather than assuming parity. Exercise the shared fixtures plus actual capture, interruption/retry and network conditions.

Acceptance: both apps implement the same field/review semantics with measured platform differences and no provider credentials on the phones.

## M8 — Stable demonstration and findings

Freeze the demonstration configuration; test fresh photographs, laptop/device networking, failure recovery and any clearly labelled replay. Build the separate attendee companion from actual processing events with masked details. Produce the Azikus HTML findings report and substantiated external summary from the measured evidence. Refresh and link the separate cost report using the final configuration; keep it a standalone deliverable.

Acceptance: dependable end-to-end demonstration, reproducible evidence, visible limitations and recovery instructions. Public materials use separately approved sanitised data. No publication, live payment execution or production-validation claim is implied.

## Sequence and authority

Markus authorized review/checks/commit/push/PR/merge for the current changes, followed by a separate chat to reorganize into `backend/`, `frontend/`, `ios/` and `android/` and create/merge its checked PR. Update status and documentation in both steps. Routine implementation choices and checks are autonomous; no new paid calls, completed evaluation reruns, private-data publication or force push. Preserve the current ledger, selected profile, drafts and credentials. The refactor can keep backend and frontend in one deployment; `android/` is a documented placeholder until Android is explicitly started.

After cleanup, wait for Markus to collaborate on the presentation. Further mobile and backend work follows, with Android at the end. Do not start the presentation, new mobile/backend features, Android, automatic discovery or paper detection during this cleanup authorization. Read [coding handoff](CODING_HANDOFF.md) for concrete continuation and [mobile checkpoint](MOBILE_CHECKPOINT.md) for current evidence and known limits.

## Future improvement outside the PoC

On 8 October the user explicitly deferred payment-barcode/QR decoding and payload interpretation beyond this PoC. It is not required for M3, mobile work or final PoC acceptance. Mention it later as a potential improvement in the final findings. Continue extracting printed payment references and identifiers through OCR/document/vision methods; barcode presence in an image does not expand scope. Existing contract fields and historical evidence remain unchanged.
