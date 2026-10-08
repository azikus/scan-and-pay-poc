# Provider access checklist

Implementation follow-up: the credential gate remains satisfied. New integrations consume the existing settings; current terms/resource checks and outcomes are in [M2_INTEGRATIONS.md](M2_INTEGRATIONS.md) and [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). The twelve-dispatch account below is the preserved M1 baseline, not the current ledger total.

Updated 6 October 2026. User instruction: request all credentials upfront and **do not proceed with additional implementation, refactoring or provider tests until the complete set is supplied**. Documentation and access preparation record this gate; they do not start implementation. This supersedes earlier just-in-time credential instructions. A missing commercial trial is a blocker unless Markus explicitly changes scope.

**Current status: the upfront credential/resource set is complete.** Required environment fields for the retained providers are populated. Google ADC/processors are prepared, the AWS temporary profile is authenticated as the dedicated IAM user. Offline implementation may resume. This does not establish inference access or quality for every provider; account terms, actual processing readiness, regions, retention and current prices still need their integration checks before any sample batch.

For the new chat, use [CODING_HANDOFF.md](CODING_HANDOFF.md) and the M2 checkpoint in [ROADMAP.md](ROADMAP.md). This file records access evidence and unresolved integration checks; it is not a request to collect all keys again. Refresh only specific expired/missing access when needed.

**Use the existing project-root `.env` for credentials and connection settings**, including the existing OpenAI/Mistral keys. It is Git-ignored and mode 0600. `.env.example` has matching placeholders, never real credentials. Keep billing tiers, access notes, product-selection prose, documentation URLs and project-phase wording out of these files. Record account/pricing/terms observations privately with integration evidence. The current backend consumes only its implemented settings; adding a future provider's key does not implement or enable that integration. Do not paste secrets into chat, source code or committed examples. Local Google/AWS authentication can be referenced by profile/path in `.env`, while the SDK manages its own credential store. Leave the optional `GOOGLE_APPLICATION_CREDENTIALS` line commented out when using local Application Default Credentials.

## Complete requested set

The following configuration names are implemented. All ten retained provider families have full-corpus attempt records; see the current implementation status.

| Service | Supply locally | Source / qualification |
| --- | --- | --- |
| OpenAI | Existing `OPENAI_API_KEY` | Already configured and used; no new key per model |
| Mistral | Existing `MISTRAL_API_KEY` | Already configured and used; selected vision/OCR/annotation methods evaluated |
| Anthropic | `ANTHROPIC_API_KEY` | [Claude API access](https://platform.claude.com/docs/en/api/overview) |
| Gemini | `GEMINI_API_KEY` | [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key); separate from Document AI authentication |
| xAI | `XAI_API_KEY` | [API quickstart](https://docs.x.ai/developers/quickstart) |
| Azure Document Intelligence | `AZURE_DOCUMENT_INTELLIGENCE_KEY`, `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | [Key/endpoint setup](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/use-sdk-rest-api?view=doc-intel-4.0.0); a usable Document Intelligence resource for Read/Invoice |
| Google Document AI | Local ADC authentication or credential-file path, project ID, processor location, OCR processor ID and Invoice Parser processor ID | [Client setup and processor identifiers](https://docs.cloud.google.com/document-ai/docs/libraries). A Gemini key alone does not configure this service; processor-version selection belongs in profile configuration |
| AWS Textract | Local authenticated AWS profile/mechanism, AWS region and access to the selected Textract operations | [Programmatic access](https://docs.aws.amazon.com/textract/latest/dg/program-access.html). Prefer a profile with temporary/SSO credentials; do not provide root credentials |
| Mindee | `MINDEE_V2_API_KEY` and `MINDEE_MODEL_ID` for the selected invoice extraction schema | [API configuration](https://docs.mindee.com/integrations/client-libraries-sdk/configure-the-client), [model ID/settings](https://docs.mindee.com/models/model-settings) |
| Together hosted open-weight models | `TOGETHER_API_KEY` | [Together API setup](https://docs.together.ai/docs/quickstart), [hosted image input](https://docs.together.ai/docs/inference/vision/overview). The selected hosted Qwen profile has completed its compatibility batch |

Record account aliases, regions, trial/credit limits and known data-use settings in private integration evidence, not environment variables. These checks remain necessary before live calls but are not extra secrets for Markus to fill in. Unknown processing residency/retention stays unknown. Do not buy subscriptions, enable auto-recharge or provision model-serving infrastructure to complete this checklist. Ask Markus about an unavailable product; do not remove it or resume automatically.

The upfront collection is complete; no further setup reply is needed. For future runs, report only concrete missing/expired access without exposing secret values.

## Historical access preparation

The following notes describe setup before sample processing. Current outcomes are in IMPLEMENTATION_STATUS.md.

Google access prepared on 6 October at Markus's request: a new dedicated project uses the existing billing account, Document AI is enabled, local ADC is configured, and EU Enterprise OCR and Invoice Parser resources are enabled. The project/location/processor IDs are saved in `.env`; the optional credential-file variable remains commented out. Management access and deployed default versions were checked, with evidence under `.local/google-documentai-setup/`. No samples were processed. Account terms, selected processor-version suitability and pricing still need their pre-inference checks; this does not waive any other provider from the upfront gate.

AWS access preparation, 6 October: Markus created the account; the console shows a free plan with credit. Installed AWS CLI 2.36.46, created the dedicated `scanpay-local` IAM user and attached a validated custom policy permitting only `AnalyzeExpense` and `DetectDocumentText` in Frankfurt plus local browser sign-in. AWS's own-password-change policy is also attached. No access keys were created. The local `scanpay` profile and `.env` connection fields use `eu-central-1`, preserving unrelated settings. After the user completed password setup, signed in as the IAM user and completed `aws login --profile scanpay --region eu-central-1`. STS verified the dedicated user; SDK-managed temporary credentials stay outside `.env`. Private identity/setup evidence is in `.local/aws-textract-setup/`. No samples were processed; Textract operation execution is not yet live-validated.

Remaining-account preparation, 6 October: Together and Azure Document Intelligence key fields are populated, alongside the earlier LLM providers and Google connection settings. Presence is not a successful access check. In the signed-in Mindee account, selecting the pre-built Invoice template created a model; its ID is saved in `.env`, and the user has supplied the API key. The account displayed a 14-day trial with 200 credits. Model settings displayed no processing-zone preference, six-hour extracted-data retention and delete-on-fetch enabled; these are observed defaults, not guarantees about all data use. Private presence inventory and resource evidence are under `.local/provider-access-2026-10-06/`. No samples, provider inference calls, subscriptions or implementation changes were made.

## Historical setup notes

AWS sign-in follow-up, 6 October: the earlier root session was explicitly signed out before the dedicated IAM login. The profile now has an authenticated `login_session`, and STS confirms `scanpay-local`. Root programmatic access was never authorized. Prior incomplete-login observations remain historical evidence only; the password was not saved in project files.


The user narrowed the provider roster to the services listed above; the removed commercial comparison is no longer an access prerequisite. All required credentials/resource identifiers are now supplied. No backend implementation or provider inference occurred during this access preparation.

- Read AGENTS.md, the handoff read order, IMPLEMENTATION_STATUS.md, PHASE2_ROLLOUT.md and this file.
- At the M1 checkpoint, Luna vision and Mistral OCR/rules were the two implemented profiles. M2 has since completed for the retained roster.
- The user requires **all samples for every provider evaluation batch**. Prepare a private full-corpus manifest, including all prepared image renditions, after the credential gate. Do not revert to the two-image starter subset.
- Main checkpoint: the user explicitly requested cleanup, documentation, commit/push to `main` and a new chat on 6 October. The target was rechecked private/empty before preparing this checkpoint. Read Git log/status and remote refs for publication state; preserve ignored private files. Do not restart account setup.
- Twelve prior provider dispatches and €12 in conservative holds remain. Do not reset the ledger; the original twelve-call cap is exhausted.
- At the access-preparation checkpoint, no backend server was running. Mobile, customer browser UI, final findings and self-hosted inference were outside scope. The user separately authorized a concise private HTML progress explainer on 7 October; see the current handoff.
