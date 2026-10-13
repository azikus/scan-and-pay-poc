# Delivery roadmap

## Agreed milestones — status reconciled 13 October 2026

Markus explicitly approved this sequence. These five **next milestones** supersede the old execution order; historical M1–M8 identifiers below remain unchanged so earlier evidence stays traceable. Development milestones may span multiple sessions. Agree the detailed work for each when it starts.

| Next milestone | Scope and completion checkpoint | Status |
| --- | --- | --- |
| 1 — Initial presentation | Create the presentation **together with Markus** from the working PoC and retained measured results. Agree audience, story, format and demo; distinguish delivered functionality, evidence and remaining work. | Delivered 9 October; 25-slide source imported into `presentation/` |
| 2 — iOS improvements and real-invoice testing | Complete the remaining agreed iOS work and verify it with real invoices, review/edit/recovery scenarios and device networking. Record actual mobile timing when measured. | Complete for current scope; Markus accepted the installed update and confirmed end-to-end testing complete on 13 October |
| 3 — Backend/admin improvements and integration testing | Complete the remaining agreed backend/admin work and verify the iOS → backend → admin journey, extraction/review semantics and failure handling. Preserve evidence and version changes. | Complete for current scope; Markus confirmed integration testing complete on 13 October |
| 4 — Android app and both-platform testing | Implement Android against the shared contract, then complete testing across iOS, Android, backend and admin. **This is the final development milestone.** | Next development milestone |
| 5 — Comprehensive final presentation and website HTML | Create a fuller final presentation plus embeddable HTML explaining functionality, workflow, architecture, measured results and limitations using sanitized material. Agree the site's embedding constraints before authoring. | Planned after development |

**User completion update — 13 October:** Markus confirmed that both the iPhone → backend → admin integration testing and the SUNMI live demo are done. This supersedes earlier next-step wording that listed either as unfinished. SUNMI completion is recorded from his confirmation; no additional test results or timing measurements are asserted here. The SUNMI companion is separate from the Android capture/review app. Next: Android and both-platform testing, then the final presentation and embeddable HTML.

**Approved updates before milestone 1:** the extracted-field review/confirmation sheets merged in PR #4. Markus subsequently approved the admin Connection panel and automatic backend network-listener updates; see [connection setup](CONNECTION_SETUP.md). These bounded follow-ups and their supporting tests/docs do not begin the later iOS/backend milestones. The initial deck has since been delivered. Its repository import does not begin later iOS/backend, Android or website implementation.

Continue the existing deck using [presentation/README.md](../presentation/README.md), [PRESENTATION_HANDOFF.md](PRESENTATION_HANDOFF.md) and the revised [continuation prompt](PRESENTATION_PROMPT.md).

The original iOS/admin checkpoint is accepted and merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2); the root backend/frontend/ios/android reorganization merged in [PR #3](https://github.com/azikus/scan-and-pay-poc/pull/3). Android contains a README only. Read [CURRENT_STATUS.md](CURRENT_STATUS.md) for the current selection snapshot; all benchmark selections/results remain dated evidence.

## Authority and preservation

**Latest scoped follow-up, 12 October:** Markus authorized Liquid Glass, screen/crop motion and connectivity/hosting assessment. The hotspot is verified; no hosted deployment or new inference is included. See [iOS scope and evidence](IOS_GLASS_AND_MOTION.md).

The sheets and connection follow-up are merged. Markus authorized the presentation source import, documentation reconciliation and commit/push on 12 October. The milestone sequence is agreed, but is not permission to begin later development or run paid experiments now. Retain the original ledger, current selection, pending drafts, credentials and private evidence. [CURRENT_STATUS.md](CURRENT_STATUS.md) records the latest snapshot and authorized mobile allowance. No new paid calls, completed evaluation reruns, force push or public publication. Read [coding handoff](CODING_HANDOFF.md) for current scope and [mobile checkpoint](MOBILE_CHECKPOINT.md) for prior acceptance.

## Historical delivery record — original M1–M8

The sections below retain the original milestone definitions and dated acceptance criteria. Their prospective wording describes the original plan; it does not start later work or override the five next milestones above. Backend managed OCR shipped before mobile; native OCR remains a separate possible mobile improvement.

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

The first slice has a capture button and manual crop; no paper detection dependency. Test paper-edge detection and a stable live outline during later mobile improvements, retaining manual fallback. This is deferred until after the joint presentation, not a scheduled automation.

Test on Markus's device: orientation/cropping/compression, upload, polling, edits, incomplete/error states, duplicate taps, late-result isolation, Pay/reset, interruption and network recovery. Measure actual capture-to-review latency. Native OCR/quality signals are optional later experiments, not a dependency of this first image-upload flow. Every payment draft requires explicit review/confirmation; the app does not execute payments.

Acceptance: a real photograph produces a reviewable draft on-device; missing/ambiguous data and errors are usable; device observations carry provenance and are independently evaluated. Native OCR does not silently replace backend evidence.

## M7 — Android mobile app

Implement the agreed contract/journey on Android after iOS. Evaluate suitable native OCR/ML Kit capabilities and script support rather than assuming parity. Exercise the shared fixtures plus actual capture, interruption/retry and network conditions.

Acceptance: both apps implement the same field/review semantics with measured platform differences and no provider credentials on the phones.

## M8 — Stable demonstration and findings

Freeze the demonstration configuration; test fresh photographs, laptop/device networking, failure recovery and any clearly labelled replay. Build the separate attendee companion from actual processing events with masked details. Produce the Azikus HTML findings report and substantiated external summary from the measured evidence. Refresh and link the separate cost report using the final configuration; keep it a standalone deliverable.

Acceptance: dependable end-to-end demonstration, reproducible evidence, visible limitations and recovery instructions. Public materials use separately approved sanitised data. No publication, live payment execution or production-validation claim is implied.

## Future improvement outside the PoC

On 8 October the user explicitly deferred payment-barcode/QR decoding and payload interpretation beyond this PoC. It is not required for M3, mobile work or final PoC acceptance. Mention it later as a potential improvement in the final findings. Continue extracting printed payment references and identifiers through OCR/document/vision methods; barcode presence in an image does not expand scope. Existing contract fields and historical evidence remain unchanged.
