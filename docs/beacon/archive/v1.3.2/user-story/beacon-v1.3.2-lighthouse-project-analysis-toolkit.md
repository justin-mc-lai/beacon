# User Story: beacon-v1.3.2-lighthouse-project-analysis-toolkit

## Story

**As a** Beacon 操作者或接手型开发者，
**I want** to use Beacon Toolkit Lighthouse to analyze a repo, package, infra chain, or feature slice into one Markdown artifact,
**So that** I can build a correct mental model quickly without entering the main Beacon workflow.

## Acceptance Criteria

- [ ] AC-001 正向流程: 用户可以对当前项目或指定子路径运行 Lighthouse，并得到单文件 Markdown 结果。
- [ ] AC-002 数据要求: 输出必须包含关键源码路径、入口文件、依赖/链路引用，并显式区分 Confirmed Facts 与 Inferred Structure。
- [ ] AC-003 用户体验: 输出默认采用 Mermaid + 中文说明，结构稳定且类似 `system-architecture-map.md`。
- [ ] AC-004 性能要求: 默认分析必须限制为单文件结果和有限张 Mermaid 图，避免变成长报告或全仓漫游。
- [ ] AC-005 安全要求: Lighthouse 默认只读分析，不自动触发 PRD / implement / QA，也不写回正式 requirement truth。
- [ ] AC-006 兼容性: Beacon 源码分析时必须同时写 `.beacon/analysis/<slug>.md` 和 `docs/beacon/<version>/execution/beacon-toolkit-lighthouse-<slug>.md`。
- [ ] AC-007 错误处理: 当 mode 不支持、target 缺失或范围不存在时，系统必须返回清晰阻断而不是静默生成错误工件。

## Metadata

| Field | Value |
|-------|-------|
| Priority | medium |
| Story Points | 3 |
| Status | draft |
| Created | 2026-04-16T10:09:37.099210 |
| Memory Context | N/A |
