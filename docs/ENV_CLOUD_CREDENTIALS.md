# Cloud credentials in .env — 13 October 2026

Markus requested that AWS and Google authentication travel with the existing private root `.env`, without interactive setup or native credential-store dependencies. The implementation adds explicit environment credentials while preserving legacy configurations and exact existing profile hashes. None of these secrets is a request option or profile snapshot field; Settings uses SecretStr for each value.

| Provider | Environment fields | Behavior |
| --- | --- | --- |
| AWS Textract | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, optional `AWS_SESSION_TOKEN`; `AWS_REGION` | Both key fields are required if any explicit credential field is populated. Direct SigV4 signing uses these credentials; `AWS_PROFILE` is optional/ignored for credential lookup in this mode. A session token is for temporary keys only. |
| Google Document AI | `GOOGLE_CREDENTIALS_JSON`; existing project/location/processor fields | Full authorized-user or service-account JSON is parsed in memory with the matching typed credential loader, scoped to cloud-platform and the configured quota project, then refreshed for OAuth bearer authentication. No ADC/default file lookup in this mode. |

Google Document AI's documented identity-based [authentication](https://docs.cloud.google.com/document-ai/docs/setup) differs from a Gemini API key. Inline JSON supports the existing authorized-user refresh credentials or a service-account key. The migration uses the current authorized-user identity; it does not create a new service account/key, widen permissions or replace it with an invented API key.

The dotenv value can be one single-quoted JSON line, with embedded private-key newlines represented as JSON `\n`. The private setup builder handles encoding; no credential is printed. Service-account token endpoints are restricted to Google's supported OAuth endpoints. Unsupported credential types, malformed JSON, credential refresh failures or partial AWS keys fail as redacted provider_auth errors without falling back to another identity. An explicitly populated credential field never causes hidden provider fallback.

If explicit fields are completely absent/empty, legacy AWS profiles and Google ADC/file configuration still work. This compatibility path allows existing checkouts/tests to keep functioning; the current operator's env now selects the explicit path. Region/processor/model/endpoints, selection and existing stored result snapshots are unchanged. The Google quota-project header is retained. No credentials are stored in profile definitions, accounting rows or raw diagnostic headers.

## Verification

**745 offline tests pass**. Domain/orchestration coverage is **96.09% statements / 91.46% branches**. Ruff lint/format, strict mypy, generated wire-contract and diff checks pass. Tests cover explicit signing and session tokens, no native fallback, partial-key rejection, typed Google loaders, malformed/unsupported credential objects, quota-project use, Settings redaction and AWS readiness without a profile.

Read-only verification with the staged exact env fields confirmed AWS `scanpay-local` with credential method `explicit`; both Google processor-version GETs returned HTTP200 / DEPLOYED. Native default credential lookup was blocked during that verification. The current live profile versions matched the new source registry. No invoice processing call was made. Private env backups/prepared data and verification live under `.local/env-cloud-migration-2026-10-13/` in the original checkout; no secret values are committed.

## Private setup handoff

The separate private `setup-private-local.sh` embeds the operator's current `.env` and `.local/providers.json` unchanged, including the newly migrated cloud fields. It installs hash-locked dependencies in a local virtual environment and creates only missing local files with owner-only permissions. Existing files are preserved and no questions are asked. It contains actual credentials, stays outside Git, and is not the earlier credential-free source ZIP. Real invoices, database, historical ledger and personal SDK stores are not bundled. Source is pulled separately from GitHub.
