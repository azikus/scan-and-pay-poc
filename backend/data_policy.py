"""Mandatory European content processing and no-training gate; no global fallback.

Transport checks constrain our routing. Private, dated operator evidence establishes
account/model eligibility and contractual controls; this is not remote attestation.
"""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from backend.config import ProviderConfig
from backend.errors import ProviderError

if TYPE_CHECKING:
    from backend.profiles import Definition

POLICY = "europe-no-training@1"
# Europe here means EEA + Switzerland, not EU member states only.
EUROPEAN_ENDPOINTS = {
    "openai": "eu.api.openai.com",
    "mistral": "api.eu.mistral.ai",
    "google_documentai": "eu-documentai.googleapis.com",
}


def violations(
    provider: str | None,
    model: str | None,
    operation: str,
    config: ProviderConfig | None,
    payloads: list[str],
    *,
    today: date | None = None,
) -> list[str]:
    """Unknown, stale, mismatched or unsupported configurations fail closed."""
    if config is None:
        return ["Missing provider data approval"]
    expected = EUROPEAN_ENDPOINTS.get(provider or "")
    if expected is None or config.endpoint_host != expected:
        return ["European processing route is not approved"]
    approval = config.data_approval
    if approval is None:
        return ["Missing European processing and no-training evidence"]
    current = today or datetime.now(UTC).date()
    failures = []
    if not approval.checked_at <= current <= approval.expires_at:
        failures.append("Data approval is expired or not yet valid")
    if (
        approval.account_alias != config.account_alias
        or approval.endpoint_host != config.endpoint_host
        or approval.model != model
        or approval.operation != operation
    ):
        failures.append("Data approval does not match account, endpoint, model and operation")
    if config.verified_processing_region != approval.processing_boundary:
        failures.append("Verified processing boundary does not match data approval")
    if not set(payloads).issubset(approval.payload_classes):
        failures.append("Data approval does not cover the outbound content")
    if not approval.no_training:
        failures.append("No-training terms or account opt-out are not verified")
    if provider == "openai" and "image" in payloads and not approval.image_processing_approved:
        failures.append("OpenAI European image processing approval is not verified")
    return failures


def definition_violations(definition: "Definition", payloads: list[str] | None = None) -> list[str]:
    if definition.stages:
        failures = []
        for index, stage in enumerate(definition.stages):
            failures.extend(
                definition_violations(stage, ["image"] if index == 0 else ["ocr_text", "layout"])
            )
        return list(dict.fromkeys(failures))
    if definition.synthetic:
        # Synthetic fixtures may run local rules, never external processing.
        return [] if payloads is None else ["Synthetic fixtures cannot dispatch externally"]
    operation = str(
        definition.parameters.get("operation", "ocr" if definition.metadata.processor else "vision")
    )
    return violations(
        definition.metadata.provider,
        definition.metadata.model or definition.metadata.processor,
        operation,
        definition.config,
        payloads if payloads is not None else ["image"],
    )


def require_definition(definition: "Definition", payloads: list[str] | None = None) -> None:
    if definition_violations(definition, payloads):
        raise ProviderError("data_policy_blocked")


def require_destination(
    url: str,
    provider: str,
    model: str,
    operation: str,
    config: ProviderConfig,
    payloads: list[str],
) -> None:
    parts = urlsplit(url)
    if (
        parts.scheme != "https"
        or parts.netloc != config.endpoint_host
        or parts.fragment
        or violations(provider, model, operation, config, payloads)
    ):
        raise ProviderError("data_policy_blocked")
