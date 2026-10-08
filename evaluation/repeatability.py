"""Compare normalized payment output and latency without treating agreement as truth."""

import hashlib
import json
import math
import statistics
from collections.abc import Iterable
from typing import Any

from backend.models import Payment


def payment_fingerprint(payment: Payment, *, payment_only: bool = False) -> str:
    """Preserve field uncertainty and linked candidates; ignore generated IDs/prose.

    Observed values use the existing normalized contract, never new normalization.
    Unresolved readings retain raw text where no normalized value exists. Evidence
    geometry, excerpts, normalization logs and review explanations are not compared.
    Candidate order and alternative order do not establish a semantic difference.
    """

    def clean(value: Any) -> Any:
        if isinstance(value, list):
            return [clean(item) for item in value]
        if not isinstance(value, dict):
            return value
        if "state" in value and "evidence_ids" in value:
            return {
                "value": value["value"],
                "state": value["state"],
                "origin": value["origin"],
                "unresolved_text": value["raw_text"]
                if value["value"] is None and not value["alternatives"]
                else None,
                "alternatives": sorted({item["value"] for item in value["alternatives"]}),
            }
        return {
            key: clean(item)
            for key, item in value.items()
            if key not in {"id", "reason", "evidence_ids", "normalization"}
        }

    candidates = {c.id: clean(c.model_dump()) for c in payment.candidates}
    snapshot = (
        {}
        if payment_only
        else clean(payment.model_dump(exclude={"candidates", "selected_candidate_id", "review"}))
    )
    snapshot["candidates"] = sorted(
        candidates.values(), key=lambda value: json.dumps(value, sort_keys=True)
    )
    snapshot["selected_candidate"] = candidates.get(payment.selected_candidate_id or "")
    snapshot["review_state"] = payment.review.state
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()


def latency_summary(values: Iterable[float | None]) -> dict[str, int | float | None]:
    """Descriptive nearest-rank p95; missing measurements are not zero latency."""
    measured = sorted(value for value in values if value is not None)
    if any(not math.isfinite(value) or value < 0 for value in measured):
        raise ValueError("Latency must be finite and nonnegative")
    return {
        "n": len(measured),
        "p50_ms": statistics.median(measured) if measured else None,
        "p95_ms": measured[math.ceil(len(measured) * 0.95) - 1] if measured else None,
        "max_ms": max(measured) if measured else None,
    }
