# Boundaries: Beacon v1.1.2 UI Prototype 层 + 主链层 + 交付层闭环

**版本**: v1.1.2
**日期**: 2026-03-16
**状态**: Draft
**Feature**: beacon-ui-prototype-lifecycle

---

## 1. 分层边界

### 研究层（Research Layer）
- 目录：`docs/beacon/v1.1.2/research/`
- 内容：`brainstorm-*`、`analysis-*`、`research-*`、`architecture-*`、`compare-*`、`convergence-*`
- 角色：输入层 / 发散层 / 方案沉淀层
- 约束：
  - 不是最终交付主源
  - 不直接参与 gate
  - 必须先收敛到 `user-story / prd`，再进入 prototype / test-case 主链

### 主链层（Main Chain Layer）
- 目录：
  - `docs/beacon/v1.1.2/user-story/`
  - `docs/beacon/v1.1.2/prd/`
  - `docs/beacon/v1.1.2/qa/test-cases/`
- 角色：正式需求与验证主源
- 约束：
  - workflow / gate 的正式需求输入仍以主链层为核心
  - `test-case` 只能从 `user-story / prd` 收敛而来
  - compat 镜像只允许自动同步，不允许人工双写

### Prototype 层（Visual Prototype Layer）
- 目录：`docs/beacon/v1.1.2/prototype/<feature>/`
- 最低必备工件：
  - `index.html`
  - `manifest.json`
  - `source-map.json`
  - `freeze.json`
- 角色：
  - UI 型需求的可视化参考实现
  - 连接 `prd` 与 `test-case / implementation` 的视觉冻结层
- 约束：
  - 不是生产代码
  - 只能由 `user-story / prd` 派生
  - 仅在 `ui_visualization_required=true` 时成为 gate 强校验对象
  - `freeze` 后若来源指纹漂移，则状态必须为 `stale`

### 交付层（Delivery Layer）
- 目录：`docs/beacon/v1.1.2/execution/`
- 最低必备交付物：
  - `boundaries.md`
  - `beacon-ui-prototype-bootstrap-stack-decision.md`
  - `delivery-manifest.json`（实现期）
  - `change-impact.json`（实现期）
  - `terminal.json`（完整闭环期）
- 角色：
  - 说明默认 UI kit 决策
  - 定义交付范围、变更影响、终态证明与 gate 判定边界

---

## 2. 默认原型技术栈边界

### 2.1 默认 UI Kit（唯一默认栈）
- `Bootstrap 5.3.x`
- `Bootstrap Icons`
- `Beacon Theme CSS`
- `Alpine.js 3.x`
- 少量原生 JS

### 2.2 默认栈职责划分

| 层 | 作用 | 是否默认必选 |
|---|---|---|
| Bootstrap 5.3.x | 组件骨架：导航、Tabs、Modal、Offcanvas、Toast、Form、Grid | 是 |
| Bootstrap Icons | 图标系统 | 是 |
| Beacon Theme CSS | 品牌色、排版、层级、卡片、状态、焦点态 | 是 |
| Alpine.js 3.x | 轻交互状态切换 | 是 |
| 原生 JS | hash 跳转、URL 状态同步、原型状态标记 | 是 |

### 2.3 不作为 v1.1.2 默认栈的选项

| 方案 | 不作为默认的原因 |
|---|---|
| Tailwind（裸） | 更偏样式系统，不是完整现成组件库 |
| Tailwind + daisyUI | 可作为未来实验栈，但当前默认治理复杂度更高 |
| React + Vite | 过重，不适合“静态单页、快速生成、可冻结” |
| Shoelace | 虽适合静态页，但不作为当前默认长期基座 |

---

## 3. In Scope

| 范围 | 描述 | 优先级 |
|------|------|--------|
| Prototype 子命令 | `create / preview / freeze / status / list` | Must |
| 静态单页原型 | 输出 `index.html` 并可直接本地预览 | Must |
| Prototype 冻结治理 | `freeze / stale / source fingerprint` 语义 | Must |
| Workflow 集成 | UI 需求插入 prototype 阶段；非 UI 需求可 skip | Must |
| Gate 校验 | prototype 缺失 / 未冻结 / stale 时阻断 | Must |
| 默认 UI kit 固化 | Bootstrap 5.3.x + Icons + Theme + Alpine | Must |
| 页面能力基线 | 导航、跳转、Modal、Tabs、Offcanvas、Toast、表单、空态/错误态 | Must |
| Web 规范基线 | 语义结构、focus、aria-label、label、reduced-motion | Must |
| 状态可视化 | workflow hud / status / report 展示 prototype 状态 | Must |

## 4. Out of Scope

| 范围 | 原因 |
|------|------|
| 多页完整站点生成器 | v1.1.2 聚焦静态单页原型 |
| 设计师级可编辑画布 | Beacon 仍聚焦可治理交付，不做设计工具 |
| 生产前端代码交付 | prototype 仅为 reference implementation |
| 默认多 UI kit 切换 | 本版固定 Bootstrap 默认栈，避免治理扩散 |
| 研究层直接进入 gate | 会污染正式交付主源 |
| compat 镜像人工维护 | 会造成 docs/beacon 与 docs/product 双写漂移 |

---

## 5. 交付必备项

### 5.1 主链必备项
- `docs/beacon/v1.1.2/user-story/beacon-ui-prototype-lifecycle.md`
- `docs/beacon/v1.1.2/prd/beacon-ui-prototype-lifecycle.md`
- `docs/beacon/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.md`
- `docs/beacon/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.ac-test-matrix.json`（实现期补齐）
- `docs/beacon/v1.1.2/qa/test-cases/beacon-ui-prototype-lifecycle.qa9-matrix.json`（实现期补齐）

### 5.2 Prototype 层必备项（UI 需求开启时）
- `docs/beacon/v1.1.2/prototype/<feature>/index.html`
- `docs/beacon/v1.1.2/prototype/<feature>/manifest.json`
- `docs/beacon/v1.1.2/prototype/<feature>/source-map.json`
- `docs/beacon/v1.1.2/prototype/<feature>/freeze.json`

### 5.3 Delivery 层必备项
- `docs/beacon/v1.1.2/execution/boundaries.md`
- `docs/beacon/v1.1.2/execution/beacon-ui-prototype-bootstrap-stack-decision.md`
- `docs/beacon/v1.1.2/execution/delivery-manifest.json`（实现期）
- `docs/beacon/v1.1.2/execution/change-impact.json`（实现期）

---

## 6. Done Criteria

| 条件 | 验证方式 |
|------|----------|
| 主链需求物料齐全 | User Story / PRD / Test Cases 均存在 |
| 默认 UI kit 决策固化 | execution 决策文档存在并明确 Bootstrap 默认栈 |
| prototype 具备可治理语义 | PRD / US / TC 已定义 create / freeze / stale / gate 语义 |
| workflow 阶段边界明确 | prototype 仅对 UI 需求启用，非 UI 可 skip |
| 页面能力边界明确 | 文档已定义导航 / Modal / Tabs / Offcanvas / 表单等基线 |
| 规范边界明确 | 文档已定义语义结构 / focus / aria / label / reduced-motion |

## 7. Blocked Criteria

| 条件 | 状态 |
|------|------|
| `ui_visualization_required=true` 但 prototype 工件缺失 | Blocked |
| `freeze.json` 缺失或不是 `frozen` | Blocked |
| prototype 已 stale | Blocked |
| prototype 来源无法追溯到 `user-story / prd` | Blocked |
| prototype 使用未授权默认栈替代 Bootstrap 默认栈 | Blocked / Design Contract Failed |
| 主链文档缺失（US / PRD / TC） | Blocked |

## 8. Reason Codes（Prototype / Delivery）

| Code | 说明 | 阻断级别 |
|------|------|---------|
| prototype_missing | prototype 工件缺失 | Blocked |
| prototype_not_frozen | prototype 未冻结 | Blocked |
| prototype_stale | prototype 来源已漂移 | Blocked |
| prototype_source_untraceable | 无法追溯来源主链文档 | Blocked |
| prototype_ui_contract_failed | 默认 UI 组件能力或主题层不满足约束 | Blocked |
| prototype_accessibility_contract_failed | prototype 不满足基础 Web 规范 | Blocked |
| main_chain_incomplete | user-story / prd / test-case 缺失 | Blocked |

## 9. 当前 v1.1.2 交付范围（本稿）

- Source of Truth: `docs/beacon/v1.1.2/`
- Default UI Kit: `Bootstrap 5.3.x`
- Prototype Theme: `Beacon Theme CSS`
- Prototype State Layer: `Alpine.js 3.x`
- Affected Project: `beacon`
- Current Worktree: `/Users/apple/Developer/Personal/my_skill/beacon`
- Status: `Draft / Requirement Materials Only`

---

**说明**：本边界文档用于定义 v1.1.2 的研究层 + 主链层 + prototype 层 + 交付层闭环规则；本轮已完成需求物料与默认栈决策固化，源码实现与交付执行工件仍待后续迭代补齐。
