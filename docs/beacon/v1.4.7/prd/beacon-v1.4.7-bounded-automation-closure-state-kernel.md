# PRD: Beacon v1.4.7 bounded automation closure-state kernel

**Feature**: `beacon-v1.4.7-bounded-automation-closure-state-kernel`  
**Version**: `v1.4.7`  
**Date**: `2026-05-15`  
**Status**: `freeze-ready`  
**Track**: `automation-runtime-kernel + bounded-repair-loop + queue-safety`  
**Scenario**: `scheduled_qa_and_implement_repair_need_a_truth-preserving_runtime_contract`

## Context

- Global boundaries:
  - `docs/beacon/global-boundaries.md`
- Current runtime baseline:
  - `docs/beacon/v1.4.6/SUMMARY.md`
  - `docs/beacon/v1.4.6/prd/beacon-v1.4.6-automation-jobs-feedback-loop-and-queue-governance.md`
- Current automation runtime surfaces:
  - `beacon/commands/automation.py`
  - `beacon/utils/automation_feedback.py`
  - `beacon/utils/automation_queue.py`
- Research closure:
  - `docs/beacon/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`
  - especially `11.1 Already Implemented Automation Contract`
  - `11.2 Missing Runtime Contract`
  - `11.3 Smallest Next Implementation Slice`
  - `11.4 CEO Feasibility Verdict`
- Version truth:
  - `beacon/version-truth.json`
  - current runtime release line remains `v1.4.6`
  - `v1.4.7` remains a planning line and must not be framed as shipped runtime behavior

## 1. Overview

Beacon `v1.4.6` already froze a real project-local automation toolkit:

- queue validation
- QA feedback ledger generation
- queue update from QA feedback
- scaffold generation
- shared automation summary

But that surface is still a toolkit contract, not a closure-state runtime.

The next `v1.4.7` automation requirement should therefore stay narrow:

> introduce the minimum runtime kernel that lets automation route repeated QA and implement repair safely, without granting automation authority to move truth or autonomously run the full lifecycle.

This PRD does **not** stand up the full Automation Closure-Loop vision.

It freezes only the bounded kernel needed to move Beacon from:

- QA feedback helper

to:

- bounded, truth-preserving QA/implement repair-loop runtime

## 2. 问题

### 2.1 现有 automation 已经不是样例，但还不是 runtime

Beacon 当前 automation 已具备：

- public CLI entrypoints
- canonical queue contract
- canonical QA feedback ledger
- queue-governed QA/implement candidate movement

但缺少正式 runtime contract 去回答：

- 当前 feature automation 处于什么 closure state
- 下一跳该去 `qa`、`implement`、`release` 还是 `human`
- 这是不是第 N 轮修复
- 当前轮继承了哪些仍然有效的问题
- 两个 scheduler 同时写 queue 时谁应该失败

结果是：

- 系统可以调度和汇总
- 但不能把 repeated QA/repair 解释成一个可审计、可收敛的 runtime object

### 2.2 如果现在直接承诺完整 Automation Closure-Loop，会引爆 Beacon 的边界

研究和 CEO review 已经把风险收得很明确：

- automation 不能自动拥有“继续追真相”的主权
- support automation 不能长成 shadow lifecycle
- 局部 QA 绿灯不能被误读成 requirement closure
- 没有 queue revision / lease / stale-writer rejection 时，真实 scheduler 环境一定会出现 forked state

因此 Beacon 现在的真实问题不是“有没有 automation 命令”，而是：

> 缺少一个足够小、足够硬的 runtime kernel，让 automation 能安全推进 repair-loop，同时不穿透 truth freeze 和 stage boundaries。

### 2.3 真实项目需要的是 bounded repair loop，不是夜间无限自演化

真实项目中更高频、更高价值的场景是：

```text
QA 发现问题
-> 形成 repair-needed runtime intent
-> implement 做一轮修复
-> 带着上一轮 active issues 回到 QA
-> 判断是否 release-ready、继续 repair、还是升级到 human
```

而不是：

```text
QA
-> implement
-> QA
-> deep
-> refreeze
-> implement
-> QA
-> release
```

后一条是长期研究方向，不应作为当前版本实现承诺。

## 3. 目标

1. 为 Beacon automation 引入最小 closure-state runtime envelope
2. 让 repeated QA/implement repair round 成为正式、可继承、可审计的 runtime contract
3. 为 queue 写入补上最小安全原语，避免 scheduler 并发把 state 写叉
4. 保持 automation 仍是 host-scheduled support plane，不扩张成新的 lifecycle stage
5. 明确冻结这条线的近线边界：只做 bounded kernel，不做 full autonomous closure-loop

## Scope

### In scope

- closure-state envelope
- active issue register
- authoritative QA exit predicates
- implement re-entry contract
- queue revision / feature execution lease / stale-writer rejection
- operator-visible runtime explanation for current round, next route, and stop signal

### Out of scope

- automatic `deep` routing as an always-on continuation engine
- automatic `change/refreeze` routing execution
- automatic truth recompilation after refreeze
- automatic scenario promotion into canonical requirement materials
- automatic release orchestration
- any runtime behavior that lets automation silently move requirement truth

## 4. 设计原则

### 4.1 这是 bounded runtime kernel，不是 full autonomous loop

当前 slice 只解决：

- QA/implement repeated repair routing
- closure-state expression
- queue safety

不解决：

- full lifecycle autonomy
- truth-evolving autonomy
- night-long unattended closure ownership

### 4.2 Automation 可以推进 repair work，不能推进 truth ownership

automation 可以：

- 记录 closure state
- 记录 round inheritance
- 建议下一跳
- 把 release-ready / repair-needed / human-escalation 机器化表达出来

automation 不能：

- 自动重写 PRD / user-story / test-case
- 在 requirement meaning 变化时继续推进实现
- 把 support discovery 直接写成 canonical truth

### 4.3 先分离 state / route / signal，再谈更深自动化

这个 kernel 必须显式拆分：

- `closure_state`
- `next_route`
- `terminal_signal`

而不是继续把这些语义隐含在松散的 queue 更新和 freeform summary 中。

### 4.4 多轮 repair 必须继承 active issue register，而不是继承整包历史 artifact

否则 repeated round 会快速变成：

- context blow-up
- stale evidence inheritance
- explainability 下降
- 收敛速度变差

### 4.5 并发安全必须先于 ambition

任何 serious timed automation rollout，在真实 host scheduler 下都会遭遇：

- 重复触发
- 晚到写入
- stale queue mutation
- 两个 worker 抢同一 feature

所以：

> 没有 queue safety primitives，就不应承诺更强的 automation autonomy。

### 4.6 终止信号必须比“继续优化”更强

每轮自动化都必须优先回答：

- 为什么停在这里
- 下一跳是谁
- 什么时候必须交还给人

而不是默认“还能继续跑就继续跑”。

## 5. 范围

### In scope

- QA round emits closure-state envelope
- implement round consumes and updates active issue register
- queue state gains revision and feature lease semantics
- automation runtime can distinguish:
  - `release_ready`
  - `repair_needed`
  - `human_escalation_required`
- release may consume a converged release-ready signal, but automation does not execute release

### Out of scope

- support-review executor admission
- `deep` routing contract
- `truth_recompiled_pending` execution path
- scenario discovery taxonomy writeback
- release-stage automation loop

## 6. 功能需求

### FR-001 Beacon 必须冻结 closure-state envelope

Beacon automation 必须为 feature 级 repeated repair work 输出 machine-readable closure-state envelope。

至少包含：

- `feature`
- `version`
- `closure_state`
- `next_route`
- `terminal_signal`
- `round_number`
- `previous_round_ref`
- `truth_hash` 或等价 truth revision binding
- `implementation_evidence_hash` 或等价 execution evidence binding

### FR-002 Beacon 必须冻结 bounded closure-state taxonomy

当前 slice 至少必须冻结以下 closure state：

- `active`
- `blocked`
- `release_ready`
- `closed`
- `human_escalation_required`

并至少冻结以下 next route：

- `qa`
- `implement`
- `release`
- `human`

该 slice 不要求把 `support_review` / `change_refreeze` 作为可执行自动路由接入 runtime。

### FR-003 Beacon 必须为 repeated repair round 冻结 active issue register

每一轮 automation repair 都必须继承 machine-readable active issue register，而不是整包复制上一轮全部 artifact。

至少包含：

- unresolved stop reasons
- accepted fixes
- targeted rerun hints still in force
- latest implement outcome ref
- current closure-state ref
- previous round summary ref

### FR-004 Beacon 必须冻结 authoritative QA exit predicates

QA surface 至少必须能正式写出以下 exit intent：

- `qa_exit_ready_for_release`
- `qa_route_implement_repair`
- `qa_route_human_escalation`

并将其稳定投影到 closure-state envelope，而不是只散落在 freeform summary 中。

### FR-005 Beacon 必须冻结 implement re-entry contract

Implement repair 至少必须能正式写出以下 exit intent：

- `implement_exit_to_qa`
- `implement_route_human_escalation`

该 contract 必须把新的 implement 结果回写到当前 feature 的 bounded repair runtime object。

### FR-006 Beacon 必须引入 queue revision contract

automation queue 写入必须带有 queue revision，并在写入时校验当前 revision 是否仍然匹配。

如果 revision 已变化，stale writer 必须被拒绝，而不是静默覆盖较新的 queue state。

### FR-007 Beacon 必须引入 feature execution lease

同一时间同一 feature 只能有一个 active automation execution lease。

至少需要支持：

- lease claim
- lease ownership visibility
- second claimant rejection
- expired or released lease recovery semantics

### FR-008 Beacon 必须拒绝 stale writer 和 double-flight

当前 slice 必须正式防止：

- stale queue writer 覆盖新状态
- 两个 scheduler 同时 claim 同一 feature
- 同一轮 runtime summary 被重复当成下一轮 authoritative input

### FR-009 Beacon 必须保留 operator-visible round explanation

每轮 bounded repair runtime 至少必须对人类可见：

- 当前 round number
- 当前 closure state
- 当前 terminal signal
- 下一跳
- 是否需要人工接管

这层输出可以是 summary/ledger/projection，但不能只存在于隐式 machine state。

### FR-010 Beacon 必须显式保持 truth boundary

当前 slice 中，automation runtime 不得：

- 自动进入 `change/refreeze`
- 自动推广 scenario discovery 为 canonical truth
- 自动把 local pass signal 等同于 release closure

一旦检测到 requirement meaning pressure，runtime 必须停在 fail-closed 边界，而不是继续推进实现。

## 7. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | Beacon 为 QA/implement repeated repair work 定义了 machine-readable closure-state envelope |
| AC-002 | Beacon 为 repeated repair round 定义了 active issue register inheritance contract |
| AC-003 | QA 能稳定写出 `ready_for_release` / `implement_repair` / `human_escalation` 三类 authoritative exit intent |
| AC-004 | Implement repair 能稳定写出回到 QA 或升级人工的 exit intent |
| AC-005 | Queue writes 具备 revision 校验，stale writer 会被拒绝 |
| AC-006 | 同一 feature 不能被两个 automation worker 同时 claim |
| AC-007 | bounded runtime 仍保持 support-plane 身份，不扩张成新的 lifecycle stage |
| AC-008 | automation runtime 不具备 truth-moving authority，也不宣传 full autonomous closure-loop |

## 8. Freeze Decision

`v1.4.7` 在 automation 方向上当前只冻结这一条近线实现承诺：

> closure-state envelope + active issue register + authoritative QA/implement bounded repair loop + queue safety primitives

明确不在本轮冻结中的方向：

- automatic `deep` continuation
- automatic refreeze routing
- truth recompilation runtime
- scenario promotion pipeline
- release-stage automation orchestration

这不是保守写法，而是刻意保护 Beacon 的边界模型。

## 9. 下一步

This PRD should route to:

- `user-story` for bounded runtime actors, round semantics, and queue-safety stories
- `test-case` for closure-state, round inheritance, stale-writer rejection, and single-flight validation

Do not route this PRD directly into implementation as if it were the full Automation Closure-Loop promise.
