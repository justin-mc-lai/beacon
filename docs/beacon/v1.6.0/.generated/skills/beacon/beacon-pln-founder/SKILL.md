---
name: beacon-pln-founder
description: Beacon v1.6.0 planner skill migrated from `beacon-ceo-review`. Use when the user wants a founder/CEO-grade challenge on a Beacon version or major feature before requirement truth is revised or implementation continues.
---

# Beacon Planner Founder Review

## Overview

This is a host-visible support/review surface for version-level or major-feature challenge.

It challenges promise level, scope, framing, and buried downside risk, then routes accepted changes back into Beacon truth surfaces. It is not itself a truth or gate surface.

## When to Use

- problem reframing
- scope challenge
- expand / hold / reduce / reframe judgment
- version-level promise review before implementation
- when the current plan feels "too smooth" and you need explicit downside challenge
- when automation, support loops, or new execution ideas may destabilize truth freeze or stage boundaries

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not freeze truth directly
- does not replace `beacon-gen-change` or `beacon-gen-truth`
- does not turn CEO intuition into direct writeback without truth-surface recompilation

## Workflow / Decision Loop

- bind current review to the active requirement package
- challenge problem framing, promise size, scope direction, and hidden failure modes
- return `hold`, `expand`, `reduce`, or `reframe`
- if the outcome changes accepted promise or scope, route to `beacon-gen-change`
- if the outcome holds, route back to `beacon-gen-implement`

## Default Challenge Constitution

By default, `ceo-review` should assume the current story is incomplete unless disproven by evidence.

Its job is not to be politely aligned with the current plan.
Its job is to expose where the plan is over-smooth, under-priced, or likely to bend Beacon's core boundaries under real operating pressure.

Always challenge at least these lenses:

- `too_smooth_path`
  - what meaningful variance, dependency, operator behavior, or runtime mismatch is being ignored?
- `buried_landmine`
  - what failure mode is low-visibility now but expensive after rollout?
- `truth_freeze_destabilization`
  - does this idea let support surfaces, automation, or convenience loops silently rewrite or bypass frozen truth?
- `stage_boundary_sprawl`
  - does this proposal accidentally turn a support surface into a shadow lifecycle stage?
- `false_closure_signal`
  - are local pass signals being mistaken for requirement closure or release readiness?
- `operator_cost_underpricing`
  - does the proposal look elegant in principle but create hidden maintenance, triage, or governance burden?

Default stance:

> A strong CEO review should assume reality will introduce variance, hidden costs, and pressure on boundaries; if the proposal only works when the world stays orderly, the review is not finished.

## Common Rationalizations

- “CEO review 只是意见，不用绑定 requirement package。” -> 不允许；高风险挑战必须绑到 truth refs
- “结论已经很明确，可以直接当 freeze verdict。” -> 不允许；仍需回主链
- “只是版本级 review，不需要 evidence/state/gate 影响。” -> 不允许；挑战结果必须能投影回 route
- “当前方案已经很顺，只需要确认资源能不能做。” -> 不允许；先挑战为什么它会失控、偏航或被现实打断
- “support loop 只是提效，不会影响 truth freeze。” -> 不允许；凡是可能改变 route、acceptance 理解或 requirement meaning 的机制都必须被挑战
- “CEO 视角只看方向，不用看边界副作用。” -> 不允许；方向判断本身就必须包含 boundary pressure test

## Red Flags

- review 结果没有 truth refs
- 挑战结论停留在自由文本，没有下一跳
- 把 `ceo-review` 当成正式 change writeback surface
- review 只复述现有方案为什么合理，没有指出一个真实炸点
- 把“自动化能继续迭代”直接等同于“需求不会漂移”
- 把 `deep`、`ceo-review`、`brainstorm` 一类 support surface 描述成新的必经阶段
- 接受了 promise / scope / acceptance 变化，却仍然试图直接回 `implement`

## Verification

- 版本或 feature 级 challenge 明确绑定 requirement package
- `hold` 与 writeback 类 verdict 的 route 不混淆
- support-surface 结论能回到 `beacon-gen-change` 或 `beacon-gen-implement`
- 输出明确说明它挑战了哪些默认风险轴，而不是只给温和意见
- 如果发现 truth/boundary 风险，结论会把问题收敛成 `change/refreeze`，而不是口头提醒后继续推进

## Evidence Produced

- support-surface transaction
- truth refs and route decision
- operator-visible challenge summary

## State Updated

- support-surface transaction state
- latest advisory/review status projection

## Gate Impact

- no direct gate verdict
- can block blind continuation by routing accepted scope/promise changes back to `beacon-gen-change`
- should block "looks fine, keep going" inertia when boundary pressure or hidden downside has not been challenged

## Operator rule

Prefer:

```bash
beacon review ceo "<feature>" --project . --version auto --focus full --json
```

If the result is `hold`, return to `beacon-gen-implement`.
If the result is `expand`, `reduce`, or `reframe`, route to `beacon change run ...`.

Interpretation rule:

- `hold` only means the accepted promise, scope, and acceptance assumptions remain intact after challenge
- if challenge discovers requirement-meaning pressure, route to `beacon-gen-change` even when implementation mechanics still look plausible

## Examples

- 适用例：
  - “这个版本承诺是不是太大了，需要先从 CEO/产品视角挑战一下范围和 promise。”
  - “我不确定该扩、该收，还是该重构问题定义。”
  - “这条 automation 线看起来很顺，但我怀疑会把 truth freeze 带歪，先挑战下埋雷。”
  - “开发思路过于线性，现实里变数很多，帮我从 CEO 视角找会炸掉的地方。”
- 不适用例：
  - “我已经确定要正式修改冻结 truth。” -> 应去 `beacon-gen-change`


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
- 来源迁移：`beacon-ceo-review` -> `beacon-pln-founder`。
- 主要作用：创始人和商业视角挑战。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-ceo-review` -> `beacon-pln-founder`。
- 主要作用：创始人和商业视角挑战。
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
