import json
from decimal import Decimal

import httpx
import pytest

from backend.adapters.extended import ExtendedAdapter
from backend.config import ModelOption
from backend.profiles import registry
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_providers import openai_response


def configured(settings, provider, operation="vision"):
    model = {
        "anthropic": "claude-haiku-4-5-20251001",
        "gemini": "gemini-3.5-flash-lite",
        "xai": "grok-4.7",
        "together": "Qwen/Qwen3-VL-8B-Instruct",
        "mistral": "mistral-small-2603",
        "mindee": "invoice",
    }.get(provider, "synthetic")
    model = model.replace("@", "-")
    opt = ModelOption(provider=provider, model=model, operation=operation)
    opt.config.enabled = True
    opt.config.max_call_eur = Decimal("1")
    settings.providers.options["test-profile"] = opt
    d = registry(settings)["test-profile"]
    d.metadata.configured = True
    return d


def llm_response(provider, text, model):
    if provider == "anthropic":
        return {
            "model": model,
            "stop_reason": "end_turn",
            "content": [{"type": "text", "text": text}],
            "usage": {"input_tokens": 100, "output_tokens": 20},
        }
    if provider == "gemini":
        return {
            "modelVersion": model,
            "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": text}]}}],
            "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20},
        }
    return {
        "model": model,
        "choices": [{"finish_reason": "stop", "message": {"content": text}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20},
    }


@pytest.mark.parametrize("provider", ["anthropic", "gemini", "xai", "together", "mistral"])
def test_extended_vision_actual_protocol_and_evidence(settings, png, uk, provider):
    definition = configured(settings, provider)
    text = openai_response(uk)["output"][0]["content"][0]["text"]
    calls = []

    def handler(request):
        calls.append(request)
        body = json.loads(request.content)
        assert "tools" not in body or body["tools"] == []
        assert (
            "base64" in request.content.decode() or "inline_data" in body["contents"][0]["parts"][0]
        )
        return httpx.Response(200, json=llm_response(provider, text, definition.metadata.model))

    adapter = ExtendedAdapter(settings, transport=httpx.MockTransport(handler))
    with client_for(settings, {"test-profile": definition}, {"extended": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        run = result["runs"][0]
        assert run["state"] == "completed", run["error"]
        assert run["payment"]["review"]["user_confirmation_required"]
        assert run["evidence"][0]["grounding"] == "model_claim"
        assert run["diagnostics"]["stages"][0]["provider"] == provider
        assert len(calls) == 1


@pytest.mark.parametrize(
    "provider",
    ["anthropic", "gemini", "xai", "together", "mistral", "azure", "mindee"],
)
@pytest.mark.parametrize(
    "status,code", [(401, "provider_auth"), (429, "provider_quota"), (500, "provider_unavailable")]
)
def test_extended_failures_redacted_once(settings, png, provider, status, code):
    op = "invoice" if provider in {"azure", "mindee"} else "vision"
    definition = configured(settings, provider, op)
    settings.resources.update(MINDEE_MODEL_ID="synthetic")
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={"message": "PRIVATE CONTENT"})

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert result["runs"][0]["error"]["code"] == code
        assert "PRIVATE CONTENT" not in json.dumps(result)
        assert len(calls) == 1


@pytest.mark.parametrize(
    "provider",
    ["anthropic", "gemini", "xai", "together", "mistral", "openai"],
)
@pytest.mark.parametrize(
    "kind", ["malformed", "refusal", "truncated", "changed_model", "negative_usage", "tool"]
)
def test_vision_abstains_on_invalid_output(settings, png, uk, provider, kind):
    definition = configured(settings, provider)
    text = openai_response(uk)["output"][0]["content"][0]["text"]
    body = llm_response(provider, text, definition.metadata.model)
    if provider == "openai":
        body = openai_response(uk)
        body["model"] = definition.metadata.model
    if kind == "malformed":
        body = []
    elif kind == "changed_model":
        body["modelVersion" if provider == "gemini" else "model"] = "unrequested-model"
    elif kind == "negative_usage":
        body["usageMetadata" if provider == "gemini" else "usage"] = {"tokens": -1}
    elif provider == "anthropic":
        body["stop_reason"] = "refusal" if kind == "refusal" else "max_tokens"
    elif provider == "gemini":
        body["candidates"][0]["finishReason"] = "SAFETY" if kind == "refusal" else "MAX_TOKENS"
    elif provider == "openai":
        body["status"] = "incomplete"
    else:
        body["choices"][0]["finish_reason"] = "content_filter" if kind == "refusal" else "length"
    adapter = ExtendedAdapter(
        settings, httpx.MockTransport(lambda _: httpx.Response(200, json=body))
    )
    with client_for(settings, {"test-profile": definition}, {"extended": adapter}) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert result["runs"][0]["state"] == "failed"
        assert result["runs"][0]["error"]["code"] in {"invalid_provider_output", "provider_refusal"}


@pytest.mark.parametrize(
    "exception,code",
    [(httpx.ReadTimeout, "provider_timeout"), (httpx.ConnectError, "provider_unavailable")],
)
def test_extended_network_failure_is_single_attempt(settings, png, exception, code):
    definition = configured(settings, "anthropic")
    calls = []

    def handler(request):
        calls.append(request)
        raise exception("PRIVATE", request=request)

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert result["runs"][0]["error"]["code"] == code
        assert len(calls) == 1


@pytest.mark.parametrize(
    "provider,op,body",
    [
        (
            "azure",
            "invoice",
            {
                "status": "succeeded",
                "analyzeResult": {
                    "content": "synthetic",
                    "modelId": "synthetic",
                    "documents": [
                        {
                            "fields": {
                                "VendorName": {"content": "Synthetic supplier"},
                                "InvoiceTotal": {"content": "GBP 20.00"},
                                "PaymentDetails": {
                                    "valueArray": [
                                        {
                                            "valueObject": {
                                                "IBAN": {"content": "GB82 WEST 1234 5698 7654 32"}
                                            }
                                        }
                                    ]
                                },
                            }
                        }
                    ],
                },
            },
        ),
        (
            "google_documentai",
            "invoice",
            {
                "document": {
                    "text": "synthetic",
                    "entities": [
                        {"type": "total_amount", "mentionText": "EUR 20.00"},
                        {"type": "supplier_iban", "mentionText": "GB82 WEST 1234 5698 7654 32"},
                    ],
                }
            },
        ),
        (
            "aws",
            "invoice",
            {
                "ExpenseDocuments": [
                    {
                        "SummaryFields": [
                            {
                                "Type": {"Text": "TOTAL"},
                                "ValueDetection": {"Text": "20.00"},
                                "Currency": {"Code": "GBP"},
                            }
                        ]
                    }
                ]
            },
        ),
        (
            "mindee",
            "invoice",
            {
                "inference": {
                    "result": {
                        "fields": {
                            "total_amount": {"value": 20.0},
                            "supplier_name": {"value": "Synthetic supplier"},
                        }
                    }
                }
            },
        ),
        (
            "mistral",
            "ocr",
            {
                "model": "mistral-small-2603",
                "pages": [{"markdown": "Sort code: 00-11-22\n\nAccount number: 00123456"}],
                "usage_info": {"pages_processed": 1},
            },
        ),
        (
            "azure",
            "ocr",
            {
                "status": "succeeded",
                "analyzeResult": {
                    "content": "IBAN: GB82 WEST 1234 5698 7654 32",
                    "modelId": "synthetic",
                },
            },
        ),
        ("google_documentai", "ocr", {"document": {"text": "IBAN: GB82 WEST 1234 5698 7654 32"}}),
        (
            "aws",
            "ocr",
            {
                "Blocks": [
                    {"Id": "line-1", "BlockType": "LINE", "Text": "Sort code: 00-00-00"},
                    {"Id": "line-2", "BlockType": "LINE", "Text": "Account number: 00123456"},
                ]
            },
        ),
    ],
)
def test_document_protocol_mapping_and_immutable_poll_artifacts(
    settings, png, monkeypatch, provider, op, body
):
    from backend.adapters import cloud_auth

    monkeypatch.setattr(
        cloud_auth, "google_headers", lambda _: {"Authorization": "Bearer synthetic"}
    )
    monkeypatch.setattr(cloud_auth, "aws_headers", lambda *a: {"Authorization": "synthetic"})
    settings.resources.update(
        GOOGLE_CLOUD_PROJECT="test-project",
        GOOGLE_DOCUMENTAI_LOCATION="eu",
        GOOGLE_DOCUMENTAI_OCR_PROCESSOR_ID="ocr-test",
        GOOGLE_DOCUMENTAI_INVOICE_PROCESSOR_ID="invoice-test",
        AWS_PROFILE="test",
        AWS_REGION="eu-central-1",
        MINDEE_MODEL_ID="synthetic",
    )
    definition = configured(settings, provider, op)
    opt = settings.providers.options["test-profile"]
    if provider == "google_documentai":
        opt.config.endpoint_host = "eu-documentai.googleapis.com"
    if provider == "aws":
        opt.config.endpoint_host = "textract.eu-central-1.amazonaws.com"
    if provider == "azure":
        opt.config.endpoint_host = "test.cognitiveservices.azure.com"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    calls = []

    def handler(request):
        calls.append(request)
        if provider == "azure" and request.method == "POST":
            return httpx.Response(
                202,
                json={},
                headers={
                    "operation-location": f"https://{opt.config.endpoint_host}/documentintelligence/documentModels/synthetic/analyzeResults/test-id?api-version=2024-11-30"
                },
            )
        if provider == "mindee" and request.method == "POST":
            return httpx.Response(
                202,
                json={
                    "job": {
                        "status": "Processed",
                        "result_url": "https://api-v2.mindee.net/v2/inferences/synthetic",
                    }
                },
            )
        return httpx.Response(200, json=body)

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        run = result["runs"][0]
        assert run["state"] == "completed", run["error"]
        assert len(
            list((settings.data_dir / "jobs" / result["scan_id"]).glob("*.raw.json"))
        ) == len(calls)
        assert run["payment"]["review"]["user_confirmation_required"]
        assert all(c["beneficiary_name"]["value"] is None for c in run["payment"]["candidates"])
        with client.app.state.store.connection() as db:
            assert db.execute("SELECT count(*) FROM budget WHERE dispatched=1").fetchone()[0] == 1


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.invalid/v2/jobs/test",
        "http://api-v2.mindee.net/v2/jobs/test",
        "https://api-v2.mindee.net@evil.invalid/v2/jobs/test",
        "https://api-v2.mindee.net/v2/delete/test",
    ],
)
def test_poll_urls_cannot_change_recipient(url):
    from backend.adapters.extended import checked_url
    from backend.errors import ProviderError

    with pytest.raises(ProviderError):
        checked_url(url, "api-v2.mindee.net", r"/v2/jobs/[A-Za-z0-9-]+")


def test_anthropic_transport_moves_unsupported_constraints_to_descriptions():
    from backend.adapters.vision import vision_request

    opt = ModelOption(provider="anthropic", operation="vision", model="test", protocol_version="2")
    _, _, body = vision_request(opt, "synthetic", "key")
    schema = body["output_config"]["format"]["schema"]

    def check(node):
        if isinstance(node, dict):
            assert not {"maxItems", "minLength", "maxLength", "minimum", "maximum"} & node.keys()
            for v in node.values():
                check(v)
        elif isinstance(node, list):
            for v in node:
                check(v)

    check(schema)
    assert "maxItems" in json.dumps(schema)  # retained as prompt guidance


def test_gemini_explicit_prompt_json_mode_still_includes_full_schema():
    from backend.adapters.vision import vision_request

    opt = ModelOption(
        provider="gemini",
        operation="vision",
        model="test",
        schema_mode="prompt_json",
        protocol_version="2",
    )
    _, _, body = vision_request(opt, "synthetic", "key")
    assert "responseJsonSchema" not in body["generationConfig"]
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert "UKDestination" in body["systemInstruction"]["parts"][0]["text"]


def test_anthropic_prompt_json_is_explicit_and_keeps_local_validation(settings, png, uk):
    from backend.adapters.vision import vision_request

    definition = configured(settings, "anthropic")
    opt = settings.providers.options["test-profile"]
    opt.schema_mode = "prompt_json"
    opt.protocol_version = "2"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    _, _, body = vision_request(opt, "synthetic", "key")
    assert "output_config" not in body
    assert "UKDestination" in body["system"]
    parsed = json.loads(openai_response(uk)["output"][0]["content"][0]["text"])
    parsed["evidence"][0]["bbox"] = [0, 0, 100, 100]

    def handler(request):
        return httpx.Response(200, json=llm_response("anthropic", json.dumps(parsed), opt.model))

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert result["runs"][0]["error"]["code"] == "invalid_provider_output"


def test_together_thinking_selection_is_explicit_and_versioned(settings):
    from backend.adapters.vision import vision_request

    opt = ModelOption(provider="together", operation="vision", model="Qwen/Qwen3.5-9B")
    settings.providers.options["qwen"] = opt
    original = registry(settings)["qwen"].metadata.version
    assert "chat_template_kwargs" not in vision_request(opt, "synthetic", "key")[2]
    opt.reasoning = "none"
    assert registry(settings)["qwen"].metadata.version != original
    assert vision_request(opt, "synthetic", "key")[2]["chat_template_kwargs"] == {
        "enable_thinking": False
    }


async def test_azure_paced_polling_never_repeats_inference(settings, monkeypatch):
    from backend.adapters.documents import document_request

    events = []
    opt = ModelOption(
        provider="azure", operation="ocr", model="prebuilt-read", poll_interval_seconds=5
    )
    opt.config.endpoint_host = "test.cognitiveservices.azure.com"

    async def sleep(delay):
        events.append(("wait", delay))

    monkeypatch.setattr("backend.adapters.documents.asyncio.sleep", sleep)

    async def request(method, path, **kwargs):
        events.append((method, path))
        if method == "POST":
            return {}, httpx.Response(
                202,
                headers={
                    "operation-location": "https://test.cognitiveservices.azure.com/documentintelligence/documentModels/prebuilt-read/analyzeResults/test"
                },
            )
        return {"status": "succeeded"}, httpx.Response(200)

    await document_request(opt, settings, request, "synthetic", b"synthetic", "key")
    assert [e[0] for e in events] == ["POST", "wait", "GET"]
    assert events[1] == ("wait", 5)


@pytest.mark.parametrize(
    "protocol,wrapper,completed",
    [("2", "fence", False), ("3", "fence", True), ("3", "prose", False), ("3", "bad_box", False)],
)
def test_prompt_json_v3_removes_only_full_json_fence(
    settings, png, uk, protocol, wrapper, completed
):
    from backend.adapters.vision import vision_request

    configured(settings, "anthropic")
    opt = settings.providers.options["test-profile"]
    opt.protocol_version = protocol
    opt.schema_mode = "prompt_json"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    data = json.loads(openai_response(uk)["output"][0]["content"][0]["text"])
    if wrapper == "bad_box":
        data["evidence"][0]["bbox"] = [0, 0, 100, 100]
    content = "```json\n" + json.dumps(data) + "\n```"
    if wrapper == "prose":
        content = "Unrequested commentary\n" + content

    def handler(request):
        return httpx.Response(200, json=llm_response("anthropic", content, opt.model))

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert (result["runs"][0]["state"] == "completed") is completed
        raw = json.loads(
            next((settings.data_dir / "jobs" / result["scan_id"]).glob("*.raw.json")).read_text()
        )
        assert raw["body"]["content"][0]["text"] == content
    if protocol == "3":
        body = vision_request(opt, "synthetic", "key")[2]
        assert "Never use pixels" in body["system"]


def test_v3_schema_boxes_match_result_coordinate_bounds():
    from backend.adapters.vision import vision_request

    opt = ModelOption(
        provider="together", operation="vision", model="Qwen/Qwen3.5-9B", protocol_version="3"
    )
    body = vision_request(opt, "synthetic", "key")[2]
    schema = body["response_format"]["json_schema"]["schema"]
    box = next(
        v for v in schema["$defs"]["Claim"]["properties"]["bbox"]["anyOf"] if v["type"] == "array"
    )
    assert box["items"]["minimum"] == 0 and box["items"]["maximum"] == 1
    assert "x+width <=1" in body["messages"][0]["content"]
