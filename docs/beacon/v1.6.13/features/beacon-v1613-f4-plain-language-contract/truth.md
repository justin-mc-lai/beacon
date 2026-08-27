---
slug: beacon-v1613-f4-plain-language-contract
version: v1.6.13
status: frozen
language: zh
domain_required: false
ux_required: false
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
package_maturity: filled
materials_status: current
canonical_refs:
  prd: docs/beacon/v1.6.13/features/beacon-v1613-f4-plain-language-contract/truth.md
  user_story: docs/beacon/v1.6.13/features/beacon-v1613-f4-plain-language-contract/truth.md
  test_case: docs/beacon/v1.6.13/features/beacon-v1613-f4-plain-language-contract/tests.md
---

# Requirement Truth: beacon-v1613-f4-plain-language-contract (v1.6.13)

## 人话

这个湖做的事情很简单：**让 beacon 的 7 个核心 skill（plan/truth/implement/qa/release/design/goal）每次交付时，都必须附带一句"不懂项目的人也能看懂的话"**——告诉你这次到底做了什么、改了什么、下一步是什么。

就像每个工具都要求你附一张"给小孩看的说明书"：术语可以保留，但一定有一句话是普通人能懂的。

- 能做：7 个 skill 的"输出说明"里都强制要求这句人话；写法统一，都复用 truth 那套"人话"规范
- 不能做：不强迫把专业内容（验收标准编号、状态机、意图矩阵）也改成大白话——那些是机器验收用的，保持原样
- 怎样算完：7 个 skill 全部带上这个必填字段；真相冻结时缺"人话"会直接拦下来（不通过）

## User Intent

推广"人话交付"契约：让 beacon 全部核心 skill 的交付说明都强制要求普通人可懂的一句话总结，复用 truth 的 L0 人话规范，不动机器字段。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: beacon-v1613-planning-source-audit-2026-08-27 F4
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | F4 审计发现：人话只约束 truth | must | AC-001 | covered |
| INT-002 | 复用 truth L0 单一规范，不另造口径 | must | AC-002 | covered |
| INT-003 | 人话不改机器字段 | must | AC-003 | covered |
| INT-004 | 真相人话缺失 freeze 拦下 | must | AC-004 | covered |

## 用户旅程

1. 触发：agent 用任何一个 beacon skill 交付（plan/truth/implement/qa/release/design/goal）
2. 关键操作：skill 的 Output contract 强制要求先写"普通人能看懂的一句话交付总结"
3. 结果：交付消息开头是这句人话，专业细节在后；不懂项目的人能立刻知道这次做了什么
4. 异常：如果某个 skill 还没带上这个字段，实现阶段会被告知"缺人话字段，先补上"

## First principles

- 系统边界：只约束"面向人的交付说明"，不约束机器验收面
- 不可变：机器字段（AC ID / FSM / Intent Matrix / mode_id）必须原样保留，人话只做附加
- 可推翻假设：人话与机器字段并存；任何人话改写不得改动验收语义

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| BeaconSkill (design/goal/implement/plan/qa/release/truth) | output_contract, plain_language_delivery_summary | 7 个 core skill 共享人话字段 |
| HumanizerProfile | locale (zh/en), L0 norm | 复用 truth-humanizer 规范 |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 7 个 beacon core skill（design/goal/implement/plan/qa/release/truth）的 `SKILL.md` Output contract 均含必填字段 `plain_language_delivery_summary`（普通人可懂的一句话交付总结）。 |
| AC-002 | 该字段的语义与写法复用 truth 的 L0 `## 人话` / `## Plain language` 规范（truth-humanizer 口径），不另造一套。 |
| AC-003 | 人话字段只附加不替换：AC ID、FSM、Intent Coverage Matrix、mode_id 等机器字段保持原样，不被"人话化"改写。 |
| AC-004 | frozen truth 缺失人话 L0（zh `## 人话` / en `## Plain language`）时 freeze fail-closed（reason_code `truth_human_l0_missing`），此约束在 7 个 skill 的 truth 面均生效。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| filled | scaffold | ac_complete |
| frozen | filled | review_gate_pass |
| change | frozen | scope_ack |

## Illegal transitions

- filled → frozen（skip review_gate_pass）
- frozen truth without L0 人话（truth_human_l0_missing）

## FSM 五元组

> domain_required=false（skill 文档层湖），状态机用元状态即可。

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | fill | ac_complete | filled | materialize |
| filled | review | gate_ok | frozen | set_frozen |
| frozen | change | scope_ack | change | record_delta |

**终态：** frozen

### invalid / illegal

- filled → frozen without review_gate_pass
- frozen truth without L0 人话 → illegal（fail-closed）

## Non-goals

- 不重写各 skill 的模式正文（那是 L4 的 F2/F3/F5 范围）
- 不把机器字段人话化
- 不新增命令面
- 不强制英文 skill 使用中文人话（按 locale 各自对应）

## Freeze readiness

- [x] Intent Matrix must 无 missing
- [x] 用户旅程非「待补」占位
- [x] First principles / Domain Model 已具体化
- [x] domain 湖 FSM 五元组（元状态即可）
- [x] 每 AC ≥ 1 TC（Command+Assertion）+ exec-layer TC
- [x] tasks 均有 ac= + evidence= 绑定
- [x] package_maturity: filled
- [x] `beacon truth review` pass 后再 freeze

### Gap vs gold (订单支付示例)

- 对照：`docs/beacon/v1.6.13/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`
- 宿主 Agent 读 Humanizer vendor 全文润色 L0（无需 API key）

## Source Excerpt

```markdown
beacon-v1613-f4-plain-language-contract
源审计：docs/beacon/research/beacon-v1613-planning-source-audit-2026-08-27.md §3 F4
```
