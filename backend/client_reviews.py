"""Private client review snapshots, separate from immutable extraction results."""

from typing import Literal

from pydantic import BaseModel, Field

from backend.errors import ServiceError
from backend.models import BillerDestination, Model, Observation, Payment, Scan, Text


class ClientReview(Model):
    schema_version: Literal["1.0"] = "1.0"
    run_id: Text
    selected_candidate_id: Text
    event: Literal["review_confirmed"] = "review_confirmed"
    simulated: Literal[True] = True
    # JSON pointers address Observations in the original payment, not replacement evidence.
    values: dict[str, Text | None] = Field(min_length=1)


class SavedClientReview(ClientReview):
    id: Text
    scan_id: Text
    received_at: Text


class ClientReviews(Model):
    reviews: list[SavedClientReview]


class ScanSummary(Model):
    scan_id: str
    created_at: str
    state: str
    execution_kind: str
    source: Literal["mobile", "automated"]
    outcomes: list[str | None]
    profiles: list[str]
    client_review_count: int


class ScanList(Model):
    scans: list[ScanSummary]
    next_offset: int | None


def review_values(payment: Payment, candidate_id: str) -> dict[str, str | None]:
    """All document observations plus exactly one linked candidate, including nulls."""
    result: dict[str, str | None] = {}

    def visit(value: object, path: str) -> None:
        if isinstance(value, Observation):
            result[path] = value.value
        elif isinstance(value, BaseModel):
            for key in type(value).model_fields:
                visit(getattr(value, key), f"{path}/{key}")

    for key in type(payment).model_fields:
        if key not in {"candidates", "review", "selected_candidate_id"}:
            visit(getattr(payment, key), f"/{key}")
    for index, candidate in enumerate(payment.candidates):
        if candidate.id == candidate_id:
            visit(candidate, f"/candidates/{index}")
            return result
    raise ServiceError(422, "invalid_candidate", "Select a candidate from this extraction.")


def validate_review(scan: Scan, review: ClientReview) -> None:
    if scan.state in {"queued", "running"}:
        raise ServiceError(409, "active_scan", "Wait for extraction before confirming a review.")
    run = next((r for r in scan.runs if r.id == review.run_id), None)
    if run is None or run.payment is None or run.result_outcome == "error":
        raise ServiceError(422, "invalid_run", "This run has no reviewable payment draft.")
    expected = review_values(run.payment, review.selected_candidate_id)
    # A phone may be recovering a frozen pre-biller-fields confirmation. Only newly
    # added, wholly absent observations may be omitted; never drop a printed value.
    legacy_absent: set[str] = set()
    for index, candidate in enumerate(run.payment.candidates):
        if candidate.id == review.selected_candidate_id and isinstance(
            candidate.destination, BillerDestination
        ):
            legacy_absent = {
                f"/candidates/{index}/destination/{name}"
                for name in ("notice_number", "creditor_tax_code", "bill_reference")
                if getattr(candidate.destination, name) == Observation()
            }
    for index, candidate in enumerate(run.payment.candidates):
        if candidate.id == review.selected_candidate_id:
            legacy_absent.update(
                f"/candidates/{index}/{name}"
                for name in ("option_label", "due_date", "payment_condition")
                if getattr(candidate, name) == Observation()
            )
    missing = expected.keys() - review.values.keys()
    extra = review.values.keys() - expected.keys()
    if extra or missing - legacy_absent:
        raise ServiceError(
            422,
            "invalid_review_fields",
            "Include every document and selected-candidate observation, with explicit nulls.",
        )
