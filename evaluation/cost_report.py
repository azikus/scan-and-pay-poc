"""Private per-option reporting. Reservations, gross estimates and cash bills are distinct."""

import argparse
import csv
import io
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.store import private_write, utcnow


def summarize(
    root: Path, manifest: dict[str, Any], batch: dict[str, Any], options: dict[str, Any]
) -> list[dict[str, Any]]:
    inputs = {i["id"]: i for i in manifest["inputs"]}
    reports = []
    for profile, version in batch["profiles"].items():
        rows = [r for r in batch["rows"] if r["profile_id"] == profile]
        costs: dict[str, Decimal] = defaultdict(Decimal)
        stages = []
        unknown = 0
        dispatched_runs = 0
        selected_option = options.get(profile)
        option_source = "provided_plan"
        for row in rows:
            if not row.get("result_path"):
                continue
            result = json.loads((root / row["result_path"]).read_text())
            for run in result["runs"]:
                if run["profile_id"] != profile or run["profile_version"] != version:
                    raise ValueError("Cost report profile snapshot mismatch")
                snapshot = run["diagnostics"].get("versions", {}).get("option")
                if snapshot:
                    saved_option = json.loads(snapshot)
                    if option_source == "stored_run_snapshot" and selected_option != saved_option:
                        raise ValueError("Cost report option snapshots differ within one version")
                    selected_option = saved_option
                    option_source = "stored_run_snapshot"
                external = [s for s in run["diagnostics"]["stages"] if s["execution"] == "external"]
                dispatched_runs += bool(external)
                for stage in external:
                    cost = stage["cost"]
                    stages.append(
                        {
                            "input_id": row["input_id"],
                            "run_id": run["id"],
                            "stage_id": stage["id"],
                            "provider": stage["provider"],
                            "endpoint_host": stage["endpoint_host"],
                            "requested_model": stage.get("requested_model")
                            or run["diagnostics"]["requested_model"],
                            "returned_model": stage.get("returned_model")
                            or run["diagnostics"]["returned_model"],
                            "usage": stage["usage"],
                            "cost": cost,
                            "run_state": run["state"],
                        }
                    )
                    if cost["status"] in {"estimated", "reported"}:
                        costs[cost["currency"]] += Decimal(cost["amount"])
                    else:
                        unknown += 1
        complete = all(r["state"] in {"succeeded", "failed"} for r in rows)
        counts = {
            state: sum(r["state"] == state for r in rows)
            for state in ("succeeded", "failed", "not_run", "accepted", "submission_unknown")
        }
        sources = len({inputs[r["input_id"]]["group_id"] for r in rows})
        totals = {c: str(v) for c, v in costs.items()}
        measured = bool(stages) and unknown == 0 and complete
        reports.append(
            {
                "profile_id": profile,
                "profile_version": version,
                "option": selected_option,
                "option_source": option_source,
                "inputs": len(rows),
                "source_groups": sources,
                "source_files": len(
                    {
                        inputs[r["input_id"]].get("source_id", inputs[r["input_id"]]["group_id"])
                        for r in rows
                    }
                ),
                "variants": dict(
                    Counter(inputs[r["input_id"]].get("variant", "unspecified") for r in rows)
                ),
                "prepared_page_inputs": sum(
                    inputs[r["input_id"]].get("page") is not None
                    and not inputs[r["input_id"]]
                    .get("variant", "supplied_image")
                    .startswith("supplied_")
                    for r in rows
                ),
                "explicit_duplicate_inputs": sum(
                    bool(inputs[r["input_id"]].get("duplicate_of")) for r in rows
                ),
                "failure_or_stop_reasons": dict(
                    Counter(
                        r.get("reason") or "unspecified" for r in rows if r["state"] != "succeeded"
                    )
                ),
                "coverage_complete": complete,
                **counts,
                "external_stages": len(stages),
                "dispatched_runs": dispatched_runs,
                "unknown_stage_charges": unknown,
                "known_estimates_and_reported_by_currency": totals,
                "cost_per_dispatched_attempt": {
                    c: str(v / dispatched_runs) for c, v in costs.items()
                }
                if measured
                else None,
                "cost_per_source_group": {c: str(v / sources) for c, v in costs.items()}
                if measured
                else None,
                "monthly_volume_scenarios": {
                    str(n): {c: str(v / sources * n) for c, v in costs.items()}
                    for n in (1000, 10000)
                }
                if measured and options.get(profile, {}).get("linear_scaling_verified")
                else None,
                "scale_note": "Monthly 1,000/10,000-document scenarios remain unavailable until complete usage, source-document grouping and tariff minimum/tier assumptions are verified. Prepared pages are separate API documents; source groups are not verified invoice counts.",
                "cash_billed": None,
                "trial_credit_applied": None,
                "tax": "unknown",
                "fx": None,
                "cost_per_correct_result": None,
                "labels_verified": False,
                "stages": stages,
            }
        )
    return reports


def write_report(output: Path, rows: list[dict[str, Any]], batch: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    private_write(
        output / "costs.json",
        json.dumps(
            {
                "generated_at": utcnow(),
                "batch_id": batch["batch_id"],
                "manifest_sha256": batch["manifest_sha256"],
                "options": rows,
            },
            indent=2,
        ).encode(),
    )
    columns = [
        "profile_id",
        "profile_version",
        "inputs",
        "source_groups",
        "succeeded",
        "failed",
        "not_run",
        "external_stages",
        "unknown_stage_charges",
        "known_estimates_and_reported_by_currency",
    ]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(
        {k: json.dumps(r[k]) if isinstance(r[k], dict) else r[k] for k in columns} for r in rows
    )
    private_write(output / "costs.csv", stream.getvalue().encode())
    text = [
        "# Private option cost comparison",
        "",
        f"Batch: `{batch['batch_id']}`. Generated {utcnow()}.",
        "",
        "Unverified labels remain unscored. API estimates are not reconciled invoices or total ownership costs. ",
        "The persistent budget ledger is reported separately. EUR reservations are not measured spend or a conversion of the subtotals below.",
        "",
        "| Option | Inputs | Succeeded / failed / not run | External stages | Known subtotal by currency | Unknown stage charges |",
        "| --- | ---: | --- | ---: | --- | ---: |",
    ]
    for r in rows:
        text.append(
            f"| {r['profile_id']} @ {r['profile_version']} | {r['inputs']} | "
            f"{r['succeeded']} / {r['failed']} / {r['not_run']} | {r['external_stages']} | "
            f"{r['known_estimates_and_reported_by_currency'] or 'Unknown / unmeasured'} | {r['unknown_stage_charges']} |"
        )
    text += ["", "## Tariffs, versions and limitations", ""]
    for r in rows:
        text += [
            f"### {r['profile_id']}",
            "",
            "```json",
            json.dumps(r["option"], indent=2),
            "```",
            "",
            r["scale_note"],
            "Cash billed, trial offsets and tax remain unknown; no implicit FX conversion.",
            "",
        ]
    private_write(output / "report.md", "\n".join(text).encode())


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("manifest", "batch", "options", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    manifest, batch, options = (
        json.loads(p.read_text()) for p in (args.manifest, args.batch, args.options)
    )
    write_report(args.output, summarize(Path.cwd(), manifest, batch, options), batch)


if __name__ == "__main__":
    main()
