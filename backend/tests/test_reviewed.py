import copy
import hashlib
import json

import pytest

from evaluation.reviewed import (
    import_review,
    indexed,
    match_options,
    normalized,
    outcome,
    score_document,
)


def source_field(value, visibility="visible", **extra):
    return {"value": value, "visibility": visibility, **extra}


def review_fixture():
    labels = {
        "version": "synthetic@1",
        "documents": [
            {
                "input_id": "image",
                "image_sha256": "image-hash",
                "document_fields": {
                    "supplier_name": source_field("Example Supplier"),
                    "issue_date": source_field("2026-01-01"),
                },
                "payment_options": [
                    {
                        "id": "option-1",
                        "fields": {
                            "amount": source_field("10.00"),
                            "iban": source_field(None, "absent"),
                            "reference": source_field(None, "uncertain", readability_review=True),
                            "beneficiary_name": source_field(
                                "Example Supplier", user_verified=True
                            ),
                            "due_date": source_field("2026-02-01"),
                        },
                    }
                ],
                "additional_printed_fields": {"note": source_field("Text")},
            }
        ],
    }
    from evaluation.reviewed import label_fields

    raw = json.dumps(labels).encode()
    fields = []
    for path, f in label_fields(labels["documents"][0]).items():
        fields.append(
            {
                "field_path": path,
                "draft_value": f["value"],
                "draft_visibility": f["visibility"],
                "decision": "unreadable" if f.get("readability_review") else "confirmed",
                "value": f["value"],
            }
        )
    review = {
        "format": "scan-pay-human-review@1",
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "label_version": labels["version"],
        "reviewer": "Synthetic Reviewer",
        "documents": [{"input_id": "image", "image_sha256": "image-hash", "fields": fields}],
    }
    return raw, review, {"inputs": [{"id": "image", "sha256": "image-hash"}]}


def test_import_preserves_sources_prior_locks_and_explicit_exclusions():
    raw, review, manifest = review_fixture()
    before = copy.deepcopy(review)
    key = import_review(
        raw,
        review,
        manifest,
        {"image/payment_options/option-1/amount": "Conflicting reviewer note"},
    )
    assert review == before
    assert key["counts"] == {
        "readable": 3,
        "absent": 1,
        "unrepresented_or_free_text": 2,
        "disputed_semantics": 1,
        "unreadable": 1,
    }
    assert key["label_sha256"] == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize(
    "change",
    [
        "hash",
        "version",
        "format",
        "image",
        "missing_document",
        "duplicate_document",
        "missing_field",
        "duplicate_field",
        "draft_value",
        "draft_visibility",
        "unknown_decision",
        "blank_value",
        "nontext",
        "changed_confirmation",
        "unlock_unreadable",
        "unlock_confirmed",
        "absent_with_value",
    ],
)
def test_review_rejects_unbound_or_contradictory_data(change):
    raw, review, manifest = review_fixture()
    doc = review["documents"][0]
    f = doc["fields"][0]
    if change in {"hash", "version", "format"}:
        review[
            {"hash": "dataset_sha256", "version": "label_version", "format": "format"}[change]
        ] = "wrong"
    elif change == "image":
        doc["image_sha256"] = "wrong"
    elif change == "missing_document":
        review["documents"] = []
    elif change == "duplicate_document":
        review["documents"].append(copy.deepcopy(doc))
    elif change == "missing_field":
        doc["fields"].pop()
    elif change == "duplicate_field":
        doc["fields"].append(copy.deepcopy(f))
    elif change == "draft_value":
        f["draft_value"] = "changed"
    elif change == "draft_visibility":
        f["draft_visibility"] = "absent"
    elif change == "unknown_decision":
        f["decision"] = "approve-everything"
    elif change == "blank_value":
        f.update(decision="corrected", value=" ")
    elif change == "nontext":
        f.update(decision="corrected", value=123)
    elif change == "changed_confirmation":
        f["value"] = "Changed"
    elif change == "unlock_unreadable":
        next(x for x in doc["fields"] if x["field_path"].endswith("/reference")).update(
            decision="corrected", value="123"
        )
    elif change == "unlock_confirmed":
        next(x for x in doc["fields"] if x["field_path"].endswith("/beneficiary_name")).update(
            decision="corrected", value="Different"
        )
    elif change == "absent_with_value":
        f["decision"] = "not_visible"
    with pytest.raises(ValueError):
        import_review(raw, review, manifest)


@pytest.mark.parametrize(
    "decision,value,visibility,status",
    [
        ("pending", "Example Supplier", "visible", "pending"),
        ("unsure", "Example Supplier", "visible", "unsure"),
        ("corrected", None, "visible", "correction_without_value"),
        ("confirmed", "Example Supplier", "uncertain", "uncertain_source"),
        ("not_visible", None, "visible", "absent"),
        ("corrected", "Reviewed Supplier", "visible", "readable"),
    ],
)
def test_partial_review_only_scores_explicit_usable_decisions(decision, value, visibility, status):
    raw, review, manifest = review_fixture()
    labels = json.loads(raw)
    labels["documents"][0]["document_fields"]["supplier_name"]["visibility"] = visibility
    raw = json.dumps(labels).encode()
    review["dataset_sha256"] = hashlib.sha256(raw).hexdigest()
    review["documents"][0]["fields"][0].update(
        decision=decision, value=value, draft_visibility=visibility
    )
    assert import_review(raw, review, manifest)["documents"][0]["fields"][0]["status"] == status


def test_unknown_hold_is_rejected():
    with pytest.raises(ValueError):
        import_review(*review_fixture(), {"wrong": "do not score"})
    with pytest.raises(ValueError):
        indexed([{"id": "same"}, {"id": "same"}], "id")


def field(name, value, option="option-1", status="readable"):
    return {"path": f"payment_options/{option}/{name}", "expected": value, "status": status}


def obs(value, **kw):
    return {"value": value, "state": "observed", "origin": "document", **kw}


def candidate(ident, amount, reference, account):
    return {
        "id": ident,
        "amount": {"value": obs(amount), "currency": obs("EUR")},
        "remittance": {"reference": obs(reference)},
        "destination": {"kind": "uk_domestic", "account_number": obs(account)},
    }


def test_linked_assignment_handles_reordering_but_penalizes_crossed_amounts():
    fields = [
        field(k, v, option=f"option-{n}")
        for n, a, r, acct in [(1, "10", "ref-A", "00000001"), (2, "20", "ref-B", "00000002")]
        for k, v in [("amount", a), ("reference", r), ("account_number", acct)]
    ]
    candidates = [
        candidate("B", "20", "ref-B", "00000002"),
        candidate("A", "10", "ref-A", "00000001"),
    ]
    doc = {"input_id": "image", "fields": fields}
    result = score_document(doc, {"candidates": candidates})
    assert result["option_matches"] == {"option-1": "A", "option-2": "B"}
    assert result["counts"]["readable"] == {"exact_match": 6}
    candidates[0]["amount"]["value"]["value"] = "10"
    candidates[1]["amount"]["value"]["value"] = "20"
    assert score_document(doc, {"candidates": candidates})["counts"]["readable"] == {
        "value_mismatch": 2,
        "exact_match": 4,
    }


def test_same_candidate_cannot_satisfy_two_options_and_no_absence_credit_for_failure():
    fields = [field("amount", "10", option=o) for o in ["option-1", "option-2"]]
    fields += [
        field("iban", None, option="option-1", status="absent"),
        field("iban", None, option="option-2", status="absent"),
        field("reference", None, status="unreadable"),
    ]
    doc = {"input_id": "image", "fields": fields}
    result = score_document(
        doc,
        {
            "candidates": [
                candidate("A", "10", "ref", "00000001"),
                candidate("extra", "99", "other", "00000009"),
            ]
        },
    )
    assert result["counts"]["readable"] == {"exact_match": 1, "missing": 1}
    assert result["counts"]["absent"] == {"unmatched_option": 1, "correct_absence": 1}
    assert result["unmatched_candidate_ids"] == ["extra"]
    assert result["counts"]["excluded"] == {"unreadable": 1}
    assert score_document(doc, None)["counts"]["absent"] == {"run_error": 2}


@pytest.mark.parametrize(
    "name,left,right,equal",
    [
        ("amount", "10.00", "10", True),
        ("amount", "10,00", "10", False),
        ("amount", "NaN", "10", False),
        ("sort_code", "01-02-03", "010203", True),
        ("account_number", "00123456", "123456", False),
        ("reference", "AB 00102", "AB00102", True),
        ("reference", "AB001-02", "AB00102", False),
        ("beneficiary_name", "Example Ltd.", "EXAMPLE LTD", True),
        ("beneficiary_name", "Example Ltd", "Example Holdings Ltd", False),
        ("currency", " EUR ", "eur", True),
        ("iban", None, None, True),
    ],
)
def test_safe_normalization_preserves_digits_and_identity(name, left, right, equal):
    assert (normalized(name, left) == normalized(name, right)) == equal


@pytest.mark.parametrize(
    "status,actual,expected",
    [
        ("readable", obs("10"), "exact_match"),
        ("readable", obs("11"), "value_mismatch"),
        ("readable", {}, "missing"),
        ("readable", {"state": "unreadable"}, "uncertain_output"),
        ("readable", obs("10", state="inferred"), "unsupported_inference"),
        ("readable", obs("10", origin="barcode"), "unsupported_inference"),
        ("absent", {}, "correct_absence"),
        ("absent", obs("10"), "unexpected_value"),
        ("absent", {"state": "ambiguous"}, "uncertain_output"),
        ("absent", {"alternatives": [{"value": "10"}]}, "uncertain_output"),
    ],
)
def test_outcomes_keep_wrong_missing_inferred_absent_and_uncertain_separate(
    status, actual, expected
):
    assert (
        outcome(
            field("amount", "10" if status == "readable" else None, status=status), actual, True
        )
        == expected
    )


def test_document_and_typed_candidate_mapping_and_bounded_assignment():
    doc = {
        "input_id": "image",
        "fields": [
            {"path": "document_fields/supplier_name", "expected": "Example", "status": "readable"},
            field("beneficiary_name", "Example"),
            field("biller_scheme", "synthetic"),
            field("model", "00"),
            field("iban", None, status="absent"),
        ],
    }
    payment = {
        "supplier_name": obs("Example"),
        "candidates": [
            {
                "id": "one",
                "beneficiary_name": obs("Example"),
                "destination": {"scheme": obs("synthetic")},
                "remittance": {"model": obs("00")},
            }
        ],
    }
    result = score_document(doc, payment)
    assert result["counts"]["readable"] == {"exact_match": 4}
    assert result["counts"]["absent"] == {"correct_absence": 1}
    with pytest.raises(ValueError):
        match_options(doc["fields"], [{}] * 17)


@pytest.mark.parametrize(
    "value,order,result",
    [
        ("03/04/2023", "DMY", "exact_match"),
        ("03/04/2023", "MDY", "value_mismatch"),
        ("03/04/2023", None, "value_mismatch"),
        ("2023-04-03", None, "exact_match"),
        ("3 Apr 2023", None, "exact_match"),
        ("31/02/2023", "DMY", "value_mismatch"),
    ],
)
def test_date_format_requires_explicit_order_and_valid_calendar(value, order, result):
    f = field("due_date", "2023-04-03")
    f["date_order"] = order
    assert outcome(f, obs(value), True) == result


def test_reviewed_printed_date_is_accepted_without_locale_guess():
    f = field("due_date", "2026-01-05")
    f["printed_date_alias"] = "05 Gennaio 2026"
    assert outcome(f, obs("05 Gennaio 2026"), True) == "exact_match"


def test_batch_score_validates_full_matrix_and_excludes_zero_field_errors(tmp_path, uk):
    from evaluation.batch import new_batch, save
    from evaluation.reviewed import score_batch

    manifest = {
        "inputs": [{"id": "image", "sha256": "hash", "status": "prepared", "group_id": "synthetic"}]
    }
    batch = new_batch(manifest, {"test": "v1"}, "synthetic-score")
    key = {
        "version": "reviewed-fields@1",
        "manifest_sha256": batch["manifest_sha256"],
        "counts": {"readable": 1, "absent": 1},
        "documents": [
            {
                "input_id": "image",
                "image_sha256": "hash",
                "fields": [field("amount", "10"), field("iban", None, status="absent")],
            }
        ],
    }
    with pytest.raises(ValueError):
        score_batch(tmp_path, manifest, batch, key)
    run = uk.runs[0].model_copy(deep=True)
    run.profile_id, run.profile_version = "test", "v1"
    save(tmp_path / "result.json", {"runs": [run.model_dump(mode="json")]})
    batch["rows"][0].update(state="succeeded", result_path="result.json")
    report = score_batch(tmp_path, manifest, batch, key)
    assert report["profiles"]["test"]["scores"]["readable"]["denominator"] == 1
    altered = copy.deepcopy(key)
    altered["manifest_sha256"] = "wrong"
    with pytest.raises(ValueError):
        score_batch(tmp_path, manifest, batch, altered)
    altered = copy.deepcopy(key)
    altered["documents"][0]["image_sha256"] = "wrong"
    with pytest.raises(ValueError):
        score_batch(tmp_path, manifest, batch, altered)
    # Explicit failed cell is retained as an error, not rewarded for absent fields.
    batch["rows"][0].update(state="failed", result_path=None)
    report = score_batch(tmp_path, manifest, batch, key)
    assert report["profiles"]["test"]["scores"]["absent"]["counts"] == {"run_error": 1}


def test_empty_payment_is_run_error_even_in_historical_outcome_less_record(tmp_path):
    from backend.models import Payment, Run
    from evaluation.batch import new_batch, save
    from evaluation.reviewed import score_batch

    manifest = {
        "inputs": [{"id": "image", "sha256": "hash", "status": "prepared", "group_id": "synthetic"}]
    }
    batch = new_batch(manifest, {"test": "v1"}, "empty-payment")
    run = Run(
        id="empty", profile_id="test", profile_version="v1", state="completed", payment=Payment()
    )
    assert run.outcome is None and run.result_outcome == "error"
    save(tmp_path / "empty.json", {"runs": [run.model_dump(mode="json")]})
    batch["rows"][0].update(state="succeeded", result_path="empty.json")
    key = {
        "version": "reviewed-fields@1",
        "manifest_sha256": batch["manifest_sha256"],
        "counts": {"absent": 1},
        "documents": [
            {
                "input_id": "image",
                "image_sha256": "hash",
                "fields": [field("iban", None, status="absent")],
            }
        ],
    }
    assert score_batch(tmp_path, manifest, batch, key)["profiles"]["test"]["scores"]["absent"][
        "counts"
    ] == {"run_error": 1}


@pytest.mark.parametrize(
    "expected,variant",
    [("Example Energy Ltd", "Example Energy"), ("Énergie Exemple", "Energie Exemple")],
)
def test_reviewed_name_variant_is_accepted_but_keeps_visible_distinction(expected, variant):
    f = field("beneficiary_name", expected)
    assert outcome(f, obs(variant), True) == "value_mismatch"
    f["accepted_name_variants"] = [
        {"value": variant, "reviewer": "Human", "reason": "Same named entity confirmed"}
    ]
    assert outcome(f, obs(variant), True) == "accepted_name_variant"
    assert outcome(f, obs(expected), True) == "exact_match"
    assert outcome(f, obs(variant, state="inferred"), True) == "unsupported_inference"
    assert outcome(f, obs("Different Customer"), True) == "value_mismatch"
    result = score_document(
        {"input_id": "image", "fields": [f]},
        {"candidates": [{"id": "c", "beneficiary_name": obs(variant)}]},
    )
    assert result["option_matches"] == {"option-1": "c"}
    assert result["counts"]["readable"] == {"accepted_name_variant": 1}


@pytest.mark.parametrize("name", ["amount", "reference", "account_number"])
def test_name_variants_cannot_relax_numeric_payment_fields(name):
    f = field(name, "100")
    f["accepted_name_variants"] = [{"value": "101", "reviewer": "Human", "reason": "Not a name"}]
    assert outcome(f, obs("101"), True) == "value_mismatch"


def test_name_variant_needs_review_attribution():
    f = field("beneficiary_name", "Example Ltd")
    f["accepted_name_variants"] = [{"value": "Example"}]
    assert outcome(f, obs("Example"), True) == "value_mismatch"


def test_variant_batch_uses_new_key_version_and_counts_accepted_matches(tmp_path, uk):
    from evaluation.batch import new_batch, save
    from evaluation.reviewed import score_batch

    manifest = {
        "inputs": [{"id": "image", "sha256": "hash", "status": "prepared", "group_id": "synthetic"}]
    }
    batch = new_batch(manifest, {"test": "v1"}, "synthetic-variant")
    run = uk.runs[0].model_copy(deep=True)
    run.profile_id, run.profile_version = "test", "v1"
    name = run.payment.candidates[0].beneficiary_name.value
    f = field("beneficiary_name", name + " Limited")
    f["accepted_name_variants"] = [
        {"value": name, "reviewer": "Human", "reason": "Reviewed abbreviation"}
    ]
    key = {
        "version": "reviewed-fields@1",
        "manifest_sha256": batch["manifest_sha256"],
        "counts": {"readable": 1},
        "documents": [{"input_id": "image", "image_sha256": "hash", "fields": [f]}],
    }
    save(tmp_path / "result.json", {"runs": [run.model_dump(mode="json")]})
    batch["rows"][0].update(state="succeeded", result_path="result.json")
    with pytest.raises(ValueError, match="version 2"):
        score_batch(tmp_path, manifest, batch, key)
    key["version"] = "reviewed-fields@2"
    result = score_batch(tmp_path, manifest, batch, key)
    assert result["version"] == "reviewed-comparison@2"
    assert result["profiles"]["test"]["scores"]["readable"] == {
        "counts": {"accepted_name_variant": 1},
        "denominator": 1,
        "fraction": 1.0,
    }
