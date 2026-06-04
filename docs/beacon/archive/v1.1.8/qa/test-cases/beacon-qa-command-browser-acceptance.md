# Test Cases: Beacon QA 命令演进、登录态保存与浏览器验收编排（v1.1.8）

**Feature**: beacon-qa-command-browser-acceptance  
**Version**: v1.1.8

## 前置 Gate 结论

- Gate0 输入完整性：Pass（已具备 `auto-test` 现状、runner 现状与用户修正目标）
- Gate1 冲突未决判定：Pass（目标明确为命令迁移 + session + runner + workflow + evidence）
- Gate2 AC→TC 映射：Pass（覆盖主入口、兼容、会话、runner、工作流、evidence、delta evolution）

## 测试用例

| TC ID | Type | Scenario | Expected Result |
| --- | --- | --- | --- |
| TC-001 | contract | `beacon qa` 作为正式主入口 | 用户主文档与命令规划以 `qa` 为主，而非 `auto-test` |
| TC-002 | compatibility | `beacon auto-test` 兼容保留 | 不破坏现有命令与 release/gate 依赖 |
| TC-003 | contract | `.beacon/qa/` 作为 canonical QA 目录 | status/runs/sessions 目录清晰可追踪 |
| TC-004 | contract | session schema 定义完整 | 包含 origin/runner/profile/cookies/storage_state/scopes/expiry |
| TC-005 | integration | 保存并复用登录态 | QA 可在后续浏览器验收中使用已保存 session |
| TC-006 | integration | `agent-browser` runner 进入 QA 正式执行面 | 可表达 screenshot/record/cookies/storage 等能力 |
| TC-007 | integration | `browser-use` runner 进入 QA 正式执行面 | 可表达 profile/cookies export-import/stateful session |
| TC-008 | workflow | QA 绑定 project profile / skill workflow | 验收链路与项目 skill 编排一致 |
| TC-009 | evolution | 需求变化后执行 `qa evolve` | 能识别 delta tests 与受影响回归面 |
| TC-010 | evidence | 浏览器验收 screenshot/video/network/session refs 回写 Beacon | review/gate 可消费这些证据 |
| TC-011 | governance | 过渡期镜像 `.beacon/auto-test-status.json` | 旧 gate/release 不回归 |
| TC-012 | scope | 当前 v1.1.8 为设计线 | 文档明确 design-only，不误报已实现 |

## 样板场景

### 场景 A：登录后验收
- 站点需要登录后才能进入核心流程
- 预期：Beacon QA 可复用已保存 session，而不是每轮重新登录

### 场景 B：agent-browser 完整验收
- 使用 `agent-browser` 完成登录、导航、表单提交、截图/录像
- 预期：这些能力在 Beacon QA 中是正式能力，而不是外部手工旁路

### 场景 C：browser-use 状态化验收
- 使用 `browser-use` real profile / cookies export-import
- 预期：Beacon QA 能表达并治理这些状态化会话

### 场景 D：需求演进后的 delta QA
- PRD / user-story / test-case 有新增或变化
- 预期：QA 识别 delta tests，而不是全量手工重编一套

## 执行语义

- `Pass`：`qa` 主入口、session、runner、workflow、evidence、evolution 设计闭环完整
- `Fail`：仍停留在旧 `auto-test` 执行器心智，没有状态化浏览器验收能力
- `Blocked`：命令迁移、session schema、evidence contract 仍有关键冲突
