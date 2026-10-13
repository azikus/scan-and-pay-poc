# Current project status — 13 October 2026

## Scope and acceptance

Markus explicitly **skipped the Android capture/review PoC and comprehensive final presentation** on 13 October. They are removed from the remaining delivery scope. The delivered 25-slide reveal.js deck remains in [presentation/](../presentation/README.md); the existing Webflow showcase is preserved in [website/](../website/README.md). No site/deck publication is implied.

The installed iOS app, backend/admin integration and SUNMI live companion are accepted for the current PoC. Automatic native document capture is also accepted. Markus subsequently confirmed that **explicit phone Send works after the backend repair**. There is no remaining phone-Send verification gate. These are user confirmations, not additional measured performance or correctness results.

## Merged functionality

Application/presentation PRs #1–#13 are merged. Main checkpoint before this cleanup: `528ad23` (PR #13).

- iOS: Apple Vision document detection/stable automatic capture, grey surround, perspective correction, full-photo crop recovery, manual capture/import, explicit Send, editable review, saved confirmation and interruption recovery; current dark Liquid Glass and hotspot-only settings.
- Backend/admin: typed payment candidates, partial-field recovery, country/route guidance, shared method/model selection, original JSON and separate confirmed edits, explicit env cloud credentials and local network listeners.
- SUNMI: live dual-display companion, masked transport/UI/provider events, next-scan selection, circular motion and saved display modes. The obsolete offline display-test prototype is retired.
- Provider integrations: 31 configured profiles after Fireworks/Aya removal. Current compact LLM profiles include country context as standard. See [provider API evidence](API_CONNECTION_STATUS.md) and [country/context study](INVOICE_CONTEXT.md).
- Assets: the approved initial deck and existing Webflow showcase use reviewed synthetic/masked material. Spatial screenshots are native Mac previews of a separate app, not headset/passthrough evidence.

## Runtime and preservation

The repaired live backend uses stable merged-source archive `.local/runtime-source/269e0223580ecba96793d9382c3efcffa77d720e/`, via `.local/mobile-live-2026-10-09/serve.py`. That archive includes the merged backend/admin/SUNMI/context changes; PR #13 adds native camera work. Removed worktrees are no longer runtime dependencies. Do not delete the archive or restart the active service for repository housekeeping.

Keep root `.env`, `.local/providers.json`, `.local/backend/`, original accounting/jobs/stages/reviews/selection/server identity, source invoices, labels, responses and device data private and intact. The last documented accounting checkpoint before this cleanup was 2,380 reservations after Markus's SUNMI scan; his subsequent successful Send means this is a dated baseline, not today's queried total. No fresh ledger/selection snapshot was taken during cleanup. The context-era selected definition was `openai-mini-image-roles-v3@2-85c414059effa4ad`; read actual live selection before operations and never reset it from a document.

Local financial/cumulative-call enforcement was explicitly removed in PR #7. Historical caps/holds are retained evidence, not current admission limits; holds are not actual provider bills. New inference still requires a defined user-authorized task. The stopped 9 October comparison stays stopped.

## Remaining work

Repository cleanup and documentation reconciliation are complete; source/backups and checks are recorded in REPOSITORY_CLEANUP.md. Markus proposed a couple more provider runs next. Before dispatch, define exact profiles, complete input inventory and repeat count, save a fresh immutable plan/keys, and preserve all prior outcomes. No inference or automatic retry belongs to this cleanup.

Known provider evidence gaps remain: Haiku 4.5's latest observed availability failure, Mistral Large 4's last timeout, and two AWS profiles with authenticated but untested processing. These dated gaps do not imply today's provider outage. Incomplete drafts are completed API requests requiring review, not transport failures.

Hosting, real payment execution and QR/barcode payload decoding remain outside the current PoC. No Android app, final deck or new acceptance rehearsal is pending.

## Verification and history

Latest application checkpoints: PR #11 had 792 backend/evaluation tests, seven frontend checks and 96.19% statement / 91.34% branch domain coverage; PR #13 had 39 native unit/recovery tests plus four UI flows, signed build and physical camera acceptance. The backend repair had authenticated service checks, exact-profile request preparation and 108 offline extraction tests. These are dated results, not new cleanup tests.

[Repository cleanup](REPOSITORY_CLEANUP.md) records source/backups and the current validation. Historical implementation/evaluation documents retain dated evidence. The former accumulated status/handoff/guidance can be recovered from Git at `528ad23`; current scope is owned by this file, [coding handoff](CODING_HANDOFF.md) and [roadmap](ROADMAP.md).
