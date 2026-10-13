import asyncio
import json
from uuid import UUID, uuid4

import pytest

from backend.client_reviews import review_values
from backend.models import Scan
from backend.tests.conftest import upload
from backend.tests.test_api import client_for, finish


def test_backend_identity_is_stable_authenticated_and_read_only(settings, definitions, adapters):
    with client_for(settings, definitions, adapters) as client:
        first = client.get("/v1/profiles").json()["server_id"]
        assert str(UUID(first)) == first
        assert client.get("/v1/profiles").json()["server_id"] == first
        assert client.get("/v1/profiles", headers={"Authorization": "wrong"}).status_code == 401
        assert client.get("/v1/admin/scans").json()["scans"] == []
        assert all(adapter.calls == 0 for adapter in adapters.values())
    with client_for(settings, definitions, adapters) as client:
        assert client.get("/v1/profiles").json()["server_id"] == first


def body_for(result):
    run = Scan.model_validate(result).runs[0]
    return {
        "run_id": run.id,
        "selected_candidate_id": run.payment.candidates[0].id,
        "values": review_values(run.payment, run.payment.candidates[0].id),
    }


def test_json_nulls_review_idempotency_and_original_immutable(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        result = finish(client, upload(client, png))
        location = "/v1/scans/" + result["scan_id"]
        original = client.get(location).json()
        body = body_for(result)
        assert any(value is None for value in body["values"].values())
        body["values"]["/candidates/0/remittance/reference"] = "0000037"
        path = location + "/reviews/" + str(uuid4())
        first = client.put(path, json=body)
        assert first.status_code == 200, first.text
        assert first.json()["simulated"] is True
        assert first.json()["values"]["/candidates/0/remittance/reference"] == "0000037"
        assert client.put(path, json=body).json() == first.json()
        assert client.get(location).json() == original
        assert len(client.get(location + "/reviews").json()["reviews"]) == 1
        assert adapters["success"].calls == 1
        body["values"]["/candidates/0/remittance/reference"] = None
        assert client.put(path, json=body).status_code == 409
        null_version = client.put(location + "/reviews/" + str(uuid4()), json=body)
        assert null_version.status_code == 200
        assert null_version.json()["values"]["/candidates/0/remittance/reference"] is None
        scan_id = result["scan_id"]
    with client_for(settings, definitions, adapters) as client:
        assert len(client.get(location + "/reviews").json()["reviews"]) == 2
        summaries = client.get("/v1/admin/scans").json()
        assert summaries["scans"][0]["client_review_count"] == 2
        assert client.delete(location).status_code == 204
        assert client.get(location + "/reviews").status_code == 404
        with client.app.state.store.connection() as db:
            assert (
                db.execute(
                    "SELECT COUNT(*) FROM client_reviews WHERE scan_id=?", (scan_id,)
                ).fetchone()[0]
                == 0
            )


@pytest.mark.parametrize(
    "change",
    [
        "run",
        "candidate",
        "missing",
        "extra",
        "cross_candidate",
        "false_simulation",
        "unknown_key",
        "blank",
    ],
)
def test_invalid_review_does_not_change_extraction(settings, definitions, adapters, png, change):
    with client_for(settings, definitions, adapters) as client:
        result = finish(client, upload(client, png))
        body = body_for(result)
        if change == "run":
            body["run_id"] = "other"
        if change == "candidate":
            body["selected_candidate_id"] = "other"
        if change == "missing":
            body["values"].pop("/supplier_name")
        if change == "extra":
            body["values"]["/unexpected"] = "value"
        if change == "cross_candidate":
            body["values"]["/candidates/1/beneficiary_name"] = "Other option"
        if change == "false_simulation":
            body["simulated"] = False
        if change == "unknown_key":
            body["secret"] = "never-reflect-this"
        if change == "blank":
            body["values"]["/supplier_name"] = ""
        location = "/v1/scans/" + result["scan_id"]
        response = client.put(location + "/reviews/" + str(uuid4()), json=body)
        assert response.status_code == 422
        assert "never-reflect-this" not in response.text
        assert client.get(location).json() == result
        assert client.get(location + "/reviews").json() == {"reviews": []}


def test_active_failed_missing_and_auth(settings, definitions, adapters, png):
    class Blocked:
        async def extract(self, context):
            await asyncio.Event().wait()

    with client_for(settings, definitions, adapters) as client:
        failed = finish(client, upload(client, png, profiles=["failure"]))
        body = {
            "run_id": failed["runs"][0]["id"],
            "selected_candidate_id": "x",
            "values": {"/supplier_name": None},
        }
        path = "/v1/scans/" + failed["scan_id"] + "/reviews/" + str(uuid4())
        assert client.put(path, json=body).status_code == 422
        assert client.put("/v1/scans/missing/reviews/" + str(uuid4()), json=body).status_code == 404
        for route in ["/v1/admin/scans", "/v1/scans/" + failed["scan_id"] + "/reviews"]:
            assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert (
            client.put(path, json=body, headers={"Authorization": "Bearer wrong"}).status_code
            == 401
        )
    adapters["success"] = Blocked()
    with client_for(settings, definitions, adapters) as client:
        active = upload(client, png, key="active").json()
        assert (
            client.put(
                "/v1/scans/" + active["scan_id"] + "/reviews/" + str(uuid4()), json=body
            ).status_code
            == 409
        )


def test_admin_pagination_and_static_security(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        assert client.get("/v1/admin/scans").json() == {"scans": [], "next_offset": None}
        for i in range(3):
            finish(client, upload(client, png, key=str(i)))
        first = client.get("/v1/admin/scans?limit=2").json()
        second = client.get("/v1/admin/scans?limit=2&offset=2").json()
        assert first["next_offset"] == 2 and second["next_offset"] is None
        assert len({x["scan_id"] for x in first["scans"] + second["scans"]}) == 3
        assert "payment" not in json.dumps(first)
        for query in ("limit=101", "offset=-1", "limit=0"):
            assert client.get("/v1/admin/scans?" + query).status_code == 422
        shell = client.get("/admin")
        assert (
            shell.status_code == 200
            and "frame-ancestors 'none'" in shell.headers["Content-Security-Policy"]
        )
        assert shell.headers["Cache-Control"] == "no-store"
        for asset in (
            "admin.js",
            "theme.js",
            "context.js",
            "admin.css",
            "logo.svg",
            "HankenGrotesk-Regular.ttf",
        ):
            assert client.get("/admin/assets/" + asset).status_code == 200
        assert client.get("/admin/assets/.env").status_code == 404
        assert (
            client.get(
                "/v1/admin/scans", headers={"Origin": "https://untrusted.example"}
            ).headers.get("Access-Control-Allow-Origin")
            is None
        )


def test_method_catalog_is_authenticated_read_only_evidence(settings, definitions, adapters):
    with client_for(settings, definitions, adapters) as client:
        before = client.get("/v1/profiles").json()
        route = "/v1/admin/methods"
        assert client.get(route, headers={"Authorization": "Bearer wrong"}).status_code == 401
        response = client.get(route)
        assert response.status_code == 200
        data = response.json()
        assert data["measured_on"] == "2026-10-08"
        assert len(data["benchmarks"]) == 6
        assert all(row["timing_n"] == 17 for row in data["benchmarks"])
        assert "image" not in data and "credentials" not in data
        assert client.get("/v1/profiles").json() == before
        assert client.get("/v1/admin/scans").json()["scans"] == []
        assert all(adapter.calls == 0 for adapter in adapters.values())


def test_admin_method_selection_is_pinned_persistent_and_does_not_dispatch(
    settings, definitions, adapters, png
):
    route = "/v1/admin/selection"
    selected = {"id": "success", "version": definitions["success"].metadata.version}
    with client_for(settings, definitions, adapters) as client:
        scan = finish(client, upload(client, png))
        calls = adapters["success"].calls
        assert client.put(route, json=selected, headers={"Authorization": "bad"}).status_code == 401
        assert client.put(route, json={**selected, "version": "changed"}).status_code == 409
        assert client.put(route, json={**selected, "id": "unknown"}).status_code == 422
        assert client.put(route, json=selected).json() == selected
        assert adapters["success"].calls == calls
        assert client.get("/v1/scans/" + scan["scan_id"]).json() == scan
    with client_for(settings, definitions, adapters) as client:
        profiles = client.get("/v1/profiles").json()
        assert profiles["default_extract_profile_id"] == selected["id"]
        assert profiles["default_extract_profile_version"] == selected["version"]
        definitions["success"].metadata.enabled = False
        assert client.put(route, json=selected).status_code == 422
        # Unavailable selections stay explicit; no automatic fallback or version replacement.
        assert client.get("/v1/profiles").json()["default_extract_profile_id"] == selected["id"]


def test_source_filter_pagination_and_idempotent_origin(settings, definitions, adapters, png):
    with client_for(settings, definitions, adapters) as client:
        automated = finish(client, upload(client, png, key="automated"))

        def mobile(key, source="mobile"):
            return client.post(
                "/v1/scans",
                headers={"Idempotency-Key": key, "X-Scanpay-Client": source},
                files={"image": ("capture.png", png, "image/png")},
                data={"options": json.dumps({"mode": "extract", "profiles": ["success"]})},
            )

        first = finish(client, mobile("phone-1"))
        second = finish(client, mobile("phone-2"))
        assert mobile("phone-1", "automated").json()["scan_id"] == first["scan_id"]
        page = client.get("/v1/admin/scans?source=mobile&limit=1").json()
        assert page["next_offset"] == 1 and page["scans"][0]["scan_id"] == second["scan_id"]
        rest = client.get("/v1/admin/scans?source=mobile&limit=1&offset=1").json()
        assert rest["next_offset"] is None and rest["scans"][0]["source"] == "mobile"
        assert rest["scans"][0]["scan_id"] == first["scan_id"]
        assert (
            client.get("/v1/admin/scans?source=automated").json()["scans"][0]["scan_id"]
            == automated["scan_id"]
        )
        assert client.get("/v1/admin/scans?source=other").status_code == 422
        assert mobile("bad", "other").status_code == 422
        client.delete("/v1/scans/" + first["scan_id"])
        with client.app.state.store.connection() as db:
            assert (
                db.execute(
                    "SELECT COUNT(*) FROM scan_sources WHERE scan_id=?", (first["scan_id"],)
                ).fetchone()[0]
                == 0
            )
        # Older evaluation records do not need their immutable results rewritten.
        with client.app.state.store.connection() as db:
            db.execute("DELETE FROM scan_sources WHERE scan_id=?", (automated["scan_id"],))
        assert (
            client.get("/v1/admin/scans?source=automated").json()["scans"][0]["source"]
            == "automated"
        )
