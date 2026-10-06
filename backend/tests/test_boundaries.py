from dataclasses import replace

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from backend.errors import ServiceError
from backend.images import prepare_image
from backend.models import Hints, Observation
from backend.ocr_rules import extract_rules
from backend.profiles import validate_limits
from backend.providers import MistralAdapter, OpenAIAdapter
from backend.review import review_payment
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_providers import definition, mistral_response, openai_response
from backend.tests.test_review import UK


def test_ocr_blank_fields_table_rows_and_conflicting_currency():
    text = (
        UK.replace("Sort code: 00-01-02", "| Sort code | 00-01-02 |")
        + "Currency: EUR\nModel:\nAccount number:\n"
    )
    p, e, _ = extract_rules(text, "image", "ocr")
    p = review_payment(p, e)
    assert p.candidates[0].destination.sort_code.value == "000102"
    assert p.candidates[0].destination.account_number.state == "ambiguous"
    assert p.candidates[0].remittance.model.state == "unreadable"
    assert p.candidates[0].amount.currency.state == "ambiguous"
    assert p.review.state == "needs_review"


def test_ocr_explicit_separate_currency_and_multiple_scheme_review():
    p, e, _ = extract_rules(UK.replace("GBP ", "") + "Currency: GBP", "image", "ocr")
    assert review_payment(p, e).review.state == "ready_for_review"
    p, e, _ = extract_rules(UK + "IBAN: GB82WEST12345698765432", "image", "ocr")
    assert len(p.candidates) == 2
    assert all(c.amount.value.value is None for c in p.candidates)
    assert review_payment(p, e).review.state == "needs_review"


def test_markdown_labels_never_strip_reference_characters():
    text = UK.replace("Sort code:", "**Sort code:**").replace(
        "Payment reference: PAY-007", "| **Payment reference** | PAY-007* |"
    )
    p, e, _ = extract_rules(text, "image", "ocr")
    assert p.candidates[0].remittance.reference.value == "PAY-007*"
    assert review_payment(p, e).review.state == "ready_for_review"


def test_explicit_account_country_conflict_is_reviewed(uk):
    p = uk.runs[0].payment
    p.candidates[0].account_country = Observation(
        value="HR", raw_text="HR", state="observed", evidence_ids=["e8"]
    )
    assert review_payment(p, uk.runs[0].evidence).review.state == "needs_review"


def test_documented_provider_limits_reject_before_dispatch(png):
    class Sized:
        def __init__(self, size):
            self.size = size

        def __len__(self):
            return self.size

    image = prepare_image(png, Hints())
    for provider, size in (("mistral", 20_000_001), ("openai", 384_000_001)):
        with pytest.raises(ServiceError) as error:
            validate_limits(replace(image, canonical=Sized(size)), [definition(provider)])
        assert error.value.status == 413


def test_hints_are_recorded_but_never_observations(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        result = finish(
            client, upload(client, png, hints={"language": "hr-HR", "issuer_country": "HR"})
        )
        assert result["input"]["hints"]["issuer_country"] == "HR"
        assert result["runs"][0]["payment"]["document_context"]["issuer_country"]["value"] is None
    with pytest.raises(ValidationError):
        Hints(issuer_country="ZZ")


@pytest.mark.parametrize("provider", ["openai", "mistral"])
@pytest.mark.parametrize("kind", ["different_model", "invalid_model", "no_usage"])
def test_provider_unknown_metadata_is_safe(settings, png, uk, provider, kind):
    body = openai_response(uk) if provider == "openai" else mistral_response()
    if kind == "no_usage":
        body.pop("usage" if provider == "openai" else "usage_info")
    else:
        body["model"] = (
            "different-model" if kind == "different_model" else {"secret": "not-a-model"}
        )
    settings.openai_key = SecretStr("test")
    adapter = (OpenAIAdapter if provider == "openai" else MistralAdapter)(
        settings, httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    )
    with client_for(settings, {provider: definition(provider)}, {provider: adapter}) as client:
        result = finish(client, upload(client, png, profiles=[provider]))
        run = result["runs"][0]
        if kind == "no_usage":
            assert run["state"] == "completed"
        else:
            assert run["error"]["code"] == "invalid_provider_output"
        assert run["diagnostics"]["stages"][0]["cost"]["status"] == "unknown"
