import json
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import SecretStr, ValidationError

from backend.config import ProfileConfig, ProviderConfig, Settings
from backend.errors import ServiceError
from backend.models import Cost, Evidence, Observation, Options, Scan
from backend.profiles import registry, resolve


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d.update(state="failed"),
        lambda d: d.update(final_result_id="missing"),
        lambda d: d.update(mode="compare"),
        lambda d: d["resolved_profiles"][0].update(version="other"),
        lambda d: d["runs"].append(d["runs"][0]),
        lambda d: d["runs"][0]["evidence"][0].update(image_id="wrong"),
        lambda d: d.update(execution_kind="live"),
        lambda d: d["runs"][0]["evidence"].append(d["runs"][0]["evidence"][0]),
        lambda d: d["runs"][0]["evidence"][0].update(source_stage_id="unknown"),
        lambda d: d["runs"][0].update(payment=None),
        lambda d: d["runs"][0].update(error={"code": "x", "message": "x"}),
        lambda d: d["runs"][0]["payment"].update(selected_candidate_id="unknown"),
        lambda d: d["runs"][0]["payment"].update(selected_candidate_id=None),
        lambda d: d["runs"][0]["payment"]["candidates"][0]["amount"]["value"].update(value="1.2"),
        lambda d: d["runs"][0]["payment"]["candidates"][0]["amount"]["currency"].update(
            value="AAA"
        ),
        lambda d: d["runs"][0]["payment"]["candidates"][0]["amount"]["value"].update(value=1.25),
        lambda d: d["runs"][0]["payment"]["review"].update(user_confirmation_required=False),
    ],
)
def test_contract_negative_invariants(uk, change):
    data = uk.model_dump()
    change(data)
    with pytest.raises(ValidationError):
        Scan.model_validate(data)


@pytest.mark.parametrize(
    "box",
    [
        [0.9, 0.1, 0.2, 0.2],
        [0.1, 0.9, 0.2, 0.2],
        [-0.1, 0, 0.1, 0.1],
        [0, 0, 1],
        [0, 0, float("nan"), 1],
    ],
)
def test_invalid_evidence_geometry(box):
    with pytest.raises(ValidationError):
        Evidence(id="e", image_id="i", source_stage_id="s", bbox=box, grounding="model_claim")


def test_empty_values_and_known_cost_requirements():
    for value in ("", None):
        with pytest.raises(ValidationError):
            Observation(value=value, state="observed")
    for payload in ({"status": "estimated"}, {"status": "unknown", "amount": "1"}):
        with pytest.raises(ValidationError):
            Cost(**payload)


def test_generated_and_handoff_schemas_accept_synthetic_examples():
    root = Path(__file__).resolve().parents[2]
    for schema in (
        Scan.model_json_schema(),
        json.loads((root / "docs/examples/scan-result.schema.json").read_text()),
    ):
        Draft202012Validator.check_schema(schema)
        for cohort in ("uk", "hr"):
            Draft202012Validator(schema).validate(
                json.loads((root / f"docs/examples/{cohort}-extract.synthetic.json").read_text())
            )


def test_registry_configured_enabled_and_versions(settings):
    first = registry(settings)
    assert all(not d.metadata.configured and not d.metadata.enabled for d in first.values())
    assert all(d.metadata.unavailable_reason for d in first.values())
    config = ProviderConfig(
        enabled=True,
        endpoint_host="eu.api.openai.com",
        account_access_checked_at="2026-10-02",
        data_terms_checked_at="2026-10-02",
        data_terms_note="Synthetic configuration test",
    )
    settings.providers.openai = config
    settings.openai_key = SecretStr("local-fixture-key")
    current = registry(settings)
    d = current["openai-luna-vision"]
    assert d.metadata.configured and d.metadata.enabled
    assert d.metadata.version != first[d.metadata.id].metadata.version
    selected, excluded = resolve(
        Options(mode="compare", profiles="all_enabled"), "image/png", current
    )
    assert [d.metadata.id for d in selected] == ["openai-luna-vision"]
    assert [d.id for d in excluded] == ["mistral-ocr-rules"]
    assert "local-fixture-key" not in json.dumps(d.snapshot())
    assert "local-fixture-key" not in repr(settings)
    config.enabled = False
    assert registry(settings)[d.metadata.id].metadata.unavailable_reason == "Disabled by operator"


def test_resolver_invalid_and_mixed_profiles(settings, definitions):
    with pytest.raises(ServiceError):
        resolve(Options(mode="compare", profiles="all_enabled"), "image/png", registry(settings))
    definitions["success"].metadata.supported_image_types = ["image/jpeg"]
    with pytest.raises(ServiceError):
        resolve(Options(mode="extract", profiles=["success"]), "image/png", definitions)
    definitions["success"].metadata.supported_image_types = ["image/png"]
    definitions["failure"] = replace(definitions["failure"], synthetic=False)
    with pytest.raises(ServiceError):
        resolve(Options(mode="compare", profiles=["success", "failure"]), "image/png", definitions)
    with pytest.raises(ServiceError):
        resolve(Options(mode="extract", profiles=["not-known"]), "image/png", definitions)


def test_config_refuses_endpoints_and_bad_tokens():
    for provider in ("openai", "mistral"):
        with pytest.raises(ValidationError):
            ProfileConfig(**{provider: ProviderConfig(endpoint_host="attacker.invalid")})
    with pytest.raises(ValidationError):
        Settings(token=SecretStr("short"))


def test_env_config_without_network(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SCANPAY_TOKEN", "x" * 32)
    monkeypatch.setenv("SCANPAY_PROFILES_FILE", str(tmp_path / "missing.json"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings.from_env()
    assert not settings.providers.openai.enabled
    path = tmp_path / "providers.json"
    path.write_text(ProfileConfig().model_dump_json())
    monkeypatch.setenv("SCANPAY_PROFILES_FILE", str(path))
    assert Settings.from_env().providers == ProfileConfig()
