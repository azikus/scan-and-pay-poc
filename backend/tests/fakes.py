"""Offline adapters for synthetic tests; never part of the live registry."""

from collections.abc import Callable

from backend.errors import ProviderError
from backend.models import Evidence, Payment, Routing
from backend.runtime import Context, Extraction


class FixtureAdapter:
    """Synthetic extraction with optional failures and call counting."""

    def __init__(
        self,
        loader: Callable[[], tuple[Payment, list[Evidence]]] | None = None,
        failure: str | None = None,
    ):
        self.loader, self.failure = loader, failure
        self.calls = 0

    async def extract(self, context: Context) -> Extraction:
        self.calls += 1
        stage = context.stage("synthetic_fixture", external=False, payloads=[])
        if self.failure:
            raise ProviderError(self.failure)
        payment, evidence = self.loader() if self.loader else (Payment(), [])
        for item in evidence:
            item.image_id = context.scan.input.image_id
            item.source_stage_id = stage.id
            item.grounding = "synthetic_fixture"
        return Extraction(
            payment,
            evidence,
            Routing(reasons=["Synthetic fixture; not an extraction or timing measurement."]),
        )
