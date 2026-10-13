# Local setup and operation

## Existing installation

Preserve the existing `.env`, `.local/providers.json`, data directory, phone data and signing identities. Use the current private launcher/source deployment; do not start a second backend or reinstall/uninstall the phone to check connectivity. The active deployment path is documented in `AGENTS.md`.

Open `http://127.0.0.1:8000/admin` on the Mac. Read-only checks use the local CLI:

```sh
.venv/bin/scanpay health
.venv/bin/scanpay profiles
```

These commands do not submit an invoice. Configuration is loaded at startup; inspect owner and queued/running work before any separately requested restart. Avoid `--reload` or multiple Uvicorn workers against the same data directory.

## Fresh backend checkout

Requires Python 3.12. From the repository root:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

Create a private root `.env` with a random `SCANPAY_TOKEN` and the required credentials. `.env.example` documents supported field names; do not copy it over an existing environment. The following initializer creates only missing starter files and never prints the token:

```sh
.venv/bin/python - <<'PYSETUP'
import os
from pathlib import Path
from secrets import token_urlsafe
files = {
    '.env': 'SCANPAY_TOKEN=' + token_urlsafe(32) + '\nSCANPAY_DATA_DIR=.local/backend\nSCANPAY_PROFILES_FILE=.local/providers.json\n',
    '.local/providers.json': Path('providers.example.json').read_text(),
}
for name, content in files.items():
    path = Path(name)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not path.exists():
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as file:
            file.write(content)
PYSETUP
```

Profiles in shipped examples start disabled. Configure and deliberately enable compatible methods using the [provider guide](PROVIDERS.md). Startup, health, profile listing and offline tests need no provider inference.

Start one backend:

```sh
.venv/bin/scanpay-serve
```

The managed macOS launcher keeps `127.0.0.1:8000` available and follows usable private/link-local IPv4 interfaces without restarting jobs. Admin **Connection** advertises successfully bound addresses, refresh state and warnings. Interface discovery failure retains the previous listener state with a warning; a failed bind is excluded and retried.

## Credentials

| Service | Private environment fields |
| --- | --- |
| API clients | `SCANPAY_TOKEN` |
| Hosted inference | The provider key fields in `.env.example` |
| AWS Textract | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`, plus `AWS_REGION` |
| Google Document AI | `GOOGLE_CREDENTIALS_JSON` plus configured project/location/processor fields |

AWS explicit key fields take precedence over SDK profile lookup. Populate both key fields; partial explicit credentials fail without fallback. A session token is for temporary credentials.

Google inline JSON accepts authorized-user or service-account credentials, loaded in memory for OAuth authentication. It is not a Gemini API key. Encode embedded private-key newlines as JSON `\n` within a single-quoted dotenv value. Malformed/unsupported explicit JSON and refresh failures are redacted and do not fall back to another identity. Native SDK-store lookup remains available only when explicit fields are absent.

Keep secrets out of source, request options, URLs, terminal arguments and logs. Region/endpoints and data-terms readiness belong to provider configuration; billing notes and verification evidence stay private.

## iPhone hotspot

1. Enable Personal Hotspot on the iPhone; connect the Mac and keep it awake.
2. In Mac admin **Connection**, copy the current Mac address.
3. On the phone, open **Connection → Hotspot → Mac address**, paste it, enter the existing local API token and tap **Reconnect**.
4. Allow local-network access when prompted. Update the address when the Mac IP changes.

There is one saved address, with no USB/cloud selector or automatic discovery. The phone's `localhost` points to the phone. Reconnect makes authenticated reads; it does not send a capture or confirm a draft. See [native build instructions](../ios/README.md).

## SUNMI and browser inspection

The same backend serves `/demo`. **Connection → Demo displays** on the phone enables sanitized telemetry; the SUNMI follows the matching phone session. Connection credentials are entered in the companion and stored in Android Keystore. See [installation/display placement](../sunmi/companion/README.md).

Admin holds its token in memory only. Confirmed edits, uploaded mobile images and retained provider outputs are private authenticated reads. No separate admin/display frontend server or build is required.

## CLI extraction and recovery

After selecting an authorized image/profile scope, an explicit upload can use:

```sh
.venv/bin/scanpay upload /path/to/invoice.png --profiles PROFILE_ID --key NEW_STABLE_REQUEST_KEY
.venv/bin/scanpay get scan_REPLACE_WITH_RETURNED_ID --wait
```

`--mode compare --profiles PROFILE_A PROFILE_B` runs independent methods; `all_enabled` resolves a snapshot of eligible configured profiles. `--no-wait` returns after acceptance. Routine output shows safe status; full responses are saved privately under `.local/client/`.

Recover uncertain acceptance with the same original bytes, options and key. A new key intentionally starts new potentially billed work. Never retry a timed-out/interrupted job automatically. Deleting terminal scans removes local artifacts/reviews and retains the minimal idempotency tombstone; it does not erase source samples, client exports or provider-held data.
