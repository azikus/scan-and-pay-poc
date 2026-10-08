import json
from dataclasses import FrozenInstanceError

import pytest

from backend.document_observations import observe


def test_google_layout_anchors_and_immutability():
    body = {
        "document": {
            "text": "Amount due: 10",
            "pages": [
                {
                    "pageNumber": 1,
                    "lines": [
                        {
                            "layout": {
                                "textAnchor": {"textSegments": [{"endIndex": "14"}]},
                                "boundingPoly": {"normalizedVertices": [{"x": 0.1, "y": 0.2}]},
                            }
                        }
                    ],
                }
            ],
        }
    }
    doc = observe(body, "google_documentai", body["document"]["text"], "image", "stage")
    assert doc.spans[0].text == "Amount due: 10"
    body["document"]["text"] = "Changed"
    assert json.loads(doc.layout_json)["text"] == "Amount due: 10"
    with pytest.raises(FrozenInstanceError):
        doc.text = "Changed"
    with pytest.raises(ValueError):
        observe(body, "google_documentai", "short", "image", "stage")


def test_azure_geometry_keeps_native_units():
    body = {
        "analyzeResult": {
            "pages": [
                {
                    "pageNumber": 1,
                    "unit": "pixel",
                    "width": 100,
                    "height": 200,
                    "lines": [{"content": "Invoice", "polygon": [1, 2, 3, 4]}],
                }
            ]
        }
    }
    doc = observe(body, "azure", "Invoice", "image", "stage")
    assert json.loads(doc.spans[0].geometry_json)["unit"] == "pixel"
    assert doc.source_stage_id == "stage"


def test_aws_line_ids_and_mistral_no_invented_boxes():
    doc = observe(
        {
            "Blocks": [
                {
                    "Id": "line-id",
                    "BlockType": "LINE",
                    "Text": "Total",
                    "Geometry": {"BoundingBox": {"Left": 0.1}},
                }
            ]
        },
        "aws",
        "Total",
        "image",
        "stage",
    )
    assert doc.spans[0].id == "line-id"
    doc = observe(
        {"pages": [{"index": 0, "markdown": "Total\n10", "tables": []}]},
        "mistral",
        "Total\n10",
        "image",
        "stage",
    )
    assert len(doc.spans) == 2
    assert doc.spans[0].geometry_json is None


def test_interpretation_payload_excludes_raw_layout_and_embedded_images():
    import json

    from backend.document_observations import DocumentObservation, DocumentSpan

    doc = DocumentObservation(
        "1",
        "synthetic",
        "stage",
        "image",
        "Untrusted text",
        (DocumentSpan("line", 1, "Untrusted text"),),
        '{"image":"data:image/png;base64,PRIVATE","metadata":"private"}',
    )
    sent = json.loads(doc.interpretation_json())
    assert "layout_json" not in sent
    assert "PRIVATE" not in doc.interpretation_json()
    assert sent["source_stage_id"] == "stage"
    assert sent["spans"][0]["text"] == "Untrusted text"
    assert "PRIVATE" in doc.to_json()
