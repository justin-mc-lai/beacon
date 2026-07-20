---
name: beacon-plan
description: >
  beacon public plan harness. Use when the user wants planning, multi-angle review,
  brainstorming before freeze, source-anchored research from code, sea-to-lake program planning,
  or friction capture — without implementing or freezing truth.
  Triggers on: 规划, 审查, review, brainstorm, 先想清楚, 对着代码, 源码调研, 拆海, program, parity, 状态机.
  Routes by strong intent to pln-review / pln-brainstorm / pln-source / pln-program / pln-friction.
  Not for longrun (use beacon-goal). Not for implement/qa/release.
metadata:
  version: "v1.6.9"
  brand: Beacon
  public_surface: true
  public_id: "plan"
  harness: "plan"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  subintent_router: beacon.utils.plan_subintent
  dual_install_with: loom-plan
  longrun: false
---

# beacon-plan

**公开面**：plan（Rust ability: `loop`）  
**长程**：否 → 用 `beacon-goal`

## 强意图路由（primary）

| 意图 | Primary skill | 产出 |
|------|---------------|------|
| 审查 / review / parity / 状态机 | pln-review | planner_review |
| brainstorm / 先想清楚 / 先别写需求 | pln-brainstorm | brainstorm_note |
| 对着代码 / 源码 / 别瞎编 | pln-source (+ review) | source_research |
| 拆海 / program / 多模块 | pln-program* | program_plan |
| 摩擦 / 阻塞 | pln-friction | friction_queue_item |
| 默认 | pln-program | light plan |

Runtime: `detect_plan_subintent` / `plan_progressive_loads_for_utterance`.

## HARD GATE（planner）

- 禁止 implement / 写 frozen truth / QA·release verdict
- 深研与审查结果是 **plan artifact**，升级 freeze 必须走 truth

## Progressive

Primary first, then full set for capability non-regression.

## Examples

- `skills/beacon/examples/surface-plan-review-30s.md`
- `skills/beacon/examples/surface-plan-brainstorm-30s.md`
- `skills/beacon/examples/surface-plan-source-research-30s.md`

## plan_artifact.v1（P0 first-principles）

Runtime: `beacon.utils.plan_artifact.build_plan_artifact`  
Attached on: `plan_progressive_loads_for_utterance` → `plan_artifact`, and goal `create_goal_run` top-level + plan stage.

| Field | Meaning |
|-------|---------|
| surface_ask | 表层诉求 |
| deep_want | 深层目标（脚手架；agent 须 refinement） |
| options | 可走路径 + tradeoff |
| recommended_next | 建议下一动作 / stage hint |
| non_goals | 含：plan 不写 frozen truth、不实现 |
| high_risk | 支付/权限/安全/状态机/parity 等 |
| structurally_complete | 结构齐全标记 |

**Soft gate**：`plan_to_truth_gate` → goal `plan_to_truth_hint`（不硬挡 tick）。

## Examples（30s）

- `skills/beacon/examples/surface-plan-review-30s.md`
- `skills/beacon/examples/surface-plan-brainstorm-30s.md`
- `skills/beacon/examples/surface-plan-source-research-30s.md`

