#!/bin/bash
set -euo pipefail
adb_tool="${ANDROID_HOME:-$HOME/Library/Android/sdk}/platform-tools/adb"
device="${DISPLAY_SERIAL:-${SUNMI_SERIAL:-}}"
if [ -z "$device" ]; then
  devices="$("$adb_tool" devices | awk '$2 == "device" {print $1}')"
  count="$(printf '%s\n' "$devices" | awk 'NF {n++} END {print n+0}')"
  if [ "$count" != 1 ]; then
    printf 'Connect one display device using ADB, or set DISPLAY_SERIAL to its ADB serial.\n' >&2
    exit 1
  fi
  device="$devices"
fi
display="$("$adb_tool" -s "$device" shell dumpsys display | sed -n '/mBaseDisplayInfo=.*FLAG_PRESENTATION/s/.*displayId \([0-9]*\).*/\1/p' | head -1)"
if [ -z "$display" ]; then
  printf 'No secondary presentation display found. Check that the smaller panel is connected.\n' >&2
  exit 1
fi
printf 'Opening live companion on display %s\n' "$display"
"$adb_tool" -s "$device" shell am start --activity-clear-top --activity-single-top --display "$display" -n com.azikus.scanpay.companion/.LauncherActivity "$@"
