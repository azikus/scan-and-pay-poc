import json
import sqlite3
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from backend.adapters.hybrid import HybridAdapter
from backend.config import HybridOption, ModelOption, ProfileConfig
from backend.images import prepare_image
from backend.models import Hints, Options
from backend.profiles import registry, validate_limits
from backend.runtime import Context
from backend.store import Store, request_digest
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish
from backend.tests.test_compact import example_v5


def configured_hybrid(settings):
    settings.mistral_key = SecretStr("synthetic-key")
    settings.openai_key = SecretStr("synthetic-key")
    for name, provider, operation in [
        ("ocr-test", "mistral", "ocr"),
        ("llm-test", "openai", "vision"),
    ]:
        opt = ModelOption(
            provider=provider,
            operation=operation,
            model="synthetic",
            protocol_version="5" if operation == "vision" else "1",
            field_policy="partial_v1" if operation == "vision" else "strict",
            rules_version="3",
        )
        opt.config.enabled = True
        opt.config.max_call_eur = Decimal(".20") if operation == "ocr" else Decimal(".30")
        opt.config.account_access_checked_at = opt.config.data_terms_checked_at = (
            opt.config.pricing_checked_at
        ) = "2026-10-08"
        opt.config.data_terms_note = "Synthetic offline fixture"
        settings.providers.options[name] = opt
    settings.providers.hybrids["hybrid-test"] = HybridOption(
        ocr_profile_id="ocr-test", interpreter_profile_id="llm-test", enabled=True
    )
    settings.providers = ProfileConfig.model_validate(settings.providers.model_dump())
    return registry(settings)["hybrid-test"]


def response():
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


def ledger(settings):
    with sqlite3.connect(settings.data_dir / "jobs.sqlite3") as db:
        return db.execute("SELECT dispatched,hold_microeur FROM budget ORDER BY id").fetchall()


@pytest.mark.parametrize("policy", ["draft_v1", "draft_v3", "draft_v4"])
def test_hybrid_policy_comes_from_its_interpreter_not_last_option(settings, policy):
    configured_hybrid(settings)
    settings.providers.options["llm-test"].interpretation_policy = policy
    expected = registry(settings)["hybrid-test"].snapshot()
    settings.providers.options["unrelated"] = settings.providers.options["ocr-test"].model_copy(
        deep=True
    )
    actual = registry(settings)["hybrid-test"]
    assert actual.parameters["interpretation_policy"] == policy
    assert actual.snapshot() == expected


@pytest.mark.parametrize("policy", ["strict", "draft_v1", "draft_v2", "draft_v3", "draft_v4"])
def test_two_stages_two_holds_no_image_in_interpretation(settings, png, policy):
    definition = configured_hybrid(settings)
    original_version = definition.metadata.version
    settings.providers.options["llm-test"].interpretation_policy = policy
    definition = registry(settings)["hybrid-test"]
    assert (definition.metadata.version != original_version) == (policy != "strict")
    assert definition.parameters.get("interpretation_policy", "strict") == policy
    calls = []

    def handler(request):
        calls.append(request)
        body = json.loads(request.content)
        if request.url.host == "api.mistral.ai":
            assert "image_url" in body["document"]
            return httpx.Response(
                200, json={"model": "synthetic", "pages": [{"markdown": "Total due: GBP 1234.50"}]}
            )
        assert request.url.host == "api.openai.com"
        assert body["tools"] == [] and body["store"] is False
        assert ("Do not decode QR" in body["instructions"]) == (policy != "strict")
        assert len(body["input"][0]["content"]) == 1
        content = body["input"][0]["content"][0]
        assert content["type"] == "input_text"
        assert "data:image" not in request.content.decode()
        assert json.loads(content["text"])["text"] == "Total due: GBP 1234.50"
        assert ledger(settings) == [(1, 200000), (1, 300000)]
        return httpx.Response(200, json=response())

    adapter = HybridAdapter(settings, httpx.MockTransport(handler))
    with client_for(settings, {"hybrid-test": definition}, {"hybrid": adapter}) as client:
        submitted = upload(client, png, profiles=["hybrid-test"])
        result = finish(client, submitted)
        run = result["runs"][0]
        assert run["state"] == "completed", run["error"]
        stages = [s for s in run["diagnostics"]["stages"] if s["execution"] == "external"]
        assert len(run["diagnostics"]["stages"]) == 2
        assert [s["provider"] for s in stages] == ["mistral", "openai"]
        assert stages[1]["source_stage_ids"] == [stages[0]["id"]]
        assert stages[1]["payload_classes"] == ["ocr_text", "layout"]
        assert stages[1]["rendition"] is None
        assert stages[0]["requested_model"] == stages[1]["returned_model"] == "synthetic"
        assert run["diagnostics"]["timings_ms"]["provider"] == sum(s["duration_ms"] for s in stages)
        assert (
            run["diagnostics"]["timings_ms"]["total"]
            >= run["diagnostics"]["timings_ms"]["provider"]
        )
        assert all(e["grounding"] == "model_claim" for e in run["evidence"])
        assert upload(client, png, profiles=["hybrid-test"]).json()["scan_id"] == result["scan_id"]
        assert len(calls) == 2
        assert client.delete(f"/v1/scans/{result['scan_id']}").status_code == 204
        assert ledger(settings) == [(1, 200000), (1, 300000)]


@pytest.mark.parametrize("failure", ["first", "second", "empty", "timeout", "malformed"])
def test_partial_failure_preserves_artifacts_and_only_releases_unsent_stage(settings, png, failure):
    definition = configured_hybrid(settings)
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            if failure == "first":
                return httpx.Response(503, json={"private": "do not log"})
            return httpx.Response(
                200,
                json={
                    "model": "synthetic",
                    "pages": [{"markdown": "" if failure == "empty" else "Amount due: GBP 20.00"}],
                },
            )
        if failure == "timeout":
            raise httpx.ReadTimeout("private text")
        if failure == "malformed":
            return httpx.Response(200, json={"broken": True})
        return httpx.Response(503, json={"private": "do not log"})

    with client_for(
        settings,
        {"hybrid-test": definition},
        {"hybrid": HybridAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        result = finish(client, upload(client, png, profiles=["hybrid-test"]))
        run = result["runs"][0]
        assert run["state"] == "failed" and run["outcome"] == "error"
        assert "private text" not in json.dumps(result)
        assert run["payment"] is None  # No silent rules fallback.
        assert len(calls) == (1 if failure in {"first", "empty"} else 2)
        assert ledger(settings) == (
            [(1, 200000)] if len(calls) == 1 else [(1, 200000), (1, 300000)]
        )
        if failure != "first":
            assert list((settings.data_dir / "jobs" / result["scan_id"]).glob("*.document.json"))


def test_hybrid_dispatches_both_stages_above_legacy_limits(settings, png):
    definition = configured_hybrid(settings)
    settings.max_calls = 1
    settings.smoke_budget_eur = Decimal("0")
    calls = []

    def handler(request):
        calls.append(request.url.path)
        body = (
            {"model": "synthetic", "pages": [{"markdown": "Amount due: GBP 20.00"}]}
            if request.url.path == "/v1/ocr"
            else response()
        )
        return httpx.Response(200, json=body)

    with client_for(
        settings,
        {"hybrid-test": definition},
        {"hybrid": HybridAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["hybrid-test"]))["runs"][0]
        assert run["state"] == "completed", run["error"]
        assert calls == ["/v1/ocr", "/v1/responses"]
        assert ledger(settings) == [(1, 200000), (1, 300000)]


def test_restart_retains_dispatched_stage_and_cannot_dispatch_twice(settings, png):
    definition = configured_hybrid(settings)
    store = Store(settings)
    options = Options(mode="extract", profiles=["hybrid-test"])
    image = prepare_image(png, Hints())
    scan, _ = store.accept("key", request_digest(png, options), image, options, [definition], [])
    scan.state = scan.runs[0].state = "running"
    store.save(scan)
    ctx = Context(store, scan, scan.runs[0], definition.stages[0], 0)
    ctx.stage("ocr", external=True, payloads=["image"])
    with pytest.raises(RuntimeError):
        store.mark_dispatched(scan.runs[0].id, 0, "second-attempt")
    with pytest.raises(RuntimeError):
        store.mark_dispatched(scan.runs[0].id, 4, "unreserved")
    store.recover()
    assert ledger(settings) == [(1, 200000)]
    assert store.get(scan.scan_id).state == "interrupted"
    store.close()


def test_hybrid_version_and_constraints(settings, png):
    definition = configured_hybrid(settings)
    assert definition.metadata.configured
    assert definition.reservations == (Decimal(".20"), Decimal(".30"))
    assert len(definition.snapshot()["stages"]) == 2
    validate_limits(prepare_image(png, Hints()), [definition])
    before = {k: v.metadata.version for k, v in registry(settings).items()}
    settings.providers.options["llm-test"].max_output_tokens = 4096
    after = registry(settings)
    assert before["hybrid-test"] != after["hybrid-test"].metadata.version
    assert before["ocr-test"] == after["ocr-test"].metadata.version
    data = settings.providers.model_dump()
    for change in [dict(ocr_profile_id="missing"), dict(interpreter_profile_id="ocr-test")]:
        changed = json.loads(json.dumps(data, default=str))
        changed["hybrids"]["hybrid-test"].update(change)
        with pytest.raises(ValidationError):
            ProfileConfig.model_validate(changed)
    data["hybrids"]["ocr-test"] = data["hybrids"].pop("hybrid-test")
    with pytest.raises(ValidationError, match="distinct"):
        ProfileConfig.model_validate(data)


def test_each_stage_has_its_own_timeout_with_full_total_timing(settings, png):
    import asyncio

    definition = configured_hybrid(settings)
    settings.stage_timeout_seconds = 0.4

    async def handler(request):
        await asyncio.sleep(0.25)
        if request.url.host == "api.mistral.ai":
            return httpx.Response(
                200, json={"model": "synthetic", "pages": [{"markdown": "Amount due: GBP 20.00"}]}
            )
        return httpx.Response(200, json=response())

    with client_for(
        settings,
        {"hybrid-test": definition},
        {"hybrid": HybridAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["hybrid-test"]))["runs"][0]
        assert run["state"] == "completed"
        assert run["diagnostics"]["timings_ms"]["provider"] >= 500


def test_hybrid_keeps_partial_fields_from_interpreter(settings, png):
    definition = configured_hybrid(settings)
    from backend.tests.test_compact import reading

    data = example_v5()
    data["candidates"][0]["destination"]["account_number"] = reading("00123456", basis="unreadable")

    def handler(request):
        if request.url.host == "api.mistral.ai":
            return httpx.Response(
                200,
                json={"model": "synthetic", "pages": [{"markdown": "Account number: 00123456"}]},
            )
        body = response()
        body["output"][0]["content"][0]["text"] = json.dumps(data)
        return httpx.Response(200, json=body)

    with client_for(
        settings,
        {"hybrid-test": definition},
        {"hybrid": HybridAdapter(settings, httpx.MockTransport(handler))},
    ) as client:
        run = finish(client, upload(client, png, profiles=["hybrid-test"]))["runs"][0]
        assert run["outcome"] == "incomplete"
        assert run["payment"]["candidates"][0]["amount"]["value"]["value"] == "1234.50"
        assert run["payment"]["candidates"][0]["destination"]["account_number"]["value"] is None


@pytest.mark.parametrize("source", ["unknown", "second"])
def test_stage_provenance_cannot_reference_missing_or_future_stage(source):
    from backend.models import Diagnostics, Run, Stage

    with pytest.raises(ValidationError, match="earlier stage"):
        Run(
            id="r",
            profile_id="hybrid",
            profile_version="1",
            diagnostics=Diagnostics(
                stages=[
                    Stage(
                        id="first", method="ocr", execution="external", source_stage_ids=[source]
                    ),
                    Stage(id="second", method="interpretation", execution="external"),
                ]
            ),
        )
