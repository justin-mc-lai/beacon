---
name: beacon-planner-doubt-review
description: Beacon v1.6.0 planner skill migrated from `beacon-doubt-review`. Use when the user wants Beacon to challenge self-rationalized plans, surface evidence gaps, and apply doubt-driven review before implementation, QA, or release continues.
---

# Beacon Planner Doubt Review

## Overview

This is a support surface for adversarial doubt.

It is designed to challenge plans or conclusions that may already be self-consistent but not yet well-proven. It does not replace truth surfaces, QA, or release gates.

## When to Use

- a plan feels too smooth and may be self-rationalized
- the user wants explicit evidence-gap challenge before continuing
- implementation or review claims need a harder skeptical pass
- the next step is unclear because confidence is high but proof is thin

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen truth directly
- if accepted scope, promise, or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the strongest current claim and the weakest current proof
- search for contradictions, missing evidence, and false certainty
- separate supported conclusions from convenient narratives
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release` as appropriate

## Common Rationalizations

- “看起来能讲通，就不用继续质疑了。” -> 不允许；可讲通不等于已证实
- “doubt review 只是补充意见，不需要明确下一跳。” -> 不允许；挑战必须回路由
- “既然发现问题，就直接在这里改掉正式 truth。” -> 不允许；support 只 challenge，不直接写 truth

## Red Flags

- 输出只有态度，没有具体疑点或证据缺口
- 明明发现 drift，却没有 route back
- 用怀疑姿态代替正式 QA 或 release gate

## Verification

- challenge 输出至少指出 claim、evidence gap、risk 或 contradiction 之一
- 若问题影响冻结承诺面，会显式回 `beacon-change`
- 若问题只是执行或验证质量问题，会回 `beacon-implement` 或 `beacon-qa`

## Evidence Produced

- doubt register
- contradiction or gap summary
- route recommendation with confidence caveat

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can stop blind continuation by exposing weak proof or self-rationalized claims

## Examples

- 适用例：
  - “我怀疑这版方案已经开始自我合理化了，帮我做一轮逆向挑战。”
  - “实现看起来差不多，但我不信证据够，先做一轮 doubt review。”
- 不适用例：
  - “我要正式确认 release 放行。” -> 应去 `beacon-release`
  - “我要正式改冻结需求。” -> 应去 `beacon-change`

## Cold-start anchors

- `doubt-review` 的职责是拆穿自洽幻觉，不是制造额外流程。
- 它要把怀疑转成明确的 evidence gap 和下一跳。
- 发现问题后要回主链，不要把 support 面当终点。


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
- 来源迁移：`beacon-doubt-review` -> `beacon-planner-doubt-review`。
- 主要作用：假设和反例挑战。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-doubt-review` -> `beacon-planner-doubt-review`。
- 主要作用：假设和反例挑战。
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
