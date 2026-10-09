# Decision register

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

## Agreed current sequence — 9 October 2026

Real-invoice iPhone testing is user-confirmed complete. Markus authorized checked PR/merge of the mobile/admin changes, then a separate checked repository-reorganization PR/merge; update status and documentation in both. Next create the presentation together, then improve the mobile client, work on the backend and implement Android last. No new paid calls or additional feature implementation during cleanup. Current truth is [mobile checkpoint](MOBILE_CHECKPOINT.md) and [coding handoff](CODING_HANDOFF.md).

## Historical sequence — 8 October 2026

Finish the bounded fresh 17-image comparison first, then import the usable human review and score correctness (step 5). Unresolved, disputed and unreadable labels stay unscored. Present the concrete results for Markus's confirmation. Only after that confirmation, create the project PR and merge pending PRs in `azikus/scan-and-pay-poc` after review/required checks, then prepare the next-chat handoff. Do not create or merge PRs before that confirmation.

Choose the pipeline with Markus for correctness and total latency, regardless of cost. Continue recording expense and respecting the existing €500 experiment cap. The next implementation focus is the iOS app in another chat, after pipeline selection and agreement on capture/review screens: capture/import an image, send JPEG/PNG to the existing Mac backend, poll and display an editable draft with incomplete/error states. A physical phone needs the Mac's reachable LAN URL, not the phone's `localhost`; make the endpoint configurable. Provider credentials stay on the backend. No mobile implementation or future-chat creation in this chat. Android follows later; barcode decoding remains outside this PoC. See [roadmap](ROADMAP.md).

Handoff baseline reconciled 1 October 2026; implementation/access and new-chat handoff updated 6 October 2026. Current acceptance evidence is in IMPLEMENTATION_STATUS.md; ROADMAP.md maps phases to milestone checkpoints.

## Settled requirements

| ID | Decision |
| --- | --- |
| C01 | Independent Scan and Pay PoC project; target git@github.com:azikus/scan-and-pay-poc.git. |
| C02 | Monorepo, backend first, native designs before code, iOS then Android. |
| C03 | One JPEG/PNG per request; no HEIC/multipage API. |
| C04 | UK sort-code/account pairs and original client samples, including Croatian model/poziv na broj. |
| C05 | Hybrid: local rules, managed OCR/document APIs and selectable provider-hosted proprietary and open-weight LLMs. Payment-barcode/QR decoding is outside this PoC (8 October scope clarification). |
| C06 | Smaller models and stronger controls; freely select models, no compulsory pair. |
| C07 | Unified review journey, explicit confirmation; separate attractive attendee display later. |
| C08 | Shared samples; ordinary camera photos suffice for early backend testing. |
| C09 | Continue implementation in a fresh local chat in the existing project using the current CODING_HANDOFF.md. Current milestone status and continuation scope live in CODING_HANDOFF.md. Final HTML findings remain deferred; a private progress explainer was separately authorized on 7 October. |
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
| P07 | Current requested roster: OpenAI, Mistral, Anthropic, Gemini, xAI, Together-hosted open-weight models, Azure Document Intelligence, Google Document AI, AWS Textract and Mindee. Model variants/stronger controls are selected independently; do not silently remove a provider family. |
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

- The user required all Phase 2 access upfront. All required fields/resources are now supplied, including Google resources/ADC, verified temporary AWS IAM authentication. PHASE2_ACCESS.md records the satisfied gate and remaining pre-inference checks. A later access/product failure is explicit, not a silent vendor waiver.
- Every provider evaluation batch, including compatibility tests and repeats, must cover all samples. Use the complete private image set and its source/page/variant manifest; retain the JPEG/PNG backend. Offline synthetic unit tests remain independent, and saved-response replays are labelled separately from fresh inference.
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

## 7 October: compatibility fixes and private progress overview

The user requested fixing retained provider compatibility, reassessing M2 and a terse private HTML explanation of implementation, results and next steps. The progress overview is authorized now; public publication, mobile and the final findings/attendee companion remain deferred. Preserve all earlier attempts and show processing acceptance separately from unverified accuracy. Cost tracking stays a concise secondary report.

## 8 October: extraction acceptance clarification and image review

The user explicitly accepts an invoice total as the draft payment amount and an account holder or supplier as a valid beneficiary reading. Do not require the literal labels “amount due” or “beneficiary” to count these as valid extractions. Preserve printed roles and evidence; distinct explicit balances, recipients and candidate associations must remain visible. This supersedes the earlier blanket prohibitions on these equivalences.

This clarification is recorded during the sample-review discussion; existing implementation/replay counts still use the earlier review checks. Implement it through a separately versioned interpretation/review policy and full saved-corpus replay, preserving historical profiles and evidence. No fresh inference is needed to reassess saved outputs.

The user offered to establish what each image contains and requested concrete examples of legitimate alternatives, unsupported schemes, nearly blank/supporting pages and Croatian model readings. Assistant-inspected examples are hypotheses until the user verifies the labels. Legitimate alternatives require selection, not an extraction-error label; absent fields must not be scored as missed readings. Keep all inputs in the corpus, including proposed negative/supporting examples, with explicit expected-field labels rather than silently removing them. Private review inventory: `.local/m3-label-review-2026-10-08/inventory.json`.

The next user clarification supersedes the preceding keep-all-inputs proposal: explicitly exclude Milan pages 2, 3, 4, 6 and 8 from the active evaluation set. The new private manifest `.local/evaluation/m3-page-selection-2026-10-08/manifest.json` retains 26 images and records all five exclusions; historical sources/results remain unchanged. Other multipage sources await review. Prefer the full total for Milan and bank transfer when multiple payment methods exist. These preferences do not authorize inventing an IBAN from biller/reference codes or importing fields from another page into a single-image result. The interpretation/review policy implementation remains pending during this labelling discussion.

The user then excluded TIM page 1, asked this chat model to choose suitable A2A/Greek pages and requested the UK pack split into individual invoices. Visual review selects A2A page 1 over page 2 (clear amount/due date/supplier), excludes A2A pages 2-6, and retains Greek pages 1 and 4 (summary with RF code and payment slip) while excluding Greek pages 2/3. A2A's retained page lacks beneficiary bank details; missing-on-page remains distinct from a missed reading. The v2 selection has 18 images, with all exclusions and their authority recorded. Separate UK PDFs preserve the five original pages and existing distinct invoice groupings without duplicating benchmark inputs. This uses existing local images and no paid provider calls; full field labels remain unverified.

## 8 October: barcode handling deferred outside the PoC

The user explicitly removed payment-barcode/QR decoding and payload parsing from this PoC. Do not implement or evaluate a dedicated barcode path in M3 or later PoC milestones. Record the capability in the eventual final findings as a potential follow-up improvement. This supersedes earlier roadmap, backend-plan and test-fixture requirements. Printed IBANs, Croatian model/references, RF references and biller identifiers remain in extraction scope. Existing schema support, saved images and historical outputs are preserved; no runtime change is implied.


### 8 October: expected-field draft and final Milan page exclusion

During manual answer-key preparation, the user explicitly chose to exclude Milan page 7 rather than retain its three instalment-only options. The v3 manifest contains 17 active inputs and 14 explicit exclusions, preserving v2 and original M2 evidence. A private image-grounded draft records values, visible/absent/uncertain status, source locations and linked alternatives for every retained image. No provider output was used as truth, no paid calls were made, and all draft labels await user review before scoring. The side-by-side HTML is a private label-review aid, separate from the final findings report.


### 8 October: white masks over 2D codes for the retained evaluation corpus

The user requested removal of all visible 2D barcodes and explicitly confirmed white masking. The 17-image selection is unchanged; ten symbols on seven images are masked using exact local pixel rectangles, including payment and app-download codes. Original files remain preserved; linear barcodes remain in scope as visible image content. Current variant manifest: `.local/evaluation/m3-no2d-2026-10-08/manifest.json`. All surrounding pixels and output images were checked. Rebuilt private review HTML embeds these variants, field explanations, exact current prompts and separately labelled proposed prompt changes. This does not implement a decoder or change old inference results. Fresh masked-image measurements must use these new inputs, not pre-mask OCR replays.

## 8 October: separately versioned draft policy and masked evaluation preparation

Implement the user's accepted totals/name fallbacks in `payment-draft@1`, retaining printed roles and explicit recipients. Bank transfer is the draft preference; all linked alternatives remain available. Compact image/annotation and OCR-text prompts require printed text only, with barcode decoding outside the PoC. Preserve historical prompt constants, strict review and saved profiles/results. The new policy has a complete offline replay and a separate 17-image, three-method fresh plan; no fresh call has been dispatched. Human review is required for correctness scores, not for continuing completeness/latency/cost evaluation. See [policy evidence and bounds](M3_DRAFT_POLICY.md).
