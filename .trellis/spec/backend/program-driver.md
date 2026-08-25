# Code-Spec: Program Lake Driver

> Contract for `beacon program drive` and the goal→program takeover hint. Added in v1.6.12 (task 08-25-program-lake-driver).

---

## Scenario: program-level phased-lake auto-dispatch

### 1. Scope / Trigger

- New public command `beacon program drive <slug>`; new runtime module `beacon/utils/program_driver.py`; additive fields on goal facade payload when a program route is pending.
- Consumes `build_program_orchestrator_state` routes (`beacon/utils/program_orchestrator.py`). The driver is a **dispatcher, not an executor**: it never writes truth, never runs implementation itself, never issues QA/release verdicts.

### 2. Signatures

- CLI: `beacon program drive <slug> [--project/-p ROOT] [--version/-v V] [--status-only] [--max-turns N] [--json]`
  - Exit `0` on complete/passive stops, exit `2` on blocked stops (same convention as `orchestrate`).
- Python: `program_drive_once(project_root, *, version="auto", program_slug, spawn_fn=None, bridge_cmd=None)` → single tick; `program_drive_loop(...)` bounded by budget/max-turns; `program_drive_start|status|stop(...)` mirror `goal_agent_driver.driver_*` shape.
- Goal side: `attach_program_takeover_hint(payload)` in `beacon/utils/product_goal_runtime.py` — called on the facade terminal path.

### 3. Contracts

- Drive state: `docs/beacon/<v>/programs/<slug>/program-drive-state.json` (separate from orchestrate-owned `program-run-state.json`). Lock: `.beacon/state/program-drive/<slug>.lock` (pid-alive check). Turn prompts: `.beacon/state/program-drive/<slug>/turn-N.prompt.md`.
- Every terminal return includes `reason_code` + `resume_action` (AC-039 resilient stop contract).
- resume_action → dispatch mapping (closed set): `prepare_next_lake_truth → beacon-gen-truth`, `run_lake_implementation → beacon-gen-implement`, `run_lake_qa → beacon-eval-qa`. **No release entry exists**; enforced via `assert_no_auto_release_policy()`.
- Progression is evidence-only: after each spawn, recompute route from `_truth_frozen` / `_implementation_closed` / `_qa_closed` filesystem artifacts. Driver memory never advances a lake/stage.
- Goal payload additions are **add-only and conditional**: present only when the program route resolves a pending `next_lake` — `program_takeover{command, next_lake, ...}`, `recommended_next["program"]`, one history event. Unbound goals are byte-identical to pre-feature output.

Binding precondition (gotcha): a goal run attaches to a program only if `docs/beacon/<v>/programs/<slug>/feature-graph.json` contains a `lakes[]` row for the feature AND `_is_program_frozen` passes (freeze file `status=frozen` or manifest/graph `program_plan_frozen=true` / `lake_package_truth_frozen=true`). Minimal graphs shaped `{"features": [...], "edges": []}` never bind — this is why legacy single-feature programs stay standalone.

### 4. Validation & Error Matrix

| Condition | reason_code | resume_action |
|---|---|---|
| graph invalid / unparsable | `feature_graph_invalid` | `none` |
| no `lakes[]` rows | `program_lakes_missing` | `none` |
| upstream lake unclosed | `await_upstream_lake_closure` | `none` (zero spawn) |
| release stage reached | `await_human_gate` | `await_human_confirmation` |
| all lakes closed | `program_complete` | `none` |
| no bridge configured | `host_bridge_missing` | `replay_substep` |
| spawn failed / non-zero | `host_spawn_failed` | `replay_substep` |
| identical route fingerprint ×3 | `blocked_streak` | `replay_substep` |
| turn/budget exhausted | `halt_budget` | `replay_substep` |
| unknown resume_action | `unknown_resume_action` | `none` |

### 5. Good/Base/Bad Cases

- Good: A→B→C chain, B depends_on A. A truth→implement→qa closes from filesystem evidence ⇒ next tick renders B-truth prompt; reaching C's release stops with `await_human_gate`.
- Base: crash mid-B-implement ⇒ rerun `drive` reloads persisted state, recomputes evidence, resumes B at implement without redoing A.
- Bad: driver "remembers" B finished and skips ahead without closure artifacts — forbidden; also spawning any prompt for a release stage — forbidden.

### 6. Tests Required

- `tests/test_v1612_program_lake_driver.py`: sequential multi-lake advance; release-stage human-gate stop (assert no release skill ever rendered); dependency no-dispatch; crash-resume idempotence; streak/budget stops emit reason_code+resume_action; goal hint present iff next_lake exists and absent otherwise. Use injected `spawn_fn`; never real subprocess/bridge in CI.

### 7. Wrong vs Correct

#### Wrong
```python
if lake in state["passed_lakes"]:   # trusting driver memory
    continue
```

#### Correct
```python
route = build_program_orchestrator_state(root, version=v, program_slug=slug)
# advance strictly from recomputed filesystem evidence (route.lakes[*].complete / stage)
```
