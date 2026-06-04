# PRD: Beacon QA 命令演进、登录态保存与浏览器验收编排（v1.1.8）

## 1. 背景

当前 Beacon 的测试执行主命令仍是：

- `beacon auto-test create`
- `beacon auto-test status`
- `beacon auto-test import-qa-use`

它已经支持：

- QA9 scope
- layer command override
- ui/api/smoke/unit/visual 等层
- browser runner 选项（playwright/cypress/browser-use/agent-browser）
- `.beacon/auto-test-status.json`

但用户修正后的方向已经变化：

> v1.1.8 要把 `auto-test` 的用户主入口升级为 `qa`，并借鉴 gstack 一类状态化浏览器验收思路，支持网站登录态保存、项目 workflow 感知、需求演进式测试，以及通过 `agent-browser` / `browser-use` 完成真实验收闭环。

### 1.1 来自 gstack 源码的直接启发

本地 gstack 源码里已经有几条非常明确的实践答案：

- `qa/SKILL.md`
  - `/qa` 是正式主入口
  - QA 不是孤立测试，而是 test → fix → verify 闭环

- `setup-browser-cookies/SKILL.md`
  - 登录态导入是正式技能，不是旁路技巧

- `browse/src/server.ts` + `browse/src/browser-manager.ts`
  - 浏览器是**持久化 daemon**
  - cookies、tabs、local/session storage 都是长期状态

- `browse/src/cookie-import-browser.ts` + `cookie-picker-routes.ts`
  - cookie/profile/session 桥接不是口头能力，而是源码级基础设施

因此，对 Beacon v1.1.8 的直接启发非常明确：

1. `qa` 应成为正式主入口，而不是继续把 `auto-test` 暴露给用户作为主心智；
2. 登录态/session 必须成为一等公民；
3. `agent-browser` / `browser-use` 不应只是 runner 选项，而应成为正式验收面；
4. 浏览器证据必须进入 Beacon review/gate 的正式证据链。

## 2. 第一性原理结论

### 2.1 为什么要把 auto-test 改为 qa

`auto-test` 更像执行器名字，而真实用户心智是：

- 我要做 QA
- 我要验证当前需求是否闭环
- 我要跑登录态下的真实浏览器验收

因此 v1.1.8 应把：

- **`qa` 作为 primary user surface**
- **`auto-test` 作为兼容 alias**

## 2.2 当前缺失的关键能力

1. 没有正式的登录态/会话保存能力；
2. `browser-use` / `agent-browser` 还不是 Beacon QA 的一等执行面；
3. 现有测试更偏执行命令，不够“需求驱动演进”；
4. 与 v1.1.7 project skill/profile/workflow 的集成还不够强。

## 3. 目标

1. **把 `qa` 升级为 Beacon 的正式测试/验收主入口**
2. **保留 `auto-test` 兼容别名，避免破坏存量工作流**
3. **支持网站登录态保存与复用**
4. **支持 `agent-browser` / `browser-use` / 其它 runner 的真实浏览器验收**
5. **支持根据当前需求物料做测试演进，而不是每次从零跑一套**
6. **支持 project skill/profile/workflow 感知式 QA 编排**

## 4. 非目标

1. 不强制所有项目都使用浏览器 runner；
2. 不把 QA 命令做成特定框架专用；
3. 不在 v1.1.8 直接实现所有 runner 深度集成；
4. 不要求所有登录态都自动托管到云端；
5. 不替代项目自己的业务测试框架。

## 5. 核心设计

## 5.1 命令面迁移

建议主入口迁移为：

- `beacon qa run`
- `beacon qa status`
- `beacon qa import`
- `beacon qa session save`
- `beacon qa session list`
- `beacon qa session use`
- `beacon qa evolve`

兼容层：
- `beacon auto-test create` → alias to `beacon qa run`
- `beacon auto-test status` → alias to `beacon qa status`
- `beacon auto-test import-qa-use` → alias to `beacon qa import`

## 5.2 QA 目录与兼容工件

新增 canonical QA 目录：

```text
.beacon/qa/
  status.json
  runs/<run_id>/summary.json
  runs/<run_id>/evidence/*
  sessions/<session_id>/manifest.json
  sessions/<session_id>/cookies.json
  sessions/<session_id>/storage-state.json
```

兼容策略：
- 继续镜像输出 `.beacon/auto-test-status.json`
- 至少一条版本线保持 `auto-test` 兼容

## 5.3 登录态 / 会话保存

登录态不应只靠“当前浏览器刚好还没退出”。

建议正式模型：

- `session_id`
- `origin`
- `runner_type`
- `profile_ref`
- `cookies_ref`
- `storage_state_ref`
- `captured_at`
- `expires_at`
- `sensitivity`
- `scopes[]`

### Runner 对应思路

#### A. agent-browser
可复用：
- `--session <name>`
- cookies / localStorage / sessionStorage 命令
- screenshot / record / eval / network requests

#### B. browser-use
可复用：
- real browser profile
- cookies export/import
- local profile / cloud profile
- stateful session persistence

## 5.4 QA 必须与项目 workflow/profile 对齐

基于 v1.1.7 已有的：
- project profile
- skill registry
- orchestrate / verify

v1.1.8 的 QA 应进一步支持：

- 某个项目声明自己的 `qa_profile`
- 某个 stage 声明自己的 browser runner / login state
- QA 编排跟随当前 feature 的 project skill workflow 运行

## 5.5 根据当前需求做测试演进

QA 不应每次都“重新生成一套静态测试”；而应支持：

- 从当前 PRD / user-story / test-case / prototype baseline 读取最新变化
- 对变更部分生成 delta tests
- 保留历史 evidence 与回归面

新增建议能力：
- `beacon qa evolve <feature>`

输出：
- changed AC 对应的新 case
- 受影响回归面
- 需要复用或更新的 session / workflow steps

## 5.6 真实浏览器验收闭环

QA 不应只停留在 curl/unit/smoke，还应支持：

- 登录态恢复
- 页面导航
- 交互执行
- 截图/视频/网络证据
- 验收结果回写 Beacon evidence/gate/review

至少支持的 runner 概念：
- `playwright`
- `cypress`
- `agent-browser`
- `browser-use`
- `custom`

## 5.7 借鉴 gstack 的状态化验收思路

v1.1.8 设计借鉴的核心不是 gstack 的具体命令，而是它的思路：

- 浏览器验收应是**有状态**的
- 登录态应可保存与复用
- QA 不是孤立脚本，而应跟随项目工作流
- 失败后应带证据与可复现入口

## 6. 功能需求

### FR-001 `qa` 成为正式主入口
Beacon v1.1.8 对外主测试入口应为 `beacon qa`，`auto-test` 仅作为兼容 alias。

### FR-002 QA 支持登录态保存
QA 必须能保存和复用网站登录态，而不是要求每轮从头登录。

### FR-003 QA 会话必须本地可治理
会话状态应落到 `.beacon/qa/sessions/`，并带 manifest，不得只散落在 runner 自己的临时目录里。

### FR-004 QA 支持 agent-browser / browser-use
这两个 runner 必须在设计上成为 Beacon QA 的正式一等执行面，而不是仅作为文字提及。

### FR-005 QA 支持现有项目 skill workflow
QA 必须能结合 project profile / skill binding / orchestration graph 跑完整验收。

### FR-006 QA 支持需求演进式测试
当 PRD / user-story / test-case / prototype baseline 变化时，QA 能识别 delta 并演进测试计划。

### FR-007 QA 证据必须能回写 Beacon
浏览器验收得到的：
- screenshot
- video
- cookies/session refs
- network evidence
- final verdict

都必须能成为 Beacon review/gate 的正式 evidence。

### FR-008 QA 兼容现有 release/gate
在过渡期：
- `qa status` 的 canonical 状态可镜像到 `.beacon/auto-test-status.json`
- release/gate 不应因命令面升级而失效

### FR-009 当前版本先冻结设计
当前 v1.1.8 先定义命令迁移、session schema、runner 语义、workflow 集成和 evidence contract，不宣称已实现。

## 7. 验收语义

### Pass
- `qa` 主入口、session、runner、workflow、evidence、delta evolution 都定义清晰；
- `auto-test` 的兼容迁移路径清晰；
- 浏览器验收不再是旁路，而是正式闭环的一部分。

### Fail
- 仍然把 QA 停留在旧 `auto-test` 语义；
- 没有登录态/会话治理；
- 无法让 `agent-browser` / `browser-use` 成为正式验收面。

### Blocked
- 命令迁移、session schema 或 evidence contract 仍存在关键冲突。
