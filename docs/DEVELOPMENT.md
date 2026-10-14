# Development

Read the [product guide](../README.md), [setup](SETUP.md) and [API contract](API_CONTRACT.md). This guide owns architecture, provider profiles and development checks. `AGENTS.md` contains workspace preservation and task-specific guidance.

## Repository map

| Path | Contents |
| --- | --- |
| `backend/` | API, provider adapters, interpretation, persistence and offline tests |
| `frontend/admin/` | Private inspector assets; bundled in wheels as `backend/admin_assets/` |
| `frontend/demo/` | Live display assets; bundled as `backend/demo_assets/` |
| `ios/` | Native SwiftUI app, XcodeGen spec/project, resources and tests |
| `companion/` | Android WebView display host and build/launch scripts |
| `contracts/v1/` | Generated API and extraction schemas |
| `evaluation/` | Corpus/batch/replay/scoring/cost tools |
| `docs/examples/` | Synthetic contract examples and preserved handoff schema used by tests |
| `website/` | Existing showcase source, reviewed assets and Webflow packaging |

Python packaging/lockfiles stay at the root. `.env`, `.local/`, `samples/`, `results/`, `reference/`, generated exports and QA captures remain ignored. Do not commit real invoice/banking data or credentials.

## Architecture

Scan & Pay runs one Python/FastAPI API service. The mobile client, admin and live display use that service; only explicitly selected provider stages send data to hosted inference APIs.

### Components

| Component | Source | Responsibility |
| --- | --- | --- |
| Native app | `ios/ScanAndPay/` | AVFoundation capture, Apple Vision detection, crop/review, authenticated upload/polling, draft recovery |
| API and worker runtime | `backend/api.py`, `backend/runtime.py` | Validate requests, resolve exact profiles, persist acceptance, execute bounded work |
| Provider adapters | `backend/adapters/` | Transport/authentication and provider-specific response mapping |
| Interpretation | `backend/document_observations.py`, `backend/ocr_rules*.py`, `backend/review.py`, `backend/review_guidance.py` | OCR observations, field associations, normalization and required/optional review guidance |
| Persistence | `backend/store.py` | SQLite jobs, stages, accounting, frozen profiles, reviews and idempotency |
| Admin | `frontend/admin/` | Shared next-scan selection and private saved-record inspection |
| Observation hub | `backend/demo_events.py` | Bounded, sanitized mobile/backend journey snapshots |
| Display | `frontend/demo/`, `companion/` | Live browser views and controlled-origin Android WebView host |
| Evaluation | `evaluation/` | Input manifests, fresh batches, saved-response scoring and costs |

### A scan's lifecycle

1. The app captures/imports and adjusts an image locally. On explicit Send, it reads the advertised selection and freezes the image, options, exact profile/version and key.
2. The API authenticates, decodes the JPEG/PNG, preserves original bytes and prepares an oriented metadata-free RGB PNG. It records hashes/transforms and atomically persists a job before dispatch.
3. A bounded worker executes the selected profile. Compare executes independently selected profiles; it never combines their votes. A hybrid explicitly composes multiple stages.
4. Adapters and local interpretation create linked payment candidates. Validation records missing/ambiguous/invalid fields while preserving usable observations.
5. The app polls the accepted scan and renders the editable draft with read-only review guidance. Original extraction/evidence remains immutable.
6. Confirm writes a separate review snapshot with a stable UUID. It does not execute a payment or change the original extraction's correctness/review outcome.

### Data destinations

| Stage | External content | Local content |
| --- | --- | --- |
| Direct vision model | Provider rendition plus task/schema | Original image, hashes, result, diagnostics and retained response |
| OCR/document service | Image and, where applicable, requested schema | Returned text/layout/fields and their mapping |
| Deterministic rules | No new external transfer | Interpretation of returned OCR/document observations |
| OCR → model | Image to OCR, then text/layout to the interpreter | Separate stage/recipient records and combined timing/cost |
| Native document detection | No provider transfer | Phone camera frames, document geometry and perspective correction |
| Display telemetry | No payment fields, image or provider credential | Sanitized identifiers, phases and observed stage events |

Provider content handling is account/service-specific. The configured API service is local, but selected inference stages are hosted. Region/retention/training metadata must not be inferred from headquarters, model licensing or a hostname. Unknown processing residency stays unknown.

### Storage and isolation

`.local/backend/jobs.sqlite3` stores jobs, immutable request/profile snapshots, stage state, accounting, backend identity, shared selection and separate mobile reviews. Private job directories retain images/renditions and raw outputs. Source samples and labels stay in their private locations.

Admin/profile/scan reads use bearer authentication. Public `/admin` and `/demo` shells contain no private records; their data endpoints authenticate. Tokens stay in device Keychain/Keystore or transient admin memory. Provider credentials remain in the private backend environment.

A process lock prevents two service owners sharing a data directory. Completed work survives restart; unfinished work becomes interrupted, with no automatic inference replay. Scan deletion rejects active work and leaves a minimal hashed idempotency tombstone, so a deleted request cannot silently run again.

### Networking and recovery

The ASGI entry point supports an explicit private bind address. Optional `scanpay-serve` reconciles private/link-local IPv4 listeners using `/sbin/ifconfig` discovery for physical `en*` interfaces; this launcher is deployment tooling, not an API requirement. The native settings store one private server address; their hotspot label reflects the current demonstration setup. Reconnect uses authenticated reads and checks the persistent `server_id`; older accepted drafts use scan/image identity checks. Uncertain legacy uploads remain bound to their original address when identity cannot be established safely.

Two jobs can progress concurrently with bounded outbound calls and queue capacity. Profile stage/job timeouts are explicit. Disconnection is not cancellation, and a timeout does not prove the upstream provider stopped processing. No hidden retry or provider fallback is introduced.

### Live observation

The phone optionally publishes best-effort phase/sequence/journey snapshots. Scan headers bind a real job to that journey. The observation hub also receives real transport/runtime events, then serves complete revisioned snapshots through authenticated SSE or polling.

Phone and backend states stay independent: reset does not cancel accepted extraction, and a prior result cannot replace a new journey. Completion is projected only after a review write succeeds. Persistence is bounded/coalesced and separate from the scan/accounting store; observation failures cannot fail extraction or confirmation. Remote progress percentages are not invented.

Exact routes and invariants are in the [API contract](API_CONTRACT.md).

## Providers and extraction profiles

A profile is a versioned processing recipe: provider/model or processor, request options, prompt/schema, mapping/rules, review policy and accounting/data-destination metadata. Multiple models from one provider remain distinct choices. The live catalogue is authoritative for currently configured/enabled choices; a name in source is not an account-access guarantee.

### Implemented integrations

| Provider | Available integration families |
| --- | --- |
| OpenAI | Direct image models; OCR-text interpretation |
| Gemini | Direct image models |
| Mistral | Direct image models, OCR + rules, OCR/schema annotations; OCR stage for hybrids |
| Anthropic | Direct image models |
| Together | Hosted open-weight vision models |
| xAI | Direct image models with separately recorded reported charges |
| Google Document AI | OCR and Invoice Parser |
| Azure Document Intelligence | Read and Invoice |
| AWS Textract | Text and Expense |
| Mindee | Structured invoice extraction |

Fireworks and Cohere Aya are not supported by the active implementation. Example presets are in `providers.example.json` and `providers.expanded.example.json`; they contain no configured credentials and do not enable themselves.

### Selection and request snapshots

The admin and live display **Next scan** controls share the same persisted selection. A new phone Send reads its exact profile ID/version, verifies readiness and freezes that reference with the request. Existing scans and pending recovery do not adopt a new default.

Extract runs one profile. Compare resolves explicit profile IDs or `all_enabled` into an immutable eligible roster. Disabled, missing, unconfigured or image-incompatible explicit choices fail before dispatch. Compare returns independent results, with no vote or automatic winning result. No provider fallback or substitution is hidden in a method.

Compatible compact LLM definitions include document country/language context as standard. The current `invoice-context@4` prompt separates Croatian remittance models from foreign identifiers and extracts pagoPA/CBILL draft identifiers without confusing payment channels with separate bills. `review@5` and normalization revision 3 are included in profile identity; new definitions get new versions without rewriting saved results or frozen request options. `backend/billers.py` owns scheme requirements, conservative identifier formatting and printed-channel guidance. Per-option labels, dates and conditions are retained. Exact duplicated pagoPA notices merge evidence only when field recovery has no findings; instalment choices retain distinct identifiers and are not labelled extraction conflicts. No payment-provider API is invoked. Account-country evidence and actual payment-route guidance remain separate; country/language alone never selects a biller scheme. Original v1/v2/v3 context prompts and schemas remain available for historical request reconstruction.

### Readiness and endpoints

Enablement requires supported configuration, credentials, model/resource access and recorded account/data-terms checks. Pricing dates/per-call ceilings are optional accounting metadata. Local spending/cumulative-call limits are not enforced. Queue capacity, authentication, supported endpoints and idempotency still apply.

Supported OpenAI hosts include `api.openai.com`, `eu.api.openai.com` and `us.api.openai.com`; Mistral supports `api.mistral.ai` and `api.eu.mistral.ai`. Regional routes are explicitly configured, not selected automatically. Google Document AI uses the processor's configured location/version. Providers can reject requests for account or model reasons; the backend preserves that failure without switching endpoints.

A regional hostname, account headquarters or open-weight licence does not establish processing residency. Unknown residency remains unknown. Account retention/training controls must be checked for the exact service; `store=false` on supported OpenAI requests is not a universal zero-retention guarantee. Credentials are described in [setup](SETUP.md).

### Results and failures

| Result | Meaning |
| --- | --- |
| `success` | Useful draft passed the selected completeness/review policy; factual accuracy still needs review |
| `incomplete` | Request produced recoverable fields with missing/uncertain requirements |
| `error` | No usable invoice/payment fields or failed processing; OCR text alone is insufficient |
| Provider error code | Authentication, quota, timeout, refusal, availability or output failure recorded for that run |

API completion, draft completeness and extraction correctness are different measurements. A timeout does not establish bad credentials or prove upstream processing stopped. Invalid individual fields can be quarantined while recoverable observations remain visible under the selected partial-field policy.

Existing evidence gaps, not newly tested in this guide: Haiku 4.5 has a retained availability/connection failure, Mistral Large 4 has a retained timeout, and two AWS processing profiles have authenticated but untested processing. These are latest recorded outcomes, not claims of current provider outage. Google OCR/Invoice have completed processing evidence.

### Accounting and destinations

Each external stage records the actual recipient, configured/verified region, payload class, requested/returned model, timing, usage and request identifier where available. Hybrids record each stage separately and add their costs/latencies.

Use provider-reported charges where supported, otherwise explicit saved tariffs and observed usage. Missing usage/pricing/failure charges remain unknown; do not convert them to zero. Internal conservative holds are not provider invoices, and tax/FX/account credits require separate evidence. Grok's opt-in reported-cost profile uses `cost_in_usd_ticks / 10^10`; missing ticks means unknown and malformed values fail rather than double-count reasoning.

Fresh provider runs need a saved complete input/profile/repeat plan, new stable keys and explicit outcome coverage. See [evaluation](EVALUATION.md).

## Native implementation

### Native capture client

The SwiftUI app supports iOS 18+, bundle ID `com.azikus.scanpay.poc`. AVFoundation capture and Apple Vision document geometry/stability/rectification run on the phone. Lifetime checks discard late camera/detection callbacks, and generation checks isolate preparation, upload and recovery from resets/backgrounding. PNG preparation runs off the UI thread.

The interface uses material/solid fallbacks, semantic colors, accessibility sizing and Reduce Motion. Document pixels and selectable wrapped JSON remain readable. Atomic Application Support records preserve frozen requests/edits/confirmations with file protection and backup exclusion; Keychain holds the local API token.

`-synthetic-preview` is a bundled offline UI fixture; remove it for real operation. Tests cover linked candidates/nulls, geometry/orientation/document stability, exact-profile mismatch, duplicates, interrupted requests, frozen confirmations and late-result isolation. Original Azikus artwork and licensed Hanken Grotesk live in Resources.

### Display host

`com.azikus.scanpay.companion` is a controlled-origin Android WebView host with Internet access, no backup and no provider keys. Android Keystore AES/GCM encrypts the local token; browser storage is disabled. GET access is limited to shell/assets, snapshots/stream and profile catalogue. Its only allowed mutation is PUT to `/v1/admin/selection`; scan submission/confirmation is blocked.

LauncherActivity renders its own window on the restricted customer display; other activities remain private. The ADB script discovers the current presentation display instead of hardcoding its ID. The host keeps only its visible windows awake, always opens the technical primary panel and customer secondary panel and changes no global display/security/network settings. Normal builds have no debug bootstrap/capture helpers or fabricated playback.

### Static frontends

FastAPI serves `/admin` and `/demo` plus allowlisted local assets. Source/editable installs use `frontend/admin/` and `frontend/demo/`; wheels bundle them as `backend/admin_assets/` and `backend/demo_assets/`. Data-free shells are public; private data endpoints use bearer authentication. User/provider metadata is rendered as text, never executed as HTML. Fonts and licences are self-hosted; no separate frontend service or build is required.

`frontend/demo/state.js` projects phone/backend state; `demo.js` owns authenticated fetch-streaming, polling fallback, controls and the stage illustrations. Snapshots are complete/authoritative, disconnection freezes timings/motion, missing heartbeats produce a separate phone state, and prior journeys are excluded. Frozen scan/stage metadata determines provider labels. Saved confirmation alone drives completion; Reduced Motion disables repeating/spatial effects.

## Backend checks

From the root:

```sh
.venv/bin/ruff check backend evaluation
.venv/bin/ruff format --check backend evaluation
.venv/bin/mypy backend evaluation
.venv/bin/pytest --cov=backend --cov=evaluation --cov-report=term-missing --cov-report=json:.local/coverage.json
.venv/bin/python -m backend.check_coverage
.venv/bin/python -m backend.export
```

Tests block sockets and use synthetic fixtures. Domain/orchestration gates require at least 90% statements and 85% branches; generated/vendor code is excluded honestly. Contract generation must match committed schemas. Test meaningful associations, null/decimal/digit semantics, partial-output handling, idempotency, recovery, review invariants and isolation from observer failures.

## Frontend and packaging

```sh
node --check frontend/admin/admin.js
node --check frontend/admin/context.js
node --test frontend/admin/context.test.mjs
node --check frontend/admin/theme.js
node --check frontend/demo/demo.js
node --test frontend/demo/state.test.mjs
.venv/bin/python -m hatchling build
```

When changing package assets, install a wheel outside the checkout and verify both shells, every allowed asset and rejection of unlisted paths. Browser QA uses isolated synthetic records, never private live invoice pages or provider calls. Review keyboard use, small screens, reduced motion, connection loss and error states.

Native build/test commands and signing preservation are in [Setup](SETUP.md#native-client-build-and-tests). Keep the existing phone bundle ID, Keychain/drafts and display signing identity. Display QA uses 1280 × 720, 1280 × 800 and 1920 × 1080 layouts, with keyboard/reduced-motion/hybrid/error/completion/reconnect checks through an isolated backend rather than file URLs.

## Documentation

`README.md` is the screenshot-led explanation. Keep the four focused technical guides current rather than adding another phase plan, change log or per-chat handoff. Git stores the change history. Benchmark measurements belong in EVALUATION.md with exact scope/caveats; private reports retain full provenance.

Reuse reviewed assets from `website/assets/` for screenshots. Retain source descriptions/hashes and licences; distinguish synthetic/native screenshots, isolated QA sessions and real-device acceptance. Do not generate a fake application screen or include readable source invoices.

Website source/build/attribution/handoff instructions live in `website/README.md`. The repository keeps seven Markdown files total; add links/sections rather than duplicate READMEs or handoffs.
