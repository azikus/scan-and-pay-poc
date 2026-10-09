# Local connection setup — 9 October 2026

Markus authorized this small connection improvement after the extracted-field sheets: add current Mac addresses/status to the admin and remove the manual backend restart when switching local networks. The initial presentation is next, in his next prompt/chat. No other development or presentation creation is part of this update.

Implementation and checked merge: [PR #5](https://github.com/azikus/scan-and-pay-poc/pull/5). Consult its actual status if resuming an interrupted closeout.

## Use it

1. On the Mac, open `http://127.0.0.1:8000/admin`, sign in with the existing token and expand **Connection** above Next scan. This loopback URL remains usable when Wi-Fi changes.
2. Copy the displayed **Wi-Fi / hotspot address**. In the iOS app, tap the sliders icon on capture, open **Connection**, enter the full base URL in **Wi-Fi address**, and tap **Reconnect**. Keep the existing access token. A link-local/USB address, when available, belongs in **USB address**.
3. When the Mac changes network, the backend updates its listeners automatically. The admin updates the displayed addresses. If the phone's saved URL changed, copy the new one and reconnect; automatic phone discovery is not included.

On 9 October the current hotspot base URL is `http://172.20.10.2:8000`; the admin is that URL plus `/admin`. Addresses can change. The physical iPhone previously authenticated over this same-iPhone hotspot at **09:13:12 CEST**, with old USB failing and hotspot Wi-Fi succeeding. Evidence: `.local/hotspot-check-2026-10-09/phone-hotspot-check.json`. This is a real phone check, separate from the automated listener-change tests below.

**Ready** means the backend has a listening local address, not proof that a particular phone can reach it. The phone's Reconnect result verifies that route. **No phone address** appears when no eligible interface is available. Failed address discovery or binding is shown explicitly; failed binds are retried. Copy works on the tested loopback/hotspot browser URLs; if the browser rejects clipboard access, the field is selected for manual copying.

## Starting the backend

The project launcher is now:

```sh
.venv/bin/scanpay-serve
```

Equivalent: `.venv/bin/python -m backend.local_server`; optional `--port 8000`. Start it from the repository root so the existing `.env`, `.local/providers.json` and data directory are reused. It is a **macOS IPv4 local-demo launcher**, using the system `/sbin/ifconfig`. Ordinary `uvicorn backend.api:create_app --factory --host 127.0.0.1 ...` still works as a manually bound server; the admin accurately reports automatic updates as off in that mode.

The existing private `.local/mobile-live-2026-10-09/serve.py` delegates to this launcher. PID/log paths and the original database remain in place. Its old contents are backed up under `.local/local-network-setup-2026-10-09/serve-before.py`. A one-time idle restart activated the new launcher; subsequent network changes do not restart the backend. Do not start a second owner or use reload/multiple workers with this private database.

## Behavior and boundaries

- Loopback `127.0.0.1` stays bound. Every two seconds the launcher discovers active physical `en*` interfaces and reconciles their private/link-local IPv4 listeners. RFC1918 and `169.254/16` are eligible; public addresses, IPv6, VPN `utun*` and virtual bridges are excluded. There is no wildcard bind or public deployment.
- New listeners share the original Uvicorn application/lifespan, request state and backend runtime. Removing a listener stops new connections at that address without restarting jobs or explicitly closing accepted requests. Losing the underlying physical network can still break a phone's connection; existing app recovery remains responsible for that.
- `GET /v1/admin/connection` is authenticated and read-only, with no-store responses. It reports `automatic`, refresh interval, last successful check, listening URLs/interface identifiers/kinds and warnings. It exposes no token or provider secret. The unauthenticated admin shell contains no addresses.
- The admin's Connection section is collapsed initially. It refreshes through the existing polling cycle, removes outdated URLs, reports errors and clears values on disconnect. Network probing runs in the launcher, not on each HTTP read.
- No iOS source or signing change is needed: the existing address fields, secure token and Reconnect flow are reused. No automatic phone discovery, QR pairing, firewall modification, Wi-Fi switching, inference, subscription or payment integration is introduced.

## Verification

- **690 offline backend/evaluation tests pass**, including 18 new connection/launcher cases. Domain/orchestration coverage: **96.03% statements / 91.25% branches**. Lint/format, strict mypy, JS syntax and regenerated OpenAPI checks pass. Scan/result schemas are unchanged.
- Built the wheel and source distribution and checked the installed `scanpay-serve` entry point. No dependencies were added.
- An isolated synthetic server bound a real private interface, removed/re-added that listener, rejected new requests at the removed address and completed an already accepted slow request. Loopback and the backend identity stayed stable. This simulates address discovery changes without changing the user's Wi-Fi or touching production data; it is not a claim of testing every physical network transition.
- Browser verification covered expanded/collapsed Connection, copying on loopback and hotspot URLs, disappearance/recovery of addresses, clearing on sign-out, 402 px layout without horizontal overflow, and no console errors. Synthetic data only.
- The running real backend now reports automatic updates enabled. Health, authenticated profiles/connection and the admin returned 200 over both loopback and the current hotspot URL after activation.
- Private evidence is in `.local/local-network-setup-2026-10-09/`: `backend-tests.log`, `listener-checks.json`, `live-verification.json`, package logs and the isolated test harness. Existing native verification remains 23 unit/recovery and 2 UI tests from the sheet PR; native code was unchanged here.

The live snapshot for this update is **2,204 dispatches / €336.75 held**, with **Mistral Small** selected (`mistral-small-image-roles-v3@2-b292ba761e512607`). This supersedes the prior Gemini/2,202 snapshot. Original ledger rows, credentials/provider configuration and the selection observed at the start of this update are preserved. Caps remain 2,217 / €338.05, leaving at most 13 calls / €1.30 under the existing separately authorized explicit-Send plan. The agent made no inference call.

Next: [initial presentation handoff](PRESENTATION_HANDOFF.md), [copyable prompt](PRESENTATION_PROMPT.md) and the agreed [milestones](ROADMAP.md).
