"""Full-matrix completeness and latency reporting; no label-based accuracy claims."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from backend.models import Run
from evaluation.batch import new_batch, save
from evaluation.cost_report import summarize as cost_summary
from evaluation.repeatability import latency_summary


def summarize(root: Path, manifest: dict[str, Any], batch: dict[str, Any]) -> dict[str, Any]:
    expected = new_batch(manifest, batch["profiles"], batch["batch_id"])
    keys = ("input_id", "profile_id", "profile_version", "key")
    if batch["manifest_sha256"] != expected["manifest_sha256"] or [
        tuple(row[k] for k in keys) for row in batch["rows"]
    ] != [tuple(row[k] for k in keys) for row in expected["rows"]]:
        raise ValueError("Report must cover the entire pinned matrix")
    profiles = {}
    for profile, version in batch["profiles"].items():
        rows = [r for r in batch["rows"] if r["profile_id"] == profile]
        outcomes: Counter[str] = Counter()
        reasons: Counter[str] = Counter()
        timings: dict[str, list[float | None]] = defaultdict(list)
        stage_timings: dict[str, list[float | None]] = defaultdict(list)
        review: Counter[str] = Counter()
        results = 0
        for row in rows:
            if not row.get("result_path"):
                outcomes["error" if row["state"] == "failed" else "pending"] += 1
                if row.get("reason"):
                    reasons[row["reason"]] += 1
                continue
            result = json.loads((root / row["result_path"]).read_text())
            if len(result["runs"]) != 1:
                raise ValueError("Each evaluation cell requires one run")
            run = Run.model_validate(result["runs"][0])
            if run.profile_id != profile or run.profile_version != version:
                raise ValueError("Report profile snapshot mismatch")
            results += 1
            outcomes[run.result_outcome or "pending"] += 1
            if run.error:
                reasons[run.error.code] += 1
            if run.payment:
                review.update({r.code for r in run.payment.review.reasons})
            for name, duration in run.diagnostics.timings_ms.model_dump().items():
                timings[name].append(duration)
            for index, stage in enumerate(run.diagnostics.stages):
                if stage.execution == "external":
                    key = f"{index}:{stage.provider}:{stage.method}"
                    stage_timings[key].append(stage.duration_ms)
        timeouts = sum(
            count
            for reason, count in reasons.items()
            if "timeout" in reason or "deadline" in reason
        )
        terminal = outcomes["success"] + outcomes["incomplete"] + outcomes["error"]
        profiles[profile] = {
            "version": version,
            "planned_inputs": len(rows),
            "terminal_inputs": terminal,
            "saved_results": results,
            "outcomes": dict(outcomes),
            "complete_for_review_fraction": outcomes["success"] / terminal if terminal else None,
            "failure_reasons": dict(reasons),
            "timeout_count": timeouts,
            "timeout_denominator": terminal,
            "timeout_rate": timeouts / terminal if terminal else None,
            "review_reason_run_counts": dict(review),
            "timings_ms": {
                name: latency_summary(timings[name])
                for name in ("queue", "preprocess", "provider", "postprocess", "total")
            },
            "external_stage_timings_ms": {
                key: latency_summary(values) for key, values in stage_timings.items()
            },
        }
    return {
        "kind": batch["kind"],
        "batch_id": batch["batch_id"],
        "manifest_sha256": batch["manifest_sha256"],
        "accuracy_scored": False,
        "note": "Completeness is readiness for human review, not correctness. Timing includes failed attempts with measurements; missing measurements are not zero. Total includes all hybrid stages, queue and local work, not mobile capture/upload/review. p95 is descriptive for this sample size. Costs retain reported/estimated/unknown status; reservations are not bills.",
        "profiles": profiles,
        "costs": cost_summary(root, manifest, batch, {}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("manifest", "state", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Use a new report destination")
    report = summarize(
        Path.cwd(), json.loads(args.manifest.read_text()), json.loads(args.state.read_text())
    )
    save(args.output, report)


if __name__ == "__main__":
    main()
