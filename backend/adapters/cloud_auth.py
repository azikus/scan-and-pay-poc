"""Explicit env credentials with legacy SDK fallback; HTTPX inference stays unchanged."""

import asyncio
import json
from typing import Any

from backend.config import ModelOption, Settings
from backend.errors import ProviderError


def google_headers(project: str, credentials_json: str = "") -> dict[str, str]:
    import google.auth
    from google.auth.transport.requests import Request

    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        if credentials_json:
            from google.oauth2 import credentials as user_credentials
            from google.oauth2 import service_account

            info = json.loads(credentials_json)
            if not isinstance(info, dict):
                raise ValueError("Invalid credential object")
            if info.get("type") == "authorized_user":
                credentials = user_credentials.Credentials.from_authorized_user_info(  # type: ignore[no-untyped-call]
                    info, scopes=scopes
                ).with_quota_project(project)
            elif info.get("type") == "service_account":
                if info.get("token_uri") not in {
                    "https://oauth2.googleapis.com/token",
                    "https://accounts.google.com/o/oauth2/token",
                }:
                    raise ValueError("Unsupported OAuth endpoint")
                credentials = service_account.Credentials.from_service_account_info(  # type: ignore[no-untyped-call]
                    info, scopes=scopes
                ).with_quota_project(project)
            else:
                raise ValueError("Unsupported credential type")
        else:
            credentials, _ = google.auth.default(scopes=scopes, quota_project_id=project)
        credentials.refresh(Request())
        return {"Authorization": "Bearer " + str(credentials.token), "x-goog-user-project": project}
    except (google.auth.exceptions.GoogleAuthError, ValueError, TypeError, KeyError):
        raise ProviderError("provider_auth") from None


def aws_headers(
    profile: str,
    region: str,
    host: str,
    payload: str,
    operation: str,
    *,
    access_key_id: str = "",
    secret_access_key: str = "",
    session_token: str = "",
) -> dict[str, str]:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials
    from botocore.exceptions import BotoCoreError

    try:
        if access_key_id or secret_access_key or session_token:
            if not access_key_id or not secret_access_key:
                raise ProviderError("provider_auth")
            credentials = Credentials(access_key_id, secret_access_key, session_token or None)
        else:
            credentials = boto3.Session(profile_name=profile, region_name=region).get_credentials()
        if credentials is None:
            raise ProviderError("provider_auth")
        req = AWSRequest(
            method="POST",
            url=f"https://{host}/",
            data=payload,
            headers={
                "Content-Type": "application/x-amz-json-1.1",
                "X-Amz-Target": "Textract." + operation,
            },
        )
        SigV4Auth(credentials.get_frozen_credentials(), "textract", region).add_auth(req)
        return dict(req.headers.items())
    except BotoCoreError:
        raise ProviderError("provider_auth") from None


async def cloud_request(
    option: ModelOption, settings: Settings, request: Any, encoded: str
) -> dict[str, Any]:
    from backend.adapters.documents import resource

    assert option.config is not None
    if option.provider == "google_documentai":
        project = resource(settings, "GOOGLE_CLOUD_PROJECT")
        location = resource(settings, "GOOGLE_DOCUMENTAI_LOCATION")
        processor = resource(
            settings,
            "GOOGLE_DOCUMENTAI_"
            + ("OCR" if option.operation == "ocr" else "INVOICE")
            + "_PROCESSOR_ID",
        )
        if option.config.endpoint_host != f"{location}-documentai.googleapis.com":
            raise ProviderError("provider_auth")
        headers = await asyncio.to_thread(
            google_headers, project, settings.google_credentials_json.get_secret_value()
        )
        path = f"/v1/projects/{project}/locations/{location}/processors/{processor}/processorVersions/{option.model}:process"
        body, _ = await request(
            "POST",
            path,
            headers=headers,
            json={
                "rawDocument": {"content": encoded, "mimeType": "image/png"},
                "skipHumanReview": True,
            },
        )
    else:
        region = resource(settings, "AWS_REGION")
        if option.config.endpoint_host != f"textract.{region}.amazonaws.com":
            raise ProviderError("provider_auth")
        operation = "DetectDocumentText" if option.operation == "ocr" else "AnalyzeExpense"
        payload = json.dumps({"Document": {"Bytes": encoded}})
        headers = await asyncio.to_thread(
            aws_headers,
            settings.resources.get("AWS_PROFILE", ""),
            region,
            option.config.endpoint_host,
            payload,
            operation,
            access_key_id=settings.aws_access_key_id.get_secret_value(),
            secret_access_key=settings.aws_secret_access_key.get_secret_value(),
            session_token=settings.aws_session_token.get_secret_value(),
        )
        body, _ = await request("POST", "/", headers=headers, content=payload)
    return dict(body)
