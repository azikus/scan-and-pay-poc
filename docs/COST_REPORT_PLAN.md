# Separate cost comparison report

Required by Markus on 6 October 2026. Produce a standalone cost report for **each evaluated option**, separate from the extraction/findings report and its later HTML presentation. This document specifies the deliverable; it is not a completed comparison or a fresh pricing check.

## Scope and timing

- M2: capture usage, tariff provenance and costs for every attempted provider/model/method; start the private report as full-corpus batches become available. Include planned, blocked and untested options explicitly, without inventing measurements.
- M3: add stage-by-stage and total costs for OCR → rules, OCR → LLM, annotations, document augmentation and bounded fallback policies.
- M4: deliver the versioned cost report alongside the reviewed quality comparison and provisional pipeline choice. Cost reporting can proceed before labels are verified; cost per correct result cannot.
- M8: refresh the separate report using the final configuration and link it from the HTML findings. Do not wait for HTML work to make costs reviewable.

Keep generated reports private under `reports/cost-comparison/`, with a dated Markdown report and matching JSON/CSV tables. Record corpus, run-set, profile/configuration and tariff versions so the figures can be reproduced. This directory is ignored by Git. Publish only separately approved, sanitised material.

## One row per actual option

An option is an exact provider + model/processor/workflow + versioned extraction profile. Different models, detail/resolution settings, custom workflows and composed methods are separate rows when compared. Cover direct-image LLMs, managed OCR/rules, prebuilt document APIs, custom document extraction and hybrids. Later device OCR gets a separately measured row when implemented. Do not collapse all models into a provider average or describe the configured Nanonets workflow as a prebuilt product.

Each row must show:

| Area | Required information |
| --- | --- |
| Identity and coverage | Exact option/version, account pricing conditions without secrets, test date, source/page/variant counts, attempted/succeeded/failed/not-run inputs and any early stop |
| Tariff | Official source URL and checked date; region/product/tier, currency, billing unit, document/page minimums and any volume tiers or fixed minimum commitment |
| Observed usage | Provider-reported input/image/output/reasoning/cache units as applicable; page/document/workflow units; individual stages, retries, fallback and failed/uncertain dispatches |
| Cost evidence | Reported charge, dated usage-based estimate, unknown or not applicable; explain missing telemetry and distinguish estimates from reconciled billing |
| Comparable totals | Cost per attempt, per source document and full-corpus batch, with denominator and completeness; distribution/sample count where supported |
| Quality-linked cost | Cost per correct complete result only for reviewed labels and a declared scored population; include failed attempts in its cost numerator and keep unscored costs visible separately |
| Scale scenarios | Clearly labelled estimates for illustrative monthly volumes, such as 1,000 and 10,000 documents, with measured workload assumptions and applicable minimums/tiers |

## Accounting rules

Report gross usage cost separately from trial credits/prepaid credit and cash billed. Credits are not a durable unit price. Keep currencies separate unless a dated FX rate/source is provided; state whether tax is known/included. Do not assume pricing scales linearly across minimums, subscriptions or volume tiers, and do not buy a subscription to complete a table.

Retain uncertain charges after failures/timeouts. A reservation ceiling is a budget hold, not measured spend: the existing twelve dispatches retain €12 in holds until reconciliation permits release. Use the same ledger; never reset it for this report. The €500 total and included ≤€30 initial tranche remain unchanged.

For reused OCR/cache stages, show actual batch charges once and the estimated standalone pipeline cost separately. Saved-response replay adds no new recognition charge but must identify the original paid work; it is not a fresh zero-cost OCR run. Include all pipeline recipients/stages without double counting.

Local rules may have zero external API fees; hardware, hosting, development and maintenance costs remain separate estimates or unknowns. Do not present API tariffs as total ownership cost. Exclude payment execution fees and unrelated products unless they become explicit scope.

## Acceptance

Every selected option has a row or an explicit unavailable/untested record. Totals reconcile to recorded stages and the same run set used for evaluation; unknown amounts stay unknown. Differences in corpus coverage, document minimums, trial terms and extraction completeness are visible before comparing prices. Recommendations cite both measured quality and cost evidence; no unsupported savings or accuracy ranking.

Related: [evaluation plan](EVALUATION_PLAN.md), [providers and budget](PROVIDERS_AND_BUDGET.md), [roadmap](ROADMAP.md), [wire cost semantics](API_CONTRACT.md).
