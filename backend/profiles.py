import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from backend.config import ModelOption, ProviderConfig, Settings, option_resources
from backend.errors import ServiceError
from backend.images import PreparedImage
from backend.models import ExcludedProfile, Model, Options, Text


class DestinationMetadata(Model):
    method: Text
    execution: Literal["local", "external"]
    provider: Text | None = None
    endpoint_host: Text | None = None
    payload_classes: list[str]


class Profile(Model):
    id: Text
    version: Text
    method: Text
    component_ids: list[Text]
    provider: Text | None = None
    model: Text | None = None
    processor: Text | None = None
    supported_image_types: list[str] = ["image/jpeg", "image/png"]
    known_languages: list[str] = []
    stage_destinations: list[DestinationMetadata] = []
    implemented: bool = True
    enabled: bool = False
    configured: bool = False
    live_validated: bool = False
    unavailable_reason: str | None = None


class ProfilesResponse(Model):
    server_id: str | None = None
    profiles: list[Profile]
    default_extract_profile_id: str | None = None
    default_extract_profile_version: str | None = None


@dataclass(frozen=True)
class Definition:
    metadata: Profile
    adapter: str
    config: ProviderConfig | None = None
    ceiling_eur: Decimal = Decimal("0")
    synthetic: bool = False
    parameters: dict[str, str | int] = field(default_factory=dict)

    stages: tuple["Definition", ...] = ()

    @property
    def reservations(self) -> tuple[Decimal, ...]:
        return tuple(s.ceiling_eur for s in self.stages) if self.stages else (self.ceiling_eur,)

    def snapshot(self) -> dict[str, object]:
        return {
            "profile": self.metadata.model_dump(),
            "adapter": self.adapter,
            "config": self.config.model_dump(mode="json") if self.config else None,
            "ceiling_eur": str(self.ceiling_eur),
            "synthetic": self.synthetic,
            "parameters": self.parameters,
            **({"stages": [s.snapshot() for s in self.stages]} if self.stages else {}),
        }


def registry(settings: Settings) -> dict[str, Definition]:
    definitions = {}
    for provider, profile_id, adapter, model, components in (
        (
            "openai",
            "openai-luna-vision",
            "openai",
            "gpt-6-luna",
            ["openai-responses@1", "review@2"],
        ),
        (
            "mistral",
            "mistral-ocr-rules",
            "mistral",
            "mistral-ocr-4-1",
            ["mistral-ocr@1", "label-rules@1", "review@2"],
        ),
    ):
        config: ProviderConfig = getattr(settings.providers, provider)
        key = getattr(settings, provider + "_key").get_secret_value()
        missing = []
        if not key:
            missing.append("local API key")
        for name in (
            "account_access_checked_at",
            "data_terms_checked_at",
            "data_terms_note",
        ):
            if getattr(config, name) is None:
                missing.append(name)
        parameters: dict[str, str | int] = {
            "attempts": 1,
            "stage_timeout_seconds": 90,
            "job_deadline_seconds": 240,
            "review": "2",
        }
        if provider == "openai":
            parameters.update(
                {
                    "max_output_tokens": 12000,
                    "reasoning": "none",
                    "detail": "high",
                    "prompt": "payment-image@2",
                    "service_tier": "default",
                    "pricing": "luna-cache-writes@2",
                }
            )
        version_data = {
            "model": model,
            "components": components,
            "config": config.model_dump(mode="json"),
            "parameters": parameters,
        }
        version = (
            "1-"
            + hashlib.sha256(json.dumps(version_data, sort_keys=True).encode()).hexdigest()[:16]
        )
        destinations = [
            DestinationMetadata(
                method="vision" if provider == "openai" else "ocr",
                execution="external",
                provider=provider,
                endpoint_host=config.endpoint_host,
                payload_classes=["image"],
            )
        ]
        if provider == "mistral":
            destinations.append(
                DestinationMetadata(
                    method="rules", execution="local", payload_classes=["ocr_text", "layout"]
                )
            )
        meta = Profile(
            id=profile_id,
            version=version,
            method="direct_vision" if provider == "openai" else "managed_ocr_rules",
            component_ids=components,
            provider=provider,
            model=model if provider == "openai" else None,
            processor=model if provider == "mistral" else None,
            known_languages=[],
            stage_destinations=destinations,
            enabled=config.enabled,
            configured=not missing,
            unavailable_reason="Missing " + ", ".join(missing)
            if missing
            else "Disabled by operator"
            if not config.enabled
            else None,
        )
        definitions[profile_id] = Definition(
            meta, adapter, config, config.max_call_eur or Decimal("0"), parameters=parameters
        )
    for profile_id, option in settings.providers.options.items():
        assert option.config is not None
        config = option.config
        missing = []
        key = (
            getattr(settings, option.provider + "_key").get_secret_value()
            if option.provider in {"openai", "mistral"}
            else settings.provider_keys.get(option.provider)
        )
        if option.provider not in {"aws", "google_documentai"} and not key:
            missing.append("local API key")
        for name in (
            "account_access_checked_at",
            "data_terms_checked_at",
            "data_terms_note",
        ):
            if getattr(config, name) is None:
                missing.append(name)
        if config.endpoint_host == "unconfigured.invalid":
            missing.append("cloud endpoint")
        resources = {
            name: settings.resources.get(name, "")
            for name in option_resources(option.provider, option.operation)
        }
        explicit_aws = option.provider == "aws" and any(
            value.get_secret_value()
            for value in (
                settings.aws_access_key_id,
                settings.aws_secret_access_key,
                settings.aws_session_token,
            )
        )
        missing.extend(
            name
            for name, value in resources.items()
            if not value and not (explicit_aws and name == "AWS_PROFILE")
        )
        if explicit_aws:
            if not settings.aws_access_key_id.get_secret_value():
                missing.append("AWS_ACCESS_KEY_ID")
            if not settings.aws_secret_access_key.get_secret_value():
                missing.append("AWS_SECRET_ACCESS_KEY")
        resource_hash = hashlib.sha256(json.dumps(resources, sort_keys=True).encode()).hexdigest()
        parameters = {
            "attempts": 1,
            "stage_timeout_seconds": 90,
            "review": "2",
            "operation": option.operation,
            "max_output_tokens": option.max_output_tokens,
            "prompt": "payment-image@" + option.protocol_version
            if option.protocol_version in {"3", "4", "5", "6"}
            else "payment-image@2",
            "rules": option.rules_version,
            "option": option.snapshot_json(),
            "resource_sha256": resource_hash,
        }
        version = (
            "2-"
            + hashlib.sha256((option.snapshot_json() + resource_hash).encode()).hexdigest()[:16]
        )
        method = {
            "vision": "direct_vision",
            "ocr": "managed_ocr_rules",
            "invoice": "prebuilt_document_mapping",
            "custom": "custom_document_mapping",
            "annotations": "document_annotations",
        }[option.operation]
        destinations = [
            DestinationMetadata(
                method=option.operation,
                execution="external",
                provider=option.provider,
                endpoint_host=config.endpoint_host,
                payload_classes=["image"],
            )
        ]
        if option.operation == "ocr":
            destinations.append(
                DestinationMetadata(
                    method="rules", execution="local", payload_classes=["ocr_text", "layout"]
                )
            )
        components = [f"{option.provider}-{option.operation}@{option.protocol_version}", "review@2"]
        if option.interpretation_policy in {"draft_v1", "draft_v2", "draft_v3", "draft_v4"}:
            components.append("payment-draft@1")
            parameters["interpretation_policy"] = option.interpretation_policy
            if option.operation in {"vision", "annotations"}:
                parameters["prompt"] = str(parameters["prompt"]) + "+draft@1"
            if option.interpretation_policy == "draft_v2":
                components.append("payment-party-roles@1")
                parameters["prompt"] = str(parameters["prompt"]) + "+party-roles@1"
            elif option.interpretation_policy == "draft_v3":
                components.append("payment-party-roles@2")
                parameters["prompt"] = str(parameters["prompt"]) + "+party-roles@2"
            elif option.interpretation_policy == "draft_v4":
                components.append("payment-party-roles@3")
                parameters["prompt"] = str(parameters["prompt"]) + "+party-roles@3"
        if option.field_policy == "partial_v1":
            components.append("partial-fields@1")
            parameters["field_policy"] = "partial_v1"
        if option.context_policy == "invoice_v1":
            components.append("invoice-context@1")
            parameters["prompt"] = str(parameters["prompt"]) + "+invoice-context@1"
        if option.operation == "ocr":
            components.insert(1, "label-rules@" + option.rules_version)
            if option.rules_version == "3":
                components.insert(2, "label-dictionary@1")
                parameters["dictionary"] = "label-dictionary@1"
        meta = Profile(
            id=profile_id,
            version=version,
            method=method,
            component_ids=components,
            provider=option.provider,
            model=option.model if option.operation == "vision" else None,
            processor=option.model if option.operation != "vision" else None,
            stage_destinations=destinations,
            enabled=config.enabled,
            configured=not missing,
            unavailable_reason="Missing " + ", ".join(missing)
            if missing
            else "Disabled by operator"
            if not config.enabled
            else None,
        )
        definitions[profile_id] = Definition(
            meta, "extended", config, config.max_call_eur or Decimal("0"), parameters=parameters
        )
    for profile_id, hybrid in settings.providers.hybrids.items():
        parts = (definitions[hybrid.ocr_profile_id], definitions[hybrid.interpreter_profile_id])
        policy = parts[1].parameters.get("interpretation_policy", "strict")
        draft = policy in {"draft_v1", "draft_v2", "draft_v3", "draft_v4"}
        hybrid_parameters: dict[str, str | int] = {"prompt": "payment-ocr@1", "attempts": 1}
        if draft:
            hybrid_parameters["interpretation_policy"] = policy
        version = (
            "3-"
            + hashlib.sha256(
                json.dumps(
                    {
                        "parts": [p.snapshot() for p in parts],
                        "hybrid": hybrid.model_dump(),
                        "prompt": "payment-ocr@1",
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest()[:16]
        )
        destinations = [
            d.model_copy(deep=True)
            for p in parts
            for d in p.metadata.stage_destinations
            if d.execution == "external"
        ]
        destinations[-1].method = "interpretation"
        destinations[-1].payload_classes = ["ocr_text", "layout"]
        metadata = Profile(
            id=profile_id,
            version=version,
            method="managed_ocr_llm",
            component_ids=[
                parts[0].metadata.version,
                "payment-ocr@1",
                parts[1].metadata.version,
                "review@2",
            ]
            + (["payment-draft@1"] if draft else [])
            + (["payment-party-roles@1"] if policy == "draft_v2" else [])
            + (["payment-party-roles@2"] if policy == "draft_v3" else [])
            + (["payment-party-roles@3"] if policy == "draft_v4" else []),
            model=parts[1].metadata.model,
            processor=parts[0].metadata.processor,
            enabled=hybrid.enabled,
            configured=all(p.metadata.configured for p in parts),
            stage_destinations=destinations,
            unavailable_reason=next(
                (p.metadata.unavailable_reason for p in parts if not p.metadata.configured), None
            )
            or (None if hybrid.enabled else "Disabled by operator"),
        )
        definitions[profile_id] = Definition(
            metadata,
            "hybrid",
            ceiling_eur=sum((p.ceiling_eur for p in parts), Decimal("0")),
            parameters=hybrid_parameters,
            stages=parts,
        )
    return definitions


def resolve(
    options: Options, mime: str, definitions: dict[str, Definition]
) -> tuple[list[Definition], list[ExcludedProfile]]:
    def unavailable(d: Definition) -> str | None:
        m = d.metadata
        if not m.implemented or not m.enabled or not m.configured:
            return m.unavailable_reason or "Profile unavailable"
        if mime not in m.supported_image_types:
            return "Incompatible image type"
        return None

    if options.profiles == "all_enabled":
        selected = [d for _, d in sorted(definitions.items()) if unavailable(d) is None]
        excluded = [
            ExcludedProfile(id=k, reason=unavailable(d) or "unavailable")
            for k, d in sorted(definitions.items())
            if unavailable(d)
        ]
    else:
        selected, excluded = [], []
        for profile_id in options.profiles:
            d = definitions.get(profile_id)
            if d is None or unavailable(d):
                raise ServiceError(
                    422,
                    "invalid_profile",
                    "Selected profile is unknown, unavailable or incompatible.",
                )
            selected.append(d)
    if not selected:
        raise ServiceError(422, "invalid_profile", "No enabled compatible profiles are configured.")
    if len({d.synthetic for d in selected}) != 1:
        raise ServiceError(
            422, "invalid_profile", "Synthetic fixtures cannot be mixed with live profiles."
        )
    return selected, excluded


def validate_limits(image: PreparedImage, definitions: list[Definition]) -> None:
    """Apply documented supplier image constraints to the outbound rendition."""
    for definition in definitions:
        if definition.stages:
            validate_limits(image, list(definition.stages[:1]))
        if definition.adapter == "extended":
            option = ModelOption.model_validate_json(str(definition.parameters["option"]))
            size = len(image.canonical)
            encoded_size = 4 * ((size + 2) // 3)
            longest = max(image.identity.width, image.identity.height)
            violation = (
                (option.provider == "mistral" and size > 20_000_000)
                or (option.provider == "aws" and (size > 10_000_000 or longest > 10000))
                or (
                    option.provider == "anthropic" and (encoded_size > 10_000_000 or longest > 8000)
                )
                or (
                    option.provider == "azure"
                    and size > int(option.tariff.get("document_limit_bytes", "500000000"))
                )
            )
            if violation:
                raise ServiceError(
                    413,
                    "provider_input_limit",
                    "Canonical image exceeds a selected provider's documented input limit.",
                )
        # Mistral's documented image limit; no bespoke application threshold.
        if definition.adapter == "mistral" and len(image.canonical) > 20_000_000:
            raise ServiceError(
                413,
                "provider_input_limit",
                "Canonical image exceeds Mistral's documented 20 MB image limit.",
            )
        # The OpenAI adapter checks its exact serialized 512 MB request as well.
        if definition.adapter == "openai" and len(image.canonical) * 4 // 3 > 512_000_000:
            raise ServiceError(
                413,
                "provider_input_limit",
                "Encoded image exceeds OpenAI's documented 512 MB request limit.",
            )
