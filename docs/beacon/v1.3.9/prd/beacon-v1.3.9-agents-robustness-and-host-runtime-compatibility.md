# PRD: Beacon v1.3.9 agents robustness and host runtime compatibility

**Feature**: `beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility`  
**Version**: `v1.3.9`

## 1. Problem

Beacon `v1.3.9` 已经开始把 agents 深度用于 `implement`，并且 `qa / release-support / doctor / archive validation` 也逐渐显露出 agent 化需求。但当前 Beacon 还缺一条明确的 agents 健壮性子线，导致三个风险同时存在：

1. **host runtime 兼容语义不够清楚**
   - `codex` 与 `claude` 已经都出现在 Beacon 的 runtime/delegation surfaces 中。
   - 但 Beacon 仍没有把两者的兼容差异、能力差异、限制差异做成正式 requirement truth。
   - 结果是实现层和支持层容易把 “都叫 host-native agent” 误当成同一种执行面。

2. **agents 能力仍偏实现期局部增强，而不是 lifecycle 级能力**
   - 当前已知稳定场景是 `implement`
   - 但 `qa`、`release-support`、`doctor`、`archive explain/validation` 也具备明确的 handoff / trace / resume / guardrail 需求
   - 如果没有统一 contract，这些场景会继续各自演化，导致 agents 能力碎片化

3. **agents 健壮性 contract 不完整**
   - handoff envelope
   - run contract
   - trace projection
   - session/resume safety
   - guardrail taxonomy
   这些都还没有被要求在 Codex / Claude Code 两类 host runtime 上做正式兼容对齐

本线的参考样本来自：

- 开源仓库：`https://github.com/openai/openai-agents-python`
- 本地镜像：`/Users/apple/Developer/Personal/oss-sync/agents/openai-agents-python`

它提供了 Beacon 可以直接借鉴的 6 个概念层：

- agent
- runner
- handoff
- guardrails
- tracing
- session / sandbox

但 Beacon 不应该直接照搬它的公开 SDK 面，而应该把这些概念吸收到 Beacon 自己的 lifecycle kernel 中。

同时，`storyverse-studio` 的真实执行摩擦也补充证明了这条子线的必要性：

- 参考分析：
  - `/Users/apple/Developer/Personal/products/storyverse-studio/.beacon/analysis/memory-friction-evolution-storyverse-inkos-skill-integration-20260427.md`

它暴露出：

- skill-backed implement surface 缺正式 contract
- Ralph 对长任务 batch/ceiling/next window 缺少原生语义
- workbench state sync 缺 artifact family transaction model
- fresh friction capture 对新场景不够敏感

这些都不是单纯 `implement` 细节，而是 Beacon agents 健壮性不足的真实例证。

## 2. Goal

新增一条 `v1.3.9` 并行 agents 子线，定义：

1. Beacon 在哪些 lifecycle 场景适合使用 agents
2. Codex 与 Claude Code 两类 host runtime 的兼容增强边界
3. agents execution / handoff / trace / guardrail / session contract
4. 在不新增公开一级 agent 命令的前提下，如何让 Beacon agents 更健壮、更可靠、更可追踪

## 3. Expected Result

完成后，Beacon 应满足：

1. `implement` 不再是唯一有正式 agents contract 的场景。
2. `qa / release-support / doctor / archive validation` 具有可复用的 agents 能力模型。
3. `codex` 与 `claude` 在 Beacon 中被正式区分为两类 host runtime compatibility target，而不是隐含等价。
4. agents 相关信息被收敛在最小人类面之后，不新增新的公开一级 agent 命令。
5. agents 的执行、handoff、trace、guardrail、resume 均能回链 requirement truth 与 transaction lineage。

## 4. Scope

### In Scope

- Codex / Claude Code host runtime compatibility contract
- lifecycle-specific agent applicability matrix
- agent run contract
- handoff envelope contract
- agent guardrail taxonomy
- agent trace human projection contract
- session / resume contract
- support/read-model 对 agents state 的消费边界

### Out of Scope

- 新增新的公开一级 agent 命令
- 把 Beacon 改造成通用 agents SDK
- 直接替换现有 Beacon team/ralph/runtime surfaces
- 让 agents 自由改写 frozen requirement truth

## 5. Product Semantics

### 5.1 Beacon 对 agents 的总原则

Beacon 的 agents 不是公开产品主面，而是内部执行增强层。

对人类仍保持：

```text
prd
-> user-story
-> test-case
-> prototype
-> implement
-> qa
-> release
```

agents 的作用是：

- 提升执行可靠性
- 提升 handoff 清晰度
- 提升 traceability
- 提升 resume/recovery 安全性

不是：

- 新增一组人类必须理解的命令层

### 5.2 Codex 与 Claude Code 兼容语义

Beacon 必须把以下区分显式建模：

1. **shared compatibility**
   - 都支持 host-native prompt orchestration
   - 都支持 subagent/team runtime readiness checks
   - 都必须绑定同一 requirement truth

2. **Codex-specific compatibility**
   - 更贴近 repo-local coding / patch / branch-aware execution
   - 更适合 `implement-team`、`native-single`、`qa repair handoff`
   - 需要更强调 workspace state、changed files、artifact writeback obligations

3. **Claude Code-specific compatibility**
   - 更贴近 reasoning-sidecar / long-form convergence / high-context routing
   - 更适合 brainstorm / architecture review / release explanation / doctor advise sidecar
   - 需要更强调 prompt-boundary、context inheritance、human-readable explanation fidelity

4. **host divergence model**
   - 同一 feature 在 `codex` / `claude` 下允许 execution shape 不同
   - 但不允许 requirement truth、acceptance semantics、transaction truth 不同

## 6. Lifecycle Applicability Matrix

### 6.1 Implement

这是当前已知成立的 agent 主场景。

目标：

- 保留 `implement-team`
- 保留 `ralph`
- 强化 handoff / trace / resume contract

### 6.2 QA

`qa` 是 `v1.3.9` 最需要补强的 agent 场景。

agent 可承担：

- coverage routing
- layer fanout
- repair handoff generation
- acceptance dual-write orchestration

### 6.3 Release-support

`release` 不应变成新的复杂 agent stage，但应支持 agent sidecar：

- release auditor
- gate/release convergence verifier
- change-doc completeness explainer

### 6.4 Doctor

`doctor` 适合作为 diagnosis-oriented agent surface：

- context drift diagnosis
- version mismatch reasoning
- materials sync failure explanation
- resume safety judgement

### 6.5 Archive / historical truth validation

适合作为 classification/explain/validation agent surface：

- archive classification
- archive safety explain
- historical truth isolation validation

### 6.6 PRD / User Story / Test Case

这些阶段允许 agent 辅助：

- ambiguity detection
- missing-point detection
- coverage suggestion

但不允许 agent 越过 formal truth contract，直接自由改写 frozen materials。

## 7. Diagram Truth Layer

本子线被视为复杂 feature，freeze 前必须具备最小 diagram truth layer。

### 7.1 Branch Flow

```text
requirement truth
-> host runtime compatibility split
-> agent run / handoff / guardrail / trace / resume contracts
-> lifecycle-specific rollout
-> implement / qa / release-support / doctor / archive validation consumption
```

### 7.2 State Machine

```text
draft
-> requirement-clarified
-> frozen
-> host-compatibility-bound
-> lifecycle-agentized
-> validated
-> released
```

异常回路：

```text
lifecycle-agentized
-> compatibility-drift-detected
-> repair / guardrail tighten / resume contract update
-> lifecycle-agentized
```

### 7.3 Decision Priority

本子线的决策优先级必须保持：

1. 不扩张公开一级命令面
2. requirement truth / acceptance semantics / transaction truth 不能因 host runtime 不同而漂移
3. Codex / Claude Code 可以 execution shape 不同，但必须 contract-compatible
4. agent trace 先保证高信号 human projection，再考虑更多 raw detail
5. 新增 agent 场景先覆盖 `qa / doctor / release-support`，最后才考虑 requirement-side增强

### 7.4 State Axes

本子线至少显式建模以下 state axes：

- `host_runtime_axis`
  - `codex`
  - `claude`

- `lifecycle_surface_axis`
  - `implement`
  - `qa`
  - `release-support`
  - `doctor`
  - `archive-validation`

- `agent_contract_axis`
  - `run-contract`
  - `handoff-envelope`
  - `guardrail-taxonomy`
  - `trace-projection`
  - `session-resume`

- `human-surface-axis`
  - `minimal-human-surface-preserved`
  - `runtime-detail-hidden`
  - `explanation-projection-available`
## 8. Core Contracts

### 8.1 Agent Run Contract

每次 Beacon agent run 至少要绑定：

- run_id
- feature
- version
- stage
- host_runtime
- execution_surface
- requirement_binding
- traceability_refs
- stop_state
- next_action

### 8.2 Handoff Envelope

至少正式覆盖：

- implement -> qa
- qa -> implement-repair
- qa -> release
- release -> doctor
- doctor -> implement/qa/human

### 8.3 Guardrail Taxonomy

Beacon agents 必须区分：

1. truth guardrail
2. execution guardrail
3. evidence guardrail

并支持按 host runtime 判断：

- 哪些 guardrails 在 `codex` 下必须阻断
- 哪些 guardrails 在 `claude` 下只允许 explanation / warn

### 8.4 Trace Projection

Beacon agents 的 trace 不应只停在 raw runtime state。

必须支持：

- machine trace
- human-readable projection

并且 human projection 默认只暴露：

- current blocker
- handoff target
- next action
- evidence refs

### 8.5 Session / Resume Contract

至少覆盖：

- safe_to_resume
- stale_context
- replay_required
- human_confirmation_required

并区分：

- Codex repo-local resume
- Claude Code reasoning-sidecar resume

## 9. Functional Requirements

| FR ID | Related AC | Requirement |
| --- | --- | --- |
| FR-001 | AC-001 | Beacon 必须把 `implement / qa / release-support / doctor / archive validation` 的 agent applicability 明确建模，而不再只隐式落在 `implement`。 |
| FR-002 | AC-002 | Beacon 必须正式区分 `codex` 与 `claude` 两类 host runtime compatibility target，并写清 shared / diverged capabilities。 |
| FR-003 | AC-003 | 所有 Beacon agent runs 必须绑定统一 agent run contract，至少包含 run_id、stage、feature、version、host_runtime、requirement_binding、traceability_refs、stop_state、next_action。 |
| FR-004 | AC-004 | Beacon 必须为关键 lifecycle 转移提供正式 handoff envelope，而不是只依赖临时 markdown/hud/state 拼接。 |
| FR-005 | AC-005 | Beacon agents 必须使用 truth / execution / evidence 三层 guardrail taxonomy，并允许对 Codex / Claude Code 做差异化兼容增强。 |
| FR-006 | AC-006 | Beacon 必须把 agent trace 投影到 machine + human 两层，并保持 human projection 只呈现高信号解释面。 |
| FR-007 | AC-007 | Beacon 必须定义 session/resume contract，并区分 Codex 的 workspace-oriented resume 与 Claude Code 的 context-oriented resume。 |
| FR-008 | AC-008 | Beacon 不得因为 agents 能力增强而新增新的公开一级主命令；agents 能力必须继续隐藏在最小人类面之后。 |

## 10. Acceptance Traceability

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | lifecycle-matrix | `implement / qa / release-support / doctor / archive validation` 的 agent applicability matrix 明确存在。 |
| AC-002 | host-compatibility | `codex` 与 `claude` 的 shared / diverged compatibility contract 被正式表达。 |
| AC-003 | run-contract | Beacon agent run contract 被 machine-readable surface 消费。 |
| AC-004 | handoff-envelope | implement/qa/release/doctor 之间的关键 handoff 存在正式 envelope。 |
| AC-005 | guardrail-taxonomy | truth / execution / evidence 三层 guardrail taxonomy 被定义，且支持 Codex / Claude Code 差异化兼容增强。 |
| AC-006 | trace-projection | agent trace 同时存在 machine trace 与 high-signal human projection。 |
| AC-007 | resume-contract | session / resume contract 明确区分 repo/workspace 与 context/reasoning 两类恢复模式。 |
| AC-008 | minimal-human-surface | agents 增强后 Beacon 仍保持当前公开一级命令面不扩张。 |

## 11. Risks

- 如果只增强 `codex` 不增强 `claude`，Beacon 会在 host-native runtime 上形成不对称稳定性。
- 如果 handoff envelope 不正式化，QA/release/doctor 侧的 agent 使用会继续退化成经验流转。
- 如果 trace 只保留 machine 视图，人类仍然无法高效理解 agent stop_state 与 next_action。
- 如果 agents 过度公开化，会直接破坏 Beacon 的极简人类主面。

## 12. Release Guard

- 本子线进入 user-story 前必须确认：
  - lifecycle applicability matrix 已明确
  - Codex / Claude Code host compatibility 已分层
  - run / handoff / guardrail / trace / resume 五类 contract 都有 requirement 锚点
- 本子线不得要求新增新的公开一级 agent 命令作为 release 条件
