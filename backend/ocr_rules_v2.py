"""Structural OCR rules v2. Original excerpts remain distinct from matching views."""

import re

from backend.models import Evidence, Payment, Routing
from backend.ocr_rules import LABELS, Span, clean_line, extract_rules

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


def field_name(text: str) -> str | None:
    return next(
        (
            name
            for name, pattern in LABELS.items()
            if re.fullmatch(r"\s*(?:" + pattern + r")\s*[:：]\s*.*", clean_line(text), re.I)
        ),
        None,
    )


def structural_spans(text: str) -> tuple[Span, ...]:
    result = []
    block = 0
    active: set[str] = set()
    table_header: list[str] | None = None
    for index, line in enumerate(text.splitlines()):
        if not line.strip():
            if not active:
                block += 1
            continue
        matching = line
        name = field_name(line)
        if name in BANK:
            if (
                name in active
                or (name == "iban" and active & {"sort_code", "account_number"})
                or (name in {"sort_code", "account_number"} and "iban" in active)
            ):
                block += 1
                active.clear()
            active.add(name)
        elif not re.search(r"\b(?:prilikom uplate|kod uplate|pri plaćanju)\b", line, re.I):
            block += 1
            active.clear()
        if line.strip().startswith("|"):
            cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            if table_header is not None and len(cells) == len(table_header):
                for col, label in enumerate(table_header):
                    if any(re.fullmatch(p, label, re.I) for p in LABELS.values()):
                        result.append(
                            Span(f"ocr-{index}-c{col}", block, line, label + ": " + cells[col])
                        )
                table_header = None
                continue
            if any(
                re.fullmatch(p, cell, re.I) for cell in cells for p in LABELS.values()
            ) and not any(re.search(r"\d", cell) for cell in cells):
                table_header = cells
            else:
                # Horizontal label/value pairs only; never choose a numeric cell across another label.
                for col, label in enumerate(cells[:-1]):
                    if any(re.fullmatch(p, label, re.I) for p in LABELS.values()):
                        following = cells[col + 1]
                        result.append(
                            Span(f"ocr-{index}-c{col}", block, line, label + ": " + following)
                        )
                        matching = ""
        else:
            table_header = None
        if re.search(r"\b(?:prilikom uplate|kod uplate|pri plaćanju)\b", line, re.I):
            for name, pattern in [
                ("model", r"\bmodel\s*:?\s*(HR\d{2})\b"),
                ("reference", r"poziv na broj(?: primatelja)?\s*:?\s*([0-9][0-9/-]*)"),
            ]:
                match = re.search(pattern, line, re.I)
                if match:
                    label = "Model" if name == "model" else "Payment reference"
                    result.append(
                        Span(f"ocr-{index}-{name}", block, line, label + ": " + match.group(1))
                    )
        if matching:
            result.append(Span(f"ocr-{index}", block, line, matching))
    return tuple(result)


def extract_rules_v2(
    markdown: str, image_id: str, stage_id: str
) -> tuple[Payment, list[Evidence], Routing]:
    payment, evidence, routing = extract_rules(
        markdown, image_id, stage_id, prepared_spans=structural_spans(markdown)
    )
    routing.applied_rule_packs = [p.replace("@1", "@2") for p in routing.applied_rule_packs]
    routing.reasons = [
        "Contiguous bank-label sections and explicit table cells; original OCR excerpts retained."
    ]
    return payment, evidence, routing
