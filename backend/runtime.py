"""Bounded workers and adapter boundary. There is no automatic retry path."""

import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Any, Protocol
from uuid import uuid4

from pydantic import ValidationError

from backend.config import Settings
from backend.errors import ProviderError
from backend.models import (
    Error,
    Evidence,
    Finding,
    Payment,
    Rendition,
    Routing,
    Run,
    Scan,
    Stage,
)
from backend.profiles import Definition
from backend.review import review_payment
from backend.store import Store


@dataclass
class Extraction:
    payment: Payment
    evidence: list[Evidence]
    routing: Routing


class Context:
    def __init__(self, store: Store, scan: Scan, run: Run, definition: Definition):
        self.store, self.scan, self.run, self.definition = store, scan, run, definition
        self.transforms, self.preprocess_ms = store.preprocessing(scan.scan_id)

    def stage(
        self, method: str, *, external: bool, payloads: list[Any], input_hash: str | None = None
    ) -> Stage:
        config = self.definition.config
        stage = Stage(
            id="stage-" + uuid4().hex,
            method=method,
            execution="external" if external else "local",
            provider=self.definition.metadata.provider if external else None,
            endpoint_host=config.endpoint_host if external and config else None,
            account_alias=config.account_alias if external and config else None,
            configured_region=config.configured_region if external and config else None,
            verified_processing_region=config.verified_processing_region
            if external and config
            else None,
            payload_classes=payloads,
            input_hash=input_hash or self.scan.input.canonical_sha256,
            rendition=Rendition(
                image_id=self.scan.input.image_id,
                width=self.scan.input.width,
                height=self.scan.input.height,
                transform=self.transforms,
            )
            if "image" in payloads
            else None,
        )
        self.run.diagnostics.stages.append(stage)
        self.store.record_stages(self.scan, self.run)
        self.store.save(self.scan)
        if external:
            self.store.mark_dispatched(self.run.id)
        return stage

    def raw(self, data: Any) -> None:
        self.store.save_raw(self.scan.scan_id, self.run.id, data)

    def persist(self) -> None:
        self.store.record_stages(self.scan, self.run)
        self.store.save(self.scan)

    def image(self) -> bytes:
        return (self.store.artifacts / self.scan.scan_id / "canonical.png").read_bytes()


class Adapter(Protocol):
    async def extract(self, context: Context) -> Extraction: ...


class Runtime:
    def __init__(self, store: Store, settings: Settings, adapters: dict[str, Adapter]):
        self.store, self.settings, self.adapters = store, settings, adapters
        self.queue: asyncio.Queue[tuple[str, list[Definition], float]] = asyncio.Queue(
            maxsize=settings.queue_capacity + settings.workers
        )
        self.tasks: list[asyncio.Task[None]] = []
        self.healthy = True

    def start(self) -> None:
        self.store.recover()
        self.tasks = [asyncio.create_task(self.worker()) for _ in range(self.settings.workers)]

    async def stop(self) -> None:
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.store.recover()

    def submit(self, scan_id: str, definitions: list[Definition]) -> None:
        self.queue.put_nowait((scan_id, definitions, monotonic()))

    async def worker(self) -> None:
        while True:
            scan_id, definitions, accepted_at = await self.queue.get()
            try:
                if not self.healthy:
                    return
                await self.process(scan_id, definitions, accepted_at)
            except Exception:
                # Fail closed on storage/worker failure; recovery interrupts durable work.
                self.healthy = False
                return
            finally:
                self.queue.task_done()

    async def process(
        self, scan_id: str, definitions: list[Definition], accepted_at: float
    ) -> None:
        scan = self.store.get(scan_id)
        scan.state = "running"
        self.store.save(scan)
        for run, definition in zip(scan.runs, definitions, strict=True):
            start = monotonic()
            remaining = self.settings.job_deadline_seconds - (start - accepted_at)
            run.state = "running"
            self.store.save(scan)
            context = Context(self.store, scan, run, definition)
            try:
                if remaining <= 0:
                    raise ProviderError("provider_timeout")
                async with asyncio.timeout(min(remaining, self.settings.stage_timeout_seconds)):
                    result = await self.adapters[definition.adapter].extract(context)
                postprocess = monotonic()
                payment = review_payment(result.payment, result.evidence)
                # Validate adapter links before publishing any payment.
                checked = Run.model_validate(
                    {
                        **run.model_dump(),
                        "state": "completed",
                        "payment": payment.model_dump(),
                        "evidence": [e.model_dump() for e in result.evidence],
                    }
                )
                if any(
                    e.image_id != scan.input.image_id
                    or (e.grounding == "synthetic_fixture" and not definition.synthetic)
                    for e in checked.evidence
                ):
                    raise ProviderError("invalid_provider_output")
                run.payment, run.evidence = checked.payment, checked.evidence
                run.diagnostics.routing = result.routing
                run.diagnostics.validation = [
                    Finding(
                        code="account_ownership",
                        path="/candidates",
                        status="not_checked",
                        message="Format and completeness do not verify account ownership.",
                    )
                ]
                run.state = "completed"
                run.diagnostics.timings_ms.postprocess = (monotonic() - postprocess) * 1000
            except (TimeoutError, ProviderError, ValidationError) as exc:
                code = (
                    exc.code
                    if isinstance(exc, ProviderError)
                    else "provider_timeout"
                    if isinstance(exc, TimeoutError)
                    else "invalid_provider_output"
                )
                run.state = "failed"
                run.error = Error(
                    code=code,
                    message="Profile execution did not produce a valid result; no automatic retry.",
                    details={
                        "stage_id": run.diagnostics.stages[-1].id
                        if run.diagnostics.stages
                        else None
                    },
                )
            except Exception:
                run.state = "failed"
                run.error = Error(
                    code="internal_error",
                    message="Profile execution failed; diagnostic contents are private.",
                )
            if not definition.synthetic:
                t = run.diagnostics.timings_ms
                t.queue = (start - accepted_at) * 1000
                t.preprocess = context.preprocess_ms
                t.total = (monotonic() - accepted_at) * 1000 + context.preprocess_ms
                times = [s.duration_ms for s in run.diagnostics.stages if s.execution == "external"]
                t.provider = (
                    sum(v for v in times if v is not None)
                    if times and all(v is not None for v in times)
                    else None
                )
            else:
                from backend.models import Timings

                run.diagnostics.timings_ms = Timings()
            if scan.mode == "extract" and run.state == "completed":
                scan.final_result_id = run.id
            self.store.reconcile(run)
            self.store.save(scan)
        states = [run.state for run in scan.runs]
        scan.state = (
            "completed"
            if all(s == "completed" for s in states)
            else "partially_completed"
            if "completed" in states
            else "failed"
        )
        self.store.save(scan)
