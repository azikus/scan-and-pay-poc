from backend.adapters.mapping import map_fields


def test_mapping_preserves_total_role_supplier_and_unsupported_bank_fields():
    result = map_fields(
        {
            "supplier_name": ["Synthetic Supplier"],
            "invoice_total": ["120.00"],
            "currency": ["GBP"],
            "account_number": ["00123456"],
        },
        "image",
        "stage",
    )
    candidate = result.payment.candidates[0]
    assert candidate.amount.role == "invoice_total"
    assert candidate.beneficiary_name.value is None
    assert candidate.destination.kind == "unresolved"
    assert any(e.excerpt == "00123456" for e in result.evidence)
    assert candidate.remittance.reference.value is None


def test_mapping_multiple_accounts_abstains_instead_of_cross_pairing():
    result = map_fields(
        {
            "sort_code": ["00-00-00", "11-11-11"],
            "account_number": ["00123456", "00987654"],
            "invoice_number": ["NOT-A-REFERENCE"],
        },
        "image",
        "stage",
    )
    dest = result.payment.candidates[0].destination
    assert dest.sort_code.value is None and dest.sort_code.state == "ambiguous"
    assert dest.account_number.value is None
    assert result.payment.candidates[0].remittance.reference.value is None


def test_mindee_nested_currency_and_iban_without_routing_number_promotion():
    from backend.adapters.documents import vendor_fields

    fields = vendor_fields(
        {
            "inference": {
                "result": {
                    "fields": {
                        "locale": {
                            "fields": {"currency": {"value": "GBP"}, "country": {"value": "GB"}}
                        },
                        "supplier_payment_details": {
                            "items": [
                                {
                                    "fields": {
                                        "iban": {"value": "GB82 WEST 1234 5698 7654 32"},
                                        "routing_number": {"value": "001122"},
                                    }
                                }
                            ]
                        },
                    }
                }
            }
        },
        "mindee",
    )
    assert fields == {"currency": ["GBP"], "iban": ["GB82 WEST 1234 5698 7654 32"]}


def test_mapping_currency_conflict_stays_ambiguous():
    result = map_fields(
        {"invoice_total": ["USD 20.00"], "currency": ["EUR", "GBP"]}, "image", "stage"
    )
    assert result.payment.candidates[0].amount.currency.state == "ambiguous"


def test_mapping_v2_normalizes_only_unambiguous_currency_tokens():
    import pytest
    from pydantic import ValidationError

    from backend.models import Payment

    fields = {"invoice_total": ["20.00"], "currency": ["€"]}
    # The original mapping remains unchanged for saved profile identities.
    with pytest.raises(ValidationError):
        Payment.model_validate(map_fields(fields, "image", "stage").payment.model_dump())
    result = map_fields(fields, "image", "stage", version="2")
    currency = result.payment.candidates[0].amount.currency
    assert currency.value == "EUR" and currency.raw_text == "€"
    assert currency.normalization == ["explicit_currency_token"]
    Payment.model_validate(result.payment.model_dump())
    for token in ["$", "kr", "unknown"]:
        result = map_fields(
            {"invoice_total": ["20.00"], "currency": [token]}, "image", "stage", version="2"
        )
        currency = result.payment.candidates[0].amount.currency
        assert currency.value is None and currency.state == "ambiguous"
        assert currency.raw_text == token
    result = map_fields(
        {"invoice_total": ["GBP 20.00"], "currency": ["€"]}, "image", "stage", version="2"
    )
    assert result.payment.candidates[0].amount.currency.state == "ambiguous"
