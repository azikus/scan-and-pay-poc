"""Enforce the handoff's separate statement/branch gates on domain/orchestration."""

import json
from pathlib import Path

# CLI/export/this reporting script are operational entry points, reported separately.
# All backend API, configuration, models, storage, runtime, rules and adapters count.
OPERATIONAL = {"backend/cli.py", "backend/export.py", "backend/check_coverage.py"}


def main() -> None:
    report = json.loads(Path(".local/coverage.json").read_text())
    summaries = [
        data["summary"] for path, data in report["files"].items() if path not in OPERATIONAL
    ]
    statements = sum(s["num_statements"] for s in summaries)
    covered = sum(s["covered_lines"] for s in summaries)
    branches = sum(s["num_branches"] for s in summaries)
    covered_branches = sum(s["covered_branches"] for s in summaries)
    print(
        f"Domain/orchestration: {covered}/{statements} statements ({covered / statements:.2%}); {covered_branches}/{branches} branches ({covered_branches / branches:.2%})"
    )
    if covered / statements < 0.90 or covered_branches / branches < 0.85:
        raise SystemExit("Coverage below the handoff requirement")


if __name__ == "__main__":
    main()
