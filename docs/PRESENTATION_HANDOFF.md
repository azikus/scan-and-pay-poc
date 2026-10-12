# Presentation handoff — Scan and Pay PoC

**Current handoff — 12 October 2026:** the initial deck was created and revised with Markus on 9 October and now lives in [presentation/](../presentation/README.md). Continue that approved 25-slide deck; do not restart audience/template discovery unless the brief changes. English slides, Croatian notes and a 19–20 minute talk including the live demo are established. [PRESENTATION_CONTENT.md](PRESENTATION_CONTENT.md) is generated from its HTML source; [PRESENTATION_EVIDENCE.md](PRESENTATION_EVIDENCE.md) records revisions and sources. Read [CURRENT_STATUS.md](CURRENT_STATUS.md) for current budget/selection/device facts. The remainder is the original 9 October source pack, with dated scope and operating snapshots retained as history.


Prepared for Markus to start a new presentation chat, 9 October 2026. This is a source pack and working brief, not a presentation or permission to implement later features. Read [coding handoff](CODING_HANDOFF.md), [roadmap](ROADMAP.md), [confirmation-sheet checkpoint](CONFIRMATION_SHEETS.md) and [connection setup](CONNECTION_SETUP.md) for current authority. Use [the copyable prompt](PRESENTATION_PROMPT.md) in the next chat.

## 1. What the next chat should accomplish

Build the **initial presentation together with Markus**, using the implemented PoC and existing results. Begin by agreeing audience, desired outcome, duration, language, output format and the role of a live demo. These are still open; do not invent a client, slide count or delivery date. Offer a concrete outline for discussion, then develop the deck collaboratively.

Keep the presentation factual and visual: show what works, explain the approaches tested, compare correctness and latency with their denominators, demonstrate review and correction, and identify the remaining development. Cost is secondary to correctness and speed. A comprehensive final presentation and an embeddable website HTML are separate deliverables after development, not this initial deck.

The extracted-field confirmation sheets and the subsequently approved admin Connection/automatic backend network update are the two pre-presentation implementation exceptions. The next prompt/chat is the initial presentation; no other iOS, backend/admin or Android implementation is in scope now. The user requested this handoff so a fresh chat can continue without reconstructing the earlier conversations. Do not create or message another chat automatically.

## 2. Agreed milestones

1. **Initial presentation together**, grounded in the current product and retained results.
2. **iOS improvements and real-invoice testing**; use multiple sessions if needed.
3. **Backend/admin improvements and integration testing**; use multiple sessions if needed.
4. **Android app and testing across both platforms** — the final development milestone.
5. **Comprehensive final presentation plus embeddable website HTML**, explaining functionality and measured findings.

[ROADMAP.md](ROADMAP.md) owns this agreed order and completion checkpoints. The older M1–M8 labels remain historical evidence identifiers. The sequence does not make Android optional or move another development milestone after it. Detailed improvement scopes and the website's embedding constraints are to be agreed when those milestones begin.

## 3. Product story and implemented journey

The PoC turns a photograph of an invoice into a structured, editable payment draft. It aims to reduce manual retyping while preserving human review of payment-critical fields. It does **not** execute payments, verify ownership of an account or establish that an extracted amount/reference is correct.

The implemented iPhone journey is:

1. Capture a photo or import an image.
2. Manually crop/rotate, then inspect the final image.
3. Press **Send** explicitly; no image upload or inference happens before that action.
4. The app reads the admin-selected exact profile, sends the image to the Mac and polls the accepted scan. Shimmer placeholders show processing; they are not incremental extraction results.
5. Review the expandable sheet against the image. It groups **Payment details** and **Invoice details**. Only observed document values populate a new draft; empty values and untouched inference are omitted. A normalized printed value can still be extracted; a guessed recipient copied from a supplier is not treated as an extracted payment recipient.
6. Edit or add fields as needed. Changes are marked **Edited** and remain separate from the immutable original response. Linked amount/destination/reference fields stay within the selected payment option.
7. Check **I've checked these details**, then press **Pay**. The confirmation sheet keeps amount and recipient prominent and displays every other non-null selected payment/invoice field. Missing/invalid payment details remain visible as warnings.
8. **Keep editing** returns to review. **Confirm** saves a separate simulated review snapshot, then shows **Complete** and resets capture. Confirming a useful incomplete draft is permitted for this PoC; an empty/error draft or an unselected option cannot be confirmed.

The display includes account holder, bank details, reference, payment model, purpose code, supplier, invoice/customer numbers, due date, description and explicit document context where actually extracted. Null fields can be entered via **Add missing details**. This is a field-based review, not a display of raw OCR text, every provider diagnostic or all competing candidates at once.

**Extracted is not verified:** the UI trusts the observation's provenance/state, including suppression of known recipient-role fallbacks. A model can confidently misread or mislabel an observation. The sheet change does not re-evaluate saved benchmark results, fix all extraction errors or guarantee that every inference is correctly tagged by a provider. Original JSON remains inspectable.

## 4. What the admin demonstrates

The local authenticated inspector is at `http://127.0.0.1:8000/admin` on the Mac. It provides:

- A collapsible **Connection** section with current Mac addresses, availability/status and **Copy address**. The managed backend keeps loopback available and updates private network listeners automatically; the phone still uses explicit saved URLs and **Reconnect**.
- A compact scan list with **Mobile / Automated** filtering.
- An always-visible **Next scan** form: **Method → Model / provider → Use for next scan**. Selection is persisted and applies on the phone's next explicit Send; pending scans keep their original exact profile/version and recovery key.
- Original normalized extraction JSON, including nulls, evidence, candidate links and warnings.
- Saved provider responses grouped by run/stage; a hybrid can expose OCR text/layout and the input passed to its interpretation stage.
- The exact uploaded mobile image and separate mobile-confirmed values for comparison with the original.

The method catalogue and benchmark/speed display were deliberately removed from the visible admin because they were confusing. The catalogue API and historical evidence remain. Put the comparisons in the presentation; do not describe them as current visible admin panels. Admin browsing, inspecting saved outputs, reconnecting and changing selection do not themselves dispatch inference. The admin is an internal local tool, not an attendee website or a production customer portal.

## 5. Architecture and data flow

| Component | Current implementation | Responsibility |
| --- | --- | --- |
| Mobile | `ios/`, native SwiftUI, iOS 18+, AVFoundation and PhotosPicker | Capture/import/crop, explicit Send, review/edit, connection and recovery; local token in Keychain |
| Backend | `backend/`, Python/FastAPI/Pydantic; one process with bounded workers | Authenticated v1 API, versioned profiles, provider calls, normalization, review policy, jobs and confirmations |
| Storage | Private SQLite and files in `.local/backend/` | Original image/response/evidence, immutable profile snapshots, idempotency, accounting and separate mobile reviews |
| Admin | `frontend/admin/`, served by the same FastAPI process | Method selection and inspection of saved mobile/automated work |
| Android | `android/README.md` only | Future implementation, final development milestone |
| Shared evidence | `contracts/`, `docs/`, `evaluation/`; real artifacts ignored/private | Wire schemas, decisions, synthetic examples and reproducible evaluation tools |

For an architecture slide: **iPhone → Mac API → selected provider(s) → Mac interpretation/review → iPhone editable draft**. The admin reads the same backend records and chooses a future scan's method. A hybrid has two external stages/recipients; local deterministic rules are distinct from cloud inference. There are no provider credentials on the phone, no self-hosted model weights and no payment-service integration.

`POST /v1/scans` accepts one JPEG/PNG plus explicit options and an idempotency key. `GET /v1/scans/{scan_id}` polls persisted work. Confirmation uses `PUT /v1/scans/{scan_id}/reviews/{review_id}` and preserves the original extraction. The native app sends an oriented PNG after cropping. Multipage backend uploads, HEIC backend input and a customer browser capture flow are not implemented. See [API contract](API_CONTRACT.md) and [architecture](ARCHITECTURE.md) for exact semantics.

## 6. Extraction approaches and current choice

Five historical method families were explored: direct image-to-fields with a hosted model; managed OCR plus deterministic rules; managed structured document/invoice extraction; OCR with schema annotations; and OCR followed by an LLM interpreting the text/layout. Ten provider families and fifteen historical methods have full attempt records. This is integration breadth, not proof that all methods extracted useful payment details or were equally accurate.

Seven exact tested profiles are enabled for the current mobile setup, across three usable approaches:

| Approach | Currently available choices |
| --- | --- |
| Direct image | OpenAI GPT-4.1 mini; Gemini 3.5 Flash-Lite; Mistral Small; Anthropic Haiku 4.5; Together-hosted Qwen 3.5 9B |
| OCR + rules | Mistral OCR |
| OCR → LLM | Mistral OCR → OpenAI |

**Current persisted demo choice:** Mistral Small, `mistral-small-image-roles-v3@2-b292ba761e512607`. The connection-update snapshot is 2,204 / €336.75, superseding the earlier Gemini/2,202 snapshot. Original ledger rows remain intact. The agent made no inference call. Preserve the actual latest selection unless Markus deliberately changes it. **Historical Phase 2 choice:** OpenAI GPT-4.1 mini, `openai-mini-image-roles-v3@2-5094b6dc13ef5718`, selected for the measured correctness/speed tradeoff on 8 October. These are different facts; do not present the historical selection as the current admin state or infer that the current choice has the best accuracy.

Grok is disabled pending its documented runtime reasoning-cost accounting fix. Other managed document integrations remain catalogued but inactive in this mobile configuration. Do not enable them, change model/prompt versions or start new experiments to prepare a slide. [Mobile live testing](MOBILE_LIVE_TESTING.md) records the scope amendment; [Phase 2 closeout](PHASE2_CLOSEOUT.md) explains the historical choice.

## 7. Evidence ready for the initial presentation

### Latest six-provider direct-image comparison — 8 October

One repeat: six providers × all 17 masked images = **102 dispatched calls**. Same reviewed key r4 and fixed prompt semantics; no completed request retries or silent provider substitutions. The following table is reproduced from [M3_DIRECT_PROVIDER_RESULTS.md](M3_DIRECT_PROVIDER_RESULTS.md).

| Provider / exact requested model | Accepted readable /102 | Accepted critical /63 | Backend median / p95 | Timeouts /17 |
| --- | ---: | ---: | --- | ---: |
| OpenAI `gpt-4.1-mini-2025-04-14` | 79 | 51 | 4.02 / 9.43 s | 0 |
| Gemini `gemini-3.5-flash-lite` | 80 | 50 | 3.31 / 5.00 s | 0 |
| Together `Qwen/Qwen3.5-9B` | 69 | 47 | 9.41 / 22.67 s | 0 |
| Mistral `mistral-small-2603` | 71 | 43 | 2.99 / 5.78 s | 0 |
| Anthropic `claude-haiku-4-5-20251001` | 65 | 42 | 5.64 / 11.14 s | 0 |
| xAI `grok-4.7` | 16 | 10 | 90.06 / 90.13 s | 14 |

Every provider has 17 timing observations, including failures. Grok had 15 error outcomes, including 14 timeouts and a documented capacity rejection; missing output must not be described as wrong OCR. Timing is backend elapsed processing, not camera-to-review or an SLA.

**Required context beside any accuracy chart:** this is a partially reviewed development corpus, not held-out or whole-invoice accuracy. There are 102 readable checks and 98 confirmed absences per provider; 146 fields were excluded, including 92 pending. Only 13 of the 17 images contain scored fields; the set includes related pages and a duplicate. Prompt development used this corpus. Accepted readable values include separately recorded human-approved name variants, never fuzzy matching of bank digits/amounts/references. Ready-for-review counts are not counts of correct invoices. Gemini's eight matching-but-inferred checks remain separately visible and uncredited under the frozen grader.

OpenAI's preceding run of the same version also had 79/102 accepted readable fields, but 52/63 critical rather than 51/63 and different individual outputs. Do not imply perfect repeatability or statistical superiority from one-field differences.

### Hybrid evidence — different, earlier batches

[Phase 2 closeout](PHASE2_CLOSEOUT.md) rescored these using the same reviewed r4 key:

| Configuration | Accepted readable /102 | Critical /63 | Backend median / p95 |
| --- | ---: | ---: | --- |
| Mistral OCR → OpenAI, draft 1 | 71 | 44 | 6.58 / 11.14 s |
| Mistral OCR → OpenAI, roles 3 | 64 | 37 | 6.02 / 8.47 s |

Both fresh stages are included. These are earlier batches, not extra rows from the latest six-provider repeat. The tested hybrid did not outperform the chosen direct-image configuration on reviewed critical fields and latency. That does not prove every hybrid is inferior. Earlier exact-only scores differ from later accepted-name-variant scoring; never combine them without noting the key/version.

### Historical integration coverage and cost

M2 recorded **1,395 attempts**: 15 methods × 31 prepared inputs × three runs. Under the then-current strict structural checks, 1,378 were accepted and 17 failed. “Accepted” means structurally processable, not accurate. A later offline partial-field replay reported 11 success, 953 incomplete and 431 error outcomes; it made no new provider calls. OCR text without extracted payment/invoice fields can yield an error outcome. These are a separate corpus, policy and question from the 17-image reviewed comparison. See [implementation status](IMPLEMENTATION_STATUS.md), [M2 integrations](M2_INTEGRATIONS.md) and [M2 operations](M2_OPERATIONS.md).

The latest six-provider batch's known usage estimates/reported charges total **$0.28243888**, with 15 Grok failed-attempt charges unknown. Its OpenAI 17-image estimate is **$0.0387228**, approximately **$0.00228/image**. These dated estimates exclude tax, FX and account adjustments and are not settled invoices or current pricing. Use [cost report guidance](COST_REPORT_PLAN.md) and the private source below; keep cost compact and secondary. No current price lookup or paid rerun is required to describe dated measurements.

## 8. Verification, acceptance and remaining limits

The latest connection update passes **690 offline backend/evaluation tests**, including listener replacement, discovery/bind failure handling, authenticated address reads and startup/shutdown checks. See [connection setup](CONNECTION_SETUP.md) for final coverage, real TCP listener-change checks, browser checks and packaging. No native code changed in that update. The preceding sheets passed **23 native unit/recovery and 2 UI tests**.

The baseline backend/refactor verification passed 672 offline tests, 95.92% statement / 91.15% branch domain/orchestration coverage, lint/format/strict typing, unchanged contract generation, JS syntax, installed-wheel serving and source-distribution rebuild. The preceding native baseline passed 16 unit/recovery and 2 UI tests. [CONFIRMATION_SHEETS.md](CONFIRMATION_SHEETS.md) records the new sheet-specific verification separately; use its final result rather than assuming the older native count still applies.

Markus confirmed real-invoice iPhone testing is complete for the accepted PoC checkpoint. That establishes user acceptance, not an independently scored camera dataset. No measured mobile capture-to-review study is available. The physical iPhone authenticated over the **same-iPhone hotspot at 09:13:12 CEST** on 9 October: old USB failed, hotspot Wi-Fi connected at `http://172.20.10.2:8000`. An earlier successful USB check is historical. The confirmation-sheet build is signed and installed, preserving phone preferences and Application Support. Mac-side authenticated reads also pass with the automatic network launcher. Automated listener-change checks simulate discovery changes on a real interface; they do not establish every physical network transition.

Known limitations for an honest initial presentation:

- Confidently wrong amounts, recipient-role mistakes, reference/invoice-number confusion, missing bank fields and variation between runs remain possible. Format/checksum validation does not establish correctness or account ownership.
- Images are manually cropped; paper detection, perspective correction, live outlines and native OCR are possible later iOS work, not delivered capabilities.
- The Mac backend automatically follows active private/link-local IPv4 addresses on physical interfaces. The phone uses explicit saved Mac URLs; automatic phone discovery is not implemented. When an IP changes, copy its new URL from admin Connection into the iOS Connection settings and reconnect. Same-iPhone hotspot authentication is verified; broader physical network-transition coverage remains future work.
- Android is not implemented. The backend is a trusted local PoC deployment, with no production readiness or availability claim.
- Every draft requires review; Pay is simulated, even when confirmation completes successfully.
- Payment QR/barcode decoding and payload interpretation are outside this PoC. Printed identifiers remain in scope. Mention decoding only as a future possibility, not unfinished acceptance work.

## 9. Demo preparation without new inference

Use the existing checkout and read actual Git/runtime state; transient addresses, PIDs and signing readiness must be checked again before a live session. Do not reset private state or start a second backend.

1. Read `ios/README.md`, `MOBILE_LIVE_TESTING.md`, `CONNECTION_SETUP.md` and the sheet checkpoint. Open `ios/ScanAndPay.xcodeproj`, scheme `ScanAndPay`, if a build is needed. Keep bundle ID `com.azikus.scanpay.poc`, signing supplied locally and existing on-device data.
2. Check the existing one-process Mac backend and `/health`, then authenticated profiles and admin reads. Private launcher/log/PID are `.local/mobile-live-2026-10-09/serve.py`, `server.log`, `server.pid`; database is `.local/backend/jobs.sqlite3`. The private launcher delegates to `.venv/bin/scanpay-serve` / `backend.local_server`, which follows local addresses without restarting jobs. If stopped, start one managed process from the repository root. Read-only health/profile/admin checks make no provider call. Never print credentials.
3. Open `http://127.0.0.1:8000/admin` on the Mac and connect using the existing `SCANPAY_TOKEN` from root `.env` locally. The admin token is held in page memory. Preserve the persisted selection unless Markus requests a change. Expand **Connection** and copy the current Wi-Fi/hotspot base URL.
4. Unlock/open the phone, update **Connection → Wi-Fi address** if needed and use **Reconnect**, which probes saved USB then Wi-Fi with authenticated reads. Inspect its actual result. A phone's localhost is not the Mac. Do not send a real invoice just to test connectivity.
5. For screenshots or a no-cost walkthrough, run `-synthetic-preview` in a simulator. It is explicitly labelled and uses bundled synthetic data without network calls. Remove the launch argument for normal operation. Its artificial delay is not extraction performance.
6. Saved scan/provider outputs can support an evidence walkthrough without new calls. Label saved/replayed material clearly. Synthetic examples or separately approved sanitized images are appropriate for shareable slides.
7. A live extraction requires Markus's explicit Send under the existing bounded mobile plan. Preparation does not authorize agents to dispatch inference. If connectivity fails, show the labelled synthetic flow or retained results and explain the limitation.

The ledger at this documentation checkpoint is **2,204 dispatched reservations / €336.75 held**, within unchanged mobile caps **2,217 / €338.05** and the original €500 project limit. Holds are internal conservative allowances, not provider charges. The remaining allowance is at most 13 calls / €1.30; hybrids reserve two calls and Anthropic has a €0.15 call ceiling, so that is not a promise of 13 scans. Do not increase caps, rerun completed evaluations, change selected versions or buy subscriptions for presentation work.

## 10. Proposed story to agree, not a finished deck

A useful starting narrative is: the manual-entry problem → the implemented capture-to-review journey → architecture and method choices → a short labelled demo → reviewed correctness/latency results → what the failures taught us → current limitations and the agreed next milestones. Use screenshots to show the actual product and a simple data-flow diagram for architecture. Include the important denominators/caveats beside charts rather than hiding them in an appendix. Keep detailed model/stage/cost evidence available as supporting material.

Ask Markus which audience and decision the first deck serves, how long it should be, language and format, and whether live demonstration or screenshots should carry the story. Agree which sanitized examples may leave the private workspace. The final website HTML's target CMS, iframe/inline embedding, responsiveness and hosting constraints belong to milestone 5, not implementation now.

Use the available **presentations:Presentations** and **azikus-brand** skills when creating the deck in that chat. Retain original Azikus logo/mark assets; the app uses licensed Hanken Grotesk as the fallback for ABC Monument Grotesk. Never apply branding transformations to invoice originals. Do not publish materials merely because the repository is private or a presentation was requested.

## 11. Source map and private evidence

| Question | Start here |
| --- | --- |
| Current scope and agreed next order | `CODING_HANDOFF.md`, `ROADMAP.md`, `CONFIRMATION_SHEETS.md`, `CONNECTION_SETUP.md` |
| Implemented product and acceptance | `MOBILE_CHECKPOINT.md`, `MOBILE_IMPLEMENTATION.md`, `../ios/README.md` |
| Current enabled methods/network/budget | `MOBILE_LIVE_TESTING.md`, `CONNECTION_SETUP.md`; authenticated `/v1/profiles` for live readiness |
| API semantics, outcomes and provenance | `API_CONTRACT.md`, `ARCHITECTURE.md`, `DECISIONS.md` |
| Latest reviewed provider comparison | `M3_DIRECT_PROVIDER_RESULTS.md`, `PHASE2_CLOSEOUT.md` |
| Recipient-role iterations and scoring changes | `M3_RECIPIENT_ROLES.md`, `M3_REVIEWED_RESULTS.md`, `M3_DRAFT_POLICY.md` |
| Integration breadth and earlier runs | `IMPLEMENTATION_STATUS.md`, `M2_INTEGRATIONS.md`, `M2_OPERATIONS.md` |
| Dated cost evidence | `COST_REPORT_PLAN.md` |
| Repository move and baseline verification | `REPOSITORY_REORGANIZATION_HANDOFF.md` |
| Safe synthetic schema/examples | `examples/README.md`, `examples/uk-extract.synthetic.json`, `examples/hr-extract.synthetic.json` |

These private local sources may contain real financial or personal data. Read only what is needed, do not paste raw rows into chat/slides or commit their contents:

- `.local/m3-direct-six-2026-10-08/REPORT.md`, `provider-ranking.csv`, `field-results.csv`, `image-outcomes.csv`, `openai-repeat-changes.csv`, `COSTS.md`, `cost-audit.json`: latest six-provider comparison, individual outcomes and costs.
- `.local/m3-name-review-2026-10-08/reviewed-key-r4.json`: frozen reviewed-fields@2 key and approved variants.
- `.local/m3-recipient-roles-2026-10-08/revision-{2,3}/report.json` and `.local/m3-scored-2026-10-08/`: historical hybrid/direct results and rescoring.
- `.local/evaluation/m3-no2d-2026-10-08/manifest.json`: 17-input masked-image identity/provenance. Original invoices and pre-mask evidence are preserved separately.
- `.local/mobile-live-2026-10-09/`: bounded mobile plan, method-selection amendment, read-only connection checks, device/test evidence and live server files.
- `.local/main-rebuild-2026-10-09/completion.json`: merged-main rebuild/install and Mac read checks; phone launch limitation.
- `.local/confirmation-sheets-2026-10-09/`: sheet regression logs, result bundle and synthetic screenshots.
- `.local/hotspot-check-2026-10-09/phone-hotspot-check.json`: actual phone authentication over its hotspot.
- `.local/local-network-setup-2026-10-09/`: automatic listener tests, live read checks, preservation snapshot, browser verification and package logs.
- `reports/overview-2026-10-07/index.html` and `reports/repeatability-2026-10-07/index.html`: earlier private progress explainers, not the final website deliverable; reconcile their dated claims with this handoff before reuse.

Root `.env`, `.local/providers.json`, SQLite, source invoices, labels, raw responses, SDK credentials and all original ledger rows must remain private and intact. Public/reusable examples need sanitized data. Historical docs retain old no-mobile gates, defaults and budget snapshots; follow current scope and date each claim instead of overwriting historical evidence.
