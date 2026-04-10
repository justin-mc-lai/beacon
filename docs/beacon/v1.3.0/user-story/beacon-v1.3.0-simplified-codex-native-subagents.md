# User Story: Beacon v1.3.0 Simplified Codex Native Subagents

**Feature**: Beacon v1.3.0 - Simplified Codex Native Subagents  
**Version**: v1.3.0  
**Date**: 2026-04-10  
**Status**: planning line

## Story 1: 作为 Beacon 使用者，我希望复杂阶段可以显式启用 subagent，而不是只能单线程生成

**验收标准**:

- Beacon 必须支持阶段级 `subagent_mode`
- `subagent_mode` 必须默认关闭
- 用户必须能看见当前阶段是否启用了 subagent

## Story 2: 作为 Beacon 维护者，我希望每个阶段只暴露有限角色，而不是任意 agent 自由发挥

**验收标准**:

- 每个阶段必须声明允许角色
- 角色必须映射到明确输入、输出、证据路径
- 不允许未注册角色直接进入正式 writeback

## Story 3: 作为需求作者，我希望 think / story / prd 可以用 subagent 做研究、结构化和批判，但最终仍回写到 Beacon 正式材料

**验收标准**:

- `think` 至少支持 `researcher` / `critic`
- `user-story` 至少支持 `story-mapper` / `ac-reviewer`
- `prd` 至少支持 `requirement-parser` / `risk-critic`
- 最终产物仍是 `docs/beacon/<version>/...` 下的正式材料

## Story 4: 作为 QA 负责人，我希望 test-case / qa 的 subagent 输出能直接表现为覆盖率与 repair handoff

**验收标准**:

- `test-case` 至少支持 `scenario-mapper` / `coverage-checker`
- `qa` 至少支持 `verifier` / `repair-handoff-writer`
- 缺失证据时必须阻塞，而不是假装通过

## Story 5: 作为实现负责人，我希望 `implement run` 能对接 Codex 原生子代理，但不重写 Beacon 主链

**验收标准**:

- `implement run` 必须支持新的 Codex-native subagent adapter
- 现有 `native-single` / `native-team` 仍保留
- release/gate 仍只依赖 Beacon 的正式证据面
