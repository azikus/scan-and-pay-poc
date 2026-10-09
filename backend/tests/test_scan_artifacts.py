import json
import os

import pytest

from backend.models import Stage
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish


def stage_fixture(client, png, methods, *, source="automated"):
    result = finish(
        client,
        client.post(
            "/v1/scans",
            headers={"Idempotency-Key": "artifacts", "X-Scanpay-Client": source},
            files={"image": ("photo.png", png, "image/png")},
            data={"options": json.dumps({"mode": "extract", "profiles": ["failure"]})},
        ),
    )
    store = client.app.state.store
    scan = store.get(result["scan_id"])
    run = scan.runs[0]
    run.diagnostics.stages = [
        Stage(
            id=f"stage-{index}",
            method=method,
            execution="external",
            provider="test-provider",
            requested_model="test-model",
            source_stage_ids=["stage-0"] if index else [],
        )
        for index, method in enumerate(methods)
    ]
    store.save(scan)
    return scan, run, store.artifacts / scan.scan_id


def write(path, value):
    path.write_text(json.dumps(value))


def test_hybrid_outputs_separate_stages_and_keep_exact_saved_values(
    settings, definitions, adapters, png
):
    with client_for(settings, definitions, adapters) as client:
        scan, run, folder = stage_fixture(client, png, ["ocr", "interpretation"])
        pending = {"http_status": 202, "body": {"status": "running"}}
        ocr = {"http_status": 200, "body": {"text": "Invoice 00007", "optional": None}}
        llm = {"http_status": 200, "body": {"output": '{"reference":"00007"}'}}
        first = folder / f"{run.id}.stage-0.zzz.raw.json"
        last = folder / f"{run.id}.stage-0.aaa.raw.json"
        write(first, pending)
        write(last, ocr)
        os.utime(first, ns=(100, 100))
        os.utime(last, ns=(200, 200))
        write(folder / f"{run.id}.stage-1.test.raw.json", llm)
        document = {"text": "Invoice 00007", "spans": []}
        write(folder / f"{run.id}.stage-0.document.json", document)
        write(folder / f"{run.id}.interpretation-input.json", document)
        write(folder / "unrelated.raw.json", {"secret": "must-not-be-returned"})
        route = f"/v1/admin/scans/{scan.scan_id}/artifacts"
        before = client.get(f"/v1/scans/{scan.scan_id}").json()
        response = client.get(route)
        assert response.status_code == 200
        stages = response.json()["runs"][0]["stages"]
        assert [s["method"] for s in stages] == ["ocr", "interpretation"]
        assert [o["value"] for o in stages[0]["outputs"]] == [pending, ocr, document]
        assert [o["value"] for o in stages[1]["outputs"]] == [llm, document]
        assert stages[1]["outputs"][1]["kind"] == "llm_input"
        assert "must-not-be-returned" not in response.text
        assert client.get(f"/v1/scans/{scan.scan_id}").json() == before
        assert adapters["failure"].calls == 1
        assert response.headers["Cache-Control"] == "no-store"
        assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert client.delete(f"/v1/scans/{scan.scan_id}").status_code == 204
        assert client.get(route).status_code == 404


@pytest.mark.parametrize("methods", [[], ["vision"], ["ocr", "interpretation"]])
def test_legacy_output_is_never_assigned_to_ambiguous_stage(
    settings, definitions, adapters, png, methods
):
    with client_for(settings, definitions, adapters) as client:
        scan, run, folder = stage_fixture(client, png, methods)
        raw = {"output": "<script>untrusted</script>", "amount": None}
        write(folder / f"{run.id}.raw.json", raw)
        stages = client.get(f"/v1/admin/scans/{scan.scan_id}/artifacts").json()["runs"][0]["stages"]
        saved = [s for s in stages if s["outputs"]]
        assert len(saved) == 1
        assert saved[0]["stage_id"] == ("stage-0" if len(methods) == 1 else None)
        assert saved[0]["outputs"][0]["value"] == raw


def test_missing_corrupt_and_symlink_artifacts(settings, definitions, adapters, png, tmp_path):
    with client_for(settings, definitions, adapters) as client:
        scan, run, folder = stage_fixture(client, png, ["ocr", "interpretation"])
        (folder / f"{run.id}.stage-0.bad.raw.json").write_text("not-json")
        secret = tmp_path / "credentials.json"
        write(secret, {"secret": "do-not-read"})
        (folder / f"{run.id}.stage-0.link.raw.json").symlink_to(secret)
        response = client.get(f"/v1/admin/scans/{scan.scan_id}/artifacts")
        stages = response.json()["runs"][0]["stages"]
        assert len(stages[0]["outputs"]) == 1
        assert stages[0]["outputs"][0]["error"]
        assert stages[1]["outputs"] == []
        assert "do-not-read" not in response.text
        assert client.get("/v1/admin/scans/missing/artifacts").status_code == 404
        # A valid stored scan must not turn a replaced folder into a file-read escape.
        folder.rename(folder.with_name("retained"))
        folder.symlink_to(tmp_path, target_is_directory=True)
        assert client.get(f"/v1/admin/scans/{scan.scan_id}/artifacts").status_code == 404


def test_mobile_image_is_exact_original_authenticated_and_mobile_only(
    settings, definitions, adapters, png
):
    with client_for(settings, definitions, adapters) as client:
        scan, run, folder = stage_fixture(client, png, ["vision"], source="mobile")
        route = f"/v1/admin/scans/{scan.scan_id}/image"
        (folder / "canonical.png").write_bytes(b"not-the-upload")
        response = client.get(route)
        assert response.status_code == 200 and response.content == png
        assert response.headers["Content-Type"] == "image/png"
        assert response.headers["Cache-Control"] == "no-store"
        assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
        automated = finish(client, upload(client, png))
        assert client.get(f"/v1/admin/scans/{automated['scan_id']}/image").status_code == 404
        (folder / "original").write_bytes(b"changed")
        assert client.get(route).status_code == 503
        (folder / "original").unlink()
        assert client.get(route).status_code == 404
        assert client.delete(f"/v1/scans/{scan.scan_id}").status_code == 204
        assert client.get(route).status_code == 404
