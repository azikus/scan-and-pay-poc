"""Managed document protocols and explicit vendor field mappings."""

import asyncio
import re
from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

import httpx

from backend.adapters.mapping import map_fields
from backend.adapters.vision import claims
from backend.config import ModelOption, Settings
from backend.document_observations import observe
from backend.errors import ProviderError
from backend.images import sha256
from backend.models import Cost, Payment, Routing, Stage
from backend.ocr_rules import extract_rules
from backend.providers import PROMPT, structured_schema
from backend.runtime import Context, Extraction
from backend.store import private_write

Request = Callable[..., Awaitable[tuple[dict[str, Any], httpx.Response]]]


def resource(settings: Settings, name: str) -> str:
    value = settings.resources.get(name, "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ProviderError("provider_auth")
    return value


async def document_request(
    option: ModelOption, settings: Settings, request: Request, encoded: str, data: bytes, key: str
) -> dict[str, Any]:
    from backend.adapters.extended import checked_url

    provider, op = option.provider, option.operation
    assert option.config is not None
    host = option.config.endpoint_host
    if provider == "mistral":
        payload: dict[str, Any] = {
            "model": option.model,
            "document": {"type": "image_url", "image_url": "data:image/png;base64," + encoded},
            "include_image_base64": False,
        }
        if op == "annotations":
            annotation_schema, annotation_prompt = structured_schema(), PROMPT
            if option.protocol_version in {"4", "5", "6"}:
                from backend.adapters.compact import PROMPT as compact_prompt
                from backend.adapters.compact import schema

                annotation_schema, annotation_prompt = (
                    schema(option.protocol_version),
                    compact_prompt,
                )
                if option.protocol_version in {"5", "6"}:
                    from backend.adapters.compact import PROMPT_V5

                    annotation_prompt = PROMPT_V5
            if option.interpretation_policy == "draft_v1":
                from backend.draft_policy import prompt_v1

                annotation_prompt = prompt_v1(annotation_prompt)
            elif option.interpretation_policy == "draft_v2":
                from backend.recipient_roles import prompt_v2, role_schema

                annotation_prompt = prompt_v2(annotation_prompt)
                annotation_schema = role_schema(annotation_schema)
            elif option.interpretation_policy == "draft_v3":
                from backend.recipient_roles import prompt_v2, role_schema_v2

                annotation_prompt = prompt_v2(annotation_prompt)
                annotation_schema = role_schema_v2(annotation_schema)
            elif option.interpretation_policy == "draft_v4":
                from backend.recipient_roles import prompt_v3, role_schema_v2

                annotation_prompt = prompt_v3(annotation_prompt)
                annotation_schema = role_schema_v2(annotation_schema)
            if option.context_policy in {"invoice_v1", "invoice_v2", "invoice_v3", "invoice_v4"}:
                from backend.invoice_context import context_prompt, context_schema

                annotation_prompt = context_prompt(annotation_prompt, policy=option.context_policy)
                annotation_schema = context_schema(annotation_schema, policy=option.context_policy)
            payload["document_annotation_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "payment_extraction",
                    "strict": True,
                    "schema": annotation_schema,
                },
            }
            payload["document_annotation_prompt"] = annotation_prompt
        body, _ = await request(
            "POST", "/v1/ocr", headers={"Authorization": "Bearer " + key}, json=payload
        )
        return body
    if provider == "azure":
        headers = {"Ocp-Apim-Subscription-Key": key}
        body, response = await request(
            "POST",
            f"/documentintelligence/documentModels/{option.model}:analyze?api-version=2024-11-30",
            headers=headers,
            json={"base64Source": encoded},
        )
        poll = checked_url(
            response.headers["operation-location"],
            host,
            r"/documentintelligence/documentModels/[A-Za-z0-9_.-]+/analyzeResults/[A-Za-z0-9-]+",
        )
        for _ in range(40):
            if option.poll_interval_seconds > 1:
                await asyncio.sleep(option.poll_interval_seconds)
            body, _ = await request("GET", poll, headers=headers)
            if body["status"] == "succeeded":
                return body
            if body["status"] not in {"notStarted", "running"}:
                raise ProviderError("provider_unavailable")
            if option.poll_interval_seconds == 1:
                await asyncio.sleep(1)
        raise ProviderError("provider_timeout")
    if provider == "mindee":
        headers = {"Authorization": key}
        body, _ = await request(
            "POST",
            "/v2/inferences/enqueue",
            headers=headers,
            data={"model_id": resource(settings, "MINDEE_MODEL_ID"), "rag": "false"},
            files={"file": ("image.png", data, "image/png")},
        )
        for _ in range(40):
            job = body["job"]
            if job["status"] == "Processed":
                url = checked_url(
                    job["result_url"],
                    host,
                    r"/v2/(?:inferences|products/extraction/results)/[A-Za-z0-9-]+",
                )
                body, _ = await request("GET", url, headers=headers)
                return body
            if job["status"] not in {"Processing", "Waiting"}:
                raise ProviderError("provider_unavailable")
            url = checked_url(job["polling_url"], host, r"/v2/jobs/[A-Za-z0-9-]+")
            await asyncio.sleep(1)
            body, _ = await request("GET", url, headers=headers, params={"redirect": "false"})
        raise ProviderError("provider_timeout")
    from backend.adapters.cloud_auth import cloud_request

    return await cloud_request(option, settings, request, encoded)


def document_extraction(
    body: dict[str, Any],
    option: ModelOption,
    context: Context,
    stage: Stage,
    *,
    recognition_only: bool = False,
) -> Extraction:
    provider = option.provider
    if provider == "mistral":
        model = body.get("model")
        if model is not None and not (
            model == option.model or model.startswith(option.model + "-")
        ):
            raise ProviderError("invalid_provider_output")
        context.run.diagnostics.returned_model = model
        if option.operation == "annotations":
            if option.context_policy in {"invoice_v1", "invoice_v2", "invoice_v3", "invoice_v4"}:
                from backend.invoice_context import extract_context

                return extract_context(
                    body["document_annotation"],
                    context.scan.input.image_id,
                    stage.id,
                    version=option.protocol_version,
                    policy=option.context_policy,
                )
            if option.protocol_version in {"4", "5", "6"}:
                from backend.adapters.compact import extract

                if option.field_policy == "partial_v1":
                    from backend.adapters.partial import recover

                    return recover(
                        body["document_annotation"],
                        context.scan.input.image_id,
                        stage.id,
                        version=option.protocol_version,
                    )

                return extract(
                    body["document_annotation"],
                    context.scan.input.image_id,
                    stage.id,
                    version=option.protocol_version,
                )
            return claims(body["document_annotation"], context, stage.id)
        (page,) = body["pages"]
        text = page["markdown"]
    elif provider == "azure":
        result = body["analyzeResult"]
        context.run.diagnostics.returned_model = result.get("modelId")
        if result.get("modelId") not in {None, option.model}:
            raise ProviderError("invalid_provider_output")
        text = result["content"]
    elif provider == "google_documentai":
        text = body["document"]["text"]
    elif provider == "aws":
        blocks = body["Blocks"] if option.operation == "ocr" else []
        if not isinstance(blocks, list):
            raise ProviderError("invalid_provider_output")
        text = "\n".join(b["Text"] for b in blocks if b.get("BlockType") == "LINE")
        context.run.diagnostics.returned_model = body.get(
            "AnalyzeExpenseModelVersion", body.get("DetectDocumentTextModelVersion")
        )
    else:
        text = ""
    stage.returned_model = context.run.diagnostics.returned_model
    document = observe(body, provider, text, context.scan.input.image_id, stage.id)
    private_write(
        context.store.artifacts
        / context.scan.scan_id
        / f"{context.run.id}.{stage.id}.document.json",
        document.to_json().encode(),
    )
    if option.operation == "ocr":
        if recognition_only:
            return Extraction(Payment(), [], Routing())
        text = document.text
        if not isinstance(text, str):
            raise ProviderError("invalid_provider_output")
        rules = context.stage(
            "rules",
            external=False,
            payloads=["ocr_text", "layout"],
            input_hash=sha256(text.encode()),
        )
        start = monotonic()
        # A separate parser revision never rewrites historical results.
        if option.rules_version == "3":
            from backend.ocr_rules_v3 import extract_rules_v3

            result_tuple = extract_rules_v3(document)
        elif option.rules_version == "2":
            from backend.ocr_rules_v2 import extract_rules_v2

            result_tuple = extract_rules_v2(text, context.scan.input.image_id, stage.id)
        else:
            result_tuple = extract_rules(text, context.scan.input.image_id, stage.id)
        rules.duration_ms = (monotonic() - start) * 1000
        rules.cost = Cost(status="not_applicable")
        return Extraction(*result_tuple)
    fields = vendor_fields(body, provider)
    return map_fields(fields, context.scan.input.image_id, stage.id, version=option.mapping_version)


# Maps only actual product fields. Unsupported payment details are not filled from OCR.
MAPS = {
    "azure": {
        "VendorName": "supplier_name",
        "InvoiceId": "invoice_number",
        "CustomerId": "customer_number",
        "DueDate": "due_date",
        "AmountDue": "amount_due",
        "InvoiceTotal": "invoice_total",
        "IBAN": "iban",
        "SWIFT": "bic",
        "BankAccountNumber": "account_number",
    },
    "google_documentai": {
        "supplier_name": "supplier_name",
        "invoice_id": "invoice_number",
        "due_date": "due_date",
        "total_amount": "invoice_total",
        "currency": "currency",
        "supplier_iban": "iban",
        "supplier_payment_ref": "reference",
    },
    "aws": {
        "VENDOR_NAME": "supplier_name",
        "INVOICE_RECEIPT_ID": "invoice_number",
        "DUE_DATE": "due_date",
        "TOTAL": "invoice_total",
        "AMOUNT_DUE": "amount_due",
    },
    "mindee": {
        "supplier_name": "supplier_name",
        "invoice_number": "invoice_number",
        "total_amount": "invoice_total",
        "currency": "currency",
        "due_date": "due_date",
        "iban": "iban",
        "swift": "bic",
        "customer_id": "customer_number",
    },
}


def vendor_fields(body: dict[str, Any], provider: str) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}

    def add(name: str, value: Any) -> None:
        if name in MAPS[provider] and value is not None:
            if not isinstance(value, str):
                # Numeric provider values cannot safely represent account numbers or references.
                if MAPS[provider][name] not in {"amount_due", "invoice_total"} or type(
                    value
                ) not in {float, int}:
                    raise ProviderError("invalid_provider_output")
                value = str(value)
            fields.setdefault(MAPS[provider][name], []).append(value)

    if provider == "azure":
        if len(body["analyzeResult"]["documents"]) > 1:
            raise ProviderError("invalid_provider_output")
        for doc in body["analyzeResult"]["documents"]:
            for name, field in doc["fields"].items():
                if name == "PaymentDetails":
                    for item in field.get("valueArray", []):
                        for child, value in item["valueObject"].items():
                            add(child, value.get("content"))
                else:
                    add(name, field.get("content"))
                    code = field.get("valueCurrency", {}).get("currencyCode")
                    if code:
                        fields.setdefault("currency", []).append(code)
    elif provider == "google_documentai":
        for entity in body["document"].get("entities", []):
            add(entity["type"], entity.get("mentionText"))
    elif provider == "aws":
        if len(body["ExpenseDocuments"]) > 1:
            raise ProviderError("invalid_provider_output")
        for doc in body["ExpenseDocuments"]:
            for field in doc["SummaryFields"]:
                add(field["Type"]["Text"], field.get("ValueDetection", {}).get("Text"))
                if field["Type"]["Text"] in {"TOTAL", "AMOUNT_DUE"} and field.get(
                    "Currency", {}
                ).get("Code"):
                    fields.setdefault("currency", []).append(field["Currency"]["Code"])
    elif provider == "mindee":
        for name, field in body["inference"]["result"]["fields"].items():
            if name == "locale":
                add("currency", field.get("fields", {}).get("currency", {}).get("value"))
            elif name == "supplier_payment_details":
                items = field.get("items", [])
                if len(items) > 1:
                    raise ProviderError("invalid_provider_output")
                for item in items:
                    for child in ("iban", "swift"):
                        add(child, item["fields"].get(child, {}).get("value"))
            else:
                add(name, field.get("value"))
    return fields
