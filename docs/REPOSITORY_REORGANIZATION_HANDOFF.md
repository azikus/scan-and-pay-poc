# Repository reorganization handoff — 9 October 2026

Markus explicitly requested a separate chat to do this after the current mobile/admin PR is merged. He authorizes the refactor, checks, status/documentation updates, commit/push, PR creation and merge without further routine confirmation. Read CODING_HANDOFF.md and MOBILE_CHECKPOINT.md, then inspect the actual current Git/PR state. Start a `codex/` branch from the merged checkpoint, preserving any newer work.

## Intended structure

- `backend/`: existing Python backend. Keep package/import semantics stable where possible; avoid an unrelated architecture rewrite.
- `frontend/`: move the admin inspector source/assets out of `backend/admin_assets/`. It can still be served by FastAPI as part of one deployment. Verify both source-checkout serving and wheel/package assets; do not assume source-relative paths work in an installed wheel.
- `ios/`: move `apps/ios/` intact and update XcodeGen/project references, schemes, build commands, docs and relevant scripts. Preserve the bundle ID, app data/recovery compatibility, source/resources, signing behavior and existing fixtures.
- `android/`: add a concise future-work README. No Android scaffolding, dependencies or implementation yet.

Keep shared contracts/docs and useful root tooling where appropriate. Do not move private samples, results, credential stores or the `.local/backend/` database/artifacts merely to match the source layout. Root `.env` remains the credential/configuration source. Update private launcher paths only if necessary, preserving listeners, original data directory and selected profile.

## Scope and checks

This is a structural refactor: preserve API routes/contracts, extraction behavior/profiles, budgets, scanner UX, source filtering, provider-output and mobile-image inspection, confirmation/recovery and reconnect semantics. No new paid calls, corpus runs, default changes, presentation, automatic discovery, paper detection, backend features or Android implementation.

Run the relevant backend lint/format/type/tests/coverage gates and contract comparison; verify JS syntax, package/wheel asset serving, and local authenticated health/profile/admin reads without inference. Build iOS from its new path and run all unit/recovery and UI tests using synthetic fixtures. A device reinstall is unnecessary unless a functional build change warrants it; preserve the user's current app/draft and do not require an unlock for this folder-only refactor.

Update README, ROADMAP, IMPLEMENTATION_STATUS, CODING_HANDOFF, MOBILE_CHECKPOINT, MOBILE_IMPLEMENTATION, MOBILE_LIVE_TESTING, ARCHITECTURE, operational/iOS instructions and AGENTS where paths/current status change. Label historical paths in old experiment records rather than rewriting immutable evidence. Check active documentation links and stale executable path references.

Record a concise final handoff with actual directory layout, validation results, preserved private-state evidence and PR/merge result. Create and attach the PR, review/check it, then merge through the normal checked flow without force push or bypassing protections. Leave the original checkout usable with the inspector running if it was running before; confirm clean Git status and original ledger/profile after any restart.

## What comes afterward

Wait for Markus to build the presentation together. Mobile-client improvements follow, then backend improvements, and Android last. The presentation will use retained experiment evidence and speed/correctness comparisons; it is not part of this unattended refactor.
