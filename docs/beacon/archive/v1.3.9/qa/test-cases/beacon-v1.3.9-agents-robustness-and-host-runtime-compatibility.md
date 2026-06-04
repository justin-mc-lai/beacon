# Test Cases: Beacon v1.3.9 agents robustness and host runtime compatibility

**Feature**: `beacon-v1.3.9-agents-robustness-and-host-runtime-compatibility`  
**Version**: `v1.3.9`

## Coverage Matrix

| TC ID | AC ID | Scenario | Layer | Expected |
| --- | --- | --- | --- | --- |
| TC-001 | AC-001 | 读取 `v1.3.9` agents 子线 requirement package | docs | `implement / qa / release-support / doctor / archive validation` 的 agents applicability matrix 清晰存在。 |
| TC-002 | AC-002 | 在 host-native runtime surfaces 中检查 `codex` 与 `claude` 兼容语义 | integration | 系统能区分 shared capability、Codex-specific compatibility、Claude-specific compatibility 与 host divergence rule。 |
| TC-003 | AC-003 | 执行一次 Beacon agent run 并读取其 machine-readable payload | integration | run payload 至少包含 run_id、stage、feature、version、host_runtime、requirement_binding、traceability refs、stop_state、next_action。 |
| TC-004 | AC-004 | 观察 `implement -> qa`、`qa -> implement-repair`、`qa -> release`、`release -> doctor` 这些关键转移 | integration | handoff 被正式写成 envelope，可被系统消费而不是只靠临时文档。 |
| TC-005 | AC-005 | 在 Codex 与 Claude Code 两类 host runtime 下检查 agent guardrails | integration | truth / execution / evidence 三层 guardrail taxonomy 存在，并允许 host-specific compatibility enhancement。 |
| TC-006 | AC-006 | 读取一个 agent-driven lifecycle feature 的 trace artifacts 与人类说明面 | docs | 同一轮 agent execution 同时有 machine trace 与 high-signal human projection。 |
| TC-007 | AC-007 | 中断并恢复一条 Codex agent run 与一条 Claude-style reasoning run | integration | 系统能区分 repo/workspace resume 与 context/reasoning resume 的恢复契约。 |
| TC-008 | AC-008 | 查看 Beacon 对外一级命令面 | docs | agents 增强后仍保持 `prd / user-story / test-case / prototype / implement / qa / release` + support surfaces，不新增公开一级 agent 命令。 |

## Execution Notes

- `TC-002`、`TC-003`、`TC-004`、`TC-005`、`TC-007` 需要至少一部分真实 run 或隔离环境验证，不能只靠静态文本断言。
- `TC-006` 和 `TC-008` 负责验证人类面没有退化成新的 runtime 噪音暴露面。
- 本子线重点是健壮性与兼容性 contract，不要求在本阶段把所有 agentized lifecycle surface 全部实现完毕。
