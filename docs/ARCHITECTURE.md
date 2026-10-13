# Architecture

Scan & Pay runs one Python/FastAPI service on the Mac. The iPhone, admin and SUNMI companion use that service; only explicitly selected provider stages send data to hosted inference APIs.

## Components

| Component | Source | Responsibility |
| --- | --- | --- |
| Native app | `ios/ScanAndPay/` | AVFoundation capture, Apple Vision detection, crop/review, authenticated upload/polling, draft recovery |
| API and worker runtime | `backend/api.py`, `backend/runtime.py` | Validate requests, resolve exact profiles, persist acceptance, execute bounded work |
| Provider adapters | `backend/adapters/` | Transport/authentication and provider-specific response mapping |
| Interpretation | `backend/document_observations.py`, `backend/ocr_rules*.py`, `backend/review.py`, `backend/review_guidance.py` | OCR observations, field associations, normalization and required/optional review guidance |
| Persistence | `backend/store.py` | SQLite jobs, stages, accounting, frozen profiles, reviews and idempotency |
| Admin | `frontend/admin/` | Shared next-scan selection and private saved-record inspection |
| Observation hub | `backend/demo_events.py` | Bounded, sanitized mobile/backend journey snapshots |
| Display | `frontend/demo/`, `sunmi/companion/` | Live browser views and controlled-origin Android WebView host |
| Evaluation | `evaluation/` | Input manifests, fresh batches, saved-response scoring and costs |

## A scan's lifecycle

1. The app captures/imports and adjusts an image locally. On explicit Send, it reads the advertised selection and freezes the image, options, exact profile/version and key.
2. The API authenticates, decodes the JPEG/PNG, preserves original bytes and prepares an oriented metadata-free RGB PNG. It records hashes/transforms and atomically persists a job before dispatch.
3. A bounded worker executes the selected profile. Compare executes independently selected profiles; it never combines their votes. A hybrid explicitly composes multiple stages.
4. Adapters and local interpretation create linked payment candidates. Validation records missing/ambiguous/invalid fields while preserving usable observations.
5. The app polls the accepted scan and renders the editable draft with read-only review guidance. Original extraction/evidence remains immutable.
6. Confirm writes a separate review snapshot with a stable UUID. It does not execute a payment or change the original extraction's correctness/review outcome.

## Data destinations

| Stage | External content | Local content |
| --- | --- | --- |
| Direct vision model | Provider rendition plus task/schema | Original image, hashes, result, diagnostics and retained response |
| OCR/document service | Image and, where applicable, requested schema | Returned text/layout/fields and their mapping |
| Deterministic rules | No new external transfer | Interpretation of returned OCR/document observations |
| OCR → model | Image to OCR, then text/layout to the interpreter | Separate stage/recipient records and combined timing/cost |
| Native document detection | No provider transfer | Phone camera frames, document geometry and perspective correction |
| SUNMI telemetry | No payment fields, image or provider credential | Sanitized identifiers, phases and observed stage events |

Provider content handling is account/service-specific. The Mac backend is local, but selected inference stages are hosted. Region/retention/training metadata must not be inferred from headquarters, model licensing or a hostname. Unknown processing residency stays unknown.

## Storage and isolation

`.local/backend/jobs.sqlite3` stores jobs, immutable request/profile snapshots, stage state, accounting, backend identity, shared selection and separate mobile reviews. Private job directories retain images/renditions and raw outputs. Source samples and labels stay in their private locations.

Admin/profile/scan reads use bearer authentication. Public `/admin` and `/demo` shells contain no private records; their data endpoints authenticate. Tokens stay in device Keychain/Keystore or transient admin memory. Provider credentials remain in the private backend environment.

A process lock prevents two service owners sharing a data directory. Completed work survives restart; unfinished work becomes interrupted, with no automatic inference replay. Scan deletion rejects active work and leaves a minimal hashed idempotency tombstone, so a deleted request cannot silently run again.

## Networking and recovery

`scanpay-serve` keeps loopback and reconciles physical private/link-local IPv4 listeners. The iOS settings expose one saved hotspot address. Reconnect uses authenticated reads and checks the persistent `server_id`; older accepted drafts use scan/image identity checks. Uncertain legacy uploads remain bound to their original address when identity cannot be established safely.

Two jobs can progress concurrently with bounded outbound calls and queue capacity. Profile stage/job timeouts are explicit. Disconnection is not cancellation, and a timeout does not prove the upstream provider stopped processing. No hidden retry or provider fallback is introduced.

## Live observation

The phone optionally publishes best-effort phase/sequence/journey snapshots. Scan headers bind a real job to that journey. The observation hub also receives real transport/runtime events, then serves complete revisioned snapshots through authenticated SSE or polling.

Phone and backend states stay independent: reset does not cancel accepted extraction, and a prior result cannot replace a new journey. Completion is projected only after a review write succeeds. Persistence is bounded/coalesced and separate from the scan/accounting store; observation failures cannot fail extraction or confirmation. Remote progress percentages are not invented.

Exact routes and invariants are in the [API contract](API_CONTRACT.md).
