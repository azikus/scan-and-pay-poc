# Live demonstration views

The existing authenticated backend serves `/demo`; the wheel bundles this directory under `backend/demo_assets`. No frontend build step or third-party runtime is needed. Local fonts, logo and the static QR are bundled. `state.js` is the pure phone/backend projection; `demo.js` owns authenticated fetch-streaming, polling fallback, controls, stage graph and live controls. It renders metadata using text nodes, with no provider/document HTML.

Run `node --test frontend/demo/state.test.mjs` for the reducer checks. Serve the actual authenticated backend for browser checks; file URLs are not a supported deployment. See [setup and verification](../../sunmi/companion/README.md).

The initial snapshot on every SSE connection is authoritative; past transfers are not replayed as live. Read-only GETs cannot dispatch extraction. The last snapshot freezes on a backend connection failure; missing phone heartbeat yields a separate paused/disconnected state. Both technical layouts use actual observed external stages, so a hybrid adds separate OCR/interpretation nodes and local rules remain on the backend. Frozen profile IDs/versions are included in snapshots; provider/model labels come from actual stages, never the admin's newer next-scan selection.

Live customer summaries contain static masked placeholders, not invoice or edited values. Assets and source are public shells; every data endpoint requires the existing bearer token. The external Azikus QR destination is unchanged.

Display copy uses platform-neutral system roles: **Mobile phone → Backend → Provider → Backend → Mobile phone**. Actual observed provider/model names are retained. Hardware-specific Mac/iOS instructions belong only in setup documentation.


## Circular journey and next-scan controls — 13 October

The technical views arrange original vector illustrations of mobile phones, backend servers and provider processors around an elliptical path with directional arrows. Separate remote stages remain separate nodes; active hybrid stages are selected by their actual stage state. Moving transfer lines, processor activity, server lights, title transitions and completion emphasis follow the projected live state. No remote percentage or fabricated server progress is shown. Reduced-motion preferences remove repeating motion. Disconnection stops motion and clears the active highlight. The customer view retains its simpler status and idle QR.

**Controls → Next scan** loads the existing authenticated `/v1/profiles` catalogue. Only implemented, enabled and configured profiles can be chosen. Method and Provider / model lead to **Use for next scan**, which sends the exact ID/version to the existing `/v1/admin/selection` endpoint. It applies to new Sends from connected mobile phones; pending uploads and in-progress drafts keep their frozen settings. Opening controls or pressing Refresh re-reads the current selection. This global selection is shared with the admin.

Verification: six frontend projection/selection tests and 23 backend review/demo tests pass. A temporary backend with two synthetic providers verified save, persistence after refresh and replay isolation, without live provider calls. Browser layouts fit 1280 × 800 and 1920 × 1080. The physical SUNMI also uses 1280 × 720 CSS pixels for its 1920 × 1080 main panel; a compact-height rule prevents clipping there. App-owned PixelCopy verified actual WebView arrows/illustrations and the current provider controls. The current provider was not changed during deployment. A final read-only checkpoint found 2,381 live reservations; the agent submitted no live extraction, and historical accounting was not altered. Hanken remains the previously disclosed local font fallback.


## Live-only cleanup — 13 October

At Markus’s request, the shipped display has no synthetic playback, fabricated provider/session data, replay controls or rehearsal server. **Reconnect** reconnects to the authenticated live stream. The QR and animation are driven only by observed phone/backend state. Completion reads **Scan complete**. At Markus’s request the payment disclaimer was removed from both completion text locations; the underlying payment confirmation remains simulated.

The existing `/demo` and `/v1/demo/*` addresses, native persisted session keys and internal telemetry names are compatibility identifiers for the real live channel. Renaming them would break the installed mobile app or saved session bindings; they do not enable a simulation. Offline unit fixtures remain test-only. The dated replay/browser checks above describe historical implementation verification, not a retained feature.


## Display motion and mobile dark mode — 13 October

The live SUNMI views now animate outgoing/incoming titles, enlarge the circular component illustrations, and show an animated active component in the center. A right-hand panel shows the actual providers/models, observed backend elapsed time and four recent journey events. Heartbeat repetitions are coalesced; prior journeys are excluded; terminal backend timings stop and disconnected timings freeze. The customer view uses one large active illustration. Saved confirmation triggers a drawn checkmark, two expanding rings and 32 particles matching the mobile celebration; provider responses and failures cannot trigger it. Reduced Motion removes spatial/repeating effects. No synthetic playback or new data endpoint was added.

The native app now uses dark glass across capture, crop, preview, review, confirmation, settings and completion. Semantic text colours and the reversed Azikus mark preserve contrast; source document pixels are unchanged. The signed update was installed in place on the existing paired iPhone 16 Pro and the SUNMI companion was relaunched. Existing tokens, selected provider and stored drafts are retained. No backend restart or agent inference was needed.

Verification: seven frontend projection/selection/timing tests, isolated browser checks at 1280 × 720, 1280 × 800 and 1920 × 1080 (including hybrid stages, completion and reduced motion), and all four existing offline native UI flows pass. Native review/completion screenshots were inspected. Real-device confirmation animation acceptance remains for Markus’s next scan; no live confirmation was submitted by the agent.
