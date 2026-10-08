"""Versioned opt-in payment-party role prompts; no entity lookup or guessing."""

from copy import deepcopy
from typing import Any

from backend.draft_policy import prompt_v1

VERSION = "payment-party-roles@1"

ROLE_INSTRUCTIONS = """
Payment-party roles (follow the direction of money):
- beneficiary_name is the payee/creditor receiving this payment, NOT the person receiving
  the invoice, letter or notice. Read the labels and surrounding payment instructions.
- A notice's Destinatario, Bill To, Customer, debtor, payer or utility-contract holder
  identifies the billed party, not the payee. In an Italian payment notice, Ente creditore
  identifies the creditor; Destinatario identifies the notice addressee. Do not translate
  the word 'recipient' into beneficiary without checking WHAT they receive.
- account_holder_name is the explicitly named owner of the RECIPIENT BANK ACCOUNT.
  A customer/utility account holder (intestatario, customer number, supply contract) is
  not evidence of that role. A bank name next to Bank/Banca/BIC names the financial
  institution, not the beneficiary or account owner. Leave the holder empty unless
  the bank-account ownership is stated; do not duplicate the supplier there by default.
- Preserve an explicit payment beneficiary even if it differs from the supplier,
  manager or agent. For a refund or other explicitly reversed payment, follow the
  printed direction: a customer or bank CAN be the payee when explicitly owed money.
- If no explicit payee is printed, keep beneficiary empty and the printed supplier in
  supplier_name; the backend can use the approved supplier fallback. If the supplier
  or payment direction is unclear, leave fields empty/ambiguous rather than choose a
  person from the address block. Personal names are not inherently payer or payee.
Synthetic role examples (names below are examples, never output them unless printed):
1. Destinatario: Alex Example; Ente creditore: Example Utility -> beneficiary is
   Example Utility; account_holder_name is empty unless separately stated.
2. Supplier: Example Services; Bill To: Example Customer; Bank: Example Bank ->
   supplier is Example Services; neither the customer nor bank is the beneficiary.
3. Issuer/manager: Example Agent; Beneficiary: Example Owners Community -> preserve
   Example Owners Community; do not replace it with the manager.
Before returning JSON, check each beneficiary/holder against the role labels and the
linked payment route. A plausible name in the wrong role is an extraction error.
"""

FIELD_DEFINITIONS = {
    "beneficiary_name": (
        "Payee/creditor receiving the MONEY for this candidate. Not the notice/invoice "
        "addressee, Bill To customer, payer or bank institution. Preserve an explicit "
        "third-party beneficiary. Empty when unstated; backend handles supplier fallback."
    ),
    "account_holder_name": (
        "Explicit owner of the recipient BANK account, not the billed customer's utility "
        "account/contract holder and not the bank name. Empty unless ownership is stated."
    ),
    "supplier_name": "Printed supplier/issuer of the invoice, distinct from its billed customer.",
}


def prompt_v2(prompt: str) -> str:
    previous = prompt_v1(prompt)
    # Replace the ambiguous v1 paragraph; retain unrelated safety and payment rules verbatim.
    start = previous.index("Keep supplier, billed customer, beneficiary and account holder as")
    end = previous.index("Copy amount_text exactly", start)
    return previous[:start] + ROLE_INSTRUCTIONS + "\n" + previous[end:]


def role_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Add role definitions at field sites without changing the response shape or old schema."""
    result = deepcopy(schema)
    for node in [result, *result.get("$defs", {}).values()]:
        for name, description in FIELD_DEFINITIONS.items():
            if name in node.get("properties", {}):
                node["properties"][name]["description"] = description
    return result


def role_schema_v2(schema: dict[str, Any]) -> dict[str, Any]:
    """OpenAI-compatible definitions: inline the role Reading instead of $ref siblings.

    Keep revision 1 reconstructible: its first live request was rejected by the
    provider for description alongside $ref, before extraction.
    """
    result = role_schema(schema)
    for node in [result, *result.get("$defs", {}).values()]:
        for name in FIELD_DEFINITIONS:
            field = node.get("properties", {}).get(name)
            if field and "$ref" in field:
                definition = result["$defs"][field["$ref"].rsplit("/", 1)[-1]]
                node["properties"][name] = {
                    **deepcopy(definition),
                    **{key: value for key, value in field.items() if key != "$ref"},
                }
    return result


ROLE_COMPLETENESS = """
Representation and completeness checks:
- Read the body and payment instructions as well as the logo/address header. If the
  invoice says 'issued by X, represented by Y', X is the represented issuer/creditor;
  Y is its representative, not automatically the beneficiary. Croatian wording such
  as 'Racun ispostavlja ... zastupana po upravitelju ...' expresses this distinction.
  Preserve the printed spelling. Follow any separately explicit payment beneficiary.
  A manager billing its own fees can still be the creditor; do not exclude managers.
- A printed creditor label establishes the payee role: copy its printed name as
  observed, not inferred merely because you interpreted or translated the role label.
  'Account name' within the destination bank details establishes the account holder.
- Role uncertainty affects only that field. Retain every printed payment option with
  its own amount, reference and destination, including total-payment and instalment
  options. Do not discard an option because its payee is unclear. Bank-transfer
  preference selects among extracted options; it must not erase other printed options.
Synthetic example: 'Invoice issued by Example Owners, represented by Example Agent'
means Example Owners is the issuer/creditor; the agent's header does not override it.
"""


def prompt_v3(prompt: str) -> str:
    """Revision 3 adds represented issuers and field-local uncertainty; v2 is frozen."""
    return prompt_v2(prompt) + "\n" + ROLE_COMPLETENESS
