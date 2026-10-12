"""Operator-only local configuration. Scan callers cannot alter endpoints or prompts."""

import json
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Literal, Self

from dotenv import load_dotenv
from pydantic import Field, SecretStr, model_validator

from backend.models import Model, Text


class ProviderConfig(Model):
    enabled: bool = False
    account_alias: Text = "local-operator"
    endpoint_host: Text
    configured_region: Text = "unknown"
    verified_processing_region: Text | None = None
    account_access_checked_at: Text | None = None
    data_terms_checked_at: Text | None = None
    data_terms_note: Text | None = None
    pricing_checked_at: Text | None = None
    # Legacy accounting metadata; optional and never an admission limit.
    max_call_eur: Decimal | None = Field(default=None, allow_inf_nan=False)


# Options are operator configuration, never caller-supplied endpoints or model names.
PROVIDER_HOSTS = {
    "openai": "api.openai.com",
    "mistral": "api.mistral.ai",
    "anthropic": "api.anthropic.com",
    "gemini": "generativelanguage.googleapis.com",
    "xai": "api.x.ai",
    "together": "api.together.ai",
    "azure": None,
    "google_documentai": None,
    "aws": None,
    "mindee": "api-v2.mindee.net",
}
# These are supported destinations, not assertions of account eligibility.
REGIONAL_PROVIDER_HOSTS = {
    "openai": {"api.openai.com", "eu.api.openai.com", "us.api.openai.com"},
    "mistral": {"api.mistral.ai", "api.eu.mistral.ai"},
}
OPERATIONS = {
    "openai": {"vision"},
    "mistral": {"vision", "ocr", "annotations"},
    "anthropic": {"vision"},
    "gemini": {"vision"},
    "xai": {"vision"},
    "together": {"vision"},
    "azure": {"ocr", "invoice"},
    "google_documentai": {"ocr", "invoice"},
    "aws": {"ocr", "invoice"},
    "mindee": {"invoice"},
}
KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "xai": "XAI_API_KEY",
    "together": "TOGETHER_API_KEY",
    "azure": "AZURE_DOCUMENT_INTELLIGENCE_KEY",
    "mindee": "MINDEE_V2_API_KEY",
}
RESOURCE_ENV = (
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_DOCUMENTAI_LOCATION",
    "GOOGLE_DOCUMENTAI_OCR_PROCESSOR_ID",
    "GOOGLE_DOCUMENTAI_INVOICE_PROCESSOR_ID",
    "AWS_PROFILE",
    "AWS_REGION",
    "MINDEE_MODEL_ID",
)


def option_resources(provider: str, operation: str) -> tuple[str, ...]:
    return {
        "azure": ("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT",),
        "google_documentai": (
            "GOOGLE_CLOUD_PROJECT",
            "GOOGLE_DOCUMENTAI_LOCATION",
            "GOOGLE_DOCUMENTAI_" + ("OCR" if operation == "ocr" else "INVOICE") + "_PROCESSOR_ID",
        ),
        "aws": ("AWS_PROFILE", "AWS_REGION"),
        "mindee": ("MINDEE_MODEL_ID",),
    }.get(provider, ())


class ModelOption(Model):
    provider: str
    model: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_./-]+$")
    operation: Literal["vision", "ocr", "invoice", "annotations"]
    config: ProviderConfig | None = None
    max_output_tokens: int = Field(default=12000, gt=0, le=16000)
    reasoning: str | None = None
    rules_version: Literal["1", "2", "3"] = "2"
    # Pricing is independently recorded per option; absent tariff remains unknown.
    tariff: dict[str, str] = Field(default_factory=dict)
    protocol_version: Literal["1", "2", "3", "4", "5", "6"] = "1"
    schema_mode: Literal["native", "prompt_json"] = "native"
    poll_interval_seconds: int = Field(default=1, ge=1, le=10)
    mapping_version: Literal["1", "2"] = "1"
    field_policy: Literal["strict", "partial_v1"] = "strict"
    interpretation_policy: Literal["strict", "draft_v1", "draft_v2", "draft_v3", "draft_v4"] = (
        "strict"
    )

    def snapshot_json(self) -> str:
        exclude = set()
        if self.protocol_version == "1":
            exclude.add("protocol_version")
        if self.schema_mode == "native":
            exclude.add("schema_mode")
        if self.poll_interval_seconds == 1:
            exclude.add("poll_interval_seconds")
        if self.mapping_version == "1":
            exclude.add("mapping_version")
        if self.field_policy == "strict":
            exclude.add("field_policy")
        if self.interpretation_policy == "strict":
            exclude.add("interpretation_policy")
        return self.model_dump_json(exclude=exclude)

    @model_validator(mode="after")
    def compatible(self) -> Self:
        if self.interpretation_policy in {"draft_v1", "draft_v2", "draft_v3", "draft_v4"} and (
            self.operation in {"vision", "annotations"} and self.protocol_version not in {"5", "6"}
        ):
            raise ValueError("Draft interpretation requires typed compact protocol 5/6")
        if self.interpretation_policy in {
            "draft_v2",
            "draft_v3",
            "draft_v4",
        } and self.operation not in {
            "vision",
            "annotations",
        }:
            raise ValueError("Recipient-role prompting requires a model interpretation operation")
        if self.field_policy == "partial_v1" and (
            self.operation not in {"vision", "annotations"}
            or self.protocol_version not in {"5", "6"}
        ):
            raise ValueError("Partial field recovery requires typed compact protocol 5/6")
        if self.operation not in OPERATIONS.get(self.provider, set()) or ".." in self.model:
            raise ValueError("Unsupported provider operation or model identifier")
        if self.schema_mode == "prompt_json" and self.provider not in {
            "anthropic",
            "gemini",
        }:
            raise ValueError("Prompt JSON transport is not implemented for this provider")
        if self.provider == "together" and self.reasoning not in {None, "none", "enabled"}:
            raise ValueError("Together thinking mode must be none or enabled")
        if self.provider == "anthropic" and self.reasoning not in {None, "adaptive"}:
            raise ValueError("Anthropic thinking mode must be adaptive or omitted")
        host = PROVIDER_HOSTS[self.provider]
        if self.config is None:
            self.config = ProviderConfig(endpoint_host=host or "unconfigured.invalid")
        if host and self.config.endpoint_host not in REGIONAL_PROVIDER_HOSTS.get(
            self.provider, {host}
        ):
            raise ValueError("Unsupported provider endpoint")
        if not host and self.config.endpoint_host != "unconfigured.invalid":
            patterns = {
                "azure": r"[a-z0-9-]+\.cognitiveservices\.azure\.com",
                "google_documentai": r"(?:eu|us)\-documentai\.googleapis\.com",
                "aws": r"textract\.[a-z0-9-]+\.amazonaws\.com",
            }
            if not re.fullmatch(patterns[self.provider], self.config.endpoint_host):
                raise ValueError("Unsupported cloud endpoint")
        return self


class BudgetPlan(Model):
    """Legacy configuration metadata, retained for existing private files."""

    reference: Text
    cumulative_call_cap: int
    cumulative_hold_eur: Decimal = Field(allow_inf_nan=False)


class HybridOption(Model):
    """Explicit two-stage composition; references separately configured options."""

    ocr_profile_id: Text
    interpreter_profile_id: Text
    enabled: bool = False
    version: Literal["1"] = "1"


class ProfileConfig(Model):
    budget_plan: BudgetPlan | None = None
    openai: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(endpoint_host="api.openai.com")
    )
    mistral: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(endpoint_host="api.mistral.ai")
    )
    options: dict[str, ModelOption] = Field(default_factory=dict)
    hybrids: dict[str, HybridOption] = Field(default_factory=dict)
    default_extract_profile_id: str | None = None

    @model_validator(mode="after")
    def fixed_destinations(self) -> Self:
        for name in [*self.options, *self.hybrids]:
            if name in {"openai-luna-vision", "mistral-ocr-rules"} or not re.fullmatch(
                r"[a-z0-9-]+", name
            ):
                raise ValueError("Reserved or invalid profile ID")
        for name, hybrid in self.hybrids.items():
            if name in self.options:
                raise ValueError("Hybrid and option IDs must be distinct")
            ocr = self.options.get(hybrid.ocr_profile_id)
            interpreter = self.options.get(hybrid.interpreter_profile_id)
            if ocr is None or ocr.operation != "ocr" or interpreter is None:
                raise ValueError("Hybrid requires configured OCR and interpreter options")
            if (
                interpreter.provider != "openai"
                or interpreter.operation != "vision"
                or interpreter.protocol_version != "5"
                or interpreter.field_policy != "partial_v1"
            ):
                raise ValueError("Text interpretation v1 requires OpenAI compact 5 partial fields")
        if self.openai.endpoint_host not in {
            "api.openai.com",
            "eu.api.openai.com",
            "us.api.openai.com",
        }:
            raise ValueError("Unsupported OpenAI endpoint")
        if self.mistral.endpoint_host not in REGIONAL_PROVIDER_HOSTS["mistral"]:
            raise ValueError("Unsupported Mistral endpoint")
        return self


class Settings(Model):
    data_dir: Path = Path(".local/backend")
    token: SecretStr
    openai_key: SecretStr = SecretStr("")
    mistral_key: SecretStr = SecretStr("")
    provider_keys: dict[str, SecretStr] = Field(default_factory=dict)
    resources: dict[str, str] = Field(default_factory=dict)
    providers: ProfileConfig = Field(default_factory=ProfileConfig)
    workers: int = Field(default=2, ge=1, le=2)
    queue_capacity: int = Field(default=10, ge=1)
    # Legacy settings are accepted for compatibility and never enforce spending/call limits.
    smoke_budget_eur: Decimal = Field(default=Decimal("30"), allow_inf_nan=False)
    max_calls: int = 12
    stage_timeout_seconds: float = Field(default=90, gt=0, le=90)
    job_deadline_seconds: float = Field(default=240, gt=0, le=240)

    @model_validator(mode="after")
    def require_auth(self) -> Self:
        if len(self.token.get_secret_value()) < 24 or self.token.get_secret_value().startswith(
            "REPLACE"
        ):
            raise ValueError("Configure a random SCANPAY_TOKEN of at least 24 characters locally")
        return self

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(override=False)
        config_path = Path(os.getenv("SCANPAY_PROFILES_FILE", ".local/providers.json"))
        providers = (
            ProfileConfig.model_validate(json.loads(config_path.read_text()))
            if config_path.exists()
            else ProfileConfig()
        )
        return cls(
            token=SecretStr(os.getenv("SCANPAY_TOKEN", "")),
            openai_key=SecretStr(os.getenv("OPENAI_API_KEY", "")),
            mistral_key=SecretStr(os.getenv("MISTRAL_API_KEY", "")),
            provider_keys={k: SecretStr(os.getenv(v, "")) for k, v in KEY_ENV.items()},
            resources={k: os.getenv(k, "") for k in RESOURCE_ENV},
            data_dir=Path(os.getenv("SCANPAY_DATA_DIR", ".local/backend")),
            providers=providers,
        )
