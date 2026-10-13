#!/bin/bash
set -euo pipefail
task_root="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$task_root/../.." && pwd)"
sdk_root="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
build_tools="$sdk_root/build-tools/36.0.0"
platform="$sdk_root/platforms/android-33/android.jar"
output="$task_root/build"
mkdir -p "$output/classes" "$repo_root/.local/sunmi-display-test"
if [ ! -f "$task_root/assets/qr.png" ]; then
  swift -module-cache-path "$output/swift-cache" "$task_root/generate-qr.swift" "$task_root/assets/qr.png"
fi
javac --release 8 -classpath "$platform" -d "$output/classes" "$task_root/src/com/azikus/scanpay/displaytest/DisplayTestActivity.java"
find "$output/classes" -name '*.class' -print > "$output/classes.list"
"$build_tools/d8" --min-api 26 --lib "$platform" --output "$output" @"$output/classes.list"
"$build_tools/aapt" package -f -M "$task_root/AndroidManifest.xml" -I "$platform" -A "$task_root/assets" -F "$output/unsigned.apk"
(cd "$output" && "$build_tools/aapt" add unsigned.apk classes.dex)
"$build_tools/zipalign" -f 4 "$output/unsigned.apk" "$output/aligned.apk"
signing_key="$repo_root/.local/sunmi-display-test/debug.keystore"
if [ ! -f "$signing_key" ]; then
  keytool -genkeypair -keystore "$signing_key" -storepass android -keypass android -alias androiddebugkey -dname 'CN=Scanpay Display Test,O=Azikus,C=HR' -keyalg RSA -keysize 2048 -validity 3650
fi
"$build_tools/apksigner" sign --ks "$signing_key" --ks-pass pass:android --key-pass pass:android --out "$output/display-test.apk" "$output/aligned.apk"
"$build_tools/apksigner" verify "$output/display-test.apk"
printf 'Built %s\n' "$output/display-test.apk"
