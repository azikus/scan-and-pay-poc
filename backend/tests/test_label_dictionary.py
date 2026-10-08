import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.label_dictionary import LabelDictionary, label_patterns, normalize_label
from backend.ocr_rules_v3 import exact_label

DATA = json.loads((Path(__file__).parents[1] / "labels/labels-v1.json").read_text())


@pytest.mark.parametrize("entry", DATA["entries"])
def test_every_alias_matches_only_its_semantic_field(entry):
    for alias in entry["aliases"]:
        assert exact_label(alias.upper() + ":") == entry["field"]
        assert exact_label("unrelated " + alias) is None
        assert exact_label(alias + " unrelated") is None
        assert re.fullmatch(label_patterns()[entry["field"]], normalize_label(alias))


def test_dictionary_rejects_cross_field_alias_collisions_and_unknown_fields():
    for entries in [
        [
            {"field": "amount_due", "language": "en", "aliases": ["Total"]},
            {"field": "invoice_total", "language": "it", "aliases": ["TOTAL"]},
        ],
        [{"field": "bank_owner_verified", "language": "en", "aliases": ["owner"]}],
        [{"field": "amount_due", "language": "en", "aliases": [" "]}],
    ]:
        with pytest.raises(ValidationError):
            LabelDictionary(version="1", entries=entries)
    with pytest.raises(ValueError, match="version"):
        label_patterns("2")


def test_language_is_metadata_and_ambiguous_labels_stay_unmapped():
    assert (
        exact_label("TOTAL DUE")
        == exact_label("ukupno za platiti")
        == exact_label("totale da pagare")
        == "amount_due"
    )
    assert exact_label("total") == "invoice_total"
    assert exact_label("account") is None
    assert exact_label("reference") is None
    assert exact_label("tax") is None
    assert exact_label("IBAN primatelja") == "iban"
    assert exact_label("s\u030cifra kupca") == "customer_number"
    assert normalize_label("  SORT\tCODE  ") == "sort code"
