# Evo Harness Contract (v1.3.4)

## Goal

- Run fixed-budget, real-input experiments over Beacon learning-plane candidates.
- Keep the editable surface small and auditable.
- Produce explicit keep/review/discard decisions instead of open-ended drift.

## Budget Contract

- max_runtime_minutes: `30`
- max_iterations: `3`
- max_command_count: `12`
- max_evidence_budget: `20`

## Subject Surface
- `execution_baseline`
- `requirement_rewrite`
- `debug_recovery_policy`

## Program Surface
- `benchmark_corpus`
- `decision_scorecard`
- `keep_discard_ledger`

## Real Benchmark Inputs
- benchmark_corpus: `.beacon/state/eval-lab/benchmark-corpus.json`
- scorecard: `.beacon/state/evo/scorecards/latest.json`
- ledger: `.beacon/state/evo/ledgers/latest.json`

## Latest Experiment
- run_id: `evo-20260331T143934.331848+0000`
- label: `Beacon v1.1.12 design governance autoresearch`
- selected_candidates: `2`
- verdict: `discard`

