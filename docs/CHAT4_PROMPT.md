# Prompt for the fourth chat

> Historical scope/checkpoint: retain the dated evidence below. Current scope, runtime and acceptance are in [CURRENT_STATUS.md](CURRENT_STATUS.md), [CODING_HANDOFF.md](CODING_HANDOFF.md) and [ROADMAP.md](ROADMAP.md). Android/final presentation are skipped; mobile/backend/SUNMI and successful phone Send are accepted. Old next-task wording, worktree paths, provider selections and financial admission limits are not current instructions.

Paste the following into a new local chat in the existing Scan and Pay project:

```text
Continue Scan and Pay with Phase 3: mobile design, then the first native iOS implementation. Work in /Users/markusi/Developer/Azikus/scan-and-pay. Phase 2 is closed; PR #1 is merged into private main (c7f2fc9471e744b75f47614b60e8b648fc876b1e). Inspect local/remote state and preserve all private evidence and any newer work before creating an appropriate codex/ implementation branch. Do not restart provider evaluation.

Read AGENTS.md, docs/CHAT4_HANDOFF.md, docs/MOBILE_UX_BRIEF.md, docs/PHASE2_CLOSEOUT.md, docs/CODING_HANDOFF.md and docs/API_CONTRACT.md, then follow the remaining handoff read order as needed before implementation.

We selected direct-image GPT-4.1 mini, model gpt-4.1-mini-2025-04-14, profile openai-mini-image-roles-v3@2-5094b6dc13ef5718. The active private config is .local/providers.json. Use the existing backend and contract, with one model call and no automatic fallback or retry. The backend is already implemented; keep provider credentials there.

I want a really modern, polished mobile UI. Start by proposing a coherent Azikus visual direction and screen/state sketches, and iterate with me before writing mobile code. My suggested first flow is:

1. Camera preview with a capture button. Image import is useful for testing too.
2. After capture, let me crop/adjust the image and retake it if needed.
3. An explicit Send button uploads the resulting JPEG/PNG to the backend on my Mac. Do not upload before I press Send.
4. Show an attractive processing state. The initial proposal is a subtle shimmer on empty field placeholders with truthful Uploading / Reading payment details text, then a smooth reveal of the result. Propose/refine this; do not show fake percentages or delay a ready result just for animation. Respect Reduce Motion.
5. Show extracted data in an editable, expandable bottom sheet over the captured image, keeping the image accessible for checking. Consider full-screen review if editing or accessibility makes the sheet awkward. Preserve useful fields, nulls, warnings, leading zeros and linked payment options. Every draft requires review.
6. Add a clearly simulated Demo Pay button. On tap, dismiss the bottom sheet, clear the current mobile draft and re-enable capturing for the next document. No real payment, payment API or fake receipt. Let's agree its exact behavior while refining the design.

Paper detection with a live outline is a TODO for when I have invoices nearby. At handoff I said tomorrow morning, meaning 9 October 2026; if this chat starts later, confirm readiness rather than assuming testing happened. Do not implement or require detection in the first manual capture/crop slice. Test it with real paper later. QR/barcode decoding remains outside this PoC.

After we agree the screens, implement iOS capture/import → crop → send → polling → editable review → simulated pay/reset. Connect to a configurable reachable Mac URL; a physical iPhone cannot use its own localhost to reach the Mac. Handle permissions, connection failures, partial/empty results, backgrounding, duplicate sends and late results from old scans. Keep secrets out of source and the phone's provider configuration. Use the established idempotency and result semantics.

The current ledger has 2,197 dispatches / €336.05 conservative allowance under the €500 project cap, and the selected config has no unused call allowance. No inference is needed for initial design or offline integration. Before real mobile scan tests, prepare a bounded plan against the same ledger and check the selected account's readiness; never reset the ledger or rerun completed experiments. Do not buy subscriptions.

Start with the visual/interaction proposal and any focused setup inspection needed for it. Keep the discussion practical and concise. Android, final findings and the attendee display come later.
```
