---
name: beacon-planner-performance-review
description: Beacon v1.6.0 planner skill migrated from `beacon-performance-review`. Use when the user wants Beacon to challenge a feature, implementation, or route from a performance and scalability perspective before implementation, QA, or release continues.
---

# Beacon Planner Performance Review

## Overview

This is a support surface for performance-focused challenge.

It highlights hot paths, scaling pressure, unnecessary work, and latency-sensitive design choices before they are locked in as “good enough.” It is not a truth source and not a gate by itself.

## When to Use

- the feature touches hot paths, loop-heavy logic, I/O, or data scale
- implementation should be challenged for latency, throughput, or resource waste
- the user wants a performance-oriented review before `implement`, `qa`, or `release`
- the design looks correct functionally but may degrade under load

## Boundary

- not a truth source
- not a gate source
- not a new lifecycle stage
- does not rewrite frozen truth directly
- if accepted scope or non-functional acceptance must change, route to `beacon-change`

## Workflow / Decision Loop

- identify hot paths, repeated work, external I/O, and scaling assumptions
- challenge waste, hidden cost, and likely bottlenecks
- distinguish execution issues, architecture tradeoffs, and requirement-level SLA gaps
- route the result back to `beacon-change`, `beacon-implement`, `beacon-qa`, or `beacon-release`

## Common Rationalizations

- “先能跑起来，性能后面再说。” -> 不允许；高成本路径可能会反向锁死设计
- “性能只是实现细节，不需要说明假设。” -> 不允许；瓶颈和负载假设必须可解释
- “发现 SLA/规模问题，直接在这里当场改 acceptance。” -> 不允许；改 truth 要回主链

## Red Flags

- 性能结论没有 workload 或 hot-path 语义
- 明显高成本路径被包装成“以后再优化”
- 用 performance review 代替正式 QA 或 release gate

## Verification

- 输出能指出至少一个 hot path、waste source、latency risk 或 scale assumption
- 若问题影响 requirement promise，会显式 route back
- 若问题只是执行质量，会回 `implement` 或 `qa`

## Evidence Produced

- performance risk summary
- bottleneck / scaling notes
- route recommendation and impact framing

## State Updated

- none by default
- optional support/read model projection only

## Gate Impact

- no direct gate verdict
- can block blind continuation by exposing unresolved performance or scale risk

## Examples

- 适用例：
  - “这条功能会跑在高频路径上，我想先做一轮性能挑战。”
  - “功能对了，但我怀疑资源消耗和延迟会出问题。”
- 不适用例：
  - “我要正式确认 QA 通过。” -> 应去 `beacon-qa`
  - “我要正式修改冻结 truth。” -> 应去 `beacon-change`

## Cold-start anchors

- `performance-review` 不是为了追求极限优化，而是先找出不能忽略的成本。
- 它先校准负载与热点，再把问题送回主链处理。
- 发现性能风险后，要区分是 acceptance 问题还是实现问题。


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
- 来源迁移：`beacon-performance-review` -> `beacon-planner-performance-review`。
- 主要作用：性能风险挑战。
- 兼容说明：旧 skill 的专业正文、workflow、boundary、verification、evidence 和附属资产在本目录内保留；旧名称不再作为 host-visible skill 目录出现。


## 职责

- Harness：`planner`。
- 来源迁移：`beacon-performance-review` -> `beacon-planner-performance-review`。
- 主要作用：性能风险挑战。
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
