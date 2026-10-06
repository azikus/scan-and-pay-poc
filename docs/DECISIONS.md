# Decision register

Handoff baseline reconciled 1 October 2026; implementation/access and new-chat handoff updated 6 October 2026. Current acceptance evidence is in IMPLEMENTATION_STATUS.md; ROADMAP.md maps phases to milestone checkpoints.

## Settled requirements

| ID | Decision |
| --- | --- |
| C01 | Independent Scan and Pay PoC project; target git@github.com:azikus/scan-and-pay-poc.git. |
| C02 | Monorepo, backend first, native designs before code, iOS then Android. |
| C03 | One JPEG/PNG per request; no PDF/HEIC/multipage API. |
| C04 | UK sort-code/account pairs and original client samples, including Croatian model/poziv na broj. |
| C05 | Hybrid: local rules/barcodes, managed OCR/document APIs and selectable provider-hosted proprietary and open-weight LLMs. |
| C06 | Smaller models and stronger controls; freely select models, no compulsory pair. |
| C07 | Unified review journey, explicit confirmation; separate attractive attendee display later. |
| C08 | Shared samples; ordinary camera photos suffice for early backend testing. |
| C09 | Continue implementation in a fresh local chat in the existing project using the current CODING_HANDOFF.md. Milestone 1 is complete; M2 is next. HTML report deferred to the end. |
| C10 | Python selected. €500 experiment cap; full upfront credential set supplied on 6 October, no automatic subscriptions. Ask only for specific missing/expired access thereafter. |
| C11 | Provider sample testing authorized; record destinations. Public display/publication separately approved. |
| C12 | Markus and assistant build this; staffing/code-freeze questions are not blockers. |
| C13 | Bespoke upload limits and expiry deferred; decoding safety/provider limits retained. |
| C14 | Third-party SDKs allowed; meaningful tests/high coverage required. |
| C15 | Native device OCR/ML explored during mobile work; optional observations tied to exact image. |
| C16 | Historical Aircash endpoint is context, not a required schema. |
| C17 | Barcode-free Croatian PNG already verified; missing screenshot is not a backend blocker. |
| C18 | Provider-hosted open-weight models are allowed alongside proprietary models. Exclude self-hosted inference locally or on project-operated cloud/GPU servers, weight downloads and model-serving deployments. Self-hosted PaddleOCR/Docling model pipelines remain excluded; managed APIs and open-source application libraries are allowed. |

## Handoff implementation defaults

These are the baseline to implement, not another unanswered architecture questionnaire. Amend explicitly if new evidence requires it.

| ID | Baseline |
| --- | --- |
| P01 | Python 3.12, FastAPI/Pydantic v2, SQLite/local files; lock compatible dependency versions during implementation. |
| P02 | Single API process, bounded workers, initially two outbound calls maximum; no Redis/Celery prerequisite. |
| P03 | Async jobs/polling and extract/compare registry; API_CONTRACT.md defines exact semantics. |
| P04 | Typed candidates link route, amount and references; field evidence and null/ambiguity. |
| P05 | Backend review rules; every draft requires confirmation, no account ownership certification. |
| P06 | Milestone 1: offline service/tests, small vision adapter, managed OCR/rules profile, independent comparison. |
| P07 | Current requested roster: OpenAI, Mistral, Anthropic, Gemini, xAI, Together-hosted open-weight models, Azure Document Intelligence, Google Document AI, AWS Textract, Nanonets and Mindee. Model variants/stronger controls are selected independently; do not silently remove a provider family. |
| P08 | First choices GPT-6 Luna and Mistral OCR 4.1, subject to account access. Record any explicit substitution. |
| P09 | Backend OCR now, native device experiments later. No compulsory OCR stage in the direct-image baseline. |
| P10 | No paid/direct-debit rejection or silent O/0/I/1 banking repair; evidence-based UK/HR routing. |
| P11 | Loopback bearer token, server-side credentials, stage-level data ledger and bounded paid-call accounting. |
| P12 | ≥90% statement/≥85% branch targets for domain/orchestration plus all critical scenarios. Milestone 1 measured 98.77%/95.17%; preserve the targets as implementation expands. |
| P13 | €240 LLM, €130 OCR/document, €50 commercial evaluation, €80 reserve. Hosted open-weight calls use the LLM/OCR envelopes as applicable; no self-hosting infrastructure allocation. First ≤€30 smoke tranche included. |
| P14 | Preserve reference code/old HTML privately. Architecture diagram is handoff documentation, not a findings report. |

## Implementation clarifications — 2 October 2026

- Milestone 1 kickoff received. GitHub remote rechecked private/empty; existing folder initialized on `codex/backend-foundation`, without commits/pushes.
- Exact Mistral OCR 4.1 wire identifier is `mistral-ocr-4-1`, verified in current official documentation. OpenAI remains `gpt-6-luna`; no substituted model.
- Canonical outbound pixels use lossless RGB PNG after EXIF orientation, white alpha flattening and metadata removal. No resize. Original bytes/hashes and transforms stay private.
- Two job workers; profiles within each comparison run sequentially and independently. This limits outbound calls to two and preserves visible partial results without shared OCR.
- Hash-versioned profile/config snapshots, one attempt, 12,000 output-token cap for vision, 90-second execution boundary and 240-second queue-inclusive job deadline. Default smoke capacity is 12 paid calls and €30; batch reservation is all-or-nothing. USD estimates never reduce EUR ceilings without explicit billing/FX reconciliation.
- General OCR labels and paragraph/two-cell-table associations are the first rules baseline. Raw OCR remains private and immutable. No supplier answers/templates, semantic-model augmentation or invented field boxes. Complex layouts may legitimately yield incomplete results.
- Deterministic bank normalization rejects differences between raw and proposed significant characters, even if a proposal passes checksum. Only observed, evidenced GBP/EUR completeness is supported for initial readiness; other currencies remain reviewable.
- Current generated contracts live under `contracts/v1`; original synthetic handoff examples remain preserved and validated. Live profile flags remain false until actual configured runs succeed.

## Live integration clarifications — 5 October 2026

- Both keys were supplied locally; read-only provider APIs confirmed exact model access. Public terms/pricing checked; residency, retention and negotiated billing remain unknown. The user later disabled Mistral API training; the signed-in UI verified training and Labs off before further calls.
- Account access does not prove OCR quota: Mistral returned HTTP 429 before and after funding. The post-funding error was `rate_limited`, code `1300`. Admin showed API pay-as-you-go disabled; the user explicitly approved activation, after which both OCR images succeeded. Training stayed off and auto-recharge was not enabled.
- Add OpenAI cache-write usage at its published rate and request the default service tier. Missing cache-write usage leaves cost unknown. This correction preceded all paid calls.
- An actual HR response exposed an amount-format gap between the generated provider schema and v1's runtime validator. `payment-image@2` shares v1's lexical constraints with the provider and preserves printed formatting in raw evidence. Deliberate new UK/HR runs validated this profile; earlier results remain unchanged.
- `review@2` corrects false conflicts from matching field labels in banking `raw_text` and equivalent explicit country names. `schwifty` remains the shared IBAN validator; significant characters, evidence and stored historical results are preserved. Synthetic regressions reject changed digits and real conflicts.
- A, B and C are complete. New UK/HR `review@2` vision runs remove false banking ambiguity; HR is ready for review, UK retains amount-role review. Mistral OCR/rules completed both images, followed by a successful HR comparison. Its local rules still miss table/prose fields and split the UK bank block into incomplete candidates; do not conceal this with an unlabelled LLM. Every draft requires confirmation. Twelve dispatches retain €12; costs remain per-currency estimates/unknowns and labels remain unscored.

## Hosting-scope correction — 5 October 2026

The user explicitly clarified: open-weight models are welcome; self-hosted models are not. The previous blanket exclusion was a mistaken interpretation. Provider-operated APIs for open-weight models are eligible under the same capability, data-use and budget checks as proprietary APIs. Do not deploy or operate inference locally or on project cloud/GPU servers, or download model weights. The next shortlist includes hosted Mistral Small 4 and Medium 3.5, with other hosted open-weight candidates as useful. Milestone 1 results and the twelve-call ledger remain unchanged.

## Phase 2 priority — 5 October 2026

The user requested the other LLMs, document APIs and OCR services as soon as possible, alongside general OCR interpretation improvements. Integrate across the shortlist without waiting for the starter rules to be complete. Direct-image LLM, OCR/rules, OCR-to-LLM, prebuilt document mapping and augmented extraction remain separately versioned methods sharing v1 and review logic. Add synthetic failure-class regressions and private saved-output replays without hardcoding invoice answers or changing correctness expectations. [PHASE2_ROLLOUT.md](PHASE2_ROLLOUT.md) records the queue and acceptance criteria; this update adds no adapter or live-run evidence.

## Access completion and remaining inputs — 6 October 2026

- The user required all Phase 2 access upfront. All required fields/resources are now supplied, including Google resources/ADC, verified temporary AWS IAM authentication and Nanonets management/schema access. PHASE2_ACCESS.md records the satisfied gate and remaining pre-inference checks. A later access/product failure is explicit, not a silent vendor waiver.
- Every provider evaluation batch, including compatibility tests and repeats, must cover all samples. Prepare private image renditions of PDF pages and a source/page/variant manifest; retain the JPEG/PNG backend. Offline synthetic unit tests remain independent, and saved-response replays are labelled separately from fresh inference.
- Before another paid batch: record a new matrix/call cap against the existing twelve holds; the starter cap is exhausted. No credentials or account changes remain required for the two completed starter integrations.
- Before accuracy claims: Markus checks assistant-drafted critical-field labels; unresolved/unverified fields remain unscored. This does not block coding or compatibility smoke tests.
- Later: targeted photos, mobile designs and public-demo sanitization/permission. Further commercial commitments need a concrete user decision; no unrequested provider/account is an extra startup gate.

## Authorization chronology

The original exploration/handoff ended on 1 October. Backend implementation began on 2 October; Milestone 1 completed on 5 October. The user then requested broader provider coverage, every-sample evaluation and upfront credentials. Account preparation completed on 6 October with no further sample processing. The earlier handoff refresh outlined the next phases/milestones without code changes. The subsequent 6 October request authorizes codebase cleanup, all-document reconciliation, a separate per-option cost report, commit/push to private `main`, and creation of the next local chat. No paid calls occur during cleanup/handoff.

The proposed milestone breakdown preserves the four existing phases: M1 foundation; M2 provider breadth/tooling, M3 interpretation/hybrids and M4 reviewed selection; M5 mobile designs, M6 iOS and M7 Android; M8 demonstration/findings. These checkpoints do not change wire semantics, require sequential completion of all M2 work before useful M3 regressions, or authorize deferred mobile/display work. Continue from the current handoff without reopening settled architecture.

## Checkpoint and separate cost deliverable — 6 October 2026

- Require the standalone cost comparison described in [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md). Start with M2 measurements, deliver for M4 and refresh for M8; it is separate from the final HTML findings.
- Keep useful existing code; move the synthetic adapter into test support, exclude tests from the runtime wheel, fix concurrent readiness probes with a reproducing regression, and privately archive the unused historical architecture bitmap. Broader provider refactoring remains M2.
- Commit/push this reviewed checkpoint directly to the existing private remote's `main` as explicitly requested; do not force push. Then create a fresh local continuation chat in this project. Future implementation starts on a `codex/` branch after state inspection; private samples, labels, results and credentials remain in this workspace and outside Git.
