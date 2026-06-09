---
name: beacon-pln-context
description: Beacon v1.6.0 planner skill migrated from `beacon-context-engineering`. Use when the user needs Beacon to strengthen execution or review by restructuring context, extracting the minimum working truth, and reducing context drift without rewriting canonical requirement truth.
---

# Beacon Planner Context Engineering

## Overview

This is a support surface for context shaping.

Its job is to improve how work is framed and consumed before or during implementation, QA, or review. It is not a truth source, not a gate source, and not a new lifecycle stage.

## When to Use

- implementation context feels bloated, noisy, or contradictory
- frozen truth exists but the working set is unclear
- too many irrelevant artifacts are competing for attention
- the user needs a smaller, clearer execution context before `beacon-gen-implement` or `beacon-eval-qa`

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen `prd`, `user-story`, `test-case`, or `.machine/`
- if accepted scope or acceptance must change, route to `beacon-gen-change`

## Workflow / Decision Loop

- identify the smallest working context that still preserves frozen truth
- separate canonical truth, active evidence, and low-value noise
- propose the minimum context pack needed for the next mainline surface
- if context confusion hides a real truth gap, route back to `beacon-gen-change`, `beacon-gen-truth`, or `beacon-gen-truth`

## Common Rationalizations

- “上下文乱一点没关系，模型自己会补。” -> 不允许；噪声会降低决策质量
- “把 context engineering 的结论直接当 requirement 改掉。” -> 不允许；它只整理上下文，不写 truth
- “只是做上下文收缩，不需要说明保留了哪些 truth。” -> 不允许；working set 必须可解释

## Red Flags

- working context 丢掉了仍然有效的 frozen truth
- context 收缩后，执行面不知道 acceptance 从哪来
- support 输出停留在泛泛建议，没有明确下一跳

## Verification

- working context 能明确说明保留了哪些 canonical truth 和 active evidence
- 缩减后的上下文更利于后续 `implement`、`qa` 或 `review`
- 如果识别到 truth gap，会显式 route back，而不是假装可以直接继续

## Evidence Produced

- context pack recommendation
- keep / discard rationale
- next-surface recommendation

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- may block premature execution by exposing unresolved truth drift or missing evidence anchors

## Examples

- 适用例：
  - “材料很多，但真正和这轮实现有关的上下文不清楚，先帮我收缩 working set。”
  - “我不想改需求，只想把执行前必须记住的 truth、evidence、风险边界理顺。”
- 不适用例：
  - “我要正式改冻结 scope。” -> 应去 `beacon-gen-change`
  - “我现在要代码实现或正式验收。” -> 应去 `beacon-gen-implement` 或 `beacon-eval-qa`

## Cold-start anchors

- `context-engineering` 解决的是上下文质量，不是 truth 写回。
- 它的价值是缩短有效 working set，而不是制造新的文档层。
- 如果整理上下文时发现正式承诺面要改，必须回主链。


## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。

HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。

## v1.6.0 Harness Migration

- Harness：`planner`。
- 来源迁移：`beacon-context-engineering` -> `beacon-pln-context`。
- 主要作用：上下文重塑与路由建议。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-context-engineering` -> `beacon-pln-context`。
- 主要作用：上下文重塑与路由建议。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
