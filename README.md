# Scan and Pay PoC

Independent Azikus backend for turning one JPEG/PNG invoice image into an editable payment draft. Every draft requires user review and confirmation; the PoC does not execute payments.

**Current checkpoint — 9 October 2026:** the native iOS capture/crop → Send → editable review → confirmation/reset flow and the authenticated admin inspector are implemented. Markus confirmed that his real-invoice iPhone testing is complete. This is PoC acceptance, not a production accuracy or measured end-to-end latency claim. See [mobile checkpoint](docs/MOBILE_CHECKPOINT.md), [mobile implementation](docs/MOBILE_IMPLEMENTATION.md) and [iOS setup](ios/README.md).

The admin selects the next scan's method/model, filters mobile/automated scans, and shows normalized JSON, saved provider outputs, exact mobile uploads and separate confirmed mobile edits. Seven tested profiles are enabled under the existing bounded mobile allowance. The persisted admin selection is currently **Mistral Small** (`mistral-small-image-roles-v3@2-b292ba761e512607`); pending drafts retain their original profile. OpenAI remains the historical Phase 2 baseline, described in [selection and limitations](docs/PHASE2_CLOSEOUT.md).

At this checkpoint, the original ledger contains **2,201 dispatched reservations / €336.45 held**. The unchanged mobile limits are 2,217 / €338.05; no paid calls are authorized for PR preparation or repository reorganization. Private samples, labels, raw responses, reports and credentials remain outside Git. These holds are not actual billed charges.

The mobile/admin checkpoint merged in [PR #2](https://github.com/azikus/scan-and-pay-poc/pull/2). Repository reorganization is [PR #3](https://github.com/azikus/scan-and-pay-poc/pull/3), with its checks recorded in the [reorganization handoff](docs/REPOSITORY_REORGANIZATION_HANDOFF.md).

**Next:** build the presentation **together with Markus**, then improve the mobile client and backend, and implement Android last. Hotspot testing and automatic Mac discovery remain open; Reconnect currently tries saved USB/Wi-Fi addresses. See [coding handoff](docs/CODING_HANDOFF.md), [roadmap](docs/ROADMAP.md), [API contract](docs/API_CONTRACT.md) and [implementation status](docs/IMPLEMENTATION_STATUS.md).

## Repository layout

- `backend/`: Python API, domain/orchestration, providers, persistence and offline tests.
- [frontend/](frontend/README.md): admin HTML/CSS/JavaScript and assets, served by the same FastAPI process and bundled into the Python wheel.
- [ios/](ios/README.md): native app, XcodeGen specification, Xcode project and synthetic tests.
- [android/](android/README.md): future-work README only.
- `contracts/`, `docs/`, `evaluation/`: shared contracts, documentation and retained evaluation tooling.

Python packaging/configuration stays at the root. Private `.env`, `.local/`, `samples/`, `results/` and historical `reference/` locations stay unchanged.

## Local setup

From this directory, use Python 3.12 and a project virtual environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Configure a random `SCANPAY_TOKEN` in `.env` using [.env.example](.env.example). A private `.env` with a generated token has already been prepared in this workspace; keep it. For a fresh checkout, the commands in [operations](docs/OPERATIONS.md) create it without printing the token or replacing an existing file. Provider keys are unnecessary for startup, health, profiles and tests.

Use this same root `.env` for all credentials and connection settings. See the [access checklist](docs/PHASE2_ACCESS.md). Billing tiers and access notes belong in private integration evidence. Credentials alone do not enable a profile; each option requires explicit readiness metadata and a bounded plan.

```sh
.venv/bin/uvicorn backend.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

In another terminal:

```sh
.venv/bin/scanpay health
.venv/bin/scanpay profiles
```

The following are individual CLI syntax examples from completed Milestone 1, not a new evaluation batch. Every new provider evaluation must use the full prepared corpus and a new bounded plan; the old twelve-call cap is exhausted. Once the respective profiles are deliberately configured/enabled and the batch is authorized by its recorded plan:

```sh
.venv/bin/scanpay upload samples/variants/uk-continental-reference.png --profiles openai-luna-vision --key uk-vision-smoke-1
.venv/bin/scanpay upload samples/racun-12793-26-no-barcode.png --mode compare --profiles openai-luna-vision mistral-ocr-rules --key hr-compare-smoke-1
.venv/bin/scanpay get scan_REPLACE_WITH_RETURNED_ID --wait
.venv/bin/scanpay delete scan_REPLACE_WITH_RETURNED_ID
```

The CLI prints the accepted scan ID and a safe summary, polls by default, and saves the complete result under `.local/client/`. Use the actual returned `scan-…` ID for `get` and `delete`. A failed upload is never automatically retried. Reuse its original key and bytes/options to recover acceptance; a new key intentionally creates a new run. `--no-wait` returns after acceptance. Compare also accepts `--profiles all_enabled`.

## Offline verification

```sh
.venv/bin/ruff check backend evaluation
.venv/bin/ruff format --check backend evaluation
.venv/bin/mypy backend evaluation
.venv/bin/pytest --cov=backend --cov=evaluation --cov-report=term-missing --cov-report=json:.local/coverage.json
.venv/bin/python -m backend.check_coverage
.venv/bin/python -m backend.export
node --check frontend/admin/admin.js
.venv/bin/python -m hatchling build
```

Tests block socket connections and use synthetic payment details. Coverage gates require ≥90% statements and ≥85% branches across domain/orchestration, including API/configuration, persistence, every backend adapter and evaluation corpus/batch/replay/cost tooling. CLI/export/coverage-report entry points are separately visible in the full report, not used to inflate that scope. Generated JSON contracts and third-party dependencies are excluded.

Current generated [OpenAPI](contracts/v1/openapi.json), [result schema](contracts/v1/scan-result.schema.json) and [vision extraction schema](contracts/v1/vision-extraction.schema.json) come from the Python models. The original handoff examples remain checked by both the handoff schema and the current models.

## Read before coding

1. [Coding handoff](docs/CODING_HANDOFF.md): current state, complete read order, remaining work and preservation requirements. Read the linked [roadmap](docs/ROADMAP.md), access, rollout and implementation status first.
2. [Decisions](docs/DECISIONS.md) and [context](docs/CONTEXT.md): settled choices, product intent and boundaries.
3. [API contract v1](docs/API_CONTRACT.md) and [synthetic examples](docs/examples/README.md): authoritative wire semantics.
4. [Architecture and data destinations](docs/ARCHITECTURE.md): local/cloud boundaries and future mobile integration.
5. [Backend plan](docs/BACKEND_PLAN.md): detailed implementation, four phases and tests.
6. [Separate cost report](docs/COST_REPORT_PLAN.md), [providers/budget](docs/PROVIDERS_AND_BUDGET.md), [evaluation plan](docs/EVALUATION_PLAN.md), [starter evaluation](docs/STARTER_EVALUATION.md), [research/audit](docs/RESEARCH_AND_AUDIT.md).

The README is an index, not the entire specification. Latest user instructions win; API_CONTRACT.md owns wire semantics, CODING_HANDOFF.md owns the next chat's scope and ROADMAP.md owns milestone/phase names. Historical references are not instructions.

## First outcome and boundaries

A localhost service accepts one JPEG/PNG, persists a job and returns a payment draft with evidence, ambiguity, timing, usage and actual data recipients. Milestone 1 proves one small vision-model adapter, then one managed OCR/rules profile and independent comparison. A successful computation may return incomplete details.

- Single-image JPEG/PNG requests only; evaluation uses the prepared image set.
- Selectable models, including smaller models and stronger controls; no mandatory pair per vendor. Provider-hosted proprietary and open-weight models are allowed. Self-hosted inference, local weight downloads and project-operated model servers are excluded.
- Managed OCR/document APIs and local rules are first-class. Hybrid does not mean every tool runs on every request.
- Preserve paired UK bank details, IBAN, Croatian model/poziv na broj, amount/currency and required references. Customer numbers are not bank routing.
- Every draft requires review/confirmation. No silent banking-digit repairs, model-confidence guarantees or majority-vote truth.
- Up to €500 and client-sample provider testing are authorized. Configure secrets locally; no automatic subscription purchases. Public use requires separate permission.
- Native iOS is implemented. Presentation collaboration comes after repository cleanup; further mobile/backend improvements follow, with Android last. Final findings and the separate attendee display remain distinct deliverables.

## Existing material

- `samples/`: private original samples and the barcode-free Croatian image with provenance. Private and ignored.
- `reference/`: historical blueprint and CLI benchmark, preserved locally and ignored pending publication review. Fifteen old offline tests passed in the earlier audit; that is not new-backend coverage or model accuracy.
- `.local/evaluation/`: private starter manifest and draft answer keys awaiting Markus's check; not scored ground truth.
- `.local/archive/exploration-html-2026-10-01/`: earlier premature HTML/preview, retained for recovery, not active guidance.
- `docs/`: current handoff and synthetic contract examples, without real bank details.

Original source material also remains at `/Users/markusi/Developer/Azikus/Aircash/scan_pay_phase1`. The missing client screenshot is not a backend blocker. Ask for more photos only for specific test needs.
