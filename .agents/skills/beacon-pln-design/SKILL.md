---
name: beacon-pln-design
description: Beacon v1.6.0 planner skill migrated from `beacon-design-review`. Use when the user wants Beacon-owned support-only UX review through the deterministic `beacon design route review` contract while preserving Beacon truth binding.
---

# Beacon Planner Design Review

## Overview

This is a host-visible child skill for the Beacon design `review` route.

It preserves the `impeccable` review capability while keeping review output as support evidence until accepted facts are bound back to Beacon truth.

## When to Use

- hierarchy review
- copy and flow friction review
- missing state review
- accessibility review
- UX finding prioritization

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- not a release verdict
- support-only design review
- does not replace `beacon-gen-design`
- does not replace `beacon-gen-prototype`
- does not treat `impeccable` output as Beacon truth

## Workflow / Decision Loop

- run or reason against `beacon design route review "<feature>" --project . --version auto --json`
- produce prioritized UX findings and candidate design truth deltas
- route accepted prototype input to `beacon prototype adapt`
- route promise-changing facts to `beacon change ... --refreeze-chain`
- hand off to `beacon implement` only after accepted facts are truth-bound

## Common Rationalizations

- “review output is accepted, so it is truth.” -> Not allowed; accepted facts still need Beacon truth binding.
- “Small UX findings do not need requirement routing.” -> Not allowed when they change product promise, behavior, AC, or QA coverage.
- “Review pass means release pass.” -> Not allowed; this is not a gate or release verdict.

## Red Flags

- review output copied into implementation without truth refs
- UX findings change acceptance behavior but skip change/refreeze
- review is treated as final UI authority

## Verification

- route payload reports `route=beacon-pln-design`, `intent=review`, and `upstream=impeccable`
- route payload marks `support_only=true`, `truth_source=false`, `gate_source=false`, and `lifecycle_stage=false`
- accepted design facts have a truth-binding route before implementation

## Evidence Produced

- route contract payload
- UX finding summary
- accepted design fact candidates
- route decision and writeback targets

## State Updated

- no lifecycle state directly
- optional support/read model evidence only

## Gate Impact

- no direct release gate verdict
- may block downstream implementation only when accepted design facts remain unbound

## Operator rule

Prefer:

```bash
beacon design route review "<feature>" --project . --version auto --json
```

If a design result is accepted:

```bash
beacon prototype adapt "<feature>" --project . --version auto --design-result-ref <accepted-design-result>
```

If design facts change product promise, behavior, AC, or QA coverage:

```bash
beacon change "<feature>" --project . --version auto --reason "accepted design truth changed requirement promise" --refreeze-chain
```

## Examples

- 适用例：
  - “这个界面做一次 UX review，看看层级、状态、文案和可访问性问题。”
  - “我想让 Beacon review UI，但不要把 review 直接当 truth。”
- 不适用例：
  - “我要正式生成 prototype bundle。” -> 应去 `beacon-gen-prototype`


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
- 来源迁移：`beacon-design-review` -> `beacon-pln-design`。
- 主要作用：UX 和设计方案挑战。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-design-review` -> `beacon-pln-design`。
- 主要作用：UX 和设计方案挑战。
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
