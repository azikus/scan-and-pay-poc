# M3 draft interpretation — 8 October 2026

**Current checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; additional handoff details are pending. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

The user's accepted equivalences now have an opt-in implementation: `interpretation_policy=draft_v1`, component `payment-draft@1`. This composes with rules 3 or prebuilt mappings and with compact protocols 5/6 plus `partial-fields@1`. Existing prompt constants, review@2, rules versions, strict profile identities, saved results, credentials and default configuration remain unchanged. The new policy is implemented, offline-tested and freshly evaluated on all 17 masked inputs. Partial reviewed correctness, failure analysis and current verification are in [M3 reviewed results](M3_REVIEWED_RESULTS.md).

## Interpretation and prompts

- Accept `invoice_total` as a draft payment amount while preserving the printed role. Subtotals, tax, unknown roles, nonpositive values, malformed fields and currency uncertainty keep their warnings.
- Fill a missing beneficiary from that candidate's printed account holder, then from the printed supplier when no explicit recipient is present. Keep the original supplier/holder fields and evidence. Record the fallback in observation normalization. Missing, inferred, unsupported, ambiguous or unreadable readings cannot become a beneficiary. A named recipient, including an ambiguous/unreadable recipient slot, is never overwritten; the billed customer is never a fallback. A global supplier cannot displace another candidate's explicitly linked recipient.
- Prefer the unique bank-transfer candidate over other payment methods. When choosing between full payment and instalments within the bank pool, require the same observed recipient, destination and currency. Preserve every candidate and its own amount/reference; different accounts or unresolved identities require a choice. No digits or totals are invented.
- A selected candidate is a draft preference, not confirmation. Under the unchanged public v1 invariant, multiple candidates still require review and remain `incomplete`, even when bank transfer is selected. All drafts require user confirmation.
- Compact prompt revisions explicitly require human-readable printed text only: no QR, Data Matrix, PDF417 or other barcode-payload decoding, masked-content reconstruction or URL fetching. Printed text beside a code remains valid evidence. Prompt identity adds `+draft@1`; the hybrid retains the text-input wrapper and includes the versioned interpreter snapshot/policy.

The code is in `backend/draft_policy.py`; adapter requests, profile snapshots and runtime review apply it only when configured. General extraction rules and the historical strict review remain separate, unchanged baselines. Barcode decoding stays outside the PoC.

## Offline evidence

Verified replay: `.local/m3-draft-policy-2026-10-08/verified/replay.json`. It covers the full original matrix: 15 methods × 31 original images × 3 rounds = 1,395 records. Its strict comparator already includes rules 3 and partial-field recovery, isolating this policy change:

| Interpretation | Complete for review | Incomplete | Error |
| --- | ---: | ---: | ---: |
| Rules 3 + partial fields, strict review | 11 | 1,085 | 299 |
| Same saved responses + draft policy | 67 | 1,029 | 299 |

56 incomplete results become complete enough for review. No complete result regresses; no error is silently removed. These are completeness counts, not correctness scores. Original prompts generated these responses; the replay cannot measure the new prompt, masking, fresh provider latency or hybrid performance.

For context only, the 17 retained images' original unmasked counterparts account for 765 of these records: 67 complete / 610 incomplete / 88 errors after this policy. This is a labelled subset of the full replay, not a masked-image evaluation. Do not divide the full 31-image result by 17 or equate empty results with unreadable invoices.

547 offline synthetic tests pass. Domain/orchestration/evaluation coverage is 95.18% statements / 89.82% branches; the new policy has 100% statement/branch coverage. Formatting, lint, strict typing and unchanged generated-contract checks pass. The replay verifies 2,094 baseline files, another 384 OCR observation/replay files, historical profile identities and the unchanged ledger. No new provider calls occurred.

## Fresh evaluation — executed

Private plan and frozen 51-cell batch: `.local/m3-draft-policy-2026-10-08/fresh/`. All 17 masked input files and provider image-size limits were checked. The planned configuration is a separate file, not the server/default configuration.

| Method | Images | Maximum provider calls | New allowance ceiling |
| --- | ---: | ---: | ---: |
| GPT-4.1 mini direct image + draft policy | 17 | 17 | €1.70 |
| Mistral OCR 4.1 + rules 3 + draft policy | 17 | 17 | €1.70 |
| Mistral OCR 4.1 → GPT-4.1 mini text + draft policy | 17 | 34 | €3.40 |
| Total | 17 per method | 68 | €6.80 |

The same interpreter provides a controlled direct-image/hybrid comparison; its choice is not an accuracy ranking. Hybrid recognition is a fresh, separately charged call, with no hidden OCR sharing. This focused experiment does not remove any retained provider from the PoC.

All 51 cells completed with 68 calls. The current ledger has 1,992 dispatched reservations / €313.00 retained allowance; all old rows are unchanged. Cumulative plan limits were 1,992 calls / €386.00 allowance within the €500 project cap. The €6.80 new allowance is not a measured charge. Access, terms and prices were refreshed separately before dispatch without rewriting the pinned configuration. Processing residency remains unknown. No retries, fallback, repeats or subscriptions occurred.

`evaluation.experiment` produces full-matrix success/incomplete/error coverage; median/p95/max with measurement counts for total, queue, preprocessing, all provider stages and postprocessing; timeout counts and denominators; and per-stage expense provenance. Failed attempts with measurements remain included, and missing timing/cost does not become zero. Hybrid expense reports now use each stage's requested/returned model. Backend total time is not mobile capture-to-review time. One round of 17 inputs gives descriptive timing, not repeatability or population estimates.

## Human review and milestone status

The returned filled HTML was recovered and validated against the frozen pack, including every image/field and prior user lock. A separate partial reviewed key and reproducible comparison are complete. The original review/draft remains unchanged. See [M3 reviewed results](M3_REVIEWED_RESULTS.md) for 200 scored fields and 146 explicit exclusions, including 92 pending fields. Full ground-truth verification and pipeline selection remain open; recipient/reference failures need attention before freezing the mobile pipeline.

Await Markus's confirmation before PR creation or merging pending project PRs, then prepare the next-chat handoff. Select for correctness and speed regardless of cost. iOS capture/upload to the local Mac backend is the next implementation focus in another chat, following selection and agreed screens; barcode decoding stays outside this PoC.
