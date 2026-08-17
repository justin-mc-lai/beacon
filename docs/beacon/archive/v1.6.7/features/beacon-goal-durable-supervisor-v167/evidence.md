---
slug: beacon-goal-durable-supervisor-v167
version: v1.6.7
status: frozen
revision_id: R1
---

# Evidence Index: beacon-goal-durable-supervisor-v167

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-gen-truth | requirement_truth | docs/beacon/archive/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md | frozen | truth |
| beacon-gen-truth | test_truth | docs/beacon/archive/v1.6.7/features/beacon-goal-durable-supervisor-v167/tests.md | frozen | truth |
| analysis | support_advisory | docs/beacon/archive/v1.6.7/research/beacon-goal-durable-supervisor-v167.md | indexed | change |
| analysis | support_advisory | .beacon/state/planner-review/beacon-goal-durable-supervisor-v167/pln-review-goal-durable-supervisor.json | indexed | change |
| program | support_advisory | docs/beacon/archive/v1.6.7/programs/beacon-product-goal-domain-delivery-v167/feature-graph.json | indexed | program |
| parent | requirement_truth | docs/beacon/archive/v1.6.7/features/beacon-product-goal-runtime-v167/truth.md | frozen | dependency |
| interrupt-parity | requirement_truth | docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/truth.md | frozen | dependency |
| domain-fsm | support_advisory | docs/beacon/archive/v1.6.7/.machine/domain-fsm/beacon-goal-durable-supervisor-v167.json | indexed | truth |
| beacon-gen-implement | support_advisory | beacon/utils/product_goal_runtime.py | indexed | implement |
| beacon-gen-implement | support_advisory | beacon/commands/goal.py | indexed | implement |
| beacon-gen-implement | support_advisory | beacon/utils/goal_durable_supervisor.py | indexed | implement |
| beacon-gen-implement | support_advisory | tests/test_v167_goal_durable_supervisor.py | indexed | implement |
| beacon-gen-implement | support_advisory | skills/beacon/beacon-goal/SKILL.md | indexed | implement |

| beacon-eval-qa | qa_verdict | .beacon/qa/features/beacon-goal-durable-supervisor-v167/scorecard.json | indexed | qa |
| beacon-eval-qa | support_advisory | docs/beacon/archive/v1.6.7/execution/qa-acceptance-brief-beacon-goal-durable-supervisor-v167.md | indexed | qa |
| beacon-eval-qa | support_advisory | .beacon/evidence/auto-test/run-20260718T093512395075/ | indexed | qa |

## Boundary

`evidence.md` is an index/read model. It must not contain final verdict, gate truth, or release readiness authority fields.
