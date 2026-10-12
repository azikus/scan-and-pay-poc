import json

import pytest

from evaluation.corpus import inventory, prepare, validate_manifest


def test_manifest_accounts_for_every_image_and_failure(tmp_path, png):
    samples = tmp_path / "samples"
    samples.mkdir()
    for name in ("photo.png", "prepared-1.png", "prepared-2.png"):
        (samples / name).write_bytes(png)
    (samples / "broken.png").write_bytes(b"invalid")
    (samples / "provenance.json").write_text("{}")
    manifest = prepare(tmp_path, samples, tmp_path / ".local/corpus")
    assert len(manifest["sources"]) == 5
    assert len(manifest["inputs"]) == 4
    assert sum(i["status"] == "prepared" for i in manifest["inputs"]) == 3
    assert manifest["inputs"][0]["failure"] == "preparation_failed"
    validate_manifest(tmp_path, manifest)
    (samples / "extra.png").write_bytes(png)
    with pytest.raises(ValueError, match="inventory"):
        validate_manifest(tmp_path, manifest)


def test_manifest_detects_changed_bytes_and_duplicate_ids(tmp_path, png):
    (tmp_path / "samples").mkdir()
    (tmp_path / "samples/a.png").write_bytes(png)
    manifest = prepare(tmp_path, tmp_path / "samples", tmp_path / ".local/corpus")
    manifest["inputs"].append(dict(manifest["inputs"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        validate_manifest(tmp_path, manifest)
    manifest["inputs"].pop()
    (tmp_path / "samples/a.png").write_bytes(b"changed")
    with pytest.raises(ValueError, match="changed"):
        validate_manifest(tmp_path, manifest)


def test_inventory_includes_unsupported_inputs(tmp_path):
    (tmp_path / "x.heic").write_bytes(b"future sample")
    assert inventory(tmp_path)[0].name == "x.heic"


def test_batch_stops_with_every_input_retained_and_resumes_same_key(tmp_path, png, monkeypatch):
    import httpx

    from evaluation.batch import new_batch, run_batch, save

    samples = tmp_path / "samples"
    samples.mkdir()
    for name in ["a.png", "b.png", "c.png"]:
        (samples / name).write_bytes(png)
    manifest = prepare(tmp_path, samples, tmp_path / ".local/corpus")
    state_path = tmp_path / ".local/batch/state.json"
    save(state_path, new_batch(manifest, {"test": "version1"}, "batch1"))
    keys = []
    fail = True
    pauses = []
    monkeypatch.setattr("evaluation.batch.time.sleep", pauses.append)

    def handler(request):
        if request.url.path == "/v1/profiles":
            return httpx.Response(
                200,
                json={
                    "profiles": [
                        {"id": "test", "version": "version1", "configured": True, "enabled": True}
                    ]
                },
            )
        if request.method == "POST":
            keys.append(request.headers["Idempotency-Key"])
            if fail:
                raise httpx.ReadTimeout("ambiguous acceptance", request=request)
            return httpx.Response(202, json={"scan_id": "scan-" + keys[-1]})
        return httpx.Response(
            200,
            json={
                "state": "completed",
                "runs": [{"state": "completed", "profile_version": "version1", "error": None}],
            },
        )

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler)) as client:
        state = run_batch(
            tmp_path, manifest, state_path, client, poll_seconds=0, inter_input_seconds=2
        )
        assert [r["state"] for r in state["rows"]] == ["submission_unknown", "not_run", "not_run"]
        assert not state["complete"]
        fail = False
        state = run_batch(
            tmp_path, manifest, state_path, client, poll_seconds=0, inter_input_seconds=2
        )
        assert state["complete"]
        assert keys[0] == keys[1]
        assert len(keys) == 4
        assert pauses == [2, 2, 2]
        run_batch(tmp_path, manifest, state_path, client)
        assert len(keys) == 4


def test_cost_report_includes_failed_unknown_costs_and_never_scores(tmp_path):
    from evaluation.batch import save
    from evaluation.cost_report import summarize, write_report

    manifest = {
        "inputs": [{"id": "one", "group_id": "source"}, {"id": "two", "group_id": "source"}]
    }
    batch = {
        "batch_id": "test",
        "manifest_sha256": "test",
        "profiles": {"p": "v"},
        "rows": [
            {"input_id": "one", "profile_id": "p", "state": "failed", "result_path": "result.json"},
            {"input_id": "two", "profile_id": "p", "state": "not_run", "result_path": None},
        ],
    }
    save(
        tmp_path / "result.json",
        {
            "runs": [
                {
                    "id": "r",
                    "profile_id": "p",
                    "profile_version": "v",
                    "state": "failed",
                    "diagnostics": {
                        "requested_model": "test",
                        "returned_model": None,
                        "stages": [
                            {
                                "id": "stage",
                                "execution": "external",
                                "provider": "p",
                                "endpoint_host": "example.invalid",
                                "usage": None,
                                "cost": {"status": "unknown", "amount": None, "currency": None},
                            }
                        ],
                    },
                }
            ]
        },
    )
    rows = summarize(tmp_path, manifest, batch, {})
    assert rows[0]["unknown_stage_charges"] == 1
    assert rows[0]["source_groups"] == 1
    assert rows[0]["cost_per_correct_result"] is None
    assert rows[0]["cost_per_dispatched_attempt"] is None
    write_report(tmp_path / "report", rows, batch)
    assert (tmp_path / "report/costs.csv").exists()


@pytest.mark.parametrize(
    "code,status,stops",
    [
        ("invalid_provider_output", 400, True),
        ("provider_quota", 429, True),
        ("budget_exceeded", None, False),
    ],
)
def test_batch_stops_on_provider_errors_but_not_legacy_local_limits(
    tmp_path, png, code, status, stops
):
    import httpx

    from evaluation.batch import new_batch, run_batch, save

    samples = tmp_path / "samples"
    samples.mkdir()
    for name in ["a.png", "b.png"]:
        (samples / name).write_bytes(png)
    manifest = prepare(tmp_path, samples, tmp_path / ".local/corpus")
    path = tmp_path / ".local/state.json"
    save(path, new_batch(manifest, {"test": "v"}, "batch"))
    calls = []

    def handler(request):
        if request.url.path == "/v1/profiles":
            return httpx.Response(
                200,
                json={
                    "profiles": [
                        {"id": "test", "version": "v", "configured": True, "enabled": True}
                    ]
                },
            )
        if request.method == "POST":
            calls.append(request)
            return httpx.Response(202, json={"scan_id": "scan"})
        return httpx.Response(
            200,
            json={
                "state": "failed",
                "runs": [
                    {
                        "state": "failed",
                        "profile_version": "v",
                        "error": {"code": code},
                        "diagnostics": {"stages": [{"usage": {"http_status": status}}]},
                    }
                ],
            },
        )

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler)) as client:
        state = run_batch(tmp_path, manifest, path, client)
    assert len(calls) == (1 if stops else 2)
    assert [r["state"] for r in state["rows"]] == (
        ["failed", "not_run"] if stops else ["failed", "failed"]
    )
    assert state["complete"] is not stops


def test_cost_tariff_uses_immutable_run_snapshot_not_changed_configuration(tmp_path):
    from evaluation.batch import save
    from evaluation.cost_report import summarize

    manifest = {"inputs": [{"id": "one", "group_id": "g"}]}
    batch = {
        "profiles": {"p": "old-version"},
        "rows": [
            {
                "input_id": "one",
                "profile_id": "p",
                "state": "succeeded",
                "result_path": "result.json",
            }
        ],
    }
    saved = {"model": "original", "tariff": {"input_rate": "1"}}
    save(
        tmp_path / "result.json",
        {
            "runs": [
                {
                    "profile_id": "p",
                    "profile_version": "old-version",
                    "diagnostics": {"stages": [], "versions": {"option": json.dumps(saved)}},
                }
            ]
        },
    )
    row = summarize(
        tmp_path, manifest, batch, {"p": {"model": "new", "tariff": {"input_rate": "99"}}}
    )[0]
    assert row["option"] == saved
    assert row["option_source"] == "stored_run_snapshot"
