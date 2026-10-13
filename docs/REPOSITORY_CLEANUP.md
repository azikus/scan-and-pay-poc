# Repository cleanup — 13 October 2026

## Scope reconciliation

Markus skipped Android capture/review and the comprehensive final presentation, requested repository/documentation cleanup, and confirmed explicit phone Send works after the backend repair. Current guidance is consolidated in AGENTS.md, CURRENT_STATUS.md, CODING_HANDOFF.md and ROADMAP.md. Android records the skip; the retained deck/showcase and platform READMEs no longer promise skipped work. Historical evaluations, presentation slides/notes and contracts are unchanged. Earlier accumulated guidance remains recoverable in Git at `528ad23`.

The old Android-based SUNMI display-test source left untracked in the original checkout is retired. Its dated README remains as a hardware record, and the live companion stays supported. The untracked top-level SUNMI launcher was also retired: it duplicated companion launch controls and force-stopped AirScreen. Use `sunmi/companion/launch.sh` and saved display mode instead.

## Source/private boundaries

The existing Webflow showcase source, licensed fonts, reviewed screenshots and builder now belong to Git. All 18 image assets were visually inspected: native flows use explicit synthetic invoices, spatial screenshots use supplied demo data and are labelled Mac UI previews, the admin images contain a synthetic UK context and selector only, and SUNMI displays sanitized journey events. No real source invoice/gallery, raw response, label key, credentials or database is added.

Three unused website images were moved to the private cleanup backup. Source provenance keeps filenames/descriptions and source hashes; full machine paths remain only in the backup. Generated website preview/standalone/ZIP and QA captures stay ignored. The page no longer advertises Android capture as the next delivery; no layout, product behavior or publication changed.

Private backup: `.local/repository-cleanup-2026-10-13/`. It retains the original untracked display-test tree, wrapper launcher, original provenance and unused screenshots, plus asset review sheets. The prior pull backup `.local/pull-main-backup-20261013T091359Z/` retains the three overlapping local documents. Twelve old local branches matched exact merged PR heads and were removed after verifying their merge commits are ancestors of main. A verified private `local-branches.bundle` and `merged-branches.json` preserve their tips and PR mapping. Remote historical branches remain available.

The running source archive `.local/runtime-source/269e0223580ecba96793d9382c3efcffa77d720e/`, launcher, environment, providers, jobs/accounting/reviews/selection/identity and phone data are untouched. No runtime restart, provider call, old-job retry or historical comparison resumption is part of this task.

## Validation

- Current documentation links and all website asset references validated.
- Website build, JavaScript syntax, standalone embedded galleries, allowlisted Webflow ZIP and rebuild from the extracted package validated; provenance/private paths and private/generated files excluded from the package.
- Existing seven live-display frontend checks pass.
- Retained presentation builds/checks: 25 slides, notes/assets intact, audience HTML self-contained, private gallery excluded.
- Git diff whitespace and staged privacy/file-boundary checks pass. No backend/iOS source or wire contract changed, so dated application test results remain dated rather than claimed as cleanup runs.

## Next follow-up

Markus proposed a couple more provider runs after cleanup. Define the selected exact profiles, complete input inventory and repeat count in a new immutable run plan before inference. Preserve stopped/failed/completed historical runs. The Haiku/Mistral last-request failures and AWS processing gaps remain dated evidence until a separately recorded fresh run addresses them. No Android or final-deck milestone remains.
