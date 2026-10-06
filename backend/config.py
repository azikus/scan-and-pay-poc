"""Operator-only local configuration. Scan callers cannot alter endpoints or prompts."""

import json
import os
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
    # Operator-supplied EUR ceiling includes taxes/FX/unknowns, not a claimed conversion.
    max_call_eur: Decimal | None = Field(default=None, gt=0, le=30, allow_inf_nan=False)


class ProfileConfig(Model):
    openai: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(endpoint_host="api.openai.com")
    )
    mistral: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(endpoint_host="api.mistral.ai")
    )
    default_extract_profile_id: Literal["openai-luna-vision", "mistral-ocr-rules"] | None = None

    @model_validator(mode="after")
    def fixed_destinations(self) -> Self:
        if self.openai.endpoint_host not in {
            "api.openai.com",
            "eu.api.openai.com",
            "us.api.openai.com",
        }:
            raise ValueError("Unsupported OpenAI endpoint")
        if self.mistral.endpoint_host != "api.mistral.ai":
            raise ValueError("Unsupported Mistral endpoint")
        return self


class Settings(Model):
    data_dir: Path = Path(".local/backend")
    token: SecretStr
    openai_key: SecretStr = SecretStr("")
    mistral_key: SecretStr = SecretStr("")
    providers: ProfileConfig = Field(default_factory=ProfileConfig)
    workers: int = Field(default=2, ge=1, le=2)
    queue_capacity: int = Field(default=10, ge=1)
    smoke_budget_eur: Decimal = Field(default=Decimal("30"), gt=0, le=30, allow_inf_nan=False)
    max_calls: int = Field(default=12, ge=1, le=100)
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
            data_dir=Path(os.getenv("SCANPAY_DATA_DIR", ".local/backend")),
            providers=providers,
        )
