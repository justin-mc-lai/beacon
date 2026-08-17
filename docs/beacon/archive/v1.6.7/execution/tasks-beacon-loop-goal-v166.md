# Beacon Implementation Tasks Ledger

- feature: `beacon-loop-goal-v166`
- version: `v1.6.7`
- plan_id: `plan-beacon-loop-goal-v166-r7`
- revision_id: `R7`
- progress: `15/15`
- status: `completed`
- next_task: ``
- blocked_tasks: `0`

## Recovery
- progress_json: `docs/beacon/archive/v1.6.7/.machine/execution/implementation-plan-beacon-loop-goal-v166.progress.json`
- canonical_plan_json: `docs/beacon/archive/v1.6.7/.machine/execution/implementation-plan-beacon-loop-goal-v166.json`
- task ledger is a human-readable projection only; gate and machine progress still read canonical plan/progress artifacts.

## Tasks

[x] `ITASK-001` TASK-023 change → `beacon-gen-change` — R6 reopen + draft human-gate redefinition (AC-014 rewrite + AC-027..030)
  - tests=TEST-014,TEST-027,TC-LG-014,TC-LG-027
[x] `ITASK-002` TASK-024 implement → `beacon-gen-implement` — update `loop_goal_state.record_review_decision`：P1-only → `standard_execution_precheck` + continue audit；blocking = P0 | user_decision_required | drift routes
  - tests=TEST-015,TEST-001,TC-LG-001,TC-LG-015 | depends_on=ITASK-001
[x] `ITASK-003` TASK-025 implement → `beacon-gen-implement` — update public/packaged `beacon-loop-goal` SKILL.md：AC-014 R6 规则、同会话立即加载下一 skill、auto-decide 表对齐
  - tests=TEST-029,TEST-028,TEST-013,TEST-016,TC-LG-013,TC-LG-016,TC-LG-028,TC-LG-029 | depends_on=ITASK-002
[x] `ITASK-004` TASK-026 implement → `beacon-gen-implement` — add `beacon status loop-goal --resume`（读 state，返回 stage + next skill；禁止 no-op 伪装）
  - tests=TEST-035,TEST-034,TEST-004,TC-LG-004 | depends_on=ITASK-003
[x] `ITASK-005` TASK-027 implement → `beacon-gen-implement` — emit observability fields：human_stops_per_run / stop_reason 分布 / p1_continue_count（pseudo_stall 可判定时）
  - tests=TEST-040 | depends_on=ITASK-004
[x] `ITASK-006` TASK-028 implement → `beacon-gen-implement` — pytest TC-LG-014 行为翻转 + TC-LG-027..030
  - tests=TEST-008,TEST-003,TC-LG-003,TC-LG-008 | depends_on=ITASK-005
[x] `ITASK-007` TASK-029 qa → `beacon-eval-qa` — R6 regression QA (carried forward)
  - tests=TEST-009,TC-LG-009 | depends_on=ITASK-006
[x] `ITASK-008` TASK-030 release → `beacon-eval-release` — human gate before ship（unchanged AC-007）
  - tests=TEST-007,TC-LG-007 | depends_on=ITASK-007
[x] `ITASK-009` TASK-031 change → `beacon-gen-change` — R7 reopen intent continuation + topology_gate + dual runtime (AC-031..040)
  - tests=TEST-031 | depends_on=ITASK-008
[x] `ITASK-010` TASK-032 implement → `beacon-gen-implement` — IntentContext, record_intent_fork, decision_cache, interrupt semantics
  - tests=TEST-030,TEST-032,TEST-033,TC-LG-030 | depends_on=ITASK-009
[x] `ITASK-011` TASK-033 implement → `beacon-gen-implement` — `beacon loop-goal run` CLI + resume utterance map
  - tests=TEST-023,TEST-026,TEST-022,TC-LG-022,TC-LG-023,TC-LG-026 | depends_on=ITASK-010
[x] `ITASK-012` TASK-034 implement → `beacon-gen-implement` — topology_gate consume in precheck; SKILL.md R7 sync
  - tests=TEST-036 | depends_on=ITASK-011
[x] `ITASK-013` TASK-035 implement → `beacon-gen-implement` — v2 schema parity fixtures + tests/test_v167_loop_goal.py
  - tests=TEST-039 | depends_on=ITASK-012
[x] `ITASK-014` TASK-036 qa → `beacon-eval-qa` — AC-031..040 QA passed
  - tests=TEST-025,TC-LG-025 | depends_on=ITASK-013
[x] `ITASK-015` TASK-037 release → `beacon-eval-release` — human gate before ship
  - tests=TEST-006,TEST-019,TEST-021,TEST-024,TEST-002,TEST-005,TEST-010,TEST-011,TEST-012,TEST-017,TEST-018,TEST-020,TEST-037,TEST-038,TC-LG-002,TC-LG-005,TC-LG-006,TC-LG-010,TC-LG-011,TC-LG-012,TC-LG-017,TC-LG-018,TC-LG-019,TC-LG-020,TC-LG-021,TC-LG-024 | depends_on=ITASK-014
