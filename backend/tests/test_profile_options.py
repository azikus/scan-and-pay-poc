from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.config import ModelOption, ProfileConfig
from backend.profiles import registry


def option(**changes):
    return ModelOption(
        provider="anthropic", model="claude-haiku-4-5-20251001", operation="vision", **changes
    )


def test_independent_options_do_not_enable_or_reprice_starters(settings):
    before = registry(settings)
    settings.providers.options = {"haiku": option()}
    after = registry(settings)
    assert after["openai-luna-vision"].snapshot() == before["openai-luna-vision"].snapshot()
    assert not after["haiku"].metadata.enabled
    assert not after["haiku"].metadata.configured
    assert after["haiku"].metadata.model == "claude-haiku-4-5-20251001"
    assert after["haiku"].ceiling_eur == Decimal("0")
    settings.providers.options["haiku"].model = "claude-sonnet-5-5"
    assert registry(settings)["haiku"].metadata.version != after["haiku"].metadata.version


def test_reserved_ids_and_incompatible_methods_rejected():
    with pytest.raises(ValidationError):
        ProfileConfig(options={"openai-luna-vision": option()})
    with pytest.raises(ValidationError):
        ModelOption(provider="anthropic", operation="invoice", model="synthetic")
    with pytest.raises(ValidationError):
        ModelOption(provider="xai", operation="vision", model="../../arbitrary")


def test_empty_secret_and_missing_resources_are_unconfigured(settings):
    from pydantic import SecretStr

    settings.provider_keys["anthropic"] = SecretStr("")
    settings.providers.options["haiku"] = option()
    assert "local API key" in registry(settings)["haiku"].metadata.unavailable_reason
    settings.providers.options["cloud"] = ModelOption(
        provider="google_documentai", operation="ocr", model="processor-v1"
    )
    assert (
        "GOOGLE_DOCUMENTAI_OCR_PROCESSOR_ID"
        in registry(settings)["cloud"].metadata.unavailable_reason
    )


def test_resource_changes_version_without_exposing_identifier(settings):
    settings.providers.options["cloud"] = ModelOption(
        provider="google_documentai", operation="ocr", model="processor-v1"
    )
    first = registry(settings)["cloud"]
    settings.resources["GOOGLE_DOCUMENTAI_OCR_PROCESSOR_ID"] = "private-processor"
    second = registry(settings)["cloud"]
    assert first.metadata.version != second.metadata.version
    assert "private-processor" not in str(second.snapshot())


@pytest.mark.parametrize("provider,dimension", [("anthropic", 8001), ("aws", 10001)])
def test_extended_provider_dimensions_rejected_before_dispatch(settings, png, provider, dimension):
    from backend.errors import ServiceError
    from backend.images import prepare_image
    from backend.models import Hints
    from backend.profiles import validate_limits

    image = prepare_image(png, Hints())
    image.identity.width = dimension
    settings.providers.options["limit"] = ModelOption(
        provider=provider,
        operation="vision" if provider == "anthropic" else "ocr",
        model="synthetic",
    )
    with pytest.raises(ServiceError) as e:
        validate_limits(image, [registry(settings)["limit"]])
    assert e.value.error.code == "provider_input_limit"


def test_documented_budget_plan_preserves_defaults_and_project_limit(settings):
    from backend.config import BudgetPlan

    assert settings.max_calls == 12
    assert settings.smoke_budget_eur == Decimal("30")
    plan = BudgetPlan(
        reference=".local/bounded-plan.json", cumulative_call_cap=167, cumulative_hold_eur="29.05"
    )
    assert plan.cumulative_call_cap == 167
    with pytest.raises(ValidationError):
        BudgetPlan(reference="plan", cumulative_call_cap=2000, cumulative_hold_eur="501")
