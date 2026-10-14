import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.models import Observation, Options, Scan
from backend.review import review_payment

EXAMPLES = Path(__file__).resolve().parents[2] / "docs/examples"


@pytest.mark.parametrize("cohort", ["uk", "hr"])
def test_handoff_fixture_and_backend_review(cohort):
    data = json.loads((EXAMPLES / f"{cohort}-extract.synthetic.json").read_text())
    scan = Scan.model_validate(data)
    run = scan.runs[0]
    result = review_payment(run.payment, run.evidence)
    assert result.review.state == run.payment.review.state
    assert result.review.user_confirmation_required is True
    expanded = scan.model_dump(mode="json")
    for saved_run, expanded_run in zip(data["runs"], expanded["runs"], strict=True):
        for original, current in zip(
            saved_run["payment"]["candidates"], expanded_run["payment"]["candidates"], strict=True
        ):
            for field in ("option_label", "due_date", "payment_condition"):
                if field not in original:
                    assert current.pop(field) == Observation().model_dump(mode="json")
    assert expanded == data


@pytest.mark.parametrize("state", ["missing", "unreadable", "ambiguous", "unsupported"])
def test_null_states_cannot_carry_values(state):
    with pytest.raises(ValidationError):
        Observation(value="00123", state=state)


@pytest.mark.parametrize(
    "payload",
    [
        {"mode": "extract", "profiles": "all_enabled"},
        {"mode": "extract", "profiles": ["a", "b"]},
        {"mode": "compare", "profiles": []},
        {"mode": "compare", "profiles": ["a", "a"]},
        {"mode": "extract", "profiles": ["a"], "url": "https://example.com"},
        {"mode": "extract", "profiles": ["a"], "hints": {"currency": "GBP"}},
    ],
)
def test_invalid_options(payload):
    with pytest.raises(ValidationError):
        Options.model_validate(payload)
