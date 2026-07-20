---
slug: beacon-plan-goal-deep-integration-v169
version: v1.6.9
status: frozen
revision_id: R1
language: zh
change_reason: "User GO: P0 plan_artifact + P1 host_subagent/stage_trace/plan_to_truth_hint + P2 design/truth checklists"
---

# Requirement Truth: Plan ↔ Goal Deep Integration (P0–P2)

## Intent

在 1+6 公开面下补齐 plan 第一性原理产出、goal 宿主子代理门控与阶段 trace、plan→truth 软提示、design/truth 哲学与 Domain-FSM 清单；**不**新增第 7 个 harness；plan **永不** freeze truth / implement。

## UD

| ID | Value |
|----|-------|
| UD-PA-001 | plan_artifact.v1: deep_want + options + recommended_next |
| UD-PA-002 | plan 阶段 writes_truth / may_implement 恒 false |
| UD-PA-003 | high_risk 启发式（支付/权限/状态机/parity…） |
| UD-P1-001 | create_goal_run 写入 host_subagent（关键词门控；默认单线程） |
| UD-P1-002 | stage_trace 指向 execution.jsonl；per_stage trace_ref |
| UD-P1-003 | plan→truth 仅 soft hint（blocked=false） |
| UD-P2-001 | design-philosophy-checklist.md |
| UD-P2-002 | domain-fsm-truth-checklist.md |
| UD-P2-003 | build_stage_plan 对 design/truth 附加 references |

## AC

| ID | Description |
|----|-------------|
| AC-PA-001 | artifact schema + deep_want + options + recommended_next |
| AC-PA-002 | plan_progressive_loads 附带 plan_artifact |
| AC-PA-003 | build_stage_plan hoist plan_artifact |
| AC-PA-004 | plan_to_truth_gate soft；missing/incomplete 不 hard-block |
| AC-PA-005 | create_goal_run 顶层 plan_artifact |
| AC-P1-001 | 无关键词 → host_subagent.gate_on false |
| AC-P1-002 | 「子代理」→ gate_on true，不自完成 goal |
| AC-P1-003 | tick plan→truth 写入 plan_to_truth_hint + stage_trace |
| AC-P2-001 | 两份 checklist 文件存在 |
| AC-P2-002 | design/truth stage references 含 checklist |
| AC-P2-003 | SKILL 提及 artifact / checklist |

## Non-goals

- 自动 spawn host agents
- 用 soft gate 硬挡 tick
- 第 7 公开 harness
- 伪造 QA scorecard

## Runtime

- `beacon/utils/plan_artifact.py`
- `beacon/utils/plan_subintent.py`（attach）
- `beacon/utils/product_goal_runtime.py`（create/tick）
- `beacon/utils/host_subagent_gate.py`（evaluate only）
