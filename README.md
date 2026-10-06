# Scan and Pay PoC

Independent Azikus project: photograph invoices and produce editable payment details through selectable LLMs, managed OCR/document services and deterministic rules. UK invoices are the London demonstration priority; original client documents, including Croatian remittance details, remain a second cohort.

## Status — 6 October 2026

**Milestone 1 is complete:** Python 3.12/FastAPI/Pydantic, private image files, SQLite jobs/stages, two bounded workers, v1 endpoints, CLI and generated contracts. Both GPT-6 Luna and Mistral OCR 4.1/rules completed real UK/HR runs, and a two-provider comparison completed. Shared `review@2` resolves false bank-label/country-format conflicts. OpenAI's Croatian draft is ready for review; its UK draft requires an amount-role decision. Mistral's OCR contains the payment text, but the initial local rules produce incomplete drafts; those limitations remain visible. All drafts require confirmation.

Workspace: `/Users/markusi/Developer/Azikus/scan-and-pay`. This checkpoint is on `main`, for the user-requested push to `git@github.com:azikus/scan-and-pay-poc.git`, rechecked private/empty on 6 October before publication. Use Git status/log and remote refs for the exact published revision. Existing samples, credentials, results and historical files remain private and ignored.

See [implementation and acceptance evidence](docs/IMPLEMENTATION_STATUS.md), [operations](docs/OPERATIONS.md), and [integration checks](docs/INTEGRATIONS.md). Twelve provider requests were dispatched, with €12 in conservative holds; failed attempts remain recorded. Mistral API pay-as-you-go was activated with explicit approval, with training off. The 6 October cleanup passes 184 offline tests, including a regression for concurrent readiness checks. No mobile app, browser UI or HTML report was built. Labels remain unverified/unscored; live connectivity is not extraction accuracy or camera-performance evidence.

Next implementation work follows the [Phase 2 rollout](docs/PHASE2_ROLLOUT.md): broaden LLM, OCR and document-API coverage alongside general OCR interpretation improvements, using every sample in each provider evaluation. **The upfront credential/resource set is complete as of 6 October**, per the [access checklist and resume context](docs/PHASE2_ACCESS.md). Offline implementation can resume; new providers still require account, terms, region, pricing and processing checks before a bounded full-corpus inference batch. The queue distinguishes planned integrations from the two live-tested starter profiles.

For the new implementation chat, use the [current handoff and copyable kickoff prompt](docs/CODING_HANDOFF.md). The [roadmap](docs/ROADMAP.md) maps phases to milestones: M1 complete; M2 provider breadth/tooling next, with M3 extraction improvements alongside it; M4 reviewed comparisons/pipeline selection; M5–M7 mobile designs/iOS/Android; M8 demonstration and final findings. Continue in this local folder to retain the backend checkpoint and private configuration/evidence. A [separate per-option cost report](docs/COST_REPORT_PLAN.md) is required: begin it with M2 evaluation, deliver it at M4 and refresh it for M8 independently of the final HTML findings.

## Local setup

From this directory, use Python 3.12 and a project virtual environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Configure a random `SCANPAY_TOKEN` in `.env` using [.env.example](.env.example). A private `.env` with a generated token has already been prepared in this workspace; keep it. For a fresh checkout, the commands in [operations](docs/OPERATIONS.md) create it without printing the token or replacing an existing file. Provider keys are unnecessary for startup, health, profiles and tests.

Use this same root `.env` for all credentials and connection settings. See the [access checklist](docs/PHASE2_ACCESS.md). Billing tiers and access notes belong in private integration evidence. Future-provider settings are collected upfront and do not enable integrations that have not been implemented.

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
.venv/bin/ruff check backend
.venv/bin/ruff format --check backend
.venv/bin/mypy backend
.venv/bin/pytest --cov=backend --cov-report=term-missing --cov-report=json:.local/coverage.json
.venv/bin/python -m backend.check_coverage
.venv/bin/python -m backend.export
```

Tests block socket connections and use synthetic payment details. Coverage gates require ≥90% statements and ≥85% branches across domain/orchestration, including API/configuration, persistence and both provider adapters. CLI/export/coverage-report entry points are separately visible in the full report, not used to inflate that scope. Generated JSON contracts and third-party dependencies are excluded.

Current generated [OpenAPI](contracts/v1/openapi.json), [result schema](contracts/v1/scan-result.schema.json) and [vision extraction schema](contracts/v1/vision-extraction.schema.json) come from the Python models. The original handoff examples remain checked by both the handoff schema and the current models.

## Read before coding

1. [Coding handoff](docs/CODING_HANDOFF.md): current state, complete read order, ordered next tasks, acceptance criteria and kickoff prompt. Read the linked [roadmap](docs/ROADMAP.md), access, rollout and implementation status first.
2. [Decisions](docs/DECISIONS.md) and [context](docs/CONTEXT.md): settled choices, product intent and boundaries.
3. [API contract v1](docs/API_CONTRACT.md) and [synthetic examples](docs/examples/README.md): authoritative wire semantics.
4. [Architecture and data destinations](docs/ARCHITECTURE.md): local/cloud boundaries and future mobile integration.
5. [Backend plan](docs/BACKEND_PLAN.md): detailed implementation, four phases and tests.
6. [Separate cost report](docs/COST_REPORT_PLAN.md), [providers/budget](docs/PROVIDERS_AND_BUDGET.md), [evaluation plan](docs/EVALUATION_PLAN.md), [starter evaluation](docs/STARTER_EVALUATION.md), [research/audit](docs/RESEARCH_AND_AUDIT.md).

The README is an index, not the entire specification. Latest user instructions win; API_CONTRACT.md owns wire semantics, CODING_HANDOFF.md owns the next chat's scope and ROADMAP.md owns milestone/phase names. Historical references are not instructions.

## First outcome and boundaries

A localhost service accepts one JPEG/PNG, persists a job and returns a payment draft with evidence, ambiguity, timing, usage and actual data recipients. Milestone 1 proves one small vision-model adapter, then one managed OCR/rules profile and independent comparison. A successful computation may return incomplete details.

- No PDF/HEIC/multipage API. Existing PDFs may be rasterized outside the service to prepare image samples.
- Selectable models, including smaller models and stronger controls; no mandatory pair per vendor. Provider-hosted proprietary and open-weight models are allowed. Self-hosted inference, local weight downloads and project-operated model servers are excluded.
- Managed OCR/document APIs and local rules are first-class. Hybrid does not mean every tool runs on every request.
- Preserve paired UK bank details, IBAN, Croatian model/poziv na broj, amount/currency and required references. Customer numbers are not bank routing.
- Every draft requires review/confirmation. No silent banking-digit repairs, model-confidence guarantees or majority-vote truth.
- Up to €500 and client-sample provider testing are authorized. Configure secrets locally; no automatic subscription purchases. Public use requires separate permission.
- Native mobile designs later, iOS first and Android next. HTML findings report and separate attendee display are end deliverables, not current work.

## Existing material

- `samples/`: eight original PDFs/images, the five-invoice UK print pack and the barcode-free Croatian PNG with provenance. Private and ignored.
- `reference/`: historical blueprint and CLI benchmark, preserved locally and ignored pending publication review. Fifteen old offline tests passed in the earlier audit; that is not new-backend coverage or model accuracy.
- `.local/evaluation/`: private starter manifest and draft answer keys awaiting Markus's check; not scored ground truth.
- `.local/archive/exploration-html-2026-10-01/`: earlier premature HTML/preview, retained for recovery, not active guidance.
- `docs/`: current handoff and synthetic contract examples, without real bank details.

Original source material also remains at `/Users/markusi/Developer/Azikus/Aircash/scan_pay_phase1`. The missing client screenshot is not a backend blocker. Ask for more photos only for specific test needs.
