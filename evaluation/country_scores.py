"""Country cohorts and reviewed-scheme diagnostics without changing extraction truth."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pycountry

from backend.models import Run
from backend.review_guidance import guidance
from evaluation.batch import save
from evaluation.reviewed import indexed, score_batch

ACCEPTED = {"exact_match", "accepted_name_variant"}
ROUTE_FIELDS = {
    "iban": {"iban", "bic"},
    "uk_domestic": {"sort_code", "account_number"},
    "biller_reference": {"biller_scheme", "biller_code"},
}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def country(value: Any) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or len(value) != 2
        or value != value.upper()
        or pycountry.countries.get(alpha_2=value) is None
    ):
        raise ValueError("Country must be an ISO alpha-2 code or null")
    return value


def context_template(key: dict[str, Any]) -> dict[str, Any]:
    """Suggestions are optional cohort labels, never automatically reviewed truth."""
    return {
        "version": "country-review@1",
        "answer_key_sha256": digest(key),
        "documents": [
            {
                "input_id": d["input_id"],
                "image_sha256": d["image_sha256"],
                "status": "pending",
                "country": None,
                "reviewer": None,
                "suggested_country": None,
                "suggestion_source": None,
            }
            for d in key["documents"]
        ],
    }


def validate_context(key: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if context["version"] != "country-review@1" or context["answer_key_sha256"] != digest(key):
        raise ValueError("Country key must bind to the exact reviewed answer key")
    docs = indexed(context["documents"], "input_id")
    expected = indexed(key["documents"], "input_id")
    if docs.keys() != expected.keys():
        raise ValueError("Country key must cover every reviewed image")
    for ident, d in docs.items():
        if d["image_sha256"] != expected[ident]["image_sha256"]:
            raise ValueError("Country key image hash mismatch")
        country(d["country"])
        country(d["suggested_country"])
        if d["status"] not in {"pending", "reviewed"}:
            raise ValueError("Invalid country review status")
        if d["status"] == "reviewed" and not str(d.get("reviewer") or "").strip():
            raise ValueError("Reviewed country requires reviewer attribution")
        if d["status"] == "pending" and d["country"] is not None:
            raise ValueError("Pending suggestions must not populate expected country")
        if d["suggested_country"] and not d.get("suggestion_source"):
            raise ValueError("Country suggestions need explicit provenance")
    return docs


def reviewed_route(fields: list[dict[str, Any]]) -> str:
    # Use reviewed printed fields, never the evaluated model's route/country prediction.
    visible = {f["path"].split("/")[-1] for f in fields if f["status"] == "readable"}
    routes = set()
    if "iban" in visible:
        routes.add("iban")
    if {"sort_code", "account_number"} <= visible:
        routes.add("uk_domestic")
    if visible & ROUTE_FIELDS["biller_reference"]:
        routes.add("biller_reference")
    return next(iter(routes)) if len(routes) == 1 else "unresolved"


def tally(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(f["outcome"] for f in rows if f["label_status"] == "readable")
    n = sum(counts.values())
    accepted = sum(counts[k] for k in ACCEPTED)
    return {
        "counts": dict(counts),
        "accepted": accepted,
        "denominator": n,
        "fraction": accepted / n if n else None,
    }


def score_countries(
    root: Path,
    manifest: dict[str, Any],
    batch: dict[str, Any],
    key: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    contexts = validate_context(key, context)
    baseline = score_batch(root, manifest, batch, key)
    inputs = indexed(manifest["inputs"], "id")
    labels = indexed(key["documents"], "input_id")
    predictions = {}
    for row in batch["rows"]:
        hint = None
        if row.get("result_path"):
            result = json.loads((root / row["result_path"]).read_text())
            if result.get("input", {}).get("original_sha256") != inputs[row["input_id"]]["sha256"]:
                raise ValueError("Saved result image does not match the evaluation input")
            run = Run.model_validate(result["runs"][0])
            g = guidance(run)
            hint = g.issuer_country if g is not None and run.result_outcome != "error" else None
        predictions[row["profile_id"], row["input_id"]] = hint
    profiles = {}
    for profile, original in baseline["profiles"].items():
        countries: dict[str, list[dict[str, Any]]] = defaultdict(list)
        country_inputs: dict[str, set[str]] = defaultdict(set)
        schemes: dict[str, list[dict[str, Any]]] = defaultdict(list)
        absences: dict[str, Counter[str]] = defaultdict(Counter)
        country_accuracy: Counter[str] = Counter()
        for d in original["documents"]:
            ident = d["input_id"]
            c = contexts[ident]
            cohort = (
                "reviewed:" + (c["country"] or "unknown")
                if c["status"] == "reviewed"
                else "suggested:" + c["suggested_country"]
                if c["suggested_country"]
                else "unreviewed:unknown"
            )
            countries[cohort].extend(d["fields"])
            country_inputs[cohort].add(ident)
            hint = predictions[profile, ident]
            if c["status"] == "reviewed":
                status = (
                    "run_error"
                    if hint is None
                    else "ambiguous"
                    if hint.status == "ambiguous"
                    else "correct"
                    if hint.value == c["country"]
                    else "incorrect"
                )
                country_accuracy[status] += 1
            grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for f in labels[ident]["fields"]:
                if f["path"].startswith("payment_options/"):
                    grouped[f["path"].split("/")[1]].append(f)
            routes = {option: reviewed_route(fields) for option, fields in grouped.items()}
            for f in d["fields"]:
                parts = f["path"].split("/")
                route = routes[parts[1]] if parts[0] == "payment_options" else "document"
                schemes[route].append(f)
                if f["label_status"] == "absent":
                    other_route = any(
                        parts[-1] in names and route != name for name, names in ROUTE_FIELDS.items()
                    )
                    applicability = (
                        "not_applicable"
                        if other_route and route in ROUTE_FIELDS
                        else "optional_or_not_stated"
                    )
                    absences[applicability][f["outcome"]] += 1
        reviewed = sum(country_accuracy.values())
        profiles[profile] = {
            "version": original["version"],
            "original_scores": original["scores"],
            "by_country": {
                c: {
                    "input_entries": len(country_inputs[c]),
                    "distinct_images": len({inputs[i]["sha256"] for i in country_inputs[c]}),
                    **tally(rows),
                }
                for c, rows in countries.items()
            },
            "by_reviewed_payment_scheme": {r: tally(rows) for r, rows in schemes.items()},
            "reviewed_absences_by_applicability": {r: dict(c) for r, c in absences.items()},
            "country_detection": {
                "counts": dict(country_accuracy),
                "reviewed_inputs": reviewed,
                "pending_inputs": len(contexts) - reviewed,
                "fraction": country_accuracy["correct"] / reviewed if reviewed else None,
            },
        }
    return {
        "version": "country-comparison@1",
        "batch_id": batch["batch_id"],
        "answer_key_sha256": digest(key),
        "country_key_sha256": digest(context),
        "input_entries": len(inputs),
        "distinct_images": len({i["sha256"] for i in inputs.values()}),
        "profiles": profiles,
        "limitations": [
            "Country cohorts are fixed by one shared key across compared profiles; suggested cohorts are not verified countries.",
            "Country detection is scored only against reviewed country labels; null fraction means unscored.",
            "Payment scheme derives from reviewed printed bank/biller fields, never from language or predicted country.",
            "Readable printed values remain scored even if country or scheme conflicts. Original scores are preserved.",
            "Correct optional/inapplicable absences do not inflate readable accuracy. Unexpected values remain visible errors.",
            "No whole-invoice, payment-readiness or applicability-accuracy claim is made without reviewed labels for those tasks.",
            "The frozen field benchmark retains explicit duplicate inputs. Entry and distinct-image counts are separate; these are not independent trials.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest", "batch", "key", "context", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Preserve prior reports; choose a new output path")
    values = [
        json.loads(getattr(args, name).read_text())
        for name in ("manifest", "batch", "key", "context")
    ]
    save(args.output, score_countries(Path.cwd(), *values))


if __name__ == "__main__":
    main()
