# PRD: 升级 agent-reach + 对齐第三方 spec skill + 沉淀 AI agent coding 方法论

**Task**: `08-26-sync-agent-reach-spec-skills`  
**Created**: 2026-08-26  
**Status**: planning

## Background

用户三条诉求：

1. 按官方 update.md 更新 Agent Reach 工具链（当前：agent-reach v1.5.0 已是最新；其上游工具 OpenCLI v1.8.6 → v1.8.7 待升）。
2. 更新 beacon 对齐的开源第三方 spec skill——即 `oss-sync` 里 28 个 canonical mirror（`docs/beacon/research/beacon-open-source-reference-source-map.md` 维护），提取上游最新更新；发现 source map 里 `awesome-design-md` 路径错误（实际 `design/skills/`，source map 写成 `core-skills/`）。
3. 把大厂 AI agent coding 方法论（Cursor 工程师 Lauren Tan @poteto 的工作方法）记录下来，支撑 beacon 持续演进。

## Goals

- G1: agent-reach 工具链更新完成并验证（`agent-reach doctor` 可用）。
- G2: 15 个落后上游的 oss-sync canonical mirror 同步到最新，并提取每个仓的更新要点。
- G3: 修正 source map 中 `awesome-design-md` 的错误路径。
- G4: 新增研究笔记记录 Lauren Tan 方法论，映射到 beacon 现有能力（verification-first QA、agent-native 对等、skill 测试、feature map、auto-merge）。

## Non-goals

- 不升级/不卸载 oss-sync 里已有的旧工具（按 manage-oss-sync 规则，保持 fallback）。
- 不为本文档写代码实现；纯文档 + 运维操作。
- 不扩展 beacon 运行时行为。

## Acceptance Criteria

- AC-1: `agent-reach version` 输出 v1.5.0（已最新），`npm ls -g @jackwener/opencli` 显示 v1.8.7，`agent-reach doctor` 正常。
- AC-2: `oss-sync` 15 个落后仓全部 sync 成功（`sync-report.json` 中 updated 计数为 15），index 已刷新。
- AC-3: source map 中 `awesome-design-md` 路径改为 `design/skills/awesome-design-md`。
- AC-4: `docs/beacon/research/` 新增方法论研究笔记，包含：原文出处（推文链接）、核心论点、与 beacon 能力映射、可持续演进的行动建议。

## Deliverables

- `docs/beacon/research/beacon-agent-coding-methodology-cursor-poteto-2026-08.md`（方法论笔记）
- `docs/beacon/research/beacon-oss-reference-sync-2026-08-26.md`（第三方 skill 同步更新摘要）
- `docs/beacon/research/beacon-open-source-reference-source-map.md`（路径修正）
- 运维结果：oss-sync 15 仓更新、opencli v1.8.7

## Notes / Risks

- GitHub 网络间歇性 SSL 断连（LibreSSL SSL_ERROR_SYSCALL）已观察到；失败仓需重试。
- `sync` 命令默认 fetch 超时短，需 `--fetch-timeout` 提升。
