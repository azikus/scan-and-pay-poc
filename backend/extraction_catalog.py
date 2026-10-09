"""Read-only method guide and dated, aggregate benchmark evidence for the inspector."""

from pathlib import Path

from backend.models import Model


class MethodGuide(Model):
    id: str
    title: str
    description: str
    options: list[str]


class Benchmark(Model):
    profile: str
    profile_version: str
    provider: str
    model: str
    median_seconds: float
    p95_seconds: float
    timing_n: int
    timeouts: int
    error: int
    accepted_readable: int
    readable_total: int
    critical_matches: int
    critical_total: int


class ExtractionCatalog(Model):
    measured_on: str
    measurement_note: str
    methods: list[MethodGuide]
    benchmarks: list[Benchmark]
    deferred: list[str]


def catalog() -> ExtractionCatalog:
    return ExtractionCatalog.model_validate_json(
        Path(__file__).with_name("extraction_catalog.json").read_text()
    )
