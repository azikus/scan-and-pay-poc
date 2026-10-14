import json

import httpx
import pytest

from backend.images import sha256
from evaluation.approved import LOCK_PATH, fingerprint, load_inputs, validate_inputs
from evaluation.batch import new_batch, run_batch, save
from evaluation.corpus import validate_manifest


@pytest.fixture
def approved(tmp_path, png):
    items = []
    for n in range(2):
        payload = png + bytes([n])
        path = tmp_path / f"image-{n}.png"
        path.write_bytes(payload)
        items.append(
            {"id": str(n), "path": path.name, "sha256": sha256(payload), "status": "prepared"}
        )
    save(
        tmp_path / LOCK_PATH,
        {"version": 1, "image_count": 2, "image_set_sha256": fingerprint(items)},
    )
    save(tmp_path / ".local/evaluation/active-inventory.json", {"inputs": items})
    return tmp_path, {"kind": "approved_inventory", "inputs": items}


def test_approved_set_is_order_independent_and_loads_private_paths(approved):
    root, manifest = approved
    assert load_inputs(root) == manifest["inputs"]
    validate_inputs(root, list(reversed(manifest["inputs"])))
    validate_manifest(root, manifest)


@pytest.mark.parametrize(
    "change",
    [
        "extra",
        "missing",
        "replacement",
        "duplicate",
        "bad_hash",
        "bytes",
        "missing_file",
        "version",
        "missing_lock",
        "absolute",
        "escape",
        "duplicate_id",
    ],
)
def test_approval_rejects_unapproved_or_changed_inputs_before_network(approved, change):
    root, manifest = approved
    items = manifest["inputs"]
    if change == "extra":
        items.append(dict(items[0], id="extra"))
    elif change == "missing":
        items.pop()
    elif change == "replacement":
        items[0]["sha256"] = "0" * 64
    elif change == "duplicate":
        items[1]["sha256"] = items[0]["sha256"]
    elif change == "bad_hash":
        items[0]["sha256"] = "not-a-hash"
    elif change == "bytes":
        (root / items[0]["path"]).write_bytes(b"changed")
    elif change == "missing_file":
        (root / items[0]["path"]).unlink()
    elif change == "version":
        lock = json.loads((root / LOCK_PATH).read_text())
        lock["version"] = 2
        save(root / LOCK_PATH, lock)
    elif change == "missing_lock":
        (root / LOCK_PATH).unlink()
    elif change == "absolute":
        items[0]["path"] = str(root / items[0]["path"])
    elif change == "escape":
        items[0]["path"] = "../escape.png"
    elif change == "duplicate_id":
        items[1]["id"] = items[0]["id"]
    path = root / ".local/run/state.json"
    save(path, new_batch(manifest, {"p": "v"}, "fresh"))
    with pytest.raises((ValueError, FileNotFoundError)):
        run_batch(root, manifest, path, None)


def test_empty_inventory_is_invalid():
    with pytest.raises(ValueError, match="identities"):
        fingerprint([])


def test_paid_run_sends_only_pinned_bytes_and_refuses_rerun(approved):
    root, manifest = approved
    path = root / ".local/run/state.json"
    save(path, new_batch(manifest, {"p": "v"}, "fresh"))
    posts = []

    def handler(request):
        if request.url.path == "/v1/profiles":
            return httpx.Response(
                200,
                json={
                    "profiles": [{"id": "p", "version": "v", "enabled": True, "configured": True}]
                },
            )
        if request.method == "POST":
            posts.append(request)
            item = manifest["inputs"][len(posts) - 1]
            assert (root / item["path"]).read_bytes() in request.content
            return httpx.Response(202, json={"scan_id": f"scan-{len(posts)}"})
        return httpx.Response(
            200,
            json={
                "state": "completed",
                "input": {"original_sha256": manifest["inputs"][len(posts) - 1]["sha256"]},
                "runs": [
                    {"state": "completed", "profile_id": "p", "profile_version": "v", "error": None}
                ],
            },
        )

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler)) as client:
        assert run_batch(root, manifest, path, client, poll_seconds=0)["complete"]
        with pytest.raises(ValueError, match="fresh batch"):
            run_batch(root, manifest, path, client)
    assert len(posts) == 2


def test_file_changed_after_preflight_is_never_sent(approved):
    root, manifest = approved
    path = root / ".local/run/state.json"
    save(path, new_batch(manifest, {"p": "v"}, "fresh"))

    def handler(request):
        assert request.method == "GET"
        (root / manifest["inputs"][0]["path"]).write_bytes(b"changed-after-preflight")
        return httpx.Response(
            200,
            json={"profiles": [{"id": "p", "version": "v", "enabled": True, "configured": True}]},
        )

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="bytes changed"):
            run_batch(root, manifest, path, client)
    assert all(r["state"] == "not_run" for r in json.loads(path.read_text())["rows"])
