import json

import pytest

from backend.document_observations import observe
from evaluation.batch import new_batch, save
from evaluation.corpus import prepare
from evaluation.replay import replay


def test_replay_accounts_for_gaps_and_preserves_source_provenance(tmp_path, png):
    samples = tmp_path / "samples"
    samples.mkdir()
    for name in ("a.png", "b.png"):
        (samples / name).write_bytes(png)
    manifest = prepare(tmp_path, samples, tmp_path / ".local/corpus")
    source = new_batch(manifest, {"test": "v1"}, "batch")
    source["rows"][0].update(state="succeeded", scan_id="s", result_path=".local/result.json")
    result = {
        "scan_id": "s",
        "input": {"image_id": "img"},
        "runs": [
            {
                "id": "r",
                "profile_id": "test",
                "profile_version": "v1",
                "diagnostics": {
                    "stages": [
                        {
                            "id": "stage",
                            "execution": "external",
                            "method": "ocr",
                            "cost": {"status": "unknown"},
                        }
                    ]
                },
            }
        ],
    }
    save(tmp_path / ".local/result.json", result)
    text = "Bank details\nSort code: 10-20-30\n\nAccount number: 12345678"
    doc = observe({"pages": [{"markdown": text}]}, "mistral", text, "img", "stage")
    path = tmp_path / ".local/artifacts/s/r.stage.document.json"
    path.parent.mkdir(parents=True)
    path.write_text(doc.to_json())
    before = path.read_bytes()
    out = tmp_path / ".local/replay.json"
    report = replay(tmp_path, manifest, source, tmp_path / ".local/artifacts", out)
    assert report["counts"] == {"replayed": 1, "unavailable": 1}
    assert report["new_external_calls"] == 0
    assert report["accuracy"] is None
    assert report["rows"][0]["source_cost"] == {"status": "unknown"}
    assert report["rows"][0]["interpretations"]["rules@2"]["payment"]["review"][
        "user_confirmation_required"
    ]
    assert path.read_bytes() == before
    with pytest.raises(ValueError, match="immutable"):
        replay(tmp_path, manifest, source, tmp_path / ".local/artifacts", out)
    source["rows"].pop()
    with pytest.raises(ValueError, match="matrix"):
        replay(tmp_path, manifest, source, tmp_path / ".local/artifacts", tmp_path / "new.json")


def test_replay_rejects_mismatched_provenance(tmp_path, png):
    samples = tmp_path / "samples"
    samples.mkdir()
    (samples / "a.png").write_bytes(png)
    manifest = prepare(tmp_path, samples, tmp_path / ".local/corpus")
    source = new_batch(manifest, {"test": "v"}, "batch")
    source["rows"][0].update(result_path="result.json", scan_id="s")
    save(
        tmp_path / "result.json",
        {
            "scan_id": "s",
            "input": {"image_id": "actual"},
            "runs": [
                {
                    "id": "r",
                    "profile_id": "test",
                    "profile_version": "v",
                    "diagnostics": {
                        "stages": [{"id": "stage", "method": "ocr", "execution": "external"}]
                    },
                }
            ],
        },
    )
    path = tmp_path / "artifacts/s/r.stage.document.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"version": "1", "source_stage_id": "stage", "image_id": "wrong"}))
    with pytest.raises(ValueError, match="provenance"):
        replay(tmp_path, manifest, source, tmp_path / "artifacts", tmp_path / "out.json")
