# Product context and requirements

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

## Agreed current sequence — 9 October 2026

Real-invoice iPhone testing is user-confirmed complete. Markus authorized checked PR/merge of the mobile/admin changes, then a separate checked repository-reorganization PR/merge; update status and documentation in both. Next create the presentation together, then improve the mobile client, work on the backend and implement Android last. No new paid calls or additional feature implementation during cleanup. Current truth is [mobile checkpoint](MOBILE_CHECKPOINT.md) and [coding handoff](CODING_HANDOFF.md).

## Historical sequence — 8 October 2026

Finish the bounded fresh 17-image comparison first, then import the usable human review and score correctness (step 5). Unresolved, disputed and unreadable labels stay unscored. Present the concrete results for Markus's confirmation. Only after that confirmation, create the project PR and merge pending PRs in `azikus/scan-and-pay-poc` after review/required checks, then prepare the next-chat handoff. Do not create or merge PRs before that confirmation.

Choose the pipeline with Markus for correctness and total latency, regardless of cost. Continue recording expense and respecting the existing €500 experiment cap. The next implementation focus is the iOS app in another chat, after pipeline selection and agreement on capture/review screens: capture/import an image, send JPEG/PNG to the existing Mac backend, poll and display an editable draft with incomplete/error states. A physical phone needs the Mac's reachable LAN URL, not the phone's `localhost`; make the endpoint configurable. Provider credentials stay on the backend. No mobile implementation or future-chat creation in this chat. Android follows later; barcode decoding remains outside this PoC. See [roadmap](ROADMAP.md).

Current implementation follow-up: M2 adapters, full-corpus tooling and general OCR rules v2 are implemented, with live evaluation recorded in [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Historical baseline descriptions below keep their original context; [M2_OPERATIONS.md](M2_OPERATIONS.md) owns current evaluation operations.

Reconciled for coding handoff, 1 October 2026; current implementation/access state refreshed 6 October. Planning record reconstructed from visible user requests, the blueprint and workspace inspection; not a verbatim transcript. Latest user instructions take precedence over historical references. See ROADMAP.md for the phase/milestone map and CODING_HANDOFF.md for the next chat.

## 1. What we are making

A reusable Scan and Pay capability: photograph a bill, invoice or other payment document and receive an editable payment draft. The user must review and confirm the extracted details. They should not need to know whether the system used OCR, a document API or a language model; all methods feed the same review journey.

The initial eight examples are a starting point, not the product's boundary. A document with a payee, amount and payment identifiers is a candidate. It may still lack a complete payment route: a customer number is not a beneficiary bank account, and some biller references need an integration.

The goal is useful extraction, transparent uncertainty and a report of measured results. A few successful scans cannot establish universal invoice support or rare-error reliability.

## 2. Two cohorts, one engine

### UK / London

Prioritise English-language UK invoice photographs, linked sort code/account number, payee/account holder, amount, currency and required payment reference. Preserve leading zeroes and distinguish supplier, billed customer and remittance beneficiary.

The customer demonstration is a native mobile app, not a browser payment flow. iOS first on Markus's test device, Android follows. A separate polished companion display lets attendees see the actual processing, evidence and selected tools. It is not Swagger or a log console.

### Original client examples

Retain all eight original documents, including images. Evaluate their languages, IBANs, references and biller identifiers separately from the UK cohort. Explicitly accommodate Croatian model and poziv na broj, without assuming every client sample is Croatian.

No Aircash service or credentials are required to run the standalone PoC. Historical ReadCode fields provide context, not hard requirements. A future client integration would map the common extraction output separately.

## 3. Confirmed delivery direction

1. Independent project and monorepo, outside the client repository.
2. Localhost backend first, accepting one JPEG or PNG still image. No page-selection, HEIC or multipage API.
3. Agree mobile designs before writing the apps. iOS first, then Android; do not wait for every optional provider experiment.
4. Hybrid direction: local rules, OCR, document services and selectable LLM/vision models. Payment-barcode/QR decoding is a future improvement outside this PoC, per the 8 October user clarification. The original LLM idea remains a baseline, not a restriction.
5. Freely select models per provider, including smaller models and selected stronger controls; no mandated pairing. Provider-hosted proprietary and open-weight models are allowed; self-hosted inference locally or on project-operated cloud/GPU servers is excluded.
6. Compare mode independently runs selected or all enabled compatible profiles. Extract mode selects one potentially composed pipeline.
7. Ordinary phone photographs suffice for initial backend tests. Explore on-device OCR/ML during mobile work, possibly supplying image-linked text, boxes and quality observations.
8. Keep shared samples and record latency, usage, cost, failures and actual data destinations.
9. Python is selected and Milestone 1 is complete. The next local coding chat starts M2 provider coverage/tooling, with general OCR improvements alongside it. HTML findings reporting is deferred to the end. See CODING_HANDOFF.md and API_CONTRACT.md for scope and wire semantics.

## 4. Delivery resources and budget

Markus and the assistant are building this together. Engineer availability and an internal code-freeze date are not planning blockers.

The total experiment budget is up to €500. Provider-hosted open-weight inference is in scope under the existing API budget. Self-hosted inference infrastructure and weight downloads are out of scope. The full requested upfront credential/resource set was supplied on 6 October. Preserve the existing private `.env` and SDK-managed cloud authentication; request only specific missing/expired access. Do not paste secrets into chat or automatically purchase recurring subscriptions. Record costs including retries, minimum billing, taxes/FX uncertainty and unknown charges.

Client samples are authorised for provider testing. This does not authorise public publication of personal/banking data. The report and future companion must make it clear when an image, text or fields leave the machine. Selected provider account, region, endpoint and payload type are recorded per stage; geographical residency is unknown unless verified.

Defer bespoke upload-limit and artifact-expiry work. Keep basic image decoding safety and actual provider constraints. Existing originals are not cleanup targets.

Third-party SDKs may be used. Check licences and write high-value unit/contract tests rather than rebuilding standard clients. Coverage targets are ≥90% statements/≥85% branches in domain/orchestration; Milestone 1 achieved 98.77%/95.17%, with evidence in IMPLEMENTATION_STATUS.md.

## 5. How the idea evolved

The discussion started with broadening a barcode-driven mobile feature using several LLMs, comparing extraction, time and cost. It expanded into a client-owned hybrid stack that can incorporate OCR, document APIs, deterministic rules and mobile ML.

The commercial proposition is to demonstrate and offer an integrated capability that clients can operate and adapt. It is not a claim to invent invoice photo-payment. Document APIs are commercial building blocks; Docling/PaddleOCR were researched but running their model pipelines ourselves is out of scope; a suitable provider-operated API is eligible for evaluation. Deterministic libraries such as invoice2data may still be evaluated against image-derived managed OCR text without running model inference locally.

The existing business blueprint remains a reference. Detailed engineering plans now describe a separate backend, rather than modifications to the client app.

## 6. Guardrails from earlier decisions

- Do not claim the category is new or no similar solution exists.
- Do not promise savings, scale or accuracy before measuring. Client ownership still has infrastructure, provider, licence and maintenance costs.
- Do not make every scan invoke every provider. A comparison tournament is not the eventual extraction policy.
- Paid/direct-debit wording is not a mandatory rejection condition or the purpose of extraction. Historic due dates do not invalidate test documents.
- Keep language, issuer location, account country and payment scheme separate. Currency is not inferred solely from an address or language.
- Never silently replace a missing/ambiguous bank digit because a candidate passes a checksum.
- User review/confirmation remains mandatory. Benchmark answer keys only provide a way to score raw, unedited outputs; they do not require a separate human review team.
- No business go/no-go exercise, invented fixed delivery duration or browser payment demo.

## 7. What exists and what remains unproved

Existing: the implemented localhost backend and v1 contract, CLI, 184 passing offline tests after the 6 October cleanup, two live starter profiles, private images/raw outputs/results and cost ledger. Twelve provider dispatches include preserved failures; successful vision/OCR runs have measured timings and usage-based USD cost estimates. All upfront credentials/resources are supplied. No mobile app exists, and broader-provider adapters/full-corpus evaluation are next.

The separate 30 September audit passed 15 historical CLI tests; those do not count toward new-backend coverage. Source samples, reference code and archived HTML remain private and preserved.

Still unproved: verified sample answer keys, broader-provider inference compatibility, comparative extraction accuracy, general camera performance, reconciled per-document bills and production readiness. No additional inference occurred during the 6 October account/documentation preparation. The old HTML is historical material, not measured results or current guidance.

## 8. Samples and provenance

The shared folder contains eight original source files, a five-page UK print pack and the added barcode-free Croatian invoice PNG. The UK pack represents five invoices: Continental Landscapes, Active8 Managed Technologies, Pestcotek, Lasercut Works and CAPALC. Verify the logical grouping of the original files; do not count photographs or every source page as independent layouts.

Exact original filenames, hashes and preparation history are recorded in the private corpus manifest.

Use the prepared image fixtures. Keep real data private and preserve source relationships in the private manifest.

A Croatian invoice was supplied on 1 October. Its payment page was prepared as samples/racun-12793-26-no-barcode.png (300 DPI, 2481 × 3508), with the barcode removed and surrounding pixels verified unchanged. A private provenance sidecar records source/output hashes and the transformation. The original source is preserved externally. The Aircash screenshot is still missing and has not been inspected.

## 9. Report, companion and event

Also produce a [separate per-option cost report](COST_REPORT_PLAN.md), beginning with M2 evaluation and delivered with M4 selection. Compare exact options, stage/retry and document-minimum costs, coverage, unknowns and qualified volume estimates; refresh it for M8.

At the end, produce an Azikus-styled HTML findings report with measured approaches, limitations, costs and data destinations. Do not build it during handoff or the initial backend milestone. Private sample data must not be embedded in public material.

ARCHITECTURE.md distinguishes the current service boundaries from planned compositions and later consumers. IMPLEMENTATION_STATUS.md records actual behavior. The later conference companion must reflect real backend events and evidence; any replay must be clearly labelled.

The previously checked official event page lists 13–14 October 2026 in London. This is context, not a fabricated internal deadline. [Event website](https://www.openbankingexpo.com/uk/).

## 10. Remaining choices

- Start a fresh local chat at M2 using the updated handoff; Python and completed Milestone 1 are settled. No further broad research round or blanket credential request is required.
- Verify actual provider accounts, regions and accessible models before calls; budget and sample-testing permission are already settled.
- Reattach the missing client screenshot when convenient; it is not a backend prerequisite. The invoice sample is prepared and verified.
- Decide which sanitised material can be displayed publicly.
- Design mobile screens before coding them; choose on-device experiments then.

Aircash reuse currently means supporting its sample cohort, not a live client API integration. Broader integration/publication would be separately agreed.
