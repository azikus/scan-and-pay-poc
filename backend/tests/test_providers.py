import json
from decimal import Decimal

import httpx
import pytest
from jsonschema import Draft202012Validator
from pydantic import SecretStr

from backend.config import ProviderConfig
from backend.profiles import Definition, Profile
from backend.providers import MistralAdapter, OpenAIAdapter, structured_schema
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_review import UK


def definition(provider):
    return Definition(
        Profile(
            id=provider,
            version="1",
            method=provider,
            component_ids=[provider + "@1"],
            enabled=True,
            configured=True,
            provider=provider,
            model="gpt-6-luna" if provider == "openai" else None,
            processor="mistral-ocr-4-1" if provider == "mistral" else None,
        ),
        adapter=provider,
        config=ProviderConfig(
            endpoint_host="api." + provider + ".com" if provider == "openai" else "api.mistral.ai"
        ),
        ceiling_eur=Decimal("1"),
    )


def openai_response(uk):
    payment = uk.runs[0].payment.model_dump(exclude={"review", "selected_candidate_id"})
    evidence = [e.model_dump(include={"id", "excerpt", "bbox"}) for e in uk.runs[0].evidence]
    return {
        "id": "resp_synthetic",
        "object": "response",
        "created_at": 1790899200,
        "status": "completed",
        "model": "gpt-6-luna",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "id": "msg_synthetic",
                "status": "completed",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps({"payment": payment, "evidence": evidence}),
                        "annotations": [],
                    }
                ],
            }
        ],
        "usage": {
            "input_tokens": 1000,
            "input_tokens_details": {"cached_tokens": 100, "cache_write_tokens": 0},
            "output_tokens": 500,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 1500,
        },
    }


def mistral_response():
    return {
        "model": "mistral-ocr-4-1",
        "pages": [
            {
                "index": 0,
                "markdown": UK,
                "dimensions": {"width": 20, "height": 30},
                "images": [],
                "hyperlinks": ["https://never-fetch.invalid"],
                "blocks": [],
            }
        ],
        "usage_info": {"pages_processed": 1},
    }


@pytest.mark.parametrize(
    "inputs,cached,written,expected",
    [
        (1000, 100, 600, "0.000356"),
        (1000, 0, 1000, "0.000375"),
        (300000, 100000, 100000, "0.047375"),
        (1000, 100, None, None),
    ],
)
def test_openai_cache_write_cost(settings, png, uk, inputs, cached, written, expected):
    settings.openai_key = SecretStr("sk-TEST-SECRET")
    body = openai_response(uk)
    body["usage"]["input_tokens"] = inputs
    body["usage"]["total_tokens"] = inputs + 500
    details = body["usage"]["input_tokens_details"] = {"cached_tokens": cached}
    if written is not None:
        details["cache_write_tokens"] = written
    adapter = OpenAIAdapter(settings, httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with client_for(settings, {"openai": definition("openai")}, {"openai": adapter}) as client:
        run = finish(client, upload(client, png, profiles=["openai"]))["runs"][0]
        assert run["state"] == "completed"
        stage = run["diagnostics"]["stages"][0]
        assert stage["usage"].get("cache_write_tokens") == written
        if expected is None:
            assert stage["cost"]["status"] == "unknown"
        else:
            assert Decimal(stage["cost"]["amount"]) == Decimal(expected)


@pytest.mark.parametrize("written", [-1, 901, "not-a-count", {}])
def test_openai_invalid_cache_write_usage(settings, png, uk, written):
    settings.openai_key = SecretStr("sk-TEST-SECRET")
    body = openai_response(uk)
    body["usage"]["input_tokens_details"]["cache_write_tokens"] = written
    adapter = OpenAIAdapter(settings, httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with client_for(settings, {"openai": definition("openai")}, {"openai": adapter}) as client:
        run = finish(client, upload(client, png, profiles=["openai"]))["runs"][0]
        assert run["error"]["code"] == "invalid_provider_output"
        assert run["diagnostics"]["stages"][0]["cost"]["status"] == "unknown"


@pytest.mark.parametrize(
    "amount,valid",
    [("1234.50", True), ("-12.00", True), ("1234,50", False), ("1,234.50", False), ("12", False)],
)
def test_vision_amount_schema_requires_contract_format(uk, amount, valid):
    body = json.loads(openai_response(uk)["output"][0]["content"][0]["text"])
    value = body["payment"]["candidates"][0]["amount"]["value"]
    value.update(value=amount, raw_text="1.234,50")
    errors = list(Draft202012Validator(structured_schema()).iter_errors(body))
    assert bool(errors) is not valid
    if errors:
        assert list(errors[0].path) == ["payment", "candidates", 0, "amount", "value", "value"]


@pytest.mark.parametrize("provider", ["openai", "mistral"])
def test_provider_success_shape_destinations_costs_and_no_tools(settings, png, uk, provider):
    calls = []

    def handler(request):
        body = json.loads(request.content)
        calls.append(body)
        assert request.url.host == ("api.openai.com" if provider == "openai" else "api.mistral.ai")
        if provider == "openai":
            assert body["tools"] == [] and body["tool_choice"] == "none" and body["store"] is False
            assert body["max_output_tokens"] == 12000
            assert body["service_tier"] == "default"
            assert body["input"][0]["content"][1]["image_url"].startswith("data:image/png;base64,")
        else:
            assert "document_annotation_format" not in body
            assert body["document"]["image_url"].startswith("data:image/png;base64,")
        return httpx.Response(
            200,
            json=openai_response(uk) if provider == "openai" else mistral_response(),
            headers={"x-request-id": "req_synthetic"},
        )

    settings.openai_key = SecretStr("sk-TEST-SECRET")
    settings.mistral_key = SecretStr("TEST-SECRET")
    adapter = (OpenAIAdapter if provider == "openai" else MistralAdapter)(
        settings, httpx.MockTransport(handler)
    )
    with client_for(settings, {provider: definition(provider)}, {provider: adapter}) as client:
        result = finish(client, upload(client, png, profiles=[provider]))
        assert result["state"] == "completed", result
        run = result["runs"][0]
        assert run["payment"]["review"]["state"] == "ready_for_review"
        assert run["diagnostics"]["stages"][0]["execution"] == "external"
        assert run["diagnostics"]["stages"][0]["cost"]["status"] == "estimated"
        assert run["diagnostics"]["stages"][0]["cost"]["currency"] == "USD"
        assert run["diagnostics"]["stages"][0]["verified_processing_region"] is None
        assert run["diagnostics"]["stages"][0]["payload_classes"] == ["image"]
        assert run["diagnostics"]["stages"][0]["request_id"] == "req_synthetic"
        assert "TEST-SECRET" not in json.dumps(result)
        assert all(
            e["grounding"] == ("model_claim" if provider == "openai" else "ocr_span")
            for e in run["evidence"]
        )
        assert len(run["diagnostics"]["stages"]) == (1 if provider == "openai" else 2)
        if provider == "mistral":
            assert run["diagnostics"]["stages"][1]["execution"] == "local"
        assert client.get("/v1/profiles").json()["profiles"][0]["live_validated"]
        assert len(calls) == 1
        assert len(list((settings.data_dir / "jobs" / result["scan_id"]).glob("*.raw.json"))) == 1
        with client.app.state.store.connection() as db:
            assert db.execute("SELECT hold_microeur,dispatched FROM budget").fetchone()[:] == (
                1_000_000,
                1,
            )


@pytest.mark.parametrize("provider", ["openai", "mistral"])
@pytest.mark.parametrize(
    "status,expected",
    [
        (401, "provider_auth"),
        (403, "provider_auth"),
        (429, "provider_quota"),
        (500, "provider_unavailable"),
        (400, "invalid_provider_output"),
        (302, "invalid_provider_output"),
    ],
)
def test_provider_http_error_single_attempt_redacted(settings, png, provider, status, expected):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"message": "SECRET banking values"}},
            headers={"x-request-id": "req_error", "Location": "https://never-follow.invalid"},
        )

    settings.openai_key = SecretStr("test")
    adapter = (OpenAIAdapter if provider == "openai" else MistralAdapter)(
        settings, httpx.MockTransport(handler)
    )
    with client_for(settings, {provider: definition(provider)}, {provider: adapter}) as client:
        result = finish(client, upload(client, png, profiles=[provider]))
        assert result["runs"][0]["error"]["code"] == expected, result
        assert "SECRET" not in json.dumps(result)
        assert len(calls) == 1
        raw_path = next((settings.data_dir / "jobs" / result["scan_id"]).glob("*.raw.json"))
        raw = json.loads(raw_path.read_text())
        assert raw["http_status"] == status
        assert "SECRET banking values" in json.dumps(raw["error_body"])
        assert raw_path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("provider", ["openai", "mistral"])
@pytest.mark.parametrize(
    "exception,expected",
    [(httpx.ReadTimeout, "provider_timeout"), (httpx.ConnectError, "provider_unavailable")],
)
def test_transport_errors(settings, png, provider, exception, expected):
    def handler(request):
        raise exception("SECRET", request=request)

    settings.openai_key = SecretStr("test")
    adapter = (OpenAIAdapter if provider == "openai" else MistralAdapter)(
        settings, httpx.MockTransport(handler)
    )
    with client_for(settings, {provider: definition(provider)}, {provider: adapter}) as client:
        result = finish(client, upload(client, png, profiles=[provider]))
        run = result["runs"][0]
        assert run["error"]["code"] == expected
        assert run["diagnostics"]["stages"][0]["cost"]["status"] == "unknown"


@pytest.mark.parametrize(
    "kind", ["refusal", "incomplete", "bad_json", "bad_evidence", "tool_call", "bad_shape"]
)
def test_openai_invalid_or_refusal_preserves_usage(settings, png, uk, kind):
    body = openai_response(uk)
    if kind == "refusal":
        body["output"][0]["content"] = [{"type": "refusal", "refusal": "private refusal"}]
    elif kind == "incomplete":
        body["status"] = "incomplete"
    elif kind == "bad_json":
        body["output"][0]["content"][0]["text"] = "{not valid}"
    elif kind == "bad_evidence":
        extracted = json.loads(body["output"][0]["content"][0]["text"])
        extracted["payment"]["candidates"][0]["amount"]["value"]["evidence_ids"] = ["invented"]
        body["output"][0]["content"][0]["text"] = json.dumps(extracted)
    elif kind == "tool_call":
        body["output"] = [
            {
                "type": "function_call",
                "id": "tool",
                "call_id": "call",
                "name": "fetch_url",
                "arguments": "{}",
                "status": "completed",
            }
        ]
    else:
        body["output"][0]["content"][0]["text"] = (
            '{"payment":{ "url":"https://never.invalid"}, "evidence":[]}'
        )
    settings.openai_key = SecretStr("test")
    adapter = OpenAIAdapter(
        settings, httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    )
    with client_for(settings, {"openai": definition("openai")}, {"openai": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["openai"]))
        run = result["runs"][0]
        assert run["state"] == "failed", result
        assert run["error"]["code"] == (
            "provider_refusal" if kind == "refusal" else "invalid_provider_output"
        )
        assert run["diagnostics"]["stages"][0]["usage"]["input_tokens"] == 1000


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"pages": []},
        {"pages": [{"markdown": 3}]},
        {"pages": [{"markdown": "a"}, {"markdown": "b"}]},
        [],
    ],
)
def test_mistral_invalid_output(settings, png, body):
    adapter = MistralAdapter(
        settings, httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    )
    with client_for(settings, {"mistral": definition("mistral")}, {"mistral": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["mistral"]))
        assert result["runs"][0]["error"]["code"] == "invalid_provider_output"


def test_strict_output_schema_has_no_unavailable_union_or_defaults():
    def inspect(node):
        if isinstance(node, dict):
            assert "oneOf" not in node and "default" not in node
            if "properties" in node:
                assert set(node["properties"]) == set(node["required"])
                assert node["additionalProperties"] is False
            for value in node.values():
                inspect(value)
        elif isinstance(node, list):
            for value in node:
                inspect(value)

    inspect(structured_schema())
