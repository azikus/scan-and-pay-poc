# Live display frontend

The backend serves `/demo` with local fonts, logo and QR. These compatibility route names represent real live telemetry; the shipped view has no synthetic playback or fabricated sessions.

`state.js` projects independent phone/backend state. `demo.js` owns authenticated fetch-streaming, polling fallback, controls, circular stage illustrations and rendering. Provider/document metadata is rendered through text nodes. No separate frontend build is needed.

## Behavior

Each SSE connection begins with a complete authoritative snapshot. Stream loss freezes the last backend state; a missing phone heartbeat gives an independent paused/disconnected state. Prior journeys are excluded from the current view. Timings stop at terminal state and freeze on disconnect.

Technical views show actual observed stages; a hybrid adds separate OCR and interpretation nodes. Provider labels use frozen scan/stage metadata rather than the newer global selection. Repeated heartbeats are coalesced. No remote percentage is invented.

Customer summaries show masked placeholders, never invoice/edit values. Completion is driven only by a successful saved review; provider responses/failures cannot celebrate. Reduced Motion stops repeating/spatial effects.

Controls → Next scan reads `/v1/profiles` and writes the exact ID/version to `/v1/admin/selection`. This applies only to new Sends and is shared with admin. Refresh/reopening Controls rereads it. Reconnect restores authenticated observation and cannot submit a scan.

## Checks and host

```sh
node --test frontend/demo/state.test.mjs
node --check frontend/demo/demo.js
```

Serve through the authenticated backend; file URLs are unsupported. Exercise layouts at 1280 × 720, 1280 × 800 and 1920 × 1080, keyboard controls, reduced motion, hybrid/error/completion states and reconnect using isolated fixtures. [SUNMI host](../../sunmi/companion/README.md) handles dual-panel placement and Keystore credentials.
