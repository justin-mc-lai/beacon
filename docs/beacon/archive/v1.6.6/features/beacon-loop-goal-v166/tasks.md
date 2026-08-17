---
slug: beacon-loop-goal-v166
version: v1.6.6
status: draft
revision_id: R6
language: zh
truth_ref: docs/beacon/archive/v1.6.6/features/beacon-loop-goal-v166/truth.md
parser_contract: beacon-feature-package-v2
---

# Tasks: Loop Goal Orchestrator v1.6.6

## Task List

- [x] TASK-001..022 — prior revisions R1..R5 (truth-on-main + standard execution + public skill) delivered / accepted under R5 QA
- [x] TASK-023 change → `beacon-gen-change` — R6 reopen + draft human-gate redefinition (AC-014 rewrite + AC-027..030)
- [x] TASK-024 implement → `beacon-gen-implement` — update `loop_goal_state.record_review_decision`：P1-only → `standard_execution_precheck` + continue audit；blocking = P0 | user_decision_required | drift routes
- [x] TASK-025 implement → `beacon-gen-implement` — update public/packaged `beacon-loop-goal` SKILL.md：AC-014 R6 规则、同会话立即加载下一 skill、auto-decide 表对齐
- [x] TASK-026 implement → `beacon-gen-implement` — add `beacon status loop-goal --resume`（读 state，返回 stage + next skill；禁止 no-op 伪装）
- [x] TASK-027 implement → `beacon-gen-implement` — emit observability fields：human_stops_per_run / stop_reason 分布 / p1_continue_count（pseudo_stall 可判定时）
- [x] TASK-028 implement → `beacon-gen-implement` — pytest TC-LG-014 行为翻转 + TC-LG-027..030
- [ ] TASK-029 qa → `beacon-eval-qa` — behavioral QA for AC-014/027..030 after implementation；formal verdict remains evaluator-owned
- [ ] TASK-030 release → `beacon-eval-release` — human gate before ship（unchanged AC-007）
