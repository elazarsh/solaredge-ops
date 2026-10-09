---
name: marketing-analytics-workflow
description: Analyse digital marketing performance with AI without fooling yourself - success layers, exposure-to-sale measurement map, data-quality checks, metric definitions, competing-explanation testing, decision log, weekly read-only reports, and when to let agents act. Use when reviewing campaign/ads/funnel data, diagnosing cost-per-result changes, writing performance reports, or setting up recurring analytics (ניתוח קמפיין, ביצועים, ROAS, CPL, דוח שבועי).
---

# Marketing analytics workflow

Start from ONE business question (e.g. "is the sales drop fewer leads, worse leads, or slower handling?"), gather evidence for each explanation before touching budget.

## Three success layers
Ad (spend, reach, clicks) -> Conversion (visits, leads) -> Business (lead quality, progress to sale, customers).
Measurement map: Exposure -> Engagement -> Lead -> Sale (with time-to-sale).

## Six steps
1. **Comparable data:** fix period, currency, time zone; export spend, impressions, relevant clicks, results with campaign/ad IDs; document attribution window; minimise personal data (aggregates).
2. **Data-quality check first:** duplicates, missing values, totals that reconcile, link clicks vs all interactions, no cross-platform double-counting.
3. **Define metrics with business definitions:** cost per lead, per *qualified* lead, per customer; ROAS = attributed revenue / spend (not profit); show "no results"/"insufficient data" not 0.
4. **Big picture first:** account/campaign totals before ad sets/ads; don't crown the cheapest row (it may have tiny spend/different audience); show result counts beside every average.
5. **Test competing explanations** when cost per result rises: creative, delivery, traffic quality, landing page/form, tracking. Build a change timeline (budget, audience, offer, landing page). Seek disconfirming evidence. Run one small defined experiment.
6. **Log decisions:** date, data period, campaign, observation + source, hypothesis, what would disprove it, action or "wait", success metric, next review date, outcome. Keep verified findings separate from hypotheses.

## Prompt patterns
- *Data check:* confirm period/currency/timezone/definitions/attribution window; flag duplicates/missing; return a short data-quality report and which analyses are safe.
- *Campaign report:* start with spend and business outcomes vs comparable period; separate facts / hypotheses / recommendations; up to 3 actions each with supporting + opposing evidence and a success metric; do not pause ads or change budgets.
- *Decision log:* choose one measurable experiment, define what stays fixed, output one log row with owner and review date; don't execute.
- *Weekly report (read-only connector):* last 7 full days vs previous 7; spend, results, cost per result with counts; flag missing data instead of zero; 3 evidence-backed findings, one test each; no budget/status changes.

## Operations
Separate roles (business owner approves budget/offer; operator checks account; measurement owner verifies results; log each). Pilot one campaign. Check changes before blaming creative fatigue. Recurring reports need scheduler, valid access, failure handling, run logs (period read) - never send a stale summary as current. Move to agents only after reports are reproducible; limit permissions/budget/objects in the tool; start with "create paused".

## Pitfalls
Platform vs internal numbers differ (currency/time zone/attribution) - compare under identical settings; same purchase in several systems; leads not matched to customers (then do NOT compute ROAS/cost per customer from lead counts); small samples; judging before leads convert (compare cohorts, state wait period); correlation != cause; time saved on reporting != better campaigns; sending customer PII to analysis tools; AI replacing oversight.

See also: `ad-creative-workflow`, `grounded-research`, `data:*` skills for SQL/dashboards, `verify-and-safety-gates`.
