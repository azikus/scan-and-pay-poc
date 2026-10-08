import copy

import pytest

from backend.models import Alternative, Amount, Candidate, Observation, Payment, UKDestination
from evaluation.repeatability import latency_summary, payment_fingerprint


def document():
    def candidate(ident, account, amount):
        return Candidate(
            id=ident,
            destination=UKDestination(account_number=Observation(value=account, state="observed")),
            amount=Amount(value=Observation(value=amount, state="observed")),
        )

    return Payment(
        candidates=[candidate("a", "00123456", "10.00"), candidate("b", "00987654", "20.00")]
    )


def test_identity_order_and_explanation_changes_do_not_change_payment():
    first = document()
    first.selected_candidate_id = "a"
    second = copy.deepcopy(first)
    second.candidates.reverse()
    second.candidates[1].id = "new-id"
    second.selected_candidate_id = "new-id"
    second.candidates[1].amount.value.evidence_ids = ["different-evidence-id"]
    second.candidates[1].amount.value.raw_text = "10,00"
    assert payment_fingerprint(first) == payment_fingerprint(second)


@pytest.mark.parametrize(
    "change", ["association", "digit", "selection", "uncertainty", "review", "duplicate"]
)
def test_real_payment_differences_remain_visible(change):
    first = document()
    second = copy.deepcopy(first)
    if change == "association":
        second.candidates[0].amount, second.candidates[1].amount = (
            second.candidates[1].amount,
            second.candidates[0].amount,
        )
    elif change == "digit":
        second.candidates[0].destination.account_number.value = "00123457"
    elif change == "selection":
        second.selected_candidate_id = "b"
    elif change == "uncertainty":
        second.candidates[0].amount.value.state = "inferred"
    elif change == "review":
        second.review.state = "needs_review"
    else:
        extra = copy.deepcopy(second.candidates[0])
        extra.id = "c"
        second.candidates.append(extra)
    assert payment_fingerprint(first) != payment_fingerprint(second)


def test_ambiguous_alternative_order_is_irrelevant_but_content_is_not():
    first = document()
    first.invoice_number = Observation(
        state="ambiguous",
        alternatives=[
            Alternative(value="001", reason="first"),
            Alternative(value="002", reason="second"),
        ],
    )
    second = copy.deepcopy(first)
    second.invoice_number.alternatives.reverse()
    second.invoice_number.raw_text = "002 | 001"
    assert payment_fingerprint(first) == payment_fingerprint(second)
    second.invoice_number.alternatives[0].value = "003"
    assert payment_fingerprint(first) != payment_fingerprint(second)
    second = copy.deepcopy(first)
    first.invoice_number.alternatives = []
    second.invoice_number.alternatives = []
    second.invoice_number.raw_text = "partial reading"
    assert payment_fingerprint(first) != payment_fingerprint(second)


def test_payment_only_ignores_description_but_preserves_linked_account_and_amount():
    first = document()
    second = copy.deepcopy(first)
    second.description = Observation(value="A different summary", state="observed")
    assert payment_fingerprint(first) != payment_fingerprint(second)
    assert payment_fingerprint(first, payment_only=True) == payment_fingerprint(
        second, payment_only=True
    )
    second.candidates[0].destination.account_number.value = "00123457"
    assert payment_fingerprint(first, payment_only=True) != payment_fingerprint(
        second, payment_only=True
    )


def test_latency_keeps_missing_and_tail_distinct():
    assert latency_summary([None]) == {"n": 0, "p50_ms": None, "p95_ms": None, "max_ms": None}
    assert latency_summary([None, 0, 10, 20, 90000]) == {
        "n": 4,
        "p50_ms": 15,
        "p95_ms": 90000,
        "max_ms": 90000,
    }
    assert latency_summary(range(1, 32))["p95_ms"] == 30


@pytest.mark.parametrize("bad", [-1, float("inf"), float("nan")])
def test_latency_rejects_invalid_measurement(bad):
    with pytest.raises(ValueError):
        latency_summary([bad])
