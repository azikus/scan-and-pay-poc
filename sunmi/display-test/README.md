# SUNMI + Vision Pro two-screen test

**Retired 13 October 2026:** Markus requested removal of demo-only code after accepting the live companion. This prototype’s source and installed APK have been removed; the original source remains recoverable in Git history. Instructions below are a dated hardware test record and are no longer runnable from the current checkout. Use [the live companion](../companion/README.md) instead.


## Ready-to-run setup

Prepared on 12 October 2026 on Markus's SUNMI D3 PRO, Android 13. AirScreen 2.16.1 is installed. The companion APK is installed as `com.azikus.scanpay.displaytest` and launched on the smaller panel.

| Panel | Current role |
| --- | --- |
| Larger, 1920 × 1080, Android display 0 | AirScreen / Vision Pro mirror |
| Smaller, 1280 × 800, Android display 7 at this checkpoint | Offline Azikus webpage with static QR and synthetic progress controls |

The smaller panel is exposed by SUNMI's USB-display service. Its display ID can change when it reconnects. The launch script discovers its current presentation display instead of hardcoding 7. Android reports separate content and touch routing for the two panels. No global display, security, sleep or network settings were changed; the companion requests keep-awake only for its own visible window.

## Run the physical test

1. Keep SUNMI and Vision Pro on the same network. AirScreen should be open on the larger panel; the smaller panel should show the QR and an advancing clock/uptime.
2. On Vision Pro, open Control Center → **Mirror My View** and select the same AirScreen receiver that already worked. Reconnect if the previous stream ended during setup.
3. With the live view playing on the larger panel, tap **Run sample journey** on the smaller panel. It cycles eight synthetic stages, four seconds each, then restores the QR. Moving symbols and pulses are illustrative, not real extraction progress.
4. Watch the headset view while the sample runs. Move a window or look around to confirm that video continues updating, rather than just showing a frozen frame. Check that the smaller panel's clock keeps advancing.
5. Tap **Next stage** to stop automatic playback and advance manually; tap **Show QR** to reset. Verify that touches on the smaller panel do not trigger AirScreen controls on the larger panel.
6. Stop and restart Vision Pro mirroring. The smaller webpage should remain present and responsive while AirScreen handles disconnect/reconnect. Finally scan the QR with a phone and verify the destination.

Success: live Vision Pro video and the independent webpage both continue updating, smaller-screen touches remain local, and reconnect does not displace the companion. If interacting with one panel stops the other, note exactly which step caused it; lifecycle/focus behaviour needs adjustment before a presentation claim.

There is no need to send an invoice. The app requests **no Android permissions**, has no network access, and contains no provider/API credentials. It has no code to initiate extraction, confirm drafts or make payments. The QR links exactly to `https://www.azikus.com/scan-and-pay-poc`; that separate website is unchanged. All progress animations are labelled synthetic.

## Restart from the Mac

With wireless ADB connected, from the repository root:

```sh
bash sunmi/display-test/launch.sh
bash sunmi/display-test/launch.sh sample
bash sunmi/display-test/launch.sh next
```

`idle` is the default. The script targets the current secondary display and leaves AirScreen's activity untouched. If several ADB devices are connected, set `SUNMI_SERIAL` to the desired serial. If the app was stopped, use this script to place it correctly; launching its ordinary app icon may put it on the larger screen.

The companion does not start automatically on boot. Reconnect ADB and run the launch script after a restart. Closing the companion releases its own keep-awake request. An optional removal command is `adb uninstall com.azikus.scanpay.displaytest`; uninstalling it does not remove AirScreen.

## Rebuild and install

Requires the existing JDK, Android SDK platform 33 and build-tools 36.0.0. No Gradle/plugin download is needed. `ANDROID_HOME` can override the SDK directory.

```sh
bash sunmi/display-test/build.sh
adb install -r sunmi/display-test/build/display-test.apk
bash sunmi/display-test/launch.sh
```

The generated APK and compiler outputs stay in ignored `build/`. The local development signing key stays in ignored `.local/sunmi-display-test/`. It is a debug test key, not a release identity. Preserve it for subsequent APK updates. Use `adb -s SERIAL install -r …` when several devices are present.

Bundled assets are the reviewed Azikus white logo, Hanken Grotesk Regular/Semibold and their OFL license. Hanken is the disclosed fallback for ABC Monument Grotesk. The static QR was generated with Core Image and decoded with Vision to verify its exact destination. `generate-qr.swift` can regenerate it on macOS; the checked-in PNG lets ordinary rebuilds avoid native image-renderer dependencies.

For layout verification only, launch with `--ez capture true`. The app uses PixelCopy to capture **its own synthetic window**, then writes `display-test.png` in its app-specific external files directory. It does not capture AirScreen or the headset view. Ordinary launches do not capture anything. Example:

```sh
adb shell am start --display DISPLAY_ID -n com.azikus.scanpay.displaytest/.DisplayTestActivity --es test_mode idle --ez capture true
adb pull /sdcard/Android/data/com.azikus.scanpay.displaytest/files/display-test.png /private/tmp/display-test.png
```

## Verification and remaining acceptance

Verified: APK builds and signature checks pass; installed package has no requested permissions; Android launches the companion on display 7; both panel content stacks and separate touch routing are present. PixelCopy captures at 1280 × 800 were visually inspected for the idle QR and animated journey. Shell syntax and whitespace checks pass. The original application/runtime, selection, ledger and approved deck were untouched.

**Physical acceptance confirmed by Markus on 12 October 2026:** after running the combined test, Markus reported “yup everything works.” The Vision Pro stream and smaller-screen companion work together. This is user-reported physical acceptance, in addition to the Android/window and layout checks above; it is not a measured latency or extended stability result.

The active mirror had returned to AirScreen's receiver activity during initial setup, before this accepted combined test; no cause is asserted. Keep reconnect/relaunch checks in future rehearsals.

This slice does not implement live mobile/backend events, automatic mode switching or the complete presentation controller. Those follow [the implementation plan](../../docs/SUNMI_DEMO_IMPLEMENTATION_PLAN.md) after the hardware test.
