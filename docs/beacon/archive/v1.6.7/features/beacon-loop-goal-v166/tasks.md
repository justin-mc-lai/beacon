---
slug: beacon-loop-goal-v166
version: v1.6.7
status: draft
revision_id: R7
language: zh
truth_ref: docs/beacon/archive/v1.6.7/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tasks: Loop Goal Orchestrator v1.6.7

## Task List

- [x] TASK-001..022 — prior revisions R1..R5 (truth-on-main + standard execution + public skill) delivered / accepted under R5 QA
- [x] TASK-023 change → `beacon-gen-change` — R6 reopen + draft human-gate redefinition (AC-014 rewrite + AC-027..030)
- [x] TASK-024 implement → `beacon-gen-implement` — update `loop_goal_state.record_review_decision`：P1-only → `standard_execution_precheck` + continue audit；blocking = P0 | user_decision_required | drift routes
- [x] TASK-025 implement → `beacon-gen-implement` — update public/packaged `beacon-loop-goal` SKILL.md：AC-014 R6 规则、同会话立即加载下一 skill、auto-decide 表对齐
- [x] TASK-026 implement → `beacon-gen-implement` — add `beacon status loop-goal --resume`（读 state，返回 stage + next skill；禁止 no-op 伪装）
- [x] TASK-027 implement → `beacon-gen-implement` — emit observability fields：human_stops_per_run / stop_reason 分布 / p1_continue_count（pseudo_stall 可判定时）
- [x] TASK-028 implement → `beacon-gen-implement` — pytest TC-LG-014 行为翻转 + TC-LG-027..030
- [x] TASK-029 qa → `beacon-eval-qa` — R6 regression QA (carried forward)
- [x] TASK-030 release → `beacon-eval-release` — human gate before ship（unchanged AC-007）


- [x] TASK-031 change → `beacon-gen-change` — R7 reopen intent continuation + topology_gate + dual runtime (AC-031..040)
- [x] TASK-032 implement → `beacon-gen-implement` — IntentContext, record_intent_fork, decision_cache, interrupt semantics
- [x] TASK-033 implement → `beacon-gen-implement` — `beacon loop-goal run` CLI + resume utterance map
- [x] TASK-034 implement → `beacon-gen-implement` — topology_gate consume in precheck; SKILL.md R7 sync
- [x] TASK-035 implement → `beacon-gen-implement` — v2 schema parity fixtures + tests/test_v167_loop_goal.py
- [x] TASK-036 qa → `beacon-eval-qa` — AC-031..040 QA passed
- [x] TASK-037 release → `beacon-eval-release` — human gate before ship
