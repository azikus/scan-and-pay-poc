"""General label/paragraph rules over immutable managed OCR observations.

No supplier lookup, URL resolution, language-based banking or digit substitution.
Paragraph-local associations are intentionally conservative on complex layouts.
"""

import re
from dataclasses import dataclass
from typing import Literal

from backend.models import (
    Alternative,
    Amount,
    Candidate,
    Destination,
    Evidence,
    IBANDestination,
    Observation,
    Payment,
    Remittance,
    Routing,
    UKDestination,
    UnresolvedDestination,
)
from backend.payment_fields import CURRENCY_TOKENS, currency_code

LABELS = {
    "sort_code": r"sort[ -]?code",
    "account_number": r"(?:bank )?account (?:number|no\.?)",
    "iban": r"(?:recipient |primatelj )?IBAN",
    "bic": r"(?:BIC|SWIFT)",
    "beneficiary_name": r"(?:beneficiary(?: name)?|payee|primatelj|korisnik plaćanja)",
    "account_holder_name": r"(?:account (?:holder|name)|naziv primatelja)",
    "amount_due": r"(?:amount due|total due|balance due|iznos za uplatu|za uplatu|ukupno za platiti)",
    "invoice_total": r"(?:invoice total|gross|ukupno|total)",
    "currency": r"(?:currency|valuta)",
    "reference": r"(?:payment reference|required reference|poziv na broj(?: primatelja)?|roll number)",
    "model": r"(?:model(?: primatelja)?|model plaćanja)",
    "purpose_code": r"(?:purpose code|šifra namjene)",
    "supplier_name": r"(?:supplier(?: name)?|dobavljač|izdavatelj)",
    "invoice_number": r"(?:invoice (?:number|no\.?)|broj računa)",
    "customer_number": r"(?:customer (?:number|no\.?)|šifra kupca)",
    "due_date": r"(?:due date|datum dospijeća|dospijeće)",
    "description": r"(?:description|opis plaćanja)",
}


@dataclass(frozen=True)
class Span:
    id: str
    block: int
    text: str
    matching_text: str | None = None


def spans_from_markdown(markdown: str) -> tuple[Span, ...]:
    spans = []
    block = 0
    for index, original in enumerate(markdown.splitlines()):
        if not original.strip() or re.match(r"^#{1,6}\s", original):
            block += 1
        if original.strip():
            spans.append(Span(f"ocr-{index}", block, original))
    return tuple(spans)


def clean_line(text: str) -> str:
    # Convert two-cell key/value markdown rows only; never merge table columns.
    text = text.strip()
    label_markup = re.match(r"^\*{1,2}([^*]+)\*{1,2}\s*:?\s*(.*)$", text)
    if label_markup:
        label, value = label_markup.groups()
        label = label.rstrip(":").strip()
        if any(re.fullmatch(pattern, label, re.I) for pattern in LABELS.values()):
            text = label + ": " + value
    if text.startswith("|"):
        cells = [part.strip() for part in text.strip("|").split("|")]
        if len(cells) == 2:
            return cells[0].strip("*").rstrip(":") + ": " + cells[1]
    return text


def labelled(spans: tuple[Span, ...], name: str) -> Observation:
    matches: list[tuple[str, str]] = []
    for span in spans:
        match = re.fullmatch(
            r"\s*(?:" + LABELS[name] + r")\s*[:：]\s*(.*?)\s*",
            clean_line(span.matching_text or span.text),
            re.I,
        )
        if match:
            matches.append((match.group(1).strip(), span.id))
    if not matches:
        return Observation()
    if len({v for v, _ in matches}) != 1:
        return Observation(
            state="ambiguous",
            raw_text=" | ".join(v for v, _ in matches),
            evidence_ids=[i for _, i in matches],
            alternatives=[
                Alternative(
                    value=v, reason="Multiple printed values for this label", evidence_ids=[i]
                )
                for v, i in [(v, i) for v, i in matches if v][:8]
            ],
        )
    value = matches[0][0]
    if not value:
        return Observation(state="unreadable", evidence_ids=[i for _, i in matches])
    return Observation(
        value=value, raw_text=value, state="observed", evidence_ids=[i for _, i in matches]
    )


def amount_observation(raw: Observation) -> tuple[Observation, Observation]:
    if raw.value is None:
        return raw, Observation()
    currency = Observation()
    tokens = re.findall(CURRENCY_TOKENS, raw.value, re.I)
    normalized_codes = {currency_code(c) for c in tokens} - {None}
    if len(normalized_codes) == 1 and "$" not in tokens:
        currency = Observation(
            value=next(iter(normalized_codes)),
            raw_text=raw.raw_text,
            state="observed",
            evidence_ids=raw.evidence_ids,
            normalization=["explicit_currency_token"],
        )
    elif len(normalized_codes) > 1 or "$" in raw.value:
        currency = Observation(
            raw_text=raw.raw_text, state="ambiguous", evidence_ids=raw.evidence_ids
        )
    numeric = re.sub(CURRENCY_TOKENS, "", raw.value, flags=re.I).strip()
    numeric = numeric.replace("\u00a0", " ")
    # Whole units have an exact decimal representation; never guess ambiguous grouping.
    if re.fullmatch(r"-?(?:[0-9]+|[0-9]{1,3}(?:[, ][0-9]{3})+)\.[0-9]{2}", numeric):
        value = numeric.replace(",", "").replace(" ", "")
    elif re.fullmatch(r"-?(?:[0-9]+|[0-9]{1,3}(?:[. ][0-9]{3})+),[0-9]{2}", numeric):
        value = numeric.replace(".", "").replace(" ", "").replace(",", ".")
    elif re.fullmatch(r"-?[0-9]+", numeric):
        value = numeric + ".00"
    else:
        return Observation(
            state="ambiguous", raw_text=raw.raw_text, evidence_ids=raw.evidence_ids
        ), currency
    return Observation(
        value=value,
        raw_text=raw.raw_text,
        state="observed",
        evidence_ids=raw.evidence_ids,
        normalization=[
            "explicit_whole_units"
            if "." not in numeric and "," not in numeric
            else "explicit_decimal_and_grouping"
        ],
    ), currency


def extract_rules(
    markdown: str, image_id: str, stage_id: str, *, prepared_spans: tuple[Span, ...] | None = None
) -> tuple[Payment, list[Evidence], Routing]:
    spans = spans_from_markdown(markdown) if prepared_spans is None else prepared_spans
    payment = Payment()
    for name in ("supplier_name", "invoice_number", "customer_number", "due_date", "description"):
        setattr(payment, name, labelled(spans, name))
    groups = [
        tuple(s for s in spans if s.block == block) for block in sorted({s.block for s in spans})
    ]
    route_groups = [
        group
        for group in groups
        if any(
            labelled(group, n).state != "missing" for n in ("sort_code", "account_number", "iban")
        )
    ]
    routing = Routing(
        applied_rule_packs=["generic-labels@1"],
        reasons=[
            "Labels and paragraph position from managed image OCR; language/address never determine routing."
        ],
    )
    if not route_groups and labelled(spans, "reference").state != "missing":
        route_groups = [spans]
    for group in route_groups:
        # Only a single route block can use unique document-level amount context.
        shared = spans if len(route_groups) == 1 else group
        due = labelled(shared, "amount_due")
        role: Literal["amount_due", "invoice_total"] = (
            "amount_due" if due.state != "missing" else "invoice_total"
        )
        raw_amount = due if due.state != "missing" else labelled(shared, "invoice_total")
        amount, currency = amount_observation(raw_amount)
        printed_currency = labelled(shared, "currency")
        if printed_currency.value in {"GBP", "EUR"}:
            if currency.value is not None and currency.value != printed_currency.value:
                currency = Observation(
                    state="ambiguous",
                    raw_text=currency.raw_text,
                    evidence_ids=currency.evidence_ids + printed_currency.evidence_ids,
                )
            elif currency.state == "missing":
                currency = printed_currency
        beneficiary = labelled(group, "beneficiary_name")
        holder = labelled(group, "account_holder_name")
        # Do not promote supplier or account-holder text to a separately observed payee.
        remittance = Remittance(
            reference=labelled(group, "reference"),
            model=labelled(group, "model"),
            purpose_code=labelled(group, "purpose_code"),
            reference_requirement="required"
            if labelled(group, "reference").state != "missing"
            else "unknown",
        )
        routes: list[Destination] = []
        if any(labelled(group, n).state != "missing" for n in ("sort_code", "account_number")):
            routes.append(
                UKDestination(
                    sort_code=labelled(group, "sort_code"),
                    account_number=labelled(group, "account_number"),
                )
            )
            routing.applied_rule_packs.append("uk-labels@1")
        if labelled(group, "iban").state != "missing":
            routes.append(IBANDestination(iban=labelled(group, "iban"), bic=labelled(group, "bic")))
        if remittance.model.state != "missing" or any(
            "poziv na broj" in s.text.lower() for s in group
        ):
            routing.applied_rule_packs.append("hr-remittance@1")
        if not routes:
            routes.append(UnresolvedDestination(reason="Reference without a bank destination"))
        for destination in routes:
            # Two schemes in one paragraph do not justify sharing its amounts/reference.
            multiple = len(routes) > 1
            payment.candidates.append(
                Candidate(
                    id=f"candidate-{len(payment.candidates) + 1}",
                    beneficiary_name=beneficiary.model_copy(deep=True),
                    account_holder_name=holder.model_copy(deep=True),
                    amount=Amount(
                        value=amount if not multiple else Observation(),
                        currency=currency if not multiple else Observation(),
                        role=role if not multiple else "unknown",
                    ),
                    destination=destination,
                    remittance=remittance.model_copy(deep=True) if not multiple else Remittance(),
                )
            )
    routing.applied_rule_packs = list(dict.fromkeys(routing.applied_rule_packs))
    evidence = [
        Evidence(
            id=s.id,
            image_id=image_id,
            excerpt=s.text,
            grounding="ocr_span",
            source_stage_id=stage_id,
        )
        for s in spans
    ]
    return payment, evidence, routing
