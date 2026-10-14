"""Synthetic bill drafts: channels are not obligations and never verify a real debt."""

import copy
import json

import httpx
import jsonschema
import pytest

from backend.adapters.compact import schema
from backend.adapters.extended import ExtendedAdapter
from backend.billers import channels, normalize_identifier
from backend.invoice_context import context_prompt, context_schema, extract_context
from backend.models import Diagnostics, Observation, Run, Stage
from backend.profiles import registry
from backend.review import review_payment
from backend.review_guidance import guidance
from backend.runtime import review_extraction
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import reading
from backend.tests.test_extended import configured
from backend.tests.test_invoice_context import context_example


def bill(scheme="pagoPA", dual=False):
    data = context_example("IT", "it")
    c = data["candidates"][0]
    c.update(
        amount_text=reading("80 Euro"),
        currency=reading("EUR"),
        reference=reading(),
        reference_requirement="not_stated",
        model=reading(),
    )
    c["destination"] = {
        "kind": "biller_reference",
        "scheme": reading(scheme),
        "biller_code": reading("0X123") if dual or scheme == "CBILL" else reading(),
        "notice_number": reading("0000 0000 0000 0000 01") if scheme == "pagoPA" else reading(),
        "creditor_tax_code": reading("00000000001") if scheme == "pagoPA" else reading(),
        "bill_reference": reading("BILL-0001") if scheme == "CBILL" else reading(),
    }
    return data


def run_for(data):
    extraction = extract_context(
        json.dumps(data), "image", "stage", version="6", policy="invoice_v3"
    )
    return Run(
        id="r",
        profile_id="synthetic",
        profile_version="1",
        state="completed",
        payment=review_extraction(extraction, "draft_v4"),
        evidence=extraction.evidence,
        diagnostics=Diagnostics(stages=[Stage(id="stage", method="vision", execution="external")]),
    )


@pytest.mark.parametrize(
    "scheme,dual,expected",
    [
        ("pagoPA", False, ["Your bank’s CBILL/pagoPA service"]),
        ("pagoPA", True, ["Your bank’s CBILL/pagoPA service"]),
        ("CBILL", False, ["CBILL via your bank"]),
    ],
)
def test_complete_biller_drafts_are_not_unsupported(scheme, dual, expected):
    data = bill(scheme, dual)
    before = copy.deepcopy(data)
    run = run_for(data)
    assert run.result_outcome == "success"
    assert run.payment.review.reasons == []
    assert len(run.payment.candidates) == 1
    assert run.payment.selected_candidate_id == "candidate-1"
    assert run.payment.review.user_confirmation_required
    g = guidance(run).candidates[0]
    assert g.supported_draft and g.payment_channels == expected
    assert "Not verified" in g.payment_note and "simulated" in g.payment_note
    assert ("pay only once" in g.payment_note) is (scheme == "pagoPA")
    assert g.fields["/candidates/0/destination/iban"].requirement == "not_applicable"
    assert g.fields["/candidates/0/remittance/model"].requirement == "optional"
    assert data == before
    if scheme == "pagoPA":
        d = run.payment.candidates[0].destination
        assert d.notice_number.value == "000000000000000001"
        assert d.notice_number.raw_text == "0000 0000 0000 0000 01"
        assert g.fields["/candidates/0/destination/biller_code"].requirement == "optional"


@pytest.mark.parametrize(
    "scheme,field,value,code",
    [
        ("pagoPA", "notice_number", reading(), "missing_required_field"),
        ("pagoPA", "notice_number", reading("00000000000000001"), "invalid_biller_identifier"),
        ("pagoPA", "notice_number", reading("00000000000000000O"), "invalid_biller_identifier"),
        (
            "pagoPA",
            "notice_number",
            reading("000000000000000001", "000000000000000002"),
            "ambiguous_field",
        ),
        ("pagoPA", "creditor_tax_code", reading(), "missing_required_field"),
        ("pagoPA", "creditor_tax_code", reading("123"), "invalid_biller_identifier"),
        (
            "pagoPA",
            "creditor_tax_code",
            reading("00000000001", basis="inferred"),
            "missing_required_field",
        ),
        ("CBILL", "biller_code", reading(), "missing_required_field"),
        ("CBILL", "biller_code", reading("123456"), "invalid_biller_identifier"),
        ("CBILL", "bill_reference", reading(), "missing_required_field"),
        ("CBILL", "bill_reference", reading(basis="unreadable"), "missing_required_field"),
    ],
)
def test_missing_or_uncertain_biller_identifiers_still_need_review(scheme, field, value, code):
    data = bill(scheme)
    data["candidates"][0]["destination"][field] = value
    run = run_for(data)
    assert run.result_outcome == "incomplete"
    assert any(r.code == code and r.path.endswith("/" + field) for r in run.payment.review.reasons)
    assert not any(r.code == "unsupported_payment_route" for r in run.payment.review.reasons)


def test_invalid_optional_cbill_code_does_not_advertise_second_channel():
    data = bill(dual=True)
    data["candidates"][0]["destination"]["biller_code"] = reading("123")
    run = run_for(data)
    assert run.result_outcome == "incomplete"
    assert guidance(run).candidates[0].payment_channels == ["Your bank’s CBILL/pagoPA service"]


@pytest.mark.parametrize("scheme", ["RF", "CBILL or something", "pagoPA/unknown"])
def test_unknown_schemes_never_become_supported_from_italian_country(scheme):
    run = run_for(bill(scheme))
    assert run.result_outcome == "incomplete"
    assert any(r.code == "unsupported_payment_route" for r in run.payment.review.reasons)
    assert not guidance(run).candidates[0].supported_draft
    assert guidance(run).candidates[0].payment_channels == []


def test_scheme_claim_without_evidence_cannot_advertise_channels_or_complete():
    run = run_for(bill(dual=True))
    d = run.payment.candidates[0].destination
    d.scheme.evidence_ids = []
    run.payment = review_payment(run.payment, run.evidence)
    assert run.payment.review.state != "ready_for_review"
    assert channels(d, run.evidence) == []


def test_distinct_notices_keep_their_own_identifiers_and_require_selection():
    data = bill(dual=True)
    c = copy.deepcopy(data["candidates"][0])
    c["destination"]["notice_number"] = reading("000000000000000002")
    c["amount_text"] = reading("20 EUR")
    c["amount_role"] = "instalment"
    data["candidates"].append(c)
    run = run_for(data)
    assert run.result_outcome == "incomplete"
    assert run.payment.selected_candidate_id is None
    assert [c.destination.notice_number.value for c in run.payment.candidates] == [
        "000000000000000001",
        "000000000000000002",
    ]
    assert [c.amount.value.value for c in run.payment.candidates] == ["80.00", "20.00"]


@pytest.mark.parametrize("version", ["5", "6"])
def test_new_schema_is_versioned_and_old_requests_keep_the_old_fields(version):
    original = schema(version)
    old = context_schema(original, policy="invoice_v2")
    new = context_schema(original, policy="invoice_v3")
    assert "notice_number" not in old["$defs"]["BillerReading"]["properties"]
    assert "notice_number" not in original["$defs"]["BillerReading"]["properties"]
    jsonschema.validate(bill(dual=True), new)
    assert "one candidate" in context_prompt("", policy="invoice_v3")
    assert "Italian bill-payment drafts" not in context_prompt("", policy="invoice_v2")


def test_old_biller_results_remain_readable_without_inventing_new_identifiers():
    data = bill()
    d = data["candidates"][0]["destination"]
    for name in ("notice_number", "creditor_tax_code", "bill_reference"):
        d.pop(name)
    run = run_for(data)
    assert run.result_outcome == "incomplete"
    assert run.payment.candidates[0].destination.notice_number.value is None


def test_malformed_notice_does_not_discard_other_printed_fields():
    data = bill(dual=True)
    data["candidates"][0]["destination"]["notice_number"] = {"values": [123], "basis": "printed"}
    run = run_for(data)
    d = run.payment.candidates[0].destination
    assert d.notice_number.value is None
    assert d.creditor_tax_code.value == "00000000001"
    assert d.biller_code.value == "0X123"
    assert run.result_outcome == "incomplete"


def test_normalization_never_repairs_identifier_digits():
    obs = Observation(
        value="000000000000000001",
        raw_text="00000000000000000I",
        state="observed",
        evidence_ids=["e"],
    )
    result = normalize_identifier(obs, "notice_number")
    assert result.state == "ambiguous" and result.value is None
    assert obs.value == "000000000000000001"


def test_api_biller_draft_uses_one_extraction_call_and_no_payment_api(settings, png):
    configured(settings, "openai")
    option = settings.providers.options["test-profile"]
    option.protocol_version, option.field_policy, option.interpretation_policy = (
        "6",
        "partial_v1",
        "draft_v4",
    )
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "model": option.model,
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": json.dumps(bill(dual=True))}],
                    }
                ],
            },
        )

    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    adapter = ExtendedAdapter(settings, httpx.MockTransport(handle))
    with client_for(settings, {"test-profile": definition}, {"extended": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        run = result["runs"][0]
        assert run["outcome"] == "success"
        assert run["review_guidance"]["candidates"][0]["payment_channels"] == [
            "Your bank’s CBILL/pagoPA service",
        ]
        saved = client.app.state.store.get(result["scan_id"])
        assert saved.runs[0].review_guidance is None
        assert len(calls) == 1
        assert calls[0].url.host == "api.openai.com"


@pytest.mark.parametrize("field", ["notice_number", "bill_reference"])
def test_blank_identifier_is_recoverable_not_a_whole_result_error(field):
    obs = Observation(value="   ", raw_text="   ", state="observed", evidence_ids=["e"])
    result = normalize_identifier(obs, field)
    assert result.state == "ambiguous" and result.value is None


@pytest.mark.parametrize(
    "change,accepted",
    [("legacy_absent", True), ("printed", False), ("unreadable", False), ("other_field", False)],
)
def test_frozen_legacy_confirmation_only_may_omit_wholly_absent_added_fields(uk, change, accepted):
    from backend.client_reviews import ClientReview, review_values, validate_review
    from backend.errors import ServiceError

    run = run_for(bill())
    run.payment.candidates[0].destination.notice_number = Observation()
    run.payment.candidates[0].destination.creditor_tax_code = Observation()
    uk.runs = [run]
    uk.final_result_id = run.id
    if change == "printed":
        run.payment.candidates[0].destination.notice_number = Observation(
            value="000000000000000001", state="observed"
        )
    if change == "unreadable":
        run.payment.candidates[0].destination.notice_number = Observation(state="unreadable")
    values = review_values(run.payment, run.payment.candidates[0].id)
    for name in ("notice_number", "creditor_tax_code", "bill_reference"):
        values.pop("/candidates/0/destination/" + name)
    if change == "other_field":
        values.pop("/supplier_name")
    review = ClientReview(
        run_id=run.id, selected_candidate_id=run.payment.candidates[0].id, values=values
    )
    before = review.model_dump()
    if accepted:
        validate_review(uk, review)
        assert review.model_dump() == before
    else:
        with pytest.raises(ServiceError):
            validate_review(uk, review)


def test_instalments_keep_dates_labels_and_are_a_choice_not_a_conflict():
    data = bill(dual=True)
    first = data["candidates"][0]
    first.update(
        option_label=reading("Rata 1"), due_date=reading("01/12/2025"), amount_role="instalment"
    )
    second = copy.deepcopy(first)
    second.update(option_label=reading("Rata 2"), due_date=reading("01/01/2026"))
    second["destination"]["notice_number"] = reading("000000000000000002")
    data["candidates"].append(second)
    run = run_for(data)
    assert [c.due_date.value for c in run.payment.candidates] == ["01/12/2025", "01/01/2026"]
    assert [r.code for r in run.payment.review.reasons] == ["payment_option_required"]
    assert (
        guidance(run).review_summary == "Choose a payment option; its printed details are complete."
    )
    assert run.result_outcome == "incomplete"  # An unresolved choice is not automatic success.


def test_exact_bank_postal_duplicates_merge_evidence_but_conflicting_amounts_do_not():
    data = bill(dual=True)
    data["candidates"].append(copy.deepcopy(data["candidates"][0]))
    run = run_for(data)
    assert run.result_outcome == "success" and len(run.payment.candidates) == 1
    assert len(run.payment.candidates[0].destination.notice_number.evidence_ids) == 2
    data["candidates"][1]["amount_text"] = reading("81 EUR")
    run = run_for(data)
    assert len(run.payment.candidates) == 2
    assert "conflicting_candidates" in [r.code for r in run.payment.review.reasons]


def test_condition_is_preserved_and_uncertain_condition_is_flagged():
    data = bill()
    condition = "Only if direct debit fails; check its status with your bank first."
    data["candidates"][0]["payment_condition"] = reading(condition)
    run = run_for(data)
    assert run.payment.candidates[0].payment_condition.value == condition
    assert run.result_outcome == "success"  # Completeness only, not payment authorization.
    data["candidates"][0]["payment_condition"] = {"values": [condition], "basis": "invalid"}
    run = run_for(data)
    assert run.result_outcome == "incomplete"
    assert run.payment.candidates[0].payment_condition.alternatives[0].value == condition


def test_cbill_organisation_can_identify_creditor_without_tax_code():
    data = bill(dual=True)
    data["candidates"][0]["destination"]["creditor_tax_code"] = reading()
    run = run_for(data)
    assert run.result_outcome == "success"
    fields = guidance(run).candidates[0].fields
    assert fields["/candidates/0/destination/creditor_tax_code"].requirement == "optional"
    assert fields["/candidates/0/destination/biller_code"].requirement == "required"


@pytest.mark.parametrize("version", ["5", "6"])
def test_option_schema_is_additive_and_old_schemas_are_frozen(version):
    old = context_schema(schema(version), policy="invoice_v3")
    new = context_schema(schema(version), policy="invoice_v4")
    assert "payment_condition" not in old["$defs"]["PaymentOptionV5"]["properties"]
    data = bill()
    data["candidates"][0].update(
        option_label=reading(), due_date=reading(), payment_condition=reading()
    )
    jsonschema.validate(data, new)
    assert "direct-debit" in context_prompt("", policy="invoice_v4")


def test_field_recovery_keeps_original_indices_instead_of_merging_duplicates():
    data = bill(dual=True)
    data["candidates"].append(copy.deepcopy(data["candidates"][0]))
    data["candidates"][1]["payment_condition"] = {"values": ["Check first"], "basis": "bad"}
    run = run_for(data)
    assert len(run.payment.candidates) == 2
    assert any(r.path == "/candidates/1/payment_condition" for r in run.payment.review.reasons)
    assert run.payment.candidates[1].payment_condition.state == "ambiguous"
