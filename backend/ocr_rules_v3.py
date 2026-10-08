"""Versioned label/layout interpretation. No recognition, network, or digit repair.

Geometry is used only within its source page. Public evidence quotes exact source
spans; native boxes are not asserted to be canonical image coordinates.
"""

import json
import math
import re
from dataclasses import dataclass

from backend.document_observations import DocumentObservation, DocumentSpan
from backend.label_dictionary import label_patterns, normalize_label
from backend.models import (
    Alternative,
    Amount,
    Candidate,
    Evidence,
    IBANDestination,
    Observation,
    Payment,
    Remittance,
    Routing,
    UnresolvedDestination,
    observations,
)
from backend.ocr_rules import LABELS, Span, amount_observation, extract_rules, labelled

PATTERNS = label_patterns("1")
CANONICAL = {name: pattern for name, pattern in LABELS.items()}
CANONICAL.update(
    {
        "account_number": "Account number",
        "invoice_number": "Invoice number",
        "amount_due": "Amount due",
        "invoice_total": "Invoice total",
    }
)
# Use literal labels for matching views; source excerpts never use these synthetic labels.
CANONICAL.update(
    dict(
        zip(
            (
                "sort_code",
                "iban",
                "bic",
                "beneficiary_name",
                "account_holder_name",
                "currency",
                "reference",
                "model",
                "purpose_code",
                "supplier_name",
                "customer_number",
                "due_date",
                "description",
            ),
            (
                "Sort code",
                "IBAN",
                "BIC",
                "Beneficiary",
                "Account holder",
                "Currency",
                "Payment reference",
                "Model",
                "Purpose code",
                "Supplier",
                "Customer number",
                "Due date",
                "Description",
            ),
            strict=True,
        )
    )
)
BANK = {
    "sort_code",
    "account_number",
    "iban",
    "bic",
    "beneficiary_name",
    "account_holder_name",
    "reference",
    "model",
    "purpose_code",
}
AMOUNTS = {"amount_due", "invoice_total"}
TOKEN = re.compile(
    r"(?<!\w)(?:"
    + "|".join(f"(?P<{name}>{pattern})" for name, pattern in PATTERNS.items())
    + r")(?=\s|[:：]|$)",
    re.I,
)


def clean(text: str) -> str:
    return text.strip().strip("*").strip()


def exact_label(text: str) -> str | None:
    token = normalize_label(clean(text).rstrip(":：").strip())
    return next((n for n, p in PATTERNS.items() if re.fullmatch(p, token, re.I)), None)


def plausible(name: str, value: str) -> bool:
    """Constrain unpunctuated/spatial claims; malformed explicit readings stay reviewable."""
    if not value or exact_label(value):
        return False
    if name in AMOUNTS:
        return bool(
            re.fullmatch(r"(?:GBP|EUR|[£€$])?\s*-?[\d., ]+(?:\s*(?:GBP|EUR|[£€$]))?", value, re.I)
        )
    if name in {"sort_code", "account_number"}:
        return bool(re.fullmatch(r"[\dOIl? -]+", value))
    if name == "iban":
        return bool(re.fullmatch(r"[A-Z]{2}[\d?OIl]{2}[A-Z0-9 ?]+", value, re.I))
    if name in {
        "invoice_number",
        "customer_number",
        "reference",
        "model",
        "purpose_code",
        "bic",
        "due_date",
        "currency",
    }:
        return bool(re.fullmatch(r"[\w./ -]+", value))
    return True


Box = tuple[float, float, float, float]


def native_box(span: DocumentSpan, provider: str) -> Box | None:
    """Normalize only known provider spaces, for local adjacency calculations."""
    if not span.geometry_json:
        return None
    try:
        g = json.loads(span.geometry_json)
        if provider == "aws":
            b = g["BoundingBox"]
            box = tuple(float(b[k]) for k in ("Left", "Top", "Width", "Height"))
        else:
            if provider == "google_documentai":
                points = [
                    (float(p.get("x", 0)), float(p.get("y", 0))) for p in g["normalizedVertices"]
                ]
            elif provider == "azure" and g["unit"] in {"pixel", "inch"}:
                xy = g["polygon"]
                points = [
                    (float(xy[i]) / float(g["width"]), float(xy[i + 1]) / float(g["height"]))
                    for i in range(0, len(xy), 2)
                ]
            else:
                return None
            xs, ys = zip(*points, strict=True)
            box = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        x, y, w, h = box
        if (
            not all(math.isfinite(v) for v in box)
            or min(x, y) < 0
            or min(w, h) <= 0
            or x + w > 1.000001
            or y + h > 1.000001
        ):
            return None
        return x, y, w, h
    except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError):
        return None


@dataclass(frozen=True)
class Reading:
    name: str
    value: str
    source: tuple[DocumentSpan, ...]
    block: int


def readings(document: DocumentObservation) -> list[Reading]:
    lines = document.spans or tuple(
        DocumentSpan(f"line-{i}", 1, t) for i, t in enumerate(document.text.splitlines())
    )
    result: list[Reading] = []
    consumed: set[int] = set()
    block = 0
    active: set[str] = set()
    header: list[str] | None = None
    header_span: DocumentSpan | None = None
    last_page: int | None = None
    for i, line in enumerate(lines):
        if line.page != last_page:
            block += 1
            active.clear()
            header = None
        last_page = line.page
        if i in consumed or not line.text.strip():
            continue
        text = clean(line.text)
        found: list[tuple[str, str, tuple[DocumentSpan, ...]]] = []
        if text.startswith("|"):
            cells = [clean(c) for c in text.strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            if header is not None and len(cells) == len(header):
                assert header_span is not None
                for label, value in zip(header, cells, strict=True):
                    name = exact_label(label)
                    if name and value and plausible(name, value):
                        found.append((name, value, (header_span, line)))
                header = None
            elif (
                any(exact_label(c) for c in cells)
                and i + 1 < len(lines)
                and re.fullmatch(r"[| :\-]+", lines[i + 1].text.strip())
            ):
                header, header_span = cells, line
                continue
            else:
                # A row's value can cross blank cells, but never another label/value.
                for col, cell in enumerate(cells[:-1]):
                    name = exact_label(cell)
                    tail = [v for v in cells[col + 1 :] if v]
                    if name and len(tail) == 1 and plausible(name, tail[0]):
                        found.append((name, tail[0], (line,)))
        else:
            header = None
            matches = [
                m
                for m in TOKEN.finditer(text)
                if m.start() == 0
                or text[m.end() :].lstrip().startswith((":", "："))
                or (
                    m.lastgroup in {"sort_code", "account_number"}
                    and re.match(r"\s+[0-9OIl?]", text[m.end() :])
                )
            ]
            for pos, match in enumerate(matches):
                name = match.lastgroup
                assert name is not None
                end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
                value = clean(text[match.end() : end].lstrip(" :：")).rstrip(";").strip()
                # In prose, only explicitly punctuated bank labels are accepted.
                prefix = text[: match.start()].strip()
                explicit = text[match.end() :].lstrip().startswith((":", "："))
                if prefix and name not in BANK:
                    continue
                if (
                    value
                    and (plausible(name, value) or (explicit and not prefix))
                    and (not prefix or explicit or name in {"sort_code", "account_number"})
                ):
                    found.append((name, value, (line,)))
            name = exact_label(text)
            if name:
                box = native_box(line, document.provider)
                candidates: list[tuple[int, DocumentSpan]] = []
                if box:
                    x, y, w, h = box
                    for j, other in enumerate(lines):
                        if (
                            j == i
                            or j in consumed
                            or other.page != line.page
                            or not plausible(name, clean(other.text))
                        ):
                            continue
                        ob = native_box(other, document.provider)
                        if not ob:
                            continue
                        ox, oy, ow, oh = ob
                        right = (
                            abs((oy + oh / 2) - (y + h / 2)) <= min(h, oh) / 2
                            and 0 <= ox - (x + w) <= 0.2
                        )
                        below = 0 <= oy - (y + h) <= 1.5 * max(h, oh) and abs(ox - x) <= 0.04
                        if right or below:
                            candidates.append((j, other))
                elif line.geometry_json is None:
                    # Text-only adjacency is deliberately one following nonblank line.
                    for j in range(i + 1, min(i + 4, len(lines))):
                        other = lines[j]
                        if other.text.strip():
                            if other.page == line.page and plausible(name, clean(other.text)):
                                candidates.append((j, other))
                            break
                if len(candidates) == 1:
                    j, other = candidates[0]
                    consumed.add(j)
                    found.append((name, clean(other.text), (line, other)))
            # Explicit Croatian remittance instructions; identifiers are never taken from headers.
            if re.search(r"\b(?:prilikom uplate|kod uplate|pri plaćanju)\b", text, re.I):
                for name, pattern in [
                    ("model", r"\bmodel\s*:?\s*(HR\d{2})\b"),
                    ("reference", r"poziv na broj(?: primatelja)?\s*:?\s*([0-9][0-9/-]*)"),
                ]:
                    m = re.search(pattern, text, re.I)
                    if m:
                        found = [f for f in found if f[0] != name]
                        found.append((name, m.group(1), (line,)))
        names = {n for n, _, _ in found}
        if not found or text.startswith("#") or names - (BANK | AMOUNTS):
            block += 1
            active.clear()
        # Repeated routing component or a different scheme starts a separate option.
        if (
            names & active & {"sort_code", "account_number", "iban"}
            or ("iban" in names and active & {"sort_code", "account_number"})
            or (names & {"sort_code", "account_number"} and "iban" in active)
        ):
            block += 1
            active.clear()
        result.extend(Reading(n, v, s, block) for n, v, s in found)
        active.update(names)
    return result


def extract_rules_v3(document: DocumentObservation) -> tuple[Payment, list[Evidence], Routing]:
    found = readings(document)
    spans = tuple(
        Span(
            f"reading-{i}",
            r.block,
            "\n".join(s.text for s in r.source),
            CANONICAL[r.name] + ": " + r.value,
        )
        for i, r in enumerate(found)
    )
    payment, evidence, routing = extract_rules(
        document.text, document.image_id, document.source_stage_id, prepared_spans=spans
    )
    # Original engine requires a route/reference before retaining amounts. Keep standalone
    # amount observations as unresolved options; never manufacture a destination/payee.
    if not payment.candidates:
        due = labelled(spans, "amount_due")
        raw = due if due.state != "missing" else labelled(spans, "invoice_total")
        if raw.state != "missing":
            value, currency = amount_observation(raw)
            payment.candidates.append(
                Candidate(
                    id="candidate-1",
                    amount=Amount(
                        value=value,
                        currency=currency,
                        role="amount_due" if due.state != "missing" else "invoice_total",
                    ),
                    destination=UnresolvedDestination(
                        reason="Amount observed without a bank destination"
                    ),
                )
            )
    used = {eid for obs in observations(payment.candidates) for eid in obs.evidence_ids}
    for block in sorted({r.block for r in found}):
        remaining = tuple(
            s
            for s, r in zip(spans, found, strict=True)
            if r.block == block and s.id not in used and r.name in BANK
        )
        if not remaining:
            continue
        # A detached reference/name cannot silently migrate to a different bank block.
        payment.candidates.append(
            Candidate(
                id=f"candidate-{len(payment.candidates) + 1}",
                beneficiary_name=labelled(remaining, "beneficiary_name"),
                account_holder_name=labelled(remaining, "account_holder_name"),
                destination=IBANDestination(bic=labelled(remaining, "bic"))
                if labelled(remaining, "bic").state != "missing"
                else UnresolvedDestination(
                    reason="Unassociated payment fields without a bank destination"
                ),
                remittance=Remittance(
                    reference=labelled(remaining, "reference"),
                    model=labelled(remaining, "model"),
                    purpose_code=labelled(remaining, "purpose_code"),
                    reference_requirement="required"
                    if labelled(remaining, "reference").state != "missing"
                    else "unknown",
                ),
            )
        )
    # Evidence references exact individual native spans (including split label/value),
    # rather than synthetic concatenations or relabelled text.
    source_evidence: dict[str, Evidence] = {}
    ids: dict[str, list[str]] = {}
    for i, r in enumerate(found):
        ids[f"reading-{i}"] = []
        for s in r.source:
            eid = f"source-{s.id}"
            ids[f"reading-{i}"].append(eid)
            source_evidence[eid] = Evidence(
                id=eid,
                image_id=document.image_id,
                excerpt=s.text,
                grounding="ocr_span",
                source_stage_id=document.source_stage_id,
            )

    def remap(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "evidence_ids" and isinstance(item, list):
                    value[key] = list(dict.fromkeys(e for old in item for e in ids[str(old)]))
                else:
                    remap(item)
        elif isinstance(value, list):
            for item in value:
                remap(item)

    for candidate in payment.candidates:
        if candidate.destination.kind == "uk_domestic":
            for name, length in [("sort_code", 6), ("account_number", 8)]:
                value = getattr(candidate.destination, name)
                if value.value and not re.fullmatch(
                    r"[0-9]{" + str(length) + r"}", re.sub(r"[ -]", "", value.value)
                ):
                    setattr(
                        candidate.destination,
                        name,
                        Observation(
                            state="ambiguous",
                            raw_text=value.raw_text,
                            evidence_ids=value.evidence_ids,
                            alternatives=[
                                Alternative(
                                    value=value.value,
                                    reason="Malformed bank reading; no digit repair",
                                    evidence_ids=value.evidence_ids,
                                )
                            ],
                        ),
                    )
    data = payment.model_dump()
    remap(data)
    routing.applied_rule_packs = [p.replace("@1", "@3") for p in routing.applied_rule_packs]
    routing.applied_rule_packs.append("label-dictionary@1")
    routing.reasons = [
        "Explicit labels, table cells and unique page-local adjacency; native source spans retained."
    ]
    return Payment.model_validate(data), list(source_evidence.values()), routing
