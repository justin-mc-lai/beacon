# User Story: beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor

## Story

**As a** Beacon 维护者 / 宿主技能编排设计者 / 稳定交付负责人,  
**I want** Beacon 把全部公开命令统一重构为“宿主原生 LLM 语义层 + Beacon 结构化执行内核”的双层模型，并保持 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 极简主流程不扩张,  
**So that** Beacon 能真正对齐 `OMC / OMX` 的 host-first 运行模式，在 Claude / Codex 中默认复用宿主大模型能力，同时保留 Beacon 自己的 requirement truth、freeze/review/gate 与稳定交付能力。

## Story Slices

### US-001: Requirement 命令必须共享同一宿主语义编译内核

As a maintainer, I want `prd / user-story / test-case / prototype` to share one host-native semantic compile path so that requirement materials no longer drift across separate provider clients and rule fragments.

### US-002: Provider 必须退居 fallback，而不是默认前提

As a skill user, I want Beacon to work inside Claude / Codex without first configuring `BEACON_LLM_API_KEY` so that the host session remains the default semantic engine.

### US-003: Beacon CLI 必须去大脑化，回到结构化执行内核

As an architecture owner, I want the Beacon CLI to focus on truth read, contract validation, canonical assembly, projection, freeze, review, gate, and runtime orchestration so that it stops acting like a second independent LLM product.

### US-004: 全公开命令必须共享同一 semantic envelope 与 mode contract

As a platform maintainer, I want every command to emit the same `requested_mode / effective_mode / fallback_reason / capability_snapshot` contract so that `help / status / doctor / release` can explain the system consistently.

### US-005: `prototype` 必须保留固定模板和 freeze/review，但语义内容改由宿主生成

As a requirement owner, I want `prototype` to keep the fixed wireframe output shell and existing freeze/review checks while moving page semantics to host-native generation so that it becomes LLM-generated content instead of template fill-in.

### US-006: `implement` 必须成为宿主原生编排入口，而不是外接 runner 拼装

As a delivery owner, I want `implement` to remain the only public implementation entry while internally selecting host direct / subagent / team orchestration so that execution becomes host-native without expanding the human command surface.

### US-007: `qa` 必须成为宿主原生验收编排入口

As a release owner, I want `qa` to bind requirement truth and orchestrate verification, repair, and evidence collection through host-native capability so that acceptance remains stable and traceable.

### US-008: `help / status / doctor / release` 必须基于统一 truth 与 evidence 给出判断

As a Beacon operator, I want support and release surfaces to read the same runtime, semantic, and gate evidence so that next-step guidance and release verdicts stop diverging.

### US-009: Runtime 模式改变执行形态，但不得改写 requirement truth

As a product owner, I want host direct / host subagent / host team / provider fallback / rule fallback to share the same `prd / user-story / test-case / prototype` truth so that acceptance semantics remain fixed.

### US-010: 人类主流程必须保持极简，内部复杂度默认隐藏

As a human user, I want Beacon to absorb host-native team, mailbox, recovery, verifier, and runtime complexity behind existing commands so that I do not need to learn a second orchestration product.

## Acceptance Criteria

- [ ] AC-001 宿主模式默认成立：在 Claude / Codex skill 环境里执行 `beacon prd / prototype / implement / qa` 默认不要求 `BEACON_LLM_API_KEY`，并保留 host-native evidence。
- [ ] AC-002 统一 mode contract：`prd / user-story / test-case / prototype / implement / qa / release / help / status / doctor` 的 machine output 或 evidence 中都存在统一的 `requested_mode / effective_mode / fallback_reason / capability_snapshot` 字段。
- [ ] AC-003 requirement 命令同核：`prd / user-story / test-case / prototype` 不再私自直连 provider，各自通过同一 host/provider/rule arbitration 与 semantic envelope 工作。
- [ ] AC-004 `prototype` 不退化：迁移后 `prototype` 仍保留固定模板、freeze/review 与 canonical projection，但页面语义改由宿主原生 LLM 驱动。
- [ ] AC-005 `implement / qa` 宿主原生化：`implement` 与 `qa` 仍是唯一公开执行入口，但内部可选择 host direct / subagent / team，并明确记录选择原因与 requirement 绑定。
- [ ] AC-006 support/release 一致性：`help / status / doctor / release` 对同一 feature 的下一步、降级、gate 与风险解释必须来自统一 truth/read model，而不是各自独立猜测。
- [ ] AC-007 人类主面不扩张：迁移完成后，对外仍只有 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release + help/status/doctor`。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 13 |
| Status | frozen-pending-implementation |
| Version | v1.3.6 |
| Track | parallel |
| Created | 2026-04-21 |
| Feature Slug | beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor |
| Architecture Blueprint | docs/beacon/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md |
