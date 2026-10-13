import copy

import pytest

from backend.models import Observation
from evaluation.batch import new_batch, save
from evaluation.country_scores import (
    context_template,
    reviewed_route,
    score_countries,
    validate_context,
)
from evaluation.reviewed import score_batch


def example(tmp_path, uk):
    scan = uk.model_copy(deep=True)
    run = scan.runs[0]
    run.profile_id, run.profile_version = "test", "1"
    run.payment.document_context.issuer_country = Observation(value="GB", state="observed")
    candidate = run.payment.candidates[0]
    candidate.remittance.reference = Observation(value="WRONG", state="observed")
    manifest = {
        "inputs": [
            {
                "id": "image",
                "sha256": scan.input.original_sha256,
                "status": "prepared",
                "group_id": "synthetic",
            }
        ]
    }
    batch = new_batch(manifest, {"test": "1"}, "context-test")
    batch["rows"][0].update(state="succeeded", result_path="result.json")
    fields = [
        ("amount", candidate.amount.value.value, "readable"),
        ("reference", "CORRECT", "readable"),
        ("sort_code", candidate.destination.sort_code.value, "readable"),
        ("account_number", candidate.destination.account_number.value, "readable"),
        ("iban", None, "absent"),
        ("model", None, "absent"),
    ]
    key = {
        "version": "reviewed-fields@2",
        "manifest_sha256": batch["manifest_sha256"],
        "counts": {"readable": 4, "absent": 2},
        "documents": [
            {
                "input_id": "image",
                "image_sha256": scan.input.original_sha256,
                "fields": [
                    {
                        "path": "payment_options/option-1/" + name,
                        "expected": value,
                        "status": status,
                    }
                    for name, value, status in fields
                ],
            }
        ],
    }
    context = context_template(key)
    context["documents"][0].update(suggested_country="HR", suggestion_source="synthetic fixture")
    save(tmp_path / "result.json", scan.model_dump(mode="json"))
    return manifest, batch, key, context


def test_fixed_country_cohort_does_not_override_reviewed_route_or_errors(tmp_path, uk):
    m, b, k, c = example(tmp_path, uk)
    original = copy.deepcopy((k, c))
    report = score_countries(tmp_path, m, b, k, c)["profiles"]["test"]
    assert report["original_scores"] == score_batch(tmp_path, m, b, k)["profiles"]["test"]["scores"]
    cohort = report["by_country"]["suggested:HR"]
    assert cohort["denominator"] == 4 and cohort["counts"]["value_mismatch"] == 1
    assert report["by_reviewed_payment_scheme"]["uk_domestic"]["denominator"] == 4
    assert report["country_detection"] == {
        "counts": {},
        "reviewed_inputs": 0,
        "pending_inputs": 1,
        "fraction": None,
    }
    assert report["reviewed_absences_by_applicability"]["not_applicable"] == {"correct_absence": 1}
    assert (k, c) == original


def test_country_accuracy_requires_reviewed_key_not_model_agreement(tmp_path, uk):
    m, b, k, c = example(tmp_path, uk)
    label = c["documents"][0]
    label.update(status="reviewed", reviewer="Synthetic reviewer", country="HR")
    assert (
        score_countries(tmp_path, m, b, k, c)["profiles"]["test"]["country_detection"]["fraction"]
        == 0
    )
    label["country"] = "GB"
    r = score_countries(tmp_path, m, b, k, c)["profiles"]["test"]
    assert r["country_detection"]["fraction"] == 1
    assert "reviewed:GB" in r["by_country"]
    b["rows"][0].update(state="failed", result_path=None)
    r = score_countries(tmp_path, m, b, k, c)["profiles"]["test"]
    assert r["country_detection"]["counts"] == {"run_error": 1}
    assert r["by_country"]["reviewed:GB"]["accepted"] == 0


@pytest.mark.parametrize(
    "change",
    ["key", "missing_image", "hash", "status", "reviewer", "pending_value", "source", "country"],
)
def test_country_key_rejects_mismatches_and_unverified_truth(tmp_path, uk, change):
    _, _, k, c = example(tmp_path, uk)
    d = c["documents"][0]
    if change == "key":
        c["answer_key_sha256"] = "different"
    elif change == "missing_image":
        c["documents"] = []
    elif change == "hash":
        d["image_sha256"] = "wrong"
    elif change == "status":
        d["status"] = "accepted"
    elif change == "reviewer":
        d.update(status="reviewed", country="HR")
    elif change == "pending_value":
        d["country"] = "HR"
    elif change == "source":
        d["suggestion_source"] = None
    elif change == "country":
        d["suggested_country"] = "ZZ"
    with pytest.raises(ValueError):
        validate_context(k, c)


def test_result_image_binding_prevents_wrong_image_scoring(tmp_path, uk):
    m, b, k, c = example(tmp_path, uk)
    scan = uk.model_dump(mode="json")
    scan["runs"][0].update(profile_id="test", profile_version="1")
    scan["input"]["original_sha256"] = "wrong"
    save(tmp_path / "result.json", scan)
    with pytest.raises(ValueError, match="Saved result image"):
        score_countries(tmp_path, m, b, k, c)


@pytest.mark.parametrize(
    "names,route",
    [
        (["iban"], "iban"),
        (["sort_code", "account_number"], "uk_domestic"),
        (["account_number"], "unresolved"),
        (["reference"], "unresolved"),
        (["biller_code"], "biller_reference"),
        (["iban", "biller_code"], "unresolved"),
    ],
)
def test_reviewed_route_uses_positive_evidence_and_keeps_conflicts(names, route):
    fields = [{"path": "payment_options/one/" + name, "status": "readable"} for name in names]
    assert reviewed_route(fields) == route
