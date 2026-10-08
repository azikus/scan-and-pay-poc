from backend.ocr_rules_v2 import extract_rules_v2


def test_split_bank_labels_rejoin_only_contiguous_payment_section():
    text = "Account name: Test Beneficiary\n\nSort code: 00-11-22\n\nAccount number: 00123456\n\nInvoice total: GBP 123.40"
    payment, evidence, _ = extract_rules_v2(text, "image", "stage")
    assert len(payment.candidates) == 1
    assert payment.candidates[0].destination.account_number.value == "00123456"
    assert payment.candidates[0].destination.sort_code.value == "00-11-22"
    assert payment.candidates[0].amount.role == "invoice_total"
    assert all(e.excerpt in text for e in evidence)


def test_sections_do_not_cross_pair_with_other_account_or_currency():
    for boundary in ["# Another account", "Currency: EUR", "Customer information: unrelated"]:
        text = f"Sort code: 00-11-22\n\n{boundary}\n\nAccount number: 00987654"
        payment, _, _ = extract_rules_v2(text, "image", "stage")
        assert len(payment.candidates) == 2
        assert payment.candidates[0].destination.account_number.value is None
        assert payment.candidates[1].destination.sort_code.value is None


def test_multicolumn_totals_preserve_roles_and_blank_cells():
    text = "IBAN: GB82 WEST 1234 5698 7654 32\n\n| Subtotal | Tax | Gross |\n|---|---|---|\n| 100.00 | 20.00 | GBP 120.00 |"
    payment, _, _ = extract_rules_v2(text, "image", "stage")
    assert payment.candidates[0].amount.value.value == "120.00"
    assert payment.candidates[0].amount.role == "invoice_total"
    text = text.replace("GBP 120.00", "")
    payment, _, _ = extract_rules_v2(text, "image", "stage")
    assert payment.candidates[0].amount.value.value is None


def test_croatian_payment_instruction_and_invoice_counterexample():
    text = "IBAN: HR12 1001 0051 8630 0016 0\nPrilikom uplate navedite model HR00 i poziv na broj 001-22-003."
    payment, _, _ = extract_rules_v2(text, "image", "stage")
    assert payment.candidates[0].remittance.model.value == "HR00"
    assert payment.candidates[0].remittance.reference.value == "001-22-003"
    payment, _, _ = extract_rules_v2(
        text.splitlines()[0] + "\nInvoice number: 001-22-003", "image", "stage"
    )
    assert payment.candidates[0].remittance.reference.value is None
