"""Two explicit fresh stages. No hidden OCR cache, fallback, retries, or field merge."""

import asyncio
import json

import httpx

from backend.adapters.extended import ExtendedAdapter
from backend.config import Settings
from backend.document_observations import DocumentObservation, DocumentSpan
from backend.errors import ProviderError
from backend.runtime import Context, Extraction


class HybridAdapter:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.settings = settings
        self.external = ExtendedAdapter(settings, transport)

    async def extract(self, context: Context) -> Extraction:
        ocr, interpreter = context.definition.stages
        async with asyncio.timeout(self.settings.stage_timeout_seconds):
            await self.external.extract(
                Context(context.store, context.scan, context.run, ocr, 0), recognition_only=True
            )
        stage = next(s for s in context.run.diagnostics.stages if s.execution == "external")
        path = (
            context.store.artifacts
            / context.scan.scan_id
            / f"{context.run.id}.{stage.id}.document.json"
        )
        data = json.loads(path.read_text())
        document = DocumentObservation(
            **{**data, "spans": tuple(DocumentSpan(**s) for s in data["spans"])}
        )
        if document.image_id != context.scan.input.image_id or document.source_stage_id != stage.id:
            raise ProviderError("invalid_provider_output")
        # Empty recognition is a visible failure; do not pay a model to invent it.
        if not document.text.strip():
            raise ProviderError("invalid_provider_output")
        async with asyncio.timeout(self.settings.stage_timeout_seconds):
            return await self.external.extract(
                Context(context.store, context.scan, context.run, interpreter, 1), document=document
            )
