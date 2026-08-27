---
slug: beacon-v1614-fsm-test-generation
version: v1.6.14
status: frozen
language: zh
domain_required: false
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
package_maturity: filled
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md
  user_story: docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/truth.md
  test_case: docs/beacon/v1.6.14/features/beacon-v1614-fsm-test-generation/tests.md
---

# Requirement Truth: beacon-v1614-fsm-test-generation (v1.6.14)

## 人话

让 beacon 的**状态机自动长出测试用例**。现在 v1.6.13 的域湖要手写"状态机走一遍"的测试（legal-walk）。这次做到：**只要需求真相里状态机写得合法，系统就能自动生成一套"合法路径"测试用例**，覆盖"从开始走到结束"的每个合法路线，并且到每个状态点都断言"确实到达了"。

- 能做：从合法 FSM 自动生成 legal-walk 测试用例；生成的用例进 exec-layer TC；非法路径不生成
- 不能做：不生成非法的（被 illegal 排除的）路径；不覆盖人类业务判断（如"金额要小于 100"这种 guard 逻辑仍需手写）
- 怎样算完：域湖的 FSM 有测试覆盖率证明（合法路径全走到），且非法转换没有被生成出来

## User Intent

用 GraphWalker 式"模型→路径生成"思路，让 beacon 从 truth FSM 自动生成 legal-walk exec 测试，对接 v1.6.13 域湖的 FSM legal-walk 测试（vertex=断言）。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: 2026-08-27 intel-radar 调研（GraphWalker）+ v1.6.13 D2 域湖 FSM legal-walk
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | FSM → legal-walk 测试生成 | must | AC-001 | covered |
| INT-002 | 生成用例进 exec-layer TC | must | AC-002 | covered |
| INT-003 | vertex=断言（到达状态即验证） | must | AC-003 | covered |
| INT-004 | illegal 路径不生成 | must | AC-004 | covered |

## 用户旅程

1. 触发：truth 冻结时（域湖 FSM 合法）
2. 关键操作：FSM 生成器走合法路径（从 initial 到 terminal，经每个可达状态），每个状态生成到达断言
3. 结果：tests.md 自动出现 legal-walk TC；QA 跑通
4. 异常：FSM 不合法 → 生成器拒绝（fail-closed，回 FSM 校验）

## First principles

- 系统边界：只从合法 FSM 生成；guards 业务条件不自动生成（需手写断言）
- 不可变：illegal 路径永不被生成；vertex 断言基于 FSM 定义
- 可推翻假设：路径生成策略（深度优先/随机）可配置，但覆盖完整可达状态是底线

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| FsmModel | states, transitions, initial, terminal, illegal | 输入 |
| LegalPathWalker | walk from initial to terminal, visited states | 生成器 |
| GeneratedTc | tc_id, path, per-state assertion | 产物 |
| IllegalExcluder | illegal transitions filtered | 安全网 |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 从合法 truth FSM 自动生成 legal-walk 测试用例（覆盖从 initial 到 terminal 的合法路径，可达状态全走）。 |
| AC-002 | 生成的用例作为 exec-layer TC 进 tests.md（可执行、断言退出码）。 |
| AC-003 | 每个到达状态生成顶点断言（vertex=验证：进入该状态即断言成功）。 |
| AC-004 | illegal 转换路径不被生成（生成器排除 illegal，产出中无非法路径）。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| generated | fsm_valid | walk_ok |
| tc_bound | generated | ac_bind |
| covered | tc_bound | all_reachable_visited |
| released | covered | qa_pass |

## Illegal transitions

- fsm 不合法仍生成（跳过校验）
- illegal 路径被生成（安全网失效）

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | generate | fsm_valid | generated | walk_legal_paths |
| generated | bind | ac_mapped | tc_bound | assign_tc |
| tc_bound | cover | reachable_all | covered | mark_covered |
| covered | release | qa_pass | released | ship |

**终态：** released（覆盖完备）

### invalid / illegal

- fsm 不合法仍生成（illegal：跳过校验）
- illegal 路径被生成（illegal：安全网失效）

## Non-goals

- 不自动生成 guards 业务条件断言（需手写）
- 不替代人工设计测试意图
- 不生成超出 FSM 定义的行为

## Freeze readiness

- [x] Intent Matrix must 无 missing
- [x] 用户旅程非「待补」占位
- [x] First principles / Domain Model 已具体化
- [x] 元状态 FSM + illegal
- [x] 每 AC ≥ 1 TC（Command+Assertion）+ exec-layer TC
- [x] tasks 均有 ac= + evidence= 绑定
- [x] package_maturity: filled
- [x] `beacon truth review` pass 后再 freeze

### Gap vs gold (订单支付示例)

- 对照：`docs/beacon/v1.6.10/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`

## Source Excerpt

```markdown
beacon-v1614-fsm-test-generation
调研：GraphWalker（graphwalker.github.io）——模型化测试：vertex=验证、edge=动作、自动生成路径
对接：v1.6.13 beacon-v1613-d2-spend-ledger 的 test_fsm_legal_walk（手写 → 本湖自动生成）
```
