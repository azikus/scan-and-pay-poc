"""Read-only presentation policy, separate from immutable extraction and confirmation values."""

from typing import Literal

import pycountry

from backend.models import (
    CandidateGuidance,
    ContextHint,
    FieldRule,
    Observation,
    Reason,
    ReviewGuidance,
    Run,
    Scan,
)


def context_hint(run: Run, observation: Observation, key: str) -> ContextHint:
    evidence = {e.id: e for e in run.evidence}
    supporting_ids = [i for i in observation.evidence_ids if i.startswith("context-" + key + "-")]
    excerpts = list(
        dict.fromkeys(
            excerpt
            for i in supporting_ids or observation.evidence_ids
            if i in evidence
            if (excerpt := evidence[i].excerpt) is not None and excerpt
        )
    )
    explanation = run.diagnostics.context_explanations.get(key)
    result = ContextHint(
        reason=explanation or "The saved extraction did not establish this context.",
        evidence_ids=observation.evidence_ids,
        excerpts=excerpts,
    )
    if observation.state == "ambiguous" or observation.alternatives:
        result.status = "ambiguous"
        result.reason = explanation or "The saved extraction contains conflicting context readings."
        return result
    value = observation.value
    if value is None:
        return result
    if key != "language":
        try:
            country = pycountry.countries.lookup(value.strip())
        except LookupError:
            result.reason = "The country reading is not a recognized country; review the source."
            return result
        result.value, result.label = country.alpha_2, country.name
    else:
        result.value = value
        try:
            result.label = pycountry.languages.lookup(value.split("-")[0]).name
        except LookupError:
            result.label = value
    result.status = (
        "derived"
        if "iban_country_prefix" in observation.normalization
        else "inferred"
        if observation.state == "inferred" or observation.origin == "caller_hint"
        else "observed"
    )
    result.reason = explanation or (
        "Account country derived from the IBAN prefix; it does not identify the issuer country."
        if "iban_country_prefix" in observation.normalization
        else "Context recorded by the extractor; no supporting explanation was saved."
    )
    return result


def guidance(run: Run) -> ReviewGuidance | None:
    payment = run.payment
    if payment is None:
        return None
    doc_fields = {
        "/" + key: FieldRule(requirement="optional", reason="Additional invoice information.")
        for key in ("supplier_name", "invoice_number", "customer_number", "description", "due_date")
    }
    for key in ("language", "issuer_country"):
        doc_fields["/document_context/" + key] = FieldRule(
            requirement="optional", reason="Document context; not a required payment value."
        )
    candidates = []
    for index, candidate in enumerate(payment.candidates):
        prefix = f"/candidates/{index}"
        fields: dict[str, FieldRule] = {}

        def rule(
            path: str,
            requirement: Literal["required", "optional", "not_applicable", "unresolved"],
            reason: str,
            fields: dict[str, FieldRule] = fields,
            prefix: str = prefix,
        ) -> None:
            fields[prefix + path] = FieldRule(requirement=requirement, reason=reason)

        for path in ("/beneficiary_name", "/amount/value", "/amount/currency"):
            rule(path, "required", "Needed to review this payment draft.")
        for path in ("/account_holder_name", "/account_country", "/remittance/purpose_code"):
            rule(path, "optional", "Additional payment information when available.")
        kind = candidate.destination.kind
        for route, names in {
            "uk_domestic": ("sort_code", "account_number"),
            "iban": ("iban", "bic"),
            "biller_reference": ("scheme", "biller_code"),
        }.items():
            for name in names:
                requirement: Literal["required", "optional", "not_applicable", "unresolved"]
                requirement = (
                    "unresolved"
                    if kind == "unresolved"
                    else "not_applicable"
                    if kind != route
                    else "optional"
                    if name == "bic"
                    else "required"
                )
                rule(
                    "/destination/" + name,
                    requirement,
                    "Route is unresolved; no bank field requirement was guessed."
                    if kind == "unresolved"
                    else "Not used by this payment route."
                    if kind != route
                    else "Additional bank identifier; optional for this PoC's IBAN draft."
                    if name == "bic"
                    else "Required by the extracted payment route.",
                )
        reference = candidate.remittance.reference_requirement
        rule(
            "/remittance/reference",
            "required"
            if reference == "required"
            else "optional"
            if reference == "not_stated"
            else "unresolved",
            "The document requires a payment reference."
            if reference == "required"
            else "No reference requirement was stated."
            if reference == "not_stated"
            else "Reference requirement is uncertain; review the payment instructions.",
        )
        model = candidate.remittance.model
        # A printed or uncertain model stays relevant even for a foreign issuer/account.
        # Absence alone never establishes either the country or a missing HR00.
        rule(
            "/remittance/model",
            "required" if model.state != "missing" else "optional",
            "Preserve the model printed for this payment option."
            if model.state != "missing"
            else "Add a Croatian payment model only when specified by the document.",
        )
        warnings = [r for r in payment.review.reasons if r.path.startswith(prefix + "/")]
        if kind in {"unresolved", "biller_reference"} and not any(
            r.code == "unsupported_payment_route" for r in warnings
        ):
            warnings.append(
                Reason(
                    code="unsupported_payment_route",
                    path=prefix + "/destination",
                    message="Payment destination needs review; no bank route was inferred.",
                )
            )
        candidates.append(
            CandidateGuidance(
                candidate_id=candidate.id,
                route=kind,
                account_country=context_hint(run, candidate.account_country, "account_country"),
                fields=fields,
                warnings=warnings,
            )
        )
    return ReviewGuidance(
        issuer_country=context_hint(run, payment.document_context.issuer_country, "issuer_country"),
        language=context_hint(run, payment.document_context.language, "language"),
        document_fields=doc_fields,
        candidates=candidates,
    )


def with_guidance(scan: Scan) -> Scan:
    result = scan.model_copy(deep=True)
    for run in result.runs:
        run.review_guidance = guidance(run)
    return result
