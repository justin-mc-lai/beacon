# PRD: beacon-goal-durable-supervisor-v167

## Problem

`$beacon-goal` 开 run 后，长程 implement/QA 依赖宿主会话；上下文满或 turn 结束时 run 仍 `running` 但无心跳，用户感知为「中断/死了」。

## Goals

1. opt-in supervisor 可持续巡检并派发工人
2. 2 分钟默认心跳 + 可审计 execution.jsonl
3. resume 只注入 checkpoint digest
4. 不削弱 verifier / human release / 单入口

## Non-goals

默认 daemon；zvec 核心依赖；自证 complete。

## Success metrics

- AC-DGS-001..014 contract tests green
- 合法 FSM 路径与非法转移有 TC
- 真实 run 在 host_interrupt 后可 resume-pack 恢复 next_action

## Requirements authority

`docs/beacon/v1.6.7/features/beacon-goal-durable-supervisor-v167/truth.md`
