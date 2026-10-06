# Local backend operations

Implemented 2 October 2026. Run one process; no Redis, hosted file store or paid startup probes. The schema contract is [API_CONTRACT.md](API_CONTRACT.md).

## Setup and configuration

Follow README's hash-locked Python 3.12 installation. For a fresh checkout only, create local files safely:

```sh
.venv/bin/python - <<'PY'
import os
from pathlib import Path
from secrets import token_urlsafe
for name, content in {
    '.env': 'SCANPAY_TOKEN=' + token_urlsafe(32) + '\nSCANPAY_DATA_DIR=.local/backend\nSCANPAY_PROFILES_FILE=.local/providers.json\nOPENAI_API_KEY=\nMISTRAL_API_KEY=\n',
    '.local/providers.json': Path('providers.example.json').read_text(),
}.items():
    path = Path(name)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.exists():
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
            f.write(content)
PY
```

`.env` and `.local/providers.json` are operator configuration, not request fields. Collect all requested provider credentials upfront in the existing `.env`, preserving configured values; see PHASE2_ACCESS.md. Keep only credentials and connection settings there, with billing tiers and access notes in private integration evidence. Never paste keys into chat. `SCANPAY_DATA_DIR` defaults to `.local/backend`. Keep any alternative data directory private and ignored. Configuration is read at startup; restart after changes. Do not use `--reload` or multiple Uvicorn workers while paid jobs are active.

Handoff checkpoint, 6 October: the requested credential set is already present. Do not run fresh-checkout initialization over existing files or copy `.env.example` onto `.env`. Google uses local ADC; AWS uses the temporary `scanpay` profile in `eu-central-1`, verified as `scanpay-local`. Reauthenticate only if needed, with the same identity/permissions; never copy SDK cache secrets into `.env`. New-provider adapters remain unimplemented. Current starting tasks and evidence paths are in CODING_HANDOFF.md.

Shipped profile examples start disabled; the private starter profiles were deliberately configured and live-validated during Milestone 1. Enabling a new profile requires a local key/authentication mechanism, model-access check date, data-terms check date and note, pricing check date and a conservative `max_call_eur` ceiling. Record configured region as `unknown` when unknown; `verified_processing_region` stays null without evidence. Public rate research does not establish account settings. No subscription is purchased by this backend. See [integration checks](INTEGRATIONS.md).

## API and inspection

Bind to `127.0.0.1`; all four `/v1/` routes require `Authorization: Bearer …`. Health is public and checks only local storage/process readiness. Swagger, ReDoc, browser CORS and public OpenAPI routes are disabled; exported OpenAPI is a development artifact. Provider/profile listings never send invoices or probe model access.

The CLI in README uses the actual multipart API. `POST /v1/scans` accepts one `image` and a JSON string `options`, plus `Idempotency-Key`. Options are `{ "mode": "extract", "profiles": ["openai-luna-vision"], "hints": {} }` or `{ "mode": "compare", "profiles": "all_enabled" }`. It returns 202 and `Location`. Poll `GET` at that location. Completed means computation finished; each payment still requires user confirmation.

Full responses are private `.local/client/scan-….json` files. Bank details are intentionally absent from routine CLI summaries. Original/canonical images and raw responses are in `.local/backend/jobs/<scan_id>/`; SQLite stores options, immutable profile/config snapshots, run results, stage timestamps/destinations, cost records and hashed idempotency keys. Raw bodies and local paths are absent from GET responses. Routine provider debug logging is suppressed.

The canonical rendition is oriented, metadata-free RGB PNG, with transparency flattened on white and no resize. The original bytes are privately preserved. Identity hashes and transforms are recorded. Pillow's decoder resource protection remains enabled. Supplier image constraints are checked separately; exceeding one rejects the entire selection, without silently dropping that profile. The initial OCR rules use general labels and paragraph/table-row positions, retain raw OCR privately, and omit boxes when no verified coordinate mapping is available. Complex layouts can return incomplete drafts.

## Queue, money and recovery

Two workers, at most two outbound calls, ten waiting slots plus two active slots. Profiles run independently, sequentially within a job; two jobs can progress concurrently. A comparison exposes each completed result while later profiles run. It has no overall winner. Each live profile makes one attempt, with a 90-second run/stage boundary and a 240-second job deadline including queue wait. There are no SDK retries or hidden fallback providers.

Acceptance atomically reserves every selected live call in SQLite. Default initial caps are 12 calls and €30, within the €500 project authorization. `max_call_eur` is a conservative operator ceiling including output, FX/tax uncertainty and possible charges; it is not a reported fee. USD estimates remain USD. Held EUR ceilings remain charged against the local smoke budget after dispatch, including failures/timeouts and successful USD estimates, until an operator can reconcile actual billing. No automatic FX conversion or refund is assumed. Never reset the database to evade a cap. An undispatched interrupted run can safely release its hold.

The process lock prevents two servers sharing the same data directory. Completed jobs survive restart. Queued/running work becomes `interrupted`; earlier completed comparison results remain. Upstream processing might continue after a local timeout or restart. Reusing the same key returns the prior job, including an interrupted one; it never restarts inference. A deliberately new key makes a new potentially billed call.

## Deletion

`scanpay delete <scan_id>` returns 204 only for a terminal job after local job artifacts and rows are removed. Active jobs return 409; unknown/deleted IDs return 404. A minimal hashed-key/request-digest tombstone returns 410 on reuse. Anonymous budget/cost records remain to prevent rebilling beyond the cap. This endpoint does not remove `.local/client/` exports; remove those manually when desired. Source samples, answer keys and historical references are never cleanup targets. Local deletion does not delete provider-held data or promise forensic secure erasure.

## Dependency changes

```sh
.venv/bin/pip-compile --extra dev --allow-unsafe --strip-extras --generate-hashes --output-file requirements.lock pyproject.toml
```

Regenerate and verify in a fresh Python 3.12 virtual environment, then rerun the documented lint/type/test/coverage commands. Never install global packages or download model weights for this project.

## Main checkpoint and continuation — 6 October 2026

The user requested the reviewed checkpoint on private `main`, then a fresh local implementation chat. Verify `git status`, `git log` and origin refs; continue in this existing folder so ignored `.env`, samples and cost ledger remain available. Start further implementation on a `codex/` branch after inspection. The runtime wheel excludes `backend/tests`; synthetic adapters are test support only. Concurrent readiness probes use distinct private files.

The separate cost comparison is generated privately under `reports/cost-comparison/` from evaluation evidence; see [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md). Preserve uncertain budget holds and historical outputs. This operational checkpoint performs no provider inference and does not change access settings.
