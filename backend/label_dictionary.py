"""Versioned literal label aliases, independent of OCR layout/association rules.

A language tag documents an alias; it never routes a document or supplies currency,
account country, missing model digits, or payment ownership. No fuzzy bank labels.
"""

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator

from backend.models import Model, Text
from backend.ocr_rules import LABELS


def normalize_label(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


class LabelEntry(Model):
    field: Text
    language: str = Field(pattern=r"^(?:[a-z]{2}|und)$")
    aliases: list[Text] = Field(min_length=1)


class LabelDictionary(Model):
    version: Text
    entries: list[LabelEntry]

    @model_validator(mode="after")
    def unambiguous(self) -> "LabelDictionary":
        seen: dict[str, str] = {}
        for entry in self.entries:
            if entry.field not in LABELS:
                raise ValueError("Unsupported semantic field")
            for alias in entry.aliases:
                normalized = normalize_label(alias)
                if not normalized or normalized in seen:
                    raise ValueError("Blank or duplicate label alias")
                seen[normalized] = entry.field
        return self

    def patterns(self) -> dict[str, str]:
        fields: dict[str, list[str]] = {}
        for entry in self.entries:
            fields.setdefault(entry.field, []).extend(entry.aliases)
        return {
            name: "(?:"
            + "|".join(
                re.escape(normalize_label(a)).replace(r"\ ", r"\s+")
                for a in sorted(aliases, key=len, reverse=True)
            )
            + ")"
            for name, aliases in fields.items()
        }


@lru_cache(maxsize=4)
def label_patterns(version: str = "1") -> dict[str, str]:
    if version != "1":
        raise ValueError("Unsupported dictionary version")
    data = LabelDictionary.model_validate_json(
        (Path(__file__).parent / "labels" / f"labels-v{version}.json").read_text()
    )
    if data.version != version:
        raise ValueError("Dictionary version mismatch")
    return data.patterns()
