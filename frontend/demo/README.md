# Live demonstration views

The existing authenticated backend serves `/demo`; the wheel bundles this directory under `backend/demo_assets`. No frontend build step or third-party runtime is needed. Local fonts, logo and the static QR are bundled. `state.js` is the pure phone/backend projection; `demo.js` owns authenticated fetch-streaming, polling fallback, controls, stage graph and labelled synthetic replay. It renders metadata using text nodes, with no provider/document HTML.

Run `node --test frontend/demo/state.test.mjs` for the reducer checks. Serve the actual backend or the isolated `python sunmi/rehearse.py` runner for browser tests; file URLs are not a supported deployment. See [setup and verification](../../sunmi/companion/README.md).

The initial snapshot on every SSE connection is authoritative; past transfers are not replayed as live. Read-only GETs cannot dispatch extraction. The last snapshot freezes on a backend connection failure; missing phone heartbeat yields a separate paused/disconnected state. Both technical layouts use actual observed external stages, so a hybrid adds separate OCR/interpretation nodes and local rules remain on the backend. Frozen profile IDs/versions are included in snapshots; provider/model labels come from actual stages, never the admin's newer next-scan selection.

`Synthetic replay` is independent of network state and must be explicitly selected. It never switches on automatically after a live failure. Live customer summaries contain static masked placeholders, not invoice or edited values. Assets and source are public shells; every data endpoint requires the existing bearer token. The external Azikus QR destination is unchanged.

Display copy uses platform-neutral system roles: **Mobile phone → Backend → Provider → Backend → Mobile phone**. Actual observed provider/model names are retained. Hardware-specific Mac/iOS instructions belong only in setup documentation.
