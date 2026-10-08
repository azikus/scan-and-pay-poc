"""API-only, resumable full-corpus evaluation. Each matrix cell exists before submission."""

import argparse
import json
import time
from pathlib import Path
from typing import Any

import httpx

from backend.config import Settings
from backend.images import sha256
from backend.store import private_write, utcnow
from evaluation.corpus import validate_manifest

TERMINAL = {"completed", "partially_completed", "failed", "interrupted"}
STOP = {"provider_auth", "provider_quota", "budget_exceeded"}


def save(path: Path, value: Any) -> None:
    private_write(path, json.dumps(value, indent=2).encode())


def new_batch(manifest: dict[str, Any], profiles: dict[str, str], batch_id: str) -> dict[str, Any]:
    return {
        "version": 1,
        "batch_id": batch_id,
        "created_at": utcnow(),
        "kind": "fresh_inference",
        "manifest_sha256": sha256(json.dumps(manifest, sort_keys=True).encode()),
        "profiles": profiles,
        "complete": False,
        "rows": [
            {
                "input_id": i["id"],
                "profile_id": p,
                "profile_version": v,
                "key": sha256(f"{batch_id}/{p}/{i['id']}".encode()),
                "scan_id": None,
                "state": "not_run",
                "reason": i.get("failure"),
                "result_path": None,
            }
            for p, v in profiles.items()
            for i in manifest["inputs"]
        ],
    }


def run_batch(
    root: Path,
    manifest: dict[str, Any],
    state_path: Path,
    client: Any,
    *,
    poll_seconds: float = 1,
    deadline_seconds: float = 260,
    inter_input_seconds: float = 0,
) -> dict[str, Any]:
    if not 0 <= inter_input_seconds <= 60:
        raise ValueError("Batch pacing must be between zero and sixty seconds")
    validate_manifest(root, manifest)
    state: dict[str, Any] = json.loads(state_path.read_text())
    expected = new_batch(manifest, state["profiles"], state["batch_id"])
    if expected["manifest_sha256"] != state["manifest_sha256"] or [
        (r["input_id"], r["profile_id"], r["profile_version"], r["key"]) for r in state["rows"]
    ] != [
        (r["input_id"], r["profile_id"], r["profile_version"], r["key"]) for r in expected["rows"]
    ]:
        raise ValueError("Batch matrix or manifest changed")
    response = client.get("/v1/profiles")
    response.raise_for_status()
    available = {p["id"]: p for p in response.json()["profiles"]}
    for name, version in state["profiles"].items():
        p = available.get(name, {})
        if p.get("version") != version or not p.get("configured") or not p.get("enabled"):
            raise ValueError("Profile configuration changed or unavailable")
    inputs = {i["id"]: i for i in manifest["inputs"]}
    stop = False
    for row in state["rows"]:
        if row["state"] in {"succeeded", "failed"}:
            continue
        item = inputs[row["input_id"]]
        if item["status"] != "prepared":
            row.update(state="not_run", reason="preparation_failed")
            continue
        if stop:
            row.update(state="not_run", reason="batch_stopped")
            continue
        try:
            if row["scan_id"] is None:
                # Persist key and uncertain state BEFORE POST; resume can reuse only this exact key.
                row.update(state="submission_unknown", reason=None)
                save(state_path, state)
                response = client.post(
                    "/v1/scans",
                    headers={"Idempotency-Key": row["key"]},
                    files={"image": ("image.png", (root / item["path"]).read_bytes(), "image/png")},
                    data={
                        "options": json.dumps({"mode": "extract", "profiles": [row["profile_id"]]})
                    },
                )
                if response.status_code != 202:
                    code = response.json().get("error", {}).get("code", "api_rejected")
                    row.update(state="failed", reason=code)
                    stop = code in STOP or response.status_code in {401, 429, 503}
                    save(state_path, state)
                    continue
                row.update(scan_id=response.json()["scan_id"], state="accepted")
                save(state_path, state)
            until = time.monotonic() + deadline_seconds
            while True:
                response = client.get("/v1/scans/" + row["scan_id"])
                response.raise_for_status()
                result = response.json()
                if result["state"] in TERMINAL:
                    break
                if time.monotonic() >= until:
                    raise TimeoutError
                time.sleep(poll_seconds)
            result_path = state_path.parent / "results" / (row["scan_id"] + ".json")
            save(result_path, result)
            (run,) = result["runs"]
            if run["profile_version"] != row["profile_version"]:
                raise ValueError("Returned profile snapshot mismatch")
            code = run["error"]["code"] if run.get("error") else None
            row.update(
                state="succeeded" if run["state"] == "completed" else "failed",
                reason=code,
                result_path=result_path.relative_to(root).as_posix(),
            )
            stop = code in STOP or any(
                stage.get("usage", {}).get("http_status") in {400, 404, 422}
                for stage in run.get("diagnostics", {}).get("stages", [])
            )
        except (httpx.HTTPError, TimeoutError):
            # Accepted/uncertain submissions remain resumable, never relabelled as a fresh attempt.
            row["reason"] = "connection_or_poll_interrupted"
            stop = True
        finally:
            save(state_path, state)
        if inter_input_seconds and not stop:
            time.sleep(inter_input_seconds)
    state["complete"] = all(r["state"] in {"succeeded", "failed"} for r in state["rows"])
    state["updated_at"] = utcnow()
    save(state_path, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--inter-input-seconds", type=float, default=0)
    args = parser.parse_args()
    settings = Settings.from_env()
    with httpx.Client(
        base_url=args.url,
        headers={"Authorization": "Bearer " + settings.token.get_secret_value()},
        timeout=30,
        trust_env=False,
        follow_redirects=False,
    ) as client:
        state = run_batch(
            Path.cwd(),
            json.loads(args.manifest.read_text()),
            args.state.resolve(),
            client,
            inter_input_seconds=args.inter_input_seconds,
        )
    print(
        json.dumps(
            {
                "complete": state["complete"],
                "counts": {
                    s: sum(r["state"] == s for r in state["rows"])
                    for s in sorted({r["state"] for r in state["rows"]})
                },
            }
        )
    )


if __name__ == "__main__":
    main()
