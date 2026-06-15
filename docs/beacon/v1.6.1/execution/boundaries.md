# Boundaries v1.6.1

Inherits `docs/beacon/v1.6.0/execution/boundaries.md`.

## v1.6.1 additions

- **Program planner triad**: `beacon-pln-program` (umbrella) delegates to `beacon-pln-program-auto` or `beacon-pln-program-interactive`; sub-skills must not write `features/*/truth.md`.
- **Single operator entry**: `beacon plan start` (CLI) or `/beacon-pln-program` (host); `plan_mode` recorded in program-manifest.
- **Program freeze** requires all lakes in `feature-graph.json` to be `status=frozen` and program parity matrix to have zero orphan capabilities.
- **Change** must append `change-intent-log.jsonl` before mutating promoted program or lake truth.
- **Sea utterances** must not collapse to a single lake without P3 feature-graph and user ack (P4).

## Hard gates (unchanged from v1.6.0)

- TIG block on freeze/refreeze
- verify-closure anti fake-delivery
- Evaluator-only QA/release verdict
