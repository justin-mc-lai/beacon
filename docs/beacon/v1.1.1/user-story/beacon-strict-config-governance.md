# User Story: Beacon 严格配置治理、Research 编排、交付 Manifest 与 AI Agent 落地（v1.1.1）

## Story

**As a** 使用 Beacon 的产品负责人 / QA / AI Agent 维护者，
**I want** Beacon 在执行前严格解析 workspace、项目、实现目录与 Git 版本配置，把 brainstorm / analysis / research 统一落盘到 research 目录后再收敛入主链，并把受影响项目与 Git 分支信息显式写入交付物，
**So that** 每次需求物料产出都能绑定到正确的项目、正确的版本，发散内容可追踪但不会污染最终交付主源，并具备可审计、可复现、可交接的执行证据。

## Acceptance Criteria

| AC ID | 维度 | 标准 |
|------|------|------|
| AC-001 | Functionality | strict 模式下，workspace 未配置或目标项目无法解析时，workflow / doctor 直接 BLOCKED |
| AC-002 | Functionality | 支持 workspace 多项目路由，优先级为 CLI > 环境变量 > cwd 匹配 > default |
| AC-003 | Functionality | 支持实现目录配置（root/include/exclude），implementation / verify 超范围时阻断 |
| AC-004 | Governance | Git branch/tag/commit 至少一项必须与 Beacon 版本对齐，否则 `verify-git-alignment --strict` BLOCKED |
| AC-005 | Governance | doctor 支持 setup-config / verify-config / fix-config / setup-workspace / verify-workspace |
| AC-006 | Agent UX | doctor 可向 `CLAUDE.md`、`AGENTS.md` 及配置声明的初始化 md 文件注入完整 Beacon 生命周期说明 |
| AC-007 | Data | 每次执行生成 `execution/config.json`、`execution/source.json`、`execution/git-alignment.json` |
| AC-008 | UX | workflow preflight 在执行前输出 Resolved Project / Version / Docs Source / Strict Mode 摘要 |
| AC-009 | Compatibility | `docs/beacon/<version>/` 为唯一人工维护源，`docs/product/<version>/` 仅作为 compat 镜像 |
| AC-010 | Error Handling | strict 模式下所有 P0 失败项都带 reason code、问题详情与修复命令建议 |
| AC-011 | CI/Gate | CI 可串联 verify-config / verify-git-alignment / verify-agent-md / gate check 作为标准校验链路 |
| AC-012 | Research Orchestration | brainstorm / analysis / research 统一落盘到 `docs/beacon/<version>/research/`，analysis 与 brainstorm 视为 research 子类型 |
| AC-013 | Research Governance | research 文档必须带有 type/status/feature/version/convergence_targets/source_of_truth 等治理信息，且 `source_of_truth=false` |
| AC-014 | Workflow Boundary | workflow / gate 只消费 `user-story / prd / test-case`，research 不得直接作为最终交付主源 |
| AC-015 | Convergence | research 必须先收敛到 `user-story / prd`，再进入 `test-case`，并可追溯来源 research 文档 |
| AC-016 | Delivery Manifest | `execution/delivery-manifest.json` 必须列出受影响项目、repo、project_root、base/current/target branch、commit/tag、worktree_path |
| AC-017 | Change Impact | `execution/change-impact.json` 必须列出 changed_layers、tasks 以及是否已完成主链/交付链收敛 |
| AC-018 | Delivery Blocking | strict 模式下 affected_projects 缺失、Git refs 缺失或 change-impact 未闭环时，交付就绪必须 BLOCKED |

## Notes

- 本故事聚焦 **Beacon 工程化治理能力**，不扩展 Beacon 到业务代码自动实现。
- 本故事目标是让 AI Agent 在项目内“默认走 Beacon 生命周期”，而不是依赖个体记忆或人工约定。
- v1.1.1 文档口径以 `docs/beacon` 为唯一 source/meta，compat 视图仅用于过渡兼容。
- research 层是输入层，不是交付层；真正参与 gate 的仍然是主链文档与执行证据。
- 多项目 / 多仓库变更范围必须成为正式交付物，而不是散落在聊天、临时注释或内部 state 文件中。

## Metadata

| Field | Value |
|-------|-------|
| Priority | high |
| Story Points | 13 |
| Status | draft |
| Created | 2026-03-13T09:44:18.288411 |
| Memory Context | /Users/apple/Developer/Personal/my_skill/beacon/.beacon/state/workflow-memory/run-20260313T014417Z-b758/user-story-context.json |
