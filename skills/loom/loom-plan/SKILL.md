---
name: loom-plan
description: >
  loom public plan harness. Use when the user wants planning, multi-angle review,
  brainstorming before freeze, source-anchored research from code, sea-to-lake program planning,
  or friction capture — without implementing or freezing truth.
  Triggers on: 规划, 审查, review, brainstorm, 先想清楚, 对着代码, 源码调研, 拆海, program, parity, 状态机.
  Routes by strong intent to pln-review / pln-brainstorm / pln-source / pln-program / pln-friction.
  Not for longrun (use loom-goal). Not for implement/qa/release.
metadata:
  version: "v1.6.9"
  brand: Loom
  public_surface: true
  public_id: "plan"
  harness: "plan"
  progressive_map: skills/beacon/references/public-surface-progressive-map.v1.json
  subintent_router: beacon.utils.plan_subintent
  dual_install_with: beacon-plan
  longrun: false
---

# loom-plan

**公开面**：plan（Rust ability: `loop`）  
**长程**：否 → 用 `loom-goal`

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
