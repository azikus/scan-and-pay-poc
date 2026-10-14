"""Printed Italian bill identifiers and draft channels; no network/payment verification."""

import json
import re
from typing import Any

from pydantic import BaseModel

from backend.models import Alternative, BillerDestination, Evidence, Observation, Payment

BILLER_FIELDS = ("scheme", "biller_code", "notice_number", "creditor_tax_code", "bill_reference")
PATTERNS = {
    "biller_code": r"[A-Z0-9]{5}",
    "notice_number": r"[0-9]{18}",
    "creditor_tax_code": r"[0-9]{11}",
    # Private bill references are issuer-defined. Do not impose pagoPA's notice format.
    "bill_reference": r"\S(?:[\s\S]*\S)?",
}
REQUIRED = {
    "pagopa": ("scheme", "notice_number", "creditor_tax_code"),
    "cbill": ("scheme", "biller_code", "bill_reference"),
}


def scheme_key(destination: BillerDestination) -> str | None:
    value = (destination.scheme.value or "").strip().casefold()
    return value if value in REQUIRED else None


def required_fields(destination: BillerDestination) -> tuple[str, ...]:
    key = scheme_key(destination)
    if (
        key == "pagopa"
        and not destination.creditor_tax_code.value
        and (
            destination.biller_code.state == "observed"
            and not destination.biller_code.alternatives
            and valid_format("biller_code", destination.biller_code)
        )
    ):
        return ("scheme", "notice_number", "biller_code")
    return REQUIRED.get(key or "", ("scheme", "biller_code"))


def normalize_identifier(obs: Observation, field: str) -> Observation:
    result = obs.model_copy(deep=True)
    if obs.value is None:
        return result

    def formatted(value: str) -> str:
        if field == "bill_reference":
            return value.strip()
        value = re.sub(r"\s", "", value)
        return value.upper() if field == "biller_code" else value

    value = formatted(obs.value)
    if not value or (obs.raw_text is not None and formatted(obs.raw_text) != value):
        return Observation(
            state="ambiguous",
            origin=obs.origin,
            raw_text=obs.raw_text,
            evidence_ids=obs.evidence_ids,
            alternatives=[
                Alternative(
                    value=obs.value,
                    evidence_ids=obs.evidence_ids,
                    reason="Printed identifier differs; no digit repair accepted",
                )
            ],
        )
    if value != result.value:
        result.value = value
        result.normalization.append("printed_biller_identifier_format")
    return result


def valid_format(field: str, obs: Observation) -> bool:
    return obs.value is not None and re.fullmatch(PATTERNS[field], obs.value) is not None


def grounded(obs: Observation, evidence: list[Evidence]) -> bool:
    by_id = {e.id: e for e in evidence}
    return (
        obs.value is not None
        and obs.state == "observed"
        and obs.origin == "document"
        and not obs.alternatives
        and bool(obs.evidence_ids)
        and all(
            i in by_id and (by_id[i].excerpt is not None or by_id[i].bbox is not None)
            for i in obs.evidence_ids
        )
    )


def channels(destination: BillerDestination, evidence: list[Evidence]) -> list[str]:
    """Only claim channels with printed scheme/organisation evidence, never from country."""
    scheme = scheme_key(destination)
    if scheme is None or not grounded(destination.scheme, evidence):
        return []
    if scheme == "pagopa":
        return ["Your bank’s CBILL/pagoPA service"]
    result = []
    code = normalize_identifier(destination.biller_code, "biller_code")
    if grounded(code, evidence) and valid_format("biller_code", code):
        result.append("CBILL via your bank")
    return result


def deduplicate_notices(payment: Payment, evidence: list[Evidence]) -> Payment:
    """Collapse exact repeated notice claims only; retain all conflicting/partial options."""
    result = payment.model_copy(deep=True)

    def semantic(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                k: semantic(v)
                for k, v in value.items()
                if k not in {"id", "evidence_ids", "raw_text", "normalization"}
            }
        if isinstance(value, list):
            return [semantic(v) for v in value]
        return value

    def merge_evidence(target: BaseModel, source: BaseModel) -> None:
        if isinstance(target, Observation) and isinstance(source, Observation):
            target.evidence_ids = list(dict.fromkeys(target.evidence_ids + source.evidence_ids))
            return
        for name in type(target).model_fields:
            a, b = getattr(target, name), getattr(source, name)
            if isinstance(a, BaseModel) and isinstance(b, BaseModel):
                merge_evidence(a, b)

    seen: dict[str, Any] = {}
    kept = []
    for candidate in result.candidates:
        d = candidate.destination
        if (
            not isinstance(d, BillerDestination)
            or scheme_key(d) != "pagopa"
            or not grounded(d.notice_number, evidence)
            or not valid_format("notice_number", d.notice_number)
            or not grounded(candidate.amount.value, evidence)
        ):
            kept.append(candidate)
            continue
        key = json.dumps(semantic(candidate.model_dump()), sort_keys=True)
        if key in seen:
            merge_evidence(seen[key], candidate)
            if result.selected_candidate_id == candidate.id:
                result.selected_candidate_id = seen[key].id
        else:
            seen[key] = candidate
            kept.append(candidate)
    result.candidates = kept
    return result
