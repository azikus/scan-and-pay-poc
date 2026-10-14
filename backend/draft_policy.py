"""Opt-in draft interpretation @1; historical review and prompts remain unchanged."""

from backend.billers import deduplicate_notices, grounded, scheme_key
from backend.models import BillerDestination, Candidate, Evidence, Observation, Payment
from backend.review import normalize_payment, review_payment

VERSION = "payment-draft@1"


def prompt_v1(prompt: str) -> str:
    """A separately named revision of the compact prompt, not a changed baseline."""
    return (
        prompt.replace(
            "Keep supplier, billed customer, beneficiary and account holder distinct. Do not copy a\n"
            "supplier into beneficiary without explicit payment instructions supporting that role.",
            "Keep supplier, billed customer, beneficiary and account holder as distinct printed roles.\n"
            "Extract an explicitly identified recipient even when a manager, agent or supplier has a\n"
            "different name. Never substitute the billed customer or representative for that recipient.\n"
            "When no explicit recipient is printed, retain the supplier and candidate-linked account\n"
            "holder in their own fields; the backend may use them as draft beneficiary fallbacks.",
        )
        + """
Use only human-readable printed text. Do not decode QR, Data Matrix, PDF417 or other
barcode payloads, reconstruct masked content, or fetch referenced URLs. Text printed
beside or beneath a barcode may be transcribed normally.
An invoice total is acceptable for the draft: keep its invoice_total role and do not
relabel it amount_due. Preserve full-payment and instalment options with their OWN
printed references and accounts. Prefer bank transfer when several payment methods
are offered, but retain all distinct candidates; the backend owns default selection.
Do not combine an instalment reference with a full total, compute a missing total,
or import information from other pages. Do not infer currency from location/language.
"""
    )


def supported(obs: Observation, evidence: list[Evidence]) -> bool:
    by_id = {e.id: e for e in evidence}
    return (
        obs.state == "observed"
        and obs.origin == "document"
        and not obs.alternatives
        and bool(obs.evidence_ids)
        and all(
            i in by_id and (by_id[i].excerpt is not None or by_id[i].bbox is not None)
            for i in obs.evidence_ids
        )
    )


def draft_beneficiaries(payment: Payment, evidence: list[Evidence]) -> Payment:
    result = payment.model_copy(deep=True)
    # A global supplier cannot override another explicitly linked recipient.
    explicit_recipient = any(c.beneficiary_name.state != "missing" for c in result.candidates)
    for candidate in result.candidates:
        if candidate.beneficiary_name.state != "missing":
            continue
        source = candidate.account_holder_name
        role = "account_holder"
        if source.state == "missing" and not explicit_recipient:
            source, role = result.supplier_name, "supplier"
        if supported(source, evidence):
            candidate.beneficiary_name = source.model_copy(deep=True)
            candidate.beneficiary_name.normalization.append("draft_beneficiary_from_" + role)
    return result


def preferred_candidate(payment: Payment) -> Candidate | None:
    candidates = payment.candidates
    banks = [c for c in candidates if c.destination.kind in {"iban", "uk_domestic"}]
    pool = banks or candidates
    if len(pool) == 1:
        return pool[0]
    # Prefer full payment over instalments only within the SAME recipient/route/currency.
    # Multiple accounts, currencies or unresolved meanings remain an explicit choice.
    full = [c for c in pool if c.amount.role in {"amount_due", "invoice_total"}]
    if len(full) != 1 or not all(c.amount.role == "instalment" for c in pool if c not in full):
        return None
    chosen = full[0]

    def identity(c: Candidate) -> tuple[object, ...]:
        destination = c.destination
        linked = [c.beneficiary_name, c.amount.currency]
        route: tuple[object, ...]
        if destination.kind == "iban":
            linked.append(destination.iban)
            route = (destination.kind, destination.iban.value)
        elif destination.kind == "uk_domestic":
            linked.extend([destination.sort_code, destination.account_number])
            route = (
                destination.kind,
                destination.sort_code.value,
                destination.account_number.value,
            )
        elif destination.kind == "biller_reference":
            identifiers = [
                destination.scheme,
                destination.biller_code,
                destination.notice_number,
                destination.creditor_tax_code,
                destination.bill_reference,
            ]
            linked.extend(o for o in identifiers if o.state != "missing")
            route = (destination.kind, *(o.value for o in identifiers))
        else:
            route = (destination.kind, c.id)
        if any(o.state != "observed" or o.value is None or o.alternatives for o in linked):
            return ("unresolved", c.id)
        return route, c.beneficiary_name.value, c.amount.currency.value

    return chosen if all(identity(c) == identity(chosen) for c in pool) else None


def review_draft(
    payment: Payment, evidence: list[Evidence], *, merge_duplicates: bool = True
) -> Payment:
    prepared = normalize_payment(draft_beneficiaries(payment, evidence))
    if merge_duplicates:
        prepared = deduplicate_notices(prepared, evidence)
    result = review_payment(prepared, evidence)
    accepted = {
        f"/candidates/{i}/amount/role"
        for i, c in enumerate(result.candidates)
        if c.amount.role == "invoice_total"
        or (
            c.amount.role == "instalment"
            and isinstance(c.destination, BillerDestination)
            and scheme_key(c.destination) is not None
        )
    }
    result.review.reasons = [
        r
        for r in result.review.reasons
        if not (r.code == "amount_role_unresolved" and r.path in accepted)
    ]
    # Different, grounded notice numbers are choices, not contradictory readings.
    notices = [
        c.destination.notice_number
        for c in result.candidates
        if isinstance(c.destination, BillerDestination) and scheme_key(c.destination) == "pagopa"
    ]
    if (
        len(notices) == len(result.candidates) > 1
        and all(grounded(n, evidence) for n in notices)
        and len({n.value for n in notices}) == len(notices)
    ):
        for reason in result.review.reasons:
            if reason.code == "conflicting_candidates":
                reason.code = "payment_option_required"
                reason.message = (
                    "Choose the printed full payment or instalment you intend to review."
                )
    preferred = preferred_candidate(normalize_payment(result))
    if preferred is not None:
        # Selection is a draft preference, not a claim of completeness or ownership.
        result.selected_candidate_id = preferred.id
    if not result.review.reasons and len(result.candidates) == 1:
        result.review.state = "ready_for_review"
    # Multiple candidates stay reviewable under v1 even with a deterministic preference.
    return Payment.model_validate(result.model_dump())
