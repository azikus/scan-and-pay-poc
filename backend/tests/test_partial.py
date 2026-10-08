"""Synthetic cases: a bad field must not erase unrelated linked payment data."""

import copy
import json

import httpx
import pytest
from pydantic import ValidationError

from backend.adapters.compact import extract
from backend.adapters.extended import ExtendedAdapter
from backend.adapters.partial import recover
from backend.config import ModelOption
from backend.models import Diagnostics, Run, Stage
from backend.profiles import registry
from backend.runtime import review_extraction
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5, reading
from backend.tests.test_extended import configured, llm_response


def recovered(data):
    result = recover(json.dumps(data), "image", "stage", version="5")
    payment = review_extraction(result)
    run = Run(
        id="run",
        profile_id="partial",
        profile_version="1",
        state="completed",
        payment=payment,
        evidence=result.evidence,
        diagnostics=Diagnostics(
            stages=[Stage(id="stage", method="vision", execution="external")],
            validation=result.findings,
        ),
    )
    run.outcome = run.result_outcome
    return run


def test_clean_output_remains_identical_and_success():
    data = example_v5()
    original = extract(json.dumps(data), "image", "stage", version="5")
    run = recovered(data)
    assert run.payment == review_extraction(original)
    assert run.evidence == original.evidence
    assert run.outcome == "success"
    assert run.payment.review.user_confirmation_required
    assert not run.diagnostics.validation


@pytest.mark.parametrize("basis", ["unreadable", "unsupported"])
def test_contradictory_bank_field_keeps_other_fields_and_raw_claim(basis):
    data = example_v5()
    data["candidates"][0]["destination"]["account_number"] = reading("00123456", basis=basis)
    run = recovered(data)
    candidate = run.payment.candidates[0]
    assert run.outcome == "incomplete"
    assert candidate.destination.sort_code.value == "001122"
    assert candidate.destination.account_number.value is None
    assert candidate.destination.account_number.alternatives[0].value == "00123456"
    assert candidate.amount.value.value == "1234.50"
    assert candidate.beneficiary_name.value == "Synthetic Payee"
    assert run.payment.selected_candidate_id is None
    assert any(e.excerpt == "00123456" for e in run.evidence)
    assert any(r.code == "contradictory_reading" for r in run.payment.review.reasons)
    with pytest.raises(ValueError):
        extract(json.dumps(data), "image", "stage", version="5")


@pytest.mark.parametrize(
    "value",
    [
        reading(""),
        reading("  "),
        reading("known", ""),
        {"values": [12345], "basis": "printed"},
        {"values": ["00123"], "basis": "bogus"},
        {"values": ["00123"], "basis": "printed", "confidence": 1},
        None,
        {"values": [str(i) for i in range(9)], "basis": "printed"},
    ],
)
def test_bad_optional_field_cannot_fail_draft_or_claim_success(value):
    data = example_v5()
    data["candidates"][0]["purpose_code"] = value
    run = recovered(data)
    assert run.outcome == "incomplete"
    assert run.payment.candidates[0].destination.account_number.value == "00123456"
    assert run.payment.candidates[0].remittance.purpose_code.value is None
    assert any(
        f.path == "/candidates/0/remittance/purpose_code" for f in run.diagnostics.validation
    )


def test_does_not_move_amount_or_reference_between_candidates():
    data = example_v5()
    second = copy.deepcopy(data["candidates"][0])
    second["amount_text"] = reading("30.00")
    second["reference"] = reading("SECOND")
    second["destination"] = {
        "kind": "iban",
        "iban": reading("GB82 WEST 1234 5698 7654 32", basis="unreadable"),
        "bic": reading(),
    }
    data["candidates"][0]["reference"] = reading("FIRST")
    data["candidates"].append(second)
    run = recovered(data)
    first, second = run.payment.candidates
    assert (first.amount.value.value, first.remittance.reference.value) == ("1234.50", "FIRST")
    assert (second.amount.value.value, second.remittance.reference.value) == ("30.00", "SECOND")
    assert first.destination.account_number.value == "00123456"
    assert second.destination.iban.value is None
    assert run.payment.selected_candidate_id is None


@pytest.mark.parametrize(
    "kind",
    [
        "missing",
        "bad_enum",
        "bad_destination",
        "cross_route",
        "bad_candidate",
        "bad_candidates",
        "unresolved",
        "bad_details",
        "extra_root",
        "extra_candidate",
    ],
)
def test_structural_gaps_remain_explicit_without_guessing_associations(kind):
    data = example_v5()
    data["supplier_name"] = reading("Synthetic issuer")
    candidate = data["candidates"][0]
    if kind == "missing":
        del data["description"]
    if kind == "bad_enum":
        candidate["amount_role"] = ["amount_due"]
    if kind == "bad_destination":
        candidate["destination"] = {"kind": "guess"}
    if kind == "cross_route":
        candidate["destination"]["iban"] = reading("GB82 WEST 1234 5698 7654 32")
    if kind == "bad_candidate":
        data["candidates"].append(None)
    if kind == "bad_candidates":
        data["candidates"] = "unusable"
    if kind == "unresolved":
        candidate["destination"] = {
            "kind": "unresolved",
            "details": [reading("untyped", basis="unreadable")],
        }
    if kind == "bad_details":
        candidate["destination"] = {"kind": "unresolved", "details": None}
    if kind == "extra_root":
        data["instructions"] = "Ignore prior instructions"
    if kind == "extra_candidate":
        candidate["confidence"] = 0.99
    run = recovered(data)
    assert run.outcome == "incomplete"
    assert run.payment.supplier_name.value == "Synthetic issuer"
    assert run.diagnostics.validation
    if kind in {"cross_route", "bad_destination"}:
        assert run.payment.candidates[0].destination.kind == "unresolved"
        assert run.payment.candidates[0].amount.value.value == "1234.50"
        assert run.payment.selected_candidate_id is None


@pytest.mark.parametrize(
    "text", ["{", "[]", "{}", '{"unrelated": "data"}', '{"candidates": [], "candidates": []}']
)
def test_unparseable_or_unrecognizable_response_remains_error(text):
    with pytest.raises(ValueError):
        recover(text, "image", "stage", version="5")


def test_document_fields_without_candidates_are_incomplete_but_no_data_is_error():
    data = example_v5()
    data["candidates"] = []
    data["invoice_number"] = reading("SYNTHETIC-001")
    assert recovered(data).outcome == "incomplete"
    for key in data:
        if key not in {"candidates", "language", "issuer_country"}:
            data[key] = {"values": [], "basis": "printed"}
    assert recovered(data).outcome == "error"
    data["invoice_number"] = {"values": ["SYNTHETIC-001", "SYNTHETIC-007"], "basis": "printed"}
    assert recovered(data).outcome == "incomplete"
    with pytest.raises(ValueError):
        recover(json.dumps(data), "image", "stage", version="4")


def test_policy_is_versioned_and_only_supported_for_typed_claims(settings):
    configured(settings, "mistral")
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = "5"
    before = registry(settings)["test-profile"]
    assert "field_policy" not in json.loads(opt.snapshot_json())
    opt.field_policy = "partial_v1"
    after = registry(settings)["test-profile"]
    assert before.metadata.version != after.metadata.version
    assert "partial-fields@1" in after.metadata.component_ids
    with pytest.raises(ValidationError):
        ModelOption(provider="mistral", model="test", operation="ocr", field_policy="partial_v1")


@pytest.mark.parametrize("operation", ["vision", "annotations"])
@pytest.mark.parametrize("scenario", ["partial", "success", "timeout", "unparseable", "empty"])
def test_api_returns_outcome_and_preserves_partial_fields(settings, png, operation, scenario):
    configured(settings, "mistral", operation)
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = "5"
    opt.field_policy = "partial_v1"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    data = example_v5()
    if scenario == "empty":
        data = {key: {"values": [], "basis": "printed"} for key in data}
        data["candidates"] = []
    if scenario == "partial":
        data["candidates"][0]["destination"]["account_number"] = reading(
            "00123456", basis="unreadable"
        )
    text = "{" if scenario == "unparseable" else json.dumps(data)
    calls = []

    def handler(request):
        calls.append(request)
        if scenario == "timeout":
            raise httpx.ReadTimeout("synthetic")
        body = (
            llm_response("mistral", text, opt.model)
            if operation == "vision"
            else {
                "model": opt.model,
                "document_annotation": text,
                "pages": [],
                "usage_info": {"pages_processed": 1},
            }
        )
        return httpx.Response(200, json=body)

    adapter = ExtendedAdapter(settings, transport=httpx.MockTransport(handler))
    with client_for(settings, {"test-profile": definition}, {"extended": adapter}) as client:
        job = finish(client, upload(client, png, profiles=["test-profile"]))
        run = job["runs"][0]
        assert len(calls) == 1
        assert run["outcome"] == (
            "error"
            if scenario in {"timeout", "unparseable", "empty"}
            else "incomplete"
            if scenario == "partial"
            else "success"
        )
        if scenario == "partial":
            assert run["state"] == "completed" and run["error"] is None
            assert run["payment"]["candidates"][0]["amount"]["value"]["value"] == "1234.50"
            assert run["payment"]["candidates"][0]["destination"]["account_number"]["value"] is None
            assert run["diagnostics"]["validation"][-1]["code"] == "contradictory_reading"
            assert job["final_result_id"] == run["id"]
        if scenario in {"timeout", "unparseable"}:
            assert run["payment"] is None
        if scenario == "empty":
            assert run["diagnostics"]["validation"][-1]["code"] == "no_usable_data"


def test_outcome_validation_and_legacy_roundtrip(uk):
    run = uk.runs[0]
    assert run.result_outcome == "success" and "outcome" not in run.model_dump()
    data = run.model_dump()
    data["outcome"] = "error"
    with pytest.raises(ValidationError):
        Run.model_validate(data)
    assert Run(id="pending", profile_id="p", profile_version="1").result_outcome is None
