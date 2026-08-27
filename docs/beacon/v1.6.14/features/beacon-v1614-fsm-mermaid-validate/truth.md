---
slug: beacon-v1614-fsm-mermaid-validate
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
  prd: docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md
  user_story: docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md
  test_case: docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/tests.md
---

# Requirement Truth: beacon-v1614-fsm-mermaid-validate (v1.6.14)

## 人话

把 beacon 需求真相里的"状态机"从**一张表格**升级成**一套专业契约**。要达成三件事：

1. **自动画图**：每个 truth 的状态机段自动带一张 mermaid 状态图，打开文档就能看到状态怎么流转，不用人肉看表格。
2. **机器能校验**：状态机不再是"写了就信"——系统能检查它是否合法：状态存不存在、转移对不对、非法转移（比如跳过审核直接冻结）有没有被挡。
3. **改了能发现**：状态机的"行为变化"和"只是换个说法"能区分开，防止悄悄改掉验收语义。

- 能做：truth 生成时自动带 mermaid 图；校验器解析 FSM 表检查合法性；行为变化可检测
- 不能做：不改各域湖的业务语义；不引入新命令面；状态机本身仍是需求真相的一部分
- 怎样算完：任何 truth 的状态机都能渲染成图 + 通过合法性校验 + 非法转移被拦（freeze 门禁 fail-closed）

## User Intent

把 beacon truth 的 FSM 五元组升级为「单源：渲染（mermaid）+ 机器校验（states/transitions/illegal）+ 行为变化检测（digest）」，对齐 statespec 模式。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: 2026-08-27 intel-radar 调研（statespec）
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | FSM 自动渲染 mermaid | must | AC-001 | covered |
| INT-002 | FSM 机器校验（states/transitions/illegal） | must | AC-002 | covered |
| INT-003 | 行为变化可检测（digest） | must | AC-003 | covered |
| INT-004 | 校验进入 freeze 门禁（fail-closed） | must | AC-004 | covered |

## 用户旅程

1. 触发：gen-truth 冻结任何 feature 的 truth
2. 关键操作：truth 的 FSM 段自动附带 mermaid 图；校验器解析 states/transitions/illegal
3. 结果：文档可见状态图；非法转移被校验器拦截（如 draft→frozen 跳过审核）
4. 异常：FSM 不合法 → freeze 被拦（fail-closed），需修 FSM

## First principles

- 系统边界：FSM 是需求真相的一部分，升级只加"渲染+校验+检测"，不改业务语义
- 不可变：状态/转移/illegal 是验收权威，mermaid 只是展示投影；校验结果不得反向改 truth
- 可推翻假设：digest 只区分"行为变化 vs 措辞变化"，不替代 revision 绑定

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| TruthFsm | states, transitions, illegal, guards | truth 里的 FSM 五元组 |
| FsmValidator | state_exists, transition_legal, illegal_blocked | 校验器 |
| FsmDigest | behavior_digest, wording_digest | 行为 vs 措辞变化 |
| MermaidRender | stateDiagram-v2, states, transitions | 展示投影 |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | truth 生成/冻结时，FSM 段自动附带 `stateDiagram-v2` mermaid 块（状态+转移），文档可渲染。 |
| AC-002 | FSM 机器校验：校验器可解析 truth FSM 表，检查 状态存在 / 转移合法 / illegal 转换被拒，输出结构化 findings。 |
| AC-003 | FSM 行为变化可检测：同一 FSM 的 states/transitions 变化产生不同 behavior digest，仅措辞变化不改变 digest。 |
| AC-004 | FSM 校验进入 freeze 门禁：FSM 不合法（如非法转移未声明）→ freeze fail-closed（reason_code `truth_fsm_invalid`）。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| rendered | scaffold | fsm_present |
| validated | rendered | validator_pass |
| digest_bound | validated | digest_computed |
| frozen | digest_bound | gate_ok |

## Illegal transitions

- scaffold → frozen（skip validate）
- fsm 不合法仍 freeze（校验绕过）

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | rendered | gen_mermaid |
| rendered | validate | states_ok ∧ transitions_ok ∧ illegal_ok | validated | run_validator |
| validated | digest | behavior_stable | digest_bound | compute_digest |
| digest_bound | freeze | gate_ok | frozen | set_frozen |

**终态：** frozen

### invalid / illegal

- scaffold → frozen without validate（illegal：跳过校验冻结）
- fsm 不合法仍 freeze（illegal：gate 绕过）

## Non-goals

- 不改各域湖业务 FSM 语义
- 不引入新命令面
- 不做可视化 IDE（只保证可渲染 + 可校验）

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
beacon-v1614-fsm-mermaid-validate
调研：statespec（pypi.org/project/statespec/）——声明式状态机单源：Mermaid 渲染 + validate + 语义 digest
beacon 现状：truth FSM 五元组为纯表格，无自动 mermaid、无机器校验、无 digest
```
