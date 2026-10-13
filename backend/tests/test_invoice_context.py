import copy
import json

import httpx
import jsonschema
import pytest
from pydantic import ValidationError

from backend.adapters.compact import schema
from backend.adapters.extended import ExtendedAdapter
from backend.adapters.vision import vision_request
from backend.config import ModelOption
from backend.invoice_context import context_schema, extract_context
from backend.models import Diagnostics, IBANDestination, Observation, Run, Stage
from backend.profiles import registry
from backend.review_guidance import guidance, with_guidance
from backend.runtime import review_extraction
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5, reading
from backend.tests.test_extended import configured


def context_example(country="HR", language="hr"):
    data = example_v5()
    data["issuer_country"] = {
        **reading(country, basis="inferred"),
        "explanation": "Issuer address identifies Zagreb, Croatia.",
        "excerpts": ["Issuer address: Zagreb, Croatia"],
    }
    data["language"] = {
        **reading(language, basis="inferred"),
        "explanation": "The invoice uses Croatian labels.",
        "excerpts": ["Račun", "Poziv na broj"],
    }
    return data


def context_run(data):
    result = extract_context(json.dumps(data), "image", "stage", version="5")
    return Run(
        id="run",
        profile_id="synthetic",
        profile_version="1",
        state="completed",
        payment=review_extraction(result, "draft_v4"),
        evidence=result.evidence,
        diagnostics=Diagnostics(
            context_explanations=result.context_explanations,
            stages=[Stage(id="stage", method="vision", execution="external")],
        ),
    )


@pytest.mark.parametrize("version", ["5", "6"])
def test_context_schema_and_extraction_preserve_payment_claims(version):
    old = schema(version)
    original = copy.deepcopy(old)
    new = context_schema(old)
    jsonschema.validate(context_example(), new)
    assert old == original
    run = context_run(context_example())
    assert run.payment.candidates[0].destination.sort_code.value == "001122"
    g = guidance(run)
    assert g.issuer_country.value == "HR" and g.issuer_country.status == "inferred"
    assert "Zagreb" in g.issuer_country.reason
    assert g.issuer_country.excerpts == ["Issuer address: Zagreb, Croatia"]
    assert g.language.label == "Croatian"
    assert g.candidates[0].route == "uk_domestic"  # Country cannot override positive bank evidence.
    assert all(e.grounding == "model_claim" for e in run.evidence)


@pytest.mark.parametrize(
    "value",
    [
        None,
        {},
        {"values": ["HR"], "basis": "inferred", "explanation": "", "excerpts": []},
        {"values": ["HR"], "basis": "inferred", "explanation": "Croatian language", "excerpts": []},
    ],
)
def test_bad_context_retains_payment_without_false_missing_country(value):
    data = context_example()
    data["issuer_country"] = value
    run = context_run(data)
    assert run.payment.candidates[0].amount.value.value is not None
    assert guidance(run).issuer_country.status == "unknown"
    assert not any(r.path == "/document_context/issuer_country" for r in run.payment.review.reasons)


def test_context_conflict_and_invalid_country_are_not_flags():
    data = context_example()
    data["issuer_country"]["values"] = ["HR", "GR"]
    assert guidance(context_run(data)).issuer_country.status == "ambiguous"
    data["issuer_country"]["values"] = ["ZZ"]
    g = guidance(context_run(data))
    assert g.issuer_country.value is None and g.issuer_country.status == "unknown"
    data["language"]["values"] = ["unknown-language"]
    assert guidance(context_run(data)).language.label == "unknown-language"


def test_context_rejects_duplicate_keys_and_nonobjects():
    for text in ('{"language":{},"language":{}}', "[]"):
        with pytest.raises(ValueError):
            extract_context(text, "image", "stage", version="5")


@pytest.mark.parametrize(
    "country,iban",
    [
        ("HR", "HR1210010051863000160"),
        ("GR", "GR1601101250000000012300695"),
        ("GB", "GB82WEST12345698765432"),
    ],
)
def test_iban_field_applicability_is_independent_of_language(country, iban):
    data = context_example(country, "en")
    data["candidates"][0]["destination"] = {"kind": "iban", "iban": reading(iban), "bic": reading()}
    run = context_run(data)
    before = run.model_dump()
    g = guidance(run)
    fields = g.candidates[0].fields
    assert fields["/candidates/0/destination/sort_code"].requirement == "not_applicable"
    assert fields["/candidates/0/destination/iban"].requirement == "required"
    assert fields["/candidates/0/destination/bic"].requirement == "optional"
    assert g.candidates[0].account_country.value == country
    assert g.candidates[0].account_country.status == "derived"
    assert run.model_dump() == before


def test_unknown_route_never_becomes_ready_from_country():
    data = context_example()
    data["candidates"][0]["destination"] = {"kind": "unresolved", "details": []}
    run = context_run(data)
    g = guidance(run)
    assert g.candidates[0].fields["/candidates/0/destination/iban"].requirement == "unresolved"
    assert run.payment.review.state != "ready_for_review"
    assert g.candidates[0].warnings


def test_reference_and_model_requirements_preserve_uncertainty():
    data = context_example("GR", "el")
    c = data["candidates"][0]
    c["reference_requirement"] = "required"
    c["model"] = reading(basis="unreadable")
    g = guidance(context_run(data))
    fields = g.candidates[0].fields
    assert fields["/candidates/0/remittance/reference"].requirement == "required"
    assert fields["/candidates/0/remittance/model"].requirement == "required"
    c["reference_requirement"] = "unknown"
    c["model"] = reading()
    fields = guidance(context_run(data)).candidates[0].fields
    assert fields["/candidates/0/remittance/reference"].requirement == "unresolved"
    assert fields["/candidates/0/remittance/model"].requirement == "optional"


def test_old_scans_get_readonly_guidance_and_separate_candidate_rules(uk):
    before = uk.model_dump_json()
    run = uk.runs[0]
    other = run.payment.candidates[0].model_copy(deep=True)
    other.id = "other"
    other.destination = IBANDestination(iban=Observation())
    run.payment.candidates.append(other)
    before = uk.model_dump_json()
    annotated = with_guidance(uk)
    assert uk.model_dump_json() == before
    assert (
        annotated.runs[0]
        .review_guidance.candidates[1]
        .fields["/candidates/1/destination/sort_code"]
        .requirement
        == "not_applicable"
    )
    assert (
        annotated.runs[0]
        .review_guidance.candidates[0]
        .fields["/candidates/0/destination/sort_code"]
        .requirement
        == "required"
    )
    assert guidance(Run(id="x", profile_id="x", profile_version="x")) is None


@pytest.mark.parametrize(
    "provider", ["openai", "gemini", "mistral", "anthropic", "together", "xai"]
)
def test_context_is_standard_but_saved_request_options_remain_immutable(settings, provider):
    configured(settings, provider)
    option = settings.providers.options["test-profile"]
    option.protocol_version, option.field_policy = "5", "partial_v1"
    option.interpretation_policy = "draft_v4"
    original_option = option.snapshot_json()
    old_request = vision_request(option, "synthetic", "secret")
    assert "context_policy" not in option.snapshot_json()
    definition = registry(settings)["test-profile"]
    current = ModelOption.model_validate_json(definition.parameters["option"])
    assert current.context_policy == "invoice_v1"
    assert "invoice-context@1" in definition.metadata.component_ids
    assert "ContextReading" in json.dumps(vision_request(current, "synthetic", "secret"))
    assert option.snapshot_json() == original_option
    assert "ContextReading" not in json.dumps(old_request)
    option.context_policy = "invoice_v1"
    assert registry(settings)["test-profile"].snapshot() == definition.snapshot()
    option.context_policy = "none"
    assert registry(settings)["test-profile"].snapshot() == definition.snapshot()
    assert vision_request(option, "synthetic", "secret") == old_request


def test_context_configuration_rejects_unsupported_protocols():
    with pytest.raises(ValidationError):
        ModelOption(
            provider="openai", model="test", operation="vision", context_policy="invoice_v1"
        )


def test_context_call_end_to_end_and_read_projection_does_not_change_saved_result(settings, png):
    configured(settings, "openai")
    option = settings.providers.options["test-profile"]
    option.protocol_version, option.field_policy, option.context_policy = (
        "5",
        "partial_v1",
        "invoice_v1",
    )
    option.interpretation_policy = "draft_v4"
    calls = []

    def handle(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "model": option.model,
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": json.dumps(context_example())}],
                    }
                ],
            },
        )

    adapter = ExtendedAdapter(settings, httpx.MockTransport(handle))
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    with client_for(settings, {"test-profile": definition}, {"extended": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        run = result["runs"][0]
        assert run["state"] == "completed"
        assert run["review_guidance"]["issuer_country"]["value"] == "HR"
        assert "Zagreb" in run["diagnostics"]["context_explanations"]["issuer_country"]
        saved = client.app.state.store.get(result["scan_id"])
        assert saved.runs[0].review_guidance is None
        assert len(calls) == 1
        assert calls[0]["tools"] == []
