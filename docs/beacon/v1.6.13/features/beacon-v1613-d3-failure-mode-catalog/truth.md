---
slug: beacon-v1613-d3-failure-mode-catalog
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
  prd: docs/beacon/v1.6.13/features/beacon-v1613-d3-failure-mode-catalog/truth.md
  user_story: docs/beacon/v1.6.13/features/beacon-v1613-d3-failure-mode-catalog/truth.md
  test_case: docs/beacon/v1.6.13/features/beacon-v1613-d3-failure-mode-catalog/tests.md
---

# Requirement Truth: beacon-v1613-d3-failure-mode-catalog (v1.6.13)

## 人话

建一本**"常见犯错手册"**。

agent 干活时会反复犯几种错：比如**不读代码就猜**、**宣称完成但没有任何可验证产出**、**漏看某处改动**。这本手册把已知的错一一记下来，每条配一个"怎么测出来"的检查方法。

交付前（QA 环节）自动翻这本手册，拿里面的检查过一遍——以前犯过的错，一眼就能抓出来。

注意：手册只负责"发现问题、提醒你"，**不自动判合格**——最后判断权在人手里。

- 能做：建失败模式目录（每条：什么错、什么症状、怎么判定、对应哪条检查用例）；检查用例能独立跑；QA 前自动引用
- 不能做：不让手册自动判定"通过/不通过"（那是人说了算）；不把手册当新增验收门禁
- 怎样算完：目录建好、每条有 rubric 和可执行检查、QA/release 前的对抗式审查会读它

## User Intent

把 beacon 的 QA/release 对抗式审查从"临时列翻车点"升级为"机制化的失败模式回归库"：目录 + rubric + 可执行用例，作为对抗式审查的固定输入。

## User Intent Snapshot

```yaml
lake_or_ocean: 湖
truth_review_gate: required
fill_depth: filled
intent_source: beacon-v1613-planning-source-audit-2026-08-27 D3
mirror_anchors: bmad claims-check + ECC eval-harness/agent-eval/council-multi-model
```

## Intent Coverage Matrix

| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-001 | D3：失败模式目录 | must | AC-001 | covered |
| INT-002 | 每条带 rubric（判定标准） | must | AC-002 | covered |
| INT-003 | 用例可独立执行 | must | AC-003 | covered |
| INT-004 | 对抗式审查 gate 消费目录 | must | AC-004 | covered |
| INT-005 | 手册不自动判 pass（人裁决） | must | AC-005 | covered |

## 用户旅程

1. 触发：QA / release 前的对抗式审查
2. 关键操作：审查先翻失败模式手册，抽取 3-5 个翻车点逐条验证
3. 结果：发现的翻车点有验证证据；手册外的新失败模式可回填目录
4. 异常：手册缺失 → 审查仍进行但提示"未引用失败模式目录"（advisory）

## First principles

- 系统边界：手册是对抗式审查的输入，不是新的 gate verdict
- 不可变：批判式意见不得自动判 pass（对齐 mirror：user decides）
- 可推翻假设：跨模型打分是意见而非分数；若未来需要自动打分须另行冻结

## Domain Model

| Entity | Key fields | Notes |
|--------|------------|-------|
| FailureMode | id, symptom, judgment_rule, linked_skill_case | 目录条目 |
| SkillCase | rubric, exec_command, assertion | 可执行用例 |
| AdversarialReview | mode, findings, evidence | 消费目录的审查 |

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | 建立失败模式目录 `beacon-qa/references/failure-mode-catalog.md`，每条含 模式/症状/判定规则/对应 skill 用例，首版 ≥ 5 条（含"猜代码漏读""只有文档没有可验证产出""软断言 TC"等已知模式）——触发 `build_catalog` 进入 filled 状态。 |
| AC-002 | filled 状态要求：每个用例含 rubric（coordinator 判定标准：什么证据算通过、什么算拦截）。 |
| AC-003 | filled 状态要求：用例可独立执行（命令 + 断言），且能在 CI/本地跑出确定结果。 |
| AC-004 | `wire_gate` 触发：QA/release 前的对抗式审查固定引用目录（从目录抽取 3-5 个翻车点），引用缺失时输出 advisory 提示——进入 wired 状态。 |
| AC-005 | `user_decides` 要求：手册输出为批判式意见（findings/evidence），不自动判 pass；最终 verdict 由人/既有 gate 决定——进入 closed 状态。 |

## Domain FSM Order

| State | From | Guard |
|-------|------|-------|
| filled | scaffold | ≥5_modes |
| wired | filled | review_refs_catalog |
| closed | wired | user_decides |

## Illegal transitions

- 目录自动判 pass（越权裁决）
- 对抗式审查未引用目录仍声称"已对抗"（advisory 缺失）

## FSM 五元组

> domain_required=false（skill/资产层湖），元状态即可。

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | build_catalog | ≥5_modes | filled | — |
| filled | wire_gate | review_refs_catalog | wired | — |
| wired | review | user_decides | closed | record_findings |

**终态：** wired（可被审查消费）

### invalid / illegal

- 目录自动判 pass（illegal：越权裁决）
- 对抗式审查未引用目录仍声称"已对抗"（illegal：advisory 缺失）

## Non-goals

- 不做自动打分器（跨模型打分仅批判式意见）
- 不把手册变成硬 gate
- 不重写既有 evals（在 `beacon-qa/evals/` 基础上扩展）

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

- 对照：`docs/beacon/v1.6.13/features/truth-gold-order-pay-v1610/truth.md`
- 对照：`skills/beacon/beacon-truth/references/examples/gold-order-pay-package.md`

## Source Excerpt

```markdown
beacon-v1613-d3-failure-mode-catalog
源审计：docs/beacon/research/beacon-v1613-planning-source-audit-2026-08-27.md §2 D3
Mirror 锚定：bmad src/bmm-skills/ship/bmad-build/references/claims-check.md（claims falsify）；ECC skills/eval-harness/SKILL.md（pass@k）；council-multi-model/SKILL.md（user decides）
```
