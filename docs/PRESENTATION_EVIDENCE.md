# Presentation authoring evidence

Internal reference only. None of this file is a presentation slide, appendix or source-map page. Retained separately following Markus’s 9 October content review.

## Historical reference A. Earlier three-run integration study

### On slide

**Earlier three-run integration study**

7 October 2026 · 31 inputs per run · 93 attempts per method

| Method | Run 1 accepted /31 | Run 2 accepted /31 | Run 3 accepted /31 | Failures /93 | Median | p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OpenAI GPT-4.1 mini | 31 | 30 | 31 | 1 | 4.2 s | 9.0 s |
| Anthropic Haiku 4.5 | 30 | 30 | 31 | 2 | 5.7 s | 10.1 s |
| Gemini 3.5 Flash-Lite | 31 | 31 | 31 | 0 | 3.1 s | 5.0 s |
| Mistral Small | 27 | 30 | 30 | 6 | 3.4 s | 6.2 s |
| xAI Grok 4.7 | 31 | 31 | 30 | 1 | 25.5 s | 50.4 s |
| Together Qwen 3.5 9B | 30 | 30 | 28 | 5 | 8.8 s | 23.9 s |
| Mistral OCR 4.1 | 31 | 31 | 31 | 0 | 3.0 s | 6.5 s |
| Google OCR | 31 | 31 | 31 | 0 | 2.1 s | 2.7 s |
| Azure Read | 31 | 31 | 31 | 0 | 6.0 s | 11.2 s |
| AWS Text | 31 | 31 | 31 | 0 | 2.5 s | 4.4 s |
| Azure Invoice | 31 | 31 | 31 | 0 | 11.1 s | 16.7 s |
| Google Invoice | 31 | 31 | 31 | 0 | 4.1 s | 5.3 s |
| AWS Expense | 31 | 31 | 31 | 0 | 2.9 s | 4.0 s |
| Mindee Invoice | 31 | 31 | 31 | 0 | 5.3 s | 6.6 s |
| Mistral annotations | 30 | 31 | 30 | 2 | 11.3 s | 29.7 s |

**Accepted means structurally processable under the historical strict policy. It does not mean correct or complete payment details.**

All 1,395 attempts retained: 1,378 accepted, 17 failed. Different corpus, configurations and policy from the later reviewed comparison. Timing includes failures and excludes mobile upload/rendering. Split over two appendix slides if necessary for projection legibility.

### Speaker notes — Croatian

Ova tablica odgovara na pitanje koliko smo sustavno ponavljali obradu. Svaka metoda obradila je sva 31 ulaza u tri prolaza. Prihvaćeno ovdje znači da je rezultat prošao tadašnje strukturne provjere, a ne da su podaci za plaćanje bili točni. Ne smijemo uspoređivati ove brojeve izravno s kasnijim ocjenama 102 polja. Čuvamo i sve neuspjele pokušaje.

## Historical reference B. Reading the reviewed results

### On slide

**Reading the reviewed results**

- 102 readable checks per provider, including 63 payment-critical checks.
- Critical fields: recipient, amount, currency, bank destination, payment model and reference.
- 98 confirmed absences assessed separately.
- 146 excluded fields: 92 pending, 2 unreadable, 5 disputed and 47 unsupported/free-text.
- 13 of 17 images have scored fields. Related pages and a duplicate remain.
- Prompt development used this corpus. It is not an independent held-out test.
- Accepted name variants are explicitly human-approved. Bank digits, amounts and references are never fuzzy-matched.
- Gemini's eight matching-but-inferred checks remain separate and uncredited under the frozen grader.
- Backend median and nearest-rank p95 include failed attempts. With n=17, p95 is the largest observation.

### Speaker notes — Croatian

Ovo su detalji metodologije za pitanja. Glavna poruka je da zadržavamo isti ključ i izuzetke za sve pružatelje te ne pretvaramo neprovjerene podatke u točne. Prihvaćene jezične varijante imena posebno su odobrene. Nikakva sličnost znamenki računa, iznosa ili reference ne donosi bodove. Procjena cijelog računa i pokrivenosti svih opcija plaćanja traži dodatnu validaciju.

## Historical reference C. Exact models and dated cost basis

### On slide

**Exact models in the latest direct-image comparison**

| Provider | Requested model |
| --- | --- |
| OpenAI | `gpt-4.1-mini-2025-04-14` |
| Google | `gemini-3.5-flash-lite` |
| Together | `Qwen/Qwen3.5-9B` |
| Mistral | `mistral-small-2603` |
| Anthropic | `claude-haiku-4-5-20251001` |
| xAI | `grok-4.7` |

8 October 2026, reviewed-fields@2, reviewed key r4. One attempt per image in the latest six-provider batch. No hidden retries or provider substitutions.

Cost basis: recorded stage usage and list tariffs checked before the run. xAI uses provider-reported returned charges. Tax, FX, credits and negotiated adjustments are excluded or unknown. Do not interpret internal EUR allowance/ledger totals as billed spend.

## Source map for authoring and notes

| Content | Evidence |
| --- | --- |
| Audience and established visual/language choices | Chat “Prepare Aircash collaboration deck”, including later addition of Vid; supplied Aircash-Azikus reveal.js package |
| Current Aircash product | Four screenshots supplied by Markus on 9 October; Markus's description of supported-code scope |
| 15+ markets and business opportunity | Markus's meeting brief, 9 October. Public Aircash business pages use the broader lower bound 10+; no exact higher public count is asserted from that source. Opportunity remains a proposal. |
| Aircash market/application direction | [Aircash's 2026 development statement](https://aircash.eu/press/a-new-phase-of-development-how-aircash-is-building-its-position-in-the-european-fintech-market), describing market expansion, everyday services and individual-country adaptation |
| Implemented journey, admin and architecture | `PRESENTATION_HANDOFF.md`, `CONFIRMATION_SHEETS.md`, `CONNECTION_SETUP.md`, `CODING_HANDOFF.md` |
| Latest six-provider results and caveats | `M3_DIRECT_PROVIDER_RESULTS.md` |
| Same-profile repeat and hybrid comparison | `PHASE2_CLOSEOUT.md` |
| Direct-provider costs | Private `.local/m3-direct-six-2026-10-08/COSTS.md`; aggregate numeric values only |
| Three-run integration results | `IMPLEMENTATION_STATUS.md`, historical 7 October table; `M2_OPERATIONS.md` |
| Cost interpretation | `COST_REPORT_PLAN.md` |


## Document API usage added on 9 October

The new document-cost table uses `.local/m3-scored-2026-10-08/costs.md` for the 17-page Mistral OCR batch and these saved `reports/cost-comparison/2026-10-06-m2/*/costs.json` reports: `aws-text-rules-seventh-batch`, `aws-expense-seventh-batch`, `google-ocr-rules-batch`, `google-invoice-third-batch`, `azure-read-rules-paced-fifth-batch`, `azure-invoice-paced-fifth-batch`, `mindee-invoice-third-batch`, `mistral-ocr-annotations-third-batch`. Only aggregate usage/cost facts are copied into content. Annotation usage contains 30 reported pages and one missing usage record, with the total monetary charge unknown. Google rates and Mindee credits are historical tariff/account bases, not measured bills.

## Initial authoring directions — superseded by the revision below

Use both authentic logos on the cover. Keep only “Proof of concept” as its status label. The full demo is slide 16, after the proposed direction. Slide 4 is a short journey overview. Fold same-profile repeatability into slide 9. Show all 17 reviewed-comparison inputs on slide 8 using sanitized, flattened previews and preserve the separate 31-input denominator. Audience architecture language uses mobile app, backend, extraction service, data/evidence store, access control, orchestration, provenance, lifecycle and observability. No implementation-stack or hosting labels. Main talk timing: 18 minutes. No appendix or source map appears in the deck.


## Initial deck delivered — 9 October 2026

Local artifact root: `/Users/markusi/.codex/visualizations/2026/10/09/01a11fd7-4c92-74a3-93e6-a4c34c670d58/scanpay-presentation/`.

`outputs/Scan-and-Pay/index.html` is the 16-slide presenter deck with Croatian notes. `Audience.html` embeds all required assets and removes speaker notes. `outputs/Scan-and-Pay.zip` contains the offline package and Mac/Windows launchers. Private build scripts and review renders stay in `build/`, outside the distributable ZIP.

Checked all 16 rendered slides, layout bounds, image loading, local asset references, audience-note removal, and all five architecture animation steps. No application code, inference calls, live selection or ledger changes. The optional video was omitted to fit the meeting preparation window. Hanken Grotesk is the bundled fallback.

Motion updated to match the supplied collaboration deck: default-speed fade; cubic-bezier(.2,.75,.2,1); staggered 22px entrances with 0.75s opacity / 0.9s movement; click-controlled 16px reveals with 0.55s opacity / 0.65s movement; 1.45s headline counters. All 16 slides have entrance sequences; tables reveal in groups. Existing five architecture steps retained. Browser verified presenter click reveals and standalone audience rendering, zero console errors and zero missing images. Both exports and ZIP rebuilt.


## Revised deck delivered — 9 October 2026

The current deck has 24 slides, planned at 18 minutes 35 seconds of speaking and demo time (approximately 19–20 minutes including transitions). It uses the reference deck’s 1600 × 900 canvas, cover signature, title styling, entrance/fragment animation timing and animated brand-sphere closing. The live demo is slide 23, followed by the closing slide. There is no appendix or source map in the audience deck.

Content changes follow Markus’s latest instructions: Scan and Pay in production; Scan and Pay 2.0 as an improvement; factual 15+ markets and almost 2M downloads supplied by Markus; ML Kit’s automatic frame processing in the existing production scanner; a separate introduction to the current PoC; three selectable extraction routes with animated binary flow; PoC Admin screenshots; five approach explanations; all 15 saved configurations across the broader three-run study; the separate six-model reviewed comparison; plain definitions of payment fields, median and p95; separate model and document API cost units; and an explicitly speculative unified ML + direct-LLM loop. PoC status and production work remain explicit.

The evaluation gallery is no longer blurred, as Markus explicitly requested. It shows all 17 prepared evaluation inputs, retaining the masks already in those test inputs. Originals are unchanged. The deck, gallery and build evidence remain local and private; no real documents or screenshots were added to Git. This supersedes the initial flattened/blurred-preview direction.

Markus asked to retain saved results and consider another evaluation only if time remained. The revision uses existing saved results only. No new evaluation, paid API calls, application changes, live selection changes or ledger changes were made. Broader structural acceptance is explicitly distinguished from reviewed payment-field correctness. Historical pricing bases are labelled as saved evaluation rates, not current quotations.

Verified all 24 slides for layout and image loading, then rechecked the corrected production and document-cost layouts. Verified moving binary markers, moving closing spheres, reference aspect ratio, all 24 standalone audience slides, zero audience speaker notes, zero missing images and no browser errors. Rebuilt the presenter deck, standalone audience HTML and offline ZIP. Updated cover preview: `outputs/Scan-and-Pay-cover.png`. The authoritative current generator is `build/rebuild_scanpay_v2.py`; do not use the older generator for this revision.


## Follow-up revision — 9 October 2026

Removed “Beyond the barcode” from the cover. The production overview now names Android ML Kit and native iOS AVFoundation as platform options rather than implying that ML Kit is Android-only or that Aircash’s iOS internals were verified. Primary references: https://developers.google.com/ml-kit/vision/barcode-scanning ; https://developer.apple.com/documentation/avfoundation/avmetadatamachinereadablecodeobject ; https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera .

Added “Current conclusion” immediately before “Future improvements”: direct-image extraction is the best starting point in the tested configurations; OpenAI GPT-4.1 mini is the provisional baseline, with Gemini a close and faster alternative. The one-field difference is explicitly not a decisive model ranking. Recommendation uses the saved Phase 2 evidence and does not change the live admin selection.

Added a fourth future improvement: define required fields for each payment type and treat missing, unreadable or conflicting required values as insufficient information, prompting a retake or manual completion. Notes distinguish preserving useful partial fields from a result with no useful fields, and state that completeness checks do not detect every confidently wrong value. This is a proposal, not implemented application behavior.

The current deck contains 25 slides with planned speaking/demo time of 19 minutes 25 seconds. Both exports, notes, README and offline ZIP were rebuilt. The four changed/new slides were rendered and checked for legibility and bounds. No paid calls or application changes.


## Repository source imported — 12 October 2026

The authoritative editable deck is now `presentation/index.html`, retaining the approved 25-slide revision, Croatian notes, 1600 × 900 canvas and motion. `presentation/deck.css` and `deck.js` hold the theme and interaction. `npm run content` generates the companion document; the earlier external generator is a historical artifact and must not overwrite the repository source.

reveal.js 6.0.2 is pinned with a lockfile. The build creates a presenter deck and self-contained audience HTML without speaker notes. The original external export remains untouched. Existing synthetic/masked/no-payment-value screenshots and supplied logos/font files were inspected and imported byte-for-byte, with hashes and provenance under `presentation/assets/manifest.json` and `presentation/ASSETS.md`.

The original unblurred invoice montage stays in ignored `presentation/private-assets/`. The normal deck uses a numbered 17-input overview in the same slide; an explicit local private build restores the original gallery. Neither generated output directory is versioned. No raw invoice, provider response or credential is added to Git. This supersedes the prior instruction that all deck source must remain outside the repository, while preserving the original private-only treatment of readable documents.

The metrics and conclusions remain the approved saved-study values. This import does not fold in the separately interrupted 9 October repeat, rerun inference, change models, alter the mobile/backend code or begin later milestones. Current operational allowance, selection and device snapshots are in `CURRENT_STATUS.md`.


### Import verification — 12 October

A clean `npm ci --ignore-scripts --offline --no-audit --no-fund` succeeded from the pinned lockfile. Both normal and private builds pass; `npm run check` verifies 25 sections/notes, unique slide IDs, asset hashes, licenses, self-contained audience output and exclusion of the invoice gallery from the normal build. All project JavaScript passes Node syntax checks. The bundled font license text is unchanged apart from trailing-whitespace normalization.

Browser inspection checked all 25 slides for slide overflow and missing images (none), visually reviewed the cover, replacement corpus overview, comparison table and conclusion, and verified audience navigation with no speaker-note elements or external script/style references. No browser warnings/errors were recorded. The Notes control was clicked, but the in-app browser did not expose a separate presenter popup; presenter-window operation should be checked in the presentation browser with popups allowed. The imported plugin and all Croatian notes are retained. Local visual proof is in `.local/presentation-import-2026-10-12/qa/cover.png`.

HTTP checks passed for normal/audience routes, rejection of POST, and 404 responses for `.env`, private asset and traversal paths. Git ignores dependency/build/private-asset folders; staged source has no matches for configured credential values. No application test rerun or paid inference was needed for this isolated deck/docs change.
