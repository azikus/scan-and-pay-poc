"""Small API client; full results go to private files, routine output stays minimal."""

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
from dotenv import load_dotenv

from backend.models import Run
from backend.store import private_write


def poll(client: httpx.Client, scan_id: str, deadline_seconds: float = 300) -> dict[str, Any]:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        response = client.get("/v1/scans/" + scan_id)
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        if data["state"] not in {"queued", "running"}:
            return data
        time.sleep(0.5)
    raise TimeoutError("Polling deadline reached; job may still be active. Poll the same scan ID.")


def summary(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "scan_id": result["scan_id"],
        "state": result["state"],
        "execution_kind": result["execution_kind"],
        "runs": [
            {
                "profile_id": run["profile_id"],
                "state": run["state"],
                "outcome": Run.model_validate(run).result_outcome,
                "review_state": run["payment"]["review"]["state"] if run["payment"] else None,
                "error_code": run["error"]["code"] if run["error"] else None,
            }
            for run in result["runs"]
        ],
    }


def main() -> None:
    load_dotenv(override=False)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health")
    commands.add_parser("profiles")
    upload = commands.add_parser("upload")
    upload.add_argument("image", type=Path)
    upload.add_argument("--mode", choices=["extract", "compare"], default="extract")
    upload.add_argument("--profiles", nargs="+", required=True)
    upload.add_argument("--key", default=None, help="Keep this key when retrying a request.")
    upload.add_argument("--no-wait", action="store_true")
    get = commands.add_parser("get")
    get.add_argument("scan_id")
    get.add_argument("--wait", action="store_true")
    delete = commands.add_parser("delete")
    delete.add_argument("scan_id")
    args = parser.parse_args()
    if args.url not in {"http://127.0.0.1:8000", "http://localhost:8000"}:
        parsed = httpx.URL(args.url)
        if parsed.host not in {"127.0.0.1", "localhost"} or parsed.scheme != "http":
            parser.error("Milestone 1 client uses loopback HTTP only")
    token = os.getenv("SCANPAY_TOKEN", "")
    if args.command != "health" and not token:
        parser.error("Configure SCANPAY_TOKEN locally")
    if hasattr(args, "scan_id") and not re.fullmatch(r"scan-[0-9a-f]{32}", args.scan_id):
        parser.error("Invalid scan ID")
    try:
        with httpx.Client(
            base_url=args.url,
            headers={"Authorization": "Bearer " + token},
            timeout=30,
            trust_env=False,
            follow_redirects=False,
        ) as client:
            if args.command in {"health", "profiles"}:
                response = client.get("/health" if args.command == "health" else "/v1/profiles")
                response.raise_for_status()
                print(json.dumps(response.json(), indent=2))
                return
            if args.command == "delete":
                response = client.delete("/v1/scans/" + args.scan_id)
                response.raise_for_status()
                print("Local scan deleted; upstream retention is unchanged.")
                return
            if args.command == "upload":
                key = args.key or uuid4().hex
                profiles = "all_enabled" if args.profiles == ["all_enabled"] else args.profiles
                print(json.dumps({"idempotency_key": key}))
                with args.image.open("rb") as f:
                    response = client.post(
                        "/v1/scans",
                        headers={"Idempotency-Key": key},
                        files={"image": (args.image.name, f)},
                        data={"options": json.dumps({"mode": args.mode, "profiles": profiles})},
                    )
                response.raise_for_status()
                accepted = response.json()
                print(json.dumps(accepted))
                if args.no_wait:
                    return
                result = poll(client, accepted["scan_id"])
            elif args.wait:
                result = poll(client, args.scan_id)
            else:
                response = client.get("/v1/scans/" + args.scan_id)
                response.raise_for_status()
                result = response.json()
            output = Path(".local/client") / (result["scan_id"] + ".json")
            private_write(output, json.dumps(result, ensure_ascii=False, indent=2).encode())
            print(json.dumps({**summary(result), "private_result": str(output)}, indent=2))
    except httpx.HTTPStatusError as exc:
        # Safe code only; never echo upstream/server error bodies by default.
        parser.exit(
            1,
            f"API returned HTTP {exc.response.status_code}; retain the key and inspect local configuration.\n",
        )
    except (httpx.RequestError, OSError, TimeoutError):
        parser.exit(
            1,
            "Request or local I/O failed. Preserve the key; retrieve the accepted scan before retrying.\n",
        )


if __name__ == "__main__":
    main()
