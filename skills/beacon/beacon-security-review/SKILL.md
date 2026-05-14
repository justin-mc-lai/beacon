---
name: beacon-security-review
description: Use when the user wants Beacon to challenge a feature, implementation, or route from a security perspective before implementation, QA, or release continues.
---

# Beacon Security Review

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
- if accepted promise, scope, or acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify the real trust boundaries, inputs, outputs, and sensitive state
- challenge assumptions around auth, authz, validation, exposure, and data handling
- distinguish product bugs, security risks, and requirement-scope issues
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release`

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
  - “我要正式给 release 放行。” -> 应去 `beacon-release`
  - “我要正式重写冻结需求。” -> 应去 `beacon-change`

## Cold-start anchors

- `security-review` 的价值是让风险显形，不是把安全当成独立主流程。
- 它先 challenge 边界和暴露面，再把结论送回主链。
- 发现风险不等于直接改 truth；要看问题属于哪一层。
