"""Offline observer contract: ordering, isolation, persistence and no extra dispatch."""

import json
import time
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.api import create_app
from backend.demo_events import DemoHub, PhoneState, observe
from backend.models import Stage


@pytest.fixture(autouse=True)
def close_observers(monkeypatch):
    opened = []
    original = DemoHub.__init__

    def init(self, *args, **kwargs):
        original(self, *args, **kwargs)
        opened.append(self)

    monkeypatch.setattr(DemoHub, "__init__", init)
    yield
    for hub in opened:
        hub.close()


def phone(seq=1, journey=None, phase="crop"):
    return PhoneState(sequence=seq, journey_id=journey or uuid4(), phase=phase)


def test_phone_order_privacy_and_expiry(tmp_path):
    now = [1000.0]
    hub = DemoHub(tmp_path / "state", ttl=60, clock=lambda: now[0])
    sid, journey = str(uuid4()), uuid4()
    hub.phone(sid, phone(2, journey, "review"))
    hub.phone(sid, phone(1, journey, "crop"))
    hub.phone(sid, phone(2, journey, "preview"))
    state = hub.snapshot()["sessions"][0]
    assert state["phone"] == "review" and len(state["events"]) == 1
    state["phone"] = "failed"
    assert hub.snapshot()["sessions"][0]["phone"] == "review"
    now[0] += 61
    assert hub.snapshot()["sessions"] == []
    for body in (
        {"sequence": 1, "phase": "review"},
        {"sequence": 1, "phase": "idle", "iban": "sensitive"},
        {"sequence": 1, "phase": "confirmed"},
    ):
        with pytest.raises(ValidationError):
            PhoneState.model_validate(body)


def test_binding_and_late_result_isolation(tmp_path, uk):
    hub = DemoHub(tmp_path / "state")
    sid, journey = str(uuid4()), uuid4()
    hub.phone(sid, phone(1, journey))
    hub.bind(uk, sid, str(journey))
    revision = hub.revision
    hub.bind(uk, str(uuid4()), str(uuid4()))
    assert hub.revision == revision
    stage = Stage(
        id="stage-1",
        method="vision",
        execution="external",
        provider="example",
        requested_model="test-model",
        payload_classes=["image"],
        input_hash="0" * 64,
    )
    hub.backend(uk.scan_id, "request", stage, run_id="run-1")
    hub.backend(uk.scan_id, "response", stage, run_id="run-1")
    state = hub.snapshot()["sessions"][0]
    assert len(state["stages"]) == 1
    assert state["stages"][0]["state"] == "response"
    assert "rendition" not in json.dumps(state) and "account_alias" not in json.dumps(state)
    hub.backend(uk.scan_id, "confirmed")
    done = hub.revision
    hub.backend(uk.scan_id, "confirmed")
    assert hub.revision == done
    hub.phone(sid, phone(2, uuid4(), "crop"))
    before = hub.snapshot()
    hub.backend(uk.scan_id, "completed", outcome="success")
    hub.backend("unknown", "failed")
    assert hub.snapshot()["sessions"] == before["sessions"]
    assert hub.snapshot()["sessions"][0]["completed_at"] is None


def test_restart_marks_interrupted_not_idle(tmp_path, uk):
    path = tmp_path / "state"
    hub = DemoHub(path)
    sid, journey = str(uuid4()), uuid4()
    hub.phone(sid, phone(1, journey, "reading"))
    hub.bind(uk, sid, str(journey))
    hub.backend(uk.scan_id, "request")
    hub.close()
    restored = DemoHub(path).snapshot()["sessions"][0]
    assert restored["backend"] == "interrupted" and restored["last_seen"] == 0
    path.write_text("broken")
    assert DemoHub(path).snapshot()["sessions"] == []


def test_bounded_retention_and_observer_failure(tmp_path, monkeypatch, uk):
    now = [1000.0]
    hub = DemoHub(tmp_path / "state", clock=lambda: now[0])
    for _ in range(10):
        now[0] += 1
        hub.phone(str(uuid4()), phone())
    assert len(hub.snapshot()["sessions"]) == 8
    sid = next(iter(hub.sessions))
    for i in range(2, 72):
        hub.phone(sid, phone(i))
    assert len(hub.sessions[sid]["events"]) == 64
    for i in range(135):
        scan = uk.model_copy(update={"scan_id": f"scan-{i}"})
        hub.bind(scan, sid, "previous-journey")
    hub.snapshot()
    assert len(hub.bindings) <= 128
    monkeypatch.setattr("backend.store.private_write", lambda *a: (_ for _ in ()).throw(OSError()))
    hub.phone(sid, phone(99))
    assert hub.sessions[sid]["phone_sequence"] == 99
    monkeypatch.setattr(hub, "phone", lambda *a: (_ for _ in ()).throw(RuntimeError()))
    observe(hub, "phone", sid, phone(100))
    observe(None, "phone", sid, phone())


def test_api_auth_and_observation_do_not_dispatch(settings, definitions, adapters, png):
    app = create_app(settings, definitions, adapters)
    with TestClient(app) as client:
        assert client.get("/v1/demo/snapshot").status_code == 401
        assert client.get("/v1/demo/events").status_code == 401
        assert client.get("/demo").status_code == 200
        for name in ("demo.js", "demo.css", "state.js", "qr.png"):
            response = client.get("/demo/assets/" + name)
            assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
        assert client.get("/demo/assets/secret").status_code == 404
        client.headers["Authorization"] = "Bearer " + settings.token.get_secret_value()
        sid, journey = str(uuid4()), str(uuid4())
        endpoint = "/v1/demo/sessions/" + sid
        assert (
            client.put(
                endpoint, json={"sequence": 1, "journey_id": journey, "phase": "uploading"}
            ).status_code
            == 200
        )
        assert (
            client.put(endpoint, json={"sequence": 2, "phase": "review", "amount": 100}).status_code
            == 422
        )
        headers = {
            "Idempotency-Key": "demo-once",
            "X-Scanpay-Demo-Session": sid,
            "X-Scanpay-Demo-Journey": journey,
        }

        def submit():
            return client.post(
                "/v1/scans",
                headers=headers,
                files={"image": ("photo.png", png, "image/png")},
                data={"options": json.dumps({"mode": "extract", "profiles": ["success"]})},
            )

        accepted = submit()
        assert accepted.status_code == 202
        for _ in range(100):
            result = client.get("/v1/demo/snapshot").json()
            if result["sessions"][0]["backend"] == "completed":
                break
            time.sleep(0.01)
        state = result["sessions"][0]
        assert state["scan_id"] == accepted.json()["scan_id"]
        assert state["backend"] == "completed"
        assert [e["kind"] for e in state["events"]][-2:] == ["validation", "completed"]
        assert submit().json()["scan_id"] == state["scan_id"]
        assert adapters["success"].calls == 1
        assert not any(
            word in json.dumps(result)
            for word in ("iban", "beneficiary", "canonical_sha256", "Bearer", "evidence")
        )


@pytest.mark.asyncio
async def test_stream_initial_snapshot_and_new_revision(settings, definitions, adapters):
    from types import SimpleNamespace

    app = create_app(settings, definitions, adapters)
    hub = DemoHub(settings.data_dir / "demo.json")

    class Request:
        app = SimpleNamespace(state=SimpleNamespace(demo=hub))

        async def is_disconnected(self):
            return False

    route = next(r for r in app.routes if r.path == "/v1/demo/events")
    response = await route.endpoint(Request(), after=9999)
    first = await anext(response.body_iterator)
    assert "event: snapshot" in first and '"sessions": []' in first
    sid = str(uuid4())
    hub.phone(sid, phone())
    second = await anext(response.body_iterator)
    assert sid in second and "id: 1" in second
    await response.body_iterator.aclose()
    hub.close()


def test_timeout_and_observer_exception_cannot_add_calls(
    settings, definitions, adapters, png, monkeypatch
):
    import asyncio

    calls = []

    class WaitingAdapter:
        async def extract(self, context):
            calls.append(context.scan.scan_id)
            stage = context.stage("synthetic_fixture", external=False, payloads=[])
            context.demo("request", stage)
            await asyncio.sleep(1)

    settings.stage_timeout_seconds = 0.01
    app = create_app(settings, definitions, {**adapters, "success": WaitingAdapter()})
    with TestClient(app) as client:
        client.headers["Authorization"] = "Bearer " + settings.token.get_secret_value()
        sid, journey = str(uuid4()), str(uuid4())
        client.put(
            "/v1/demo/sessions/" + sid,
            json={"sequence": 1, "journey_id": journey, "phase": "reading"},
        )
        response = client.post(
            "/v1/scans",
            headers={
                "Idempotency-Key": "timeout",
                "X-Scanpay-Demo-Session": sid,
                "X-Scanpay-Demo-Journey": journey,
            },
            files={"image": ("a.png", png, "image/png")},
            data={"options": json.dumps({"mode": "extract", "profiles": ["success"]})},
        )
        assert response.status_code == 202
        for _ in range(100):
            state = client.get("/v1/demo/snapshot").json()["sessions"][0]
            if state["backend"] == "failed":
                break
            time.sleep(0.01)
        assert state["backend"] == "failed" and state["outcome"] == "error"
        assert state["completed_at"] is None and len(calls) == 1
        monkeypatch.setattr(app.state.demo, "bind", lambda *a: (_ for _ in ()).throw(OSError()))
        response = client.post(
            "/v1/scans",
            headers={
                "Idempotency-Key": "observer-down",
                "X-Scanpay-Demo-Session": sid,
                "X-Scanpay-Demo-Journey": journey,
            },
            files={"image": ("a.png", png, "image/png")},
            data={"options": json.dumps({"mode": "extract", "profiles": ["failure"]})},
        )
        assert response.status_code == 202


def test_upload_can_arrive_before_phone_telemetry_and_reset_does_not_cancel(tmp_path, uk):
    hub = DemoHub(tmp_path / "state")
    sid, journey = str(uuid4()), uuid4()
    hub.bind(uk, sid, str(journey))
    state = hub.snapshot()["sessions"][0]
    assert state["last_seen"] == 0 and state["phone"] == "paused"
    hub.phone(sid, phone(1, journey, "reading"))
    hub.backend(uk.scan_id, "request")
    hub.phone(sid, PhoneState(sequence=2, phase="idle"))
    state = hub.snapshot()["sessions"][0]
    assert state["phone"] == "idle" and state["backend"] == "request"
    assert state["scan_id"] == uk.scan_id and state["journey_id"] == str(journey)
    hub.backend(uk.scan_id, "completed", outcome="success")
    assert hub.snapshot()["sessions"][0]["backend"] == "completed"
