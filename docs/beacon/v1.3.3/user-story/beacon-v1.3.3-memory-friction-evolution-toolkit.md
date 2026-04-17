# 用户故事：Beacon v1.3.3 记忆进化与摩擦演进 Toolkit

**Feature**: `beacon-v1.3.3-memory-friction-evolution-toolkit`  
**Version**: `v1.3.3`  
**Date**: `2026-04-17`  
**Status**: `planning line`

## US-001：作为维护者，我希望 toolkit 与 lighthouse 并行运行而不干扰主链

**验收标准**：

- toolkit 仅在 `labs/hidden` 面可见
- 与 `beacon-toolkit-lighthouse` 可并行执行并各自产物
- 不改变 `prd -> user-story -> test-case -> implement -> qa -> release` 主路径

## US-002：作为维护者，我希望复用现有记忆与摩擦数据面，而不是新增 memory silo

**验收标准**：

- 复用 `remember/recall/workflow_memory/debug_feedback/learning_loop`
- 不新增第二套 memory 目录标准
- 输出候选必须可追溯到已有证据引用

## US-003：作为问题排障者，我希望看到可执行的 Top-N 摩擦候选

**验收标准**：

- 每条候选包含 `friction_summary`
- 每条候选包含 `evidence_refs`
- 每条候选包含 `recommendation` 与 `recommended_command`

## US-004：作为运行控制者，我希望 loop 可控且可回放

**验收标准**：

- 每轮都有结构化 continue/stop 决策
- `max_turns` 必须生效，防止无限循环
- 每次 run 都有可回放 artifact

## US-005：作为迭代负责人，我希望候选可最小闭环写回 memory

**验收标准**：

- 只允许通过 `remember add --upsert` 语义写回
- 写回必须携带来源和证据引用
- 不允许旁路写回新记忆文件

## US-006：作为版本负责人，我希望并行 toolkit 不扩张主 6+3 心智

**验收标准**：

- 命令面只在 `labs/hidden` 暴露
- 默认帮助面不主动教学该 toolkit
- release 叙事将其归类为 optional analysis plane

## Acceptance Criteria Matrix

| ID | Theme | Acceptance Criteria |
|----|-------|---------------------|
| AC-001 | parallel-tooling | toolkit 与 lighthouse 并行运行，且主链不受影响。 |
| AC-002 | memory-reuse | toolkit 仅复用既有 memory/debug/learning 数据面，不新增 memory silo。 |
| AC-003 | executable-candidates | Top-N 候选必须包含 summary/evidence/recommendation/command。 |
| AC-004 | bounded-loop | loop 每轮结构化决策，且 `max_turns` 有效。 |
| AC-005 | minimal-writeback | 写回仅经 remember upsert，证据可追溯。 |
| AC-006 | no-mainline-expansion | toolkit 只在 optional analysis 面暴露，不扩张主 6+3。 |
