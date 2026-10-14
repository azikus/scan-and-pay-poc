import copy
import json

import httpx
import pytest
from pydantic import ValidationError

from backend.adapters.compact import CompactExtraction, PaymentOption, extract, schema
from backend.adapters.extended import ExtendedAdapter
from backend.adapters.vision import vision_request
from backend.models import Diagnostics, Run, Stage
from backend.profiles import registry
from backend.review import review_payment
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_extended import configured, llm_response


def reading(*values, basis="printed"):
    return {"values": list(values), "basis": basis}


def example():
    candidate = {
        k: reading()
        for k in PaymentOption.model_fields
        if k
        not in {
            "route",
            "amount_role",
            "reference_requirement",
            "option_label",
            "due_date",
            "payment_condition",
        }
    }
    candidate.update(
        beneficiary_name=reading("Synthetic Payee"),
        amount_text=reading("£1,234.50"),
        currency=reading("GBP"),
        amount_role="amount_due",
        route="uk_domestic",
        sort_code=reading("00-11-22"),
        account_number=reading("00123456"),
        reference_requirement="not_stated",
    )
    return {
        **{k: reading() for k in CompactExtraction.model_fields if k != "candidates"},
        "candidates": [candidate],
    }


def mapped(data):
    result = extract(json.dumps(data), "image", "stage")
    result.payment = review_payment(result.payment, result.evidence)
    Run(
        id="run",
        profile_id="test",
        profile_version="4",
        state="completed",
        payment=result.payment,
        evidence=result.evidence,
        diagnostics=Diagnostics(stages=[Stage(id="stage", method="vision", execution="external")]),
    )
    return result


def test_compact_maps_printed_claims_and_backend_owns_review():
    result = mapped(example())
    c = result.payment.candidates[0]
    assert c.destination.account_number.value == "00123456"
    assert c.destination.sort_code.value == "001122"
    assert c.amount.value.value == "1234.50" and c.amount.value.raw_text == "£1,234.50"
    assert result.payment.review.state == "ready_for_review"
    assert result.payment.review.user_confirmation_required
    assert all(e.bbox is None and e.grounding == "model_claim" for e in result.evidence)
    assert len({e.id for e in result.evidence}) == len(result.evidence)


def test_compact_preserves_candidate_associations_and_ambiguity():
    data = example()
    second = copy.deepcopy(data["candidates"][0])
    second.update(
        route="iban",
        sort_code=reading(),
        account_number=reading(),
        iban=reading("GB82 WEST 1234 5698 7654 32"),
        amount_text=reading("30,00"),
        currency=reading("€"),
        reference=reading("000123", "000128"),
        model=reading("HR00"),
        reference_requirement="required",
    )
    data["candidates"].append(second)
    result = mapped(data)
    first, second = result.payment.candidates
    assert first.amount.currency.value == "GBP" and first.amount.value.value == "1234.50"
    assert second.amount.currency.value == "EUR" and second.amount.value.value == "30.00"
    assert second.remittance.reference.value is None
    assert [v.value for v in second.remittance.reference.alternatives] == ["000123", "000128"]
    assert second.remittance.model.value == "HR00"
    assert second.destination.iban.raw_text == "GB82 WEST 1234 5698 7654 32"
    assert result.payment.selected_candidate_id is None


@pytest.mark.parametrize("basis", ["inferred", "unreadable", "unsupported"])
def test_compact_uncertainty_cannot_become_ready(basis):
    data = example()
    field = data["candidates"][0]["amount_text"]
    field.update(basis=basis, values=["£12.00"] if basis == "inferred" else [])
    result = mapped(data)
    assert result.payment.candidates[0].amount.value.state == basis
    assert result.payment.review.state != "ready_for_review"


def test_inferred_embedded_currency_is_not_promoted_to_printed():
    data = example()
    c = data["candidates"][0]
    c["amount_text"] = reading("£20.00", basis="inferred")
    c["currency"] = reading()
    result = mapped(data)
    assert result.payment.candidates[0].amount.currency.state == "inferred"
    assert result.payment.candidates[0].amount.currency.origin == "derived"


@pytest.mark.parametrize("currency", ["€", "$", "kr"])
def test_conflicting_or_unresolved_currency_never_guessed(currency):
    data = example()
    data["candidates"][0]["currency"] = reading(currency)
    result = mapped(data)
    assert result.payment.candidates[0].amount.currency.state == "ambiguous"
    assert result.payment.review.state != "ready_for_review"


def test_compact_empty_document_and_unresolved_and_biller_routes():
    data = example()
    data["candidates"] = []
    assert mapped(data).payment.review.state == "insufficient_data"
    for route in ["unresolved", "biller_reference"]:
        data = example()
        c = data["candidates"][0]
        c.update(route=route, sort_code=reading(), account_number=reading())
        if route == "biller_reference":
            c.update(biller_scheme=reading("Synthetic scheme"), biller_code=reading("0001"))
        result = mapped(data)
        assert result.payment.candidates[0].destination.kind == route
        assert result.payment.review.state != "ready_for_review"


@pytest.mark.parametrize(
    "kind", ["blank", "contradiction", "numeric_bank", "extra", "cross_route", "review"]
)
def test_compact_rejects_malformed_claims_without_salvage(kind):
    data = example()
    c = data["candidates"][0]
    if kind == "blank":
        c["account_number"] = reading(" ")
    if kind == "contradiction":
        c["account_number"] = reading("00123456", basis="unreadable")
    if kind == "numeric_bank":
        c["account_number"]["values"] = [123456]
    if kind == "extra":
        c["account_number"]["confidence"] = 1
    if kind == "cross_route":
        c["iban"] = reading("GB82 WEST 1234 5698 7654 32")
    if kind == "review":
        data["review"] = {"state": "ready_for_review"}
    with pytest.raises((ValueError, ValidationError)):
        mapped(data)


@pytest.mark.parametrize(
    "provider,schema_mode",
    [
        ("openai", "native"),
        ("anthropic", "prompt_json"),
        ("gemini", "prompt_json"),
        ("gemini", "native"),
        ("xai", "native"),
        ("together", "native"),
        ("mistral", "native"),
    ],
)
@pytest.mark.parametrize("version", ["4", "5", "6"])
def test_compact_live_protocol_offline_fixture(settings, png, provider, schema_mode, version):
    configured(settings, provider)
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = version
    opt.schema_mode = schema_mode
    if provider == "together":
        opt.reasoning = "none"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    text = json.dumps(example() if version == "4" else example_v5())
    calls = []

    def handler(request):
        calls.append(request)
        body = json.loads(request.content)
        if provider == "together":
            assert body["chat_template_kwargs"] == {"enable_thinking": False}
        if provider == "gemini":
            if schema_mode == "native":
                assert body["generationConfig"]["responseJsonSchema"] == schema(version)
            else:
                assert "responseJsonSchema" not in body["generationConfig"]
        if provider == "openai":
            response = {
                "model": opt.model,
                "status": "completed",
                "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
            }
        else:
            response = llm_response(provider, text, opt.model)
        return httpx.Response(200, json=response)

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["test-profile"]))["runs"][0]
        assert run["state"] == "completed", run["error"]
        assert run["payment"]["review"]["state"] == "ready_for_review"
        assert run["diagnostics"]["versions"]["prompt"] == "payment-image@" + version
        assert len(calls) == 1


@pytest.mark.parametrize("version", ["4", "5", "6"])
def test_compact_mistral_annotations_protocol(settings, png, version):
    configured(settings, "mistral", "annotations")
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = version
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True

    def handler(request):
        body = json.loads(request.content)
        assert body["document_annotation_format"]["json_schema"]["schema"] == schema(version)
        return httpx.Response(
            200,
            json={
                "model": opt.model,
                "document_annotation": json.dumps(example() if version == "4" else example_v5()),
            },
        )

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["test-profile"]))["runs"][0]
        assert run["state"] == "completed", run["error"]


def test_compact_schema_is_not_the_public_contract(settings):
    from backend.config import ModelOption

    opt = ModelOption(provider="anthropic", model="test", operation="vision", protocol_version="4")
    payload = vision_request(opt, "synthetic", "synthetic")[2]
    compiled = payload["output_config"]["format"]["schema"]
    assert "evidence" not in compiled["properties"]
    assert "Observation" not in compiled["$defs"]
    assert compiled["$defs"]["Reading"]["additionalProperties"] is False


def example_v5():
    data = example()
    for candidate in data["candidates"]:
        destination = {
            "kind": candidate.pop("route"),
            "sort_code": candidate.pop("sort_code"),
            "account_number": candidate.pop("account_number"),
        }
        for field in ["iban", "bic", "biller_scheme", "biller_code"]:
            candidate.pop(field)
        candidate["destination"] = destination
    return data


@pytest.mark.parametrize("kind", ["uk_domestic", "iban", "biller_reference", "unresolved"])
def test_v5_typed_destinations_preserve_claims(kind):
    data = example_v5()
    c = data["candidates"][0]
    if kind == "iban":
        c["destination"] = {
            "kind": kind,
            "iban": reading("GB82 WEST 1234 5698 7654 32"),
            "bic": reading(),
        }
    if kind == "biller_reference":
        c["destination"] = {
            "kind": kind,
            "scheme": reading("Synthetic biller"),
            "biller_code": reading("00012"),
        }
    if kind == "unresolved":
        c["destination"] = {"kind": kind, "details": [reading("untyped identifier 00012")]}
    result = extract(json.dumps(data), "image", "stage", version="5")
    payment = review_payment(result.payment, result.evidence)
    assert payment.candidates[0].destination.kind == kind
    if kind == "unresolved":
        assert any(e.excerpt == "untyped identifier 00012" for e in result.evidence)
        assert payment.review.state == "insufficient_data"
    if kind == "uk_domestic":
        assert payment.candidates[0].destination.account_number.value == "00123456"


def test_v5_rejects_cross_route_fields_instead_of_discarding():
    data = example_v5()
    data["candidates"][0]["destination"]["iban"] = reading("GB82 WEST 1234 5698 7654 32")
    with pytest.raises(ValidationError):
        extract(json.dumps(data), "image", "stage", version="5")
    assert "anyOf" in schema("5")["$defs"]["PaymentOptionV5"]["properties"]["destination"]


def test_compact_v6_fixed_destination_tags_use_supported_enums():
    old, revised = schema("5"), schema("6")
    for name, tag in (
        ("UKReading", "uk_domestic"),
        ("IBANReading", "iban"),
        ("BillerReading", "biller_reference"),
        ("UnresolvedReading", "unresolved"),
    ):
        before = old["$defs"][name]["properties"]["kind"]
        after = revised["$defs"][name]["properties"]["kind"]
        assert before["const"] == tag
        assert after["enum"] == [tag] and "const" not in after
        assert {k: v for k, v in before.items() if k != "const"} == {
            k: v for k, v in after.items() if k != "enum"
        }
