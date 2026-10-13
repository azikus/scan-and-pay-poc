import io
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal
from threading import Event

import pytest
from PIL import Image

from backend.errors import ServiceError
from backend.images import prepare_image
from backend.models import Hints, Options
from backend.store import Store, request_digest


def test_concurrent_readiness_checks_do_not_interfere(settings, monkeypatch):
    import backend.store as module

    store = Store(settings)
    first_written = Event()
    second_finished = Event()
    write = module.private_write

    def overlapping_write(path, data):
        write(path, data)
        if not first_written.is_set():
            first_written.set()
            assert second_finished.wait(timeout=5)

    def second_check():
        assert first_written.wait(timeout=5)
        try:
            return store.ready()
        finally:
            second_finished.set()

    monkeypatch.setattr(module, "private_write", overlapping_write)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            checks = [pool.submit(store.ready), pool.submit(second_check)]
            assert all(check.result(timeout=10) for check in checks)
        assert not list(store.root.glob("health-probe*"))
    finally:
        store.close()


def test_orientation_metadata_and_decode_safety(png, monkeypatch):
    source = Image.new("RGB", (10, 20), "white")
    exif = Image.Exif()
    exif[274] = 6
    exif[270] = "Private camera metadata"
    stream = io.BytesIO()
    source.save(stream, "JPEG", exif=exif)
    prepared = prepare_image(stream.getvalue(), Hints())
    assert (prepared.identity.width, prepared.identity.height) == (20, 10)
    canonical = Image.open(io.BytesIO(prepared.canonical))
    assert not canonical.getexif() and not canonical.info
    assert prepared.identity.original_sha256 != prepared.identity.canonical_sha256
    assert "exif_orientation:6" in prepared.transforms
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 100)
    with pytest.raises(ServiceError) as e:
        prepare_image(png, Hints())
    assert e.value.status == 400


def test_gif_animated_png_and_truncated(png):
    for fmt in ("GIF", "PNG"):
        stream = io.BytesIO()
        Image.new("RGB", (10, 10), "red").save(
            stream, fmt, save_all=True, append_images=[Image.new("RGB", (10, 10), "green")]
        )
        with pytest.raises(ServiceError) as e:
            prepare_image(stream.getvalue(), Hints())
        assert e.value.status == 415
    with pytest.raises(ServiceError) as e:
        prepare_image(png[:40], Hints())
    assert e.value.status == 400


def test_compare_accepts_above_legacy_limits_and_preserves_existing_records(
    settings, definitions, png
):
    settings.max_calls = 0
    settings.smoke_budget_eur = Decimal("0")
    store = Store(settings)
    try:
        with store.connection() as db:
            db.execute(
                "INSERT INTO budget(run_id,hold_microeur,dispatched,cost) VALUES(?,?,?,?)",
                ("historical", 900_000_000, 1, '{"status":"unknown"}'),
            )
            original = dict(db.execute("SELECT * FROM budget WHERE run_id='historical'").fetchone())
        image = prepare_image(png, Hints())
        options = Options(mode="compare", profiles=["success", "failure"])
        ds = [replace(d, synthetic=False, ceiling_eur=Decimal("20")) for d in definitions.values()]
        scan, created = store.accept("k", request_digest(png, options), image, options, ds, [])
        assert created and len(scan.runs) == 2
        again, created = store.accept("k", request_digest(png, options), image, options, ds, [])
        assert not created and again.scan_id == scan.scan_id
        with store.connection() as db:
            assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
            assert db.execute("SELECT COUNT(*) FROM budget").fetchone()[0] == 3
            assert (
                dict(db.execute("SELECT * FROM budget WHERE run_id='historical'").fetchone())
                == original
            )
    finally:
        store.close()


def test_call_count_and_missing_ceiling_do_not_block_acceptance(settings, definitions, png):
    settings.max_calls = 1
    store = Store(settings)
    try:
        image = prepare_image(png, Hints())
        options = Options(mode="extract", profiles=["success"])
        d = replace(definitions["success"], synthetic=False, ceiling_eur=Decimal("1"))
        one, _ = store.accept("one", request_digest(png, options), image, options, [d], [])
        two, _ = store.accept("two", request_digest(png, options), image, options, [d], [])
        assert one.scan_id != two.scan_id
        store.recover()
        three, created = store.accept(
            "three",
            request_digest(png, options),
            image,
            options,
            [replace(d, ceiling_eur=Decimal("0"))],
            [],
        )
        assert created and three.state == "queued"
    finally:
        store.close()


def test_single_owner_and_recovery_retains_billed_hold(settings, definitions, png):
    store = Store(settings)
    try:
        with pytest.raises(RuntimeError):
            Store(settings)
        assert store.ready()
        assert store.db_path.stat().st_mode & 0o777 == 0o600
        options = Options(mode="extract", profiles=["success"])
        image = prepare_image(png, Hints())
        d = replace(definitions["success"], synthetic=False, ceiling_eur=Decimal("2"))
        scan, _ = store.accept("k", request_digest(png, options), image, options, [d], [])
        store.mark_dispatched(scan.runs[0].id)
        store.recover()
        assert store.get(scan.scan_id).state == "interrupted"
        store.delete(scan.scan_id)
        with store.connection() as db:
            row = db.execute("SELECT * FROM idempotency").fetchone()
            assert row["deleted"] == 1 and row["scan_id"] is None
            assert set(row.keys()) == {"key_hash", "digest", "scan_id", "deleted"}
            assert db.execute("SELECT SUM(hold_microeur) FROM budget").fetchone()[0] == 2_000_000
    finally:
        store.close()


def test_acceptance_file_failure_rolls_back(settings, definitions, png, monkeypatch):
    import backend.store as module

    store = Store(settings)
    try:

        def fail(*args):
            raise OSError("disk full")

        monkeypatch.setattr(module, "private_write", fail)
        options = Options(mode="extract", profiles=["success"])
        with pytest.raises(OSError):
            store.accept(
                "k",
                request_digest(png, options),
                prepare_image(png, Hints()),
                options,
                [definitions["success"]],
                [],
            )
        assert store.existing("k", request_digest(png, options)) is None
        assert list(store.artifacts.iterdir()) == []
    finally:
        store.close()
