import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from backend.api import create_app
from backend.models import Scan
from backend.tests.conftest import upload


def client_for(settings, definitions, adapters):
    return TestClient(
        create_app(settings, definitions, adapters),
        headers={"Authorization": "Bearer " + settings.token.get_secret_value()},
    )


def finish(client, response):
    assert response.status_code == 202, response.text
    location = response.headers["location"]
    for _ in range(100):
        result = client.get(location)
        assert result.status_code == 200
        if result.json()["state"] not in {"queued", "running"}:
            return result.json()
        time.sleep(0.01)
    pytest.fail("Job did not finish")


def test_api_completed_persists_and_deletion_tombstone(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/v1/profiles").status_code == 200
        submitted = upload(client, png)
        result = finish(client, submitted)
        assert result["state"] == "completed"
        assert result["runs"][0]["payment"]["review"]["state"] == "ready_for_review"
        assert result["final_result_id"] == result["runs"][0]["id"]
        assert result["runs"][0]["diagnostics"]["timings_ms"]["total"] is None
        Scan.model_validate(result)
    with client_for(settings, definitions, adapters) as client:
        assert client.get(submitted.headers["location"]).json() == result
        again = upload(client, png)
        assert again.json()["scan_id"] == result["scan_id"]
        assert adapters["success"].calls == 1
        assert client.delete(submitted.headers["location"]).status_code == 204
        assert client.get(submitted.headers["location"]).status_code == 404
        assert upload(client, png).status_code == 410
        assert not (settings.data_dir / "jobs" / result["scan_id"]).exists()


def test_saved_result_survives_profile_removal(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        submitted = upload(client, png)
        result = finish(client, submitted)
        assert result["state"] == "completed"
    with client_for(settings, {}, {}) as client:
        assert client.get(submitted.headers["location"]).json() == result
        assert upload(client, png, key="new-request").status_code == 422
        assert adapters["success"].calls == 1


def test_partial_compare_snapshot_and_same_key(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        response = upload(client, png, mode="compare", profiles="all_enabled")
        result = finish(client, response)
        assert result["state"] == "partially_completed"
        assert result["final_result_id"] is None
        assert [r["profile_id"] for r in result["runs"]] == ["failure", "success"]
        definitions["success"].metadata.enabled = False
        assert (
            upload(client, png, mode="compare", profiles="all_enabled").json()["scan_id"]
            == result["scan_id"]
        )
        assert upload(client, png, key="different").status_code == 422
        assert upload(client, png, mode="extract").status_code == 409


def test_concurrent_retry_creates_one_job(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(pool.map(lambda _: upload(client, png), range(12)))
        assert all(r.status_code == 202 for r in responses)
        assert len({r.json()["scan_id"] for r in responses}) == 1
        finish(client, responses[0])
        assert adapters["success"].calls == 1


@pytest.mark.parametrize(
    "body,status", [(b"garbage", 400), (b"\x00\x00\x00\x18ftypheic", 415), (b"GIF89a", 415)]
)
def test_bad_bytes(settings, definitions, adapters, body, status):
    with client_for(settings, definitions, adapters) as client:
        assert upload(client, body).status_code == status
        assert adapters["success"].calls == 0


def test_bad_auth_options_headers_and_multiple_files(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        assert client.get("/health", headers={"Authorization": "invalid"}).status_code == 200
        assert (
            client.get("/v1/profiles", headers={"Authorization": "Bearer wrong"}).status_code == 401
        )
        for options, expected in [
            ("{", 400),
            ('{"mode":"extract","profiles":["success"],"secret":"do-not-reflect"}', 422),
            ("null", 422),
        ]:
            result = client.post(
                "/v1/scans",
                headers={"Idempotency-Key": "x"},
                files={"image": ("x", png)},
                data={"options": options},
            )
            assert result.status_code == expected
            assert "do-not-reflect" not in result.text
        assert (
            client.post(
                "/v1/scans", files={"image": ("x", png)}, data={"options": "{}"}
            ).status_code
            == 422
        )
        result = client.post(
            "/v1/scans",
            headers={"Idempotency-Key": "x"},
            files=[("image", ("a", png)), ("image", ("b", png))],
            data={"options": json.dumps({"mode": "extract", "profiles": ["success"]})},
        )
        assert result.status_code == 422
        assert client.get("/docs").status_code == 404
        assert client.get("/v1/scans/unknown").status_code == 404
        assert client.delete("/v1/scans/unknown").status_code == 404


def test_shutdown_interrupts_and_active_delete_rejected(settings, definitions, adapters, png):
    class Blocking:
        calls = 0

        async def extract(self, context):
            self.calls += 1
            context.stage("waiting", external=False, payloads=[])
            await asyncio.Event().wait()

    blocker = Blocking()
    adapters["success"] = blocker
    with client_for(settings, definitions, adapters) as client:
        response = upload(client, png)
        assert client.delete(response.headers["location"]).status_code == 409
    with client_for(settings, definitions, adapters) as client:
        result = client.get(response.headers["location"]).json()
        assert result["state"] == "interrupted"
        assert result["runs"][0]["state"] == "interrupted"
        assert blocker.calls == 1
        assert upload(client, png).json()["scan_id"] == result["scan_id"]


@pytest.mark.parametrize(
    "code",
    [
        "provider_auth",
        "provider_quota",
        "provider_timeout",
        "provider_refusal",
        "provider_unavailable",
        "unsupported_language",
        "invalid_provider_output",
        "budget_exceeded",
    ],
)
def test_safe_provider_errors(settings, definitions, adapters, png, code):
    adapters["failure"].failure = code
    with client_for(settings, definitions, adapters) as client:
        result = finish(client, upload(client, png, profiles=["failure"]))
        assert result["state"] == "failed"
        assert result["runs"][0]["error"]["code"] == code
        assert result["final_result_id"] is None


def test_timeout_and_unexpected_error_do_not_leak(settings, definitions, adapters, png):
    class Bad:
        async def extract(self, context):
            raise RuntimeError("SECRET and invoice banking details")

    adapters["success"] = Bad()
    with client_for(settings, definitions, adapters) as client:
        result = finish(client, upload(client, png))
        assert "SECRET" not in json.dumps(result)
        assert result["runs"][0]["error"]["code"] == "internal_error"


def test_bounded_queue(settings, definitions, adapters, png):
    settings.workers, settings.queue_capacity = 1, 1

    class Blocking:
        async def extract(self, context):
            await asyncio.Event().wait()

    adapters["success"] = Blocking()
    with client_for(settings, definitions, adapters) as client:
        assert upload(client, png, key="one").status_code == 202
        assert upload(client, png, key="two").status_code == 202
        assert upload(client, png, key="three").status_code == 429
