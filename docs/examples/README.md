# Synthetic contract examples

These files preserve the synthetic v1 handoff response shape, now checked by the implemented backend's contract tests. They are manually constructed examples, not provider outputs or evidence of extraction quality. Current generated contracts are under `contracts/v1/`; API_CONTRACT.md remains normative.

- uk-extract.synthetic.json: a complete synthetic UK payment draft with a linked sort-code/account pair and required reference; mandatory confirmation remains true.
- hr-extract.synthetic.json: a synthetic Croatian draft with amount, HR model and reference but an unreadable IBAN. It is a completed computation with needs_review, null account value and no selected candidate.
- scan-result.schema.json: JSON Schema 2020-12 for GET scan-result structure. API_CONTRACT.md owns semantic validation, including pairing, evidence links, readiness and job aggregation.

Names and payment details are synthetic. Zero UK bank details are placeholders, not verified/routable accounts. No real invoices were copied into these examples. execution_kind identifies fixtures; hashes are placeholders, timings/usage/cost are not measurements, and no provider is named as having produced them. Do not use these details to send money or display them as a live demo.

For compare, return each run independently under runs and keep final_result_id=null. For queued/running/failed runs payment can be null. Completed runs require a payment object even when fields are missing. Preserve these and the implemented negative/semantic tests as providers expand; passing the structural schema alone does not prove the business rules.
