# Fourth-chat handoff — technical baseline

**Status:** baseline prepared; Markus will supply the remaining handoff brief later. No fourth chat has been created. Do not infer design approval, device/project details or additional requirements from this placeholder.

## Start here

Continue in `/Users/markusi/Developer/Azikus/scan-and-pay`, remote `git@github.com:azikus/scan-and-pay-poc.git`. Inspect Git status/log and preserve private local files. The closeout work uses `codex/m2-provider-coverage`; inspect the remote for its merged checkpoint before starting a new `codex/` implementation branch. Do not discard this checkout or assume ignored evidence is in Git.

Read `AGENTS.md`, [Phase 2 closeout](PHASE2_CLOSEOUT.md), [coding handoff](CODING_HANDOFF.md), [roadmap](ROADMAP.md), [API contract](API_CONTRACT.md), and [operations](OPERATIONS.md). Follow the coding handoff's remaining read order before implementation. Historical M2/M3 documents describe experiments, not instructions to restart them.

## Settled choice

- One direct-image call to `gpt-4.1-mini-2025-04-14`.
- Profile `openai-mini-image-roles-v3@2-5094b6dc13ef5718`, active in `.local/providers.json`; exact tested snapshot retained in `.local/phase2-closeout-2026-10-08/providers-selected.json`.
- Compact protocol 5, `partial_v1`, `draft_v4`, printed text only, no barcode decoding, bank-transfer preference and explicit payer/payee/account-holder distinctions.
- No automatic provider fallback or retry. Gemini is a measured alternative, not an enabled second call. OCR → LLM did not justify its extra stage for the current selection.
- Correctness and speed determine selection; expense stays recorded within the €500 cap.

## Existing API and mobile behavior

Backend: Python 3.12, FastAPI/Pydantic, SQLite, private local files, one process and at most two workers. It accepts one JPEG/PNG, with EXIF orientation and metadata handling. The mobile client converts HEIC before upload; no multipage API or source-PDF text extraction.

1. Configure the Mac's reachable base URL and the local bearer token. Provider API keys stay in the Mac's existing ignored `.env`. Do not place tokens in committed app code or paste them in chat.
2. Read authenticated `GET /v1/profiles`; submit `POST /v1/scans` as multipart `image` plus JSON-string `options`, for example `{"mode":"extract","profiles":["openai-mini-image-roles-v3"]}`. Send a stable `Idempotency-Key` for recovery of the same upload; changed image/options need a new key.
3. Poll the returned location using `GET /v1/scans/{scan_id}`. Execution state and `run.outcome` are different: a completed run may be incomplete or have no usable fields. Find the referenced run via `final_result_id`, then inspect its outcome/payment/review.
4. Render linked candidate fields as editable strings, preserving decimal values and leading zeros. Let the user select an unresolved alternative; do not combine fields across candidates. Preserve useful fields when others are null or malformed.
5. Display missing/ambiguous amounts empty with a needs-input message. An incomplete draft can still have a useful amount. A confidently wrong observed amount is not automatically detectable; mandatory review applies to every draft.
6. Handle service failure, retake, interruption and connection recovery. A disconnect is not cancellation of a paid call. Reuse the accepted job/key rather than automatically resubmitting. Confirmation is a demo review action, not payment execution.

API details and enums belong to API_CONTRACT.md and generated `contracts/v1/`; do not invent a second mobile wire schema.

## Startup and inference allowance

From the existing checkout, `.venv/bin/uvicorn backend.api:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log` starts the local backend. It is stopped at closeout. The default configuration points to the selected OpenAI profile; `/health` and profile inspection do not call providers. Physical-device access requires explicitly configured LAN binding/security: the iPhone's localhost is the phone, not the Mac. Do not expose the backend publicly.

The active configuration is capped at the current ledger: **2,197 dispatches / €336.05 conservative allowance**. It intentionally permits no new paid calls during handoff. Before real mobile scan testing, create a bounded new plan against the same ledger under the €500 cap and check the selected account's current readiness. Do not reset the ledger, release unknown dispatched charges or rerun completed evaluation batches. Offline synthetic API tests can proceed without provider calls.

## Evidence and follow-ups

- Latest six-direct-provider results: `.local/m3-direct-six-2026-10-08/REPORT.md`, `comparison.json`, `failures.csv`, `COSTS.md` and frozen plans/batches. All 102 attempts recorded; Grok had 14 timeouts and one capacity failure.
- Reviewed key: `.local/m3-name-review-2026-10-08/reviewed-key-r4.json`. Its three explicitly accepted name variants are field-scoped; no fuzzy banking/reference/amount matches.
- Hybrid rescoring: `.local/m3-name-review-2026-10-08/{baseline,roles-2,roles-3}-comparison.json`; original raw runs under the corresponding M3 experiment directories.
- Current 17 masked images: `.local/evaluation/m3-no2d-2026-10-08/manifest.json`. Source originals, earlier manifests and review HTML stay private and intact.
- Original ledger/artifacts: `.local/backend/`. Credentials: root `.env` plus existing SDK-managed cloud stores. None of these are committed.
- Closeout verification/default backup: `.local/phase2-closeout-2026-10-08/`. Reproduce tests using README's offline commands; the latest suite has 651 tests.

Known limitations: partial labels, development-corpus bias, erroneous observed values, reference association, uncertain name/inference grading, small timing sample and no mobile-camera validation. Additional label adjudication can rescore saved responses offline. xAI cost accounting omits separate reasoning output in its historical runtime estimate; the latest report uses returned cost ticks. Fix this separately before relying on a future xAI estimate.

Next authorized direction is M5 design agreement followed by M6 iOS in the next chat. Await Markus's additional brief before finalizing that handoff. No mobile code, final HTML findings, attendee display, Android implementation or barcode decoding belongs to this closeout.
