"""Hash-bound human-review import and conservative, linked-option exact-match scoring.

Scores are field-level evidence, not verified whole invoices. Unreviewed labels never
enter denominators; confirmed absence is reported separately from readable values.
"""

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.models import Run

DOC_FIELDS = {"supplier_name", "invoice_number", "customer_number", "due_date"}
OPTION_FIELDS = {
    "beneficiary_name",
    "account_holder_name",
    "amount",
    "currency",
    "iban",
    "bic",
    "sort_code",
    "account_number",
    "model",
    "reference",
    "biller_scheme",
    "biller_code",
}
ANCHORS = {"iban", "account_number", "sort_code", "reference", "biller_code"}
CRITICAL = {
    "beneficiary_name",
    "amount",
    "currency",
    "iban",
    "sort_code",
    "account_number",
    "model",
    "reference",
    "biller_code",
}
DECISIONS = {"confirmed", "corrected", "not_visible", "unreadable", "pending", "unsure"}


def label_fields(document: dict[str, Any]) -> dict[str, Any]:
    fields = {f"document_fields/{k}": v for k, v in document["document_fields"].items()}
    for option in document["payment_options"]:
        for key, value in option["fields"].items():
            path = f"payment_options/{option['id']}/{key}"
            if path in fields:
                raise ValueError("Duplicate label field")
            fields[path] = value
    fields.update(
        {
            f"additional_printed_fields/{k}": v
            for k, v in document.get("additional_printed_fields", {}).items()
        }
    )
    return fields


def indexed(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    result = {r[key]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError("Duplicate review identity")
    return result


def import_review(
    label_bytes: bytes,
    review: dict[str, Any],
    manifest: dict[str, Any],
    holds: dict[str, str] | None = None,
) -> dict[str, Any]:
    labels = json.loads(label_bytes)
    digest = hashlib.sha256(label_bytes).hexdigest()
    if (
        review["format"] != "scan-pay-human-review@1"
        or review["dataset_sha256"] != digest
        or review["label_version"] != labels["version"]
    ):
        raise ValueError("Review does not match frozen labels")
    sources = indexed(labels["documents"], "input_id")
    reviews = indexed(review["documents"], "input_id")
    inputs = indexed(manifest["inputs"], "id")
    if sources.keys() != reviews.keys() or sources.keys() != inputs.keys():
        raise ValueError("Review must account for every input")
    holds = holds or {}
    used_holds = set()
    documents = []
    counts: Counter[str] = Counter()
    for ident, source in sources.items():
        reviewed = reviews[ident]
        if (
            source["image_sha256"] != reviewed["image_sha256"]
            or source["image_sha256"] != inputs[ident]["sha256"]
        ):
            raise ValueError("Review image hash mismatch")
        originals = label_fields(source)
        responses = indexed(reviewed["fields"], "field_path")
        if originals.keys() != responses.keys():
            raise ValueError("Review field inventory mismatch")
        fields = []
        for path, original in originals.items():
            answer = responses[path]
            decision, value = answer["decision"], answer["value"]
            if (
                decision not in DECISIONS
                or answer["draft_value"] != original["value"]
                or answer["draft_visibility"] != original["visibility"]
            ):
                raise ValueError("Changed review source or unknown decision")
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError("Reviewed values must be nonblank text or null")
            if decision == "confirmed" and value != original["value"]:
                raise ValueError("Changed value requires corrected decision")
            if original.get("readability_review") and decision != "unreadable":
                raise ValueError("Prior unreadability decision is locked")
            if original.get("user_verified") and (
                decision != "confirmed" or value != original["value"]
            ):
                raise ValueError("Prior confirmed value is locked")
            key = ident + "/" + path
            reason = None
            if decision in {"pending", "unsure", "unreadable"}:
                reason = decision
            elif key in holds:
                reason = "disputed_semantics"
                used_holds.add(key)
            elif decision == "confirmed" and original["visibility"] == "uncertain":
                reason = "uncertain_source"
            elif decision == "corrected" and value is None:
                reason = "correction_without_value"
            elif path.startswith("document_fields/") and path.split("/")[-1] not in DOC_FIELDS:
                reason = "unrepresented_or_free_text"
            elif path.startswith("additional_printed_fields/"):
                reason = "unrepresented_or_free_text"
            elif (
                path.startswith("payment_options/")
                and path.split("/")[-1] not in OPTION_FIELDS
                and not (path.endswith("/due_date") and len(source["payment_options"]) == 1)
            ):
                reason = "unrepresented_candidate_field"
            if decision in {"not_visible", "unreadable"} and value is not None:
                raise ValueError("Absent/unreadable decisions cannot assert a value")
            expected = None if decision == "not_visible" else value
            status = reason or ("absent" if expected is None else "readable")
            counts[status] += 1
            fields.append(
                {
                    "path": path,
                    "expected": expected,
                    "status": status,
                    "decision": decision,
                    "reviewer": answer.get("reviewer", review["reviewer"]),
                    "hold_reason": holds.get(key),
                    "printed_date_alias": (
                        original.get("raw_text")
                        if path.endswith("/due_date") and expected == original["value"]
                        else None
                    ),
                }
            )
        documents.append(
            {"input_id": ident, "image_sha256": source["image_sha256"], "fields": fields}
        )
    if set(holds) != used_holds:
        raise ValueError("Hold must identify a reviewed field eligible for semantic review")
    return {
        "version": "reviewed-fields@1",
        "label_sha256": digest,
        "review_sha256": hashlib.sha256(json.dumps(review, sort_keys=True).encode()).hexdigest(),
        "manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest(),
        "counts": dict(counts),
        "documents": documents,
    }


def normalized(name: str, value: str | None) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", value).strip().casefold()
    if name == "amount":
        # The public contract and answer key use canonical decimals, never locale guesses.
        try:
            number = Decimal(text)
            return str(number.normalize()) if number.is_finite() else text
        except InvalidOperation:
            return text
    if name == "reference":
        return re.sub(r"\s", "", text)
    if name in {"sort_code", "iban", "bic", "account_number", "biller_code"}:
        # Formatting only: preserve every letter and leading zero.
        return re.sub(r"[\s-]", "", text)
    if name.endswith("_name"):
        # No fuzzy names, translations, added/dropped words or supplier aliases.
        return "".join(c for c in text if c.isalnum())
    return " ".join(text.split())


def observation(payment: dict[str, Any], candidate: dict[str, Any], path: str) -> dict[str, Any]:
    name = path.split("/")[-1]
    if path.startswith("document_fields/") or name == "due_date":
        return dict(payment.get(name) or {})
    if name in {"beneficiary_name", "account_holder_name"}:
        return dict(candidate.get(name) or {})
    if name in {"amount", "currency"}:
        return dict(candidate.get("amount", {}).get("value" if name == "amount" else name) or {})
    if name in {"model", "reference"}:
        return dict(candidate.get("remittance", {}).get(name) or {})
    return dict(
        candidate.get("destination", {}).get("scheme" if name == "biller_scheme" else name) or {}
    )


def outcome(field: dict[str, Any], actual: dict[str, Any], available: bool) -> str:
    if not available:
        return "run_error"
    value = actual.get("value")
    alternatives = actual.get("alternatives", [])
    if field["status"] == "absent":
        if value is not None:
            return "unexpected_value"
        return (
            "uncertain_output"
            if alternatives or actual.get("state") == "ambiguous"
            else "correct_absence"
        )
    if value is None:
        return (
            "uncertain_output"
            if alternatives or actual.get("state") in {"ambiguous", "unreadable"}
            else "missing"
        )
    if actual.get("state") != "observed" or actual.get("origin") != "document":
        return "unsupported_inference"
    name = field["path"].split("/")[-1]
    if name == "due_date":
        if normalized(name, value) == normalized(name, field.get("printed_date_alias")):
            return "exact_match"
        # Date order must be supplied by a separate source-format adjudication.
        # Never guess it from country, provider agreement or the desired score.
        formats = ["%Y-%m-%d", "%d %b %Y", "%d %B %Y"]
        if field.get("date_order") == "DMY":
            formats.append("%d/%m/%Y")
        elif field.get("date_order") == "MDY":
            formats.append("%m/%d/%Y")
        for date_format in formats:
            try:
                if datetime.strptime(value, date_format).date().isoformat() == field["expected"]:
                    return "exact_match"
            except ValueError:
                continue
    if normalized(name, value) == normalized(name, field["expected"]):
        return "exact_match"
    # Explicit human-approved name variants only. Never relax payment digits or
    # treat similarity, inferred names or ambiguous observations as correctness.
    if name.endswith("_name") and any(
        alias.get("reviewer")
        and alias.get("reason")
        and isinstance(alias.get("value"), str)
        and normalized(name, value) == normalized(name, alias["value"])
        for alias in field.get("accepted_name_variants", [])
    ):
        return "accepted_name_variant"
    return "value_mismatch"


def match_options(
    fields: list[dict[str, Any]], candidates: list[dict[str, Any]]
) -> dict[str, int | None]:
    # One-to-one whole-candidate assignment; anchors win over superficial name/amount matches.
    options: dict[str, list[dict[str, Any]]] = {}
    for field in fields:
        if field["status"] in {"readable", "absent"} and field["path"].startswith(
            "payment_options/"
        ):
            options.setdefault(field["path"].split("/")[1], []).append(field)
    names = list(options)
    if len(names) > 12 or len(candidates) > 16:
        raise ValueError("Too many options for bounded exact assignment")
    weights = []
    for name in names:
        scores = []
        for candidate in candidates:
            anchors = matches = 0
            for field in options[name]:
                if field["status"] == "readable" and outcome(
                    field, observation({}, candidate, field["path"]), True
                ) in {"exact_match", "accepted_name_variant"}:
                    matches += 1
                    anchors += field["path"].split("/")[-1] in ANCHORS
            scores.append(anchors * 1000 + matches)
        weights.append(scores)

    @lru_cache(None)
    def assign(index: int, used: int) -> tuple[int, tuple[int | None, ...]]:
        if index == len(names):
            return 0, ()
        score, tail = assign(index + 1, used)
        best = score, (None, *tail)
        for j, weight in enumerate(weights[index]):
            if weight > 0 and not used & (1 << j):
                score, tail = assign(index + 1, used | (1 << j))
                if score + weight > best[0]:
                    best = score + weight, (j, *tail)
        return best

    return dict(zip(names, assign(0, 0)[1], strict=True))


def score_document(document: dict[str, Any], payment: dict[str, Any] | None) -> dict[str, Any]:
    available = payment is not None
    payment = payment or {}
    candidates = payment.get("candidates", [])
    matches = match_options(document["fields"], candidates)
    rows = []
    counts: dict[str, Counter[str]] = {
        k: Counter() for k in ("readable", "absent", "critical_readable", "excluded")
    }
    for field in document["fields"]:
        status, path = field["status"], field["path"]
        if status not in {"readable", "absent"}:
            counts["excluded"][status] += 1
            continue
        candidate = {}
        option = path.split("/")[1] if path.startswith("payment_options/") else None
        matched = matches.get(option) if option else None
        if matched is not None:
            candidate = candidates[matched]
        actual = observation(payment, candidate, path)
        result = outcome(field, actual, available)
        # An unmatched option cannot demonstrate that the provider correctly left its fields blank.
        if option and matched is None and status == "absent" and available:
            result = "unmatched_option"
        counts[status][result] += 1
        if option and status == "readable" and path.split("/")[-1] in CRITICAL:
            counts["critical_readable"][result] += 1
        rows.append(
            {
                "path": path,
                "expected": field["expected"],
                "label_status": status,
                "actual": actual.get("value"),
                "actual_state": actual.get("state"),
                "outcome": result,
                "candidate_id": candidate.get("id"),
            }
        )
    used = {j for j in matches.values() if j is not None}
    return {
        "input_id": document["input_id"],
        "counts": {k: dict(v) for k, v in counts.items()},
        "option_matches": {
            k: candidates[v].get("id") if v is not None else None for k, v in matches.items()
        },
        "unmatched_candidate_ids": [c.get("id") for j, c in enumerate(candidates) if j not in used],
        "fields": rows,
    }


def score_batch(
    root: Path, manifest: dict[str, Any], batch: dict[str, Any], key: dict[str, Any]
) -> dict[str, Any]:
    from evaluation.experiment import summarize

    # Existing matrix validation checks every cell and exact profile/version snapshot.
    measurements = summarize(root, manifest, batch)
    if (
        key["version"] not in {"reviewed-fields@1", "reviewed-fields@2"}
        or key["manifest_sha256"] != batch["manifest_sha256"]
    ):
        raise ValueError("Answer key is not bound to this matrix")
    variants_enabled = key["version"] == "reviewed-fields@2"
    if not variants_enabled and any(
        "accepted_name_variants" in field
        for document in key["documents"]
        for field in document["fields"]
    ):
        raise ValueError("Accepted name variants require a version 2 answer key")
    documents = indexed(key["documents"], "input_id")
    inputs = indexed(manifest["inputs"], "id")
    if documents.keys() != inputs.keys() or any(
        documents[k]["image_sha256"] != inputs[k]["sha256"] for k in inputs
    ):
        raise ValueError("Answer key image inventory mismatch")
    profiles: dict[str, Any] = {}
    for profile, version in batch["profiles"].items():
        totals: dict[str, Counter[str]] = {
            k: Counter() for k in ("readable", "absent", "critical_readable", "excluded")
        }
        results = []
        for row in batch["rows"]:
            if row["profile_id"] != profile:
                continue
            if row["state"] not in {"succeeded", "failed"}:
                raise ValueError("Finish the bounded matrix before scoring")
            payment = None
            if row.get("result_path"):
                run = Run.model_validate(
                    json.loads((root / row["result_path"]).read_text())["runs"][0]
                )
                # A zero-field error must not gain true-negative credit for empty output.
                if run.result_outcome != "error" and run.payment is not None:
                    payment = run.payment.model_dump(mode="json")
            result = score_document(documents[row["input_id"]], payment)
            results.append(result)
            for name, counts in result["counts"].items():
                totals[name].update(counts)
        scores = {}
        for name, counts in totals.items():
            denominator = sum(counts.values())
            metric = "correct_absence" if name == "absent" else "exact_match"
            matched = counts[metric] + (
                counts["accepted_name_variant"] if name in {"readable", "critical_readable"} else 0
            )
            scores[name] = {
                "counts": dict(counts),
                "denominator": denominator,
                "fraction": matched / denominator if denominator and name != "excluded" else None,
            }
        profiles[profile] = {
            "version": version,
            "scores": scores,
            "documents": results,
            "measurements": measurements["profiles"][profile],
        }
    return {
        "version": "reviewed-comparison@2" if variants_enabled else "reviewed-comparison@1",
        "answer_key_sha256": hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest(),
        "batch_id": batch["batch_id"],
        "label_coverage": key["counts"],
        "limitations": [
            "Partial reviewed fields only; no whole-document accuracy or representative corpus claim.",
            "Value mismatches require inspection, especially names; no fuzzy/semantic aliases are silently accepted.",
            "Confirmed absences are separate from readable-value accuracy. Unmatched options and errors receive no absence credit.",
            "Options are matched one-to-one using reviewed destination/reference anchors before other fields. Extra unmatched candidates are exposed but not automatically classified as wrong.",
            "Only single-option due dates map to the public document due_date. Per-option dates, unsupported document fields and free prose are excluded.",
            "Option preference, amount-role semantics and completeness of the option inventory are not human-verified by this field form.",
        ],
        "profiles": profiles,
        "costs": measurements["costs"],
    }
