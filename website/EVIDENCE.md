# Content and capture evidence

Prepared 13 October 2026 for the Open Banking Expo London attendee audience.

## Product sources

- Supplied `~/Downloads/App-Screenshots/README.txt` and `manifest.json`: five native iPhone UI screenshots and five SwiftUI Mac renderer captures of Azikus Showcase. The latter are not headset screenshots, passthrough footage or proof of spatial positioning. All supplied invoice, account, balance and receipt values are synthetic.
- Current merged backend source: `269e022` (PR #11), including earlier SUNMI integration. The repository is reconciled at main checkpoint `528ad23`, including PR #13. Read current status/handoff for operating scope; the live backend uses the stable source archive, not an active worktree.
- Latest native capture work: `docs/IOS_DOCUMENT_SCANNING.md` in `codex/ios-auto-document-scan`. Native detection, stability checks, perspective correction and original-photo recovery are implemented and tested offline. Markus confirmed physical automatic-capture acceptance and subsequently confirmed explicit Send works after the backend repair. Those are user confirmations, not a measured camera-quality study.
- The overall iPhone/SUNMI end-to-end integration is user-confirmed complete in the 13 October status. Markus skipped Android capture/review and the final presentation on 13 October. Real payment-service integration remains outside this PoC.
- Original review, confirmation, frozen recovery, source/edit separation and explicit Send behavior are retained. Confirmation is simulated; no funds move.

## Screenshots

- Hero and dark mobile walkthrough: actual native UI-test attachments from the 13 October dark-mode implementation, inspected individually; all financial values are synthetic.
- Light walkthrough and spatial gallery: supplied original application captures, visually unchanged apart from resized/compressed delivery copies.
- SUNMI: existing current companion QA capture showing the real app rendered with an isolated test session. The caption explicitly distinguishes this capture from separate physical live integration acceptance. It is not a fresh live provider run or a latency benchmark.
- Admin context: dark admin capture of an isolated synthetic UK fixture (United Kingdom, English, UK domestic transfer), using the unchanged production context renderer and stylesheet from 269e022. This replaces the Croatian example; no inference or live records were used.
- Admin selection: freshly captured from the authenticated restored local admin on 13 October; cropped to the method/model controls. No private scan list, document, token, raw output or real payment field is included. Current selection was not changed.
- `assets/provenance.json` records source filenames/descriptions, treatment and source hashes. Full local source paths are preserved only in the private cleanup backup. It stays out of the packaged website. No invoice originals or private corpus gallery are included.

## Metrics (authoring background; removed from the page)

The entire evidence/results section was removed at Markus’s request. The repository link is retained in the closing contact area. The following is historical provenance, not current page content.

The former expandable results used the **13 October country-context study**, not the earlier deck's direct-image benchmark. `docs/INVOICE_CONTEXT.md` records 37 distinct image byte sequences, one fresh request per image, zero API errors/timeouts, two success and 35 incomplete drafts. This is request behavior, not accuracy.

The reviewed 17-entry subset contains 16 distinct hashes, one explicit duplicate, 102 readable fields and 63 payment-critical readable fields. Country-aware OpenAI GPT-4.1 mini: 76/102 accepted readable fields (74 exact + 2 accepted name variants); 48/63 accepted payment fields. The same frozen reviewed key excludes unreviewed labels. These are development field counts, not invoice success rates or independent production accuracy. The page does not advertise the 17/17 approved country agreement as a general accuracy score.

Backend timing: reviewed subset median 5.39 s / p95 20.75 s; full 37-image batch median 6.69 s / p95 25.29 s. Capture, upload and rendering are excluded. No promise of instant/real-time inference is made.

The **792 offline backend/evaluation tests** metric is the final merged PR #11 verification checkpoint on 13 October. It is not a fresh website test result or extraction correctness measure. Five extraction approaches are supported by the retained presentation/research and current admin catalogue. Historical costs, customer downloads and Aircash commercial claims are deliberately not repurposed for this public-facing showcase.

## External and brand sources

- [Azikus](https://azikus.com): public positioning and contact address `contact@azikus.com`, retrieved 13 October 2026. Direct browser rendering encountered a certificate/connection error; no warning was bypassed.
- [Open Banking Expo](https://www.openbankingexpo.com): UK & Europe event, London, 13–14 October 2026, verified on the organiser's site. The page does not imply sponsorship or a partnership with the organiser.
- Azikus brand skill: near-black `#0A0A0A`, white, ice blue `#CFE2F6`, muted blue `#9BB0CB` and slate `#3E4855`. Hanken is the disclosed local fallback, not the official Monument font. No new or redrawn Azikus mark is introduced; authentic marks visible in actual application screenshots are preserved.

## Server repair during authoring

The user authorised rerunning the local server if needed. The old process referenced a removed `invoice-context-review` worktree, causing `/admin` and its assets to fail. Confirmed no queued/running jobs; saved read-only table hashes; copied merged source `269e022` into an ignored stable runtime directory; backed up and corrected the private launcher; gracefully restarted the one service owner.

Both `/admin` and `/demo` returned HTTP 200. Jobs, budget, stages, reviews, selected profile and backend identity matched the pre-restart hashes. No extraction, retry, provider selection change or payment confirmation was submitted. Private repair evidence is under `.local/website-2026-10-13/`; no credentials or state are included in this website package.
