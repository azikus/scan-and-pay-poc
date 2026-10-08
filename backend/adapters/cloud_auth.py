"""SDK-managed credentials with HTTPX inference, no credential-store duplication."""

import asyncio
import json
from typing import Any

from backend.config import ModelOption, Settings
from backend.errors import ProviderError


def google_headers(project: str) -> dict[str, str]:
    import google.auth
    from google.auth.transport.requests import Request

    try:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"], quota_project_id=project
        )
        credentials.refresh(Request())  # type: ignore[no-untyped-call]
        return {"Authorization": "Bearer " + str(credentials.token), "x-goog-user-project": project}
    except google.auth.exceptions.GoogleAuthError:
        raise ProviderError("provider_auth") from None


def aws_headers(
    profile: str, region: str, host: str, payload: str, operation: str
) -> dict[str, str]:
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.exceptions import BotoCoreError

    try:
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
        headers = await asyncio.to_thread(google_headers, project)
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
            resource(settings, "AWS_PROFILE"),
            region,
            option.config.endpoint_host,
            payload,
            operation,
        )
        body, _ = await request("POST", "/", headers=headers, content=payload)
    return dict(body)
