"""Fail-closed input approval for paid evaluation; invoice files remain private."""

import json
import re
from pathlib import Path
from typing import Any

from backend.images import sha256

LOCK_PATH = Path("evaluation/approved-inventory.json")
INVENTORY_PATH = Path(".local/evaluation/active-inventory.json")


def fingerprint(inputs: list[dict[str, Any]]) -> str:
    hashes = [item["sha256"] for item in inputs]
    if not hashes or any(not re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes):
        raise ValueError("Inventory requires SHA-256 image identities")
    if len(hashes) != len(set(hashes)):
        raise ValueError("Duplicate image in approved inventory")
    return sha256("\n".join(sorted(hashes)).encode())


def validate_inputs(root: Path, inputs: list[dict[str, Any]]) -> None:
    """Reject changed membership, missing approval, unsafe paths or changed image bytes."""
    lock = json.loads((root / LOCK_PATH).read_text())
    if lock.get("version") != 1 or lock.get("image_count") != len(inputs):
        raise ValueError("Approved inventory count/version mismatch")
    if fingerprint(inputs) != lock.get("image_set_sha256"):
        raise ValueError("Images do not match the approved inventory")
    for item in inputs:
        path = (root / item["path"]).resolve()
        if Path(item["path"]).is_absolute() or not path.is_relative_to(root.resolve()):
            raise ValueError("Approved image path must stay inside the workspace")
        checked_payload(item, path.read_bytes())


def checked_payload(item: dict[str, Any], payload: bytes) -> bytes:
    """Check the exact bytes being sent, not a prior read of a mutable file."""
    if sha256(payload) != item["sha256"]:
        raise ValueError("Approved image bytes changed")
    return payload


def load_inputs(root: Path) -> list[dict[str, Any]]:
    inputs: list[dict[str, Any]] = json.loads((root / INVENTORY_PATH).read_text())["inputs"]
    validate_inputs(root, inputs)
    return inputs
