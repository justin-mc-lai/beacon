---
name: beacon-implement
description: Use when the user wants to plan or run implementation through Beacon's current v1.4.6 runtime surface. Keep `implement` as the only public implementation entrypoint; treat team runtime and subagent lanes as internal.
---

# Beacon Implement

## Overview

This skill routes execution work through Beacon's `implement` surface.

`implement` remains the only public implementation entrypoint. It consumes frozen requirement truth and execution governance context without rewriting those truths.

## When to Use

- implementation planning
- implementation execution
- implementation progress or handoff checks
- implementation readiness after freeze and technical review
- requirement completeness checks before execution

## Boundary

- `implement` is not permission to rewrite requirement truth
- it does not replace `change`
- team/runtime internals stay internal unless explicitly requested

## Workflow / Decision Loop

- enter only after requirement truth is frozen enough for execution
- block when truth must reopen, cutover guardrails fail, or conditionally required prototype is missing
- execute against the frozen package and current delivery governance
- hand off to `qa` once implementation evidence is ready

## Common Rationalizations

- “代码先做，后面再补 truth。” -> 不允许；truth 漂移要先回 `change`
- “只是顺手改旁边一点逻辑，不用看冻结范围。” -> 不允许；实现必须受冻结边界约束
- “prototype 还没补齐，但先写代码问题不大。” -> 不允许；真实 UX/UI handoff 不能跳过

## Red Flags

- requirement package 仍不稳定，却已经试图进入 execution
- 双读/兼容窗口存在，但准备忽略 fail-closed guardrail
- implementation progress 被当成 completion truth

## Verification

- execution 入口明确绑定 frozen `prd / user-story / test-case`
- blocked reason、gate context、branch/execution governance 可解释
- prototype 条件触发时，不会被静默跳过

## Evidence Produced

- implementation plan or execution summary
- implementation evidence and handoff context
- blocked reason or repair route when execution cannot start

## State Updated

- implementation progress state
- execution governance/read model state

## Gate Impact

- unlocks `qa` only when implementation evidence is sufficient
- blocks execution when truth drift, prototype gate, or delivery guardrails fail

## Inputs Contract

- `project-root`
- `version`
- `feature`
- frozen `prd / user-story / test-case`
- conditionally required `prototype` when the feature has real UX/UI handoff
- current gate / blocked reason / branch or execution governance context when present

## Decision Protocol

- Enter `implement` only after requirement truth is frozen enough for execution.
- Block when frozen truth requires `change`, when cutover guardrails fail, or when a conditionally triggered prototype is still missing.
- Keep `implement` as the only execution entry; `ask --execute` and support surfaces may route here but must not replace it.
- Prefer explanation and routing logic in skill surface; keep final schema, contract, and gate writes in Python guardrails.
- When dual-read or compatibility windows exist, fail closed on mismatch.

## Anti-Inertia Notes

- `implement` is not permission to rewrite requirement truth.
- `goal`, task ledgers, or partial execution progress do not define completion truth.
- If the feature needs UX/UI handoff and prototype is triggered, do not skip straight into coding.
- Team/runtime internals stay internal unless the user explicitly asks for them.
- `implement` cannot rewrite frozen truth or override gate truth by itself.

## Learning Notes

- Reuse implementation learning to avoid repeated blocked paths or flaky cutovers.
- Learning may shape route explanation and caution, but cannot override gate truth.
- Downgrade stale learning instead of silently trusting it.

## Backstop CLI

- `beacon implement ...`
- `beacon change ...` when truth must reopen
- `beacon qa ...` after implementation evidence is ready

## Examples

- 适用例：
  - “需求已经冻结，准备开始实现这条 feature。”
  - “我想确认这条 feature 现在能不能正式进入执行。”
  - “代码已经动了，想看 implementation handoff 或 readiness 有没有被阻断。”
- 不适用例：
  - “PRD 还没收口，scope 还在变。” -> 应先回 requirement surfaces
  - “我现在是在判断证据够不够 release。” -> 应优先去 `beacon-qa` 或 `beacon-release`

## Cold-start anchors

- `implement` 是执行入口，不是改 truth 的地方。
- 进入 `implement` 的前提是 requirement truth 已经足够稳定。
- 如果真实存在 UX/UI handoff，而 `prototype` 尚未补齐，不应直接跳过进入 coding。
