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

FIELD_INSTRUCTIONS_V2 = """
Field applicability and printed payment instructions:
- The candidate's model field means ONLY the Croatian payment/remittance model
  explicitly printed for that payment option (for example HR01). It is not an AI model,
  payment-method name, customer code, tax code, tariff, account number, reference or
  foreign payment identifier. Never put those in model. Do not add a model because the
  issuer, language or bank is Croatian. A foreign issuer can explicitly request a
  Croatian payment model; preserve that instruction when printed.
- For every absent or inapplicable field, including model, use values:[], basis:printed.
  Use unreadable only when a relevant printed value is present but cannot be read.
  Unknown reference_requirement means the payment instructions are genuinely unclear;
  use not_stated when the document states no reference requirement. Never invent one.
- A visibly named biller scheme (for example pagoPA, CBILL or a labelled RF payment
  code) belongs in a biller_reference destination with its own printed identifiers,
  not in model or an invented IBAN. Preserve each full-payment/instalment option and
  its linked amount and reference, even if no bank account is printed. The backend
  will still mark unsupported biller execution as requiring review. An unlabelled
  customer number alone does not establish a biller scheme.
- Copy amount_text exactly, including whole-unit amounts such as 80, and currency
  words such as Euro; the backend normalizes their formatting. Read the amount's label
  and payment instructions: do not substitute a subtotal, tax, previous balance or
  instalment for the printed final amount due. Preserve genuine alternative payment
  amounts as separate candidates, never compute or guess a missing total.
"""


BILLER_INSTRUCTIONS = """
Italian bill-payment drafts (these rules refine the generic separate-route instructions):
- A printed pagoPA notice uses scheme:pagoPA, notice_number:Codice Avviso and
  creditor_tax_code:Codice Fiscale Ente Creditore. Never use the payer's tax code.
  Keep the entire printed notice number, not only its IUV portion. Never pad digits.
- biller_code means ONLY the printed CBILL/SIA organisation code, never the creditor
  tax code, notice number, invoice number or postal account. For private CBILL bills,
  use scheme:CBILL and bill_reference for the explicitly labelled bill payment code.
- When the SAME pagoPA notice offers CBILL, retain one candidate with scheme:pagoPA
  and its printed biller_code, notice_number and creditor_tax_code. These are two
  channels for one bill, not two inconsistent amounts or two separate obligations.
  A CBILL label/code alone does not prove that a private bill is a pagoPA notice.
- Keep distinct notices, instalments, full-payment amounts and unrelated bank
  transfers as separate candidates with their OWN identifiers. Never combine fields
  across options/pages. Do not duplicate a notice simply because bank/postal channels
  repeat the SAME identifiers and amount. Preserve uncertainty instead of guessing.
- These identifiers live in destination, not the Croatian model or generic remittance
  reference. Use reference_requirement:not_stated unless a separate transfer reference
  is explicitly required or genuinely unclear. No IBAN or HR00 is required for these
  biller drafts. Country/language alone never establishes a payment scheme.
- Use only visible printed text, including text beside masked barcodes. Do not decode
  barcode payloads, reconstruct masked content or look up missing payment identifiers.
"""


OPTION_INSTRUCTIONS_V4 = """
Payment options and conditions:
- pagoPA is the notice/payment system; CBILL is the bank service used to pay such a
  notice. They are not competing payment choices. Keep one pagoPA candidate when
  bank and postal sections repeat the same notice and amount. Retain all printed
  identifiers; never treat a postal account or Type P1 as a bank-transfer route/model.
- Each distinct instalment is a separate option with its OWN notice number, amount,
  option_label and due_date. Keep the printed instalment role. Copy the option label
  and due date as printed; do not compute, translate or infer them. If several dates
  apply, leave the document-level due_date empty and put each date on its own option.
- payment_condition copies the complete printed condition governing use of that
  option, including any instruction to check direct-debit status first. A fallback
  notice for failed direct debit is conditional; never imply it should be paid again.
  Do not infer whether an existing debit succeeded or whether a debt is still payable.
- If there is no printed label/date/condition for an option, use an empty reading.
  A bill breakdown or details QR alone does not supply a payment route. Never create
  payment instructions from a details URL, customer number or another page.
"""


class ContextReading(Reading):
    explanation: str = Field(max_length=600)
    excerpts: list[str] = Field(max_length=4)


def context_prompt(prompt: str, *, policy: str = "invoice_v1") -> str:
    instructions = (
        FIELD_INSTRUCTIONS_V2 if policy in {"invoice_v2", "invoice_v3", "invoice_v4"} else ""
    )
    if policy in {"invoice_v3", "invoice_v4"}:
        instructions = instructions.replace(
            "The backend\n  will still mark unsupported biller execution as requiring review.",
            "The backend checks draft completeness separately from payment execution.",
        )
    biller_instructions = BILLER_INSTRUCTIONS
    if policy == "invoice_v4":
        biller_instructions = biller_instructions.replace(
            "These are two\n  channels for one bill, not two inconsistent amounts or two separate obligations.",
            "Use one bank CBILL/pagoPA bill-payment flow for this notice.",
        )
    return (
        prompt
        + "\n"
        + INSTRUCTIONS
        + instructions
        + (biller_instructions if policy in {"invoice_v3", "invoice_v4"} else "")
        + (OPTION_INSTRUCTIONS_V4 if policy == "invoice_v4" else "")
    )


def context_schema(schema: dict[str, Any], *, policy: str = "invoice_v1") -> dict[str, Any]:
    result = deepcopy(schema)
    if policy in {"invoice_v3", "invoice_v4"}:
        biller = result["$defs"]["BillerReading"]
        for key in ("notice_number", "creditor_tax_code", "bill_reference"):
            biller["properties"][key] = {"$ref": "#/$defs/Reading"}
            biller["required"].append(key)
    if policy == "invoice_v4":
        option = result["$defs"]["PaymentOptionV5"]
        for key in ("option_label", "due_date", "payment_condition"):
            option["properties"][key] = {"$ref": "#/$defs/Reading"}
            option["required"].append(key)
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


def extract_context(
    text: str, image_id: str, stage_id: str, *, version: str, policy: str = "invoice_v1"
) -> Extraction:
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
    result.routing.applied_rule_packs.append("invoice-context@" + policy.removeprefix("invoice_v"))
    return result
