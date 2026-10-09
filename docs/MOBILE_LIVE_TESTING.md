# Mobile live testing — 9 October 2026

Markus authorized bounded real API use from the mobile client, local connection setup, opening the Zapad Stan invoice in Preview, and removal of unnecessary operational/simulation labels from the interface. This supersedes the prior zero-additional-call gate and the earlier visible-label requirement. Pay remains a simulated confirmation/reset action in code.

## Current checkpoint

Markus confirmed real-invoice iPhone testing complete on 9 October. The latest ledger is 2,201 dispatched reservations / €336.45 held, leaving at most 16 calls / €1.60 under unchanged caps; current persisted choice is Mistral Small. Subsequent figures below are dated historical snapshots. PR preparation and repository reorganization make no paid calls. Status/docs are updated in both authorized PRs; the presentation is a joint task when Markus returns, followed by mobile improvements, backend work and Android last. See [checkpoint](MOBILE_CHECKPOINT.md).

## Authorized allowance

**Method-choice amendment, 9 October:** Markus requested selecting the next mobile method in the admin. The frozen source configurations were reused byte-for-byte for five direct models (OpenAI, Gemini, Mistral, Anthropic, Together), Mistral OCR/rules and the tested Mistral OCR → OpenAI hybrid. Their exact profile versions match the saved experiments. The prior single-option configuration is backed up as `.local/mobile-live-2026-10-09/providers-before-method-selection.json`; the amended recipient/stage scope is `method-selection-plan.json` beside it. No model/prompt, credential, subscription or cumulative cap was changed. Grok remains disabled pending the recorded reasoning-cost accounting fix; other document integrations remain inactive.

At the amendment the user had dispatched two mobile scans: **2,199 calls / €336.25 held**, leaving at most **18 calls / €1.80**. Direct/OCR-rules selections reserve one call; the hybrid reserves two (€0.20 total); Claude's existing per-call ceiling is €0.15. Thus the remaining number of possible scans depends on the chosen method. Stop at either original cumulative cap. The following single-profile paragraphs describe the initial plan; the amendment supersedes only method scope, not budget or explicit-Send behavior.

The same private ledger starts at **2,197 dispatched reservations / €336.05**. This session permits at most **20 additional calls**, reserving at most **€2.00** (the existing €0.10 ceiling per selected call). The configured cumulative limits are **2,217 calls / €338.05**, below the €500 project cap. These are conservative reserved allowances, not actual billed charges.

Scope: manual captures/imports sent explicitly from this mobile client. This is not a corpus evaluation batch; no completed experiments are rerun. One call per new scan, with no automatic retry/fallback. A retry of an uncertain upload reuses its idempotency key. Once this allowance is exhausted, stop rather than increasing it automatically.

Keep direct-image `gpt-4.1-mini-2025-04-14`, profile `openai-mini-image-roles-v3@2-5094b6dc13ef5718`. Only this option is enabled. The option, prompt, readiness fields and model snapshot were not modified; only `budget_plan` changed, preserving the selected version. Every dispatched call is recorded in the original backend ledger with its recipient and cost reservation.

Private plan, pre-change configuration, original budget rows and access check: `.local/mobile-live-2026-10-09/`. Read-only model retrieval returned HTTP 200 on 9 October; this was not inference. Current [model pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini) remains $0.40 input / $1.60 output per million text tokens. Existing `store=false` handling remains; [data controls](https://developers.openai.com/api/docs/guides/your-data) describe retention and image-input exceptions. Account-specific processing region remains unknown. No subscription or model change was made.

## Connection and token

The existing random `SCANPAY_TOKEN` in the root `.env` authenticates the mobile app and admin inspector. It is distinct from provider API keys. Setup reuses it; it does not rotate any credential. Read it locally from `.env` when signing into the inspector. The app stores it in Keychain.

For an intentionally new token, generate a cryptographically random value locally with `.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))'`. Updating `SCANPAY_TOKEN` requires restarting the backend and updating the phone/admin login; there is no reason to rotate it for this test. Never replace the whole `.env` with an example or overwrite unrelated keys.

Debug builds accept a one-time `connection-setup.json` copied via Xcode into their existing `tmp` directory. This file contains candidate Mac addresses and the local access token, is never bundled or committed, and is deleted on consumption. Read-only profile checks choose a working route, with a Wi-Fi fallback. A token-free `Application Support/connection-check.json` records addresses/status for device verification. Use the existing `tmp` directory for transfer: Xcode may create missing destination folders owned by root, preventing the app from removing files or saving future drafts. Release builds omit this setup mechanism. No image or provider request is made during setup.

The test server binds only loopback and the current Mac interface addresses, retaining the same data directory and process lock. The local launcher is `.local/mobile-live-2026-10-09/serve.py`; it now discovers the current addresses of the existing Wi-Fi (`en0`) and iPhone USB (`en24`) interfaces at startup. If an address changes while running, restart the idle backend and update the phone's connection settings. The inspector remains at `http://127.0.0.1:8000/admin`. A cable used for Xcode installation does not itself establish that ordinary app HTTP traffic uses USB; use the phone's connection-check result as evidence.

On reconnecting USB later on 9 October, `en24` changed from `169.254.32.26` to `169.254.102.169`, while the phone retained the old address. Wi-Fi remained `192.168.1.134`. A one-time Wi-Fi-only setup was copied to the installed app to remove USB reconnects from the phone's HTTP route. After Markus unlocked and opened the app, its fresh connection-check report confirmed an authenticated connection to `http://192.168.1.134:8000` at 02:48:17 CEST. The app now retains that Wi-Fi address, so unplugging/reconnecting USB does not change this route. Existing records, app credentials and the extraction selection were retained. The idle backend was restarted with the current interface addresses and the new artifact endpoints.

## Invoice and UI

### Reconnect follow-up

Markus requested a Reconnect button and USB-first preference. The signed update is installed and launched with the current USB (`169.254.102.169`) and Wi-Fi (`192.168.1.134`) URLs saved. At 03:03:58 CEST, the physical phone's reconnect report recorded **USB failed → Wi-Fi connected**, selecting `http://192.168.1.134:8000`. This verifies the ordered attempt and fallback on the device; it does not claim USB was reachable in this check. Both URLs reached the same authenticated backend from the Mac. The phone's route remains Wi-Fi until a later USB check succeeds. Token-free evidence: `.local/mobile-live-2026-10-09/reconnect-device-check.json`.

The button is on capture, in Connection settings and in the scan menu. Saved addresses persist; USB address changes are not automatically discovered. New pending scans pin the backend's persistent identity, with legacy scan ID/image-hash checks before changing accepted drafts. Reconnect itself sends only GET requests. The updated backend retained the original ledger (2,199 / €336.25), scans and selected extraction method; no paid API calls were made.

The supplied Zapad Stan image is `samples/racun-12793-26-no-barcode.png`, opened in Preview for Markus to photograph. It stays private. The updated app removes the repeated “Simulation only,” “No payment sent,” manual-capture label and Send explanatory line; the inspector removes its private-records/payment footer and related boilerplate. Meaningful field warnings and explicit synthetic-fixture identification remain.

Live accuracy, capture quality and end-to-end latency belong to the new device/photo records. Prior saved-response evaluation scores are not scores for these new photographs.

## Verified outcome

At 00:49:52 CEST, the physical iPhone successfully authenticated to the selected profile through **http://169.254.32.26:8000**. The Mac hardware registry maps `en24` to **iPhone → NCM Data → AppleUSBNCMData**, confirming the USB network interface. The phone saved this address and the existing token in Keychain; its one-time setup file was consumed and removed. The Wi-Fi listener is also available at `http://192.168.1.134:8000`, but the successful phone probe used USB. If the cable/interface disappears, choose the Wi-Fi address in Connection settings.

The first setup transfer created an Application Support folder owned by root. No captured/pending scans existed; test-app Documents was empty. Available app files were backed up (OS snapshot files are not exportable), the test installation was replaced, and the final setup uses the existing temporary folder instead. Temporary repair/console diagnostics and the one-off device inspection test were removed from source.

The inspector is signed in at `/admin`. The Zapad Stan image is open in Preview. Signed device build, nine native unit/recovery tests and both simulator UI tests pass; a separate physical-device UI check confirmed the normal app and configured address. Thirty focused backend API/review tests, Ruff, mypy, JavaScript syntax and diff checks pass. The setup/probes made no inference calls: the final ledger check remains **2,197 dispatched / €336.05 held**, leaving the new 20-call / €2.00 allowance available.

## First phone scan and UI follow-up

Markus made one live mobile scan after setup: the ledger is now **2,198 dispatched / €336.15 held**, leaving **19 calls / €1.90** in the existing plan. Its pending mobile upload key and image hash verified the source assignment. This UI/debugging iteration made no inference calls and did not change the plan. The returned destination was unresolved; the previous client completeness gate explained the disabled Pay button. The new PoC confirmation retains the warning and permits reviewed useful drafts without changing their extraction status.

Purpose code is the optional HUB “šifra namjene” classification (see [HUB 3 instructions](https://www.hub.hr/sites/default/files/inline-files/1306-hub3-uputa.pdf)); it was null in this scan. Document language and issuer country were model-returned `hr` / `HR`, both marked inferred/derived with model-claim evidence. The selected direct-image profile uses no separate language classifier, geocoder or phone-location lookup; input hints were null. These observations do not determine currency or bank ownership. No independent reason trace establishes exactly which visual cues produced those country/language guesses.
