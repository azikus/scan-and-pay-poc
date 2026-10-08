"""Synthetic regressions for the separately versioned draft interpretation policy."""

import json

import httpx
import pytest
from pydantic import ValidationError

from backend.adapters.compact import PROMPT_V5
from backend.adapters.extended import ExtendedAdapter
from backend.adapters.vision import vision_request
from backend.config import ModelOption
from backend.draft_policy import draft_beneficiaries, preferred_candidate, prompt_v1, review_draft
from backend.models import (
    Alternative,
    BillerDestination,
    Finding,
    IBANDestination,
    Observation,
    Payment,
    Routing,
    UnresolvedDestination,
)
from backend.profiles import registry
from backend.review import review_payment
from backend.runtime import Extraction, review_extraction
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5, reading
from backend.tests.test_extended import configured, llm_response
from backend.tests.test_review import obs


def test_total_and_supplier_are_accepted_without_changing_source_roles(uk):
    payment, evidence = uk.runs[0].payment, uk.runs[0].evidence
    candidate = payment.candidates[0]
    candidate.amount.role = "invoice_total"
    candidate.beneficiary_name = Observation()
    candidate.account_holder_name = Observation()
    payment.supplier_name = obs("Synthetic Supplier")
    original = payment.model_dump()
    strict = review_payment(payment, evidence)
    draft = review_draft(payment, evidence)
    assert strict.review.state == "needs_review"
    assert draft.review.state == "ready_for_review"
    assert draft.review.user_confirmation_required
    assert draft.candidates[0].amount.role == "invoice_total"
    assert draft.candidates[0].beneficiary_name.value == payment.supplier_name.value
    assert draft.candidates[0].beneficiary_name.evidence_ids == payment.supplier_name.evidence_ids
    assert draft.candidates[0].beneficiary_name.normalization == ["draft_beneficiary_from_supplier"]
    assert draft.supplier_name == payment.supplier_name
    assert payment.model_dump() == original


@pytest.mark.parametrize("state", ["observed", "ambiguous", "unreadable"])
def test_explicit_recipient_is_never_replaced_by_manager_or_holder(uk, state):
    payment, evidence = uk.runs[0].payment, uk.runs[0].evidence
    c = payment.candidates[0]
    c.beneficiary_name = (
        obs("Synthetic Owners Community") if state == "observed" else Observation(state=state)
    )
    c.account_holder_name = obs("Synthetic Agent")
    payment.supplier_name = obs("Synthetic Supplier")
    result = draft_beneficiaries(payment, evidence)
    assert result.candidates[0].beneficiary_name == c.beneficiary_name
    assert result.candidates[0].account_holder_name == c.account_holder_name


@pytest.mark.parametrize(
    "bad",
    [
        "missing",
        "unreadable",
        "ambiguous",
        "inferred",
        "barcode",
        "no_evidence",
        "dangling",
        "empty_span",
        "alternatives",
    ],
)
def test_fallback_requires_a_supported_unambiguous_printed_reading(uk, bad):
    payment, evidence = uk.runs[0].payment, uk.runs[0].evidence
    c = payment.candidates[0]
    c.beneficiary_name = Observation()
    payment.supplier_name = Observation()
    c.account_holder_name = obs("Synthetic Holder")
    if bad in {"missing", "unreadable", "ambiguous"}:
        c.account_holder_name = Observation(state=bad)
    elif bad == "inferred":
        c.account_holder_name.state = "inferred"
    elif bad == "barcode":
        c.account_holder_name.origin = "barcode"
    elif bad == "no_evidence":
        c.account_holder_name.evidence_ids = []
    elif bad == "dangling":
        c.account_holder_name.evidence_ids = ["unknown"]
    elif bad == "empty_span":
        for e in evidence:
            e.excerpt = e.bbox = None
    else:
        c.account_holder_name.alternatives = [
            Alternative(value="Other", reason="Uncertain", evidence_ids=["e8"])
        ]
    assert draft_beneficiaries(payment, evidence).candidates[0].beneficiary_name.state == "missing"


def test_fallback_is_candidate_linked_and_global_supplier_cannot_override_recipient(uk):
    payment, evidence = uk.runs[0].payment, uk.runs[0].evidence
    first = payment.candidates[0]
    second = first.model_copy(deep=True)
    second.id = "second"
    second.beneficiary_name = Observation()
    second.account_holder_name = Observation()
    payment.candidates.append(second)
    payment.supplier_name = obs("Synthetic Manager")
    assert draft_beneficiaries(payment, evidence).candidates[1].beneficiary_name.state == "missing"
    second.account_holder_name = obs("Synthetic Linked Holder")
    result = draft_beneficiaries(payment, evidence)
    assert result.candidates[1].beneficiary_name.value == "Synthetic Linked Holder"
    assert result.candidates[1].beneficiary_name.normalization == [
        "draft_beneficiary_from_account_holder"
    ]
    assert result.candidates[0].beneficiary_name == first.beneficiary_name


@pytest.mark.parametrize(
    "change,code",
    [
        (lambda c: setattr(c.amount, "role", "other"), "amount_role_unresolved"),
        (lambda c: setattr(c.amount, "value", obs("-1.00")), "nonpositive_amount"),
        (lambda c: setattr(c.amount, "currency", Observation()), "missing_required_field"),
        (
            lambda c: setattr(
                c.amount,
                "currency",
                Observation(value="GBP", state="inferred", origin="caller_hint"),
            ),
            "currency_inferred",
        ),
        (
            lambda c: setattr(c.destination, "account_number", obs("O0000000")),
            "invalid_account_format",
        ),
    ],
)
def test_draft_total_does_not_suppress_other_failures(uk, change, code):
    p = uk.runs[0].payment
    p.candidates[0].amount.role = "invoice_total"
    change(p.candidates[0])
    result = review_draft(p, uk.runs[0].evidence)
    assert code in {r.code for r in result.review.reasons}
    assert result.review.state != "ready_for_review"


def test_bank_preference_preserves_all_options_and_their_associations(uk):
    p, evidence = uk.runs[0].payment, uk.runs[0].evidence
    bank = p.candidates[0]
    biller = bank.model_copy(deep=True)
    biller.id = "biller"
    biller.destination = BillerDestination(scheme=obs("Synthetic Scheme"), biller_code=obs("007"))
    biller.amount.value = obs("9.00")
    biller.remittance.reference = obs("OTHER-REF")
    p.candidates.insert(0, biller)
    result = review_draft(p, evidence)
    assert result.selected_candidate_id == bank.id
    assert len(result.candidates) == 2
    assert result.candidates[0].amount.value.value == "9.00"
    assert result.candidates[0].remittance.reference.value == "OTHER-REF"
    assert result.candidates[1].remittance.reference.value == bank.remittance.reference.value
    assert result.review.state == "needs_review"  # Existing v1 multiple-candidate contract.


@pytest.mark.parametrize("kind", ["uk_domestic", "iban", "biller_reference", "unresolved"])
@pytest.mark.parametrize("difference", [None, "currency", "account", "recipient", "second_total"])
def test_full_payment_preference_requires_matching_destination_and_currency(uk, kind, difference):
    p = uk.runs[0].payment
    first = p.candidates[0]
    if kind == "iban":
        first.destination = IBANDestination(iban=obs("GB82WEST12345698765432"))
    elif kind == "biller_reference":
        first.destination = BillerDestination(
            scheme=obs("Synthetic Scheme"), biller_code=obs("001")
        )
    elif kind == "unresolved":
        first.destination = UnresolvedDestination(reason="Synthetic untyped payment")
    first.amount.role = "invoice_total"
    second = first.model_copy(deep=True)
    second.id = "instalment"
    second.amount.role = "instalment"
    second.amount.value = obs("10.00")
    second.remittance.reference = obs("INSTALMENT-REF")
    p.candidates.append(second)
    if difference == "currency":
        second.amount.currency = obs("EUR")
    elif difference == "account":
        if kind == "uk_domestic":
            second.destination.account_number = obs("00123456")
        elif kind == "iban":
            second.destination.iban = obs("GB29NWBK60161331926819")
        elif kind == "biller_reference":
            second.destination.biller_code = obs("002")
    elif difference == "recipient":
        second.beneficiary_name = obs("Another Recipient")
    elif difference == "second_total":
        second.amount.role = "invoice_total"
    chosen = preferred_candidate(p)
    assert (chosen is not None) == (difference is None and kind != "unresolved")
    if chosen:
        assert chosen.id == first.id and chosen.remittance.reference != second.remittance.reference


def test_runtime_preserves_partial_findings_and_no_data(uk):
    result = Extraction(
        uk.runs[0].payment,
        uk.runs[0].evidence,
        Routing(),
        [
            Finding(
                code="contradictory_reading",
                path="/description",
                status="fail",
                message="Synthetic contradiction",
            )
        ],
    )
    assert review_extraction(result, "draft_v1").review.state == "needs_review"
    assert result.routing.applied_rule_packs == ["payment-draft@1"]
    review_extraction(result, "draft_v1")
    assert result.routing.applied_rule_packs == ["payment-draft@1"]
    assert review_draft(Payment(), []).review.state == "insufficient_data"
    with pytest.raises(ValueError, match="Unknown interpretation"):
        review_extraction(result, "unknown")


@pytest.mark.parametrize(
    "provider", ["openai", "mistral", "anthropic", "gemini", "xai", "together"]
)
def test_prompt_and_identity_are_opt_in_and_old_request_is_unchanged(settings, provider):
    configured(settings, provider)
    option = settings.providers.options["test-profile"]
    option.protocol_version = "6" if provider == "gemini" else "5"
    original = vision_request(option, "synthetic", "synthetic-key")
    old = registry(settings)["test-profile"]
    assert "interpretation_policy" not in json.loads(option.snapshot_json())
    option.interpretation_policy = "draft_v1"
    new = registry(settings)["test-profile"]
    prompt = json.dumps(vision_request(option, "synthetic", "synthetic-key")[2])
    assert "Do not decode QR" in prompt
    assert "Prefer bank transfer" in prompt
    assert "Do not copy a" not in prompt
    assert new.metadata.version != old.metadata.version
    assert "payment-draft@1" in new.metadata.component_ids
    assert new.parameters["prompt"].endswith("+draft@1")
    option.interpretation_policy = "strict"
    assert registry(settings)["test-profile"].snapshot() == old.snapshot()
    assert vision_request(option, "synthetic", "synthetic-key") == original
    assert "Do not decode QR" not in PROMPT_V5
    assert "distinct printed roles" in prompt_v1(PROMPT_V5)


def test_incompatible_legacy_prompt_rejected():
    with pytest.raises(ValidationError, match="typed compact"):
        ModelOption(
            provider="mistral",
            model="synthetic",
            operation="vision",
            interpretation_policy="draft_v1",
        )


@pytest.mark.parametrize("operation", ["vision", "annotations"])
@pytest.mark.parametrize("policy", ["strict", "draft_v1", "draft_v2", "draft_v3", "draft_v4"])
def test_actual_request_and_runtime_policy(settings, png, operation, policy):
    configured(settings, "mistral", operation)
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = "5"
    opt.field_policy = "partial_v1"
    opt.interpretation_policy = policy
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    data = example_v5()
    data["candidates"][0].update(
        beneficiary_name=reading(),
        account_holder_name=reading("Synthetic Holder"),
        amount_role="invoice_total",
    )
    calls = []

    def handler(request):
        calls.append(request)
        assert ("Do not decode QR" in request.content.decode()) == (policy != "strict")
        body = (
            llm_response("mistral", json.dumps(data), opt.model)
            if operation == "vision"
            else {
                "model": opt.model,
                "document_annotation": json.dumps(data),
                "pages": [],
                "usage_info": {"pages_processed": 1},
            }
        )
        return httpx.Response(200, json=body)

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["test-profile"]))["runs"][0]
        assert run["outcome"] == ("success" if policy != "strict" else "incomplete"), run
        assert len(calls) == 1
        assert run["payment"]["candidates"][0]["amount"]["role"] == "invoice_total"


@pytest.mark.parametrize("field", ["account", "currency", "recipient"])
def test_two_unknown_values_do_not_establish_a_shared_payment_identity(uk, field):
    p = uk.runs[0].payment
    first = p.candidates[0]
    first.amount.role = "invoice_total"
    if field == "account":
        first.destination.account_number = Observation()
    elif field == "currency":
        first.amount.currency = Observation()
    else:
        first.beneficiary_name = Observation()
    second = first.model_copy(deep=True)
    second.id = "instalment"
    second.amount.role = "instalment"
    p.candidates.append(second)
    assert preferred_candidate(p) is None
