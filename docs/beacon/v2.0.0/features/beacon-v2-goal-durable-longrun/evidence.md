---
slug: beacon-v2-goal-durable-longrun
version: v2.0.0
status: frozen
revision_id: R3
---

# Evidence Index: beacon-v2-goal-durable-longrun

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| requirement_truth | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/truth.md | frozen R3 | truth |
| test_truth | test_truth | docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tests.md | frozen R3 | truth |
| tasks | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-goal-durable-longrun/tasks.md | frozen R3 | truth |
| upstream | requirement_truth | docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md | frozen | parity |
| program | support_advisory | docs/beacon/v2.0.0/programs/beacon-v2-product-goal-parallel-v200/feature-graph.json | indexed | program |
| research_longrun | support_advisory | docs/beacon/v2.0.0/research/beacon-v2-goal-durable-longrun.md | indexed | change |
| research_steering | support_advisory | docs/beacon/v2.0.0/research/loom-goal-steering-codex-continuation-pln-review.md | accepted GO | change |
| change_r3 | support_advisory | docs/beacon/v2.0.0/change/beacon-v2-goal-durable-longrun-steering-r3.md | indexed | change |
| steering_fixtures | requirement_truth | docs/beacon/v2.0.0/fixtures/steering/continuation.md | contract asset | implement |
| steering_fixtures | requirement_truth | docs/beacon/v2.0.0/fixtures/steering/budget_limit.md | contract asset | implement |
| steering_fixtures | requirement_truth | docs/beacon/v2.0.0/fixtures/steering/objective_updated.md | contract asset | implement |
| must_checklist | requirement_truth | skills/beacon/references/goal-steering/MUST_SECTIONS.md | contract asset | implement |
| parent | requirement_truth | docs/beacon/v2.0.0/features/beacon-v2-product-goal-orchestrator/truth.md | frozen | dependency |
| implement_tests | test_truth | tests/test_v200_goal_durable_longrun.py | partial (ST package tests pass; inject wire open (TASK-V2-ST)) | implement |

## Boundary

`evidence.md` is an index/read model only. Not acceptance/release authority.

## R3 notes

- User GO 2026-07-19: hang durable-longrun; objective_updated Must; complete→awaiting_verifier; gen-change
- Package ST contract tests: `pytest -k 'steering or continuation_must or ...'` → 7 passed
- Runtime inject wire-up remains open under TASK-V2-ST-*


## R3 implement (2026-07-20)

- Module: `beacon/utils/goal_steering.py` (InjectBundle + templates)
- Driver: `beacon/utils/goal_agent_driver.py` `render_turn_prompt` uses InjectBundle order
- Suite: `python3 -m pytest tests/test_v200_goal_durable_longrun.py` → **31 passed**
- Skills: beacon-goal / loom-goal longrun section documents InjectBundle
- Complete still requires verifier; release human
