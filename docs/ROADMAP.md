# Delivery roadmap

Updated 6 October 2026. Phases are the four broad delivery stages from `BACKEND_PLAN.md`; milestones are reviewable checkpoints inside them. M1 was already defined and is complete. M2–M8 make the remaining plan explicit; they are proposed delivery checkpoints, not claims of completed work or authorization to start the deferred mobile/display work.

| Phase | Milestones | Current status |
| --- | --- | --- |
| 1 — Backend foundation and first comparison | M1: service, v1 contract, vision and managed OCR/rules | Complete; measured evidence retained |
| 2 — Provider breadth, extraction quality and evaluation | M2: provider coverage/tooling; M3: better interpretation/hybrids; M4: reviewed comparisons/pipeline selection | Next; complete upfront access set supplied |
| 3 — Mobile designs and implementation | M5: agreed designs; M6: iOS; M7: Android | Deferred; no mobile code now |
| 4 — Demonstration and findings | M8: stable demo, attendee companion and final report | Deferred; no browser product UI or HTML report now |

Backend managed OCR already shipped in M1. M2 broadens OCR/document providers; M3 improves how their observations become payment candidates. Native platform OCR belongs to mobile work. These are separate capabilities, not conflicting milestone assignments.

## M1 — Backend foundation: complete

Python/FastAPI/Pydantic, private JPEG/PNG processing, SQLite jobs/stages, bounded workers, v1 endpoints, CLI and independent comparison. GPT-6 Luna vision and Mistral OCR 4.1/local rules both have UK/HR runs. Shared review normalization includes IBAN validation and resolves false format-only bank conflicts. Latest cleanup verification on 6 October: 184 offline tests, 98.76% statement/95.11% branch coverage; the concurrency regression passes and production packaging excludes synthetic test support. OCR-rule gaps, legitimate review reasons, prior failures and unverified labels remain visible in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md).

## M2 — Provider coverage and full-corpus evaluation tooling: next

Scope:

- Create the private source/page/variant manifest and JPEG/PNG renditions of all PDF pages. Add API-based batch execution and explicit complete/failed/not-run coverage accounting.
- Make models/methods independently selectable, enabled, versioned and costed. Preserve old results/profile snapshots and the current default extract profile.
- Add tested adapters across OpenAI, Mistral hosted vision/OCR/annotations, Anthropic, Gemini, xAI, Together-hosted open-weight models, Azure Document Intelligence, Google Document AI, AWS Textract, Nanonets and Mindee. Existing adapters are extended/reused, not rewritten for each model. No exhaustive Cartesian product of models or mandatory small/large pairs.
- Separate vendor transport/mapping, immutable document observations, extraction methods and shared review. Add per-stage accounting/provenance before multi-call compositions.
- Begin the [separate cost report](COST_REPORT_PLAN.md), with one row per exact option, complete coverage accounting, tariff provenance, observed stage/retry usage and explicit unknowns.
- Perform account-specific capability/terms/region/pricing checks, then bounded compatibility runs over every sample for each selected profile. Preserve the exhausted starter cap and twelve existing holds; record the next cap/plan before dispatch.

Acceptance: meaningful offline tests pass; every corpus input is accounted for; representative compatible profiles cover each requested provider family with full-corpus attempt records. Individual document failures are visible outcomes. Account/product blocks and early stops leave that profile's coverage incomplete, so overall M2 remains partial until resolved or explicitly removed from scope by the user. No accuracy ranking is required or allowed from unverified labels. The configured Nanonets custom workflow must be labelled as such, and unsupported fields must remain missing.

## M3 — Better extraction and separately measured hybrids

Can overlap M2; broad integration must not wait for perfect rules. Add synthetic regressions first for bank-section association, multi-column amount roles, Croatian model/reference instructions, multiple payment options and conflicting evidence. Improve general rules without supplier/sample lookup tables. Keep shared `schwifty` validation; UK modulus validation is an optional, separately justified library/table check with licence/version handling, not account ownership verification.

Add selected OCR → LLM, schema-annotation and document-augmentation profiles; preserve raw document mappings and direct-image baselines. Add supported payment-barcode parsing with synthetic payload fixtures and explicit unsupported cases; never follow arbitrary QR URLs. Measure methods independently, retaining source spans, actual recipients, stage costs and failure behavior.

Acceptance: failure-class regressions and counterexamples pass; private saved-response replay covers all available corpus recordings with explicit gaps; promising methods have separately labelled full-corpus fresh evaluations. Old results remain immutable. No test expectations are weakened to force completion/readiness, and no hybrid is assumed better in advance.

## M4 — Reviewed comparison and provisional pipeline selection

Verify critical labels and source/layout groups with Markus; keep unresolved fields unscored and held-out groups out of tuning. Compare field/record correctness, critical errors, missing/ambiguous outcomes, latency, cost and coverage across UK/client cohorts. Select a provisional pipeline from measured evidence, including direct image if it performs best. Evaluate any bounded fallback as its own versioned policy.

Acceptance: reproducible measurements, a Markdown experiment record and the separate per-option cost report support the selection and its limitations. The cost report includes comparable per-attempt/document/corpus costs and qualified volume scenarios; cost per correct result requires reviewed labels. Checked labels underpin every accuracy claim; camera claims require actual camera inputs. Freeze a versioned profile/configuration suitable for mobile integration, with genuine review/retake paths. Final HTML remains in M8.

## M5 — Agree the mobile experience

Later scope: capture/import, actual processing, editable review, missing-field/retake, provider failure and explicit demo confirmation. Use the same payment contract, preserve leading zeroes and distinguish review from executing a payment. Apply Azikus styling to designed artifacts, never invoice originals.

Acceptance: Markus agrees the screens/states and API mapping before mobile code. Phase 3 may begin after that explicit scope/design agreement and a stable backend; it need not wait for every optional model comparison in Phase 2.

## M6 — iOS mobile app

Implement the agreed journey on Markus's device and test upload, polling, edits, cancellation/interruption and network recovery. Measure actual camera orientation/compression and capture-to-review behavior. Explore Apple native OCR/quality signals as optional observations tied to the exact image, while preserving image-only operation.

Acceptance: a real photograph produces a reviewable draft on-device; missing/ambiguous data and errors are usable; device observations carry provenance and are independently evaluated. Native OCR does not silently replace backend evidence.

## M7 — Android mobile app

Implement the agreed contract/journey on Android after iOS. Evaluate suitable native OCR/ML Kit capabilities and script support rather than assuming parity. Exercise the shared fixtures plus actual capture, interruption/retry and network conditions.

Acceptance: both apps implement the same field/review semantics with measured platform differences and no provider credentials on the phones.

## M8 — Stable demonstration and findings

Freeze the demonstration configuration; test fresh photographs, laptop/device networking, failure recovery and any clearly labelled replay. Build the separate attendee companion from actual processing events with masked details. Produce the Azikus HTML findings report and substantiated external summary from the measured evidence. Refresh and link the separate cost report using the final configuration; keep it a standalone deliverable.

Acceptance: dependable end-to-end demonstration, reproducible evidence, visible limitations and recovery instructions. Public materials use separately approved sanitised data. No publication, live payment execution or production-validation claim is implied.

## Sequence and authority

The next implementation chat starts M2, with useful M3 work alongside it. M4 needs measured comparisons and checked labels. M5–M8 remain later scope, not automatic work authorized by finishing M2. No estimated dates are invented; the event context is not an internal deadline.

Detailed execution: [coding handoff](CODING_HANDOFF.md), [Phase 2 rollout](PHASE2_ROLLOUT.md), [evaluation plan](EVALUATION_PLAN.md) and [backend plan](BACKEND_PLAN.md). Latest user instructions override this proposed breakdown. The €500 total, included ≤€30 first tranche, mandatory review, full-corpus batches and hosting/privacy boundaries apply throughout.
