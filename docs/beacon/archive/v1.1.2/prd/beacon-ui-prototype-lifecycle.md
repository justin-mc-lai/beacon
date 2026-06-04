# PRD: Beacon 静态 UI Prototype（Bootstrap 默认栈）生成、冻结治理与 Workflow 集成（v1.1.2）

## 1. 目标

将 Beacon 从“需求主链文档治理工具”扩展为“需求主链 + UI 可视化参考实现”的交付系统，并在 v1.1.2 明确默认原型栈为 **Bootstrap 5.3.x**，确保：

1. UI 型需求可从 `user-story / prd` 生成可运行的静态单页 prototype。
2. prototype 作为正式工件进入 workflow 生命周期与 gate 治理。
3. prototype 能被 freeze，并与来源文档建立强指纹绑定，防止视觉意图漂移。
4. 生成结果可直接本地运行查看，作为后续 `test-case / implementation` 的参考实现。
5. 新能力继续遵守 `docs/beacon/<version>/` 为唯一 source 的目录治理规则。
6. 默认原型在“可快速运行”的同时，具备基础设计层与基础可访问性，不仅仅是控件堆叠页。

## 2. 背景

当前 Beacon 主链已覆盖：

`think -> user-story -> prd -> test-case -> implementation -> verify -> gate`

在 v1.1.2 的 prototype 需求收敛中，组件栈经过 Tailwind 与 Bootstrap 的比较，结论如下：

1. Beacon prototype 的目标是 **静态单页、快速生成、带弹窗跳转、可冻结、可治理**。
2. Tailwind 更像样式系统，不是完整现成组件库；若作为默认方案，仍需要额外叠加组件层与治理约束。
3. Bootstrap 5.3.x 自带成熟的导航、Tabs、Modal、Offcanvas、Toast、Dropdown、Form 等组件，更适合作为静态单页原型默认底座。
4. 通过 Beacon Theme CSS 可以降低“裸 Bootstrap 感”，同时保留 Bootstrap 的稳定组件能力与治理优势。
5. 因此 v1.1.2 需要在需求物料中正式固化：**Bootstrap 是 Beacon prototype 的默认 UI kit**。

## 3. 范围

### In Scope

1. 新增 `prototype` 子命令组。
2. 生成静态单页 HTML 原型。
3. prototype 工件目录与 manifest / freeze / source-map 规范。
4. workflow 集成 prototype 阶段。
5. gate 对 prototype 缺失、未冻结、stale 的阻断逻辑。
6. prompt / ask / router 对 prototype 意图的识别。
7. prototype 状态进入 status / hud / report。
8. verify 阶段对 prototype 做基础 smoke 校验。
9. 默认 UI kit 固化为 `Bootstrap 5.3.x + Bootstrap Icons + Beacon Theme CSS + Alpine.js`。
10. prototype 模板默认具备基础导航、弹窗、抽屉、标签切换、表单交互、空态/错误态。

### Out of Scope

1. 不实现多页完整站点生成器。
2. 不实现设计师级视觉编辑器。
3. 不引入 React / Vite / Figma 依赖作为默认运行方式。
4. 不把 prototype 直接作为生产前端代码交付。
5. 不要求所有需求都启用 prototype；仅对 UI 型需求强制。
6. 不在 v1.1.2 默认支持多套 UI kit 动态切换；Bootstrap 为唯一默认栈。

## 4. 功能需求

### FR-001 Prototype 子命令组

新增：

- `beacon prototype create <feature>`
- `beacon prototype preview <feature>`
- `beacon prototype freeze <feature>`
- `beacon prototype list`
- `beacon prototype status <feature>`

要求：
- 命令风格与现有 Beacon 子命令一致。
- 支持 `--project`、`--version`、`--output` 等标准参数。
- `create` 默认从当前版本下的 `user-story / prd` 自动解析。

### FR-002 Prototype 输出目录

prototype 统一输出到：

```text
docs/beacon/<version>/prototype/<feature>/
```

最小工件：

- `index.html`
- `manifest.json`
- `source-map.json`
- `freeze.json`
- `README.md`（可选）
- `screenshots/`（可选）

### FR-003 静态单页 HTML 生成

`prototype create` 必须生成一个可运行的单页原型，满足：

- 单 HTML 文件；
- 无复杂构建步骤；
- 本地快速打开可查看；
- 至少包含页面标题、核心信息区、主 CTA、主要状态区、基础交互元素；
- 页面明确标注“Reference Prototype / 非生产代码”。

### FR-004 来源映射

prototype 必须记录来源映射：

- 来源 user-story 路径
- 来源 PRD 路径
- 来源指纹（sha256）
- 页面结构到需求字段的映射关系

`source-map.json` 至少记录：
- `feature`
- `version`
- `source_refs`
- `source_fingerprints`
- `sections[]`
- `derived_from[]`

### FR-005 Freeze 机制

`prototype freeze` 必须：

1. 记录当前来源文档指纹；
2. 记录当前 `index.html` 指纹；
3. 将 prototype 状态设置为 `frozen`；
4. 当来源文档后续变化时，prototype 状态自动变为 `stale`。

`freeze.json` 至少记录：
- `status: frozen|stale|draft`
- `frozen_at`
- `source_fingerprints`
- `artifact_fingerprints`
- `generator_version`
- `ui_kit: bootstrap-5.3.x`

### FR-006 Workflow 集成

当需求为 UI 型时，workflow 支持 prototype 阶段：

```text
think -> user-story -> prd -> prototype -> test-case -> implementation -> verify -> gate
```

当需求非 UI 型时：
- prototype 阶段自动 `skipped`
- lifecycle 记录 skip reason
- gate 不因 prototype 缺失而阻断

### FR-007 UI 需求声明

Beacon 需要支持在主链中声明 UI 需求属性，例如：

- `ui_visualization_required: true|false`
- `prototype_mode: static-single-page`
- `prototype_freeze_required: true|false`
- `prototype_ui_kit: bootstrap-5.3.x`

来源建议：
- user-story metadata
- prd metadata
- workflow start 参数

### FR-008 Intent Routing

`prompt optimize` / `ask` 必须新增 prototype intent，识别关键词：

- prototype
- 交互原型
- 可点击原型
- UI 原型
- 单页原型
- html prototype

并避免被当前 `design` 意图误吸收。

### FR-009 Gate 阻断规则

当 `ui_visualization_required=true` 时，gate 必须校验：

1. `index.html` 存在；
2. `manifest.json` 存在；
3. `freeze.json.status == frozen`；
4. prototype 非 stale；
5. 来源链可追溯到 `user-story / prd`。

任一失败 ⇒ BLOCKED。

建议 reason code：
- `prototype_missing`
- `prototype_not_frozen`
- `prototype_stale`
- `prototype_source_untraceable`

### FR-010 Verify 阶段最小原型校验

verify 应支持对 prototype 做最小 smoke：
- 页面能打开
- DOM 主结构存在
- console 无阻断级错误
- 基础交互元素存在
- 页面头部带 reference 标签
- Modal / Offcanvas / Tabs / 导航跳转可执行基础交互检查

### FR-011 Report / HUD / Status 展示

以下命令必须可感知 prototype 状态：
- `workflow hud`
- `workflow status`
- `status --board`
- `report`

至少展示：
- enabled / skipped
- draft / frozen / stale
- source hash 状态
- ui kit 信息
- gate blocking 状态

### FR-012 默认 UI Kit 固化

v1.1.2 明确默认 prototype UI kit 为：

- **Bootstrap 5.3.x**
- **Bootstrap Icons**
- **Beacon Theme CSS**
- **Alpine.js 3.x**

要求：
- Bootstrap 提供基础组件能力；
- Beacon Theme CSS 负责品牌色、排版、层级、卡片、阴影、焦点态、状态色与布局密度；
- Alpine.js 负责轻交互状态，不引入重型框架。

### FR-013 Prototype 页面组件能力

默认模板至少支持：

- 顶部导航 / 区块跳转
- 主 CTA / 次 CTA
- Tabs / Pills
- Modal
- Offcanvas / Drawer
- Toast / Inline Alert
- 表单输入 / 校验提示
- Empty / Loading / Error / Success 状态区
- 信息卡片 / 列表 / 指标块

### FR-014 Prototype 页面质量约束

默认模板必须满足：

- 语义化 HTML：`header / nav / main / section / footer / form`
- 图标按钮具备 `aria-label`
- 表单具备 label 与基础可达性
- 可见 focus ring，不允许裸移除 outline
- 支持 `prefers-reduced-motion`
- 长文本、空态、错误态与滚动容器有基础处理
- 避免裸默认 Bootstrap 视觉，必须注入 Beacon 主题层

## 5. 非功能要求

### 性能
- `prototype create` 默认应在数秒内完成。
- 无需安装前端依赖即可运行原型。

### 兼容性
- macOS / Linux / Windows 可使用浏览器直接查看；
- 支持 `file://` 或 `python -m http.server` 快速预览。

### 可维护性
- 默认 stack 不依赖复杂前端构建；
- 单文件 HTML 结构稳定，可回归测试；
- 生成器模板可版本化。

## 6. 技术方案

### 6.1 默认 HTML 技术栈（最终）

为兼顾“快速运行 / 设计基础 / 开源成熟度 / 弹窗跳转等组件能力”，v1.1.2 默认推荐：

- **HTML5**：语义化结构
- **Bootstrap 5.3.x**：默认 UI 组件库（导航、Tabs、Modal、Offcanvas、Dropdown、Toast、Form、Layout）
- **Bootstrap Icons**：图标系统
- **Beacon Theme CSS**：基于 CSS Variables 覆盖品牌色、排版、阴影、圆角、密度、状态色
- **Alpine.js 3.x**：处理轻交互状态，如筛选、局部显隐、步骤切换、轻量状态机
- **少量原生 JS**：hash 跳转、section 切换、prototype 状态标记

### 6.2 为什么不是 Tailwind 默认栈

1. Tailwind 更偏样式系统，不是现成完整组件库。
2. 若采用 Tailwind，通常还需要再配组件层（如 daisyUI / Headless UI），复杂度更高。
3. Bootstrap 对静态单页、快速生成、可冻结与可治理更友好。
4. Bootstrap 组件能力更直接覆盖 Modal / Offcanvas / Tabs / Navbar / Form 等 Beacon 原型需求。

### 6.3 设计层要求

为避免 prototype 退化为“裸 Bootstrap 控件页”，模板应吸收高质量前端设计原则：

- 清晰的视觉主次与版式节奏
- 有辨识度但可复用的品牌色与中性色体系
- 标题、正文、说明、标签、状态文案的层级规范
- 卡片、面板、分组区块、空态、错误态的统一视觉语言
- hover / active / focus / disabled / loading 的细节表现

### 6.4 Web 规范要求

默认模板应吸收 Web Interface Guidelines 的关键约束：

- 语义化结构优先
- 图标按钮必须有文本语义或 aria-label
- 表单必须有 label
- focus 样式可见
- 动画尊重 reduced motion
- 交互组件不可造成滚动/焦点陷阱失控

## 7. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| prototype 漂移 | gate 误判或评审失真 | freeze + stale detection |
| design 与 prototype 意图冲突 | 路由错误 | 新增独立 prototype intent |
| 页面能看但需求映射不清 | 交付不可追溯 | source-map.json 强制生成 |
| 默认 Bootstrap 视觉过于通用 | 原型不够有辨识度 | 增加 Beacon Theme CSS 与模板设计层 |
| 组件过多导致模板复杂 | 生成不稳定 | 先限定组件清单与可选状态集 |

## 8. 成功指标

1. UI 型需求可在主链中生成可运行 prototype。
2. 相关工件全部落盘到 `docs/beacon/archive/v1.1.2/prototype/...`。
3. workflow / gate / report 能正确表达 prototype 状态。
4. 至少一组 contract tests 覆盖：
   - command
   - routing
   - workflow stage
   - gate blocking
   - freeze / stale
   - bootstrap stack contract
5. 不重新引入 `docs/product` 作为人工维护路径。
