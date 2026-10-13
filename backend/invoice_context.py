"""Opt-in, single-call context claims; payment extraction remains independently recoverable."""

import json
from copy import deepcopy
from typing import Any

from pydantic import Field, ValidationError

from backend.adapters.compact import Reading
from backend.adapters.partial import recover, unique_object
from backend.models import Evidence, Observation
from backend.runtime import Extraction

INSTRUCTIONS = """
Document context (part of this SAME extraction, not a separate classification task):
- Identify document language and issuer country separately from the payment route and
  bank-account country. Use a language code such as en, hr, el or it, and ISO alpha-2
  country codes such as GB, HR, GR or IT. Unknown is an empty values array.
- For language and issuer_country, include a short explanation and exact supporting
  printed excerpts. These are evidence summaries, not a reasoning transcript. Do not
  include bank account numbers in context excerpts; bank fields already capture them.
- Detected language is inferred unless explicitly stated on the document. Country is
  printed only when explicitly named for the ISSUER; a city/address may support an
  inferred suggestion. Customer addresses, language alone, currency, a company name
  alone, absent fields or an IBAN prefix cannot establish issuer country. Leave unknown
  when support is insufficient. Preserve alternatives when context is contradictory.
- Choose each destination from positive printed bank/payment evidence. An IBAN uses
  the IBAN destination, including on an English-language invoice. A linked UK sort
  code/account pair uses uk_domestic, including on a non-English invoice. A Greek RF
  reference is not an IBAN and does not by itself establish a routable bank destination.
- Croatian HR model and poziv na broj are separate remittance fields when printed.
  Preserve leading zeros. Never invent HR00, a sort code, BIC or payment reference to
  fill an absent field. Do not infer currency from country or language.
- Keep every populated field and distinct payment option, even if it conflicts with
  the country suggestion. The backend determines applicability and missing-field UI;
  do not emit completeness decisions. An optional absent field is not a failed reading.
"""


class ContextReading(Reading):
    explanation: str = Field(max_length=600)
    excerpts: list[str] = Field(max_length=4)


def context_prompt(prompt: str) -> str:
    return prompt + "\n" + INSTRUCTIONS


def context_schema(schema: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(schema)
    reading = deepcopy(result["$defs"]["Reading"])
    reading["properties"].update(
        explanation={"type": "string", "maxLength": 600},
        excerpts={"type": "array", "items": {"type": "string"}, "maxItems": 4},
    )
    reading["required"] = list(reading["properties"])
    result["$defs"]["ContextReading"] = reading
    for key in ("language", "issuer_country"):
        result["properties"][key] = {"$ref": "#/$defs/ContextReading"}
    return result


def extract_context(text: str, image_id: str, stage_id: str, *, version: str) -> Extraction:
    original = json.loads(text, object_pairs_hook=unique_object)
    if not isinstance(original, dict):
        raise ValueError("Expected an extraction object")
    contexts: dict[str, ContextReading] = {}
    invalid: set[str] = set()
    for key in ("language", "issuer_country"):
        try:
            reading = ContextReading.model_validate(original.get(key))
            if reading.values and (
                not reading.explanation.strip() or not any(s.strip() for s in reading.excerpts)
            ):
                raise ValueError("Context claim lacks supporting text")
            contexts[key] = reading
            original[key] = reading.model_dump(include={"values", "basis"})
        except (ValueError, ValidationError):
            invalid.add(key)
            # Unusable context cannot discard valid payment fields or invent a country.
            original[key] = {"values": [], "basis": "unsupported"}
    result = recover(json.dumps(original), image_id, stage_id, version=version)
    for key, reading in contexts.items():
        observation: Observation = getattr(result.payment.document_context, key)
        ids = []
        for excerpt in reading.excerpts:
            if not excerpt.strip():
                continue
            ident = f"context-{key}-{len(result.evidence)}"
            result.evidence.append(
                Evidence(
                    id=ident,
                    image_id=image_id,
                    source_stage_id=stage_id,
                    excerpt=excerpt,
                    grounding="model_claim",
                )
            )
            ids.append(ident)
        # Retain original exact value claims as evidence; expose supporting excerpts first.
        observation.evidence_ids = ids + observation.evidence_ids
        result.context_explanations[key] = (
            reading.explanation.strip() or "Context was not established."
        )
    for key in invalid:
        result.context_explanations[key] = "Context was absent or unsupported; review the image."
    result.routing.applied_rule_packs.append("invoice-context@1")
    return result
