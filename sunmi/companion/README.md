# SUNMI live companion

First implementation, 13 October 2026. Package `com.azikus.scanpay.companion` is separate from both the accepted offline display test and the future Android capture app. The backend and phone changes must be deployed together before using live mode. This source build has not yet been accepted on the physical SUNMI.

## Build and launch

From the repository root, with Java and the local Android SDK (platform 33, build-tools 36.0.0):

```sh
bash sunmi/companion/build.sh
adb install -r sunmi/companion/build/companion.apk
adb shell am start -n com.azikus.scanpay.companion/.LauncherActivity
```

The launcher discovers the attached presentation display; do not hardcode the previously observed ID 7. If no secondary display exists it uses the main display. Both activities are landscape, fullscreen and keep their own display awake. No boot receiver, device-owner provisioning or kiosk lockdown is installed. Launch the companion again after a reboot. Build outputs and the local development signing key are ignored. Preserve `.local/sunmi-companion/debug.keystore` when updating an installed build, or supply its path through `SUNMI_SIGNING_KEY`; do not commit it. The app has no backup and requests only Internet access.

Enter the Mac's private HTTP base URL and existing local access token in **Backend connection**. Use the address from the Mac admin Connection panel; localhost on the SUNMI is not the Mac. The address is configurable, never embedded in the APK. Tokens are encrypted with an Android Keystore AES/GCM key and delivered only to the controlled local page. Browser storage is disabled. WebView accepts GET requests only for the configured origin's demo shell/assets and read-only snapshot/stream endpoints. It cannot invoke scan submission or confirmation through its request allowlist. Provider keys remain on the Mac. Android Back reopens native connection settings if the page cannot load.

## Operator flow

1. Keep the existing single Mac backend owner. Apply the source update only when no extraction is active; do not start a second process against its data directory. Preserve the original environment, provider config, selected profile, ledger and pending drafts.
2. Install the updated iPhone app with its existing bundle ID and signing identity. In **Connection**, enable **Demo displays**. Match its eight-character phone session label in the display's **Controls → Follow mobile phone session**.
3. **Vision Pro mode** is the default: AirScreen owns the larger display; the compact journey and idle QR occupy the smaller display. The initial launcher leaves the main display alone. Connect the headset through AirScreen as in the accepted setup.
4. **Scan & Pay mode** opens the full journey on display 0 and changes the smaller panel to customer status. Returning to **Vision Pro mode** closes the full journey activity and opens AirScreen's launch activity. Reconnect headset mirroring if needed; seamless stream preservation during this switch is not yet physically verified.
5. **Synthetic replay** is explicit, labelled and local to that webpage. It sends no scan request. Select **Live** to resume observation. In this first version replay clocks are independent on the two panels; synchronized live state comes from the shared followed session. **Clear followed session** clears the selection on both native views without touching phone drafts or backend jobs.

An absent/paused phone is not idle. Heartbeats arrive every eight seconds while the app is foreground; after 30 seconds without one the QR and active motion stop. A broken backend stream is detected within approximately 14–15 seconds; polling falls back to a 500 ms interval between completed requests. Deliberate phone backgrounding sends a best-effort paused update and stops heartbeats. Turning telemetry off stops updates; the display ages out after the heartbeat timeout. Successful simulated confirmation briefly shows “Demo complete — no payment made”, then the idle QR. No payment integration is added.

The QR points exactly to https://www.azikus.com/scan-and-pay-poc. That external static site remains independent. No invoice pixels, raw JSON, actual recipient, amount, bank/reference values, edit keystrokes or provider credentials enter the companion channel.

## Rehearse without inference

Use an isolated, temporary backend with no profiles or provider adapters:

```sh
python sunmi/rehearse.py
```

Open `http://127.0.0.1:8769/demo` on the Mac and choose **Synthetic replay**. This requires no token. For testing authenticated lifecycle snapshots only, the isolated server's disposable test token is `synthetic-demo-access-no-private-data`; never use it for a backend with real data. `--host <Mac-private-IP>` permits a SUNMI network rehearsal. The server never reads the root `.env`, live database or provider configuration, and deletes its temporary state on a normal shutdown. It is deliberately unable to extract images. Stop it after rehearsal.

For an ordinary browser against the real local backend, use `/demo`, enter the existing local token and choose a phone session. The token stays in memory and must be entered again after reload. `?view=technical`, `?view=compact` and `?view=customer` select layouts; no token belongs in URLs. Browser view selections and replay are local to each tab.

## Verification recorded 13 October

- 698 offline backend tests passed. Backend coverage: 96.53% statements / 90.91% branches; backend plus evaluation: 95.43% / 90.33%. Network sockets are blocked in this suite.
- Observer checks cover ordering, duplicate acceptance, late previous-journey results, immutable bindings, bounded retention, restart interruption, snapshot streaming, invalid/unauthorized payloads, sanitized projection, timeout and observer failure isolation. No added dispatch occurs on observation.
- 29 native unit/recovery tests passed, including legacy pending-record decoding, frozen journey bindings and successful review/confirmation during telemetry outage. Four existing synthetic UI tests passed in the first complete simulator run.
- Four frontend projection tests passed; static checks and the Android APK build/signature verification passed. Installed-wheel serving passed from a temporary directory outside the checkout.
- Browser checks at 1280 × 800 and 1920 × 1080 covered the technical layout, labelled replay and authenticated idle QR. The isolated SSE stream delivered synthetic phone heartbeats; the browser console had no errors during those checks.
- The accepted older AirScreen/offline-shell hardware test remains recorded in [display-test](../display-test/README.md). It does not establish physical acceptance of this new networked package.

Still required on the physical setup: install/configure the new shell and updated phone against the idle updated backend; verify live WebView SSE or polling, both panel placements, both mode transitions, AirScreen reconnection, token persistence and app/device relaunch, network loss/recovery, backgrounding, failed confirmation, QR scan at room distance, reduced-motion preference and update latency. No under-500-ms display measurement is claimed. Real extraction requires Markus's explicit Send within the then-current approved allowance. No agent paid call, device migration or live runtime restart was performed for this implementation.
