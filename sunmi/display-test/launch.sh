#!/bin/bash
set -euo pipefail
task_root="$(cd "$(dirname "$0")" && pwd)"
adb_tool="${ANDROID_HOME:-$HOME/Library/Android/sdk}/platform-tools/adb"
mode="${1:-idle}"
case "$mode" in idle|sample|next) ;; *) printf 'Usage: bash launch.sh [idle|sample|next]\n' >&2; exit 1;; esac
device="${SUNMI_SERIAL:-}"
if [ -z "$device" ]; then
  devices="$("$adb_tool" devices | awk '$2 == "device" {print $1}')"
  count="$(printf '%s\n' "$devices" | awk 'NF {n++} END {print n+0}')"
  if [ "$count" != 1 ]; then
    printf 'Connect one SUNMI using ADB, or set SUNMI_SERIAL to its ADB serial.\n' >&2
    exit 1
  fi
  device="$devices"
fi
display="$("$adb_tool" -s "$device" shell dumpsys display | sed -n '/mBaseDisplayInfo=.*FLAG_PRESENTATION/s/.*displayId \([0-9]*\).*/\1/p' | head -1)"
if [ -z "$display" ]; then
  printf 'No secondary presentation display found. Check that the smaller panel is connected.\n' >&2
  exit 1
fi
printf 'Opening offline companion on display %s\n' "$display"
"$adb_tool" -s "$device" shell am start --display "$display" -n com.azikus.scanpay.displaytest/.DisplayTestActivity --es test_mode "$mode"
