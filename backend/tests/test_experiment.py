import copy
import json

import pytest

from backend.models import Cost, Error, Run, Stage, Timings
from evaluation.batch import new_batch, save
from evaluation.experiment import summarize


def matrix():
    manifest = {
        "inputs": [{"id": str(i), "group_id": "synthetic", "status": "prepared"} for i in range(4)]
    }
    return manifest, new_batch(manifest, {"test": "v1"}, "test-batch")


def test_empty_matrix_is_pending_not_zero_latency_or_error(tmp_path):
    manifest, batch = matrix()
    report = summarize(tmp_path, manifest, batch)
    p = report["profiles"]["test"]
    assert not report["accuracy_scored"]
    assert p["outcomes"] == {"pending": 4}
    assert p["complete_for_review_fraction"] is None
    assert p["timeout_rate"] is None
    assert p["timings_ms"]["total"]["n"] == 0
    assert p["timings_ms"]["total"]["p50_ms"] is None
    assert report["costs"][0]["cash_billed"] is None


def test_all_hybrid_stages_failure_timings_and_unknown_cost_are_accounted(tmp_path, uk):
    manifest, batch = matrix()
    run = uk.runs[0].model_copy(deep=True)
    run.profile_id, run.profile_version = "test", "v1"
    # Keep existing synthetic evidence stage, then add independent external stages.
    run.diagnostics.stages.extend(
        [
            Stage(
                id="ocr",
                method="ocr",
                execution="external",
                provider="mistral",
                requested_model="ocr-model",
                returned_model="ocr-returned",
                duration_ms=10,
                cost=Cost(status="estimated", amount="0.004", currency="USD"),
            ),
            Stage(
                id="llm",
                method="interpretation",
                execution="external",
                provider="openai",
                requested_model="text-model",
                returned_model="text-returned",
                duration_ms=20,
                source_stage_ids=["ocr"],
            ),
        ]
    )
    run.diagnostics.timings_ms = Timings(
        total=35, provider=30, queue=2, preprocess=1, postprocess=2
    )
    # Non-provider historical synthetic stage should not contribute expense.
    run.diagnostics.stages[0].execution = "local"
    save(tmp_path / "success.json", {"runs": [run.model_dump(mode="json")]})
    failed = Run(
        id="failure",
        profile_id="test",
        profile_version="v1",
        state="failed",
        error=Error(code="provider_timeout", message="Synthetic timeout"),
    )
    failed.diagnostics.timings_ms = Timings(total=90000, provider=90000)
    save(tmp_path / "failed.json", {"runs": [failed.model_dump(mode="json")]})
    batch["rows"][0].update(state="succeeded", result_path="success.json")
    batch["rows"][1].update(state="failed", result_path="failed.json", reason="provider_timeout")
    batch["rows"][2].update(state="failed", reason="provider_auth")
    result = summarize(tmp_path, manifest, batch)
    p = result["profiles"]["test"]
    assert p["outcomes"] == {"success": 1, "error": 2, "pending": 1}
    assert p["timeout_count"] == 1 and p["timeout_denominator"] == 3
    assert p["complete_for_review_fraction"] == 1 / 3
    assert p["timings_ms"]["total"]["p95_ms"] == 90000
    assert p["timings_ms"]["total"]["n"] == 2
    assert len(p["external_stage_timings_ms"]) == 2
    costs = result["costs"][0]
    assert costs["unknown_stage_charges"] == 1
    assert costs["cost_per_dispatched_attempt"] is None
    assert costs["known_estimates_and_reported_by_currency"] == {"USD": "0.004"}
    assert [s["requested_model"] for s in costs["stages"]] == ["ocr-model", "text-model"]
    assert [s["returned_model"] for s in costs["stages"]] == ["ocr-returned", "text-returned"]


@pytest.mark.parametrize("change", ["missing_row", "hash", "version", "multiple_runs"])
def test_report_rejects_silent_subsets_or_wrong_profile(tmp_path, uk, change):
    manifest, batch = matrix()
    if change == "missing_row":
        batch["rows"].pop()
    elif change == "hash":
        batch["manifest_sha256"] = "wrong"
    else:
        run = uk.runs[0].model_dump(mode="json")
        result = {"runs": [run, copy.deepcopy(run)] if change == "multiple_runs" else [run]}
        (tmp_path / "result.json").write_text(json.dumps(result))
        batch["rows"][0].update(state="succeeded", result_path="result.json")
    with pytest.raises(ValueError):
        summarize(tmp_path, manifest, batch)
