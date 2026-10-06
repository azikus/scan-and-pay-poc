"""Deterministic completeness checks; never a claim of account ownership."""

import re
from decimal import Decimal
from typing import Literal

import pycountry
from schwifty import IBAN

from backend.models import (
    Alternative,
    Evidence,
    IBANDestination,
    Observation,
    Payment,
    Reason,
    Review,
    UKDestination,
)


def normalized(observation: Observation, value: str, step: str) -> Observation:
    result = observation.model_copy(deep=True)
    if result.value != value:
        result.value = value
        result.normalization.append(step)
    return result


def bank_normalized(
    observation: Observation, *, field: Literal["iban", "sort_code", "account_number"]
) -> Observation:
    if observation.value is None:
        return observation.model_copy(deep=True)
    iban = field == "iban"
    pattern = r"\s" if iban else r"[\s-]"
    value = re.sub(pattern, "", observation.value)
    labels = {
        "iban": r"(?:recipient |primatelj )?IBAN",
        "sort_code": r"sort[ -]?code",
        "account_number": r"(?:bank )?account (?:number|no\.?)",
    }
    raw_value = re.sub(
        r"^\s*(?:" + labels[field] + r")\s*[:：]\s*",
        "",
        observation.raw_text or "",
        count=1,
        flags=re.I,
    )
    raw = re.sub(pattern, "", raw_value)
    if iban:
        value, raw = value.upper(), raw.upper()
    if observation.raw_text is not None and value != raw:
        return Observation(
            state="ambiguous",
            origin=observation.origin,
            raw_text=observation.raw_text,
            evidence_ids=observation.evidence_ids,
            alternatives=[
                Alternative(
                    value=value,
                    reason="Proposed value changes printed characters; no repair accepted",
                    evidence_ids=observation.evidence_ids,
                )
            ],
        )
    return normalized(
        observation, value, "iban_remove_spaces_uppercase" if iban else "remove_bank_separators"
    )


def normalize_payment(payment: Payment) -> Payment:
    """Only reversible formatting edits; never repair, pad or cross-pair digits."""
    result = payment.model_copy(deep=True)
    for c in result.candidates:
        if c.account_country.value is not None:
            try:
                country = pycountry.countries.lookup(c.account_country.value.strip())
            except LookupError:
                pass
            else:
                c.account_country = normalized(
                    c.account_country, country.alpha_2, "explicit_country_to_iso_alpha2"
                )
        d = c.destination
        if isinstance(d, UKDestination):
            if d.sort_code.value is not None:
                d.sort_code = bank_normalized(d.sort_code, field="sort_code")
            if d.account_number.value is not None:
                d.account_number = bank_normalized(d.account_number, field="account_number")
        if isinstance(d, IBANDestination) and d.iban.value is not None:
            d.iban = bank_normalized(d.iban, field="iban")
            if (
                d.iban.value is not None
                and re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]+", d.iban.value)
                and c.account_country.state == "missing"
            ):
                c.account_country = Observation(
                    value=d.iban.value[:2],
                    state="inferred",
                    origin="derived",
                    evidence_ids=d.iban.evidence_ids,
                    normalization=["iban_country_prefix"],
                )
    return result


def review_payment(payment: Payment, evidence: list[Evidence]) -> Payment:
    result = normalize_payment(payment)
    reasons: list[Reason] = []
    evidence_by_id = {e.id: e for e in evidence}

    def reason(code: str, path: str, message: str) -> None:
        reasons.append(Reason(code=code, path=path, message=message))

    def check(obs: Observation, path: str, code: str = "missing_required_field") -> bool:
        grounded = bool(obs.evidence_ids) and all(
            i in evidence_by_id
            and (evidence_by_id[i].excerpt is not None or evidence_by_id[i].bbox is not None)
            for i in obs.evidence_ids
        )
        valid = (
            obs.state == "observed"
            and obs.origin in {"document", "barcode"}
            and grounded
            and not obs.alternatives
        )
        if not valid:
            reason(
                "ambiguous_field" if obs.state == "ambiguous" or obs.alternatives else code,
                path,
                "Printed, unambiguous document evidence is required.",
            )
        return valid

    if len(result.candidates) > 1:
        reason(
            "conflicting_candidates", "/candidates", "Multiple payment options require a choice."
        )
    meaningful = False
    complete_route = False
    for n, c in enumerate(result.candidates):
        p = f"/candidates/{n}"
        check(c.beneficiary_name, p + "/beneficiary_name", "beneficiary_unresolved")
        check(c.amount.value, p + "/amount/value")
        if c.amount.value.value is not None and Decimal(c.amount.value.value) <= 0:
            reason(
                "nonpositive_amount",
                p + "/amount/value",
                "Amount must be positive for a payment draft.",
            )
        if c.amount.role != "amount_due":
            reason(
                "amount_role_unresolved",
                p + "/amount/role",
                "The amount is not explicitly an amount due.",
            )
        check(
            c.amount.currency,
            p + "/amount/currency",
            "currency_inferred"
            if c.amount.currency.state == "inferred"
            or c.amount.currency.origin in {"caller_hint", "derived"}
            else "missing_required_field",
        )
        # Initial currency semantics are GBP/EUR. Other ISO currencies remain reviewable.
        if c.amount.currency.value not in {None, "GBP", "EUR"}:
            reason(
                "ambiguous_field",
                p + "/amount/currency",
                "Currency semantics require review in this initial profile.",
            )
        d = c.destination
        if isinstance(d, UKDestination):
            meaningful |= any(o.state != "missing" for o in (d.sort_code, d.account_number))
            if c.account_country.value not in {None, "GB"}:
                reason(
                    "ambiguous_field",
                    p + "/account_country",
                    "Account-country observation conflicts with the destination.",
                )
            complete_route = True
            for name, length in (("sort_code", 6), ("account_number", 8)):
                obs = getattr(d, name)
                complete_route &= check(obs, p + "/destination/" + name)
                if obs.value is not None and not re.fullmatch(rf"[0-9]{{{length}}}", obs.value):
                    complete_route = False
                    reason(
                        "invalid_account_format",
                        p + "/destination/" + name,
                        "Account component has invalid format; no digits were repaired.",
                    )
        elif isinstance(d, IBANDestination):
            meaningful |= d.iban.state != "missing"
            if d.iban.value is not None and c.account_country.value not in {None, d.iban.value[:2]}:
                reason(
                    "ambiguous_field",
                    p + "/account_country",
                    "Account-country observation conflicts with the destination.",
                )
            complete_route = check(d.iban, p + "/destination/iban")
            if d.iban.value is not None:
                try:
                    IBAN(d.iban.value)
                except ValueError:
                    complete_route = False
                    reason(
                        "failed_iban_checksum",
                        p + "/destination/iban",
                        "IBAN format/checksum failed; account ownership is not checked.",
                    )
        else:
            complete_route = False
            reason(
                "unsupported_payment_route",
                p + "/destination",
                "No implemented bank route or biller resolver.",
            )
        r = c.remittance
        if r.reference_requirement == "unknown":
            reason(
                "reference_requirement_unknown",
                p + "/remittance/reference_requirement",
                "Payment reference requirement is uncertain.",
            )
        if r.reference_requirement == "required":
            check(r.reference, p + "/remittance/reference")
        if r.model.state != "missing":
            check(r.model, p + "/remittance/model")
            if r.model.value is not None and not re.fullmatch(r"HR[0-9]{2}", r.model.value):
                reason(
                    "invalid_account_format",
                    p + "/remittance/model",
                    "Croatian model must preserve the printed HR model.",
                )
        # A seen but unresolved reference/model cannot silently disappear from readiness.
        if r.reference.state in {"ambiguous", "unreadable", "unsupported"}:
            check(r.reference, p + "/remittance/reference")
        if c.account_holder_name.state in {"ambiguous", "unreadable"}:
            check(c.account_holder_name, p + "/account_holder_name", "beneficiary_unresolved")
    if not result.candidates:
        reason("missing_required_field", "/candidates", "No payment option was found.")
    state: Literal["ready_for_review", "needs_review", "insufficient_data"] = (
        "ready_for_review" if not reasons else "needs_review" if meaningful else "insufficient_data"
    )
    result.review = Review(state=state, reasons=reasons)
    result.selected_candidate_id = (
        result.candidates[0].id if len(result.candidates) == 1 and complete_route else None
    )
    return Payment.model_validate(result.model_dump())
