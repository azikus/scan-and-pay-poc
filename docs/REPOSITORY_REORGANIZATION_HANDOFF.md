# Repository reorganization — 9 October 2026

The mobile/admin checkpoint merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2) at `62ac67da3aefd5817466e326cdd0b362ae58edd1`. Markus authorized this separate structural refactor, checks, documentation/status updates and normal PR/merge without further routine confirmation. Refactor branch: `codex/repository-layout`. The PR link is recorded below when created; verify actual merge state at that link.

## Delivered layout

| Directory | Contents |
| --- | --- |
| `backend/` | Existing Python package, API, domain/orchestration, providers, persistence and offline tests; import names unchanged |
| `frontend/admin/` | Inspector HTML, JavaScript, CSS, artwork and licensed fonts, moved byte-for-byte from the former `backend/admin_assets/` source directory |
| `ios/` | Native project, XcodeGen specification, source/resources and tests, moved from the former `apps/ios/`; README paths/current setup updated |
| `android/` | Future-work README only; no app, scaffolding or dependencies |
| `contracts/`, `docs/`, `evaluation/` | Shared contract, documentation and evaluation tooling, retained at the root |

Root `pyproject.toml`, `requirements.lock`, examples and private configuration remain in place. Backend and frontend still use a single FastAPI deployment. Source/editable runs resolve assets in `frontend/admin/`; Hatch bundles those same files and the font license into `backend/admin_assets/` inside installed wheels. That internal wheel path is intentional. No separate frontend build or server was introduced.

API routes/contracts, extraction profiles/behavior, scan UX, source filters, saved provider-output/mobile-image inspection, confirmation, recovery and reconnect semantics are unchanged. Historical experiment records were not rewritten. Private source/evidence/data directories were not moved.

## Verification

- **672 offline backend/evaluation tests pass**. Measured domain/orchestration coverage: **3,598/3,751 statements (95.92%) and 1,318/1,446 branches (91.15%)**. Ruff lint/format, strict mypy, JavaScript syntax and regenerated-contract comparison pass; all three contract exports are unchanged.
- Source-checkout admin serving passes. A wheel installed into a temporary directory was exercised outside the checkout with network connections blocked and synthetic settings: health, authentication, `/admin`, every allowlisted asset, security headers and rejection of unlisted assets pass. Every packaged asset and the font license matches its source hash. Tests/private/mobile files are absent from the wheel. A fresh wheel rebuilt from the source distribution retains the same assets.
- `xcodegen generate --spec ios/project.yml` regenerates a byte-identical project. All moved iOS implementation, project, scheme, resources and fixtures are byte-identical; only its README changes. A fresh simulator build from the new path passes **16 native unit/recovery tests and 2 UI tests** on the existing iPhone 16 Pro / iOS 18.6 simulator (`A01D44F3-7512-4AED-BD55-5B5688DB2015`). No physical-phone reinstall, unlock or new device test was needed or performed.
- Authenticated local profiles, methods and mobile scan-list reads pass, along with health and all admin asset routes. These are GET requests only; no inference, evaluation replay or paid call occurred.
- The Python check reports a dependency deprecation warning for Starlette's httpx TestClient integration. Xcode reports skipped App Intents metadata extraction because the app does not use that framework. Neither warning fails a check; dependencies and app behavior were not changed for this refactor.

Private verification evidence is in `.local/repository-reorganization-2026-10-09/`: `backend-checks.log`, `ios-checks.log`, `ios-tests.xcresult`, `packaging-checks.log`, the packaging verification script/builds, and preservation records. No private logs, artifacts or raw payment data enter Git.

## Private state and runtime

Before editing, the original credential/config fingerprints and all **2,201 budget rows** matched `.local/mobile-pr-checkpoint-2026-10-09/private-state-before.json`, including its original-row digest. The reorganization recorded a fresh database snapshot, SQLite backup and hashes for **8,102 private files** across source samples, results, historical reference material and backend job artifacts. Verification compares every recorded database table, credential/config fingerprint and artifact hash after the move.

The ledger remains **2,201 dispatches / €336.45 held**, under unchanged cumulative limits of 2,217 / €338.05. The persisted selection remains **Mistral Small direct**, `mistral-small-image-roles-v3@2-b292ba761e512607`. Existing scans, keys, confirmations, profile snapshots and backend identity are preserved. Root `.env`, SDK credential stores, `.local/providers.json`, `.local/backend/jobs.sqlite3`, source invoices, labels and raw responses remain private.

The existing launcher `.local/mobile-live-2026-10-09/serve.py` was restarted only after checking its PID and confirming zero queued/running jobs. The same launcher, PID file, log, settings and data directory remain the single backend owner; no launcher or network-design change was required. Read its `server.pid` for the current PID. The inspector is available at `http://127.0.0.1:8000/admin`, with the existing local token and interface listeners. Startup still discovers the Mac's current configured interfaces; saved phone URLs are not automatic discovery.

The installed iPhone app and its data were untouched. The latest physical reconnect evidence remains **USB failed → Wi-Fi connected**; this refactor does not establish new USB, hotspot, real-invoice accuracy or camera-to-review timing results.

## Next joint task

Build the presentation **together with Markus when he returns**, using retained speed/correctness evidence. Then improve the mobile client, work on the backend and implement Android last. Presentation work, paper detection, native OCR, automatic discovery and new backend features were not started during cleanup. No force push, protection bypass, public publication or subscription is part of this work.
