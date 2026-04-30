# User Story: Beacon v1.3.9 agents robustness and host runtime compatibility

**Feature**: `beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility`  
**Version**: `v1.3.9`

## Story

作为 Beacon 的版本治理者与真实项目操作者，我希望 Beacon 的 agents 能力不只在 `implement` 中可用，而且在 `qa / release-support / doctor / archive validation` 等场景下也能更可靠、更可恢复，同时明确区分 `codex` 与 `claude` 两类 host runtime 的兼容增强边界，这样我既能得到稳定的内部 agent 执行能力，又不会破坏 Beacon 的最小人类面。

## Requirement Description

本子线聚焦 `v1.3.9` 的 agents 健壮性补强：

- lifecycle applicability matrix
- host runtime compatibility split
- agent run / handoff / guardrail / trace / session contract
- Codex / Claude Code 差异化兼容增强
- 不扩张公开一级命令面

## User Stories

### US-001: Beacon 应明确哪些 lifecycle 场景适合 agents

作为版本治理者，我希望 `implement / qa / release-support / doctor / archive validation` 的 agents 适用面被正式表达，这样新能力不会继续只靠隐式约定扩张。

### US-002: Codex 与 Claude Code 应被区分为两类 host runtime target

作为 host-native runtime 使用者，我希望 Beacon 清楚表达 `codex` 与 `claude` 的 shared capability 和 diverged capability，这样实现与支持层不会把两者误判成等价执行面。

### US-003: Agent run 应有统一 contract

作为调试与运维 Beacon agent runs 的操作者，我希望每次 agent run 都绑定统一 contract，包括 run_id、stage、host_runtime、requirement_binding、traceability refs、stop_state 和 next_action，这样 run 才能被稳定追踪与恢复。

### US-004: 关键 lifecycle 转移应有正式 handoff envelope

作为在 `implement -> qa -> release -> doctor` 之间推进闭环的操作者，我希望 handoff 是正式对象而不是临时 markdown 或散乱状态，这样系统能可靠消费和审计这些转移。

### US-005: Beacon agents 应有分层 guardrails

作为质量与安全边界维护者，我希望 Beacon agents 明确区分 truth guardrail、execution guardrail、evidence guardrail，并允许 Codex / Claude Code 在兼容策略上做差异化增强。

### US-006: Agent trace 应有 machine + human 双层投影

作为人机协作操作者，我希望 agent trace 不只存在 raw runtime 数据，还能投影成高信号 human-readable explanation，这样我能快速看到 blocker、handoff target、next action 和 evidence refs。

### US-007: Session / resume 应按 host runtime 分型

作为恢复中断执行的操作者，我希望 Beacon 对 `codex` 的 repo/workspace resume 与 `claude` 的 context/reasoning resume 分别建模，这样恢复策略不会混淆。

### US-008: Agents 增强不应扩张 Beacon 的公开一级命令面

作为 Beacon 产品边界维护者，我希望 agents 增强仍然隐藏在最小人类面之后，不把内部 runtime 细节变成新的公开命令负担。

## Acceptance Criteria

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
