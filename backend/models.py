"""Single typed source for v1. Business readiness is computed by review.py."""

import re
from collections.abc import Iterator
from typing import Annotated, Any, Literal, Self

import pycountry
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Text = Annotated[str, Field(min_length=1)]
Milliseconds = Annotated[float, Field(ge=0, allow_inf_nan=False)]
DecimalText = Annotated[str, Field(pattern=r"^-?[0-9]+(?:\.[0-9]+)?$")]
AMOUNT_VALUE_PATTERN = r"^-?[0-9]+\.[0-9]{2}$"
CURRENCY_PATTERN = r"^[A-Z]{3}$"


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True, allow_inf_nan=False)


class Alternative(Model):
    value: Text
    reason: Text
    evidence_ids: list[Text] = Field(default_factory=list)


class Observation(Model):
    value: Text | None = None
    raw_text: Text | None = None
    state: Literal["observed", "missing", "unreadable", "ambiguous", "inferred", "unsupported"] = (
        "missing"
    )
    origin: Literal["document", "barcode", "caller_hint", "derived"] = "document"
    evidence_ids: list[Text] = Field(default_factory=list)
    normalization: list[Text] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def value_matches_state(self) -> Self:
        if (self.value is not None) != (self.state in {"observed", "inferred"}):
            raise ValueError("Observation state and value disagree")
        return self


class Evidence(Model):
    id: Text
    image_id: Text
    excerpt: Text | None = None
    bbox: list[Annotated[float, Field(ge=0, le=1)]] | None = Field(
        default=None, min_length=4, max_length=4
    )
    grounding: Literal["ocr_span", "barcode_payload", "model_claim", "synthetic_fixture"]
    source_stage_id: Text

    @model_validator(mode="after")
    def geometry(self) -> Self:
        if self.bbox is not None:
            x, y, w, h = self.bbox
            if x + w > 1.000000001 or y + h > 1.000000001:
                raise ValueError("Evidence box exceeds canonical image")
        return self


class UKDestination(Model):
    kind: Literal["uk_domestic"] = "uk_domestic"
    sort_code: Observation = Field(default_factory=Observation)
    account_number: Observation = Field(default_factory=Observation)


class IBANDestination(Model):
    kind: Literal["iban"] = "iban"
    iban: Observation = Field(default_factory=Observation)
    bic: Observation = Field(default_factory=Observation)


class BillerDestination(Model):
    kind: Literal["biller_reference"] = "biller_reference"
    scheme: Observation = Field(default_factory=Observation)
    biller_code: Observation = Field(default_factory=Observation)


class UnresolvedDestination(Model):
    kind: Literal["unresolved"] = "unresolved"
    reason: Text


Destination = Annotated[
    UKDestination | IBANDestination | BillerDestination | UnresolvedDestination,
    Field(discriminator="kind"),
]


class Amount(Model):
    value: Observation = Field(default_factory=Observation)
    currency: Observation = Field(default_factory=Observation)
    role: Literal["amount_due", "invoice_total", "instalment", "other", "unknown"] = "unknown"


class Remittance(Model):
    reference: Observation = Field(default_factory=Observation)
    model: Observation = Field(default_factory=Observation)
    purpose_code: Observation = Field(default_factory=Observation)
    reference_requirement: Literal["required", "not_stated", "unknown"] = "unknown"


class Candidate(Model):
    id: Text
    account_country: Observation = Field(default_factory=Observation)
    beneficiary_name: Observation = Field(default_factory=Observation)
    account_holder_name: Observation = Field(default_factory=Observation)
    amount: Amount = Field(default_factory=Amount)
    destination: Destination
    remittance: Remittance = Field(default_factory=Remittance)


class Reason(Model):
    code: Text
    path: Annotated[str, Field(pattern=r"^/")]
    message: Text


class Review(Model):
    state: Literal["ready_for_review", "needs_review", "insufficient_data"] = "insufficient_data"
    user_confirmation_required: Literal[True] = True
    reasons: list[Reason] = Field(default_factory=list)


class DocumentContext(Model):
    language: Observation = Field(default_factory=Observation)
    issuer_country: Observation = Field(default_factory=Observation)


class PaymentFields(Model):
    document_context: DocumentContext = Field(default_factory=DocumentContext)
    supplier_name: Observation = Field(default_factory=Observation)
    invoice_number: Observation = Field(default_factory=Observation)
    customer_number: Observation = Field(default_factory=Observation)
    description: Observation = Field(default_factory=Observation)
    due_date: Observation = Field(default_factory=Observation)
    candidates: list[Candidate] = Field(default_factory=list)


class Payment(PaymentFields):
    selected_candidate_id: Text | None = None
    review: Review = Field(default_factory=Review)

    @model_validator(mode="after")
    def candidate_links(self) -> Self:
        ids = [c.id for c in self.candidates]
        if len(set(ids)) != len(ids) or (
            self.selected_candidate_id is not None and self.selected_candidate_id not in ids
        ):
            raise ValueError("Invalid candidate identity/selection")
        for c in self.candidates:
            if c.amount.value.value is not None and not re.fullmatch(
                AMOUNT_VALUE_PATTERN, c.amount.value.value
            ):
                raise ValueError("Amount must be a signed decimal string with two decimal places")
            if c.amount.currency.value is not None and (
                not re.fullmatch(CURRENCY_PATTERN, c.amount.currency.value)
                or pycountry.currencies.get(alpha_3=c.amount.currency.value) is None
            ):
                raise ValueError("Currency must use an ISO code or null")
        if self.review.state == "ready_for_review" and (
            len(ids) != 1 or self.selected_candidate_id is None
        ):
            raise ValueError("Ready draft needs a single selected candidate")
        return self


class Cost(Model):
    status: Literal["reported", "estimated", "unknown", "not_applicable"] = "unknown"
    amount: DecimalText | None = None
    currency: Text | None = None
    pricing_source: Text | None = None
    priced_at: Text | None = None

    @model_validator(mode="after")
    def known_cost(self) -> Self:
        if self.status in {"reported", "estimated"} and (
            self.amount is None or self.currency is None
        ):
            raise ValueError("Priced cost requires amount and currency")
        if self.status == "unknown" and self.amount is not None:
            raise ValueError("Unknown cost cannot carry an amount")
        return self


class Rendition(Model):
    image_id: Text
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    transform: list[Text] = Field(default_factory=list)


class Stage(Model):
    id: Text
    method: Text
    execution: Literal["local", "external"]
    provider: Text | None = None
    endpoint_host: Text | None = None
    account_alias: Text | None = None
    configured_region: Text | None = None
    verified_processing_region: Text | None = None
    payload_classes: list[Literal["image", "crop", "ocr_text", "layout", "fields"]] = Field(
        default_factory=list
    )
    input_hash: Text | None = None
    rendition: Rendition | None = None
    request_id: Text | None = None
    duration_ms: Milliseconds | None = None
    usage: dict[str, Milliseconds | None] = Field(default_factory=dict)
    cost: Cost = Field(default_factory=Cost)


class Timings(Model):
    queue: Milliseconds | None = None
    preprocess: Milliseconds | None = None
    provider: Milliseconds | None = None
    postprocess: Milliseconds | None = None
    total: Milliseconds | None = None


class Finding(Reason):
    status: Literal["pass", "fail", "not_checked", "unknown"]


class Routing(Model):
    applied_rule_packs: list[Text] = Field(default_factory=list)
    reasons: list[Text] = Field(default_factory=list)


class Diagnostics(Model):
    requested_model: Text | None = None
    returned_model: Text | None = None
    versions: dict[str, str] = Field(default_factory=lambda: {"schema": "1.0"})
    timings_ms: Timings = Field(default_factory=Timings)
    validation: list[Finding] = Field(default_factory=list)
    routing: Routing = Field(default_factory=Routing)
    stages: list[Stage] = Field(default_factory=list)


class Error(Model):
    code: Text
    message: Text
    retryable: bool = False
    details: dict[str, str | float | bool | None] = Field(default_factory=dict)


class ErrorResponse(Model):
    error: Error


class Run(Model):
    id: Text
    profile_id: Text
    profile_version: Text
    state: Literal["queued", "running", "completed", "failed", "interrupted"] = "queued"
    payment: Payment | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    diagnostics: Diagnostics = Field(default_factory=Diagnostics)
    error: Error | None = None

    @model_validator(mode="after")
    def completed_payment(self) -> Self:
        if (self.state == "completed") != (self.payment is not None):
            raise ValueError("Only completed runs carry payment drafts")
        if self.state == "completed" and self.error is not None:
            raise ValueError("Completed run cannot have an error")
        ids = [e.id for e in self.evidence]
        stages = [s.id for s in self.diagnostics.stages]
        if len(ids) != len(set(ids)) or len(stages) != len(set(stages)):
            raise ValueError("Duplicate evidence/stage ID")
        if any(e.source_stage_id not in stages for e in self.evidence):
            raise ValueError("Unknown evidence stage")
        for obs in observations(self.payment):
            refs = obs.evidence_ids + [ref for a in obs.alternatives for ref in a.evidence_ids]
            if not set(refs).issubset(ids):
                raise ValueError("Unknown evidence ID")
        return self


class Hints(Model):
    language: Annotated[str, Field(pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")] | None = None
    issuer_country: Annotated[str, Field(pattern=r"^[A-Z]{2}$")] | None = None

    @field_validator("issuer_country")
    @classmethod
    def iso_country(cls, value: str | None) -> str | None:
        if value is not None and pycountry.countries.get(alpha_2=value) is None:
            raise ValueError("Issuer country hint must be an ISO alpha-2 code")
        return value


class Options(Model):
    mode: Literal["extract", "compare"]
    profiles: list[Text] | Literal["all_enabled"]
    hints: Hints = Field(default_factory=Hints)

    @model_validator(mode="after")
    def selection(self) -> Self:
        if isinstance(self.profiles, list):
            if not self.profiles or len(set(self.profiles)) != len(self.profiles):
                raise ValueError("Profiles must be nonempty and unique")
        if self.mode == "extract" and (
            not isinstance(self.profiles, list) or len(self.profiles) != 1
        ):
            raise ValueError("Extract requires exactly one profile")
        return self


class ImageInput(Model):
    image_id: Text
    original_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    canonical_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    mime_type: Literal["image/jpeg", "image/png"]
    hints: Hints = Field(default_factory=Hints)


class ProfileRef(Model):
    id: Text
    version: Text


class ExcludedProfile(Model):
    id: Text
    reason: Text


JobState = Literal["queued", "running", "completed", "partially_completed", "failed", "interrupted"]


class Accepted(Model):
    schema_version: Literal["1.0"] = "1.0"
    scan_id: Text
    state: JobState
    status_url: Text


class Scan(Model):
    schema_version: Literal["1.0"] = "1.0"
    execution_kind: Literal["live", "synthetic_fixture"]
    scan_id: Text
    mode: Literal["extract", "compare"]
    state: JobState = "queued"
    created_at: Text
    updated_at: Text
    input: ImageInput
    resolved_profiles: list[ProfileRef]
    excluded_profiles: list[ExcludedProfile] = Field(default_factory=list)
    runs: list[Run]
    final_result_id: Text | None = None

    @model_validator(mode="after")
    def associations(self) -> Self:
        ids = [r.id for r in self.runs]
        if len(ids) != len(set(ids)) or not ids:
            raise ValueError("Invalid run IDs")
        if [(r.profile_id, r.profile_version) for r in self.runs] != [
            (p.id, p.version) for p in self.resolved_profiles
        ]:
            raise ValueError("Run/profile snapshots disagree")
        if self.mode == "extract" and len(self.runs) != 1:
            raise ValueError("Extract needs one run")
        completed = [r.id for r in self.runs if r.state == "completed"]
        expected_final = completed[0] if self.mode == "extract" and completed else None
        if self.final_result_id != expected_final:
            raise ValueError("Invalid final result")
        states = [r.state for r in self.runs]
        valid_state = {
            "queued": all(s == "queued" for s in states),
            "running": True,
            "completed": all(s == "completed" for s in states),
            "partially_completed": "completed" in states
            and "failed" in states
            and all(s in {"completed", "failed"} for s in states),
            "failed": all(s == "failed" for s in states),
            "interrupted": "interrupted" in states,
        }
        if not valid_state[self.state]:
            raise ValueError("Job state disagrees with its runs")
        for run in self.runs:
            for e in run.evidence:
                if e.image_id != self.input.image_id:
                    raise ValueError("Evidence belongs to a different image")
                if (
                    e.grounding == "synthetic_fixture"
                    and self.execution_kind != "synthetic_fixture"
                ):
                    raise ValueError("Synthetic evidence in live result")
        return self


def observations(value: Any) -> Iterator[Observation]:
    if isinstance(value, Observation):
        yield value
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            yield from observations(getattr(value, name))
    elif isinstance(value, list):
        for item in value:
            yield from observations(item)
