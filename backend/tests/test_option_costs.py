from backend.adapters.extended import record_usage
from backend.config import ModelOption
from backend.models import Stage


def stage():
    return Stage(
        id="stage",
        method="vision",
        execution="external",
        provider="gemini",
        endpoint_host="generativelanguage.googleapis.com",
        payload_classes=["image"],
    )


def test_token_cost_retains_reasoning_cache_and_does_not_double_count():
    option = ModelOption(
        provider="gemini",
        model="synthetic",
        operation="vision",
        tariff={
            "unit": "tokens",
            "input_rate": "0.1",
            "output_rate": "0.4",
            "currency": "USD",
            "source": "https://example.com/pricing",
            "checked_at": "2026-10-06",
        },
    )
    s = stage()
    record_usage(
        {
            "usageMetadata": {
                "promptTokenCount": 1000,
                "candidatesTokenCount": 200,
                "thoughtsTokenCount": 50,
                "cachedContentTokenCount": 100,
                "promptTokensDetails": [{"modality": "IMAGE", "tokenCount": 900}],
            }
        },
        s,
        option,
    )
    assert s.usage["thoughtsTokenCount"] == 50
    assert s.usage["promptTokensDetails.0.tokenCount"] == 900
    assert s.cost.amount == "0.0002"


def test_missing_usage_stays_unknown():
    s = stage()
    record_usage({}, s, ModelOption(provider="openai", model="synthetic", operation="vision"))
    assert s.cost.status == "unknown"
