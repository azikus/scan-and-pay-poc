"""Full-matrix local interpretation replay; never calls a provider or alters source evidence."""

import argparse
import json
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.document_observations import DocumentObservation, DocumentSpan
from backend.images import sha256
from backend.ocr_rules import extract_rules
from backend.ocr_rules_v2 import extract_rules_v2
from backend.ocr_rules_v3 import extract_rules_v3
from backend.review import review_payment
from backend.store import utcnow
from evaluation.batch import new_batch, save
from evaluation.corpus import validate_manifest


def replay(
    root: Path,
    manifest: dict[str, Any],
    source: dict[str, Any],
    artifacts: Path,
    output: Path,
) -> dict[str, Any]:
    validate_manifest(root, manifest)
    expected = new_batch(manifest, source["profiles"], source["batch_id"])

    def identities(rows: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
        return [(r["input_id"], r["profile_id"], r["profile_version"]) for r in rows]

    if source["manifest_sha256"] != expected["manifest_sha256"] or identities(
        source["rows"]
    ) != identities(expected["rows"]):
        raise ValueError("Replay source matrix does not cover the pinned manifest")
    if output.exists():
        raise ValueError("Use a new replay destination; existing evidence is immutable")
    rows = []
    for original in source["rows"]:
        row: dict[str, Any] = {
            "input_id": original["input_id"],
            "source_profile": original["profile_id"],
            "source_profile_version": original["profile_version"],
            "source_scan_id": original.get("scan_id"),
            "source_result_path": original.get("result_path"),
            "state": "unavailable",
            "reason": "missing_saved_observation",
        }
        rows.append(row)
        if not original.get("result_path"):
            continue
        result_data = (root / original["result_path"]).read_bytes()
        row["source_result_sha256"] = sha256(result_data)
        result = json.loads(result_data)
        (run,) = result["runs"]
        if (
            run["profile_id"] != original["profile_id"]
            or run["profile_version"] != original["profile_version"]
        ):
            raise ValueError("Replay source profile mismatch")
        stages = [
            s
            for s in run["diagnostics"]["stages"]
            if s["execution"] == "external" and s["method"] == "ocr"
        ]
        if len(stages) != 1:
            row["reason"] = "not_single_ocr_observation"
            continue
        (stage,) = stages
        path = artifacts / result["scan_id"] / f"{run['id']}.{stage['id']}.document.json"
        if not path.exists():
            continue
        data = path.read_bytes()
        document = json.loads(data)
        if (
            document["version"] != "1"
            or document["image_id"] != result["input"]["image_id"]
            or document["source_stage_id"] != stage["id"]
        ):
            raise ValueError("Replay observation provenance mismatch")
        row.update(
            source_observation=path.relative_to(root).as_posix(),
            source_observation_sha256=sha256(data),
            source_stage_id=stage["id"],
            source_cost=stage["cost"],
            source_stage_duration_ms=stage.get("duration_ms"),
            source_timings_ms=run["diagnostics"].get("timings_ms"),
            interpretations={},
        )
        for version, extractor in [("rules@1", extract_rules), ("rules@2", extract_rules_v2)]:
            payment, evidence, routing = extractor(
                document["text"], document["image_id"], stage["id"]
            )
            payment = review_payment(payment, evidence)
            row["interpretations"][version] = {
                "payment": payment.model_dump(mode="json"),
                "evidence": [e.model_dump(mode="json") for e in evidence],
                "routing": routing.model_dump(mode="json"),
            }
        observation = DocumentObservation(
            **{**document, "spans": tuple(DocumentSpan(**s) for s in document["spans"])}
        )
        started = perf_counter()
        payment, evidence, routing = extract_rules_v3(observation)
        payment = review_payment(payment, evidence)
        row["interpretations"]["rules@3"] = {
            "payment": payment.model_dump(mode="json"),
            "evidence": [e.model_dump(mode="json") for e in evidence],
            "routing": routing.model_dump(mode="json"),
            "local_replay_ms": (perf_counter() - started) * 1000,
        }
        row["rules_v3_payment_changed"] = (
            row["interpretations"]["rules@2"]["payment"]
            != row["interpretations"]["rules@3"]["payment"]
        )
        row.update(state="replayed", reason=None)
        row["payment_changed"] = (
            row["interpretations"]["rules@1"]["payment"]
            != row["interpretations"]["rules@2"]["payment"]
        )
    report = {
        "kind": "saved_response_replay",
        "created_at": utcnow(),
        "source_batch_id": source["batch_id"],
        "manifest_sha256": source["manifest_sha256"],
        "new_external_calls": 0,
        "new_provider_charge": "0",
        "source_charges_are_not_rebilled": True,
        "labels_verified": False,
        "accuracy": None,
        "inputs_per_profile": len(manifest["inputs"]),
        "counts": dict(Counter(r["state"] for r in rows)),
        "payment_changed": sum(r.get("payment_changed", False) for r in rows),
        "rows": rows,
    }
    save(output, report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("manifest", "source", "artifacts", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = replay(
        Path.cwd(),
        json.loads(args.manifest.read_text()),
        json.loads(args.source.read_text()),
        args.artifacts.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "kind",
                    "counts",
                    "payment_changed",
                    "new_external_calls",
                    "labels_verified",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
