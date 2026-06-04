# Test Cases: beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor

## Overview

**Feature**: `beacon-v1.3.6-host-native-llm-orchestration-and-full-command-runtime-refactor`  
**Version**: `v1.3.6`  
**Status**: `frozen-pending-implementation`  
**Architecture Blueprint**: `docs/beacon/archive/v1.3.6/execution/host-native-llm-and-skill-runtime-blueprint.md`

## Scenario Test Set

### TC-001 (AC-001): Claude / Codex host 环境下 requirement 与 execution 入口默认无需 provider key

- Given：Beacon 运行在 Claude 或 Codex 的 skill/session 环境中，且未设置 `BEACON_LLM_API_KEY`
- When：分别执行 `beacon prd`、`beacon prototype`、`beacon implement`、`beacon qa`
- Then：命令默认仍可进入 host-native 模式或等价 host arbitration，不因缺少 provider key 直接失败，并留下 host-native evidence

### TC-002 (AC-002): 全命令共享统一 mode contract

- Given：对同一 feature 分别触发 `prd / user-story / test-case / prototype / implement / qa / release / help / status / doctor`
- When：检查 machine output、projection 或 evidence artifact
- Then：都应能读取统一的 `requested_mode / effective_mode / fallback_reason / capability_snapshot`

### TC-003 (AC-003): Requirement 命令不再私自直连 provider

- Given：进入 requirement material 生成路径
- When：检查 `prd / user-story / test-case / prototype` 的底层实现与 evidence
- Then：四者都通过同一 semantic adapter 与 arbitration 层运行，而不是各自维护独立 provider client

### TC-004 (AC-004): `prototype` 保持固定模板与 freeze/review，同时改用宿主语义

- Given：已有 requirement truth 与 `prototype` 固定模板
- When：执行 `beacon prototype`
- Then：输出仍符合固定 wireframe 模板、freeze/review 与 canonical projection 契约，但页面语义来自宿主生成而不是模板占位

### TC-005 (AC-005): `implement` 维持唯一公开入口但内部可选择 host direct / subagent / team

- Given：同一 feature 在不同复杂度和宿主能力下执行 `beacon implement`
- When：检查 run contract 与 evidence
- Then：对外仍只有 `implement` 入口；内部可选择 host direct / subagent / team，并记录为什么做出该选择

### TC-006 (AC-005): `qa` 维持唯一公开入口且绑定 requirement truth

- Given：同一 feature 已有 `prd / user-story / test-case / prototype`
- When：执行 `beacon qa`
- Then：QA 运行记录明确绑定 requirement truth，并能解释宿主验证、修复、重试或降级路径

### TC-007 (AC-006): `help / status / doctor / release` 对同一 feature 给出一致解释

- Given：某 feature 存在 host capability、fallback 或 gate 风险
- When：分别调用 `beacon help`、`beacon status`、`beacon doctor`、`beacon release`
- Then：四者对当前模式、降级原因、下一步与风险的解释来自统一 truth/read model，不互相打架

### TC-008 (AC-007): 人类主流程不因宿主原生能力增强而膨胀

- Given：Beacon 已完成宿主原生编排层迁移
- When：检查文档、skill surface、help surface 与公开 CLI 命令
- Then：人类主流程仍然是 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release + help/status/doctor`，没有新增公开一级 `team / subagent / runtime-readiness` 主命令

## Suggested Commands

- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main user-story list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.6`
- `BEACON_ALLOW_CONTEXT_VERSION_DRIFT=1 python3 -m beacon.main test-case list --project /Users/apple/Developer/Personal/products/beacon --version v1.3.6`

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | from AC-001 |
| TC-002 | Pending | from AC-002 |
| TC-003 | Pending | from AC-003 |
| TC-004 | Pending | from AC-004 |
| TC-005 | Pending | from AC-005 |
| TC-006 | Pending | from AC-005 |
| TC-007 | Pending | from AC-006 |
| TC-008 | Pending | from AC-007 |
