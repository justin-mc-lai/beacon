---
name: beacon-pln-security
description: Beacon v1.6.0 planner skill migrated from `beacon-security-review`. Use when the user wants Beacon to challenge a feature, implementation, or route from a security perspective before implementation, QA, or release continues.
---

# Beacon Planner Security Review

## Overview

This is a support surface for security-focused challenge.

It highlights exposure, trust-boundary, auth, input, and data-handling risks before they are mistaken for implementation detail or release trivia. It is not a truth source and not a release gate by itself.

## When to Use

- auth, permission, or trust-boundary risk exists
- external input or data exposure needs scrutiny
- the user wants a security-oriented challenge before `implement`, `qa`, or `release`
- a feature looks functionally complete but may still be unsafe

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen requirement truth
- if accepted promise, scope, or acceptance must change, route to `beacon-gen-change`

## Workflow / Decision Loop

- identify the real trust boundaries, inputs, outputs, and sensitive state
- challenge assumptions around auth, authz, validation, exposure, and data handling
- distinguish product bugs, security risks, and requirement-scope issues
- route the result back to `beacon-gen-change`, `beacon-gen-implement`, `beacon-eval-qa`, or `beacon-eval-release`

## Common Rationalizations

- “功能没问题，安全细节后面再说。” -> 不允许；安全风险不是装饰层
- “security review 发现问题，直接在这里改 acceptance 就行。” -> 不允许；改 truth 要回主链
- “没有明显攻击面，所以不用说明边界。” -> 不允许；trust boundary 必须显式

## Red Flags

- 权限、输入或数据暴露边界未被说明
- challenge 输出没有回路由
- 把 security review 当成正式 release gate verdict

## Verification

- 输出能指出至少一个 trust boundary、exposure surface、validation risk 或 permission risk
- 若问题影响承诺面或 acceptance，会显式 route back
- 若问题属于实现或验证质量，会回 `implement`、`qa` 或 `release`

## Evidence Produced

- security risk summary
- exposure / trust-boundary notes
- route recommendation and severity framing

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can block blind continuation by surfacing unresolved security risk or missing validation evidence

## Examples

- 适用例：
  - “这条功能涉及权限和外部输入，我想先做一轮安全挑战。”
  - “实现差不多了，但我不确定有没有暴露面或信任边界漏洞。”
- 不适用例：
  - “我要正式给 release 放行。” -> 应去 `beacon-eval-release`
  - “我要正式重写冻结需求。” -> 应去 `beacon-gen-change`

## Cold-start anchors

- `security-review` 的价值是让风险显形，不是把安全当成独立主流程。
- 它先 challenge 边界和暴露面，再把结论送回主链。
- 发现风险不等于直接改 truth；要看问题属于哪一层。


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
- 来源迁移：`beacon-security-review` -> `beacon-pln-security`。
- 主要作用：安全风险挑战。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-security-review` -> `beacon-pln-security`。
- 主要作用：安全风险挑战。
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
