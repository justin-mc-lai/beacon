# Beacon UI Prototype 默认 Bootstrap 栈与参考实现架构决策（v1.1.2）

## 1. 结论

Beacon 原型默认选 **Bootstrap 5.3.x**，不是因为它最潮，而是因为它最适合以下交付场景：

- 静态单页
- 快速生成
- 带弹窗跳转
- 可冻结
- 可治理

v1.1.2 的默认 prototype 栈定案如下：

- **Bootstrap 5.3.x**
- **Bootstrap Icons**
- **Beacon Theme CSS**
- **Alpine.js 3.x**
- **少量原生 JS**

## 2. 为什么不是 Tailwind 默认栈

经过对比，Tailwind 在以下方面不如 Bootstrap 适合作为 Beacon prototype 默认栈：

1. **Tailwind 更偏样式系统，不是现成组件库**。
2. 若采用 Tailwind，通常还需要再配组件层（如 daisyUI / Headless UI），复杂度更高。
3. Beacon prototype 需要的是“快速稳定输出、组件能力直接可用、DOM 结构容易治理”，而不是最高自由度。
4. 对 freeze / stale / gate / verify 来说，Bootstrap 的结构化组件更稳定。

## 3. 默认栈职责分工

### 3.1 Bootstrap 5.3.x

负责：
- Navbar / Nav / Tabs
- Modal
- Offcanvas / Drawer
- Dropdown
- Toast
- Form Controls
- Grid / Layout

### 3.2 Bootstrap Icons

负责：
- 常规导航图标
- 状态图标
- CTA / 空态 / 列表图标

### 3.3 Beacon Theme CSS

负责：
- 品牌色与状态色
- 排版层级
- 卡片 / 面板 / 指标块样式
- 圆角 / 阴影 / 边框体系
- Focus ring / hover / active / disabled / loading 样式
- 空态 / 错误态 / 提示态统一视觉

### 3.4 Alpine.js 3.x

负责：
- 局部显隐
- 步骤状态切换
- 轻量过滤与切页
- prototype 内部小型状态机

### 3.5 原生 JS

负责：
- hash 跳转
- URL 状态同步
- prototype 状态角标 / 标签注入
- preview 辅助逻辑

## 4. Prototype 页面能力基线

默认模板应具备以下 UI 能力：

1. 顶部导航与区块跳转
2. 主 CTA / 次 CTA
3. 指标卡片 / 列表 / 表单布局
4. Tabs / Pills 切换
5. Modal 弹窗
6. Offcanvas / Drawer
7. Toast / Alert
8. Empty / Loading / Error / Success 状态区

## 5. 设计质量要求

为了避免 prototype 退化为“裸 Bootstrap 控件页”，必须满足：

1. 页面有明确的信息层级与版式节奏。
2. 主题层必须覆盖 Bootstrap 默认主色与关键变量。
3. 页面要具备基础“产品原型感”，而非单纯组件演示页。
4. 重点交互元素（按钮、切换、弹层、表单）要有状态反馈。
5. 页面首屏要能体现当前需求的核心目标与主流程入口。

## 6. Web 规范要求

默认模板应内置以下规则：

- 使用 `header / nav / main / section / footer / form` 等语义标签
- 图标按钮带 `aria-label`
- 表单带 `label`
- focus 可见，不允许完全去除 outline
- 尊重 `prefers-reduced-motion`
- 基础弹层与抽屉不制造明显焦点/滚动陷阱

## 7. 与 Workflow / Gate 的关系

Bootstrap 默认栈被选为 Beacon prototype 底座后，治理语义如下：

- `prototype create` 生成基于 Bootstrap 的静态单页 reference implementation
- `prototype freeze` 冻结其来源指纹与 HTML 指纹
- `verify` 校验 DOM / console / 交互 smoke
- `gate` 在 `ui_visualization_required=true` 时校验 prototype 是否存在、冻结、未 stale

## 8. 后续扩展

v1.1.2 不默认开放多 UI kit 模式，但后续可扩展：

- `prototype_ui_kit=bootstrap`（默认）
- `prototype_ui_kit=tailwind-daisyui`（未来实验栈）
- `prototype_theme=dashboard/mobile-app/b2b-console`（未来主题档位）

原则：
- 默认栈以治理稳定为先
- 扩展栈以表达力增强为辅

## 9. 本轮对外口径

> Beacon 原型默认选 Bootstrap，不是因为它最潮，而是因为它最适合“静态单页、快速生成、带弹窗跳转、可冻结、可治理”的交付场景。
