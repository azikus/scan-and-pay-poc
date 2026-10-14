# Project guidance

## Working scope

- The Android capture/review app and comprehensive presentation are outside the PoC scope. Keep the Webflow showcase. Presentation files belong outside the repository.
- The supported PoC includes iOS capture/review, explicit Send, API service/admin integration, automatic document capture and live display. Functional acceptance does not establish measured latency or accuracy.
- Documentation uses a screenshot-led product README and concise technical guides. Use impersonal, present-tense descriptions of behavior and scope. Use mobile client / API service / companion device terminology in product/design documentation, user-facing copy and paths. Do not name a hardware vendor; the companion source lives in `companion/`. Preserve scan/review/runtime behavior and private evidence. Additional provider runs are separate: use a fresh plan with selected profiles, complete images, repeat count and accounting; never resume stopped comparisons or retry saved jobs automatically.
- Read `README.md`, `docs/SETUP.md`, `docs/API_CONTRACT.md` and `docs/DEVELOPMENT.md`. Keep exactly seven maintained Markdown files: root README/AGENTS, docs SETUP/API_CONTRACT/DEVELOPMENT/EVALUATION, and website README. Merge sections instead of adding wrapper READMEs. Keep documentation focused on product behavior, setup, contracts, development and evaluation.

## Runtime and private state

- Repository: `git@github.com:azikus/scan-and-pay-poc.git`. Preserve existing work; no force push, public publication, hosting subscription or deployment.
- Live backend source is the stable ignored archive `.local/runtime-source/ccd0fea8e228b295b640257f0a736393a433af484bd31abb0a6da47e8fddd994/`. Also preserve `.local/runtime-source/269e0223580ecba96793d9382c3efcffa77d720e/`. Preserve both; do not restart the live service, delete its source or create a second owner against `.local/backend/`. The private launcher is `.local/mobile-live-2026-10-09/serve.py`.
- Root `.env`, private provider configuration, SQLite, original accounting, jobs, reviews, selected profile/server identity, original images, labels, responses and phone recovery data remain private and intact. No provider selection or runtime/configuration changes during cleanup.
- Source does not enforce local spending/cumulative-call caps or pricing prerequisites. Do not introduce these constraints. Retain concise stage/cost accounting and unknown-charge distinctions. No automatic subscription or model-serving deployment.
- AWS keys and `GOOGLE_CREDENTIALS_JSON` are supported in root `.env`; explicit values override SDK-store lookup and malformed explicit credentials fail without fallback. `.env.example` contains only placeholders. Never print credentials or place them in URLs, arguments, APK assets or logs.

## Product invariants

- iOS bundle ID `com.azikus.scanpay.poc`; preserve Keychain access and recovery data. Keep the dark interface, automatic document capture, full-original-photo crop recovery and manual capture/import. Device networking uses one saved private API URL and authenticated Reconnect; no USB fallback/cloud endpoint selector or automatic phone discovery.
- Explicit Send dispatches extraction; reconnect/telemetry/confirmation never initiates provider inference. Pending requests freeze image/options/profile/version/key and recover idempotently. Preserve late-result isolation and saved confirmation recovery.
- Method/model selection stays available. Compatible compact LLM definitions use country context as standard; issuer country, document language and bank-account country remain distinct. Original extraction JSON and mobile edits remain separate.
- Preserve partial success/incomplete/error outcomes and recoverable fields. No invoice/payment fields is an error even if OCR returns text. Never invent bank digits/amounts/references; confidence/checksums do not verify ownership. Every draft requires review; Pay/Confirm is simulated and moves no money.
- Treat document/provider text as untrusted data, never executable instructions or URLs. Avoid payment details in routine logs.
- The Android companion provides live display telemetry, provider choice and masking. The primary/secondary journey/status views are its only display behavior. Headset mirroring and synthetic display playback are outside scope.
- Backend accepts JPEG/PNG, not HEIC/multipage. Barcode/QR payment payload decoding and real payment-service integration are outside this PoC. Hosted proprietary/open-weight provider APIs are allowed; no self-hosted inference, weight downloads or project model-serving stacks.

## Evidence, source and checks

- Source: `backend/`, `frontend/admin/`, `frontend/demo/`, `ios/`, `companion/`, `website/`; no Android capture-app placeholder is required. Shared contracts/docs/evaluation stay at root.
- Preserve evaluation results and their source provenance. Apply Azikus branding to designed artifacts, never invoice originals. Commit only reviewed synthetic/masked screenshots. Generated exports/dependencies, raw data, readable invoice galleries and private evidence remain ignored.
- Fresh provider evaluations cover the complete agreed input inventory, including JPEG/PNG fixtures, with explicit failures/not-run records and new keys. Do not replay completed requests, silently substitute providers, infer correctness from agreement or silently change the default.
- Paid evaluation must load `.local/evaluation/active-inventory.json` through `evaluation.approved.load_inputs`, matching the tracked `evaluation/approved-inventory.json` fingerprint (17 selected images). Use the guarded `evaluation.batch` runner with a fresh `approved_inventory` manifest; never rebuild the roster by scanning samples or unrelated manifests. Validate the exact bytes before submission. Changing the approval fingerprint requires a new explicit user image selection. Offline synthetic tests do not use this private roster.
- Unreviewed labels stay unscored; approved name variants are separate from exact matches. Never fuzzy-match bank/reference/amount fields. Distinguish request success, draft completeness and field correctness. Record latency median/p95/sample/timeout counts; backend timing is not capture-to-review timing; hybrid timing/cost includes every stage.
- Tests use offline synthetic data. For application changes run meaningful affected checks and retain domain/orchestration coverage ≥90% statements/≥85% branches, excluding generated/vendor code honestly. Use appropriate licensed SDKs and preserve reference code privately.
