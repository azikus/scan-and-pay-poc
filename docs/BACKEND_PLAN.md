# Detailed backend-first implementation plan

> Historical scope/checkpoint: retain the dated evidence below. Current scope, runtime and acceptance are in [CURRENT_STATUS.md](CURRENT_STATUS.md), [CODING_HANDOFF.md](CODING_HANDOFF.md) and [ROADMAP.md](ROADMAP.md). Android/final presentation are skipped; mobile/backend/SUNMI and successful phone Send are accepted. Old next-task wording, worktree paths, provider selections and financial admission limits are not current instructions.

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

## Agreed next sequence — 8 October 2026

Finish the bounded fresh 17-image comparison first, then import the usable human review and score correctness (step 5). Unresolved, disputed and unreadable labels stay unscored. Present the concrete results for Markus's confirmation. Only after that confirmation, create the project PR and merge pending PRs in `azikus/scan-and-pay-poc` after review/required checks, then prepare the next-chat handoff. Do not create or merge PRs before that confirmation.

Choose the pipeline with Markus for correctness and total latency, regardless of cost. Continue recording expense and respecting the existing €500 experiment cap. The next implementation focus is the iOS app in another chat, after pipeline selection and agreement on capture/review screens: capture/import an image, send JPEG/PNG to the existing Mac backend, poll and display an editable draft with incomplete/error states. A physical phone needs the Mac's reachable LAN URL, not the phone's `localhost`; make the endpoint configurable. Provider credentials stay on the backend. No mobile implementation or future-chat creation in this chat. Android follows later; barcode decoding remains outside this PoC. See [roadmap](ROADMAP.md).

Handoff baseline, reconciled 1 October 2026; implementation started 2 October. Current handoff update, 6 October: **Milestone 1 complete**, with real UK/HR runs through both starter profiles, corrected shared bank normalization, and a successful independent comparison. Mistral API billing activation was explicitly approved; training remains off. Twelve dispatches retain €12 in conservative holds. The initial OCR rules miss table/prose fields and split a bank block across blank lines; preserve these baseline limitations before later versioned comparisons. The upfront access set is now complete. [Current evidence](IMPLEMENTATION_STATUS.md), [roadmap/milestones](ROADMAP.md) and [next-chat handoff](CODING_HANDOFF.md) describe the next work. API_CONTRACT.md owns wire semantics and ARCHITECTURE.md shows boundaries.

## 1. The first thing we should be able to do

Start a local backend, upload an ordinary photo of a UK invoice, select an enabled extraction profile, and retrieve a structured result with the printed payment fields, evidence, unresolved fields and processing time. Repeat with an original client document using the same service and contract.

Milestone 1 proves one small real vision adapter first, then one managed OCR/rules profile and their independent comparison. A fake adapter supports offline tests, not live milestone completion. Additional providers follow incrementally.

### The main architectural challenge

Do not implement “run every tool and ask another LLM to combine everything” as the default. That would conflate evaluation with product behaviour, increase latency/cost and make it difficult to identify the source of an error.

Implement two operating modes:

- **Compare:** explicitly selected profiles run independently on the same input; return each result, failure, timing and usage separately. No majority-vote payment draft.
- **Extract:** one configured pipeline produces one review result. It may use rules, OCR, document services or a bounded fallback, but each step and its provenance remain visible. Start with a simple pipeline; make it hybrid where experiments justify it.

Hybrid means having composable approaches, not requiring every technology on every request. Keep the LLM-only baseline even if another approach is selected for the demo.

## 2. Scope and monorepo

Target structure; `backend/` and `contracts/` exist. Add new areas only as implemented; mobile/HTML work remains deferred; private cost reporting begins with evaluation:

```text
scan-and-pay/
  backend/             API, jobs, adapters, rules, tests
  apps/
    ios/               first mobile app, after design agreement
    android/           second mobile app
  contracts/           versioned schema, OpenAPI exports, synthetic fixtures
  evaluation/          manifest tools, scorer, benchmark runner, report tooling
  docs/                decisions, plan, operations, findings
  reports/             ignored cost comparisons from M2; final HTML findings later
  samples/             shared originals and photographs; private, ignored
  .local/              private labels, jobs, images, credentials; ignored
  results/             private experimental outputs; ignored
  reference/           unchanged historical material
```

The two apps share contracts and test fixtures, not UI code. Agree capture/review designs before mobile implementation. Build iOS first on Markus's device, then Android. Explore device OCR/ML during that work. Keep the original sample files at their current paths; add photographs and generated evaluation variants in clearly named subfolders with manifest links.

### Selected implementation baseline

- Python with FastAPI/Pydantic for the backend and typed contracts; reuse reviewed Python benchmark ideas and the Python document-processing ecosystem.
- One API process and a bounded worker pool for the local PoC. Keep image decoding and other CPU work off the request path. Avoid a mandatory Redis/Celery/microservice platform initially.
- SQLite for local job metadata and state; local private files for inputs and optional raw responses. Persist state changes around dispatch and completion.
- A small command-line evaluation client calling the same service as the future mobile apps. Direct adapter tests are additional diagnostics, not a substitute for end-to-end API tests.
- Dependency versions locked after an environment compatibility check; Docker packaging is useful later but not a prerequisite to the first localhost run.

This local PoC baseline is implemented for the two starter profiles; planned extensions below are not production-scale capabilities. Markus and the assistant are the delivery team; staffing/code-freeze questions are not blockers. The architecture visual is in ARCHITECTURE.md.

### Framework rationale — decision closed

All three can accept images, call providers, expose typed contracts, coordinate jobs and support good tests. Framework choice does not improve an LLM's accuracy, and Python is not inherently faster at serving requests.

| Option | Why it fits | Trade-off for this PoC |
| --- | --- | --- |
| Python / FastAPI | Typed validation/OpenAPI, evaluation tooling and some reviewed benchmark ideas already in Python; no self-hosted inference dependency. | Isolate CPU-bound work; be disciplined about types/dependencies. Reusing old code is secondary to ecosystem fit. |
| .NET / ASP.NET Core | Strong C# tooling, dependency injection, typed APIs and HTTP clients; valid for all hosted extraction services. | Valid hosted-service alternative; would require different evaluation/service tooling from the selected Python approach. |
| Kotlin / Ktor | Coroutines, explicit HTTP services, Kotlin familiarity and capable testing/serialization. Hosted APIs work equally well. | Valid hosted-service alternative, not selected. Sharing Kotlin does not by itself share native iOS UI. |

**Decision:** Python/FastAPI. The user chose Python; the earlier local-model rationale is superseded by the provider-hosted inference boundary. Do not reopen the framework choice unless a concrete blocker emerges. Provider adapters should not require their vendor's preferred SDK language; REST is an alternative. Third-party SDKs are welcome where they reduce work, with version/licence checks and mocked contract tests.

Official framework capabilities: [FastAPI](https://fastapi.tiangolo.com/features/), [ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0), [Ktor testing](https://ktor.io/docs/server-testing.html).

## 3. Input contract and preprocessing

Public input: **one JPEG or PNG still image per scan**. Photographs and screenshots are supported. No page-selection, HEIC or multipage API is required. Phone capture should upload a documented JPEG/PNG encoding.

Defer bespoke upload-limit and artifact-expiry work. Do not add the previous 20 MiB/50 MP thresholds or seven-day expiry. Keep safe decoding, bounded processing and actual provider input constraints. If an adapter needs a different rendition, record its dimensions and transformation rather than claiming identical bytes.

Preprocessing sequence:

1. Validate the actual image type and successful decode, not just MIME headers or extension; reject malformed/decompression-bomb inputs.
2. Apply EXIF orientation before dropping unnecessary metadata. Retain a private original hash and processing record.
3. Produce a canonical oriented image without aggressive downscaling or automatic enhancement by default.
4. Detect gross quality issues such as tiny text, severe blur, clipping or multiple documents where feasible. Initially surface advisory signals, not an unvalidated “good scan” score.
5. Create adapter-specific renditions only as required, with dimensions, crop/rotation and compression settings recorded.

Deskewing, document cropping and enhancement are separate experimental variants. A crop can remove payment details in a footer; preserve an uncropped fallback and do not assume an enhancement improves recognition.

## 4. Localhost API overview

Use asynchronous jobs even for a single image so slow providers do not impose a fragile long HTTP request on the future mobile app. Polling is sufficient initially; streaming updates are optional later.

| Endpoint | Purpose and result |
| --- | --- |
| `GET /health` | Process/storage readiness. No automatic billable provider probes. |
| `GET /v1/profiles` | Configured profile IDs, provider/model identity, method, capabilities and configuration status; never secrets. “Configured” does not mean a live call has succeeded. |
| `POST /v1/scans` | Multipart image plus mode and profile selection. Returns `202`, scan ID and status URL after validation/acceptance. |
| `GET /v1/scans/{id}` | Job state, stage, completed per-profile results, outstanding profiles, structured errors and the extraction-mode final result when available. |
| `DELETE /v1/scans/{id}` | Remove local input and results; reject/coordinate deletion of running work. Explain any upstream retention the local deletion cannot control. |

`POST` options: `mode=extract|compare`; one pipeline profile for extract, an explicit list or `all_enabled` selection for compare; optional country/language hints; idempotency key. Resolve `all_enabled` to a stored snapshot of implemented, configured, compatible profiles within the run budget; never silently enable accounts or run all possible vendors. Hints must be recorded as supplied context, never presented as observed evidence. Reject unknown profile IDs and unapproved modes; arbitrary provider URLs, credentials, filesystem paths and prompt overrides are not accepted from the caller.

The implemented CLI submits an image to a selected profile, polls and saves the result; it also supports independent comparison between the implemented profiles. README and OPERATIONS.md document actual commands. A comparison that includes a document-API adapter remains planned until that adapter is implemented and verified.

### Job semantics

- Job states: `queued`, `running`, `completed`, `partially_completed`, `failed`, `interrupted`. Store per-profile states independently.
- An ambiguous or incomplete extraction is a completed computation, not an HTTP/server error.
- One failed comparison profile does not discard others. In extraction mode, a failed required stage returns an explicit failure unless an approved fallback profile applies.
- Idempotency key plus input/options hash returns the same accepted job; reuse with different data returns conflict. Identical images submitted under a new key are genuine new runs, not hidden cache hits.
- On restart, unfinished jobs become interrupted; do not silently replay possibly billable requests. Completed results remain retrievable locally; automatic expiry is deferred.
- Caller disconnect does not imply upstream cancellation. Deletion/cancellation policy must prevent orphaned local writes, and record that a dispatched request may still incur cost.

Suggested errors: invalid/unsupported image (`400`/`415`), size limit (`413`), invalid options (`422`), unauthorised (`401`), unknown job (`404`), idempotency conflict (`409`), bounded queue full (`429`), unavailable service (`503`). Provider authentication, quota, timeout, refusal, invalid output and unsupported language are typed per-profile errors, with sensitive details removed.

## 5. Common extraction contract

Maintain a small payment draft for callers and a richer evidence/diagnostic section for evaluation. Both are versioned; provider-specific JSON is private debug material, not the app contract. Provider prompts may use a simplified schema, but adapters must map into the full internal contract and validate it.

### Payment candidate fields

| Group | Fields and meaning (wire names in API_CONTRACT.md) |
| --- | --- |
| Record | Schema version, scan ID, profile/run ID, document language/country observations and separate caller hints. |
| Payee | Printed supplier/payee name plus separately observed account-holder/remittance name. Do not assume they are always identical. |
| Amount | Decimal string, ISO currency code or null, amount role (due/total/instalment/other), printed representation and evidence. Never binary float for canonical money. |
| Destination | Candidate ID and type: `uk_domestic`, `iban`, `biller_reference`, or `unresolved`. Keep related values together as one option. |
| UK destination | Sort code and account number as strings; account-holder name if printed; secondary reference/roll number if explicitly required. |
| IBAN destination | Printed and normalized IBAN; optional BIC and named beneficiary. |
| Croatian remittance | Separately observed model (for example HR plus printed model digits), poziv na broj primatelja, purpose code and description where printed; linked to the destination/amount. Preserve raw form and leading zeroes. Never default a missing model. |
| Biller destination | Explicit scheme/provider/biller code and reference, when known. Without a resolver/integration, this is extracted data, not a complete bank route. |
| Reference | Payment/remittance reference distinct from invoice number and customer number; link it to the appropriate candidate. |
| Other useful fields | Description, invoice number, customer number and due date, all optional. No line-item accounting is required initially. |
| Selection | Selected candidate ID only when justified; otherwise null, alternatives and field-specific reasons. |
| Review state | `ready_for_review`, `needs_review`, `insufficient_data`. User review and explicit confirmation are mandatory for every result. |

Amounts, references and destinations must remain associated. Do not combine a GBP amount with a EUR bank option or take a sort code from one account and a number from another. A candidate should point to its applicable amount/reference observations rather than flattening every number into a shared list.

### Field evidence and uncertainty

Each meaningful extracted field records raw text, normalized value (or null), origin (`document`, `barcode`, `caller_hint`, `derived`), evidence reference and normalization steps. Evidence references the single image ID and a text excerpt; add a bounding box only if it can be grounded. Coordinates use a documented normalized coordinate system on the canonical oriented image, with transforms to original/provider images retained.

A model-supplied quote or box is a claim, not verified evidence. Mark whether it was linked to actual OCR spans/coordinates or remains unverified. Do not invent boxes to make the diagnostic UI look more complete.

Missing, unreadable, conflicting, inferred and unsupported are different states. Use null for unavailable values rather than empty strings or zero. Preserve alternatives when needed. Model/vendor confidence can be retained as a raw diagnostic but must not be compared across engines as a calibrated probability of correctness.

Backend rules, not an LLM's self-declared readiness, compute completeness and review reasons. `ready_for_review` means sufficiently complete and internally consistent for the chosen profile; it does not certify ownership or factual correctness of the bank account.

### Required semantics

- UK domestic completeness normally needs payee, linked sort code/account number, amount and currency; require a reference when the document instructs one. Preserve incomplete outputs rather than suppressing successfully extracted fields.
- Format normalization can remove sort-code separators and IBAN spaces while preserving the raw value. Normalization of references is scheme-specific; do not strip punctuation indiscriminately.
- Implemented in Milestone 1's shared review layer: `schwifty` validates IBAN structure, country length and checksum after formatting normalization. `review@2` also ignores a matching leading bank-field label when comparing raw and extracted values, and uses `pycountry` for equivalent explicit country names/codes. Original text and significant bank characters remain intact; altered digits and conflicting values still require review. These checks apply to every extraction profile.
- Amount selection distinguishes current due amount from VAT, subtotal, previous balance, credit, monthly tariff and optional instalment. Ambiguous choices remain alternatives.
- Printed currency symbols may justify a normalization, but document country or language alone is not an explicit currency. Record any inference; conflicts require review.
- An invoice/customer number is not bank routing. A known biller scheme can make such an identifier useful, but requires a separate rule/adapter with documented semantics.
- Paid/direct-debit wording can be an optional observation, not a mandatory field or automatic extraction rejection. Do not compare historic due dates to today to invalidate test documents.
- Syntax, IBAN checksum and any future UK modulus checks are distinct from account existence and name verification. A failed check must not trigger silent digit substitution. Confirmation of Payee is not implemented by OCR or a regex.

### Country/scheme-aware interpretation

Do not implement a hard language-to-country switch. Maintain separate observations for document language/script, issuer country, billed customer's address, account country and payment scheme. An English invoice can point to an HR IBAN; a UK address may belong to the customer. EUR does not imply Croatia.

Prefer explicit payment signals: labelled sort code plus account number, a recognised IBAN country prefix and structure, Croatian model/poziv na broj labels, or an explicitly supported biller scheme. Language/address are supporting hints, never sole routing proof. A checksum supports format consistency, not account ownership.

Start with a generic extraction pass or observations already obtained by OCR. Apply UK/HR rule packs or prompt supplements when evidence supports them. Record routing reasons, conflicting signals and rule/prompt versions. Do not add a compulsory paid language-classification call to every direct-image baseline. Multiple destinations remain separate; unknown/conflicting routes use generic extraction and review, not a forced country. Compare generic versus routed profiles on the same images before choosing routing as the default.

### OCR ambiguity: O/0, I/1 and similar characters

Keep raw text/boxes immutable. Recognise field context before generating a small set of alternatives: a numeric account component differs from an alphanumeric reference or payee name. Store the original, proposed character change, position, evidence and validation result separately. Never apply blanket replacements across the document.

Validate candidate length/pattern/checksum where applicable. A candidate passing an IBAN checksum is not proof that a substitution is correct. If necessary, re-read the original region with another OCR/vision pass, including enough surrounding context to preserve field meaning. Record crop, extra cost and latency. If evidence remains ambiguous, return alternatives or null and a review/retake reason. Do not silently select a guessed digit merely to make a format check pass. User corrections are recorded separately and never improve the raw benchmark score.

### Relationship to the existing client API (historical context only)

The inspected client `ReadCode` response includes amount, currency, receiver name and description, but also transaction IDs, fees, routing/form information and other business fields. The user clarified that this is historical context, not hard guidance. Reuse only useful semantics, not the transaction object. The PoC returns extraction fields; any later client adapter supplies client-specific transaction/routing behaviour through that client's backend. No fees or transaction IDs should be fabricated by a model.

## 6. Processing components and experiments

All components receive a versioned input descriptor and return observations, errors, stage timing and usage. Keep raw observations immutable; normalization and selection are explicit subsequent steps.

1. **Direct vision LLM:** image to constrained fields. Establish the client's original idea as a baseline.
2. **Managed OCR plus local rules:** image goes to a managed OCR service; returned text/boxes feed local candidate/structural checks. Start with one service. Rules should be general label/position/pattern logic; supplier-specific templates belong in a separately labelled experiment.
3. **OCR plus LLM:** OCR text/layout to semantic fields. Compare with direct vision to identify whether OCR helps or loses layout information. Text-only models can participate here even if they cannot accept images.
4. **Document API:** prebuilt invoice extraction mapped into the contract, with unsupported/missing fields explicit.
5. **Document API plus rules/LLM:** a separate hybrid profile for filling gaps from returned OCR/layout. Never attribute its performance or cost to the unaugmented API.
**Future improvement outside this PoC:** payment-barcode/QR decoding and supported-payload mapping. The user explicitly deferred this on 8 October; it is not part of any PoC milestone or acceptance criterion. Record it in the eventual findings; no implementation or barcode-specific test suite is required now.

Local rules in step 2 run on the backend machine. Managed OCR sends the image externally. No mobile processing is implemented yet.

### Registry and profile composition

A **component** does one job: OCR, invoice parsing, vision extraction, rules or validation. A **profile** describes a versioned sequence of components, including inputs/outputs and any bounded fallback. The public selector chooses profiles, not arbitrary code or user-provided URLs. Examples: Mistral OCR → local UK/HR rules; Azure invoice mapping; Google OCR → selected provider-hosted LLM; direct vision; document API → semantic completion.

Record capabilities: JPEG/PNG support, accepted language/scripts, fields supplied, local/cloud execution, exact model/processor/version, endpoint/region, configured credentials, pricing basis, schema mode and tested status. Distinguish planned, configured and live-validated. Unavailable providers are not silently replaced; return a reason.

Compare runs profiles independently and never turns agreement into payment truth. For shared OCR prerequisites, document whether cached output is reused: charge shared work once to the whole batch, but show the standalone pipeline cost/latency too. Run independent prerequisites for isolated latency comparisons. One profile failure must not hide others.

### Provider rollout

First live adapter: a small vision model, initially GPT-6 Luna subject to account access. Milestone 1 then adds Mistral OCR 4.1 → local UK/HR rules, with independent compare results. Phase 2 expands managed methods: Azure Read/Invoice, Google OCR/Invoice Parser, Mistral annotations and Textract; selected smaller/stronger OpenAI, Anthropic, Gemini and hosted Mistral models; composable OCR-plus-LLM profiles.

Provider-hosted open-weight models are eligible alongside proprietary models; self-hosted inference is excluded. Together, xAI and Mindee are included in the requested adapter roster. A deterministic invoice2data template comparison may consume managed OCR text without model-weight dependencies. A documented provider is not an implemented adapter. The full upfront credential/resource set was supplied on 6 October; concrete processing/access limitations still require explicit reporting and cannot silently remove a provider.

See [provider shortlist and budget](PROVIDERS_AND_BUDGET.md) for current exact model candidates and €500 allocation. Self-hosted inference, weight downloads and project-operated cloud/GPU model servers are out of scope.

## 7. Validation, runtime and data controls

Use standard schema validation and explicit semantic validators. The old hand-written JSON-schema subset validator is not the new contract authority. Tests must cover nested nulls, unknown properties, decimal handling and cross-field pairing.

Start with a bounded queue and at most two outbound calls, configurable per provider. Record queue wait separately from inference. Follow API_CONTRACT.md: initial smoke profiles make one attempt, with a 90-second stage timeout and 240-second job deadline. Later transient retries need an explicit bounded profile revision. Do not retry invalid credentials or malformed requests. Retries and partial billed failures count toward run usage; exact upstream billing can remain unknown.

Before a comparison batch, show documents x variants x profiles x repeats and an estimated spend where pricing is known. The total authorised budget is €500, including a reserve for tax/FX/retries; use a first smoke-test tranche of at most €30 within that total. Enforce maximum calls, concurrency and output limits. An estimated spend cap is not a guarantee of the provider's final invoice: unknown/retried charges need explicit handling and provider-side account limits where available.

Bind to loopback by default. Use a local bearer token, narrow file permissions and no permissive browser CORS by default. Credentials stay server-side; callers never supply them in image requests. Sanitize errors and logs. Treat document text as untrusted data; it cannot alter instructions, make tool calls, fetch URLs or select provider endpoints.

Keep private inputs, answer keys and results under ignored directories. Custom expiry/cleanup scheduling is deferred; do not remove curated originals. A manual local deletion does not imply deletion from a provider.

### Data-destination ledger

The user permits client-sample provider testing. Each stage records scan/profile ID, actual service/host, account/region configuration, request timestamp, payload classes (full image, crop, OCR text/boxes, extracted fields), source/rendition hash, provider request ID if available, returned artifacts and local storage location. Do not log secrets or unnecessarily copy raw payment fields into application logs. If geographic processing/residency cannot be established, record **unknown** rather than infer it from a URL.

Local rules send nothing externally; managed OCR sends the image; OCR → cloud LLM sends document text (and layout/crop only if configured); a document-API → cloud-LLM profile sends data to two services. Text-only is not personal-data-free. Provider retention/training terms depend on product, account and settings and must not be invented.

ARCHITECTURE.md illustrates these paths; the final HTML report is deferred. The later live companion reads this ledger and stage events, with private details masked for public display. Client testing permission does not automatically permit conference display or repository publication.

No external calls are made during startup/health checks. Model-weight downloads and provisioning self-hosted inference are out of scope; paid provider inference is an explicitly bounded operation. “Backend on localhost” does not mean invoice data never leaves the machine.

## 8. Four delivery phases

[ROADMAP.md](ROADMAP.md) is the naming authority: Phase 1 = M1; Phase 2 = M2–M4; Phase 3 = M5–M7; Phase 4 = M8. M2 provider coverage and M3 interpretation improvements can overlap. Backend OCR already exists in M1; native OCR remains later mobile work.

### Phase 1 — Localhost service and first method comparison

Completed as Milestone 1. The following records its implementation scope; the new coding chat starts M2 using CODING_HANDOFF.md:

4. Establish backend package, pinned dependencies, common contracts and offline test fixtures.
5. Implement input validation, canonical image handling, job persistence and the five basic API endpoints.
6. Add fake adapters for tests, then one real small vision adapter and one managed OCR/local-rules profile; map, validate and persist independent results.
7. Add the command-line submission/polling path, profile configuration and basic timing/usage capture.
8. Document startup, credentials setup, upload, result inspection and cleanup.

Completion evidence: reproducible local startup; live vision and managed-OCR profile outputs for the selected UK and Croatian reference images, with real photos added when available; sort code/account pairing and leading zeroes preserved where present; missing/ambiguous fixture behaviour shown; invalid input/provider failure paths tested; no client app changes. A provider failure is reported, not disguised as a model extraction.

### Phase 2 — Compare methods and select a provisional pipeline

User priority: broaden provider coverage alongside improving OCR interpretation. The upfront credential/resource gate in [PHASE2_ACCESS.md](PHASE2_ACCESS.md) was satisfied on 6 October. Every provider evaluation must cover the full sample corpus. M2 delivers provider coverage/tooling, M3 improved interpretation and separately measured hybrids, and M4 reviewed comparisons/pipeline selection. The queue, code boundaries and acceptance checklist are in [PHASE2_ROLLOUT.md](PHASE2_ROLLOUT.md). Do not make successful tuning of the two starter profiles a prerequisite for other integrations or assume a hybrid must win.

1. Catalogue/group original documents and prepare labels, image variants and split assignments alongside integration work; unverified labels block scoring, not adapter development.
2. After the full access gate, add comparison adapters across the shortlisted LLM, managed OCR and document-service families with offline adapter fixture tests and full-corpus live evaluations, including compatibility batches. Account for all samples and explicit failures; do not return to a two-image subset.
3. Extend managed OCR/rules with structural/association regressions while adding OCR-plus-LLM, document annotations and document-API augmentation as separate profiles. Preserve the unaugmented baselines and shared v1 validation.
4. Run the controlled evaluation from EVALUATION_PLAN.md; retain per-document failures, not just average scores.
5. Select a provisional extraction pipeline based on correctness, missing-field behaviour, latency and cost. Test a bounded fallback against the baseline; retain it only if the observed trade-off is useful.
6. Save machine-readable measurements, a concise Markdown experiment log and a separate per-option cost report under [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md); tag a profile/configuration for mobile integration. Cost reporting begins with M2 and is an M4 acceptance deliverable. Defer the polished HTML findings to Phase 4.

Completion evidence: comparable independent results for the approved full-corpus matrix; reproducible runs; UK and client breakdowns; no unlabelled hidden augmentation; selected pipeline rationale and known limitations. Only the user may waive an unavailable provider from the upfront access gate.

### Phase 3 — Agree mobile designs, build iOS first, then Android

Later scope, with M5 design agreement before M6 iOS and M7 Android. Phase 1 already establishes the backend contract; Phase 2 can continue alongside explicitly requested mobile work, which need not wait for an exhaustive provider tournament. Do not start mobile work as part of the current handoff/M2 task.

1. Agree the native capture/review UX separately: capture/import, processing, editable draft, missing-field/retake and demo confirmation states.
2. After design approval, connect iOS first to the tested job API on Markus's device. Prove upload/result rendering and review/confirmation before capture automation. Then implement the same contract on Android.
3. Test LAN connectivity, foreground/background interruptions, retries, upload orientation/compression and the same canonical field fixtures on both platforms.
4. Explore Apple Vision/VisionKit OCR, capture quality and document detection during iOS work; evaluate ML Kit or relevant native components later on Android. The image request may include optional device observations: image hash, text/boxes, coordinate space, orientation/crop transforms, language hypotheses, engine/OS/device version and processing time. Validate their association and shape on the backend; treat them as untrusted observations, not truth. Image-only requests must continue to work. Measure image-only, image+device-OCR and text-only where suitable; OCR can help, but can also lose layout or propagate character errors.
5. Measure end-to-end capture-to-review latency, battery/thermal impact if relevant, image size and retake/correction behaviour. Only then decide whether on-device results replace or supplement backend steps.

Completion evidence: both native apps photograph a document and populate the same review contract; correct leading-zero display/editing; partial results and errors are usable. Dedicated barcode decoding remains outside the PoC. Mobile UX approval is separate from this backend plan.

### Phase 4 — Stabilise the demonstration and package the findings

M8 in ROADMAP.md; deferred from the next implementation chat.

1. Freeze the demonstrated profile/configuration and test it with fresh photographs, not only files used during tuning.
2. Build the Azikus attendee companion as a visually clear explanation of the actual scan journey: selected methods, local/cloud destinations, progress, evidence-backed fields, differences, elapsed time and known/estimated/unknown cost. Use large readable typography and a coherent narrative, not logs, developer tooling or invented live metrics. Keep operator diagnostics separate and private fields masked. A browser is acceptable for this separate display, not the customer app.
3. Verify both apps against the demo laptop/network; restrict LAN access, configure secure transport and keep provider credentials off the phones. A phone's `localhost` is the phone, not the laptop.
4. Document setup, recovery and network/provider failure behaviour. If recorded results are available as a fallback, explicitly label them as replay, never as live extraction.
5. Refresh the separate cost report for the final configuration and link it from the final internal HTML findings report: tested approaches, results, failure examples, costs and next improvements. Prepare the BD-facing summary using the existing Azikus proposition and only substantiated claims.
6. Prepare a sanitised repository/demo corpus if requested. Public publication, licensing and redistribution require separate approval.

Completion evidence: dependable native end-to-end demonstration, a recoverable backend, visible limitations and a reproducible evidence pack. This is not a claim of production validation or a business go/no-go exercise.

## 9. Protect the critical path

Core: image upload, small vision and managed OCR/rules profiles, correct common contract, UK/client fixtures, measured hybrid comparison, both native apps, honest review/error behaviour.

Do not make these prerequisites for the first backend: a browser dashboard, every model family, local GPU inference, fine-tuning, generic multi-page document splitting, all payment barcode schemes, or full payment execution integration.

Markus and the assistant are doing the work; no engineer-availability or code-freeze questionnaire is required. Sequence by demonstrable outcomes: working backend, meaningful comparisons, agreed designs, iOS, Android and the companion. Phase 2 access collection is complete; offline implementation is next. Self-hosted inference setup is excluded.

## 10. Ready for handoff

Python, image-only input, async jobs, paired candidates, independent comparison, provider order and Milestone 1 criteria are recorded in the handoff. Milestone 1 is complete. Phase 2 uses the upfront credential checklist, full-corpus policy and resume context in PHASE2_ACCESS.md and PHASE2_ROLLOUT.md. Mobile UX and public-demo permissions remain later decisions.

## 11. Test strategy and coverage targets

Use third-party SDKs for standard transport/authentication where helpful; our tests focus on adapter mappings and domain behaviour. Keep live tests opt-in and budgeted. No API calls in the unit-test suite.

Implementation target for our backend domain/orchestration code: **at least 90% statement coverage and 85% branch coverage**, with every listed payment-critical scenario explicitly tested. Report scope/exclusions; generated contracts, vendored SDKs and unused scaffolding must not inflate coverage. Milestone 1 measured 98.77%/95.17%; see IMPLEMENTATION_STATUS.md for its exact scope and date, and remeasure after implementation changes.

- Unit tests: amount/currency semantics, leading zeroes, UK account pairing, Croatian model/reference, aliases, nulls, routing conflicts, OCR O/0 and I/1 alternatives, ambiguous totals and references.
- Property-based tests where useful: formatting normalisation preserves significant characters and is idempotent; decimal round trips; candidate pairing cannot cross-contaminate.
- Adapter fixtures: real-shaped redacted responses, missing/wrong types, structured-output limits, token/page minimum accounting, polling, timeouts, refusal and invalid credentials.
- Orchestration/API tests: mode/profile selection, all-enabled snapshot, unsupported input, bounded retries, partial comparison success, restart/interruption, idempotency and no silent provider fallback.
- Data ledger tests: image versus text destinations, transformations, unknown residency/cost, secret-redacted errors, no prompt/tool execution from invoice text.
- Evaluation tests: answer-key versions, per-image visibility, exact critical-field/record scoring, no counting user corrections as model accuracy, shared OCR cost attribution.
- Mobile contract fixtures later: decimal/display fidelity, reference edits, processing errors, explicit confirmation and optional device observations tied to the exact image.

A failed critical scenario must be fixed even if the headline coverage percentage is high. Lock tests to API_CONTRACT.md and the acceptance checklist; do not treat the diagram as evidence of implementation.
