"""Regional routing works without a backend account-approval attestation."""

import json

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from backend.adapters.extended import ExtendedAdapter
from backend.config import ModelOption, ProfileConfig, ProviderConfig
from backend.profiles import registry
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_extended import llm_response
from backend.tests.test_providers import mistral_response, openai_response


def configured_option(settings, provider, host, operation):
    settings.openai_key = settings.mistral_key = SecretStr("synthetic-key")
    settings.providers.options["regional-test"] = ModelOption(
        provider=provider,
        model="synthetic",
        operation=operation,
        config=ProviderConfig(
            enabled=True,
            endpoint_host=host,
            configured_region="unknown",
            verified_processing_region=None,
            account_access_checked_at="2026-10-12",
            data_terms_checked_at="2026-10-12",
            data_terms_note="Synthetic fixture; no regional approval claimed.",
        ),
    )
    settings.providers = ProfileConfig.model_validate(settings.providers.model_dump())
    return registry(settings)["regional-test"]


@pytest.mark.parametrize(
    "provider,host,operation",
    [
        ("openai", "api.openai.com", "vision"),
        ("openai", "eu.api.openai.com", "vision"),
        ("openai", "us.api.openai.com", "vision"),
        ("mistral", "api.mistral.ai", "vision"),
        ("mistral", "api.eu.mistral.ai", "vision"),
        ("mistral", "api.eu.mistral.ai", "ocr"),
    ],
)
def test_endpoint_routes_without_verified_region_or_approval(
    settings, png, uk, provider, host, operation
):
    definition = configured_option(settings, provider, host, operation)
    assert definition.metadata.configured
    assert definition.metadata.unavailable_reason is None
    calls = []

    def handler(request):
        calls.append(request)
        assert request.url.host == host
        body = json.loads(request.content)
        assert body["model"] == "synthetic"
        if operation == "ocr":
            response = mistral_response()
        elif provider == "openai":
            assert body["store"] is False
            response = openai_response(uk)
        else:
            text = openai_response(uk)["output"][0]["content"][0]["text"]
            response = llm_response(provider, text, "synthetic")
        response["model"] = "synthetic"
        return httpx.Response(200, json=response)

    with client_for(
        settings,
        {"regional-test": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        catalogue = client.get("/v1/profiles").json()["profiles"][0]
        assert catalogue["configured"]
        assert (
            client.put(
                "/v1/admin/selection",
                json={"id": definition.metadata.id, "version": definition.metadata.version},
            ).status_code
            == 200
        )
        run = finish(client, upload(client, png, profiles=["regional-test"]))["runs"][0]
        assert run["state"] == "completed", run["error"]
        stage = run["diagnostics"]["stages"][0]
        assert stage["endpoint_host"] == host
        assert stage["verified_processing_region"] is None
    assert len(calls) == 1


def test_european_provider_rejection_is_reported_without_global_fallback(settings, png):
    definition = configured_option(settings, "openai", "eu.api.openai.com", "vision")
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(403, json={"message": "Synthetic account restriction"})

    with client_for(
        settings,
        {"regional-test": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["regional-test"]))["runs"][0]
        assert run["error"]["code"] == "provider_auth"
    assert len(calls) == 1
    assert calls[0].url.host == "eu.api.openai.com"


def test_mistral_starter_accepts_regional_endpoint_without_approval():
    config = ProfileConfig(mistral=ProviderConfig(endpoint_host="api.eu.mistral.ai"))
    assert config.mistral.verified_processing_region is None


@pytest.mark.parametrize(
    "provider,host",
    [
        ("openai", "eu.api.openai.com.attacker.invalid"),
        ("mistral", "api.eu.mistral.ai.attacker.invalid"),
        ("openai", "api.eu.mistral.ai"),
    ],
)
def test_regional_support_preserves_provider_destination_validation(provider, host):
    with pytest.raises(ValidationError, match="Unsupported provider endpoint"):
        ModelOption(
            provider=provider,
            model="synthetic",
            operation="vision",
            config=ProviderConfig(endpoint_host=host),
        )
