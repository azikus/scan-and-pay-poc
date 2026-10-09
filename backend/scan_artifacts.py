"""Read retained scan evidence without executing extraction or following supplied paths."""

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, JsonValue

from backend.errors import ServiceError
from backend.models import Model, Scan


class SavedOutput(Model):
    kind: Literal["provider_response", "ocr_document", "llm_input"]
    value: JsonValue = None
    error: str | None = None


class StageOutputs(Model):
    stage_id: str | None
    method: str
    execution: str
    provider: str | None = None
    model: str | None = None
    outputs: list[SavedOutput] = Field(default_factory=list)


class RunOutputs(Model):
    run_id: str
    profile_id: str
    profile_version: str
    state: str
    stages: list[StageOutputs] = Field(default_factory=list)


class ScanArtifacts(Model):
    scan_id: str
    source: Literal["mobile", "automated"]
    runs: list[RunOutputs]


def scan_directory(root: Path, scan: Scan) -> Path:
    directory = root / scan.scan_id
    if directory.is_symlink() or directory.resolve().parent != root.resolve():
        raise ServiceError(404, "not_found", "Scan artifacts not found.")
    return directory


def safe_file(path: Path, directory: Path) -> bool:
    return not path.is_symlink() and path.resolve().parent == directory.resolve() and path.is_file()


def read_output(
    path: Path, kind: Literal["provider_response", "ocr_document", "llm_input"]
) -> SavedOutput:
    try:
        return SavedOutput(kind=kind, value=json.loads(path.read_text()))
    except (OSError, ValueError):
        return SavedOutput(kind=kind, error="This saved output could not be read.")


def read_artifacts(root: Path, scan: Scan, source: Literal["mobile", "automated"]) -> ScanArtifacts:
    directory = scan_directory(root, scan)
    # Only known run/stage names are matched, never arbitrary client-supplied file names.
    files = (
        {p.name: p for p in directory.iterdir() if safe_file(p, directory)}
        if directory.is_dir()
        else {}
    )
    runs = []
    for run in scan.runs:
        record = RunOutputs(
            run_id=run.id,
            profile_id=run.profile_id,
            profile_version=run.profile_version,
            state=run.state,
        )
        external = [s for s in run.diagnostics.stages if s.execution == "external"]
        for stage in run.diagnostics.stages:
            output = StageOutputs(
                stage_id=stage.id,
                method=stage.method,
                execution=stage.execution,
                provider=stage.provider,
                model=stage.returned_model or stage.requested_model,
            )
            prefix = f"{run.id}.{stage.id}."
            raw = [
                p
                for name, p in files.items()
                if name.startswith(prefix) and name.endswith(".raw.json")
            ]
            # mtime keeps asynchronous polling responses in arrival order; UUID names do not.
            raw.sort(key=lambda p: (p.stat().st_mtime_ns, p.name))
            output.outputs.extend(read_output(p, "provider_response") for p in raw)
            if len(external) == 1 and stage.id == external[0].id:
                legacy = files.get(f"{run.id}.raw.json")
                if legacy:
                    output.outputs.append(read_output(legacy, "provider_response"))
            document = files.get(f"{run.id}.{stage.id}.document.json")
            if document:
                output.outputs.append(read_output(document, "ocr_document"))
            interpretation = files.get(f"{run.id}.interpretation-input.json")
            if stage.method == "interpretation" and interpretation:
                output.outputs.append(read_output(interpretation, "llm_input"))
            record.stages.append(output)
        # Historical records without one unambiguous external stage stay run-level.
        legacy = files.get(f"{run.id}.raw.json")
        if legacy and len(external) != 1:
            record.stages.append(
                StageOutputs(
                    stage_id=None,
                    method="unassigned",
                    execution="external",
                    outputs=[read_output(legacy, "provider_response")],
                )
            )
        runs.append(record)
    return ScanArtifacts(scan_id=scan.scan_id, source=source, runs=runs)
