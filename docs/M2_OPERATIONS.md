# Provider breadth and full-corpus operations

**Current continuation (9 October):** see [coding handoff](CODING_HANDOFF.md) and [mobile checkpoint](MOBILE_CHECKPOINT.md). The dated Phase 2 text below is historical; its old implementation/approval gates do not govern the current work.

**Historical Phase 2 checkpoint — 8 October 2026:** Phase 2 is closed for the current PoC scope. Direct-image GPT-4.1 mini (`openai-mini-image-roles-v3@2-5094b6dc13ef5718`) is selected for mobile integration. See [Phase 2 closeout](PHASE2_CLOSEOUT.md) for the decision, limits and verification, and [fourth-chat handoff](CHAT4_HANDOFF.md) for the prepared baseline. Markus authorized commit/push and the earlier PR/merge sequence; the supplied mobile brief is in MOBILE_UX_BRIEF.md and the new-chat prompt is in CHAT4_PROMPT.md. No new chat or mobile code yet. Earlier status/default/approval statements below are historical snapshots superseded by this checkpoint.

Updated 8 October 2026. This extends the M1 operations guide. The API remains JPEG/PNG-only. Credentials and resource settings remain in the existing ignored `.env`; do not replace that file.

## Profiles and boundaries

`ProfileConfig.options` adds independently named `ModelOption` entries. Each pins provider, model/processor version, operation, output limit, optional reasoning setting, rules revision, protocol/schema mode, readiness metadata and its own tariff. The registry snapshots the option plus a hash of selected resource bindings. Caller requests still contain only profile IDs. Changing a versioned option does not rewrite stored runs. The original two profile identities and default extraction choice remain unchanged.

Supported operations are direct-image vision (OpenAI, Mistral, Anthropic, Gemini, xAI, Together), OCR/rules (Mistral, Azure, Google Document AI, AWS), invoice mapping (Azure, Google, AWS, Mindee), and Mistral annotations. Document products map only their actual fields; unsupported bank details stay missing. No hidden OCR augmentation, provider substitution or majority merge occurs.

`providers.options.example.json` is a disabled developer template, not a file Markus needs to fill in. The working private configurations and credentials are already set up. The example shows which model/method settings a future developer can copy when adding a profile; cloud IDs and keys belong in `.env`, never in this template. Select a profile by its ID when submitting a scan. The current offline-replayed configuration is `.local/m3-partial-2026-10-08/providers-current.json`; the fresh-inference baseline is preserved in `.local/m2-repeatability-2026-10-07/providers.json`; the existing default configuration stays separate so experiments are enabled deliberately.

Azure/Mindee polling retrieves the same job without issuing a second inference. Every HTTP response is saved as a distinct private artifact. Returned polling URLs must match the selected host and an allowed read path; redirects are disabled. Original and normalized document observations are separate from payment interpretation. Provider-native geometry remains explicitly native; rules 1/2 consume text/markdown structure; rules 3 adds bounded unique adjacency in supported native coordinate spaces, without claiming general layout understanding.

OCR → OpenAI text composition is now offline-tested through an explicitly configured hybrid, with two atomic per-stage reservations and separate recipients. See [M3 interpretation](M3_INTERPRETATION.md). Existing single-call options still reserve one inference; unknown vendor-internal step charges remain unknown. No new hybrid is enabled by this change.

## Result policy

Read `run.outcome` for success/incomplete/error, not execution `state`. Incomplete retains fields and uncertain alternatives; a completed response with zero invoice/payment fields has outcome error and finding `no_usable_data`. Raw OCR text alone does not count as mapped fields. Historical stored results omit the additive field; CLI summaries derive it. See [contract](API_CONTRACT.md) for exact semantics.

`field_policy=partial_v1` is available for compact protocols 5/6 only and changes the profile version. It isolates malformed fields with explicit findings, keeps their raw private response and preserves candidate positions. Strict remains the default for historical configurations. The seven selected compact methods are enabled with the new policy in the current private catalogue. Replay all 45 preserved source batches with the private `.local/m3-partial-2026-10-08/replay.py` script: it has no network client, verifies source hashes and never modifies original batches/results. The new profiles are not marked live-validated by this offline operation. There is no additional inference allowance.

## Budget continuation

The original database and its twelve M1 dispatches/€12 holds remain authoritative. A private profile configuration may contain:

```json
{
  "budget_plan": {
    "reference": ".local/evaluation/dated-plan.json",
    "cumulative_call_cap": 100,
    "cumulative_hold_eur": "30"
  }
}
```

These are cumulative ledger caps, not additional allowances. Beyond the initial tranche a documented plan is required; the hard project maximum remains €500. The plan must exist as reviewable evidence before execution: current ledger totals, full matrix, recipients, checked terms/region/tariffs, output limits, ceilings and stop rules. Set `SCANPAY_PROFILES_FILE` in the launching process to the new private config; keep the established root `.env` intact. Never delete/reset the ledger, release uncertain dispatched holds, or treat credits as measured cost. Settings are read only at startup.

## Corpus, execution and recovery

Inventory a directory of prepared images, retaining explicit failures:

```sh
.venv/bin/python -m evaluation.corpus --help
```

The current private manifest is `.local/evaluation/m2-corpus-2026-10-06/manifest.json`: 27 prepared page images plus four supplied images, 31 inputs total. It accounts for all 12 inventory files, including provenance metadata. Source/page/variant grouping and exact duplicate relationships are retained. Grouping is conservative and labels are unverified. Never skip an image merely because it duplicates another rendition.

Create a batch state with `evaluation.batch.new_batch(manifest, {profile_id: exact_version}, unique_batch_id)` and save it privately with `evaluation.batch.save`. Every matrix cell is recorded before submission. Obtain exact versions from the configured local `/v1/profiles` response; no provider inference happens during profile listing. The runner verifies manifest hashes and current profile versions before proceeding:

```sh
.venv/bin/python -m evaluation.batch \
  --manifest .local/evaluation/m2-corpus-2026-10-06/manifest.json \
  --state .local/evaluation/REPLACE-batch.json --url http://127.0.0.1:8765
```

Run at most two profile batches concurrently against the one local server. The state file records accepted scan IDs and stable idempotency keys before and after submission. Resuming uses the same key for uncertain acceptance and polls existing accepted work. A new batch ID deliberately requests fresh paid inference; it is not a recovery mechanism.

Authentication, quota, budget and HTTP 400/404/422 failures stop the remaining rows with explicit `not_run` reasons. Individual document/schema validation failures remain recorded outcomes. No automatic retries occur. An early-stopped profile leaves M2 incomplete until its blocker is resolved or the user explicitly removes it from scope. Before resuming, diagnose the saved private error and review the plan. Do not repeat a known invalid request over the corpus.

## Saved-response replay

Replay is a separate local operation and preserves original provider charges/provenance:

```sh
.venv/bin/python -m evaluation.replay \
  --manifest .local/evaluation/m2-corpus-2026-10-06/manifest.json \
  --source .local/m2-2026-10-06/first-batch.json \
  --artifacts .local/backend/jobs \
  --output .local/evaluation/REPLACE-rules-replay.json
```

The full matrix must match. Every input either has a saved OCR observation replayed through rules 1, 2 and 3 or an explicit gap. Existing replay files cannot be overwritten. Replays are not fresh recognition evidence, do not affect live-validation flags and do not establish accuracy.

## Cost evidence

`evaluation.cost_report` writes private Markdown/JSON/CSV with exact profile versions, coverage, every external stage and unknown charges. Its `--options` input is the option dictionary, not the enclosing profile configuration. Generated reports stay under ignored `reports/cost-comparison/`. Keep old and revised batches separate; an earlier failed attempt is never replaced by a later successful one. USD gross estimates, EUR reservations, trial allowances and cash invoices are distinct. Cost per correct result remains null until labels are verified. See [COST_REPORT_PLAN.md](COST_REPORT_PLAN.md) for the M4 deliverable.

## Account-limit follow-ups

Azure's first live responses identified the resource as **F0**. Fast polling then hit HTTP429; no tier upgrade was made. The explicitly versioned paced profiles wait five seconds before polling and between further polls. Their batches run sequentially on the Azure resource, with `--inter-input-seconds 2`. These delays are part of measured stage/batch latency, not claimed provider compute time. Polls never resubmit inference; a throttled earlier run remains a separate failure/uncertain charge. New private raw-response artifacts preserve selected operation-location/retry/request-ID headers for diagnosis.

`mapping_version=2` normalizes explicit `€`/`£` and valid ISO currency tokens to the contract format while preserving the returned raw token and evidence. Ambiguous dollar/unknown symbols remain ambiguous. Version1 is unchanged.

AWS Textract returned `SubscriptionRequiredException` for both operations despite successful dedicated-user authentication. The console redirected to incomplete registration / free-plan limitations; the limited IAM user cannot inspect billing. The user then confirmed upgrading the account to the paid plan. A seventh bounded plan adds two fresh 31-input AWS matrices under a cumulative ceiling of 801 calls / €245.90; both operations completed all 31 inputs successfully. Preserve the earlier blocked attempts separately. No IAM or credential changes were needed.

The paced Azure Read and Invoice matrices both finished 31/31 successfully. The AWS post-activation matrices also finished 31/31 each. Current results are maintained in IMPLEMENTATION_STATUS.md.

## Latest compatibility profiles

The current catalogue retains 15 selected options plus the original default profiles. Protocol 5 uses compact printed readings and typed destinations; Gemini protocol 6 uses equivalent single-value enums for fixed tags. The public v1 API and old profile versions remain unchanged. Thinking is explicitly disabled for Together. Google Invoice uses mapping 2. All latest selected batches cover 31 inputs; residual document failures are listed in IMPLEMENTATION_STATUS.md.

The private progress overview is `reports/overview-2026-10-07/index.html`; it embeds aggregate results only and works offline. Regenerate it with `.local/m2-compat-2026-10-07/build_overview.py` when intentionally updating the selected evidence. This is separate from the final findings report. No fresh inference is required to regenerate it.


## Three-run repeatability evidence

The approved 7 October follow-up completed two additional full-corpus rounds for every selected method, using the same profile versions and prepared images. All 930 new outcomes and 465 baseline outcomes remain separate. Private evidence and generators are under `.local/m2-repeatability-2026-10-07/`; results are in `reports/repeatability-2026-10-07/`. Regenerating diagnosis and reports reads saved responses only. Do not invoke the paid runner to regenerate a report.

`evaluation.repeatability` compares normalized linked payment candidates while preserving uncertainty and selection. See EVALUATION_PLAN.md for the stability denominator and exclusions. Total/provider median, nearest-rank p95, maximum and timeout counts remain stored, including failures. The inference server is stopped. Existing budget reservations remain intact; new paid work needs a separate plan.
