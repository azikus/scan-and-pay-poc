# SUNMI live demo implementation plan

Revised 13 October 2026 around the physically tested two-screen arrangement. Implementation was subsequently authorized in a separate worktree on 13 October. The first source version and offline/browser checks are recorded in [the companion guide](../sunmi/companion/README.md); physical live integration remains open.

Already delivered: AirScreen 2.16.1 and the offline synthetic companion are installed on the SUNMI D3 PRO, Android 13. On 12 October Markus confirmed that simultaneous Vision Pro streaming and smaller-screen companion interaction work. See [setup and acceptance](../sunmi/display-test/README.md). This establishes hardware feasibility; it is not a measured latency or extended stability result. This earlier acceptance establishes only the offline hardware baseline; it does not establish physical acceptance of the new live controller.

## Agreed experience

Use the SUNMI as a two-display companion to the existing iPhone demo, with two manually selected presentation modes:

| Mode | Bigger screen: 1920 × 1080 | Smaller screen: 1280 × 800 |
| --- | --- | --- |
| Vision Pro — primary arrangement | Live Vision Pro view received by the existing AirScreen app | Compact animated technical journey during a scan; website QR while idle |
| Scan & Pay | Full animated technical journey | User status and masked payment summary during a scan; website QR while idle |

The default is Vision Pro mode. The companion follows the iPhone scan session; headset mirroring is a separate video feed, not a source of scan-state events. A headset stream can be active while the phone is idle and the QR remains visible.

The smaller screen shows a static QR while idle. Its exact destination is **https://www.azikus.com/scan-and-pay-poc**. That external website is independent of this project: no website edits, integration, session parameters or tracking are needed. The QR is a link to information, not a payment code or device-pairing code.

The existing iPhone retains capture, crop, explicit Send, review, edits and simulated Pay confirmation. The SUNMI observes the journey; it does not submit extraction jobs or execute payments. The approved reveal.js deck remains separate.

## Architecture decision

Build the visual experience as local webpages, hosted by the existing Mac backend and displayed through a small Android shell. Extend the proven `sunmi/display-test/` approach into a maintained companion. AirScreen continues to own video reception; do not implement another AirPlay receiver or relay video through the extraction backend.

In Vision Pro mode, the shell keeps the compact webpage on the smaller display and leaves AirScreen on the bigger one. In Scan & Pay mode, it presents the full journey on the bigger display and the customer view on the smaller one, sharing the same session-state model. Provide a deliberate operator mode switch and verify both directions physically; do not change mode automatically when AirPlay disconnects. Switching back to AirScreen may require the wearer to reconnect mirroring, so document the actual observed behaviour.

Proposed source locations:

| Location | Responsibility |
| --- | --- |
| `frontend/demo/` | Journey view, customer view, shared state reducer, animation, local fonts/artwork and QR |
| `backend/demo_events.py` | Sanitized session snapshots, event sequencing, reconnection and bounded retention |
| `backend/api.py`, `backend/runtime.py`, affected adapters | Additive event publication at actual lifecycle boundaries |
| `ios/ScanAndPay/ScanSession.swift`, `BackendClient.swift`, relevant views | Best-effort UI lifecycle events, session association and recovery |
| `sunmi/` | Dedicated Android display shell, panel placement, manual modes, protected connection settings and setup instructions |

Keep the SUNMI shell separate from `android/`, which remains the future Android capture/payment-draft client milestone. Reuse the existing Mac backend owner and authentication. Package demo frontend assets into the backend wheel using the existing admin packaging pattern. No second process should own the database.

The webpages must also work in ordinary Mac browsers for development, rehearsal and optional projector display. Native code owns only display placement, fullscreen behaviour, connection configuration and protected credential storage.

## Display content and motion

Markus’s 13 October copy clarification: display system roles as **Mobile phone** and **Backend**, rather than hardware/platform names. Keep actual provider/model labels. Device-specific setup instructions can still identify the physical Mac and iPhone.

The table below describes Scan & Pay mode. In Vision Pro mode the bigger screen remains the live headset feed throughout; the smaller screen shows a compact version of the technical journey below, including its current stage, actual provider/model and elapsed time. Before capture and after completion/reset it returns to the same static website QR.

| Observed stage | Larger screen: system journey | Smaller screen: user journey |
| --- | --- | --- |
| Idle, connected | Complete diagram, inactive nodes, “Ready for the next scan” | Static QR, “Explore Scan & Pay”, “Scan to learn more” |
| Photo captured / crop opened | Highlight iPhone, “Adjusting crop” | “Preparing your invoice”; QR fades away |
| Preview ready | Highlight iPhone, “Ready to send” | “Ready to send” |
| Upload started | Invoice icon travels iPhone → Mac | “Sending invoice” |
| Backend accepted / queued | Highlight Mac; show queue separately when relevant | “Invoice received” |
| Provider request dispatched | Data travels Mac → actual provider | “Reading invoice” |
| Awaiting provider response | Provider pulses; show elapsed wait | Calm processing animation |
| Provider response received | Structured-field symbols travel provider → Mac | “Preparing your draft” |
| Local validation | Highlight Mac, “Checking extracted fields” | “Preparing your draft” |
| Result received on phone / review opened | Highlight iPhone, “User reviewing details” | Masked summary and “Review on your phone” |
| Confirmation summary opened | “User checking confirmation” | “Confirm on your phone” |
| Confirmation saved | “Demo complete — no payment made” | Brief completion treatment, then QR |
| Failure, cancellation or disconnection | Accurate status at the affected node | Clear status; no successful completion animation |

Use the simple Mobile phone → Backend → Provider → Backend → Mobile phone layout for direct vision. Render OCR/rules and OCR → LLM as their actual stage graph, with correct recipient and model labels from the scan's resolved profile. Never animate an LLM step for an OCR/rules scan. The current admin choice describes the next scan; an active scan must continue displaying its own frozen profile.

Motion is explanatory: moving document/field symbols for transfers, a pulse while waiting, and a brief result assembly. Do not imply that symbolic particles measure network bytes. Upload percentage is shown only if measured by the client. No simulated provider percentage, token stream or internal reasoning. “Waiting for AI response” covers the unobservable remote interval; elapsed time is observable, internal model processing is not.

Fast stages may finish before their animation. Keep decorative motion brief and interruptible; immediately show the latest true stage. Do not slow extraction or build an animation queue that falls behind. On reconnect, restore the current state without replaying historic transfers as live activity.

Use the existing Azikus artwork and local Hanken Grotesk fallback, near-black/white foundations and restrained ice-blue highlights. Hanken is a fallback for the official ABC Monument Grotesk. Adapt diagrams to the actual display aspect ratios, preserve clear text at viewing distance and support reduced motion. Keep the QR static with a white quiet zone; its dot styling may follow Markus's supplied reference only after decoding and physical scan verification.

## Event and session model

Existing scan APIs expose queued/running/terminal states and stage diagnostics. They do not expose phone capture/crop/review activity, and there is currently no streaming endpoint. Add a separate, versioned demo channel rather than changing payment semantics or replaying inference.

Proposed endpoints, to be finalized in `API_CONTRACT.md` during implementation:

- Authenticated session creation and binding for one explicitly followed phone journey.
- An authenticated phone event endpoint for bounded, validated lifecycle events.
- An authenticated session snapshot endpoint containing current state and its revision.
- An authenticated event stream supporting a last-seen cursor and snapshot resynchronization.

Prefer SSE consumed through authenticated `fetch` streaming, allowing the bearer token in an Authorization header. Standard `EventSource` cannot set that header. Verify streaming support on the actual SUNMI WebView; support authenticated snapshot polling as a fallback. Do not put tokens into QR codes, URLs, browser history or event payloads. An initial snapshot and bounded event replay must come from one consistent revision boundary so events cannot be lost during subscription.

Each event has a schema version, unique event ID, session ID, server sequence, source, kind, server timestamp, optional client timestamp, scan/run/stage identifiers where applicable, and allowlisted metadata. Store no invoice images, raw provider bodies, field keystrokes or credentials in the event channel.

The phone creates or resumes a demo session before capture. Associate an accepted scan with that session through an additive validated request header or equivalent explicit binding. Keep extraction options, idempotency keys, original JSON and recovery records intact. Repeated upload acceptance binds the same scan; it does not dispatch again. A newly captured invoice receives a new journey identity.

Authority is explicit:

- Phone events describe UI activity, not extraction success. Emit crop cancellation, preview, upload, result receipt, review opening, confirmation opening and reset at their real transitions.
- Backend events describe queue, dispatch, response receipt, normalization/validation and terminal outcomes. Instrument the transport boundaries, not merely adapter creation; “response received” is distinct from “valid result.”
- Emit confirmation-saved only after the existing review endpoint has persisted the simulated confirmation. Do not infer it from a button tap.

Track phone state and backend state separately. Derive the display from both so a phone reset cannot falsely cancel a backend run that is still executing. Associate events with the active generation/scan and deduplicate them. Late events from an earlier scan cannot overwrite a newer journey. Never regress a terminal backend state because an older phone event arrived late.

Use bounded private session/event retention with a configurable expiry, independent of the original scan ledger and artifacts. Persist enough state for display reloads and backend restart recovery. Restarted interrupted jobs remain interrupted under the existing contract; no automatic rerun. Expired or unbound sessions display “Waiting for phone” until an actual fresh idle state is reported.

Telemetry must not block or fail capture, extraction, review or confirmation. Use bounded best-effort publication and reconnect with a current phone snapshot. Event-write errors are safe diagnostic failures, not extraction failures. Heartbeats distinguish a connected idle phone from an absent phone. Treat client timestamps as advisory; use existing monotonic timers for measured backend durations.

## Privacy, reliability and setup

Default both displays to a sanitized projection: generic recipient label, masked destination/reference, no invoice photo, no raw JSON and no full confirmed values. Summary rows may use placeholders where masking removes useful detail. Any later choice to reveal real values must be explicit and scoped. Synthetic previews can show useful example values and must be labelled synthetic.

Do not publish field-by-field edits in the first version. Show “Reviewing” and confirmation activity; the saved review may refresh the masked summary after confirmation. This preserves the current contract's separation of original extraction and confirmed edits.

Use existing authenticated local access, no-store data responses and self-hosted assets. The SUNMI shell stores credentials using platform-protected storage and provides them to the controlled page at runtime without putting them in persistent web storage. It allows only the configured local demo origin; provider keys stay on the Mac. Verify the phone and SUNMI can reach the same Mac on the chosen hotspot/LAN. Ethernet or Wi-Fi is a setup choice, not a presumed guarantee of reachability.

On connection loss, pause active motion and show “Connection lost — last known stage: …”. Do not silently return to the QR. Successful confirmation may retain completion for about four seconds before the QR returns; cancellation/reset may return directly. Backgrounding and loss of the phone heartbeat display a paused/disconnected state, not proof of idle. An operator may clear the followed display session without cancelling jobs, changing selection, deleting drafts or changing budget records.

Replay mode is an explicit operator choice backed by synthetic or sanitized saved events, labelled “Replay” throughout. It never dispatches provider requests. No automatic transition from a failed live scan into a successful replay.

## Delivery sequence and acceptance

| Step | Work | Done when |
| --- | --- | --- |
| 1 — Two-screen feasibility — complete | AirScreen installed; native shell displays a bundled webpage on the smaller panel; QR and synthetic journey rendered; Markus confirmed concurrent streaming and interaction. | Accepted physical setup is the baseline. Do not repeat installation or reopen the architecture spike. Network/authenticated live-feed checks remain part of integration. |
| 2 — Web experience | Refine the existing synthetic prototype into compact/full technical views and a customer view, with one reducer, idle QR and representative event traces. | Both modes fit the actual panels. All stages, errors and disconnected states are readable; QR scans at presentation distance; reduced motion works. |
| 3 — Backend events | Add sanitized session state, snapshot/stream/polling, dispatch/response/validation hooks and scan binding. | A fake provider drives truthful stages; reconnection/restart recovers state; malformed responses and timeout never animate success; ledger/inference behaviour is unchanged. |
| 4 — iPhone events | Add optional demo telemetry at real UI transitions and persistent journey association compatible with pending draft recovery. | Synthetic native flow matches the displays through crop, Send, review, confirmation, cancel/reset and recovery. Telemetry outage leaves the original flow usable. |
| 5 — SUNMI integration and operator controls | Extend the shell for authenticated local web content, automatic discovery of the attached panel, reliable startup, fullscreen and keep-awake. Add manual Vision Pro / Scan & Pay modes, live/replay choice and display-session reset; preserve the existing offline fixture. | Vision Pro streaming coexists with live progress. Both manual mode transitions and relaunch work; network loss is visible; credentials stay protected. Reset affects only the display session. |
| 6 — Rehearsal and closeout | Offline/fake end-to-end rehearsal, QR scan, failure/reconnect checks, documentation and usual checked source closeout. | Complete demo and recovery paths pass on the physical setup, with no new paid calls in implementation checks. Record actual verification and remaining gaps. |

Continue from the accepted hardware setup. The existing test app is offline and requests no permissions; live integration requires deliberate network access and protected connection configuration in the maintained shell. The visual work and fake-provider integration can proceed without paid inference. A real-invoice extraction rehearsal is separate: only an explicit user Send within the then-current authorized allowance, or renewed authorization if needed. Read actual live selection and budget at that time; do not copy a dated snapshot into runtime settings.

Required meaningful tests: session/scan association; duplicate and out-of-order events; late result isolation; replay/live separation; stream reconnect/expiry; malformed payloads and unauthorized access; masking; provider-stage success/error/timeout; telemetry failure isolation; pending-draft recovery; no added dispatch on observation or confirmation. Run the affected native tests and backend domain/contract checks, retain required coverage, and test installed-wheel serving outside the checkout.

Frontend/device checks must include both actual resolutions, room-distance legibility, reduced motion, measured QR readability, brief stages, a long provider wait, connection loss, phone backgrounding, incomplete draft and failed confirmation save. Rehearse live headset video alongside active scan progress, touch interaction, AirPlay reconnect, both mode switches and device/app relaunch. Observe that screen updates arrive promptly; use a practical target of under 500 ms after an event reaches the backend on the local network, measured separately from extraction latency. A fallback poll interval around 500 ms is a starting point to tune on-device, not a claimed result.

Implementation handoff updates: `API_CONTRACT.md`, `ARCHITECTURE.md`, `CURRENT_STATUS.md`, affected platform/frontend READMEs and a dedicated SUNMI setup/rehearsal guide. Preserve the approved presentation and external website. Coordinate iOS event hooks with the current in-progress iOS work instead of overwriting it. Do not expand the remaining Android mobile milestone into this display shell.

## References

- Current local basis: [status](CURRENT_STATUS.md), [handoff](CODING_HANDOFF.md), [API contract](API_CONTRACT.md), [roadmap](ROADMAP.md) and [presentation](../presentation/README.md).
- [Accepted SUNMI D3 PRO setup](../sunmi/display-test/README.md): actual device, panel configuration, build/launch instructions and physical acceptance. Panel IDs can change; discover them at runtime.
- [Android Presentation](https://developer.android.com/reference/android/app/Presentation): alternate separate-display content API. The accepted test uses an activity launched on the secondary display; retain that proven path unless integration shows a concrete need to change it.
- [Android WebView](https://developer.android.com/develop/ui/views/layout/webapps/webview): hosting the web interface inside the small shell.
