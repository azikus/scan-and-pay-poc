# European hosting and model-training controls

Checked on **12 October 2026**. This document records provider options and account setup. The backend supports explicitly configured European OpenAI and Mistral endpoints while preserving global integrations. It does not require proof of European account eligibility, a no-training attestation, or a known verified processing region before accepting a profile.

## Backend behavior

OpenAI model options accept `api.openai.com`, `eu.api.openai.com` and the already supported starter endpoint `us.api.openai.com`. Mistral model options and starter OCR accept `api.mistral.ai` and `api.eu.mistral.ai`. The operator selects the endpoint explicitly; defaults, saved selection and existing configurations are unchanged. The normal checks for supported endpoints, credentials and profile readiness still apply.

Missing or unknown account approval does **not** block a scan locally. A missing `verified_processing_region` remains unknown in diagnostics and does not disable the profile. No European approval gate, approval-expiry check or policy-specific rejection is installed. Existing global OpenAI profiles continue to work without regional approval. If an operator chooses an EU endpoint, the provider can still reject requests for account or model reasons; the backend reports that provider response without silently changing endpoints.

OpenAI requests retain `store=false`. Training preferences are managed by provider account settings and terms; the backend cannot enable an account opt-out through an invented request flag. Account requirements below are operational documentation, not backend admission rules.

## What leaves the device

After an explicit Send, the mobile app uploads the invoice image to the Mac backend. A direct hosted-model or cloud OCR method then sends image content to its provider. An OCR → LLM method has two recipients: the OCR provider receives the image, and the interpreter receives extracted text/layout. Local rules process the returned content on the backend. Images and extracted text may contain the same personal or banking information, so both recipients matter.

## European processing options

| Service | European option | What to verify |
| --- | --- | --- |
| OpenAI API | `eu.api.openai.com`; Europe means EEA + Switzerland. | Account/project eligibility, supported model/features, the required abuse-monitoring controls and Modified Retention amendment. Image inputs need enhanced Zero Data Retention or enhanced Modified Abuse Monitoring approval. An endpoint hostname or successful model listing alone does not establish account eligibility. [Data controls](https://developers.openai.com/api/docs/guides/your-data). |
| Mistral hosted API | `api.eu.mistral.ai`; documented geography includes EU and EFTA countries. | Availability of the exact model and operation in the regional catalogue. Stateful features such as Agents, Batch and Files have regional limitations. The global endpoint has no location commitment. Regional inference does not regionalize all account or operational metadata. [Regional inference](https://docs.mistral.ai/inference/regional-inference). |
| Google Document AI | EU processor location with `eu-documentai.googleapis.com`. | Matching processor location/version and regional service support. Document AI is a separate product from the Gemini Developer API. [Regions](https://docs.cloud.google.com/document-ai/docs/regions), [security and content use](https://docs.cloud.google.com/document-ai/docs/security). |

For other providers and hosting products, obtain the exact service's current regional and content-use terms before describing them as European. A provider's headquarters, an open-weight model, or a server's hostname alone does not establish how invoice content is handled. This review did not live-validate other European routes.

## Keeping images and outputs out of training

OpenAI API inputs and outputs are excluded from model training by default unless the organization explicitly opts into sharing. Inspect the relevant organization's data-sharing controls; ChatGPT settings are separate. No-training status does not itself establish European processing eligibility. [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data).

For Mistral, inspect the organization's API Privacy controls and disable API model training and Labs participation where offered. Retain dated evidence of both settings and the applicable account terms. Do not assume a Le Chat or Vibe preference applies to API requests. [Training controls](https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models).

Google states that customer documents and predictions are not used to train its Document AI models. Verify the relevant Cloud service and processor rather than applying that statement to every Google AI product. [Document AI security](https://docs.cloud.google.com/document-ai/docs/security).

No-training and retention are separate controls. A provider may retain content for operational or safety purposes while excluding it from training; OpenAI's `store=false` is not a universal zero-retention guarantee. Review retention terms, exceptions and subprocessors separately. [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data), [Mistral zero data retention](https://docs.mistral.ai/admin/monitor-comply/zero-data-retention).

## Manual setup and verification

1. Identify the exact organization/project, API product, model and operation receiving images or OCR text. Include both stages of a hybrid method.
2. Obtain the applicable processing agreement and regional eligibility confirmation. Define the required geography explicitly: EU member states, EEA, and EFTA are different boundaries.
3. Review training/data-sharing settings in that account and save dated evidence privately. Record retention separately.
4. If adopting a regional route, configure its supported endpoint and compatible account/project explicitly. Confirm adapter support before changing an existing profile; this PR adds the regional hostname support described above but does not migrate configurations.
5. Check model availability, then use a synthetic invoice for functional verification. Record the actual destination, exact model, timestamp, request identifier where available and any fallback or redirect. A successful response establishes functionality, not independent proof of physical server location.
6. Recheck settings and terms when accounts, keys, models or provider features change. Regional processing claims do not cover every category of operational metadata or automatically establish legal compliance.

## Checks completed on 12 October

The signed-in Mistral API Privacy page showed API model training and Labs **off**. Both settings were already disabled; no account toggle was changed.

One synthetic invoice was processed by each of `mistral-small-2603` and `mistral-ocr-4-1` through `api.eu.mistral.ai`. Both returned useful typed drafts with the expected synthetic amount and linked UK bank details. The drafts remained **incomplete**, with beneficiary/account-holder information requiring review. No retry or fallback occurred. Provider-stage durations were approximately 3.03 seconds and 1.34 seconds respectively, one sample per model; these are not mobile capture-to-review measurements or full accuracy results.

The European OpenAI model catalogue returned the selected mini model, but European image inference was not run: Markus confirmed that supplier approval had not been requested. Catalogue availability does not replace that approval. Google Document AI was not live-tested in this check.

These results describe temporary test configuration, not a migration of the running service. Existing provider configuration, credentials and saved selection were preserved. No real invoice was uploaded in these checks. Account screenshots, provider responses and synthetic test evidence remain private under `.local/europe-live-2026-10-12/`.
