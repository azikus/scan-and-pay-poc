# iOS Liquid Glass, motion and connectivity — 12 October 2026

Markus requested native Liquid Glass, screen transitions (especially cropping), a review of client connectivity/hosting options, and a working hotspot connection. This starts the scoped iOS polish work after the initial presentation; it does not authorize cloud deployment or another provider experiment.

## UI changes

- Native iOS 26 `glassEffect` on secondary controls and tinted primary actions. iOS 18–25 uses material secondary controls and a solid ice-blue primary action. Reduce Transparency uses solid surfaces. The Azikus artwork and existing Hanken Grotesk fallback remain unchanged.
- Capture/crop/document transitions use a brief spring with a shared document frame between crop and preview. Review/confirmation retain native sheet presentation. Processing fields animate into the ready review.
- Crop rotation animates one quarter-turn, fits the rotated image inside its canvas, then commits the same pixel-preserving rotation. Actions wait until that transition finishes. Reset eases back to the full image; a rule-of-thirds guide appears while adjusting the crop.
- Reduce Motion replaces spatial transitions with a short fade and performs crop rotation/reset immediately. Existing shimmer and completion reduced-motion behavior remains.
- Extraction, confirmation, persistence, idempotency, review rules and payment simulation are unchanged. Nothing is sent before explicit Send.

## Current connectivity

| Option | Current client support | Dependency |
| --- | --- | --- |
| iPhone Personal Hotspot | Verified on the physical phone on 12 October | Mac connected to that hotspot; backend/Mac awake |
| Shared Wi-Fi | Saved private IP or `.local` hostname | Both devices can reach each other; some guest networks isolate clients |
| USB | Saved link-local URL, attempted first when configured | An actual working network interface over the cable; plugging in alone does not guarantee one |
| Hosted HTTPS backend | URL validation and authenticated requests already support it | A deployed compatible backend, valid HTTPS and token; setup UI currently calls this the Wi-Fi address |

No automatic phone discovery is implemented. The Mac launcher follows eligible physical local IPv4 addresses. The phone retains editable addresses and Reconnect. Drafts are tied to the backend identity, so a new cloud server will not silently take over an existing draft.

On 12 October, the running backend authenticated over loopback and `http://172.20.10.2:8000`. The phone was configured for this hotspot route and reported **Wi-Fi connected at 21:04:02 UTC / 22:04:02 London time**. This was an authenticated profile read, not an invoice submission. Its diagnostic contains only connection information at `.local/ios-glass-2026-10-12/phone-hotspot-check.json`. Phone invoice/draft files were not copied or cleared. This setup selects the hotspot alone; a USB URL can be added again in Connection settings when needed.

Addresses may change after reconnecting. Use the admin Connection panel to obtain the current URL and update the phone when necessary. Keep the Mac awake during the demo. The existing backend process and private state remain in place.

## Hosting recommendation

Use the verified hotspot for now. For independent phone use without the Mac, Railway is the simpler candidate for the next hosting task: it documents FastAPI deployment and persistent volumes. This app needs a single API/worker owner and durable storage for SQLite, images and provider artifacts. Use a persistent volume, not an ephemeral container filesystem. Railway volumes currently cannot be combined with replicas. [FastAPI deployment](https://docs.railway.com/guides/fastapi), [volume reference](https://docs.railway.com/volumes/reference).

Hostinger is also possible via a Linux VPS. Its published Python support is VPS-only and self-managed, so we would own system updates, service/container management, TLS, backups and monitoring. [Hostinger language/framework support](https://www.hostinger.com/support/which-programming-languages-and-frameworks-are-supported-at-hostinger/).

Before deploying, choose the account/region, prepare persistent paths and provider credentials, use a Linux-compatible Uvicorn entrypoint (not the macOS network launcher), and review the shared local token/admin exposure for the hosted environment. Treat any data migration and retained scans explicitly. Hosting charges are separate from provider-call allowances. No hosting account, subscription, public endpoint, data migration or deployment was created in this task.

## Verification

- The iOS 26.2 iPhone 16 Pro simulator passed all **23 native unit/recovery tests and both existing UI tests**, including JSON wrapping, editable fields, confirmation/reset and saved-value behavior. Synthetic review/confirmation/capture screenshots were inspected.
- The new crop regression test compiles. Its automated execution and the additional iOS 18 run were blocked before test startup by Xcode simulator service-hub/runner errors. These are not recorded as passing tests. A clean simulator restart allowed direct UI verification of capture → crop → Rotate → Reset crop → Use crop → Edit crop on iOS 26.2; controls re-enabled after rotation and the image stayed in bounds. Screenshot: `manual-crop.png`. Direct iOS 18.6 inspection also verified rotation and the material fallback. A primary-action contrast issue was corrected and visually rechecked in `manual-ios18-final.png`.
- Signed build succeeded and was installed/opened on the physical iPhone 16 Pro (iOS 26.6.1), preserving its existing app data. The final fallback-contrast revision also built and installed; its relaunch was blocked when the phone locked. No live invoice or payment was submitted by the agent. Physical animation feel remains for Markus to assess.
- Swift formatting and `git diff --check` pass. The original budget rows/configuration hashes remain unchanged: **2,273 dispatched reservations / €351.95 held**. The backend was not restarted.
- Private evidence, builds, test logs and screenshots are under `.local/ios-glass-2026-10-12/`. Test exports also retain two UIKit `_UIReparentingView` warnings while presenting the menu; the exercised menu/JSON flow passed.
