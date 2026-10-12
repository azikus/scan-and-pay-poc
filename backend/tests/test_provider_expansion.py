"""Offline compatibility and preservation checks; no live model performance claims."""

import copy
import json
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from backend.adapters.extended import ExtendedAdapter
from backend.adapters.vision import vision_request, vision_text
from backend.config import ModelOption, ProfileConfig
from backend.errors import ProviderError
from backend.profiles import registry
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5
from backend.tests.test_extended import llm_response

PRESETS = ProfileConfig.model_validate_json(
    (Path(__file__).resolve().parents[2] / "providers.expanded.example.json").read_text()
).options


def test_presets_are_inert_and_leave_existing_profile_versions_alone(settings):
    before = {key: value.snapshot() for key, value in registry(settings).items()}
    settings.providers.options.update(copy.deepcopy(PRESETS))
    definitions = registry(settings)
    assert {key: definitions[key].snapshot() for key in before} == before
    assert settings.providers.default_extract_profile_id is None
    for name in PRESETS:
        meta = definitions[name].metadata
        assert not meta.enabled and not meta.configured and not meta.live_validated
        assert definitions[name].ceiling_eur == 0
        assert "account_access_checked_at" in meta.unavailable_reason


@pytest.mark.parametrize("name", PRESETS)
def test_every_expanded_model_uses_one_dispatch_and_keeps_review(settings, png, name):
    option = copy.deepcopy(PRESETS[name])
    option.config.enabled = True
    option.config.max_call_eur = Decimal("1")
    for field in ("account_access_checked_at", "data_terms_checked_at", "pricing_checked_at"):
        setattr(option.config, field, "2026-10-12")
    option.config.data_terms_note = "Synthetic offline approval"
    if option.provider in {"openai", "mistral"}:
        setattr(settings, option.provider + "_key", SecretStr("offline-secret"))
    else:
        settings.provider_keys[option.provider] = SecretStr("offline-secret")
    settings.providers.options[name] = option
    definition = registry(settings)[name]
    assert definition.metadata.enabled and definition.metadata.configured
    calls = []
    payload = example_v5()
    if option.protocol_version == "6":
        # Native Gemini protocol uses nullable singleton value, not a values array.
        def singleton(value):
            if isinstance(value, dict):
                return {
                    ("value" if key == "values" else key): (child[0] if child else None)
                    if key == "values"
                    else singleton(child)
                    for key, child in value.items()
                }
            if isinstance(value, list):
                return [singleton(child) for child in value]
            return value

        payload = singleton(payload)
    text = json.dumps(payload)
    body = llm_response(option.provider, text, option.model)
    if option.provider == "openai":
        body = {
            "model": option.model,
            "status": "completed",
            "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
        }
    if option.reasoning == "adaptive":
        body["content"].insert(0, {"type": "thinking", "thinking": "Untrusted thought"})

    def handler(request):
        calls.append(request)
        assert request.url.host == option.config.endpoint_host
        sent = json.loads(request.content)
        assert (
            sent["model"] == option.model
            if option.provider != "gemini"
            else option.model in request.url.path
        )
        return httpx.Response(200, json=body)

    with client_for(
        settings,
        {name: definition},
        {"extended": ExtendedAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        selected = {"id": name, "version": definition.metadata.version}
        assert client.put("/v1/admin/selection", json=selected).status_code == 200
        assert not calls
        result = finish(client, upload(client, png, profiles=[name]))
        run = result["runs"][0]
        assert run["state"] == "completed", run["error"]
        assert run["payment"]["review"]["user_confirmation_required"]
        assert run["diagnostics"]["returned_model"] == option.model
        assert len(calls) == 1


@pytest.mark.parametrize(
    "content",
    [
        [{"type": "thinking", "thinking": "secret"}, {"type": "text", "text": "{}"}],
        [{"type": "redacted_thinking", "data": "secret"}, {"type": "text", "text": "{}"}],
    ],
)
def test_adaptive_thinking_requires_explicit_opt_in_and_is_never_parsed(content):
    body = {"stop_reason": "end_turn", "content": content, "model": "synthetic"}
    with pytest.raises(ProviderError):
        vision_text(body, "anthropic")
    assert vision_text(body, "anthropic", adaptive_thinking=True) == ("{}", "synthetic")
    body["content"].append({"type": "tool_use", "input": {}})
    with pytest.raises(ProviderError):
        vision_text(body, "anthropic", adaptive_thinking=True)


def test_reasoning_controls_and_snapshot_versions(settings):
    for provider, reasoning in [("anthropic", "low")]:
        with pytest.raises(ValidationError):
            ModelOption(
                provider=provider, model="synthetic", operation="vision", reasoning=reasoning
            )
    option = copy.deepcopy(PRESETS["anthropic-sonnet-expanded"])
    settings.providers.options["sonnet"] = option
    first = registry(settings)["sonnet"].metadata.version
    _, _, body = vision_request(option, "synthetic", "secret")
    assert body["thinking"] == {"type": "adaptive"}
    option.reasoning = None
    assert registry(settings)["sonnet"].metadata.version != first
    assert "thinking" not in vision_request(option, "synthetic", "secret")[2]


@pytest.mark.parametrize("provider", ["fireworks", "cohere"])
def test_removed_recipients_cannot_be_configured(provider):
    with pytest.raises(ValidationError, match="Unsupported provider operation"):
        ModelOption(provider=provider, model="synthetic", operation="vision")
