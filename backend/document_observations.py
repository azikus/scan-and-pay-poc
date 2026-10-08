"""Immutable recognition observations, separate from payment interpretation and review."""

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentSpan:
    id: str
    page: int
    text: str
    # Provider-native coordinates; never pretend they are canonical normalized boxes.
    geometry_json: str | None = None


@dataclass(frozen=True)
class DocumentObservation:
    version: str
    provider: str
    source_stage_id: str
    image_id: str
    text: str
    spans: tuple[DocumentSpan, ...]
    layout_json: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    def interpretation_json(self) -> str:
        # Explicitly whitelist text/line geometry. Raw layout can contain vendor
        # image attachments, fields or unrelated metadata; never forward it wholesale.
        return json.dumps(
            {
                "version": self.version,
                "provider": self.provider,
                "source_stage_id": self.source_stage_id,
                "image_id": self.image_id,
                "text": self.text,
                "spans": [asdict(s) for s in self.spans],
                "geometry_space": "provider-native per page; not canonical image boxes",
            },
            ensure_ascii=False,
        )


def observe(
    body: dict[str, Any], provider: str, text: str, image_id: str, stage_id: str
) -> DocumentObservation:
    spans = []

    def add(ident: str, page: int, value: str, geometry: Any = None) -> None:
        if not isinstance(value, str):
            raise ValueError("Malformed recognition span")
        spans.append(
            DocumentSpan(ident, page, value, json.dumps(geometry) if geometry is not None else None)
        )

    if provider == "azure":
        layout = body["analyzeResult"]
        for page in layout.get("pages", []):
            for index, line in enumerate(page.get("lines", [])):
                add(
                    f"page-{page['pageNumber']}-line-{index}",
                    page["pageNumber"],
                    line["content"],
                    {
                        "polygon": line.get("polygon"),
                        "unit": page.get("unit"),
                        "width": page.get("width"),
                        "height": page.get("height"),
                    },
                )
    elif provider == "google_documentai":
        layout = body["document"]
        for page in layout.get("pages", []):
            for index, line in enumerate(page.get("lines", [])):
                block = line["layout"]
                chunks = []
                for segment in block["textAnchor"]["textSegments"]:
                    start, end = int(segment.get("startIndex", 0)), int(segment["endIndex"])
                    if not 0 <= start <= end <= len(text):
                        raise ValueError("Invalid recognition text anchor")
                    chunks.append(text[start:end])
                add(
                    f"page-{page['pageNumber']}-line-{index}",
                    page["pageNumber"],
                    "".join(chunks),
                    block.get("boundingPoly"),
                )
    elif provider == "aws":
        layout = {"blocks": body.get("Blocks", []), "expenses": body.get("ExpenseDocuments", [])}
        for block in layout["blocks"]:
            if block.get("BlockType") == "LINE":
                add(block["Id"], block.get("Page", 1), block["Text"], block.get("Geometry"))
    elif provider == "mistral":
        layout = {"pages": body["pages"]}
        for page in body["pages"]:
            for index, line in enumerate(page["markdown"].splitlines()):
                add(f"page-{page.get('index', 0) + 1}-line-{index}", page.get("index", 0) + 1, line)
    else:
        layout = body
    return DocumentObservation(
        "1",
        provider,
        stage_id,
        image_id,
        text,
        tuple(spans),
        json.dumps(layout, ensure_ascii=False),
    )
