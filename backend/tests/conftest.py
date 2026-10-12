import io
import json
import socket
from pathlib import Path

import pytest
from PIL import Image
from pydantic import SecretStr

from backend import data_policy
from backend.config import Settings
from backend.models import Scan
from backend.profiles import Definition, Profile
from backend.tests.fakes import FixtureAdapter


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Offline tests must not access network")

    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.fixture(autouse=True)
def historical_protocol_fixtures(request, monkeypatch):
    """Old synthetic transports exercise historical global-provider protocols.

    Production has no policy-off flag. Mark data_policy tests to exercise the real
    mandatory gate; sockets remain blocked in every test, including this suite.
    """
    historical_modules = {
        "test_boundaries",
        "test_partial",
        "test_compact",
        "test_draft_policy",
        "test_extended",
        "test_providers",
        "test_hybrid",
        "test_profile_options",
        "test_validation",
        "test_recipient_roles",
    }
    historical_budget_tests = {
        "test_budget_batch_atomic_no_partial_dispatch",
        "test_call_count_and_missing_ceiling",
        "test_single_owner_and_recovery_retains_billed_hold",
    }
    module = request.module.__name__.rsplit(".", 1)[-1]
    if (
        module in historical_modules
        or (module == "test_images_store" and request.node.name in historical_budget_tests)
    ) and request.node.get_closest_marker("data_policy") is None:
        monkeypatch.setattr(data_policy, "violations", lambda *args, **kwargs: [])


@pytest.fixture
def png():
    stream = io.BytesIO()
    Image.new("RGB", (20, 30), "white").save(stream, "PNG")
    return stream.getvalue()


@pytest.fixture
def settings(tmp_path):
    return Settings(
        data_dir=tmp_path / "private", token=SecretStr("offline-test-token-with-32-characters")
    )


@pytest.fixture
def uk():
    path = Path(__file__).resolve().parents[2] / "docs/examples/uk-extract.synthetic.json"
    return Scan.model_validate_json(path.read_text())


@pytest.fixture
def definitions():
    return {
        name: Definition(
            Profile(
                id=name,
                version="1",
                method="synthetic_fixture",
                component_ids=["fixture@1"],
                enabled=True,
                configured=True,
            ),
            adapter=name,
            synthetic=True,
        )
        for name in ("success", "failure")
    }


@pytest.fixture
def adapters(uk):
    return {
        "success": FixtureAdapter(
            lambda: (
                uk.runs[0].payment.model_copy(deep=True),
                [e.model_copy(deep=True) for e in uk.runs[0].evidence],
            )
        ),
        "failure": FixtureAdapter(failure="provider_refusal"),
    }


def upload(client, png, key="test", mode="extract", profiles=None, **options):
    return client.post(
        "/v1/scans",
        headers={"Idempotency-Key": key},
        files={"image": ("photo.png", png, "image/png")},
        data={
            "options": json.dumps({"mode": mode, "profiles": profiles or ["success"], **options})
        },
    )
