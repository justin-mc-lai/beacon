# Beacon v1.6.11 Source Architecture Index

## Existing authorities to reuse

| Module | Responsibility |
|--------|----------------|
| `beacon/utils/product_goal_runtime.py` | GoalRun orchestration and stage ownership |
| `beacon/utils/program_plan_state.py` | Program lifecycle state contract |
| `beacon/utils/intent_decomposition.py` | Intent decomposition |
| `beacon/utils/plan_artifact.py` | Plan artifact and Change inputs |
| `beacon/utils/planner_review_runtime.py` | Multi-reviewer/subagent review runtime |
| `beacon/utils/host_subagent_gate.py` | Intent-on host subagent gate |
| `beacon/utils/workspace_admission.py` | Real worktree admission |
| `beacon/utils/goal_implement_admission.py` | Goal adapter to shared admission |
| `beacon/utils/git_scope_graph.py` | Service/worktree topology |
| `beacon/utils/agent_trace.py` | `agent_trace.v1` lifecycle events |
| `beacon/utils/truth_review_gate.py` | Truth Review A–D |
| `beacon/utils/feature_package.py` | Current package shape and task/evidence gates |

## Planned v1.6.11 components

| Component | Responsibility | Must reuse |
|-----------|----------------|------------|
| Context resolver | commit/Truth/code/test/Change envelope | truth map + governance |
| Intent completeness engine | recursive must/should closure | intent decomposition |
| Change state diff | promise/interface/data/FSM/test delta | plan artifact |
| Task graph compiler | atomic DAG + delegation/admission bindings | Goal + subagent + admission |
| Progress ledger | task/path attempts and snapshots | Goal run_id + lifecycle index |
| Drift review gate | canonical human decision gate | planner findings |
| Replan scheduler | cancel/replacement/ready-set recompute | Goal runtime + admission |
| Convergence verifier | six-layer closure | QA evidence + Goal owner |

## Dependency direction

```text
frozen truth + governance
  -> GoalRun / ContextEnvelope
  -> intent + Change diff
  -> task DAG
  -> shared worktree admission / delegated execution
  -> progress + human decisions + agent_trace
  -> independent QA evidence
  -> Goal convergence verdict
```

No old-shape compatibility layer is permitted.

