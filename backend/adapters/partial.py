"""Versioned field isolation for typed compact responses; no guessed values or JSON repair."""

import json
from typing import Any

from pydantic import ValidationError

from backend.adapters.compact import CompactExtractionV5, PaymentOptionV5, Reading, extract
from backend.models import Alternative, Evidence, Finding, Observation, Payment
from backend.runtime import Extraction


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys make field associations uncertain")
        result[key] = value
    return result


def recover(text: str, image_id: str, stage_id: str, *, version: str) -> Extraction:
    if version not in {"5", "6"}:
        raise ValueError("Partial field recovery requires typed destinations")
    original = json.loads(text, object_pairs_hook=unique_object)
    if not isinstance(original, dict) or not set(original).intersection(
        CompactExtractionV5.model_fields
    ):
        raise ValueError("No recognizable extraction structure")
    findings: list[Finding] = []
    rejected: list[tuple[str, list[str]]] = []

    def flag(path: str, code: str, message: str) -> None:
        findings.append(Finding(path=path, code=code, message=message, status="fail"))

    def extras(node: dict[str, Any], allowed: set[str], path: str) -> None:
        if set(node) - allowed:
            flag(
                path,
                "unexpected_provider_fields",
                "Unrecognized fields retained only in the private response.",
            )

    def reading(value: Any, path: str) -> dict[str, Any]:
        try:
            parsed = Reading.model_validate(value)
            blank = any(not v.strip() for v in parsed.values)
            contradiction = parsed.basis in {"unreadable", "unsupported"} and bool(parsed.values)
            if not blank and not contradiction:
                return parsed.model_dump()
            code = "contradictory_reading" if contradiction else "blank_provider_reading"
        except ValidationError:
            code = "invalid_provider_field"
        flag(
            path, code, "Field could not be accepted; review the source. Other fields are retained."
        )
        # Preserve exact string claims as uncertain alternatives, never as selected values.
        values = value.get("values") if isinstance(value, dict) else None
        strings = (
            list(dict.fromkeys(v for v in values if isinstance(v, str) and v.strip()))
            if isinstance(values, list)
            else []
        )
        rejected.append((path, strings if len(strings) <= 8 else []))
        return {"values": [], "basis": "unreadable"}

    def required_reading(node: dict[str, Any], key: str, path: str) -> dict[str, Any]:
        if key not in node:
            flag(
                path,
                "missing_provider_field",
                "Expected field was absent; other fields are retained.",
            )
            return {"values": [], "basis": "printed"}
        return reading(node[key], path)

    def enum(node: dict[str, Any], key: str, choices: set[str], path: str) -> str:
        value = node.get(key)
        if isinstance(value, str) and value in choices:
            return value
        flag(
            path, "invalid_provider_field", "Field meaning is unresolved; no meaning was inferred."
        )
        return "unknown"

    cleaned: dict[str, Any] = {}
    root_fields = set(CompactExtractionV5.model_fields) - {"candidates"}
    extras(original, root_fields | {"candidates"}, "/")
    for key in sorted(root_fields):
        path = "/document_context/" + key if key in {"language", "issuer_country"} else "/" + key
        cleaned[key] = required_reading(original, key, path)
    candidates = original.get("candidates")
    if not isinstance(candidates, list):
        flag(
            "/candidates",
            "invalid_provider_candidates",
            "Candidate structure is unusable; document fields are retained.",
        )
        candidates = []
    cleaned["candidates"] = []
    candidate_fields = set(PaymentOptionV5.model_fields) - {
        "destination",
        "amount_role",
        "reference_requirement",
    }
    for index, candidate in enumerate(candidates):
        base = f"/candidates/{index}"
        if not isinstance(candidate, dict):
            flag(
                base,
                "invalid_provider_candidate",
                "Unusable candidate retained as an unresolved slot; no reassociation.",
            )
            candidate = {}
        extras(candidate, set(PaymentOptionV5.model_fields), base)
        item: dict[str, Any] = {}
        for key in sorted(candidate_fields):
            field = {
                "amount_text": "amount/value",
                "currency": "amount/currency",
                "reference": "remittance/reference",
                "model": "remittance/model",
                "purpose_code": "remittance/purpose_code",
            }.get(key, key)
            item[key] = required_reading(candidate, key, base + "/" + field)
        item["amount_role"] = enum(
            candidate,
            "amount_role",
            {"amount_due", "invoice_total", "instalment", "other", "unknown"},
            base + "/amount/role",
        )
        item["reference_requirement"] = enum(
            candidate,
            "reference_requirement",
            {"required", "not_stated", "unknown"},
            base + "/remittance/reference_requirement",
        )
        dest = candidate.get("destination")
        kinds = {
            "uk_domestic": {"sort_code", "account_number"},
            "iban": {"iban", "bic"},
            "biller_reference": {"scheme", "biller_code"},
            "unresolved": {"details"},
        }
        if (
            not isinstance(dest, dict)
            or not isinstance(dest.get("kind"), str)
            or dest["kind"] not in kinds
        ):
            flag(
                base + "/destination",
                "invalid_provider_destination",
                "Destination is unresolved; no bank scheme or pairing was guessed.",
            )
            item["destination"] = {"kind": "unresolved", "details": []}
        else:
            kind = dest["kind"]
            allowed = kinds[kind]
            # Extra route fields can contradict the declared scheme. Retain the whole
            # destination privately rather than choose one route or discard bank digits.
            if set(dest) - (allowed | {"kind"}):
                flag(
                    base + "/destination",
                    "conflicting_provider_destination",
                    "Unexpected destination fields; no route was selected.",
                )
                item["destination"] = {"kind": "unresolved", "details": []}
            elif kind == "unresolved":
                details = dest.get("details")
                if not isinstance(details, list):
                    flag(
                        base + "/destination",
                        "invalid_provider_field",
                        "Untyped destination details are unusable.",
                    )
                    details = []
                # These claims remain evidence only; no synthetic bank route is created.
                item["destination"] = {
                    "kind": kind,
                    "details": [reading(v, base + "/destination") for v in details],
                }
            else:
                item["destination"] = {
                    "kind": kind,
                    **{
                        key: required_reading(dest, key, base + "/destination/" + key)
                        for key in sorted(allowed)
                    },
                }
        cleaned["candidates"].append(item)

    result = extract(json.dumps(cleaned), image_id, stage_id, version=version)
    for path, strings in rejected:
        alternatives = []
        ids = []
        for value in strings:
            ident = f"rejected-claim-{len(result.evidence)}"
            result.evidence.append(
                Evidence(
                    id=ident,
                    image_id=image_id,
                    source_stage_id=stage_id,
                    excerpt=value,
                    grounding="model_claim",
                )
            )
            ids.append(ident)
            alternatives.append(
                Alternative(
                    value=value,
                    evidence_ids=[ident],
                    reason="Rejected field claim; source review required",
                )
            )
        # Untyped details have no corresponding payment field, only retained evidence.
        if path.endswith("/destination"):
            continue
        node: Any = result.payment
        parts = path.strip("/").split("/")
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else getattr(node, part)
        setattr(
            node,
            parts[-1],
            Observation(
                state="ambiguous" if strings else "unreadable",
                raw_text=" | ".join(strings) or None,
                evidence_ids=ids,
                alternatives=alternatives,
            ),
        )
    result.payment = Payment.model_validate(result.payment.model_dump())
    result.findings = findings
    result.routing.applied_rule_packs.append("partial-fields@1")
    return result
