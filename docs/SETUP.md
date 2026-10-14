# Local setup and operation

## Existing installation

Preserve the existing `.env`, `.local/providers.json`, data directory, phone data and signing identities. Use the configured private launcher/source deployment; do not start a second backend or reinstall/uninstall the phone to check connectivity. The active deployment path is documented in `AGENTS.md`.

Open `http://127.0.0.1:8000/admin` on the API host. Read-only checks use the local CLI:

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

Profiles in shipped examples start disabled. Configure and deliberately enable compatible methods using the [profile configuration](DEVELOPMENT.md#providers-and-extraction-profiles). Startup, health, profile listing and offline tests need no provider inference.

Start one API service with the portable ASGI entry point. Replace `SERVER_PRIVATE_IP` with the host's actual private network address; use `127.0.0.1` for same-host inspection only:

```sh
.venv/bin/python -m uvicorn backend.api:create_app --factory \
  --host SERVER_PRIVATE_IP --port 8000 --workers 1 --no-access-log --no-proxy-headers
```

The client needs a reachable address and bearer token, not a particular host vendor or tethering topology. Host firewall/network permissions must allow the intended private connection. This is a local deployment; public hosting is outside this setup.

An optional `scanpay-serve` launcher provides automatic listener updates using `/sbin/ifconfig` discovery for physical `en*` interfaces. It keeps loopback plus usable private/link-local listeners without restarting jobs. Other compatible hosts use the ASGI command with an explicit bind address. Manual startup reports `automatic=false`; admin Connection displays the actual private listener address. Automatic discovery failure retains previous listeners with a warning, while a failed bind is excluded and retried.

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

## Client networking

1. Put the API host, mobile client and display client on a reachable shared private network.
2. Copy the server base URL from admin Connection, or use the explicitly configured private bind address.
3. Enter that URL and the existing local bearer token in the client's Connection settings, then Reconnect.
4. Allow local-network access when prompted and update the saved URL when the server address changes.

The mobile client stores one private server address, without automatic discovery or a public/cloud endpoint selector. The connection settings use a hotspot label; any reachable shared private network is supported. The host and client need compatible network settings. A client's localhost is not the API host. Reconnect makes authenticated reads and does not submit a capture or confirmation.

## Display and browser inspection

The same backend serves `/demo`. **Connection → Demo displays** on the phone enables sanitized telemetry; the display follows the matching phone session. Connection credentials are entered in the companion and stored in Android Keystore. Installation/display placement is below.

Admin holds its token in memory only. Confirmed edits, uploaded mobile images and retained provider outputs are private authenticated reads. No separate admin/display frontend server or build is required.

## Native client build and tests

The app requires iOS 18+. Open `ios/ScanAndPay.xcodeproj` and build scheme `ScanAndPay`. `ios/project.yml` is the XcodeGen source; regenerate from the repository root only when needed:

```sh
xcodegen generate --spec ios/project.yml
```

Select the existing signing team, connect/unlock/trust the physical phone and enable Developer Mode. Upgrade in place: preserve bundle ID `com.azikus.scanpay.poc`, Keychain and Application Support. Team/provisioning credentials are not committed.

For offline native tests, choose an available simulator:

```sh
xcrun simctl list devices available
xcodebuild -project ios/ScanAndPay.xcodeproj -scheme ScanAndPay \
  -destination 'platform=iOS Simulator,id=SIMULATOR_UUID' \
  -derivedDataPath .local/ios-build CODE_SIGNING_ALLOWED=NO test
```

Use `-synthetic-preview` only for the bundled offline fixture flow; remove it for real capture/networking. Fixture timing is not provider performance. Hanken Grotesk is the licensed fallback for ABC Monument Grotesk; the OFL stays with native Resources.

## Display client build, connection and panels

Requires Java, Android SDK platform 33 and build-tools 36.0.0. From the repository root:

```sh
bash companion/build.sh
adb install -r companion/build/companion.apk
bash companion/launch.sh
```

`ANDROID_HOME` can override the SDK path. Preserve the installed signing key, or point `DISPLAY_SIGNING_KEY` to it; updates must keep the installed signing identity. Build outputs and keys are ignored. The ordinary APK has no debug setup/capture hooks.

The launcher uses one attached ADB device or `DISPLAY_SERIAL`, discovers the secondary presentation display and places LauncherActivity there. It does not hardcode secondary display IDs or control another application. Run it again after a reboot/customer-panel reconnect; the ordinary app icon cannot guarantee two-screen placement. There is no boot receiver/device-owner/kiosk provisioning.

Enter the advertised API URL and existing local bearer token in **Backend connection**. The address is configurable, never embedded in the APK. Android Back opens connection settings if loading fails. Enable phone **Connection → Demo displays** and select its matching short session on the display.

The primary panel always shows the technical system journey; the secondary panel shows customer status and the idle website QR. The launcher opens both application views using the saved connection/session data.

Display disconnection cannot fail a mobile extraction or confirmation. Next scan controls use the same persisted selection as admin and affect only new Sends. Internal isolation and WebView restrictions are documented in [Development](DEVELOPMENT.md#display-host).

## CLI extraction and recovery

After selecting an authorized image/profile scope, an explicit upload can use:

```sh
.venv/bin/scanpay upload /path/to/invoice.png --profiles PROFILE_ID --key NEW_STABLE_REQUEST_KEY
.venv/bin/scanpay get scan_REPLACE_WITH_RETURNED_ID --wait
```

`--mode compare --profiles PROFILE_A PROFILE_B` runs independent methods; `all_enabled` resolves a snapshot of eligible configured profiles. `--no-wait` returns after acceptance. Routine output shows safe status; full responses are saved privately under `.local/client/`.

Recover uncertain acceptance with the same original bytes, options and key. A new key intentionally starts new potentially billed work. Never retry a timed-out/interrupted job automatically. Deleting terminal scans removes local artifacts/reviews and retains the minimal idempotency tombstone; it does not erase source samples, client exports or provider-held data.
