"""Durable single-process store: atomic acceptance, spend holds and deletion tombstones."""

import fcntl
import json
import os
import shutil
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import ROUND_CEILING
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

from backend.client_reviews import (
    ClientReview,
    ClientReviews,
    SavedClientReview,
    ScanList,
    ScanSummary,
    validate_review,
)
from backend.config import Settings
from backend.errors import ServiceError
from backend.images import PreparedImage, sha256
from backend.models import Diagnostics, Error, ExcludedProfile, Options, ProfileRef, Run, Scan
from backend.profiles import Definition
from backend.scan_artifacts import ScanArtifacts, read_artifacts, safe_file, scan_directory

if TYPE_CHECKING:
    from backend.demo_events import DemoHub


def utcnow() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def private_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + ".tmp")
    with os.fdopen(os.open(temporary, os.O_CREAT | os.O_TRUNC | os.O_WRONLY, 0o600), "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)


def request_digest(data: bytes, options: Options) -> str:
    canonical = json.dumps(options.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return sha256((sha256(data) + "\n" + canonical).encode())


class Store:
    def __init__(self, settings: Settings):
        self.demo: DemoHub | None = None
        self.settings = settings
        self.root = settings.data_dir.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.root.chmod(0o700)
        self.artifacts = self.root / "jobs"
        self.artifacts.mkdir(exist_ok=True, mode=0o700)
        self._lock_file = (self.root / "owner.lock").open("a+")
        os.chmod(self.root / "owner.lock", 0o600)
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            raise RuntimeError("Only one API process may own this data directory") from None
        self.db_path = self.root / "jobs.sqlite3"
        self._mutex = threading.RLock()
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=DELETE")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, state TEXT NOT NULL, body TEXT NOT NULL,
                    options TEXT NOT NULL, snapshots TEXT NOT NULL, transforms TEXT NOT NULL,
                    preprocess_ms REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS idempotency (
                    key_hash TEXT PRIMARY KEY, digest TEXT NOT NULL,
                    scan_id TEXT, deleted INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY, run_id TEXT UNIQUE, hold_microeur INTEGER NOT NULL,
                    dispatched INTEGER NOT NULL DEFAULT 0, cost TEXT
                );
                CREATE TABLE IF NOT EXISTS stage_reservations (
                    run_id TEXT NOT NULL, slot INTEGER NOT NULL, budget_key TEXT NOT NULL UNIQUE,
                    stage_id TEXT, PRIMARY KEY(run_id, slot)
                );
                CREATE TABLE IF NOT EXISTS validated_profiles (
                    profile_id TEXT NOT NULL, version TEXT NOT NULL, validated_at TEXT NOT NULL,
                    PRIMARY KEY(profile_id, version)
                );
                CREATE TABLE IF NOT EXISTS stages (
                    id TEXT PRIMARY KEY, scan_id TEXT NOT NULL, run_id TEXT NOT NULL,
                    started_at TEXT NOT NULL, finished_at TEXT, body TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scan_sources (
                    scan_id TEXT PRIMARY KEY, source TEXT NOT NULL CHECK(source IN ('mobile','automated'))
                );
                CREATE TABLE IF NOT EXISTS client_reviews (
                    scan_id TEXT NOT NULL, id TEXT NOT NULL, body TEXT NOT NULL,
                    PRIMARY KEY(scan_id, id)
                );
                CREATE TABLE IF NOT EXISTS mobile_selection (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                    profile_id TEXT NOT NULL, version TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS backend_identity (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1), id TEXT NOT NULL
                );
            """)
            db.execute("INSERT OR IGNORE INTO backend_identity VALUES(1,?)", (str(uuid4()),))
            self.backend_id: str = db.execute(
                "SELECT id FROM backend_identity WHERE singleton=1"
            ).fetchone()[0]
        self.db_path.chmod(0o600)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        with self._mutex:
            db = sqlite3.connect(self.db_path, timeout=5)
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA secure_delete=ON")
            db.execute("PRAGMA synchronous=FULL")
            try:
                with db:
                    yield db
            finally:
                db.close()

    def close(self) -> None:
        self._lock_file.close()

    def mobile_selection(self) -> ProfileRef | None:
        with self.connection() as db:
            row = db.execute(
                "SELECT profile_id,version FROM mobile_selection WHERE singleton=1"
            ).fetchone()
        return ProfileRef(id=row["profile_id"], version=row["version"]) if row else None

    def select_mobile_profile(self, selection: ProfileRef) -> None:
        with self.connection() as db:
            db.execute(
                "INSERT INTO mobile_selection VALUES(1,?,?) "
                "ON CONFLICT(singleton) DO UPDATE SET profile_id=excluded.profile_id,version=excluded.version",
                (selection.id, selection.version),
            )

    def ready(self) -> bool:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("SELECT 1 FROM jobs LIMIT 1")
        probe = self.root / f"health-probe-{uuid4().hex}"
        private_write(probe, b"ok")
        probe.unlink()
        return True

    @staticmethod
    def _existing(db: sqlite3.Connection, key: str, digest: str) -> Scan | None:
        row = db.execute(
            "SELECT * FROM idempotency WHERE key_hash=?", (sha256(key.encode()),)
        ).fetchone()
        if row is None:
            return None
        if row["deleted"]:
            raise ServiceError(
                410, "deleted_key", "This idempotency key belongs to a deleted scan."
            )
        if row["digest"] != digest:
            raise ServiceError(
                409, "idempotency_conflict", "Idempotency key was already used for different input."
            )
        job = db.execute("SELECT body FROM jobs WHERE id=?", (row["scan_id"],)).fetchone()
        return Scan.model_validate_json(job["body"])

    def existing(self, key: str, digest: str) -> Scan | None:
        with self.connection() as db:
            return self._existing(db, key, digest)

    def accept(
        self,
        key: str,
        digest: str,
        image: PreparedImage,
        options: Options,
        definitions: list[Definition],
        excluded: list[ExcludedProfile],
        source: Literal["mobile", "automated"] = "automated",
    ) -> tuple[Scan, bool]:
        scan_id = "scan-" + uuid4().hex
        created_dir = False
        try:
            with self.connection() as db:
                db.execute("BEGIN IMMEDIATE")
                existing = self._existing(db, key, digest)
                if existing:
                    return existing, False
                active = db.execute(
                    "SELECT COUNT(*) FROM jobs WHERE state IN ('queued','running')"
                ).fetchone()[0]
                if active >= self.settings.queue_capacity + self.settings.workers:
                    raise ServiceError(429, "queue_full", "The bounded job queue is full.", True)
                holds = [
                    int((ceiling * 1_000_000).to_integral_value(rounding=ROUND_CEILING))
                    for d in definitions
                    if not d.synthetic
                    for ceiling in d.reservations
                ]
                used, count = db.execute(
                    "SELECT COALESCE(SUM(hold_microeur),0), COUNT(*) FROM budget"
                ).fetchone()
                if holds and (
                    used + sum(holds) > int(self.settings.smoke_budget_eur * 1_000_000)
                    or count + len(holds) > self.settings.max_calls
                    or any(h <= 0 for h in holds)
                ):
                    raise ServiceError(
                        422,
                        "budget_exceeded",
                        "The entire batch exceeds the remaining call or EUR reservation budget.",
                    )
                now = utcnow()
                runs = [
                    Run(
                        id="run-" + uuid4().hex,
                        profile_id=d.metadata.id,
                        profile_version=d.metadata.version,
                        diagnostics=Diagnostics(
                            requested_model=d.metadata.model or d.metadata.processor,
                            versions={
                                "schema": "1.0",
                                "adapter": d.adapter + "@1",
                                "review": "1",
                                **{k: str(v) for k, v in d.parameters.items()},
                            },
                        ),
                    )
                    for d in definitions
                ]
                scan = Scan(
                    execution_kind="synthetic_fixture" if definitions[0].synthetic else "live",
                    scan_id=scan_id,
                    mode=options.mode,
                    created_at=now,
                    updated_at=now,
                    input=image.identity,
                    resolved_profiles=[
                        ProfileRef(id=d.metadata.id, version=d.metadata.version)
                        for d in definitions
                    ],
                    excluded_profiles=excluded,
                    runs=runs,
                )
                created_dir = True
                private_write(self.artifacts / scan_id / "original", image.original)
                private_write(self.artifacts / scan_id / "canonical.png", image.canonical)
                db.execute(
                    "INSERT INTO jobs VALUES(?,?,?,?,?,?,?)",
                    (
                        scan_id,
                        scan.state,
                        scan.model_dump_json(),
                        options.model_dump_json(),
                        json.dumps([d.snapshot() for d in definitions]),
                        json.dumps(image.transforms),
                        image.duration_ms,
                    ),
                )
                db.execute(
                    "INSERT INTO idempotency(key_hash,digest,scan_id) VALUES(?,?,?)",
                    (sha256(key.encode()), digest, scan_id),
                )
                db.execute("INSERT INTO scan_sources VALUES(?,?)", (scan_id, source))
                for run, d in zip(runs, definitions, strict=True):
                    if not d.synthetic:
                        for slot, ceiling in enumerate(d.reservations):
                            hold = int(
                                (ceiling * 1_000_000).to_integral_value(rounding=ROUND_CEILING)
                            )
                            budget_key = f"{run.id}:{slot}" if d.stages else run.id
                            db.execute(
                                "INSERT INTO budget(run_id,hold_microeur) VALUES(?,?)",
                                (budget_key, hold),
                            )
                            if d.stages:
                                db.execute(
                                    "INSERT INTO stage_reservations(run_id,slot,budget_key) VALUES(?,?,?)",
                                    (run.id, slot, budget_key),
                                )
                return scan, True
        except BaseException:
            if created_dir:
                shutil.rmtree(self.artifacts / scan_id, ignore_errors=True)
            raise

    def get(self, scan_id: str) -> Scan:
        with self.connection() as db:
            row = db.execute("SELECT body FROM jobs WHERE id=?", (scan_id,)).fetchone()
            if row is None:
                raise ServiceError(404, "not_found", "Scan not found.")
            return Scan.model_validate_json(row["body"])

    def save(self, scan: Scan) -> None:
        scan.updated_at = utcnow()
        # Validate nested invariants after mutable orchestration changes.
        checked = Scan.model_validate(scan.model_dump())
        with self.connection() as db:
            db.execute(
                "UPDATE jobs SET state=?,body=? WHERE id=?",
                (checked.state, checked.model_dump_json(), checked.scan_id),
            )

    def list_scans(
        self, limit: int, offset: int, source: Literal["mobile", "automated"] | None = None
    ) -> ScanList:
        with self.connection() as db:
            rows = db.execute(
                "SELECT body, COALESCE(s.source, 'automated') AS source, "
                "(SELECT COUNT(*) FROM client_reviews r WHERE r.scan_id=j.id) AS reviews "
                "FROM jobs j LEFT JOIN scan_sources s ON s.scan_id=j.id "
                "WHERE (? IS NULL OR COALESCE(s.source, 'automated')=?) "
                "ORDER BY json_extract(body, '$.created_at') DESC, j.id DESC LIMIT ? OFFSET ?",
                (source, source, limit + 1, offset),
            ).fetchall()
        summaries = []
        for row in rows[:limit]:
            scan = Scan.model_validate_json(row["body"])
            summaries.append(
                ScanSummary(
                    scan_id=scan.scan_id,
                    created_at=scan.created_at,
                    state=scan.state,
                    execution_kind=scan.execution_kind,
                    source=row["source"],
                    outcomes=[r.result_outcome for r in scan.runs],
                    profiles=[p.id for p in scan.resolved_profiles],
                    client_review_count=row["reviews"],
                )
            )
        return ScanList(scans=summaries, next_offset=offset + limit if len(rows) > limit else None)

    def client_reviews(self, scan_id: str) -> ClientReviews:
        with self.connection() as db:
            if db.execute("SELECT 1 FROM jobs WHERE id=?", (scan_id,)).fetchone() is None:
                raise ServiceError(404, "not_found", "Scan not found.")
            rows = db.execute(
                "SELECT body FROM client_reviews WHERE scan_id=? ORDER BY rowid", (scan_id,)
            ).fetchall()
        return ClientReviews(reviews=[SavedClientReview.model_validate_json(r[0]) for r in rows])

    def save_client_review(
        self, scan_id: str, review_id: str, review: ClientReview
    ) -> SavedClientReview:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT body FROM jobs WHERE id=?", (scan_id,)).fetchone()
            if row is None:
                raise ServiceError(404, "not_found", "Scan not found.")
            scan = Scan.model_validate_json(row[0])
            validate_review(scan, review)
            existing = db.execute(
                "SELECT body FROM client_reviews WHERE scan_id=? AND id=?", (scan_id, review_id)
            ).fetchone()
            if existing:
                saved = SavedClientReview.model_validate_json(existing[0])
                if (
                    ClientReview.model_validate(
                        saved.model_dump(include=set(ClientReview.model_fields))
                    )
                    != review
                ):
                    raise ServiceError(
                        409, "review_conflict", "This review ID has different values."
                    )
                return saved
            saved = SavedClientReview(
                **review.model_dump(), id=review_id, scan_id=scan_id, received_at=utcnow()
            )
            db.execute(
                "INSERT INTO client_reviews VALUES(?,?,?)",
                (scan_id, review_id, saved.model_dump_json()),
            )
            return saved

    def preprocessing(self, scan_id: str) -> tuple[list[str], float]:
        with self.connection() as db:
            row = db.execute(
                "SELECT transforms,preprocess_ms FROM jobs WHERE id=?", (scan_id,)
            ).fetchone()
            return json.loads(row["transforms"]), row["preprocess_ms"]

    def mark_dispatched(
        self, run_id: str, slot: int | None = None, stage_id: str | None = None
    ) -> None:
        with self.connection() as db:
            if slot is None:
                db.execute("UPDATE budget SET dispatched=1 WHERE run_id=?", (run_id,))
                return
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT budget_key,stage_id FROM stage_reservations WHERE run_id=? AND slot=?",
                (run_id, slot),
            ).fetchone()
            if row is None or row["stage_id"] is not None:
                raise RuntimeError("Missing or already dispatched stage reservation")
            db.execute("UPDATE budget SET dispatched=1 WHERE run_id=?", (row["budget_key"],))
            db.execute(
                "UPDATE stage_reservations SET stage_id=? WHERE run_id=? AND slot=?",
                (stage_id, run_id, slot),
            )

    @staticmethod
    def release_undispatched(db: sqlite3.Connection, run_id: str) -> None:
        db.execute(
            "DELETE FROM budget WHERE dispatched=0 AND (run_id=? OR run_id IN (SELECT budget_key FROM stage_reservations WHERE run_id=?))",
            (run_id, run_id),
        )

    def record_stages(self, scan: Scan, run: Run) -> None:
        with self.connection() as db:
            for stage in run.diagnostics.stages:
                db.execute(
                    "INSERT INTO stages VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET finished_at=COALESCE(stages.finished_at,excluded.finished_at),body=excluded.body",
                    (
                        stage.id,
                        scan.scan_id,
                        run.id,
                        utcnow(),
                        utcnow() if stage.duration_ms is not None else None,
                        stage.model_dump_json(),
                    ),
                )

    def reconcile(self, run: Run) -> None:
        # Preserve EUR holds even on known USD estimates: no implicit FX or forgiveness.
        with self.connection() as db:
            costs = [
                s.cost.model_dump() for s in run.diagnostics.stages if s.execution == "external"
            ]
            db.execute("UPDATE budget SET cost=? WHERE run_id=?", (json.dumps(costs), run.id))
            slots = db.execute(
                "SELECT budget_key,stage_id FROM stage_reservations WHERE run_id=?", (run.id,)
            ).fetchall()
            for slot in slots:
                stage = next((s for s in run.diagnostics.stages if s.id == slot["stage_id"]), None)
                if stage is not None:
                    db.execute(
                        "UPDATE budget SET cost=? WHERE run_id=?",
                        (stage.cost.model_dump_json(), slot["budget_key"]),
                    )
            if slots:
                self.release_undispatched(db, run.id)
            if run.state == "completed" and costs:
                db.execute(
                    "INSERT OR REPLACE INTO validated_profiles VALUES(?,?,?)",
                    (run.profile_id, run.profile_version, utcnow()),
                )

    def is_validated(self, profile_id: str, version: str) -> bool:
        with self.connection() as db:
            return (
                db.execute(
                    "SELECT 1 FROM validated_profiles WHERE profile_id=? AND version=?",
                    (profile_id, version),
                ).fetchone()
                is not None
            )

    def recover(self) -> None:
        with self.connection() as db:
            rows = db.execute(
                "SELECT body FROM jobs WHERE state IN ('queued','running')"
            ).fetchall()
            for row in rows:
                scan = Scan.model_validate_json(row["body"])
                scan.state = "interrupted"
                for run in scan.runs:
                    if run.state in {"queued", "running"}:
                        run.state = "interrupted"
                        run.outcome = "error"
                        run.error = Error(
                            code="interrupted",
                            message="Process stopped; no automatic upstream replay.",
                        )
                        self.release_undispatched(db, run.id)
                scan.updated_at = utcnow()
                db.execute(
                    "UPDATE jobs SET state=?,body=? WHERE id=?",
                    (scan.state, scan.model_dump_json(), scan.scan_id),
                )
            known = {row[0] for row in db.execute("SELECT id FROM jobs")}
            # Only app-owned per-job directories; samples/ and other .local/ assets are untouched.
            for path in self.artifacts.iterdir():
                if path.is_dir() and path.name not in known:
                    shutil.rmtree(path)

    def delete(self, scan_id: str) -> None:
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT body FROM jobs WHERE id=?", (scan_id,)).fetchone()
            if row is None:
                raise ServiceError(404, "not_found", "Scan not found.")
            scan = Scan.model_validate_json(row["body"])
            if scan.state in {"queued", "running"}:
                raise ServiceError(409, "active_scan", "Active scans cannot be deleted.")
            if (self.artifacts / scan_id).exists():
                shutil.rmtree(self.artifacts / scan_id, ignore_errors=False)
            for run in scan.runs:
                self.release_undispatched(db, run.id)
                db.execute(
                    "UPDATE budget SET run_id=NULL WHERE run_id=? OR run_id IN (SELECT budget_key FROM stage_reservations WHERE run_id=?)",
                    (run.id, run.id),
                )
                db.execute("DELETE FROM stage_reservations WHERE run_id=?", (run.id,))
            db.execute("DELETE FROM jobs WHERE id=?", (scan_id,))
            db.execute("DELETE FROM stages WHERE scan_id=?", (scan_id,))
            db.execute("DELETE FROM client_reviews WHERE scan_id=?", (scan_id,))
            db.execute("DELETE FROM scan_sources WHERE scan_id=?", (scan_id,))
            db.execute("UPDATE idempotency SET deleted=1,scan_id=NULL WHERE scan_id=?", (scan_id,))

    def save_raw(self, scan_id: str, run_id: str, value: Any) -> None:
        private_write(
            self.artifacts / scan_id / (run_id + ".raw.json"),
            json.dumps(value, ensure_ascii=False).encode(),
        )

    def scan_source(self, scan_id: str) -> Literal["mobile", "automated"]:
        with self.connection() as db:
            row = db.execute(
                "SELECT source FROM scan_sources WHERE scan_id=?", (scan_id,)
            ).fetchone()
            return "mobile" if row and row[0] == "mobile" else "automated"

    def scan_artifacts(self, scan_id: str) -> ScanArtifacts:
        with self.connection():
            scan = self.get(scan_id)
            return read_artifacts(self.artifacts, scan, self.scan_source(scan_id))

    def mobile_image(self, scan_id: str) -> tuple[bytes, str]:
        with self.connection():
            scan = self.get(scan_id)
            directory = scan_directory(self.artifacts, scan)
            original = directory / "original"
            if self.scan_source(scan_id) != "mobile" or not safe_file(original, directory):
                raise ServiceError(404, "not_found", "Mobile image not found.")
            data = original.read_bytes()
            if sha256(data) != scan.input.original_sha256:
                raise ServiceError(
                    503, "service_unavailable", "The saved image could not be verified."
                )
            return data, scan.input.mime_type
