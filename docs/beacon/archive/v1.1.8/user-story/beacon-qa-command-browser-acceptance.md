# User Story: Beacon QA 命令演进、登录态保存与浏览器验收编排（v1.1.8）

**Feature**: beacon-qa-command-browser-acceptance  
**Version**: v1.1.8

**As a** 使用 Beacon 做真实需求验收的产品/研发/QA/AI Agent 协作方  
**I want** Beacon 把 `auto-test` 正式演进为 `qa`，并支持登录态保存、状态化浏览器验收、项目工作流感知和需求演进式测试  
**So that** Beacon 能用 `agent-browser` / `browser-use` 等 runner 完成真正可交付的完整验收，而不是只跑无状态测试命令。

## Story Slices

### US-001: Beacon 以 `qa` 作为正式用户主入口
作为 Beacon 使用者，我希望用 `beacon qa` 而不是 `auto-test`，以便命令语义更符合真实工作心智。

### US-002: Beacon 兼容 `auto-test`
作为 Beacon 维护者，我希望旧命令仍能兼容，以便不破坏现有工作流。

### US-003: Beacon 支持登录态保存与复用
作为 Beacon 使用者，我希望 QA 能保存网站登录态，以便浏览器验收能连续进行。

### US-004: Beacon 支持状态化浏览器 runner
作为 Beacon 使用者，我希望 `agent-browser` / `browser-use` 成为正式 QA runner，以便真实页面验收可执行。

### US-005: Beacon 支持 project workflow 感知 QA
作为 Beacon 使用者，我希望 QA 能跟随现有 beacon project skill/profile/workflow，以便验收不是旁路脚本。

### US-006: Beacon 支持需求演进式测试
作为 Beacon 使用者，我希望需求变化后 QA 能识别 delta 并演进测试，而不是每次从零来一遍。

### US-007: Beacon 支持浏览器验收证据回写
作为 Beacon 使用者，我希望截图、视频、session refs、网络证据能正式回写到 Beacon evidence/gate/review。

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | Primary Surface | `beacon qa` 成为正式测试/验收主入口 |
| AC-002 | Compatibility | `beacon auto-test` 作为兼容 alias 保留 |
| AC-003 | QA Directory | `.beacon/qa/` 成为 canonical QA 目录 |
| AC-004 | Login State | QA 支持登录态/会话保存与复用 |
| AC-005 | Session Schema | session 至少包含 origin/runner/profile/cookies/storage_state/scopes/expiry |
| AC-006 | agent-browser | `agent-browser` 成为正式 QA runner 之一 |
| AC-007 | browser-use | `browser-use` 成为正式 QA runner 之一 |
| AC-008 | Workflow Binding | QA 可绑定 project profile / skill workflow |
| AC-009 | Delta Evolution | QA 可根据当前需求变化做 delta 测试演进 |
| AC-010 | Browser Evidence | screenshot/video/network/session evidence 可回写 Beacon |
| AC-011 | Gate Compatibility | 过渡期 release/gate 继续兼容 `auto-test-status` |
| AC-012 | Design Scope | v1.1.8 当前先冻结 QA 演进设计，不宣称已实现 |

## 风险与提醒

- 若只改命令名，不补 session 与 runner 一等公民能力，实际体验不会改善
- 若浏览器验收证据不能回写 Beacon，QA 仍然是旁路流程
- 若没有 delta evolution，需求一变测试就会重新人工拼装，成本过高
