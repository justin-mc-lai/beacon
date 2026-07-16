# Agent Eval Contract (v1.6.1)

Normative public CLI for `beacon-agent-eval-v161`.

## Public entry

```bash
beacon eval catalog --project-root . --version v1.6.1 --json
beacon eval run --split regression-core|optimization|holdout|all --runner replay|simulated|live --version v1.6.1 --json
beacon eval scorecard --project-root . --version v1.6.1 --json
beacon eval benchmark --version v1.6.1 --json
```

All outputs include:

- `runtime_evidence_only=true`
- `formal_verdict_authority=false`
- `release_verdict_authority=false`

## Machine artifacts

| Artifact | Path |
|----------|------|
| Capability catalog | `docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-capability-catalog-v161.json` |
| Live skill matrix | `docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-live-skill-matrix-v161.json` |
| Live runner admission | `docs/beacon/archive/v1.6.1/.machine/execution/agent-eval-runner-admission.json` |

## Live skill matrix

- Authoritative skill set: `v160_skill_package_projection()` (**36**) + `beacon-eval-agent` = **37** entries
- Materialize via `beacon eval catalog --materialize`
- `--runner live --split regression-core` executes per-skill traces under `.beacon/state/agent-eval/runs/<run-id>/traces/live-skills/`

## Runner admission

Live runner requires valid admission JSON:

```json
{
  "schema_version": "1.0",
  "admitted": true,
  "host": "cursor",
  "trace_format": "agent-eval-live-v1",
  "timeout_seconds": 300
}
```

Without admission: `status=blocked`, `reason_code=agent_eval_live_runner_not_admitted`.

## Scorecard schema

Scorecards write to `.beacon/state/agent-eval/scorecards/<scorecard-id>.json`.

Dimensions (0–100):

- `route_stability` (15%)
- `boundary_preservation` (20%)
- `source_anchor_coverage` (10%)
- `capability_catalog_coverage` (20%)
- `behavior_evidence_quality` (25%)
- `fake_delivery_resistance` (10%)

Simulated mode: `degraded=true`, `simulated_composite_score` present, `composite_score` capped at **85**.

## Benchmark artifacts

`beacon eval benchmark --version v1.6.1` writes:

- `eval_metadata/`
- `grading/`
- `benchmark/`
- `analysis/`

Root: `.beacon/state/agent-eval/benchmarks/<benchmark-id>/`

## Skill eval kit bridge

`beacon skill eval-kit` and `beacon eval` share boundary replay cases via `.beacon/state/skill-eval` (documented in agent-eval `cases.json` as `shared_skill_eval_root`).

## Host skill

- `beacon-eval-agent` (evaluator harness) routes to `beacon eval *`
- HARD GATE: no truth write, no implementation repair, no release verdict

## Authority

Agent Eval scorecard may supplement Acceptance Kit `trace-scorecard` layer only. It does **not** replace formal QA or release gates.
