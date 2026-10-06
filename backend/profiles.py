import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

from backend.config import ProviderConfig, Settings
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
    profiles: list[Profile]
    default_extract_profile_id: str | None = None


@dataclass(frozen=True)
class Definition:
    metadata: Profile
    adapter: str
    config: ProviderConfig | None = None
    ceiling_eur: Decimal = Decimal("0")
    synthetic: bool = False
    parameters: dict[str, str | int] = field(default_factory=dict)

    def snapshot(self) -> dict[str, object]:
        return {
            "profile": self.metadata.model_dump(),
            "adapter": self.adapter,
            "config": self.config.model_dump(mode="json") if self.config else None,
            "ceiling_eur": str(self.ceiling_eur),
            "synthetic": self.synthetic,
            "parameters": self.parameters,
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
            "pricing_checked_at",
            "max_call_eur",
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
