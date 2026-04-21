# PRD：Beacon v1.3.6 可视化管理端与项目物料查看器

**Feature**: `beacon-v1.3.6-visual-management-console-and-material-viewer`
**Version**: `v1.3.6`  
**Date**: `2026-04-20`  
**Status**: `frozen`
**Track**: `main`  
**Scenario**: `visual-management-console`  
**Template**: `主 PRD / UI-console`  

## Context

- Global boundaries: `docs/beacon/global-boundaries.md`
- Version summary: `docs/beacon/v1.3.6/SUMMARY.md`
- Execution index: `docs/beacon/v1.3.6/execution/index.md`
- Upstream freeze line: `docs/beacon/v1.3.5/prd/beacon-v1-3-5-prototype-wireframe-mode-and-prototype-surface-refactor.md`
- Design input: `docs/plans/2026-04-20-prototype-wireframe-mode-design.md`
- Upstream source line: `docs/beacon/v1.3.4/prd/beacon-v1.3.4-global-runtime-projection-and-pocketbase-control-plane.md`

## 1. 问题

### 1.1 当前缺口

`v1.3.4` 已经把 Beacon 的 runtime projection、SQLite、PocketBase、`pb_public` 静态面和公开域名链路拉通，`v1.3.5` 又把 `prototype` 收口为 `wireframe only` 并冻结了 Beacon 管理端看板的页面结构。

当前仍未闭环的缺口是：

1. wireframe 已经有了，但管理端产品面还没有被正式实现。
2. 页面结构、角色层级、文档查看器体验仍停留在冻结说明，而不是实际产品承诺。
3. 如果继续把 wireframe 与 UI 成品放在同一版本线，会把“需求冻结”和“产品化实现”再次混淆。

### 1.2 为什么要进入 `v1.3.6`

版本顺序必须明确：

- `v1.3.5` 先解决 `prototype -> wireframe freeze`
- `v1.3.6` 再消费这些 freeze artifact，正式实现 Beacon 管理端看板

这样才能避免：

1. 还没冻结页面结构就直接改 UI。
2. 又回到 HTML 高保真原型主导需求的旧路径。
3. 实现团队与需求团队对“当前到底在做结构冻结还是做产品交付”理解不一致。

## 2. 目标

### 2.1 主要目标

`v1.3.6` 的目标是把 Beacon 可视化管理端单独定义为一个正式产品面，并基于 `v1.3.5` wireframe 包实现以下四类交付：

1. Beacon UI 展示项
2. Beacon UI 数据视图
3. Beacon UI 交互结构
4. Beacon 项目物料 Markdown 只读查看

### 2.2 非目标

本版本不承担以下内容：

- 不重做 SQLite / PocketBase / runtime-ledger 的底层存储契约
- 不重写 `prototype` wireframe 规范
- 不开放 Markdown 在线编辑
- 不新增人类公开一级主命令
- 不把 `omc`、`omx` 等 Beacon 外系统纳入管理端范围

### 2.3 与 `v1.3.5` 的分层目标

- `v1.3.5` 负责：
  - `prototype` 收口为 `wireframe only`
  - 页面清单、导航图、单页草图、状态说明冻结
- `v1.3.6` 负责：
  - Beacon 管理端成品 UI
  - Markdown 物料查看器成品体验
  - 角色化信息组织
  - 页面交互和展示层收口

规则：

> `v1.3.5` 冻结结构，`v1.3.6` 产品化实现结构。

## 3. 设计原则

### 3.1 正式真相不迁移

Beacon UI 只能消费投影数据，不得改写正式真相。

正式真相仍然是：

- `docs/beacon/<version>/`
- `.beacon/`
- 目标项目继承的 `AGENTS.md` / `CLAUDE.md`

### 3.2 生命周期优先于机器噪音

管理端默认先展示：

- 项目推进到哪里
- 当前交付内容
- 还缺什么
- 是否需要介入

而不是默认先展示：

- tmux pane
- raw event
- 完整 transcript
- 机器内部调度细节

### 3.3 页面必须回链 wireframe freeze

`v1.3.6` 中的页面实现必须能够回链到 `v1.3.5` 的 wireframe artifact：

- 页面 ID
- 页面职责
- 页面跳转
- 页面状态说明

不得在实现阶段重新引入 HTML 高保真原型作为 requirement 来源。

### 3.4 Markdown 只读查看必须正式化

项目物料查看器是正式产品功能，但必须严格限制为：

- 网页内只读查看
- 按版本展示
- 按文档类型分类

不得演变为在线编辑器。

## 4. 范围

### In scope

- Beacon 管理端首页
- Beacon 管理总览页
- Beacon 项目详情页
- Beacon 运行中心页
- Beacon 恢复诊断页
- 项目 Markdown 物料只读查看器
- 角色视图和页面信息优先级
- 页面级数据映射与交互行为定义
- 多项目、多版本、多 PRD 轨道展示

### Out of scope

- 在线编辑 Markdown
- 在 UI 中直接创建 / 修改 PRD、User Story、Test Case
- 替代命令行主流程
- 跨产品控制台融合
- 重新定义 prototype 规范

## 5. 功能需求

### FR-001 首页必须先回答经营判断

首页必须首先回答 CEO / 一人公司经营者最关心的问题：

1. 现在有哪些项目在推进。
2. 每个项目推进到哪个阶段。
3. 当前交付了什么。
4. 哪些项目被阻塞。
5. 接下来需要我介入什么。

### FR-002 管理总览必须提供多项目密集视图

管理总览必须提供一张密集、稳定、可扫描的多项目注册表，支持快速理解：

- 项目名
- 项目类型
- 当前版本
- 主线 feature
- 当前阶段
- 进度摘要
- 下一步
- 推荐 skill
- 运行态摘要
- 健康态
- debug 态
- 需求物料状态

### FR-003 项目详情必须成为接力页

项目详情页必须优先服务项目负责人和接力操作者，回答：

1. 这个项目现在推进到哪里。
2. 为什么是这个状态。
3. 当前版本有哪些主 PRD / 并行 PRD。
4. 还缺什么 requirement 物料。
5. 当前应该走哪个 Beacon skill。
6. 当前 git / worktree 是否处在规范状态。

### FR-004 运行中心必须下钻 single / team / ralph

运行中心必须专门承担 runtime 下钻，而不是抢首页叙事。

### FR-005 项目物料查看器必须支持按版本只读查看

管理端必须支持网页内查看版本包文档、PRD、user-story、test-case，并保留来源路径与版本上下文。

### FR-006 页面实现必须依赖 `v1.3.5` wireframe 包

每个正式页面都必须能找到对应的上游 freeze artifact，至少包括：

- `wireframe-summary.md`
- `navigation-map.md/json`
- 对应 `pages/*.md`
- freeze / review 结论

## 6. 验收方向

`v1.3.6` 进入实现的前提是：

1. `v1.3.5` 已经冻结 Beacon 管理端看板的 wireframe 包。
2. 本线页面承诺和 `v1.3.5` wireframe artifact 存在稳定映射。
3. 管理端首页、总览、详情、运行中心、恢复诊断、文档查看器的产品边界已经明确。
4. `omc / omx` 等 Beacon 外系统仍然被排除在默认展示边界外。
