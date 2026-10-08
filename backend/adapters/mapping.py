"""Conservative field mapping, without OCR augmentation or supplier-to-payee promotion."""

import pycountry

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
from backend.ocr_rules import amount_observation
from backend.runtime import Extraction


def map_fields(
    fields: dict[str, list[str]], image_id: str, stage_id: str, *, version: str = "1"
) -> Extraction:
    evidence: list[Evidence] = []

    def observation(name: str) -> Observation:
        values = list(dict.fromkeys(v for v in fields.get(name, []) if v.strip()))
        ids = []
        for value in values:
            ident = f"field-{len(evidence)}"
            ids.append(ident)
            evidence.append(
                Evidence(
                    id=ident,
                    image_id=image_id,
                    excerpt=value,
                    grounding="model_claim",
                    source_stage_id=stage_id,
                )
            )
        if not values:
            return Observation()
        if len(values) > 1:
            return Observation(
                state="ambiguous",
                raw_text=" | ".join(values),
                evidence_ids=ids,
                alternatives=[
                    Alternative(value=v, evidence_ids=[i], reason="Multiple returned field values")
                    for v, i in list(zip(values, ids, strict=True))[:8]
                ],
            )
        return Observation(value=values[0], raw_text=values[0], state="observed", evidence_ids=ids)

    payment = Payment()
    for name in ("supplier_name", "invoice_number", "customer_number", "due_date", "description"):
        setattr(payment, name, observation(name))
    sort, account, iban, bic = (
        observation(n) for n in ("sort_code", "account_number", "iban", "bic")
    )
    destinations: list[Destination] = []
    if sort.state != "missing":
        destinations.append(UKDestination(sort_code=sort, account_number=account))
    if iban.state != "missing":
        destinations.append(IBANDestination(iban=iban, bic=bic))
    if not destinations:
        destinations.append(
            UnresolvedDestination(
                reason="Document API supplies no explicit supported bank scheme; untyped account claims retained as evidence"
            )
        )
    raw_due = observation("amount_due")
    total = observation("invoice_total")
    due = raw_due.state != "missing"
    amount, currency = amount_observation(raw_due if due else total)
    explicit_currency = observation("currency")
    if version == "2" and explicit_currency.value is not None:
        raw_code = explicit_currency.value.strip()
        code = {"€": "EUR", "£": "GBP"}.get(raw_code, raw_code.upper())
        if pycountry.currencies.get(alpha_3=code) is not None:
            explicit_currency.value = code
            if code != raw_code:
                explicit_currency.normalization.append("explicit_currency_token")
        else:
            explicit_currency.value = None
            explicit_currency.state = "ambiguous"
    if explicit_currency.state == "ambiguous":
        currency = explicit_currency
    elif explicit_currency.value is not None:
        if currency.value is not None and currency.value != explicit_currency.value:
            currency = Observation(
                state="ambiguous",
                evidence_ids=currency.evidence_ids + explicit_currency.evidence_ids,
            )
        elif currency.state == "missing":
            currency = explicit_currency
    beneficiary, holder = observation("beneficiary_name"), observation("account_holder_name")
    reference, model, purpose = (observation(n) for n in ("reference", "model", "purpose_code"))
    for destination in destinations:
        single = len(destinations) == 1
        payment.candidates.append(
            Candidate(
                id=f"candidate-{len(payment.candidates) + 1}",
                destination=destination,
                beneficiary_name=beneficiary.model_copy(deep=True),
                account_holder_name=holder.model_copy(deep=True),
                amount=Amount(
                    value=amount, currency=currency, role="amount_due" if due else "invoice_total"
                )
                if single
                else Amount(),
                remittance=Remittance(
                    reference=reference,
                    model=model,
                    purpose_code=purpose,
                    reference_requirement="unknown",
                )
                if single
                else Remittance(),
            )
        )
    return Extraction(
        payment,
        evidence,
        Routing(
            applied_rule_packs=["document-mapping@" + version],
            reasons=[
                "Only returned fields mapped; unsupported fields stay missing; no OCR augmentation."
            ],
        ),
    )
