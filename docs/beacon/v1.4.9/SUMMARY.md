# Beacon v1.4.9 总览

## 版本状态

- `v1.4.9` 当前主题：`ui-ux-externalization-prototype-adapter-and-version-visualization`
- 当前版本状态：`requirement_frozen`
- 本版本线用于冻结 Beacon UI/UX 执行外部化、`prototype` 降级为设计结果适配器、以及版本级业务流程 / 状态机 / 三件套映射图契约。

## 版本目标

`v1.4.9` 当前包含两条正式子线：

1. `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
2. `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`

第一条子线已经冻结 UI/UX 责任边界：

> Beacon 不再冗余维护 UI/UX 设计执行能力；UI/UX 探索、系统建议、评审、打磨、截图拆解和设计库参考统一路由到 `ui-ux-dev`。Beacon 只保留设计结果进入需求冻结 truth 的治理适配层，并补齐版本级人类可读业务流程、状态机和 PRD / user-story / test-case 映射投影。

第二条子线按 P0 优先级冻结真实项目 QA 闭环修复：

> 先修复 implementation evidence writeback、Markdown QA -> machine matrix fail-closed、project runner profile、admission blocker taxonomy 和 BMTOP regression fixture；Better Harness Skill Eval Kit 与 `qa-evo-deep` 作为后续 P1/P2 输入。

## 当前需求包

- Research
  - `docs/beacon/v1.4.9/research/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/research/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
  - `docs/beacon/v1.4.9/research/qa-evo-deep-human-subskill-and-implementation-qa-closure-gap.md`
  - `docs/beacon/v1.4.9/research/better-harness-skill-eval-kit-and-source-driven-regression-core.md`
- Source Architecture
  - `docs/beacon/v1.4.9/source-architecture/index.md`
  - `docs/beacon/v1.4.9/source-architecture/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/source-architecture/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- Change
  - `docs/beacon/v1.4.9/change/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/change/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- PRD
  - `docs/beacon/v1.4.9/prd/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/prd/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- User Story
  - `docs/beacon/v1.4.9/user-story/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- Test Cases
  - `docs/beacon/v1.4.9/qa/test-cases/ui-ux-externalization-prototype-adapter-and-version-visualization-contract.md`
  - `docs/beacon/v1.4.9/qa/test-cases/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`

## 正式子线

- `ui-ux-externalization-prototype-adapter-and-version-visualization-contract`
- `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`

## 冻结边界

本次冻结包括：

- UI/UX execution ownership 从 Beacon 迁移到 `ui-ux-dev`
- Beacon `prototype` 从设计生成面降级为 design-result adapter
- `beacon-design-review` 从设计执行面降级为 route / governance support surface
- 版本级 business flow projection 契约
- 版本级 state-machine projection 契约
- 版本级 PRD / user-story / test-case map 契约
- 每个可视化投影必须具备 truth bindings
- 旧 prototype 材料兼容读取与迁移边界

本次冻结不包括：

- 直接删除所有 `prototype` 代码
- 直接实现 UI/UX upstream 调用器
- 把 `ui-ux-dev` 变成 Beacon 生命周期 stage
- 把业务流程图、状态机图或设计输出变成 canonical truth
- 执行 implementation、QA 或 release
- 直接实现 Better Harness Skill Eval Kit
- 直接新增 `qa-evo-deep` 主能力

## P0 QA 闭环冻结边界

新增 P0 子线包括：

- implementation evidence writeback / import-evidence
- Markdown QA -> machine AC matrix 编译，失败必须 fail closed
- project runner profile，首批至少覆盖 Go + UniApp 命令矩阵
- environment / runner / auth / evidence blocker 与 product/test failure 分层
- BMTOP `rules-encyclopedia-admin-closure` regression fixture

新增 P0 子线不包括：

- Better Harness Skill Eval Kit 完整实现
- support-skill regression core 完整实现
- `qa-evo-deep` release supplement 自动化
- 新生命周期 stage

## 下一步

冻结完成后，下一跳是：

- `beacon-implement`

UI/UX 子线 implement 必须先实现并验证：

- prototype 命令与 skill 的 deprecation / adapter 化路线
- `ui-ux-dev` route handoff contract
- requirement visualization 文件结构与 truth binding parser
- gate 对缺失 visualization truth bindings 的 fail-closed 规则
- historical prototype compatibility guard

P0 QA 闭环子线 implement 必须先实现并验证：

- implementation evidence marker 与 import-evidence
- Markdown QA parser fail-closed
- Go + UniApp runner profile
- admission blocker taxonomy
- BMTOP regression fixture
