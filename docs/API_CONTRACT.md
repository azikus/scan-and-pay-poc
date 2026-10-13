# API contract v1

## Demo observation channel — 13 October 2026

This additive version-1 channel observes the phone and existing extraction lifecycle. It creates no extraction reservation, changes no profile/selection and executes no payment. All `/v1/demo/*` routes require the same bearer authentication as the existing API and return no-store responses. `/demo` and its allowlisted assets are data-free public shells with a self-only CSP.

- `PUT /v1/demo/sessions/{session_id}`: UUID path; body `{ "sequence": 1, "journey_id": "<UUID>", "phase": "crop" }`. Sequence is an integer 1–9,007,199,254,740,991, strictly increasing within a phone session. Unknown fields are rejected. Phases are `idle`, `crop`, `preview`, `preparing`, `uploading`, `queued`, `reading`, `review`, `confirmation`, `recovery`, `failed`, `paused`. Journey is nullable only for idle/paused. Response `{ "received": true }` acknowledges best-effort receipt, not durable persistence or extraction success. Equal/older sequence snapshots are ignored. A phone sends a fresh snapshot every eight seconds; times from the phone are not trusted or required.
- `GET /v1/demo/snapshot`: `{ version: 1, revision, server_time, sessions: [...] }`. A single consistent lock boundary covers revision and sessions. Session projection includes session/journey/scan IDs, phone sequence/phase/last-seen, independent backend state, frozen profile references, allowlisted observed stages, bounded recent event envelopes, outcome and confirmation time. Times are server Unix seconds in UTC. No payment fields, image/hash, evidence, raw payload, account alias or credential is included.
- `GET /v1/demo/events?after=<revision>`: SSE `event: snapshot`, `id: <revision>`, JSON `data` with the same complete projection. Every connection starts with a current complete snapshot even if `after` is ahead/expired; it is a resynchronization hint, not a promise to replay history. Subsequent changed revisions are checked every 250 ms; an unchanged snapshot is sent at least every ten seconds. Authenticated fetch streaming sets the bearer header. Ordinary `EventSource` is not used. The browser can fall back to authenticated snapshots.
- `POST /v1/scans` accepts optional UUID headers `X-Scanpay-Demo-Session` and `X-Scanpay-Demo-Journey`; both must be present to associate a scan. This does not enter options, image hashes or idempotency semantics. The first observed binding is immutable; duplicate uploads do not dispatch or rebind. Only a binding matching the current phone journey may change its projection. A reset does not cancel work. Prior-journey results cannot overwrite a new capture.

Events have `version`, UUID `event_id`, monotonic server `sequence`, `session_id`, `journey_id`, optional `scan_id`, `source`, `kind`, `server_time` and optional stage/run IDs. Backend kinds include accepted/running/request/response/local/validation/terminal execution states/confirmed. A request event precedes the actual transport await; a response event indicates receipt only, including HTTP failures and asynchronous polling responses. It does not claim valid extraction or visibility into remote processing. `confirmed` is emitted only after the existing review write succeeds; duplicates do not restart completion. Backend failure or a terminal `outcome=error` never implies a usable draft.

Separate `demo-state.json` stores only sanitized observation state: up to eight sessions, 128 recent scan bindings and 64 events per session. Default inactivity retention is eight hours (`Settings.demo_retention_seconds`, configurable 60–86,400 seconds). Persistence is coalesced on a single background writer. Observer/storage errors cannot fail extraction or confirmation. Following a restart, phone connection is unknown and unfinished observed stages become interrupted; no job is rerun. A fresh phone snapshot restores presence. A crash can lose the most recent best-effort update; this channel is not an audit ledger. Old mobile drafts without demo association remain valid and simply lack full display telemetry.

Display-only session selection/reset and replay are local operator controls; they never delete sessions/scans or alter the phone. Details and physical acceptance gates are in [SUNMI setup](../sunmi/companion/README.md).

## Admin method selection — 9 October 2026

Authenticated `GET /v1/profiles` advertises `default_extract_profile_id` and the additive nullable `default_extract_profile_version`. A persisted admin selection takes precedence over the configured baseline default; changed/disabled/missing selected versions remain explicit and never silently fall back. A new mobile Send fetches this pair, verifies the matching enabled/configured profile, and freezes its ID/version alongside the upload options and idempotency key. Recovery of an existing upload verifies its frozen selection, independent of a newer default.

The additive `server_id` identifies the backend data store with a persisted random UUID. It survives server restarts and is returned only behind existing authentication; it grants no access itself. The mobile app records it alongside new pending uploads so Reconnect can switch USB/Wi-Fi addresses only when they lead to the same backend. This identity is independent of extraction profiles and makes no provider call.

Authenticated `PUT /v1/admin/selection` accepts `{ "id": "<profile-id>", "version": "<exact-version>" }` and returns the same reference. Unknown/disabled/unconfigured profiles return 422; stale versions return 409. The singleton selection persists in SQLite separately from extraction records. Selecting makes no inference call or reservation and never rewrites a scan. Scans still pass an explicit single profile ID in `options.profiles`; existing submit semantics are unchanged.

Authenticated `GET /v1/admin/methods` provides the read-only method guide and sanitized aggregate benchmark snapshot dated 8 October. Those historical results are not a live readiness claim. Runtime availability comes from `/v1/profiles`; timings are backend elapsed time, not mobile capture-to-review time.

Handoff baseline, 1 October 2026, implemented in Milestone 1. This remains the normative v1 wire specification as providers expand. Wire names are snake_case; schema_version is "1.0". See the preserved [handoff result schema](examples/scan-result.schema.json) and [synthetic responses](examples/README.md). Export current Pydantic/OpenAPI contracts from the typed source and keep agreement tests; do not hand-maintain incompatible contracts. The 6 October handoff refresh changes no wire semantics.

Implementation note, 5 October 2026: Milestone 1 implements this contract with real UK/HR runs through both starter profiles, corrected bank normalization, successful independent comparison and preserved partial-failure evidence. [Generated result schema](../contracts/v1/scan-result.schema.json) and [OpenAPI](../contracts/v1/openapi.json) are exported from the Python models. The original examples/schema above are the preserved handoff baseline; [acceptance evidence](IMPLEMENTATION_STATUS.md) records validation and known extraction limitations.

## Product outcome — 8 October 2026

New terminal runs expose `outcome: success | incomplete | error`:

- **success:** one complete, consistent draft is ready for review. Confirmation is still mandatory; correctness and ownership are not verified.
- **incomplete:** some invoice/payment field data survives, but the draft needs correction or completion. Ambiguous alternatives remain data for review, never selected facts.
- **error:** execution failed/interrupted, the response is unusable, or there are no invoice/payment field values, raw readings or alternatives. Language/country alone and unstructured OCR text do not count as populated fields.

`state` continues to describe execution, and `payment.review.state` describes detailed review readiness. A valid response containing no fields can therefore have `state=completed`, `outcome=error`, an empty draft and a `no_usable_data` validation finding. Its transport `error` remains null. Clients use `outcome` for the three result labels; job completion and `final_result_id` are not usability signals. Queued/running outcomes are omitted. Historical records omit the optional field and remain unchanged; the CLI derives their outcome from the saved state/data.

The versioned `field_policy=partial_v1` handles compact protocols 5/6 field by field. It preserves valid fields and candidate associations, records findings/review reasons, and retains rejected exact strings only as uncertain alternatives with evidence. Missing or contradictory fields make a draft incomplete when other data survives. Invalid JSON, duplicate keys, unknown response structures, provider identity mismatches and transport failures remain errors. No bank digits, scheme or cross-candidate pairing are guessed. Original strict profiles remain reproducible under their existing versions.

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

Every selector resolves to immutable profile/config versions. Explicit disabled/unconfigured/incompatible profiles produce 422 before any dispatch, including in compare. all_enabled selects only implemented, enabled, configured, image-compatible profiles, sorted by ID; store selected IDs/versions and excluded IDs/reasons. If none are eligible, return 422. Live validation is tracked but not a prerequisite to a deliberately enabled smoke-test profile. Selection is independent of local spending or cumulative call limits; missing pricing metadata does not reduce the selected batch. Unsupported provider language discovered during execution is a per-profile failure, not a silent switch.

JPEG/PNG bytes must decode successfully; MIME/extension alone are insufficient. Apply EXIF orientation, remove unnecessary metadata from outbound renditions, preserve original/canonical hashes and transforms. Do not silently resize or send hidden source text. One source image per job, no pages parameter. Bespoke upload thresholds/expiry are deferred, but decoder resource safety, bounded queues and provider hard limits remain required.

## 2. Idempotency, jobs and failure behavior

Atomically persist accepted job, input identity, canonicalized options, resolved profile snapshot and idempotency reservation before dispatch. Same key plus same original image bytes and canonical options returns the original scan (202, including if already terminal), without re-resolving all_enabled or billing again. Same key with different image/options returns 409. Repeated concurrent submissions must create only one job. The same bytes with a new key intentionally create a new run.

State progression: queued → running → completed / partially_completed / failed. On process restart, nonterminal jobs/runs become interrupted; no automatic possibly billable replay. An interrupted job remains retrievable with earlier successful profile results. Run states: queued, running, completed, failed, interrupted. completed means computation succeeded, not payment correctness.

- All runs completed: job completed. Mixed completed/failed: partially_completed. All failed: failed. interrupted overrides final aggregation when recovery cannot establish completion.
- Each run succeeds or fails independently; no majority-vote merge. In compare, final_result_id is always null. In extract, it references the single completed run; otherwise null. Clients read its payment object, not a duplicated second draft.
- Preserve completed comparison results while other runs execute. No streaming endpoint in v1; polling is sufficient.
- One API process owns bounded workers; initially at most two outbound calls. Default live smoke profile: one attempt (no auto-retry), 90-second stage timeout, 240-second job deadline. Later transient retries must be explicitly profile-versioned, bounded and charged. Ambiguous billed timeouts are never silently retried.
- Caller disconnect is not cancellation. DELETE rejects active jobs; restart interruption is not proof upstream processing stopped. Keep a minimal idempotency tombstone after local deletion: reuse returns 410, not another paid run. Tombstone retains only key/request digest and deleted marker, not invoice data.
- Error responses: {error:{code,message,retryable,details}} with sanitized details. 400 malformed bytes/JSON, 401 bad/missing token, 404 missing job, 409 key conflict/active deletion, 410 deleted-key reuse, 415 unsupported image format, 422 options/profile validation, 429 bounded queue full, 503 storage/service unavailable. 413 only for an actual documented enforced infrastructure/provider limit, not an invented product threshold.
- Per-run error codes include provider_auth, provider_quota, provider_timeout, provider_refusal, provider_unavailable, unsupported_language, invalid_provider_output and internal_error. Preserve safe stage ID/request ID, not provider raw error bodies.

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
- needs_review: useful draft with conflicting/missing/unreadable critical values, inferred currency, unresolved beneficiary association, invoice_total under the historical strict policy, uncertain reference requirement, multiple destinations, or nonpositive/credit amount. Do not convert an invoice total into amount_due.
- insufficient_data: no meaningful payment option can be assembled (for example unrelated image or reference-only bill without routing). Retain successfully extracted observations. Malformed bytes instead fail input validation; unsupported_input is not a payment-review state.

Opt-in `payment-draft@1` accepts `invoice_total` while preserving its role, and can fill a missing beneficiary from supported candidate-linked account-holder or supplier evidence without overriding an explicit recipient. It records the fallback in normalization. It can set `selected_candidate_id` to the preferred bank-transfer option while keeping multiple candidates and `needs_review`; the existing single-candidate `ready_for_review` invariant remains unchanged. Selection never authorizes payment. See [versioned policy](M3_DRAFT_POLICY.md).

Review reasons are stable {code,path,message} objects; paths are JSON Pointers relative to payment. Initial codes: missing_required_field, ambiguous_field, conflicting_candidates, unsupported_payment_route, invalid_account_format, failed_iban_checksum, currency_inferred, amount_role_unresolved, nonpositive_amount, beneficiary_unresolved and reference_requirement_unknown.

Apply deterministic normalization, candidate association, evidence-based UK/HR interpretation and explicit validators after adapters. Do not use model self-confidence to select review state. Never silently O→0, I→1, pad digits or choose a checksum-valid guess. Store bounded alternatives, request a new image or run an explicitly costed reread if configured. No automatic paid/direct-debit rejection or rejection based on historical dates. UK modulus checks are optional later; checksum/format/CoP/account-existence are different claims.

## 6. Run diagnostics and data recipients

Each run includes profile_id/version, state, payment (nullable before completion/on failure), evidence, diagnostics and error (nullable). Diagnostics records requested/returned model/processor, prompt/schema/adapter/rules versions, timings_ms (queue/preprocess/provider/postprocess/total), validation findings, routing (applied_rule_packs and reasons), and stage records. Route only on observations available to that profile; generic, UK and HR rule/prompt variants are separately versioned. Do not make a paid language classifier compulsory. Durations use a monotonic clock; timestamps are UTC ISO 8601. Unknown duration/usage/cost is null, not zero.

Each stage records id/method, local or external execution, provider, endpoint_host, account_alias (never credentials), configured_region, verified_processing_region (nullable), payload_classes, input image/text hashes and rendition, request_id, timing, usage and cost. Payload classes include image, crop, ocr_text, layout and fields. A cloud-OCR→LLM profile records both recipients. A regional endpoint alone is not verified data residency. Routine GET output exposes safe metadata, not raw provider bodies or local filesystem paths; raw responses stay in ignored private storage.

Stages optionally include `requested_model`, `returned_model` and `source_stage_ids`; source links must reference earlier stages in the same run. Historical stages may omit them. A two-call hybrid records both intended stages atomically at acceptance, records each actual dispatch separately, and releases only undispatched provisional records on failure/restart. Required-stage failure keeps earlier private artifacts and diagnostics but returns a failed run, without an implicit payment fallback.

Cost object: status=reported|estimated|unknown|not_applicable, amount decimal string or null, currency or null, pricing_source or null, priced_at or null. Locally computed rules may have zero external fee but are not free infrastructure. Keep per-currency totals separate unless an explicit dated FX conversion exists. Synthetic fixtures carry unknown costs/null usage; their timings are not measurements.

Shared prerequisites are off by default for v1 comparisons so results have independent timing. A later explicitly cached profile must disclose cache hits, real batch charges and separately estimated standalone costs; no hidden reused OCR. There is no local monetary or cumulative-call admission limit, and unknown maximum cost does not require a ceiling before enabling a profile. Actual usage, unknown charges and historical accounting records remain reportable without affecting admission.

## 7. Contract tests required during coding

Generate API models and schemas from one typed source. Validate the two synthetic examples, plus negative and boundary fixtures; test unknown fields, enums, decimal strings, evidence IDs/coordinates, missing states, candidate IDs, cross-pair prevention, review rules, extract/compare semantics, idempotency races, restart and deletion tombstones. The supplied JSON Schema validates structural shape; business invariants above require code tests and must not be delegated to an LLM.

## Private mobile review inspector (additive, 9 October 2026)

All nullable observation values in `GET /v1/scans/{scan_id}` remain explicit `null`, and original candidates, warnings, evidence and decimal/digit strings are preserved. Mobile and admin pretty-print this response without stripping nulls. Null result rows can be omitted in the mobile presentation without changing those observations. The additive 13 October review guidance below is computed at read time.

`GET /admin` serves a private inspector shell with no scan data. Its data requests require the same bearer token as the scan API. The page keeps that token in memory only, uses no-store responses and self-only assets, and never sends extraction requests. It is intended for the trusted local setup, not public hosting.

- `GET /v1/admin/scans?limit=50&offset=0&source=mobile`: scan metadata, outcome list, resolved profile IDs, source and confirmation counts. The optional `source` filter is `mobile` or `automated` and is applied before pagination. `limit` is 1–100, `offset` is nonnegative, and `next_offset` is nullable. The list contains no invoice field values.
- `GET /v1/admin/scans/{scan_id}/artifacts`: retained provider responses grouped by recorded run and stage, plus saved OCR text/layout and the OCR input passed to a hybrid LLM. Each output has `kind`, its original JSON `value`, and a nullable read `error`. Polling/error responses are preserved in arrival order. Historical run-level responses are assigned to a stage only when there is exactly one external stage; otherwise they remain unassigned run output. Missing outputs are explicit and never regenerated. This is separate from the normalized original scan result.
- `GET /v1/admin/scans/{scan_id}/image`: original JPEG/PNG upload bytes, verified against `input.original_sha256`, with their image MIME type. Only scans recorded as mobile are eligible; missing/nonmobile/deleted images return 404, and a saved hash mismatch returns 503. The provider's canonical rendition is not substituted. Both new reads require the same bearer token and return `Cache-Control: no-store`; the image is fetched with Authorization and displayed through a temporary blob URL, never a token-bearing URL.
- `GET /v1/scans/{scan_id}/reviews`: `{ "reviews": [...] }`, containing separate mobile-confirmed snapshots, in received order.
- `PUT /v1/scans/{scan_id}/reviews/{review_id}`: save one snapshot with a client-generated UUID. Include `schema_version: "1.0"`, the original `run_id`, `selected_candidate_id`, `event: "review_confirmed"`, `simulated: true`, and `values`.

`values` maps JSON pointers to original **Observation nodes** in that run's payment to edited strings or explicit nulls. It must include every document/document-context observation and every observation of exactly the selected candidate at its original array index. For example, `/candidates/0/amount/value` maps to `"123.45"`, `/candidates/0/destination/account_number` to `"00000000"`, and `/due_date` to `null`. These scalars do not replace original observations, confidence, evidence or evaluation labels. No numeric conversion, inferred payment ownership or actual payment occurs.

The saved response adds `id`, `scan_id` and server `received_at`. Identical UUID/body retries return the same record and timestamp. A different body for an existing UUID is 409; active scans are 409; an unknown scan is 404; a non-reviewable run, foreign candidate, missing/extra field or invalid payload is 422. Blank strings must be represented as null. This endpoint records review activity and does not validate a real payment or change provider/budget state. Deleting a scan through the existing deletion endpoint also deletes its associated mobile snapshots.

New submissions accept `X-Scanpay-Client: mobile|automated` (default `automated`). Source is saved separately at first acceptance and cannot be changed by an idempotent replay. Historical evaluation records without source metadata display as automated. This is client-declared UI provenance, not authentication or a payment-verification claim.

The app submits edits only after Pay opens a summary and the user presses Confirm. Keystrokes are not logged. The inspector shows original JSON and mobile-confirmed values separately and highlights differences.

The PoC confirmation accepts a checked, selected, reviewable candidate even when payment fields are incomplete. Missing/invalid fields remain visible in the confirmation summary. This records `review_confirmed` with `simulated=true`; it does not change backend review state or make the candidate executable. Empty/error results and unselected candidates cannot be confirmed.

## Invoice review guidance (additive, 13 October 2026)

Scan reads add optional `runs[].review_guidance` when payment extraction is present. `policy_version` is `invoice-fields@1`. `issuer_country` and `language` contain nullable `value`/`label`, `status` (`observed|inferred|derived|unknown|ambiguous`), `reason`, `evidence_ids` and `excerpts`. Each candidate has `candidate_id`, `route`, separate `account_country`, `fields` and `warnings`. Document rules are under `document_fields`. Field maps use JSON pointers into `run.payment`; each rule has `requirement` (`required|optional|not_applicable|unresolved`) and `reason`. They can include virtual other-route pointers absent from the candidate's discriminated destination shape; those are presentation rules, not editable observation nodes.

This guidance is a deep-copy read projection, including for old scans, and does not replace stored observations, validation, outcomes, evidence or confirmations. No new provider call is made by a read. Country suggestions cannot override positive payment-route evidence. Missing context is not a missing payment field; unresolved routes and real missing required data remain review concerns. Clients retain populated/edited/uncertain fields and may hide optional empty observations. Older clients may ignore this additive object; newer clients have a route-based fallback when it is absent. Review uploads still enumerate only actual observation nodes, never virtual guidance pointers.

Opt-in compact extraction profiles can add `diagnostics.context_explanations` with short model-supplied explanations for `language`/`issuer_country` and linked evidence excerpts with `grounding: model_claim`. Historical profiles/results omit that empty dictionary. Country labels and flag glyphs are presentation conveniences; neither proves country, account ownership or payment validity. See [INVOICE_CONTEXT.md](INVOICE_CONTEXT.md) for the single-call prompt and evidence.

## Local connection status (additive, 9 October 2026)

Authenticated `GET /v1/admin/connection` returns `automatic` (boolean), `refresh_seconds` (nullable integer), `checked_at` (nullable timestamp of the last successful interface check), `addresses` (URL, interface identifier and `network|link_local` kind) and `warnings` (strings). The managed Mac launcher reports only successfully bound private/link-local IPv4 listeners. Loopback is not advertised as a phone URL. Discovery failure retains the previous listener list and check time with an explicit warning; bind failures are excluded and retried by the launcher. Responses are no-store and contain no token. Reads do not enumerate interfaces, dispatch inference, alter selection or change drafts.

Ordinary manual Uvicorn startup reports `automatic=false` and, when the request's actual server socket address is private/link-local, that address only. It never treats a client Host header as a discovered address. Listener availability is not proof of connectivity from a particular phone. Existing scan, review, profile and identity semantics are unchanged.
