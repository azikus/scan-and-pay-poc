"""Shared field semantics; absence never supplies a country or payment value."""

import pycountry

from backend.models import Observation

REVIEW_VERSION = "5"
NORMALIZATION_VERSION = "3"
CURRENCY_TOKENS = r"\b(?:pounds? sterling|euros?|GBP|EUR)\b|[£€$]"


def currency_code(value: str) -> str | None:
    token = value.strip()
    aliases = {
        "€": "EUR",
        "euro": "EUR",
        "euros": "EUR",
        "£": "GBP",
        "pound sterling": "GBP",
        "pounds sterling": "GBP",
    }
    code = aliases.get(token.casefold(), token.upper())
    return code if pycountry.currencies.get(alpha_3=code) is not None else None


def has_reading(observation: Observation) -> bool:
    """Empty unsupported optional fields are absent, but uncertainty is retained."""
    return bool(
        observation.value
        or observation.raw_text
        or observation.alternatives
        or observation.state in {"unreadable", "ambiguous"}
    )
