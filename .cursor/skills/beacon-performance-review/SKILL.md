---
name: beacon-performance-review
description: Use when the user wants Beacon to challenge a feature, implementation, or route from a performance and scalability perspective before implementation, QA, or release continues.
---

# Beacon Performance Review

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
