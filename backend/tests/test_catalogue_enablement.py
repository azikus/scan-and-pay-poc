"""New recipient and opt-in charge accounting regressions; all inference is mocked."""

from decimal import Decimal

import pytest

from backend.adapters.extended import record_usage
from backend.config import ModelOption
from backend.errors import ProviderError
from backend.models import Stage


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
