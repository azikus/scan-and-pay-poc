"""Prepare every source outside the image-only backend, retaining failures and provenance."""

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

from backend.images import sha256
from backend.store import private_write
from evaluation.approved import validate_inputs


def inventory(samples: Path) -> list[Path]:
    return sorted(p for p in samples.rglob("*") if p.is_file() and p.name != ".DS_Store")


def prepare(
    root: Path,
    samples: Path,
    output: Path,
) -> dict[str, Any]:
    sources, inputs = [], []
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    for source in inventory(samples):
        relative = source.relative_to(root).as_posix()
        digest = sha256(source.read_bytes())
        source_id = "source-" + sha256(relative.encode())[:16]
        record = {"id": source_id, "path": relative, "sha256": digest}
        sources.append(record)
        if source.suffix.lower() == ".json":
            record["kind"] = "provenance_sidecar"
            continue
        record["kind"] = "document"
        folder = output / source_id
        folder.mkdir(mode=0o700)
        try:
            pages, transform = [source], "supplied_image"
            for page, path in enumerate(pages, 1):
                with Image.open(path) as img:
                    img.load()
                    if img.format not in {"PNG", "JPEG"}:
                        raise ValueError("Unsupported format")
                    width, height = img.size
                if path.is_relative_to(output):
                    path.chmod(0o600)
                inputs.append(
                    {
                        "id": f"{source_id}-p{page}",
                        "source_id": source_id,
                        "page": page,
                        "group_id": source_id,
                        "cohort": "unreviewed",
                        "variant": transform,
                        "split": "unassigned",
                        "labels_verified": False,
                        "path": path.relative_to(root).as_posix(),
                        "sha256": sha256(path.read_bytes()),
                        "width": width,
                        "height": height,
                        "status": "prepared",
                        "failure": None,
                    }
                )
        except (OSError, ValueError):
            # Retain successfully prepared pages and a source-level failure; never silently omit.
            inputs.append(
                {
                    "id": source_id + "-failure",
                    "source_id": source_id,
                    "page": None,
                    "group_id": source_id,
                    "status": "preparation_failed",
                    "failure": "preparation_failed",
                    "path": None,
                    "sha256": None,
                }
            )
    manifest = {
        "version": 1,
        "samples_path": samples.relative_to(root).as_posix(),
        "scoring_allowed": False,
        "sources": sources,
        "inputs": inputs,
    }
    private_write(output / "manifest.json", json.dumps(manifest, indent=2).encode())
    return manifest


def validate_manifest(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("kind") == "approved_inventory":
        validate_inputs(root, manifest["inputs"])
        if len({i["id"] for i in manifest["inputs"]}) != len(manifest["inputs"]):
            raise ValueError("Manifest has duplicate input IDs")
        return
    actual = {p.relative_to(root).as_posix() for p in inventory(root / manifest["samples_path"])}
    if actual != {s["path"] for s in manifest["sources"]}:
        raise ValueError("Source inventory changed; prepare a new manifest")
    ids = [i["id"] for i in manifest["inputs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Manifest has duplicate input IDs")
    accounted = {i["source_id"] for i in manifest["inputs"]}
    for source in manifest["sources"]:
        if source["kind"] != "provenance_sidecar" and source["id"] not in accounted:
            raise ValueError("Source missing input/failure record")
    for item in [*manifest["sources"], *manifest["inputs"]]:
        if item.get("path") and sha256((root / item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError("Manifest bytes changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=Path, required=True, help="Directory of prepared images")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path.cwd()
    manifest = prepare(root, root / args.samples, root / args.output)
    print(
        json.dumps(
            {
                "sources": len(manifest["sources"]),
                "inputs": len(manifest["inputs"]),
                "prepared": sum(i["status"] == "prepared" for i in manifest["inputs"]),
            }
        )
    )


if __name__ == "__main__":
    main()
