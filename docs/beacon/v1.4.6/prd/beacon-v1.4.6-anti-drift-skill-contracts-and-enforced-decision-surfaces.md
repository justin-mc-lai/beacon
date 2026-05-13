# PRD: Beacon v1.4.6 anti-drift skill contracts and enforced decision surfaces

**Feature**: `beacon-v1.4.6-anti-drift-skill-contracts-and-enforced-decision-surfaces`  
**Version**: `v1.4.6`  
**Date**: `2026-05-13`  
**Status**: `freeze-ready`  
**Track**: `skill-governance + anti-drift-enforcement`  
**Scenario**: `philosophy-contracts-connected-to-state-evidence-and-gate`

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Brainstorm closure:
  - `docs/brainstorms/2026-05-13-beacon-brainstorm-beacon-v1.4.6-evolution-brainstorm-absorb-addyosmani-agent-skills-engineering-ph.md`
- Relevant current surfaces:
  - `skills/beacon/using-beacon/SKILL.md`
  - `skills/beacon/beacon-brainstorm/SKILL.md`
  - `skills/beacon/beacon-change/SKILL.md`
  - `skills/beacon/beacon-implement/SKILL.md`
  - `skills/beacon/beacon-qa/SKILL.md`
  - `skills/beacon/beacon-release/SKILL.md`
- External reference input:
  - `oss-sync/agents/agent-skills/addyosmani-agent-skills`
- Product tension:
  - Beacon already has stronger truth, evidence, gate, and transaction governance than most skill packs.
  - Beacon still needs sharper host-visible behavior contracts so the public surfaces drift less before machine governance catches them.

## Overview

Beacon v1.4.6 should freeze a stronger anti-drift skill contract layer.

The goal is not to copy external skill packs or reduce Beacon into a prompt library. The goal is to absorb the strongest parts of modern workflow-skill design:

- skill as executable contract
- explicit anti-rationalization
- explicit orchestration boundaries
- adversarial decision challenge for high-risk claims

and connect them to Beacon's existing strengths:

- canonical truth
- evidence contracts
- state projection
- gate enforcement
- transaction consistency

The result should be a Beacon line where host-visible skills are harder to misuse, support surfaces are harder to overreach, and the path from judgment to evidence to gate becomes more checkable.

## 1. 问题

### 1.1 Beacon 的治理骨架已经很强，但部分 public skill contract 仍然不够锋利

Beacon 当前已经具备：

- 主链 truth 治理
- requirement traceability
- machine projection
- gate / fail-closed 面
- transaction 和 drift 检查

但在 public human-facing surfaces 上，仍存在这些问题：

- 某些 skill 更像 capability description，而不是执行合同
- 模型最常见的漂移借口没有被显式建模
- support surface 的 explain / challenge / route 边界虽已存在，但还未统一提升为更强的 contract anatomy
- judgment 与 evidence / state / gate 的衔接，在 skill 层还不够显式

这会导致 Beacon 在强模型条件下出现一种结构性风险：

- 机器层最终仍能做较强治理
- 但用户先接触到的 public surface，仍可能在 framing、route、scope、verification 上先发生漂移

### 1.2 Beacon 需要的是“更强的前端行为约束”，不是退回逐步脚本化

Beacon 不能因为要减少漂移，就把全部 skill 写成僵硬 how-to 剧本。

那会破坏 Beacon 已冻结的 skill 哲学边界：

- 先定义决策边界
- 再暴露最小完备工具
- 最后补足容易遗忘但必须成立的事实

因此 v1.4.6 要解决的不是“让 skill 更长”，而是：

- 让 contract 更清楚
- 让借口更难成立
- 让 route 和 verdict 更可回溯
- 让 public surface 和 machine governance 更紧耦合

### 1.3 外部参考仓库证明了“workflow contract + anti-rationalization”对减漂移有效，但 Beacon 还没有完全把这层吸收到自身系统

参考仓库 `addyosmani/agent-skills` 的强项不是 runtime，而是：

- skills are workflows, not reference docs
- route by task/decision surface
- common rationalizations as first-class failure mode
- persona/orchestrator boundary clarity
- explicit verification exits

Beacon 不应把它当成新的 runtime dependency。

Beacon 应吸收的是：

- 其工程思想
- 其 contract anatomy
- 其反漂移设计方法

并把这些方法接入 Beacon 自己的 truth / evidence / state / gate 系统。

## 2. 目标

1. 冻结 Beacon v1.4.6 的 anti-drift skill contract baseline
2. 让关键 host-visible surfaces 统一采用更强的 contract anatomy
3. 把 anti-rationalization 提升为 Beacon 一等设计原则
4. 冻结 high-risk decision challenge 的正式边界与输出合同
5. 冻结 Beacon surface family 的 orchestration constitution
6. 把 prompt-level contract 部分提升为 machine-checkable enforcement

## 3. 非目标

- 不把 Beacon 改造成纯 skills 仓库
- 不把外部 skill pack 升级为 Beacon 默认运行前提
- 不新增新的公开主生命周期 stage
- 不让 `brainstorm`、`deep`、`ceo-review`、`design-review` 变成 truth source 或 gate source
- 不为了反漂移而把全部 skill 降级成逐步操作剧本

## 4. 设计原则

### 4.1 Skill 必须是 executable contract，不只是 capability description

一个合格的 Beacon public skill，必须至少能说明：

- 什么时候该用
- 什么情况下不该用
- 这轮判断/动作的边界是什么
- 常见漂移借口是什么
- 完成时必须留下什么验证或证据

### 4.2 Anti-rationalization 必须是一等设计原则

Beacon 必须主动建模强模型最常见的失败模式，例如：

- “先做实现，之后再补 truth”
- “这次改动很小，不用补 evidence”
- “brainstorm 已经够清楚，可以直接当正式承诺”
- “learning hint 已经足够，不必回 requirement truth”
- “为了省事，顺手把相邻模块一起改了”

如果这些借口不被写入 contract，漂移就会在 public surface 先发生，再由 machine governance 被动兜底。

### 4.3 Support surface 的价值是 challenge / explain / route，不是偷渡 verdict

`brainstorm`、`deep`、`ceo-review`、`design-review`、`help`、`status`、`doctor` 仍然必须遵守：

- not truth source
- not gate source
- not new lifecycle stage

v1.4.6 需要做的是把这个边界写得更硬、更一致、更可检查。

### 4.4 High-risk judgment 必须允许 adversarial challenge，但 challenge 结果不能脱离 Beacon 的 evidence/state/gate 面

高风险判断不能只靠“模型有信心”。

当涉及：

- public promise
- release verdict
- acceptance closure
- cross-surface consistency
- irreversible decisions

时，Beacon 必须允许显式 challenge。

但 challenge 的产物不能只是自由文本，它必须能投影回：

- evidence
- state
- route
- gate impact

### 4.5 Beacon 吸收外部思想时，必须吸收 contract，而不是外部依赖

Beacon 可以借鉴外部开源的：

- skill anatomy
- routing philosophy
- anti-rationalization pattern
- orchestration boundary pattern

但不得把外部仓库变成 Beacon 的默认前提或强依赖。

## 5. 范围

### In scope

- Beacon public skill contract baseline for v1.4.6
- anti-rationalization contract for key surfaces
- decision-challenge surface contract
- orchestration constitution for public/support/truth/gate surfaces
- machine-checkable lint/check design for anti-drift enforcement

### Out of scope

- 大规模重写全部历史版本 skill
- 任意引入外部 skill pack 作为默认运行资源
- 直接重构整个 CLI catalog
- 一次性重写所有 user-story / test-case / QA assets

## 6. 功能需求

### FR-001 Beacon 必须冻结 `Skill Anatomy v2`

Beacon 必须为关键 host-visible skills 冻结统一 contract anatomy。

该 anatomy 至少包括：

- Overview
- When to Use
- Boundary
- Workflow / Decision Loop
- Common Rationalizations
- Red Flags
- Verification
- Evidence Produced
- State Updated
- Gate Impact

### FR-002 Beacon 必须把 anti-rationalization 提升为关键 skill 的强制内容

至少以下 surfaces 必须具备显式 anti-rationalization section：

- `using-beacon`
- `beacon-prd`
- `beacon-change`
- `beacon-brainstorm`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`

### FR-003 Beacon 必须冻结 support surface 的统一 contract boundary

Beacon 必须让 guidance/support family 统一表达：

- not truth source
- not gate source
- not new lifecycle stage
- must route back to canonical truth or delivery surfaces

并且该边界不能只散落在 docs 中，而要进入 host-visible contract。

### FR-004 Beacon 必须引入受治理的 high-risk decision challenge contract

Beacon 必须正式定义一个 high-risk challenge capability，用于：

- challenge non-trivial claims
- expose contradictory evidence
- force explicit reconcile

它的最小输出合同至少包括：

- claim
- artifact under challenge
- contract / expected boundary
- findings
- reconcile result
- stop condition
- route outcome

### FR-005 Beacon 必须把 decision challenge 与 evidence/state/gate 面连接起来

当 challenge 发生时，Beacon 必须能表达：

- 产生了哪些 evidence
- 更新了哪些 state
- 对哪些 gate 或 route 有影响

challenge 不得停留在孤立 markdown 结论层。

### FR-006 Beacon 必须冻结 orchestration constitution

Beacon 必须正式说明：

- 哪些 surface 是 truth surfaces
- 哪些 surface 是 support/guidance surfaces
- 哪些 surface 是 execution surfaces
- 哪些 surface 是 gate surfaces
- 哪些能力只能由 main session / main router 调用
- 哪些能力只能做 explain / diagnose / challenge，不能 give verdict

### FR-007 Beacon 必须把关键 anti-drift contract 提升为 machine-checkable checks

Beacon 至少需要设计并支持以下 checks：

- skill anatomy lint
- anti-rationalization coverage check
- evidence contract check
- state/gate trace check

### FR-008 Beacon 必须保持 philosophy-first，而不是滑向 script-first

即使 skill contract 更强，Beacon 也必须保持：

- decision boundary first
- minimum complete tools second
- necessary factual grounding third

不得把 public skill 普遍退化成针对强模型的逐步动作剧本。

### FR-009 Beacon 必须允许把外部开源方法蒸馏为内部 contract，而不是 runtime dependency

Beacon 必须能表达：

- external source as research input
- internalized principle as frozen Beacon truth
- no default dependency on external repo presence

### FR-010 Beacon 必须让 `brainstorm -> change/prd` promotion 边界更明确

对于类似本次 `v1.4.6` evolution 头暴，Beacon 必须能清楚区分：

- 哪些内容只停留在 brainstorm / research
- 哪些内容应 promotion 到正式 PRD / change

避免 support-surface 研究结论长期悬空。

## 7. 验收标准

| AC ID | 说明 |
| --- | --- |
| AC-001 | Beacon v1.4.6 冻结统一的 `Skill Anatomy v2` |
| AC-002 | 关键 host-visible skills 具备显式 anti-rationalization sections |
| AC-003 | support surface 的 non-truth / non-gate boundary 被统一写入 public contract |
| AC-004 | high-risk decision challenge 的最小输出合同被正式定义 |
| AC-005 | challenge 结果能映射回 evidence / state / gate impact |
| AC-006 | Beacon 的 orchestration constitution 正式表达 public/support/truth/gate 分层 |
| AC-007 | anti-drift contract 至少具备 lint/check 级 machine enforcement 设计 |
| AC-008 | v1.4.6 没有把 Beacon 退化成 script-first skill pack |
| AC-009 | 外部开源方法被蒸馏为内部 contract，而不是默认 runtime dependency |
| AC-010 | `brainstorm` 到 `change/prd` 的 promotion boundary 更清楚且可执行 |

## 8. 约束与边界

- 仍遵守 `docs/beacon/global-boundaries.md`
- `brainstorm` 仍然是 read-only convergence surface
- `change` 仍然是 frozen truth 的正式补料/重开路由
- `implement / qa / release` 不得反向重写 requirement truth
- learning 仍只能辅助判断，不能直接定义 truth 或 gate verdict

## 9. 风险

### 9.1 把 skill 写得更重，可能误伤 Beacon 的轻量哲学

如果 v1.4.6 只是让 skill 变长，而不是让 contract 变清楚，结果会变成：

- 文档更重
- 用户更难读
- 模型仍然可能漂

### 9.2 只写 prompt contract，不做 machine enforcement，会停留在半完成状态

如果只新增 sections，而不补 lint/check：

- contract 可能在新 skill 中逐步退化
- 维护者无法稳定检查覆盖度

### 9.3 把外部开源“整体搬进来”会破坏 Beacon 边界

Beacon 需要的是蒸馏方法，不是引入新的公开主叙事或运行前提。

## 10. Open Questions

1. `high-risk decision challenge` 应作为独立 public surface 冻结，还是先作为 `beacon-implement / beacon-qa / beacon-release` 的受治理子合同存在？
2. `Skill Anatomy v2` 应先覆盖全部 public surfaces，还是先覆盖最核心的 `using-beacon / brainstorm / change / implement / qa / release`？
3. machine enforcement 应先落在 docs lint，还是先落在 release/qa-facing trace checks？
