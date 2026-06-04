# 版本规划：Beacon v1.1.8 Prototype / Debug / QA / Implement / Init 五线并行演进

## 版本定位

- target_version: `v1.1.8`
- base_version: `v1.1.7`
- strategy: `bump:patch`
- owner: `Beacon Team`
- generated_at: `2026-03-25`

## 当前实现状态

- 人类物料：已齐备
- machine 物料：已齐备
- 代码实现：已落地
- formal spec review：`5/5 pass`
- acceptance：已完成

## 目标与范围

- 主题：在 v1.1.8 同时推进 prototype baseline、runtime debug feedback、qa/browser acceptance、implement 技术归档、init 架构主入口五条设计线
- 目标：
  1. 解决原型冻结后无法约束真实实现的问题
  2. 解决实践项目中 Beacon skill 生命周期缺少实时产品反馈的问题
  3. 解决 `auto-test` 仍停留在旧命令心智、缺少登录态保存与状态化浏览器验收的问题
- 范围：
  - prototype baseline / implementation binding / verify-impl / prototype debug
  - runtime debug feedback / debug directory / issue & idea harvesting
  - qa primary surface / auto-test alias / session persistence / agent-browser/browser-use acceptance
  - implement technical archive / code-db-api-config summary / multi-service technical archive
  - init progressive disclosure / architecture blueprint / version evolution blueprint / implementation archive index

## 版本演进动机

真实问题来源：

- `products/milemon/docs/beacon/v0.1.0/prototype/site-visual-system/theme.json` 已冻结品牌主色 `#F26522` 与辅助色 `#1E4D8C`；
- 真实实现位于 `wp-content/themes/milemon/`，其中 `assets/css/design-tokens.css`、`style.css`、`front-page.php`、`header.php`、`woocommerce/*.php` 才是最终交付路径；
- 当前 Beacon 没有把 prototype surface / theme token 绑定到这些实现文件，因此无法判断“实现是否真的按原型落地”。
- 本地 gstack 源码直接分析还表明：
  - gstack 已把 `/qa`、浏览器 daemon、cookie 导入、session 复用、field report 做成正式能力；
  - Beacon 在这些点上仍存在明显产品化差距；
  - 详细差距矩阵已沉淀在 `docs/beacon/archive/v1.1.8/research/gstack-gap-analysis.md`。

## 本版输出目标

### 线 A：Prototype Baseline
1. Beacon 支持 **Prototype Baseline Manifest**
2. Beacon 支持 **Implementation Binding Manifest**
3. Beacon 支持 **Theme / Style / Effect token 映射**
4. Beacon 支持 **Prototype ↔ Implementation Verify**
5. Beacon 支持 **类似 gstack 的 prototype debug 修复闭环**
6. 以 `milemon` 作为真实样板验证通用性，但不写死到 WordPress

### 线 B：Runtime Debug Feedback
7. Beacon Debug 支持 **实践项目实时反馈**
8. Beacon Debug 支持 **debug 目录聚合 issue / idea**
9. Beacon Debug 支持 **直接服务版本迭代 planning**

### 线 C：QA Command Evolution
10. Beacon 支持 **`qa` 作为正式主入口**
11. Beacon 保留 **`auto-test` 兼容 alias**
12. Beacon 支持 **登录态保存 / session 治理**
13. Beacon 支持 **agent-browser / browser-use 的真实浏览器验收**
14. Beacon 支持 **需求演进式测试**

### 线 D：Implement Technical Archive
15. Beacon 支持 **technical-implementation 文档归档**
16. Beacon 支持 **代码 / CRUD / DB / API / config / risk 的结构化技术归档**
17. Beacon 支持 **多服务实现归档**

### 线 E：Init Architecture Entry
18. Beacon init 支持 **greenfield / takeover 模式语义**
19. Beacon init 支持 **渐进式披露 AGENTS 主入口**
20. Beacon init 支持 **architecture blueprint / version evolution blueprint / implementation archive index**

## 五线之间的递进关系

这五条线应该被理解为两层结构：

### 1. 项目接入层
- `Init Architecture Entry`
- `Runtime Debug Feedback`

### 2. 交付闭环层
- `Prototype Baseline`
- `Implement Technical Archive`
- `QA Command Evolution`

换句话说：

- `init` 负责把项目接进 Beacon
- `prototype / implement / qa` 负责接管需求交付
- `debug` 负责把真实使用反馈回流到下一轮版本演进

## 版本接管链

v1.1.8 更准确的目标，不是“多补 5 个功能点”，而是建立一个更完整的接管链：

```text
beacon init
→ project onboarding / architecture blueprint / version evolution blueprint
→ prototype baseline
→ implement + technical archive
→ qa + browser evidence + session
→ gate / release
→ debug feedback / issue / idea
→ next version planning
```

## 每条线的主要输入 / 输出

| 设计线 | 主要输入 | 主要输出 | 下游使用方 |
| --- | --- | --- | --- |
| Init Architecture Entry | 项目根目录、runtime version、context files | onboarding、architecture blueprint、version blueprint、AGENTS 渐进式披露 | prototype / implement / qa / help / doctor |
| Prototype Baseline | PRD / User Story / Prototype Contract | baseline、binding、verify-impl、prototype debug | implement / qa / review |
| Implement Technical Archive | implement run result、changed_files、verification | technical archive、implementation archive index | qa / review / evolution-summary |
| QA Command Evolution | test-case / profile / session / browser runner | qa status、browser evidence、delta test evolution | gate / release / report |
| Runtime Debug Feedback | 真实项目生命周期运行事件 | issue / idea / friction archive | 下一轮 version planning |

## 追溯

建议后续继续补：

### Prototype
- `beacon prototype baseline <feature>`
- `beacon prototype bind <feature> --adapter <adapter>`
- `beacon prototype verify-impl <feature>`
- `beacon prototype debug <feature> --watch`

### Debug
- `beacon debug project-feed <feature>`
- `beacon debug harvest`
- `beacon debug export-ideas`

### QA
- `beacon qa run`
- `beacon qa session save`
- `beacon qa evolve <feature>`

### Implement Archive
- `beacon implement run <feature> -> technical-implementation-<feature>.{json,md}`

### Init
- `beacon init --project-mode greenfield`
- `beacon init --project-mode takeover`

## 推荐实现顺序

如果后续进入编码实现，最推荐的顺序是：

1. `init-progressive-architecture-blueprint`
   - 先把项目接入和主入口建立好
2. `qa-command-browser-acceptance`
   - 解决主用户面、session、browser evidence
3. `debug-runtime-feedback-loop`
   - 让真实使用开始反哺 Beacon
4. `implement-technical-architecture-archive`
   - 补强技术归档和版本演进事实源
5. `prototype-baseline`
   - 最后把 UI/实现防漂移闭环做严

原因：
- `init` 和 `qa/debug` 更接近项目接管入口
- `implement/prototype` 更接近交付细化层
