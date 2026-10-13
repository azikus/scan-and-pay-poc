# Google Document AI verification — 13 October 2026

Markus requested fixing the two Google Document AI profiles after the earlier all-catalogue run failed authentication before either processing dispatch. Investigation loaded the original root environment and the active worktree, checked exact live profile versions, and exercised `cloud_request` resource/host/path/auth preparation. Its processing POST was replaced by a read-only processor-version GET with no invoice bytes. Both configured versions returned HTTP200 and DEPLOYED. No replacement credentials, permission expansion or code changes were necessary. The exact cause of the earlier failure remains unproven.

Two subsequent actual requests used the previously inspected, full-resolution, barcode-free Croatian invoice and its identical prepared PNG/hash. Each had its own frozen profile and persisted new idempotency key, one processing dispatch and no retry/fallback. These were the first processing dispatches for the two profiles in this follow-up, not replay of a previously completed Google processing request.

| Profile | Exact processor version | Result | Backend seconds |
| --- | --- | --- | ---: |
| Google OCR/rules | `pretrained-ocr-v2.1-2024-08-07` | Completed, incomplete draft requiring review | 7.059 |
| Google Invoice Parser | `pretrained-invoice-v2.0-2023-12-06` | Completed, incomplete draft requiring review | 8.207 |

Authentication and processing now pass; incomplete outputs remain explicit and are not proof of extraction correctness. Timing is n=1 per profile and excludes mobile capture/upload/rendering. No median/p95 or accuracy claim is made.

Two dispatches used EUR0.30 in conservative reservations within existing caps; no added allowance or runtime restart. Actual charges remain unknown in the retained response accounting. Final snapshot: **2,342 reservations, 2,340 dispatched / EUR369.60 held**; caps unchanged **2,350 / EUR370.40**, leaving eight reservations/EUR0.80 for the existing mobile scope. Every prior ledger row, current selection, backend identity and private provider configuration matched the pre-run snapshots.

Private preflight, bounded plan, keys, raw results and verification are in `.local/google-auth-fix-2026-10-13/` in the original checkout. Real invoice fields and source pixels remain ignored/private. The dated earlier failure remains intact in [ALL_CATALOGUE_LIVE_2026-10-12.md](ALL_CATALOGUE_LIVE_2026-10-12.md). No paid processing should be repeated automatically now that verification is complete.

AWS clarification: Markus created/configured the existing IAM user's access key locally with `aws configure --profile scanpay`. Read-only STS confirmed `scanpay-local`, `eu-central-1`, credential provider `shared-credentials-file`. AWS keys remain SDK-managed, root environment selects profile/region, and no Textract processing request was sent. Its earlier processing skip remains recorded. Fireworks and Aya remain removed from the current 31-profile catalogue.

No implementation changed during this verification, so the prior 715-test/96.07% statement/91.37% branch offline checkpoint remains the relevant source check; it was not rerun or relabelled as a new test run.
