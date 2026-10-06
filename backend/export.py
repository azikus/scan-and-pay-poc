"""Regenerate public synthetic contracts from the Python models; no startup/probes."""

import json
from pathlib import Path

from backend.api import create_app
from backend.models import Scan
from backend.providers import structured_schema


def main() -> None:
    output = Path("contracts/v1")
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "scan-result.schema.json": Scan.model_json_schema(),
        "openapi.json": create_app().openapi(),
        "vision-extraction.schema.json": structured_schema(),
    }
    for name, value in artifacts.items():
        (output / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
