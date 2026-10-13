# SUNMI companion host

Package `com.azikus.scanpay.companion` hosts the [live webpage](../../frontend/demo/README.md) in a controlled-origin WebView across the SUNMI's two displays. The app requests Internet access, has no backup and keeps only its own visible windows awake. It contains no provider keys, scan-submission capability or payment confirmation API.

## Build and install

Requires Java, Android SDK platform 33 and build-tools 36.0.0. From the repository root:

```sh
bash sunmi/companion/build.sh
adb install -r sunmi/companion/build/companion.apk
bash sunmi/companion/launch.sh
```

`ANDROID_HOME` may override the default SDK path. Preserve `.local/sunmi-companion/debug.keystore` or supply the existing key through `SUNMI_SIGNING_KEY`; an update needs the installed signing identity. Build outputs/keys remain ignored. The normal APK has no debug bootstrap, window-capture helper or fabricated playback.

The launch script selects one attached ADB device or `SUNMI_SERIAL`, discovers the current secondary presentation display and places LauncherActivity there. It does not hardcode a display ID or force-stop AirScreen. SUNMI customer-display restrictions mean ordinary app-to-app activity placement is insufficient. Run the launcher after a reboot/customer-display reconnect; the regular app icon cannot guarantee two-screen placement. There is no boot receiver/device-owner/kiosk provisioning.

## Connection

In Backend connection, enter the advertised Mac base URL and existing local bearer token. `localhost` on SUNMI means SUNMI, not the Mac. The address is configurable, never embedded in the APK. Android Keystore AES/GCM protects the token; browser storage is disabled.

The WebView permits GETs to the configured origin's shell/assets, snapshots/stream and catalogue. Its only allowed mutation is PUT to `/v1/admin/selection` for Next scan. Scan submission/confirmation stay blocked. Android Back opens native connection settings if loading fails.

Enable Connection → Demo displays on the phone and select the matching short phone session. The telemetry is real and sanitized. Loss of display connection cannot fail a phone extraction or confirmation.

## Display modes

- **Vision Pro:** AirScreen receives headset mirroring on the main display, with the live customer view on the smaller panel. Connect both devices to the appropriate shared network and use the headset's Mirror My View control.
- **Scan & Pay:** a full technical journey on the main panel and customer status/idle QR on the smaller panel.

Choose in Controls; relaunch restores the saved main-screen mode. Public LauncherActivity renders its own window on the restricted customer display; the other activities remain private. No global display/security/network settings are changed.

## Live controls

Next scan selects the shared method/provider/model for a new phone Send; pending drafts keep their frozen selection. The display shows observed transport/runtime events, active stages, backend elapsed time and recent events. It hides invoice pixels/payment/edit values and never fabricates remote progress. Successful saved review triggers completion; reduced motion removes repeating effects.

The [API contract](../../docs/API_CONTRACT.md) describes snapshots/SSE and binding semantics. The [setup guide](../../docs/SETUP.md) covers the local backend/hotspot. Inspect layout and reconnect with isolated fixtures; do not submit live invoices just to test the display.
