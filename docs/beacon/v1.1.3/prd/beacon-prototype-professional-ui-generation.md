# PRD: Beacon 原型子命令升级为专业 UI 原型生成（v1.1.3）

## 1. 目标

在 v1.1.3 需求层正式定义 `beacon prototype` 的下一阶段能力边界，使它从“静态 Bootstrap 单页生成器”升级为“基于 PRD + User Story 的 Prototype Contract 驱动的专业 UI 参考实现生成器”，确保：

1. 原型不再只是 generic shell，而是真实表达需求结构、主题、导航、CTA 与状态；
2. 原型从创建、review、freeze 到 gate 成为完整闭环；
3. 原型产物可被 `test-case / workflow / gate / report` 消费；
4. 当前阶段是需求草稿阶段，允许与 v1.1.2 代码实现存在差距。

## 2. 背景

当前 `beacon/beacon/commands/prototype.py` 与 `prototype_utils.py` 已具备：

- `create / preview / freeze / status / list`
- `index.html / manifest.json / source-map.json / freeze.json`

但当前实现仍有明显限制：

1. `prototype create` 主要基于 `user-story / prd` 前几行文本 preview 拼装页面；
2. 生成结果更像通用 Bootstrap 演示页，而不是需求对齐的专业原型；
3. 当前没有设计意图层、导航契约层、交互契约层；
4. 当前缺少 `prototype review` 阶段，导致原型是否真正覆盖需求只能人工判断；
5. 当前 `test-case / gate` 还不能消费导航/交互 contract。

从第一性原理看，原型子命令真正要回答的是：

1. 这个需求的目标用户是谁；
2. 用户要完成什么关键路径；
3. 页面结构和导航应该如何组织；
4. 点击后跳到哪里、为什么跳；
5. 页面应该呈现什么专业气质，而不是默认蓝色 Bootstrap 壳子。

## 3. 范围

### In Scope

1. 用 PRD + User Story 中的结构化 Prototype Contract 作为原型生成输入；
2. 为 `prototype create` 增加专业原型所需的主题/导航/交互产物；
3. 新增 `prototype review` 子命令；
4. 让 workflow/gate/test-case 消费原型 contract；
5. 保持 `docs/beacon/<version>/prototype/<feature>/` 为唯一产物根目录；
6. 明确当前为需求草稿阶段，不要求与文档同步完成功能实现。

### Out of Scope

1. 不引入前端构建系统（React/Vite）作为默认原型方案；
2. 不引入设计师级可编辑画布；
3. 不把原型直接当作生产前端代码；
4. 不新增与原型无关的 PM 模板命令；
5. 不通过模糊兜底生成 generic 页面来掩盖需求结构缺失。

## 4. Prototype Contract 设计

### 4.1 PRD / User Story 必须承载的结构化字段

原型生成至少应读取以下 contract：

#### A. 页面原型类型
- `prototype_archetype`
  - `dashboard`
  - `list-detail`
  - `form-wizard`
  - `marketing-page`
  - `admin-workbench`
  - `mobile-task-flow`

#### B. 设计意图
- `theme_mood`
- `brand_keywords`
- `theme_primary`
- `theme_secondary`
- `surface_style`

#### C. 信息架构
- `screens / sections`
- `navigation`
- `primary_entry`
- `primary_exit`

#### D. 交互与跳转 contract
- `primary_cta`
- `secondary_cta`
- `jump_map`
- `modal_map`
- `drawer_map`
- `tab_map`

#### E. 状态 contract
- `empty`
- `loading`
- `error`
- `success`
- `permission`
- `stale / review-needed`

### 4.2 Fail-fast 规则

当关键 contract 缺失时：

- `prototype create` 必须直接失败；
- 不允许回退为“读文本前几行然后猜一个页面”；
- 必须输出明确的缺失字段说明，要求先补全 PRD / User Story 结构化内容。

## 5. 功能需求

### FR-001 保留现有命令组并升级语义

保留：
- `prototype create`
- `prototype preview`
- `prototype freeze`
- `prototype status`
- `prototype list`

新增：
- `prototype review`

### FR-002 `prototype create` 必须基于 Prototype Contract 生成

- 从 PRD + User Story 读取结构化 contract；
- 根据 archetype 生成对应的真实页面框架；
- 页面标题、CTA、跳转、状态区不能再使用 generic placeholder。

### FR-003 输出专业原型所需的新产物

除现有：
- `index.html`
- `manifest.json`
- `source-map.json`
- `freeze.json`

还必须新增：
- `prototype-brief.json`
- `theme.json`
- `navigation-map.json`
- `interaction-map.json`

### FR-004 `prototype-brief.json`

至少记录：
- `feature`
- `version`
- `prototype_archetype`
- `target_user`
- `primary_flow`
- `primary_cta`
- `design_intent`

### FR-005 `theme.json`

至少记录：
- primary / secondary / accent color
- typography scale
- spacing scale
- radius
- shadow
- motion strategy
- light/dark strategy

### FR-006 `navigation-map.json`

至少记录：
- sections / screens
- navigation nodes
- entry / exit
- jump target
- jump rationale

### FR-007 `interaction-map.json`

至少记录：
- CTA
- modal
- drawer
- tabs
- toast
- form actions
- state transitions

### FR-008 原型必须是“真实页面”，不是“组件展示页”

原型必须做到：
- 页面标题来自需求；
- CTA 文案来自需求；
- 跳转说明来自需求；
- 页面结构与 archetype 相匹配；
- 主题风格来自 design intent，而不是默认蓝色 Bootstrap 壳子。

### FR-009 `prototype review` 子命令

新增：
- `beacon prototype review <feature>`

它至少检查：
1. 需求覆盖
2. 信息架构完整性
3. CTA / jump 完整性
4. 状态覆盖
5. 设计一致性
6. 可访问性
7. AI slop 风险

### FR-010 `prototype review` 输出

至少输出：
- `prototype-review.json`
- `prototype-review.md`

### FR-011 Workflow 集成

当 `ui_visualization_required=true` 时，prototype 阶段的完整链条应被视为：

- `prototype create`
- `prototype review`
- `prototype freeze`

而不是只 create 后直接 freeze。

### FR-012 Gate 集成

当 `ui_visualization_required=true` 时，gate 除检查 freeze 外，还应检查：
- `theme.json`
- `navigation-map.json`
- `interaction-map.json`
- `prototype-review` 产物

### FR-013 Test-case 集成

`test-case create` 应能读取：
- `navigation-map.json`
- `interaction-map.json`

以生成：
- CTA 跳转用例
- 状态覆盖用例
- UI smoke 用例

### FR-014 可访问性与专业设计约束继续保留

原型仍必须满足：
- 语义化结构
- 可见 focus
- aria-label
- form label
- reduced motion
- 空态/错误态/滚动容器基础处理

### FR-015 当前阶段记录

必须明确：
- 当前 v1.1.3 仍是 requirement materials draft；
- 现有 `prototype.py` 尚未具备上述完整能力是正常现象；
- 当前验收重点是：需求结构冻结，而不是功能已完成。

## 6. 代码调整点（需求层冻结）

未来实现期最短路径应聚焦：

### `beacon/beacon/commands/prototype.py`
- 重构 `create` 语义；
- 新增 `review`；
- `status` 展示 theme/navigation/interaction/review 状态。

### `beacon/beacon/utils/prototype_utils.py`
当前问题函数：
- `_doc_preview()`
- `_build_section_cards()`
- `render_bootstrap_prototype_html()`

未来应增加：
- `extract_prototype_contract_from_user_story()`
- `extract_prototype_contract_from_prd()`
- `merge_prototype_contract()`
- `derive_theme_tokens()`
- `derive_navigation_map()`
- `derive_interaction_map()`
- `render_professional_prototype_html()`
- `review_prototype_bundle()`

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 继续用 generic shell 假装原型 | 需求失真 | contract 缺失即 fail-fast |
| 原型表达很完整但无法验证 | review 缺位 | 新增 `prototype review` |
| 原型与测试/门禁断开 | 交付脱节 | 让 gate/test-case 消费 contract |
| 设计意图仍然无法冻结 | 风格漂移 | `theme.json + prototype-brief.json` |
| 当前未实现被误判为版本失败 | 认知噪音 | 明确 requirement draft 阶段语义 |

## 8. 成功指标

- prototype 从“generic Bootstrap 单页”升级为“需求对齐的专业 UI 原型”；
- CTA、跳转、状态、主题都有结构化 contract；
- workflow/gate/test-case 能消费 prototype contract；
- 当前需求物料明确记录：v1.1.3 仍是草稿阶段，未实现正常。

## 9. Prototype Contract Draft

ui_visualization_required: true
prototype_archetype: admin-workbench
target_user: product manager
theme_mood: trusted
theme_primary: #2563eb
theme_secondary: #111827
brand_keywords: trust, delivery, visibility
surface_style: elevated-clean
sections: Overview, Contract, Review
navigation: Overview, Contract, Review
primary_entry: Overview
primary_exit: Review
primary_cta: Review prototype contract
secondary_cta: Freeze approved prototype
jump_map: Overview->Contract: Inspect structured contract; Contract->Review: Validate completeness
modal_map: Review summary modal
drawer_map: Contract details drawer
tab_map: Overview, Contract, States
states: empty, loading, error, success, review-needed
