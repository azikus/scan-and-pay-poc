from types import SimpleNamespace

import boto3
import google.auth
import pytest
from botocore.credentials import Credentials
from botocore.exceptions import ProfileNotFound
from google.auth.exceptions import DefaultCredentialsError

from backend.adapters.cloud_auth import aws_headers, google_headers
from backend.errors import ProviderError


def test_aws_signs_exact_payload_with_temporary_credentials(monkeypatch):
    seen = {}

    def session(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(
            get_credentials=lambda: Credentials(
                "synthetic-id", "synthetic-secret", "synthetic-session"
            )
        )

    monkeypatch.setattr(boto3, "Session", session)
    a = aws_headers(
        "test-profile",
        "eu-central-1",
        "textract.eu-central-1.amazonaws.com",
        '{"Document":{}}',
        "AnalyzeExpense",
    )
    b = aws_headers(
        "test-profile",
        "eu-central-1",
        "textract.eu-central-1.amazonaws.com",
        '{"Document":{"Bytes":"changed"}}',
        "AnalyzeExpense",
    )
    assert seen == {"profile_name": "test-profile", "region_name": "eu-central-1"}
    assert a["X-Amz-Security-Token"] == "synthetic-session"
    assert a["Authorization"] != b["Authorization"]
    assert a["X-Amz-Target"] == "Textract.AnalyzeExpense"


@pytest.mark.parametrize("missing", [True, False])
def test_aws_missing_or_expired_credentials_redacted(monkeypatch, missing):
    def session(**kwargs):
        if missing:
            return SimpleNamespace(get_credentials=lambda: None)
        raise ProfileNotFound(profile="PRIVATE")

    monkeypatch.setattr(boto3, "Session", session)
    with pytest.raises(ProviderError) as error:
        aws_headers(
            "test",
            "eu-central-1",
            "textract.eu-central-1.amazonaws.com",
            "{}",
            "DetectDocumentText",
        )
    assert error.value.code == "provider_auth"
    assert "PRIVATE" not in str(error.value)


def test_google_refreshes_sdk_credentials_with_quota_project(monkeypatch):
    calls = []
    credentials = SimpleNamespace(
        token="synthetic-token", refresh=lambda request: calls.append("refresh")
    )

    def default(**kwargs):
        calls.append(kwargs)
        return credentials, None

    monkeypatch.setattr(google.auth, "default", default)
    headers = google_headers("synthetic-project")
    assert calls == [
        {
            "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
            "quota_project_id": "synthetic-project",
        },
        "refresh",
    ]
    assert headers == {
        "Authorization": "Bearer synthetic-token",
        "x-goog-user-project": "synthetic-project",
    }


def test_google_missing_credentials_redacted(monkeypatch):
    def fail(**kwargs):
        raise DefaultCredentialsError("PRIVATE")

    monkeypatch.setattr(google.auth, "default", fail)
    with pytest.raises(ProviderError) as error:
        google_headers("synthetic-project")
    assert error.value.code == "provider_auth"
