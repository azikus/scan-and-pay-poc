"""Private, bounded observation channel. Never contains payment fields or provider bodies."""

import asyncio
import json
import logging
import threading
import time
from collections.abc import AsyncIterator, Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Literal, cast
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import Field, model_validator

from backend.errors import ServiceError
from backend.models import Model, Scan, Stage

PhonePhase = Literal[
    "idle",
    "crop",
    "preview",
    "preparing",
    "uploading",
    "queued",
    "reading",
    "review",
    "confirmation",
    "recovery",
    "failed",
    "paused",
]


class PhoneState(Model):
    sequence: int = Field(ge=1, le=9007199254740991)
    journey_id: UUID | None = None
    phase: PhonePhase

    @model_validator(mode="after")
    def journey_required(self) -> "PhoneState":
        if self.phase not in {"idle", "paused"} and self.journey_id is None:
            raise ValueError("An active phase requires a journey")
        return self


class DemoHub:
    """Single-owner state, independent of scan storage and spend accounting.

    All updates have one revision boundary. Streams always start with a complete
    snapshot; reconnect never animates historical events. A stale cursor therefore
    requires no unbounded replay log. Phone sequence numbers reject late snapshots.
    """

    def __init__(self, path: Path, *, ttl: float = 28800, clock: Callable[[], float] = time.time):
        self.path, self.ttl, self.clock = path, ttl, clock
        self.lock = threading.RLock()
        self.revision = 0
        self.sessions: dict[str, Any] = {}
        self.bindings: dict[str, Any] = {}
        self.writer = ThreadPoolExecutor(max_workers=1, thread_name_prefix="demo-state")
        self.dirty = False
        self.writing = False
        try:
            data = json.loads(path.read_text())
            if data.get("version") == 1:
                self.revision = int(data["revision"])
                self.sessions = data["sessions"]
                self.bindings = data["bindings"]
                self._prune()
                for state in self.sessions.values():
                    state["last_seen"] = 0  # A restart is not evidence the phone is connected.
                    if state["backend"] in {
                        "queued",
                        "running",
                        "request",
                        "response",
                        "validation",
                        "local",
                    }:
                        state["backend"] = "interrupted"
                self.revision += 1
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            self.sessions, self.bindings = {}, {}

    def _prune(self) -> None:
        cutoff = self.clock() - self.ttl
        self.sessions = {k: v for k, v in self.sessions.items() if v["updated_at"] > cutoff}
        self.bindings = {k: v for k, v in self.bindings.items() if v["at"] > cutoff}
        while len(self.sessions) > 8:
            del self.sessions[min(self.sessions, key=lambda k: self.sessions[k]["updated_at"])]
        while len(self.bindings) > 128:
            del self.bindings[min(self.bindings, key=lambda k: self.bindings[k]["at"])]

    def _new(self, sid: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self.sessions.setdefault(
                sid,
                {
                    "session_id": sid,
                    "journey_id": None,
                    "phone_sequence": 0,
                    "phone": "paused",
                    "backend": "none",
                    "last_seen": 0,
                    "updated_at": self.clock(),
                    "scan_id": None,
                    "profiles": [],
                    "stages": [],
                    "events": [],
                    "completed_at": None,
                    "outcome": None,
                },
            ),
        )

    def _event(self, state: dict[str, Any], source: str, kind: str, **meta: Any) -> None:
        self.revision += 1
        now = self.clock()
        state["updated_at"] = now
        state["events"] = (
            state["events"]
            + [
                {
                    "version": 1,
                    "event_id": str(uuid4()),
                    "sequence": self.revision,
                    "session_id": state["session_id"],
                    "journey_id": state["journey_id"],
                    "scan_id": state["scan_id"],
                    "source": source,
                    "kind": kind,
                    "server_time": now,
                    **meta,
                }
            ]
        )[-64:]
        self._prune()
        # Coalesce writes off the extraction/event-loop thread. The queue is bounded
        # to one writer and one latest state, even during a slow disk or event burst.
        self.dirty = True
        if not self.writing:
            self.writing = True
            self.writer.submit(self._persist)

    def _persist(self) -> None:
        while True:
            with self.lock:
                if not self.dirty:
                    self.writing = False
                    return
                self.dirty = False
                data = json.dumps(
                    {
                        "version": 1,
                        "revision": self.revision,
                        "sessions": self.sessions,
                        "bindings": self.bindings,
                    }
                ).encode()
            try:
                from backend.store import private_write

                private_write(self.path, data)
            except (OSError, ValueError):
                logging.getLogger(__name__).warning("Demo state persistence unavailable")

    def close(self) -> None:
        self.writer.shutdown(wait=True)

    def phone(self, sid: str, body: PhoneState) -> None:
        with self.lock:
            self._prune()
            state = self._new(sid)
            if body.sequence <= state["phone_sequence"]:
                return
            journey = str(body.journey_id) if body.journey_id else state["journey_id"]
            if journey != state["journey_id"]:
                state.update(
                    journey_id=journey,
                    backend="none",
                    scan_id=None,
                    profiles=[],
                    stages=[],
                    outcome=None,
                )
                if journey is not None:
                    state["completed_at"] = None
            state.update(phone_sequence=body.sequence, phone=body.phase, last_seen=self.clock())
            self._event(state, "phone", body.phase)

    def bind(self, scan: Scan, sid: str, journey: str) -> None:
        with self.lock:
            self._prune()
            if scan.scan_id in self.bindings:
                return  # Immutable binding, including idempotent uploads.
            self.bindings[scan.scan_id] = {"session": sid, "journey": journey, "at": self.clock()}
            state = self._new(sid)
            if state["journey_id"] is None and state["phone_sequence"] == 0:
                state["journey_id"] = journey
            if state["journey_id"] != journey:
                return
            state.update(
                scan_id=scan.scan_id,
                backend=scan.state,
                profiles=[
                    {"id": run.profile_id, "version": run.profile_version} for run in scan.runs
                ],
            )
            self._event(state, "backend", "accepted")

    def backend(
        self,
        scan_id: str,
        kind: str,
        stage: Stage | None = None,
        outcome: str | None = None,
        run_id: str | None = None,
    ) -> None:
        with self.lock:
            self._prune()
            binding = self.bindings.get(scan_id)
            if not binding:
                return
            state = self.sessions.get(binding["session"])
            if (
                not state
                or state["journey_id"] != binding["journey"]
                or state["scan_id"] != scan_id
            ):
                return
            if kind == "confirmed":
                if state["completed_at"] is not None:
                    return
                state["completed_at"] = self.clock()
            else:
                state["backend"] = kind
            if stage is not None:
                safe_stage = {
                    "id": stage.id,
                    "run_id": run_id,
                    "method": stage.method,
                    "execution": stage.execution,
                    "provider": stage.provider,
                    "model": stage.requested_model,
                    "state": kind,
                }
                state["stages"] = [s for s in state["stages"] if s["id"] != stage.id] + [safe_stage]
                state["stages"] = state["stages"][-16:]
            if outcome is not None:
                state["outcome"] = outcome
            self._event(state, "backend", kind, stage_id=stage.id if stage else None, run_id=run_id)

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            self._prune()
            # Deep copy: streaming consumers cannot mutate the live projection.
            return cast(
                dict[str, Any],
                json.loads(
                    json.dumps(
                        {
                            "version": 1,
                            "revision": self.revision,
                            "server_time": self.clock(),
                            "sessions": list(self.sessions.values()),
                        }
                    )
                ),
            )


def observe(hub: DemoHub | None, method: str, *args: Any, **kwargs: Any) -> None:
    """Observation is best-effort even if storage or a future observer breaks."""
    if hub is not None:
        try:
            getattr(hub, method)(*args, **kwargs)
        except Exception:
            logging.getLogger(__name__).warning("Demo observation unavailable")


def install_routes(app: FastAPI, auth: Callable[..., None]) -> None:
    assets = Path(__file__).parent / "demo_assets"
    if not assets.is_dir():
        assets = Path(__file__).parent.parent / "frontend/demo"

    @app.get("/demo", include_in_schema=False)
    async def shell() -> FileResponse:
        return FileResponse(assets / "index.html")

    @app.get("/demo/assets/{name}", include_in_schema=False)
    async def asset(name: str) -> FileResponse:
        if name not in {
            "demo.css",
            "demo.js",
            "state.js",
            "qr.png",
            "logo.svg",
            "HankenGrotesk-Regular.ttf",
            "HankenGrotesk-Semibold.ttf",
        }:
            raise ServiceError(404, "not_found", "Asset not found.")
        return FileResponse(assets / name)

    @app.put("/v1/demo/sessions/{session_id}", dependencies=[Depends(auth)])
    async def phone(session_id: UUID, body: PhoneState, request: Request) -> dict[str, bool]:
        observe(request.app.state.demo, "phone", str(session_id), body)
        return {"received": True}

    @app.get("/v1/demo/snapshot", dependencies=[Depends(auth)])
    async def snapshot(request: Request) -> dict[str, Any]:
        return request.app.state.demo.snapshot()  # type: ignore[no-any-return]

    @app.get(
        "/v1/demo/events",
        dependencies=[Depends(auth)],
        response_class=StreamingResponse,
        responses={200: {"content": {"text/event-stream": {}}}},
    )
    async def events(request: Request, after: int = Query(default=0, ge=0)) -> StreamingResponse:
        async def stream() -> AsyncIterator[str]:
            revision = -1  # Always resync, even when a last-seen cursor is supplied.
            last_sent = 0.0
            while not await request.is_disconnected():
                current = request.app.state.demo.snapshot()
                if current["revision"] != revision or time.monotonic() - last_sent > 10:
                    revision, last_sent = current["revision"], time.monotonic()
                    yield f"id: {revision}\nevent: snapshot\ndata: {json.dumps(current)}\n\n"
                await asyncio.sleep(0.25)

        return StreamingResponse(
            stream(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no"}
        )
