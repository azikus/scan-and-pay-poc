# Starter evaluation pack

Prepared for handoff, 1 October 2026. Private labels are assistant-drafted and awaiting Markus's check; no accuracy result exists. Backend requests use the prepared JPEG/PNG images only.

## Concrete first inputs

Historical Milestone 1 starter subset only. The latest user instruction requires **all samples in every Phase 2 provider evaluation batch**, after the upfront credential gate. Inventory/preparation and coverage rules are in [PHASE2_ROLLOUT.md](PHASE2_ROLLOUT.md); do not reuse this two-image manifest as the Phase 2 corpus.

| ID | Input | Condition and purpose |
| --- | --- | --- |
| uk-continental-reference | samples/variants/uk-continental-reference.png | Page 1 of the existing UK print pack, rendered at 160 DPI. UK sort-code/account pairing; distinguishes gross invoice total from explicit amount due and header reference from payment instructions. Not a camera photo. |
| hr-racun-12793-reference | samples/racun-12793-26-no-barcode.png | Existing verified 300-DPI payment-page rendering with barcode removed. IBAN, model and poziv na broj; issuer/manager versus community beneficiary is a useful ambiguity. Not a camera photo. |

Private manifest: .local/evaluation/starter-manifest.json. Draft values and unresolved questions: .local/evaluation/starter-answer-keys.json. They contain source hashes, image linkage, draft labels, evidence and verification status, and are ignored by Git. No real payment values are copied into tracked examples or documentation.

The UK image has bank instructions but labels its payable-looking total as Gross; preserve invoice_total rather than silently relabel amount_due. Its header Ref does not itself prove a payment-reference instruction. The Croatian sample prints the property-management firm and says the community of co-owners issues the bill through it; account-holder/beneficiary association needs explicit review. Labels retain those ambiguities rather than picking convenient answers.

## Before scoring

Markus checks the draft critical values and unresolved roles; record verifier/date and label version, then score only verified visible fields. Source text helped draft/check labels but must never be sent to an extraction profile or substituted for image OCR. User confirmation in the eventual app is a separate step; these labels do not eliminate it.

The first API smoke calls can run while labels remain unverified, but may claim only compatibility and captured outputs/timing, not accuracy. Real photos are not required to build the service. Request an ordinary full-page table photo of each starter invoice when beginning camera-condition tests, then targeted oblique/difficult captures. Add originals under samples/photos/ with device/export metadata. Keep variants of a document in the same development/holdout group.

## Synthetic cases to implement as tests

- Complete UK route with leading-zero sort code/account and required reference.
- Missing sort code, OCR O/0 or I/1 ambiguity, invalid IBAN and checksum-passing but visually unsupported repair.
- Two account options; prevent cross-pairing account, amount, currency or reference.
- HR model/reference versus invoice/customer IDs; English invoice with HR IBAN and conflicting address hints.
- Invoice total/VAT/subtotal/due/credit distinction; ambiguous currency; separate manager, supplier and account holder.
- Reference-only bill; irrelevant QR URL; barcode/text disagreement; instruction-like invoice content.
- Rotated/malformed/unsupported image; provider failure; independent partial compare; restart, idempotency races, deletion tombstone and spend reservation.

Public examples under docs/examples/ illustrate shape and expected review behavior. They are not the private sample answer key. Milestone 1 implemented synthetic tests for the applicable scenarios and reports measured coverage in IMPLEMENTATION_STATUS.md. Broader-layout/method regressions remain M2/M3 work; no public example is a provider accuracy result. The 8 October scope clarification defers barcode decoding outside this PoC.

## Evidence status

The two existing documents exercised Milestone 1's first integrations, not broad reliability. Every prepared sample image belongs in the full-corpus evaluation. The upfront gate was satisfied on 6 October; the starter manifest must not be reused as the full-corpus manifest. Historical 15-test success is separate from the 183-test Milestone 1 baseline and actual starter runs. The subsequent 6 October cleanup passes 184 tests; see IMPLEMENTATION_STATUS.md. No new external inference occurred during handoff/cleanup. The separate COST_REPORT_PLAN.md uses forthcoming full-corpus evidence, not this two-image starter selection.
