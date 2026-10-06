import asyncio
from time import monotonic

from backend.images import prepare_image
from backend.models import Hints, Options
from backend.runtime import Runtime
from backend.store import Store, request_digest
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish


async def test_deadline_expires_before_dispatch(settings, definitions, adapters, png):
    store = Store(settings)
    try:
        options = Options(mode="extract", profiles=["success"])
        scan, _ = store.accept(
            "k",
            request_digest(png, options),
            prepare_image(png, Hints()),
            options,
            [definitions["success"]],
            [],
        )
        runtime = Runtime(store, settings, adapters)
        await runtime.process(scan.scan_id, [definitions["success"]], monotonic() - 241)
        assert adapters["success"].calls == 0
        assert store.get(scan.scan_id).runs[0].error.code == "provider_timeout"
    finally:
        store.close()


def test_stage_timeout_and_partial_results_visible(settings, definitions, adapters, png):
    settings.stage_timeout_seconds = 0.1

    class Slow:
        async def extract(self, context):
            await asyncio.Event().wait()

    adapters["failure"] = Slow()
    with client_for(settings, definitions, adapters) as client:
        response = upload(client, png, mode="compare", profiles=["success", "failure"])
        import time

        for _ in range(50):
            current = client.get(response.headers["location"]).json()
            if current["runs"][0]["state"] == "completed":
                break
            time.sleep(0.001)
        assert current["runs"][0]["payment"] is not None
        assert current["final_result_id"] is None
        result = finish(client, response)
        assert result["state"] == "partially_completed"
        assert result["runs"][1]["error"]["code"] == "provider_timeout"


def test_restart_preserves_first_completed_comparison(settings, definitions, adapters, png):
    class Slow:
        async def extract(self, context):
            await asyncio.Event().wait()

    adapters["failure"] = Slow()
    with client_for(settings, definitions, adapters) as client:
        response = upload(client, png, mode="compare", profiles=["success", "failure"])
        import time

        for _ in range(100):
            partial = client.get(response.headers["location"]).json()
            if partial["runs"][0]["state"] == "completed":
                break
            time.sleep(0.005)
        assert partial["runs"][0]["payment"] is not None
    with client_for(settings, definitions, adapters) as client:
        result = client.get(response.headers["location"]).json()
        assert result["state"] == "interrupted"
        assert result["runs"][0]["payment"] == partial["runs"][0]["payment"]
        assert result["runs"][1]["state"] == "interrupted"
        assert adapters["success"].calls == 1


def test_health_and_storage_errors_are_sanitized(settings, definitions, adapters, monkeypatch, png):
    with client_for(settings, definitions, adapters) as client:

        def fail(*args):
            raise OSError("SECRET payment and path")

        monkeypatch.setattr(client.app.state.store, "ready", fail)
        assert client.get("/health").status_code == 503
        monkeypatch.setattr(client.app.state.store, "get", fail)
        result = client.get("/v1/scans/unknown")
        assert result.status_code == 503 and "SECRET" not in result.text
        client.app.state.runtime.healthy = False
        assert upload(client, png).status_code == 503
