# Development

Read the [product guide](../README.md), [architecture](ARCHITECTURE.md), [API contract](API_CONTRACT.md) and the affected source README. `AGENTS.md` contains workspace preservation and task-specific guidance.

## Repository map

| Path | Contents |
| --- | --- |
| `backend/` | API, provider adapters, interpretation, persistence and offline tests |
| `frontend/admin/` | Private inspector assets; bundled in wheels as `backend/admin_assets/` |
| `frontend/demo/` | Live display assets; bundled as `backend/demo_assets/` |
| `ios/` | Native SwiftUI app, XcodeGen spec/project, resources and tests |
| `sunmi/companion/` | Android WebView display host and build/launch scripts |
| `contracts/v1/` | Generated API and extraction schemas |
| `evaluation/` | Corpus/batch/replay/scoring/cost tools |
| `docs/examples/` | Synthetic contract examples and preserved handoff schema used by tests |
| `presentation/` | Existing reveal.js deck and local export tooling |
| `website/` | Existing showcase source, reviewed assets and Webflow packaging |
| `android/` | Capture-app scope marker; no Android capture app |

Python packaging/lockfiles stay at the root. `.env`, `.local/`, `samples/`, `results/`, `reference/`, generated exports and QA captures remain ignored. Do not commit real invoice/banking data or credentials.

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
node --check frontend/admin/theme.js
node --check frontend/demo/demo.js
node --test frontend/demo/state.test.mjs
.venv/bin/python -m hatchling build
```

When changing package assets, install a wheel outside the checkout and verify both shells, every allowed asset and rejection of unlisted paths. Browser QA uses isolated synthetic records, never private live invoice pages or provider calls. Review keyboard use, small screens, reduced motion, connection loss and error states.

Native build/tests and signing preservation are in [ios/README.md](../ios/README.md); Android display packaging is in [sunmi/companion/README.md](../sunmi/companion/README.md). Keep the existing phone bundle ID, Keychain/drafts and display signing identity.

## Documentation

`README.md` is the screenshot-led explanation. Keep the six focused technical guides current rather than adding another phase plan, change log or per-chat handoff. Git stores the change history. Benchmark measurements belong in EVALUATION.md with exact scope/caveats; private reports retain full provenance.

Reuse reviewed assets from `website/assets/` for screenshots. Retain source descriptions/hashes and licences; distinguish synthetic/native screenshots, isolated QA sessions and real-device acceptance. Do not generate a fake application screen or include readable source invoices.

The existing deck's English slides/Croatian notes are preserved. `npm run content` in `presentation/` generates `presentation/CONTENT.md`; source HTML remains the authority. Website source/build/handoff instructions stay together in `website/`.
