# SUNMI live companion

First implementation, 13 October 2026. Package `com.azikus.scanpay.companion` is separate from both the accepted offline display test and the future Android capture app. The backend and phone changes must be deployed together before using live mode. Installed on the physical SUNMI and mobile phone on 13 October; live idle/heartbeat and QR rendering are verified. See the installation record below for the checks completed and remaining rehearsal items.

## Build and launch

From the repository root, with Java and the local Android SDK (platform 33, build-tools 36.0.0):

```sh
bash sunmi/companion/build.sh
adb install -r sunmi/companion/build/companion.apk
bash sunmi/companion/launch.sh
```

The ADB launch script discovers the attached presentation display; do not hardcode a display ID. SUNMI exposes its USB customer screen as a restricted display: launching another activity there from an ordinary app fails with a security exception. The existing public launcher therefore renders its own companion window directly, placed by the authorized ADB shell. The other activities remain private. The script stops with a clear message when no secondary display exists. The display windows are fullscreen and keep their own display awake. No boot receiver, device-owner provisioning or kiosk lockdown is installed. Run the ADB launch script again after a reboot or customer-display reconnection. The ordinary app icon opens on the current display and does not reliably place the customer window. Build outputs and the local development signing key are ignored. Preserve `.local/sunmi-companion/debug.keystore` when updating an installed build, or supply its path through `SUNMI_SIGNING_KEY`; do not commit it. The app has no backup and requests only Internet access.

Enter the backend’s private HTTP base URL and existing local access token in **Backend connection**. Use the address from the backend admin Connection panel; localhost on the SUNMI refers to the SUNMI itself. The address is configurable, never embedded in the APK. Tokens are encrypted with an Android Keystore AES/GCM key and delivered only to the controlled local page. Browser storage is disabled. WebView accepts GET requests for the configured origin’s demo shell/assets, snapshot/stream and profile catalogue. The only allowed mutation is PUT to `/v1/admin/selection`, authorized for the Next scan controls. Scan submission and confirmation remain blocked by its request allowlist. Provider keys remain on the backend. Android Back reopens native connection settings if the page cannot load.

## Operator flow

1. Keep the existing single backend owner. Apply the source update only when no extraction is active; do not start a second process against its data directory. Preserve the original environment, provider config, selected profile, ledger and pending drafts.
2. Install the updated iPhone app with its existing bundle ID and signing identity. In **Connection**, enable **Demo displays**. Match its eight-character phone session label in the display's **Controls → Follow mobile phone session**.
3. **Vision Pro mode** is the default: AirScreen owns the larger display; the compact journey and idle QR occupy the smaller display. The initial launcher leaves the main display alone. Connect the headset through AirScreen as in the accepted setup.
4. **Scan & Pay mode** opens the full journey on display 0 and changes the smaller panel to customer status. Returning to **Vision Pro mode** closes the full journey activity and opens AirScreen's launch activity. Reconnect headset mirroring if needed; seamless stream preservation during this switch is not yet physically verified.
5. **Reconnect** reconnects the live feed. **Clear followed session** clears the selection on both native views without touching phone drafts or backend jobs. There is no synthetic playback mode.

An absent/paused phone is not idle. Heartbeats arrive every eight seconds while the app is foreground; after 30 seconds without one the QR and active motion stop. A broken backend stream is detected within approximately 14–15 seconds; polling falls back to a 500 ms interval between completed requests. Deliberate phone backgrounding sends a best-effort paused update and stops heartbeats. Turning telemetry off stops updates; the display ages out after the heartbeat timeout. Successful simulated confirmation briefly shows “Scan complete — no payment made”, then the idle QR. No payment integration is added.

The QR points exactly to https://www.azikus.com/scan-and-pay-poc. That external static site remains independent. No invoice pixels, raw JSON, actual recipient, amount, bank/reference values, edit keystrokes or provider credentials enter the companion channel.

## Browser access

Open the actual backend’s `/demo` page (locally, `http://127.0.0.1:8000/demo`), enter the existing access token and choose the mobile phone session. The token stays in memory and must be entered again after reload. `?view=technical`, `?view=compact` and `?view=customer` select layouts; no token belongs in URLs. The old standalone server on port 8769 was removed and stopped.

## Historical verification recorded 13 October (before live-only cleanup)

- 698 offline backend tests passed. Backend coverage: 96.53% statements / 90.91% branches; backend plus evaluation: 95.43% / 90.33%. Network sockets are blocked in this suite.
- Observer checks cover ordering, duplicate acceptance, late previous-journey results, immutable bindings, bounded retention, restart interruption, snapshot streaming, invalid/unauthorized payloads, sanitized projection, timeout and observer failure isolation. No added dispatch occurs on observation.
- 29 native unit/recovery tests passed, including legacy pending-record decoding, frozen journey bindings and successful review/confirmation during telemetry outage. Four existing synthetic UI tests passed in the first complete simulator run.
- Four frontend projection tests passed; static checks and the Android APK build/signature verification passed. Installed-wheel serving passed from a temporary directory outside the checkout.
- Browser checks at 1280 × 800 and 1920 × 1080 covered the technical layout, labelled replay and authenticated idle QR. The isolated SSE stream delivered synthetic phone heartbeats; the browser console had no errors during those checks.
- The accepted older AirScreen/offline-shell hardware test remains recorded in [display-test](../display-test/README.md). It does not establish physical acceptance of this new networked package.

Still required on the physical setup: install/configure the new shell and updated phone against the idle updated backend; verify live WebView SSE or polling, both panel placements, both mode transitions, AirScreen reconnection, token persistence and app/device relaunch, network loss/recovery, backgrounding, failed confirmation, QR scan at room distance, reduced-motion preference and update latency. No under-500-ms display measurement is claimed. Real extraction requires Markus’s explicit Send. The dated offline implementation checks made no paid calls; installation and the runtime switch are recorded below.


## Physical installation — 13 October

Markus authorized installation on the Wi-Fi-connected SUNMI and existing iPhone. Before deployment, current main plus invoice-context and explicit cloud-credential support were integrated (source merge `0a8190f`) to preserve the running feature set. The integrated source passed 775 backend tests, 32 native unit/recovery tests, four frontend projection tests, Ruff and Android build/signature verification. The signed iPhone build succeeded with the existing bundle and team.

The idle backend was switched to this worktree using the existing private launcher, environment and data directory. All 32 profile definitions, selected OpenAI mini profile and backend identity were unchanged. Baseline accounting was 2,379 reservations. A read-only SQLite backup, per-table fingerprints, configuration hashes and phone data backup are retained privately under the original checkout’s `.local/sunmi-install-2026-10-13/`. No pending phone draft was present in Application Support at backup time. Never archive this source worktree while the live launcher refers to it.

The existing mobile app was upgraded without uninstalling it. One-time development setup enabled **Demo displays** and connected to the current hotspot backend; the phone reported idle with regular heartbeats. The new SUNMI package was installed alongside AirScreen and the old offline test. The discovered smaller display was ID 2 at this checkpoint, 1280 × 800. An app-owned PixelCopy image verified the actual WebView showing **Live · Mobile connected** and the idle website QR. AirScreen was opened on display 0. No invoice pixels or headset image were captured.

During initial installation, the now-removed `SUNMI_DEVELOPMENT_SETUP=1` variant supplied temporary device setup and app-owned capture helpers. This paragraph records that historical setup, not current build support. Authorized ADB `run-as` can place an internal `files/connection-setup.json` containing `origin`, the existing local `token`, and optional followed `session`. This file is consumed/deleted before validation and the token is stored encrypted with Android Keystore. The ordinary build does not enable this path. Never put tokens in command arguments, source, APK assets, URLs or logs. The iOS DEBUG-only one-time setup similarly accepts optional `demoDisplays: true`. Both device setup files were consumed during installation. The development variant also accepts `--ez capture true` on launch to save only its own sanitized window internally; ordinary launches do not capture.

Physical launch revealed and fixed the restricted-display activity handoff failure. Existing export boundaries were preserved. Relaunch using `bash sunmi/companion/launch.sh`; choose the desired mode in **Controls**. Mode transitions, headset continuity, network recovery and measured visual latency still require physical rehearsal. Markus performed one live scan and confirmed: “Yes, it followed correctly; I dismissed the result.” Observed states were crop → preview → preparing/uploading → backend accepted/running/request → response/validation/completed → review → idle. The SUNMI followed and restored the QR. One reservation was added (2,380 total); every original accounting row, prior review, selection and backend identity was verified unchanged, as were environment/provider-file hashes. This rehearsal did not exercise Pay → Confirm or mode switching with a live headset stream. Backend observation itself sends no extraction request.


## Illustrated flow and provider selection update — 13 October

The installed companion now has circular illustrated technical journeys and **Controls → Next scan → Method / Provider / model → Use for next scan**. This updates the shared backend selection for a new mobile Send; it does not modify any existing scan or pending draft. The same UI works in an authenticated browser. Opening Controls refreshes the selection. Live OpenAI mini selection and private records were preserved during this update; test writes used only an isolated fake backend.

The public launcher restores the saved Scan & Pay main-screen activity when relaunched. The installed device’s saved Scan & Pay mode was retained. The now-removed debug-only own-window capture verified both companion activities and their controls without capturing AirScreen or other apps. Native manifest exports and permissions are unchanged. Actual WebView checks caught and fixed unsupported SVG arrow-marker colouring and the main panel’s effective CSS-height constraint. Backend restart and mobile reinstallation were not required for this display update.


## Live-only deployment — 13 October

Removed synthetic replay and all fabricated sessions/provider events from the shipped webpage. Removed the Android development bootstrap, capture intent handling, PixelCopy helpers and debuggable build option. The clean APK is installed as an in-place update with the same signing identity, encrypted access token, followed session and saved display mode. Its generated test captures were removed. Normal **Backend connection** settings remain available for setup; no provider keys are stored on the display.

The obsolete `com.azikus.scanpay.displaytest` package was uninstalled, its source removed (dated README retained), and the isolated rehearsal process on port 8769 stopped. The live backend was not restarted. All live routes and persistent session identifiers were retained for compatibility with the installed mobile app. The existing mobile setting is still called **Demo displays** and enables real telemetry; the separate simulated payment flow and offline regression fixtures are unchanged.

Verification: six frontend checks and 23 backend review/demo tests pass; the APK builds with no `application-debuggable` flag and no removed bootstrap/capture methods in its DEX. Live provider selection and private state are preserved. No agent inference was performed.
