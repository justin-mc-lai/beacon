# Evo Scorecard Contract (v1.3.2)

## Single Main KPI

- `false_complete_rate`
- Definition: high-risk benchmark cases that still resolve to `discard`, divided by total high-risk benchmark cases in the selected experiment set.
- Lower is better.

## Supporting Metrics

- `evidence_coverage`
- `recovery_success_rate`
- `operator_load`
- `cost_per_trial`

## Decision Thresholds

- keep threshold: `75`
- discard threshold: `35`
- review: any score between discard and keep, or mixed evidence cases.

## Current Decision Summary

- keep: `2`
- review: `0`
- discard: `1`

## Latest Score Delta

- main_kpi_score: `0.0`
- score_delta.main_kpi_score: `None`
- score_delta.false_complete_rate: `None`

## Artifacts

- decision_engine: `.beacon/state/evo/decision-engine.json`
- scorecard: `.beacon/state/evo/scorecards/latest.json`
- latest_experiment: `.beacon/state/evo/experiments/latest.json`

