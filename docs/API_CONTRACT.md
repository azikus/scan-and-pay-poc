# API contract v1

Handoff baseline, 1 October 2026, implemented in Milestone 1. This remains the normative v1 wire specification as providers expand. Wire names are snake_case; schema_version is "1.0". See the preserved [handoff result schema](examples/scan-result.schema.json) and [synthetic responses](examples/README.md). Export current Pydantic/OpenAPI contracts from the typed source and keep agreement tests; do not hand-maintain incompatible contracts. The 6 October handoff refresh changes no wire semantics.

Implementation note, 5 October 2026: Milestone 1 implements this contract with real UK/HR runs through both starter profiles, corrected bank normalization, successful independent comparison and preserved partial-failure evidence. [Generated result schema](../contracts/v1/scan-result.schema.json) and [OpenAPI](../contracts/v1/openapi.json) are exported from the Python models. The original examples/schema above are the preserved handoff baseline; [acceptance evidence](IMPLEMENTATION_STATUS.md) records validation and known extraction limitations.

## 1. Transport and requests

Bind to 127.0.0.1 by default. Bearer authentication is required except GET /health. Credentials, arbitrary URLs, local paths, raw prompts and model IDs are never accepted from scan callers. No provider calls on startup, health or profile-list requests.

| Endpoint | Contract |
| --- | --- |
| GET /health | 200 with status=ok when process/storage ready, 503 otherwise; no secrets or provider probes. |
| GET /v1/profiles | 200 with profiles and configured default_extract_profile_id (nullable). Each profile includes id/version, method, component IDs, provider/model/processor, supported image types, known languages, stage payload destinations, enabled/configured/live_validated flags and unavailable_reason. Availability is not extraction quality. |
| POST /v1/scans | multipart/form-data with image (one binary JPEG/PNG) and options (JSON encoded string). Requires Idempotency-Key header. Returns 202 with schema_version, scan_id, state and status_url; Location equals status_url. |
| GET /v1/scans/{scan_id} | 200 with persistent job envelope, input identity, resolved profiles, completed/in-progress results and final_result_id; unknown/deleted ID returns 404. |
| DELETE /v1/scans/{scan_id} | 204 for a terminal job after local artifact/row cleanup; 409 for queued/running work; 404 if unknown. Does not delete source samples or promise upstream deletion. |

Options object (reject unknown properties):

- mode: extract or compare; required.
- profiles: nonempty unique array of profile IDs OR the literal string all_enabled; required. Extract requires an array of exactly one ID. Compare accepts either form.
- hints: optional object, default {}; language and issuer_country are optional nullable strings (BCP-47 / ISO alpha-2 respectively). Treat as caller hints, not observed facts. No supplied account-country or currency override in v1.

Every selector resolves to immutable profile/config versions. Explicit disabled/unconfigured/incompatible profiles produce 422 before any dispatch, including in compare. all_enabled selects only implemented, enabled, configured, image-compatible profiles, sorted by ID; store selected IDs/versions and excluded IDs/reasons. If none are eligible, return 422. Live validation is tracked but not a prerequisite to a deliberately enabled smoke-test profile. Never silently downselect for spend: reject a batch whose conservative budget reservation fails. Unsupported provider language discovered during execution is a per-profile failure, not a silent switch.

JPEG/PNG bytes must decode successfully; MIME/extension alone are insufficient. Apply EXIF orientation, remove unnecessary metadata from outbound renditions, preserve original/canonical hashes and transforms. Do not silently resize or send hidden PDF text. One source image per job, no pages parameter. Bespoke upload thresholds/expiry are deferred, but decoder resource safety, bounded queues and provider hard limits remain required.

## 2. Idempotency, jobs and failure behavior

Atomically persist accepted job, input identity, canonicalized options, resolved profile snapshot and idempotency reservation before dispatch. Same key plus same original image bytes and canonical options returns the original scan (202, including if already terminal), without re-resolving all_enabled or billing again. Same key with different image/options returns 409. Repeated concurrent submissions must create only one job. The same bytes with a new key intentionally create a new run.

State progression: queued → running → completed / partially_completed / failed. On process restart, nonterminal jobs/runs become interrupted; no automatic possibly billable replay. An interrupted job remains retrievable with earlier successful profile results. Run states: queued, running, completed, failed, interrupted. completed means computation succeeded, not payment correctness.

- All runs completed: job completed. Mixed completed/failed: partially_completed. All failed: failed. interrupted overrides final aggregation when recovery cannot establish completion.
- Each run succeeds or fails independently; no majority-vote merge. In compare, final_result_id is always null. In extract, it references the single completed run; otherwise null. Clients read its payment object, not a duplicated second draft.
- Preserve completed comparison results while other runs execute. No streaming endpoint in v1; polling is sufficient.
- One API process owns bounded workers; initially at most two outbound calls. Default live smoke profile: one attempt (no auto-retry), 90-second stage timeout, 240-second job deadline. Later transient retries must be explicitly profile-versioned, bounded and charged. Ambiguous billed timeouts are never silently retried.
- Caller disconnect is not cancellation. DELETE rejects active jobs; restart interruption is not proof upstream processing stopped. Keep a minimal idempotency tombstone after local deletion: reuse returns 410, not another paid run. Tombstone retains only key/request digest and deleted marker, not invoice data.
- Error responses: {error:{code,message,retryable,details}} with sanitized details. 400 malformed bytes/JSON, 401 bad/missing token, 404 missing job, 409 key conflict/active deletion, 410 deleted-key reuse, 415 unsupported image format, 422 options/profile validation, 429 bounded queue full, 503 storage/service unavailable. 413 only for an actual documented enforced infrastructure/provider limit, not an invented product threshold.
- Per-run error codes include provider_auth, provider_quota, provider_timeout, provider_refusal, provider_unavailable, unsupported_language, invalid_provider_output, budget_exceeded and internal_error. Preserve safe stage ID/request ID, not provider raw error bodies.

## 3. Observation and evidence model

An Observation has value (string or null), raw_text (string or null), state, origin, evidence_ids, normalization and alternatives. State is observed, missing, unreadable, ambiguous, inferred or unsupported. Origin is document, barcode, caller_hint or derived. Values are strings even for amounts/accounts. No empty-string stand-ins, floating-point money or automatic leading-zero removal.

Missing/unreadable/ambiguous/unsupported observations have null value. Alternatives preserve plausible strings, their supporting evidence and reason, never silently replace the original. observed means claimed as printed, not verified by a bank. inferred/caller_hint/derived critical payment values cannot make a draft ready_for_review by themselves.

Evidence records id, canonical image_id, excerpt, optional normalized bounding box [x,y,width,height], grounding (ocr_span, barcode_payload, model_claim or synthetic_fixture), and source_stage_id. Coordinates refer to the oriented canonical image, origin top-left, units 0..1; sum of offset and extent must fit the image. Provider/crop coordinates need recorded transforms. A model quote/box remains a model_claim unless actually linked to an OCR span; checking geometry does not establish transcription accuracy. Never invent boxes. synthetic_fixture is allowed only when execution_kind=synthetic_fixture.

## 4. Payment object and associations

Payment contains document_context (language and issuer_country Observations), supplier_name, invoice_number, customer_number, description, due_date (Observations), candidates, selected_candidate_id and review. Candidate account_country is a separate Observation; a country inferred from an IBAN prefix has derived origin and recorded transformation. Caller hints remain in input.hints, never copied into observed context. An issuer/customer address is not the account country. Supplier and billed customer must not be confused. Every candidate contains:

- id; account_country, beneficiary_name and account_holder_name (separate Observations; do not assume supplier owns the account).
- amount: value and currency Observations, plus role=amount_due|invoice_total|instalment|other|unknown. Canonical amount is a signed decimal string with dot and two decimal places for initial GBP/EUR tests; preserve printed role. Currency is ISO 4217 or null. Unknown/ambiguous symbols require review, not language-based guessing.
- destination: discriminated kind. uk_domestic has sort_code/account_number Observations (normalized six/eight digits, leading zeroes retained); iban has iban/bic Observations; biller_reference has scheme/biller_code Observations; unresolved has reason. Incomplete fields remain in a typed candidate with null values, not discarded.
- remittance: reference/model/purpose_code Observations and reference_requirement=required|not_stated|unknown. Preserve Croatian HR model and poziv na broj separately, linked to this candidate. Secondary UK references/roll numbers belong here. Invoice/customer numbers remain separate unless explicit payment instructions establish their use.

Candidates represent linked payment options: amount, currency, beneficiary, route and reference travel together. Different account options or totals stay separate; never cross-pair sort code/account or GBP/EUR routes. A single plausible but unresolved candidate may exist while selected_candidate_id is null. A customer/biller reference with no implemented resolver is not a complete bank route. V1 extracts it but cannot mark it ready.

## 5. Backend review rules

Every payment.review has user_confirmation_required=true. There is no confirmed or executable-payment flag in v1. Later UI corrections remain separate from the immutable extraction.

- ready_for_review: one justified selected candidate, observed payee, positive amount explicitly marked amount_due, observed unambiguous currency, complete UK/IBAN destination, required reference/model where explicitly stated, and no blocking conflict/format/checksum issue. Critical fields need document evidence; model_claim evidence may qualify but must remain labelled unverified. This is completeness/consistency, not factual verification or bank ownership.
- needs_review: useful draft with conflicting/missing/unreadable critical values, inferred currency, unresolved beneficiary association, invoice_total without an explicitly justified due amount, uncertain reference requirement, multiple destinations, or nonpositive/credit amount. Do not convert an invoice total into amount_due.
- insufficient_data: no meaningful payment option can be assembled (for example unrelated image or reference-only bill without routing). Retain successfully extracted observations. Malformed bytes instead fail input validation; unsupported_input is not a payment-review state.

Review reasons are stable {code,path,message} objects; paths are JSON Pointers relative to payment. Initial codes: missing_required_field, ambiguous_field, conflicting_candidates, unsupported_payment_route, invalid_account_format, failed_iban_checksum, currency_inferred, amount_role_unresolved, nonpositive_amount, beneficiary_unresolved and reference_requirement_unknown.

Apply deterministic normalization, candidate association, evidence-based UK/HR interpretation and explicit validators after adapters. Do not use model self-confidence to select review state. Never silently O→0, I→1, pad digits or choose a checksum-valid guess. Store bounded alternatives, request a new image or run an explicitly costed reread if configured. No automatic paid/direct-debit rejection or rejection based on historical dates. UK modulus checks are optional later; checksum/format/CoP/account-existence are different claims.

## 6. Run diagnostics and data recipients

Each run includes profile_id/version, state, payment (nullable before completion/on failure), evidence, diagnostics and error (nullable). Diagnostics records requested/returned model/processor, prompt/schema/adapter/rules versions, timings_ms (queue/preprocess/provider/postprocess/total), validation findings, routing (applied_rule_packs and reasons), and stage records. Route only on observations available to that profile; generic, UK and HR rule/prompt variants are separately versioned. Do not make a paid language classifier compulsory. Durations use a monotonic clock; timestamps are UTC ISO 8601. Unknown duration/usage/cost is null, not zero.

Each stage records id/method, local or external execution, provider, endpoint_host, account_alias (never credentials), configured_region, verified_processing_region (nullable), payload_classes, input image/text hashes and rendition, request_id, timing, usage and cost. Payload classes include image, crop, ocr_text, layout and fields. A cloud-OCR→LLM profile records both recipients. A regional endpoint alone is not verified data residency. Routine GET output exposes safe metadata, not raw provider bodies or local filesystem paths; raw responses stay in ignored private storage.

Cost object: status=reported|estimated|unknown|not_applicable, amount decimal string or null, currency or null, pricing_source or null, priced_at or null. Locally computed rules may have zero external fee but are not free infrastructure. Keep per-currency totals separate unless an explicit dated FX conversion exists. Synthetic fixtures carry unknown costs/null usage; their timings are not measurements.

Shared prerequisites are off by default for v1 comparisons so results have independent timing. A later explicitly cached profile must disclose cache hits, real batch charges and separately estimated standalone costs; no hidden reused OCR. Before each dispatch atomically reserve a conservative per-call budget including the output cap and retry allowance; unknown maximum cost requires an operator-provided ceiling before enabling, not an unlimited run. Reconcile actual usage and retain uncertain charges after timeouts.

## 7. Contract tests required during coding

Generate API models and schemas from one typed source. Validate the two synthetic examples, plus negative and boundary fixtures; test unknown fields, enums, decimal strings, evidence IDs/coordinates, missing states, candidate IDs, cross-pair prevention, review rules, extract/compare semantics, idempotency races, restart and deletion tombstones. The supplied JSON Schema validates structural shape; business invariants above require code tests and must not be delegated to an LLM.
