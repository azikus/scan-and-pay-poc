# M3 interpretation implementation

**Current checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; additional handoff details are pending. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Latest implementation (8 October): **the draft policy is implemented and offline-tested**. Invoice totals and evidence-backed supplier/account-holder fallbacks are accepted without overwriting explicit recipients; bank transfer is preferred; versioned prompts require printed text only and no barcode decoding. Historical prompts/results/defaults remain unchanged. Full replay: **67 complete / 1,029 incomplete / 299 errors**, versus 11 / 1,085 / 299 with strict review and rules 3. This is completeness on original images, not correctness or masking evidence. **547 tests** pass (95.18% statement / 89.82% branch coverage). The fresh 17-image × 3-method matrix is prepared, **not dispatched**: at most 68 calls / €6.80 new allowance. Colleague JSON and correctness scoring remain pending. See [draft policy and prepared evaluation](M3_DRAFT_POLICY.md) for current semantics, evidence and exact continuation paths.

Updated 8 October 2026. This is offline implementation and saved-response replay, not M3 completion or fresh provider validation. Existing defaults, rules 1/2, historical profiles/results, credentials and the original ledger are preserved. Work remains in the existing checkout and branch, without commit/push.

## Multilingual labels

`backend/labels/labels-v1.json` is a versioned dictionary of literal aliases, semantic fields and language tags. Initial coverage is English, Croatian and selected Italian labels; this is not complete language support. `backend/label_dictionary.py` checks field names, blank aliases and normalized alias collisions. Unicode composition, case and whitespace are normalized for label matching; bank values are never translated or repaired.

The dictionary maps labels to meanings; `ocr_rules_v3.py` determines values and associations. Amount due, invoice total and payment reference remain distinct. Bare “account” and “reference” are deliberately unsupported because they do not establish a bank account or payment reference. Language tags document translations; they never select currency, account country, payee ownership or an OCR provider. All languages' aliases can match the same multilingual document.

To extend coverage, add reviewed literal translations with a synthetic positive case and counterexamples for competing meanings. Preserve a dictionary version once it has replay evidence; introduce another dictionary/profile revision for subsequent changes. Supplier names, invoice identifiers, sample hashes and document-specific answers never belong in the dictionary. Layout/value constraints stay independently tested in the parser. Broad natural-language interpretation belongs to a separately measured model method, not an ever-growing list of invoice exceptions.

## Rules 3

Rules 3 adds colonless labels, bounded inline bank-label recognition, separate label/value lines, Markdown table headers and cells, and unique page-local geometric adjacency. AWS normalized boxes, Google normalized vertices and Azure page-scaled polygons are used internally only when their coordinate space and dimensions are valid. Unknown geometry does not become a fabricated canonical box. Evidence references exact original source spans, including separate label and value spans.

Recognized amounts are retained without a bank route. Detached references/payee readings remain unresolved candidates rather than migrating to another account. Account/currency/header boundaries, contradictory readings, malformed bank characters and multiple routes remain reviewable. Supplier/account holder is not silently promoted to beneficiary. Unknown wording and nonmonetary totals remain gaps. Rules 1/2 are unchanged.

`rules_version="3"` selects this interpreter for the four managed OCR adapters. Profiles disclose `label-dictionary@1`; the existing selected/default configurations are not replaced automatically.

## OCR → LLM composition

`ProfileConfig.hybrids` references one configured OCR option and one configured OpenAI compact-protocol-5 interpreter with `partial_v1`. The first implementation deliberately supports that text transport only; it does not claim every provider's text interface has been integrated. Each hybrid has its own identity and enablement. Existing direct-image options and results remain separate.

The image goes to the OCR recipient. Only whitelisted OCR text, line spans and native geometry go to the interpreter; raw layout attachments, embedded images and unrelated vendor metadata are excluded. The private exact interpretation input and both responses are retained. The output is explicitly `model_claim` evidence; no OCR grounding or image verification is invented. The text request uses the existing Responses structured-output transport with no tools or URL execution, consistent with [official text-input documentation](https://developers.openai.com/api/docs/guides/text).

Both external calls are reserved atomically before acceptance. A new `stage_reservations` mapping links each slot to its own row in the existing budget ledger; historical rows are untouched. Dispatch consumes only its reserved slot and cannot be repeated. Failure/restart releases only undispatched reservations; uncertain dispatched costs stay retained. Both recipients, requested/returned versions, source-stage linkage, input hashes, timings and costs are recorded. The public stage additions are optional for historical records.

Each external stage retains the configured timeout, and the whole pipeline remains bounded by the job deadline. Total timing includes both stages; provider duration is their sum. Empty recognition or a failed interpreter produces an explicit failure with preserved first-stage artifacts. There is no automatic retry, rules fallback, cross-method merge or shared OCR cache. Field-level recovery still preserves usable interpreter fields when another field is malformed.

## Replay and verification

Private evidence: `.local/m3-interpretation-2026-10-08/final/summary.md`, `summary.json`, twelve full-matrix replay files and `providers-proposed.json`. The proposed catalogue changes four OCR rule versions and adds one **disabled** hybrid; it is not a new spending plan or a live-validation claim. Earlier trial replays remain in the parent directory.

Replay covers all **372 saved OCR recordings: four methods × 31 images × three rounds**. Original outcomes were 63 incomplete / 309 zero-field errors; rules 3 produces **195 incomplete / 177 zero-field errors**. Thus 132 previously empty records now retain invoice/payment fields, and no previously populated record becomes empty. These are repeated method/image records, not unique invoices or correctness scores. All results still require review; labels are unverified.

Local rules median is approximately 1.2–1.4 ms and p95 1.8–5.2 ms per method (93 recordings each). These are local replay timings, excluding original OCR and any model call. Source stage/total timings and costs remain provenance in the replay files; no fresh hybrid latency or expense has been measured. The separate cost report receives no new charge rows because no inference occurred.

Verification: **485 offline tests**, **95.21% statement / 89.59% branch coverage** across domain/orchestration/evaluation. Lint, formatting, strict typing and generated contracts pass. Preservation checks cover 2,041 original source artifacts, all 45 saved batches, old profile identities, rules 1/2, credentials and the original 1,924 dispatched reservations / €306.20 retained allowance. This allowance is not a provider bill. No dependency changes or new paid calls occurred.

## Remaining M3 work

- Extend multilingual/structural interpretation using reviewed aliases, failure classes and counterexamples. Remaining empty records mix unrecognized labels/roles, uncertain geometry, blank/supporting pages and recognition limitations; do not equate them with unreadable invoices.
- Complete separately labelled fresh full-corpus evaluations of promising new methods under a new bounded plan and current readiness checks. The old 1,924-call plan is consumed; saved OCR sent to a model is still paid inference.
- M4 still needs reviewed expected fields, correctness/latency/cost comparisons and pipeline selection. Mobile/display work remains deferred.

## Future improvement outside the PoC

On 8 October the user explicitly deferred payment-barcode/QR decoding and payload interpretation beyond this PoC. It is not required for M3, mobile work or final PoC acceptance. Mention it later as a potential improvement in the final findings. Continue extracting printed payment references and identifiers through OCR/document/vision methods; barcode presence in an image does not expand scope. Existing contract fields and historical evidence remain unchanged.
