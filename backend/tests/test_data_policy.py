"""Real policy gates over synthetic content and mocked HTTP; no vendor uploads."""

import json
import sqlite3
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from time import monotonic

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from backend import data_policy
from backend.adapters.extended import ExtendedAdapter
from backend.adapters.hybrid import HybridAdapter
from backend.config import DataApproval, HybridOption, ModelOption, ProfileConfig, ProviderConfig
from backend.errors import ProviderError, ServiceError
from backend.images import prepare_image
from backend.models import Hints, Options
from backend.profiles import registry, resolve
from backend.providers import MistralAdapter, OpenAIAdapter
from backend.runtime import Context, Runtime
from backend.store import Store, request_digest
from backend.tests.conftest import upload
from backend.tests.fakes import FixtureAdapter
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5
from backend.tests.test_providers import definition as starter_definition
from backend.tests.test_providers import mistral_response, openai_response

pytestmark = pytest.mark.data_policy


def approved_option(provider="openai", operation="vision", payloads=None):
    today = datetime.now(UTC).date()
    host = data_policy.EUROPEAN_ENDPOINTS[provider]
    approval = DataApproval(
        account_alias="synthetic-account",
        endpoint_host=host,
        model="synthetic",
        operation=operation,
        payload_classes=payloads or ["image"],
        no_training=True,
        image_processing_approved=True,
        checked_at=today,
        expires_at=today + timedelta(days=30),
        region_evidence=".local/synthetic-region.json",
        training_evidence=".local/synthetic-training.json",
        retention_note="Synthetic fixture, not a vendor agreement or approval.",
    )
    return ModelOption(
        provider=provider,
        operation=operation,
        model="synthetic",
        protocol_version="5" if operation == "vision" else "1",
        field_policy="partial_v1" if operation == "vision" else "strict",
        config=ProviderConfig(
            enabled=True,
            account_alias=approval.account_alias,
            endpoint_host=host,
            configured_region="eu",
            verified_processing_region="eea_switzerland",
            account_access_checked_at=str(today),
            data_terms_checked_at=str(today),
            data_terms_note="Synthetic offline fixture",
            pricing_checked_at=str(today),
            max_call_eur=Decimal(".10"),
            data_approval=approval,
        ),
    )


def configure(settings, option=None):
    settings.openai_key = settings.mistral_key = SecretStr("synthetic-key")
    settings.providers.options["policy-test"] = option or approved_option()
    settings.providers = ProfileConfig.model_validate(settings.providers.model_dump())
    return registry(settings)["policy-test"]


def counts(settings):
    with sqlite3.connect(settings.data_dir / "jobs.sqlite3") as db:
        return db.execute("SELECT COUNT(*), COALESCE(SUM(dispatched),0) FROM budget").fetchone()


def accept(store, definition, png):
    options = Options(mode="extract", profiles=[definition.metadata.id])
    return store.accept(
        "privacy-key",
        request_digest(png, options),
        prepare_image(png, Hints()),
        options,
        [definition],
        [],
    )[0]


@pytest.mark.parametrize(
    "provider,host",
    [
        ("openai", "api.openai.com"),
        ("openai", "us.api.openai.com"),
        ("mistral", "api.mistral.ai"),
        ("anthropic", "api.anthropic.com"),
        ("gemini", "generativelanguage.googleapis.com"),
        ("together", "api.together.ai"),
        ("xai", "api.x.ai"),
        ("aws", "textract.eu-central-1.amazonaws.com"),
        ("azure", "synthetic.cognitiveservices.azure.com"),
        ("mindee", "api-v2.mindee.net"),
    ],
)
def test_global_or_unimplemented_routes_block_even_with_operator_claim(provider, host):
    config = approved_option().config
    config.endpoint_host = host
    config.data_approval.endpoint_host = host
    assert data_policy.violations(provider, "synthetic", "vision", config, ["image"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("account_alias", "other"),
        ("endpoint_host", "api.openai.com"),
        ("model", "other-model"),
        ("operation", "ocr"),
        ("payload_classes", ["ocr_text"]),
        ("no_training", False),
        ("image_processing_approved", False),
        ("expires_at", datetime.now(UTC).date() - timedelta(days=1)),
        ("checked_at", datetime.now(UTC).date() + timedelta(days=1)),
    ],
)
def test_approval_must_match_actual_request_and_be_current(field, value):
    config = approved_option().config
    setattr(config.data_approval, field, value)
    assert data_policy.violations("openai", "synthetic", "vision", config, ["image"])


def test_missing_evidence_and_unverified_boundary_block():
    assert data_policy.violations("openai", "synthetic", "vision", None, ["image"])
    config = approved_option().config
    config.data_approval = None
    assert data_policy.violations("openai", "synthetic", "vision", config, ["image"])
    config = approved_option().config
    config.verified_processing_region = "unknown"
    assert data_policy.violations("openai", "synthetic", "vision", config, ["image"])
    with pytest.raises(ValidationError):
        DataApproval.model_validate(
            {**approved_option().config.data_approval.model_dump(), "expires_at": "2000-01-01"}
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://eu.api.openai.com/v1/responses",
        "https://api.openai.com/v1/responses",
        "https://eu.api.openai.com:443/v1/responses",
        "https://eu.api.openai.com.evil.invalid/v1/responses",
        "https://user@eu.api.openai.com/v1/responses",
        "https://eu.api.openai.com/v1/responses#x",
    ],
)
def test_actual_request_destination_is_checked(url):
    with pytest.raises(ProviderError, match="data_policy_blocked"):
        data_policy.require_destination(
            url, "openai", "synthetic", "vision", approved_option().config, ["image"]
        )


@pytest.mark.parametrize(
    "provider,operation",
    [
        ("openai", "vision"),
        ("mistral", "vision"),
        ("mistral", "ocr"),
        ("google_documentai", "ocr"),
        ("google_documentai", "invoice"),
    ],
)
def test_reviewed_supported_routes_pass(provider, operation):
    option = approved_option(provider, operation)
    assert not data_policy.violations(provider, option.model, operation, option.config, ["image"])
    data_policy.require_destination(
        f"https://{option.config.endpoint_host}/v1/test",
        provider,
        option.model,
        operation,
        option.config,
        ["image"],
    )


def test_unreviewed_profile_unavailable_and_api_rejects_before_reservation(settings, png):
    option = approved_option()
    option.config.data_approval = None
    definition = configure(settings, option)
    assert not definition.metadata.configured
    assert "no-training evidence" in definition.metadata.unavailable_reason
    adapter = FixtureAdapter()
    with client_for(
        settings, {definition.metadata.id: definition}, {"extended": adapter}
    ) as client:
        meta = next(
            p
            for p in client.get("/v1/profiles").json()["profiles"]
            if p["id"] == definition.metadata.id
        )
        assert not meta["configured"]
        response = upload(client, png, profiles=[definition.metadata.id])
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "data_policy_blocked"
        assert counts(settings) == (0, 0)
        assert adapter.calls == 0
    with pytest.raises(ServiceError):
        resolve(
            Options(mode="compare", profiles="all_enabled"),
            "image/png",
            {definition.metadata.id: definition},
        )


def test_expiry_rechecked_in_catalog_selection_and_store(settings, png):
    definition = configure(settings)
    definition.config.data_approval.expires_at = datetime.now(UTC).date() - timedelta(days=1)
    with client_for(
        settings, {definition.metadata.id: definition}, {"extended": FixtureAdapter()}
    ) as client:
        assert not client.get("/v1/profiles").json()["profiles"][0]["configured"]
        selection = client.put(
            "/v1/admin/selection",
            json={"id": definition.metadata.id, "version": definition.metadata.version},
        )
        assert selection.status_code == 422
        with pytest.raises(ServiceError, match="data_policy_blocked"):
            accept(client.app.state.store, definition, png)
        assert counts(settings) == (0, 0)


@pytest.mark.asyncio
async def test_queued_approval_revocation_blocks_before_adapter_and_releases_hold(settings, png):
    definition = configure(settings)
    store = Store(settings)
    try:
        scan = accept(store, definition, png)
        assert counts(settings) == (1, 0)
        definition.config.data_approval.no_training = False
        adapter = FixtureAdapter()
        await Runtime(store, settings, {"extended": adapter}).process(
            scan.scan_id, [definition], monotonic()
        )
        result = store.get(scan.scan_id)
        assert result.runs[0].error.code == "data_policy_blocked"
        assert not result.runs[0].diagnostics.stages
        assert adapter.calls == 0
        assert counts(settings) == (0, 0)
        # Same-key retries retrieve the immutable original, without creating work.
        assert accept(store, definition, png).model_dump() == result.model_dump()
        assert counts(settings) == (0, 0)
    finally:
        store.close()


def test_external_stage_checks_again_before_dispatch_marker(settings, png):
    definition = configure(settings)
    store = Store(settings)
    try:
        scan = accept(store, definition, png)
        definition.config.data_approval.no_training = False
        context = Context(store, scan, scan.runs[0], definition)
        with pytest.raises(ProviderError, match="data_policy_blocked"):
            context.stage("vision", external=True, payloads=["image"])
        assert counts(settings) == (1, 0)
        assert not scan.runs[0].diagnostics.stages
    finally:
        store.close()


def test_synthetic_fixture_cannot_dispatch_external_content(definitions):
    with pytest.raises(ProviderError, match="data_policy_blocked"):
        data_policy.require_definition(definitions["success"], ["image"])


def test_hybrid_requires_both_recipients_and_text_approval(settings):
    configure(settings)
    settings.providers.options = {
        "ocr": approved_option("mistral", "ocr"),
        "interpreter": approved_option(payloads=["ocr_text", "layout"]),
    }
    settings.providers.hybrids["hybrid"] = HybridOption(
        ocr_profile_id="ocr",
        interpreter_profile_id="interpreter",
        enabled=True,
    )
    hybrid = registry(settings)["hybrid"]
    assert hybrid.metadata.configured
    assert not data_policy.definition_violations(hybrid)
    for stage in hybrid.stages:
        before = stage.config.data_approval.no_training
        stage.config.data_approval.no_training = False
        assert data_policy.definition_violations(hybrid)
        stage.config.data_approval.no_training = before
    hybrid.stages[1].config.data_approval.payload_classes = ["image"]
    assert data_policy.definition_violations(hybrid)


def test_approval_changes_profile_version_but_legacy_config_serialization_is_unchanged(settings):
    definition = configure(settings)
    before = definition.metadata.version
    settings.providers.options[
        "policy-test"
    ].config.data_approval.training_evidence = ".local/new-review.json"
    assert registry(settings)["policy-test"].metadata.version != before
    assert "data_approval" not in ProviderConfig(endpoint_host="api.openai.com").model_dump()
    serialized = definition.snapshot()
    assert serialized["config"]["data_approval"]["no_training"] is True
    assert "synthetic-key" not in json.dumps(serialized)


def success_response():
    return {
        "model": "synthetic",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(example_v5())}],
            }
        ],
        "usage": {"input_tokens": 100, "output_tokens": 50},
    }


def test_approved_image_request_uses_europe_no_store_no_tools(settings, png):
    definition = configure(settings)
    requests = []

    def handler(request):
        requests.append(request)
        assert request.url.host == "eu.api.openai.com"
        body = json.loads(request.content)
        assert body["store"] is False
        assert body["tools"] == []
        return httpx.Response(
            200, json=success_response(), headers={"x-request-id": "synthetic-request"}
        )

    adapter = ExtendedAdapter(settings, httpx.MockTransport(handler))
    with client_for(
        settings, {definition.metadata.id: definition}, {"extended": adapter}
    ) as client:
        result = finish(client, upload(client, png, profiles=[definition.metadata.id]))
        assert result["state"] == "completed"
        stage = result["runs"][0]["diagnostics"]["stages"][0]
        assert stage["endpoint_host"] == "eu.api.openai.com"
        assert stage["verified_processing_region"] == "eea_switzerland"
        assert stage["request_id"] == "synthetic-request"
        assert counts(settings) == (1, 1)
    assert len(requests) == 1


@pytest.mark.parametrize("kind", ["redirect", "outage"])
def test_regional_failure_never_falls_back_or_retries(settings, png, kind):
    definition = configure(settings)
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            307 if kind == "redirect" else 503,
            json={},
            headers={"location": "https://api.openai.com/v1/responses"},
        )

    adapter = ExtendedAdapter(settings, httpx.MockTransport(handler))
    with client_for(
        settings, {definition.metadata.id: definition}, {"extended": adapter}
    ) as client:
        result = finish(client, upload(client, png, profiles=[definition.metadata.id]))
        assert result["state"] == "failed"
        assert counts(settings) == (1, 1)
    assert len(requests) == 1
    assert requests[0].url.host == "eu.api.openai.com"


@pytest.mark.asyncio
async def test_frozen_option_mismatch_blocked_before_transport(settings, png):
    definition = configure(settings)
    other = approved_option()
    other.model = other.config.data_approval.model = "other-model"
    definition = replace(
        definition, parameters={**definition.parameters, "option": other.snapshot_json()}
    )
    store = Store(settings)
    try:
        scan = accept(store, definition, png)

        def handler(request):
            pytest.fail("Mismatched snapshot must not reach transport")

        with pytest.raises(ProviderError, match="data_policy_blocked"):
            await ExtendedAdapter(settings, httpx.MockTransport(handler)).extract(
                Context(store, scan, scan.runs[0], definition)
            )
        assert counts(settings) == (1, 0)
    finally:
        store.close()


@pytest.mark.parametrize("revoke_second_stage", [False, True])
def test_hybrid_european_egress_and_mid_job_revocation(settings, png, revoke_second_stage):
    configure(settings)
    settings.providers.options = {
        "ocr": approved_option("mistral", "ocr"),
        "interpreter": approved_option(payloads=["ocr_text", "layout"]),
    }
    settings.providers.hybrids["hybrid"] = HybridOption(
        ocr_profile_id="ocr",
        interpreter_profile_id="interpreter",
        enabled=True,
    )
    definition = registry(settings)["hybrid"]
    calls = []

    def handler(request):
        calls.append(request)
        body = json.loads(request.content)
        if request.url.host == "api.eu.mistral.ai":
            assert "image_url" in body["document"]
            if revoke_second_stage:
                definition.stages[1].config.data_approval.no_training = False
            return httpx.Response(
                200, json={"model": "synthetic", "pages": [{"markdown": "Total due: GBP 1234.50"}]}
            )
        assert request.url.host == "eu.api.openai.com"
        assert "data:image" not in request.content.decode()
        assert body["store"] is False and body["tools"] == []
        return httpx.Response(200, json=success_response())

    adapter = HybridAdapter(settings, httpx.MockTransport(handler))
    with client_for(settings, {"hybrid": definition}, {"hybrid": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["hybrid"]))
        if revoke_second_stage:
            assert result["state"] == "failed"
            assert result["runs"][0]["error"]["code"] == "data_policy_blocked"
            assert counts(settings) == (1, 1)
            assert len(calls) == 1
        else:
            assert result["state"] == "completed", result["runs"][0]["error"]
            assert counts(settings) == (2, 2)
            assert len(calls) == 2
        stages = result["runs"][0]["diagnostics"]["stages"]
        assert all(s["verified_processing_region"] == "eea_switzerland" for s in stages)


@pytest.mark.parametrize("provider", ["openai", "mistral"])
@pytest.mark.parametrize("mismatch", [False, True])
def test_starter_adapters_check_actual_model_and_destination(settings, png, uk, provider, mismatch):
    original = starter_definition(provider)
    model = original.metadata.model or original.metadata.processor
    option = approved_option(provider, "vision" if provider == "openai" else "ocr")
    option.config.data_approval.model = "other-model" if mismatch else model
    metadata = original.metadata.model_copy(deep=True)
    if mismatch:
        if provider == "openai":
            metadata.model = "other-model"
        else:
            metadata.processor = "other-model"
    definition = replace(original, metadata=metadata, config=option.config)
    settings.openai_key = settings.mistral_key = SecretStr("synthetic-key")
    calls = []

    def handler(request):
        calls.append(request)
        assert request.url.host == data_policy.EUROPEAN_ENDPOINTS[provider]
        assert json.loads(request.content)["model"] == model
        return httpx.Response(
            200, json=openai_response(uk) if provider == "openai" else mistral_response()
        )

    adapter = (OpenAIAdapter if provider == "openai" else MistralAdapter)(
        settings, httpx.MockTransport(handler)
    )
    with client_for(settings, {definition.metadata.id: definition}, {provider: adapter}) as client:
        result = finish(client, upload(client, png, profiles=[definition.metadata.id]))
        if mismatch:
            assert result["state"] == "failed"
            assert result["runs"][0]["error"]["code"] == "data_policy_blocked"
            assert counts(settings) == (0, 0)
            assert not calls
            assert not result["runs"][0]["diagnostics"]["stages"]
        else:
            assert result["state"] == "completed", result["runs"][0]["error"]
            assert counts(settings) == (1, 1)
            assert len(calls) == 1
