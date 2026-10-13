"""Inline cloud credentials are redacted and never fall back after explicit failure."""

import json
from types import SimpleNamespace

import boto3
import google.auth
import pytest
from google.oauth2 import credentials as user_credentials
from google.oauth2 import service_account
from pydantic import SecretStr

from backend.adapters.cloud_auth import aws_headers, cloud_request, google_headers
from backend.config import ModelOption, Settings
from backend.errors import ProviderError
from backend.profiles import registry


def no_store(*args, **kwargs):
    raise AssertionError("Explicit credentials must not read native credential stores")


@pytest.mark.parametrize("token", ["", "synthetic-session"])
def test_aws_explicit_keys_sign_without_profile_lookup(monkeypatch, token):
    monkeypatch.setattr(boto3, "Session", no_store)
    headers = aws_headers(
        "ignored-profile",
        "eu-central-1",
        "textract.eu-central-1.amazonaws.com",
        '{"Document":{}}',
        "AnalyzeExpense",
        access_key_id="synthetic-id",
        secret_access_key="synthetic-secret",
        session_token=token,
    )
    assert "Credential=synthetic-id/" in headers["Authorization"]
    assert headers.get("X-Amz-Security-Token", "") == token


@pytest.mark.parametrize("keys", [("id", "", ""), ("", "secret", ""), ("", "", "token")])
def test_aws_partial_inline_credentials_fail_without_fallback(monkeypatch, keys):
    monkeypatch.setattr(boto3, "Session", no_store)
    with pytest.raises(ProviderError) as error:
        aws_headers(
            "ignored",
            "eu-central-1",
            "textract.eu-central-1.amazonaws.com",
            "{}",
            "AnalyzeExpense",
            access_key_id=keys[0],
            secret_access_key=keys[1],
            session_token=keys[2],
        )
    assert error.value.code == "provider_auth"


@pytest.mark.parametrize("kind", ["authorized_user", "service_account"])
def test_google_explicit_json_uses_typed_loader_and_quota_project(monkeypatch, kind):
    calls = []
    credential = SimpleNamespace(
        token="synthetic-token",
        refresh=lambda request: calls.append("refresh"),
    )
    credential.with_quota_project = lambda project: calls.append(project) or credential

    def load(info, scopes):
        assert info["type"] == kind
        assert scopes == ["https://www.googleapis.com/auth/cloud-platform"]
        calls.append("load")
        return credential

    monkeypatch.setattr(google.auth, "default", no_store)
    target = (
        user_credentials.Credentials if kind == "authorized_user" else service_account.Credentials
    )
    method = (
        "from_authorized_user_info" if kind == "authorized_user" else "from_service_account_info"
    )
    monkeypatch.setattr(target, method, load)
    info = {"type": kind, "token_uri": "https://oauth2.googleapis.com/token"}
    assert google_headers("test-project", json.dumps(info)) == {
        "Authorization": "Bearer synthetic-token",
        "x-goog-user-project": "test-project",
    }
    assert calls == ["load", "test-project", "refresh"]


@pytest.mark.parametrize(
    "info",
    [
        "PRIVATE-bad-json",
        "[]",
        '{"type":"external_account"}',
        '{"type":"service_account","token_uri":"https://evil.example"}',
        '{"type":"authorized_user"}',
    ],
)
def test_google_invalid_explicit_credentials_redacted_without_fallback(monkeypatch, info):
    monkeypatch.setattr(google.auth, "default", no_store)
    with pytest.raises(ProviderError) as error:
        google_headers("test-project", info)
    assert error.value.code == "provider_auth" and "PRIVATE" not in str(error.value)


def test_aws_readiness_requires_pair_but_not_profile(settings):
    option = ModelOption(provider="aws", model="AnalyzeExpense", operation="invoice")
    option.config.enabled = True
    option.config.endpoint_host = "textract.eu-central-1.amazonaws.com"
    option.config.account_access_checked_at = option.config.data_terms_checked_at = "2026-10-13"
    option.config.data_terms_note = "Synthetic account approval"
    settings.providers.options["aws"] = option
    settings.resources["AWS_REGION"] = "eu-central-1"
    settings.aws_access_key_id = SecretStr("synthetic-id")
    assert "AWS_SECRET_ACCESS_KEY" in registry(settings)["aws"].metadata.unavailable_reason
    settings.aws_secret_access_key = SecretStr("synthetic-secret")
    assert registry(settings)["aws"].metadata.configured
    assert "synthetic-secret" not in json.dumps(registry(settings)["aws"].snapshot())


def test_env_credentials_are_loaded_and_secret_redacted(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SCANPAY_TOKEN", "synthetic-token-long-enough-for-auth")
    monkeypatch.setenv("SCANPAY_PROFILES_FILE", str(tmp_path / "missing.json"))
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "PRIVATE-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "PRIVATE-secret")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "PRIVATE-session")
    monkeypatch.setenv(
        "GOOGLE_CREDENTIALS_JSON", '{"type":"authorized_user","refresh_token":"PRIVATE-refresh"}'
    )
    loaded = Settings.from_env()
    assert loaded.aws_access_key_id.get_secret_value() == "PRIVATE-id"
    assert loaded.aws_secret_access_key.get_secret_value() == "PRIVATE-secret"
    assert loaded.aws_session_token.get_secret_value() == "PRIVATE-session"
    assert "PRIVATE-refresh" in loaded.google_credentials_json.get_secret_value()
    assert "PRIVATE-" not in loaded.model_dump_json()


@pytest.mark.asyncio
async def test_cloud_request_passes_inline_credentials_without_aws_profile(settings, monkeypatch):
    seen = {}
    option = ModelOption(
        provider="aws",
        model="AnalyzeExpense",
        operation="invoice",
        config={"endpoint_host": "textract.eu-central-1.amazonaws.com"},
    )
    settings.resources["AWS_REGION"] = "eu-central-1"
    settings.aws_access_key_id = SecretStr("synthetic-id")
    settings.aws_secret_access_key = SecretStr("synthetic-secret")

    def headers(*args, **kwargs):
        seen.update(kwargs)
        assert args[0] == ""
        return {"Authorization": "synthetic"}

    async def request(method, path, **kwargs):
        assert method == "POST" and path == "/"
        return {}, None

    monkeypatch.setattr("backend.adapters.cloud_auth.aws_headers", headers)
    await cloud_request(option, settings, request, "synthetic-image")
    assert seen == {
        "access_key_id": "synthetic-id",
        "secret_access_key": "synthetic-secret",
        "session_token": "",
    }
