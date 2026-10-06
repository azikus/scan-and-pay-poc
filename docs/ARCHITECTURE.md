# Architecture and data destinations

Handoff design from 1 October 2026, updated 5 October for the hosting clarification and 6 October for the checkpoint/cost-report references. Milestone 1 is implemented; see IMPLEMENTATION_STATUS.md for measured evidence. This diagram describes service boundaries and later consumers, not a production platform or the final HTML report.

The current two-adapter implementation and proposed Phase 2 module boundaries are described in [PHASE2_ROLLOUT.md](PHASE2_ROLLOUT.md). Multi-provider pipelines require stage-specific recipient/raw-artifact/dispatch accounting before use. This refactor has not started; the upfront access set was completed on 6 October, so it is now M2 work under [ROADMAP.md](ROADMAP.md). [PHASE2_ACCESS.md](PHASE2_ACCESS.md) separates completed resource preparation from pending inference checks.

```mermaid
flowchart LR
    C["API / CLI client<br/>One JPEG or PNG"] --> A
    subgraph Local["Local backend"]
        A["Authenticate, decode and persist<br/>FastAPI · SQLite · private files"] --> W["Bounded workers<br/>Selected versioned profiles"]
        W --> R["Map and validate<br/>UK / HR rules · evidence · review"]
        R --> P["Persist drafts and diagnostics<br/>Poll results · user confirmation"]
    end
    subgraph Hosted["Provider-operated services"]
        V["Hosted vision / LLM API<br/>Proprietary or open-weight models"]
        O["Managed OCR / document API"]
    end
    W -->|"Image + task/schema"| V
    V -->|"Field claims"| R
    W -->|"Image"| O
    O -->|"Text / layout / fields"| R
    O -.->|"OCR-to-LLM: separate profile"| V
```

Inference runs through provider-operated APIs. Self-hosted model servers and weight downloads are excluded. The unused original handoff PNG is preserved privately under `.local/archive/pre-main-*/docs/assets/`; the editable diagram above is the current architecture reference.

## Reading the flow

1. An API/command-line client uploads a JPEG/PNG now. Later the native iOS and Android apps call the same service. A developer's API client is not the customer-facing conference UX.
2. FastAPI validates/authenticates input, prepares a canonical oriented image and persists an idempotent job/profile snapshot in SQLite. A bounded worker dispatches approved stages with a spend reservation. Start with one process, not a distributed queue.
3. Extract chooses one pipeline. Compare runs selected profiles independently; it does not merge their votes. Vision receives an image; managed OCR/document services receive an image; OCR→LLM additionally sends extracted text/layout to a second recipient. Only configured stages execute.
4. Local adapters map observations; UK/HR rules preserve route/amount/reference association, normalize safely and compute review reasons. Language/address are supporting hints, not sufficient account-country evidence. A model claim is not bank verification.
5. Private results, stage events, timings, usage and destination records persist locally. Polling returns the common contract. Every draft requires review/confirmation. No user corrections are counted as raw extraction accuracy.

## Stage-level data map

| Profile/stage | What leaves the machine | Recipient | What stays local |
| --- | --- | --- | --- |
| Direct vision | Canonical/provider rendition plus task/schema | Selected OpenAI, Anthropic, Google, Mistral or other enabled provider-operated endpoint, using proprietary or open-weight models | Input hashes, normalized draft, diagnostics, raw response if retained |
| Managed OCR → local rules | Image to OCR; rules send nothing | Selected Mistral/Azure/Google OCR endpoint | Returned text/layout, UK/HR logic, validation |
| Prebuilt document API | Image | Azure Invoice, Google Invoice Parser, Textract or configured commercial API | Raw mapping, missing-field handling, validators |
| OCR → LLM, later | Image to OCR, then text/layout (and image only in an explicitly named variant) to model | Two separately recorded services | Stage association and total/individual costs |
| Barcode/local rules, later | Nothing by themselves; unknown codes do not trigger URL fetches | None for the local stage | Decoded payload and mapped fields |
| Native OCR, mobile phase | Depending on agreed profile, image plus image-linked observations to this backend | Backend, then only configured provider stages | Device work is measured separately |

Every external stage records actual service/host, account alias, configured region, known/unknown processing residency, payload classes, hashes/renditions and request ID. A local server is not local-only processing; text can contain the same sensitive details as the original image. No model/SDK may introduce an undisclosed remote fallback. Account retention/training settings are verified at integration, not assumed from provider branding.

## Persistence and operational boundary

- SQLite: jobs, run/stage status, idempotency, profile/version snapshots, costs and data-destination metadata.
- .local/: private inputs, renditions, raw responses and evaluation labels. Curated source samples stay in samples/ and are never cleanup targets.
- Atomic acceptance before dispatch; completed results survive restart. Nonterminal work becomes interrupted and is not automatically replayed. DELETE rejects active work, removes local terminal artifacts and retains a minimal idempotency tombstone; it cannot erase upstream retention.
- Default loopback binding and local bearer token. Native device access later needs deliberately configured LAN address/security; phone localhost is not laptop localhost.
- Bounded concurrency, timeouts, explicit retry policy, cost reservations and unknown-charge handling. No provider probes or model downloads at startup.

## Later consumers, not first-milestone work

Native mobile capture/review is designed before implementation, iOS first. The attendee companion later reads safe job/stage events and masks private fields; it is separate from the customer flow. Final HTML findings use measured evaluation outputs and clearly labelled limitations. Neither is needed to get this backend working.

The current diagram is editable documentation. Final findings and the [separate cost report](COST_REPORT_PLAN.md) are distinct deliverables.
