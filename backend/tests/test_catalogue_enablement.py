"""New recipient and opt-in charge accounting regressions; all inference is mocked."""

import json
from decimal import Decimal

import httpx
import pytest

from backend.adapters.extended import ExtendedAdapter, record_usage
from backend.adapters.vision import vision_text
from backend.config import ModelOption
from backend.errors import ProviderError
from backend.models import Stage
from backend.profiles import registry
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5
from backend.tests.test_extended import configured, llm_response


def test_xai_reported_ticks_include_reasoning_and_are_not_estimated_twice():
    option = ModelOption(
        provider="xai",
        model="grok-4.7",
        operation="vision",
        tariff={
            "accounting": "xai-ticks-v1",
            "checked_at": "2026-10-12",
            "unit": "tokens",
            "input_rate": "999",
            "output_rate": "999",
            "currency": "USD",
            "source": "https://example.com",
        },
    )
    s = Stage(id="s", method="vision", execution="external")
    record_usage(
        {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "completion_tokens_details": {"reasoning_tokens": 70},
                "cost_in_usd_ticks": 37756000,
            }
        },
        s,
        option,
    )
    assert s.cost.status == "reported" and s.cost.currency == "USD" and s.cost.amount == "0.0037756"
    assert s.usage["completion_tokens_details.reasoning_tokens"] == 70


@pytest.mark.parametrize("ticks", [None, 0, True, "123", -1])
def test_xai_missing_zero_and_malformed_reported_charge(ticks):
    option = ModelOption(
        provider="xai",
        model="grok-4.7",
        operation="vision",
        tariff={"accounting": "xai-ticks-v1", "checked_at": "2026-10-12"},
    )
    s = Stage(id="s", method="vision", execution="external")
    if ticks in [True, "123", -1] and type(ticks) is not int or ticks == -1:
        with pytest.raises(ProviderError):
            record_usage({"usage": {"cost_in_usd_ticks": ticks}}, s, option)
    else:
        record_usage({"usage": {} if ticks is None else {"cost_in_usd_ticks": ticks}}, s, option)
        assert s.cost.status == ("unknown" if ticks is None else "reported")
        if ticks == 0:
            assert Decimal(s.cost.amount) == 0


def test_cohere_prices_billed_units_and_preserves_total_usage_separately():
    option = ModelOption(
        provider="cohere",
        model="synthetic",
        operation="vision",
        tariff={
            "unit": "tokens",
            "input_rate": "1",
            "output_rate": "2",
            "currency": "USD",
            "source": "https://example.com",
            "checked_at": "2026-10-12",
        },
    )
    s = Stage(id="s", method="vision", execution="external")
    record_usage(
        {
            "usage": {
                "tokens": {"input_tokens": 9999, "output_tokens": 9999},
                "billed_units": {"input_tokens": 100, "output_tokens": 20},
            }
        },
        s,
        option,
    )
    assert s.cost.amount == "0.00014" and s.usage["tokens.input_tokens"] == 9999


def test_aya_prompt_json_transport_uses_full_typed_schema_and_one_request(settings, png):
    configured(settings, "cohere")
    option = settings.providers.options["test-profile"]
    option.schema_mode = "prompt_json"
    option.protocol_version = "5"
    option.max_output_tokens = 4000
    option.field_policy = "partial_v1"
    option.interpretation_policy = "draft_v4"
    definition = registry(settings)["test-profile"]
    definition.metadata.configured = True
    calls = []

    def handler(request):
        calls.append(request)
        body = json.loads(request.content)
        assert request.url.host == "api.cohere.com" and request.url.path == "/v2/chat"
        assert body["max_tokens"] == 4000 and "response_format" not in body and "tools" not in body
        assert "Return only JSON" in body["messages"][0]["content"]
        assert "$defs" in body["messages"][0]["content"]
        return httpx.Response(
            200,
            json=llm_response(
                "cohere",
                "```json\n" + json.dumps(example_v5()) + "\n```",
                definition.metadata.model,
            ),
        )

    with client_for(
        settings,
        {"test-profile": definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["test-profile"]))
        assert (
            result["runs"][0]["state"] == "completed"
            and result["runs"][0]["payment"]["review"]["user_confirmation_required"]
        )
        assert len(calls) == 1


@pytest.mark.parametrize("kind", ["tool", "part", "truncated", "refused"])
def test_cohere_rejects_unrequested_actions_and_incomplete_output(kind):
    body = llm_response("cohere", "{}", "synthetic")
    if kind == "tool":
        body["message"]["tool_calls"] = [{"name": "untrusted"}]
    elif kind == "part":
        body["message"]["content"].append({"type": "image", "url": "https://evil.example"})
    else:
        body["finish_reason"] = "ERROR_TOXIC" if kind == "refused" else "MAX_TOKENS"
    with pytest.raises(ProviderError):
        vision_text(body, "cohere")
