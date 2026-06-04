# Beacon v1.1.8 Summary

**主题**: prototype、debug、qa、implement 归档、init 蓝图五线并行设计  
**状态**: Implemented and Release-Ready  
**日期**: 2026-03-25

---

## 本版目标

v1.1.8 现在包含五条并行设计线：

1. `prototype-baseline`
2. `debug-runtime-feedback-loop`
3. `qa-command-browser-acceptance`
4. `implement-technical-architecture-archive`
5. `init-progressive-architecture-blueprint`

其中第一条线不再把 `beacon prototype` 只当成“静态参考页生成器”，而是把它升级为：

> **需求原型基线（Prototype Baseline）→ 实现绑定（Implementation Binding）→ 差异校验（Verify Impl）→ Debug 修复闭环**

核心问题来自真实实践：

- 当前 Beacon prototype 可以生成 `index.html / theme.json / source-map.json / freeze.json` 等工件；
- 但它只对 **需求文档** 做 freeze，不对 **实际实现代码** 做绑定与校验；
- 因此像 `products/milemon` 这种项目里，原型与真实实现可以长期分叉，Beacon 也无法自动发现。

---

## 当前结论

当前 `beacon prototype` / `debug` / `auto-test` 已具备：

- contract-driven static prototype generation
- prototype review / freeze / status
- theme / navigation / interaction contract 输出
- prompt / run debug feedback capture
- QA9 / layer command / browser runner selection / auto-test status

但仍缺少：

1. **原型基线定义**：缺少可被实现阶段消费的正式 baseline manifest；
2. **实现绑定**：缺少“某个原型 surface 对应哪些 route / template / component / CSS token”的绑定关系；
3. **原型 ↔ 实现校验**：缺少视觉、语义、交互、token、effect 多层 diff；
4. **开发期 debug 闭环**：缺少类似 gstack 的 mismatch watch / rerun / 修复建议机制。
5. **原型自身设计基线**：基于 `frontend-design` + `web-design-guidelines` 审计，当前 generator 仍存在 generic typography、模板化 card shell、generic CTA 与 Web UI 语义缺口。
6. **实践项目 runtime debug 反馈**：当前 debug 还不能把实践项目中深度使用 Beacon skill 生命周期的真实摩擦沉淀为 Beacon 自身版本迭代输入。
7. **QA 主入口与状态化验收**：当前 `auto-test` 还未升级为 `qa` 主入口，也缺少登录态保存、session 治理、需求演进式测试与 `agent-browser/browser-use` 的正式闭环。
8. **implement 技术归档面**：当前 implementation-summary 更像执行摘要，还不足以给技术接手/复盘使用。
9. **init 技术主入口面**：当前 init 仍偏建目录与 managed block，不足以建立架构主文档、演进蓝图与渐进式披露主入口。

---

## 五条设计线的关系图

这五条线不是并排孤立存在，而是分成两个层级：

### A. 项目接管入口层
1. `init-progressive-architecture-blueprint`
   - 负责把项目接入 Beacon
   - 建立主入口、架构蓝图、版本演进蓝图、接管级别

2. `debug-runtime-feedback-loop`
   - 负责把真实使用摩擦回流到 Beacon 本体迭代
   - 是“运行中的产品反馈层”

### B. 需求交付闭环层
3. `prototype-baseline`
   - 负责定义 UI/原型基线，约束实现不漂移

4. `implement-technical-architecture-archive`
   - 负责把实现结果转成技术归档，服务接手/复盘/风险审计

5. `qa-command-browser-acceptance`
   - 负责真实浏览器验收、登录态保存、需求演进式测试、gate 输入

可以概括为：

```text
init
→ 建立项目主入口 / 架构蓝图 / 接管状态
→ prototype / implement / qa 三条交付线开始运转
→ debug 持续吸收真实使用摩擦
→ 反馈回下一轮 version planning
```

---

## 五线依赖关系

| 设计线 | 主要输入 | 主要输出 | 服务哪条线 |
| --- | --- | --- | --- |
| init-progressive-architecture-blueprint | 项目根目录、当前版本、上下文文件 | architecture blueprint、version blueprint、project onboarding、AGENTS 渐进式披露 | 为全部后续设计线提供项目级主入口 |
| prototype-baseline | PRD / User Story / Prototype Contract | baseline、binding、verify-impl、prototype debug | 为 implement / qa 提供 UI 基线 |
| implement-technical-architecture-archive | implement run result、changed_files、verification、artifact_updates | technical implementation archive | 为 qa / review / version evolution 提供技术事实源 |
| qa-command-browser-acceptance | PRD / User Story / Test Case / Profile / Session | qa runs、browser evidence、auto-test alias compatibility | 为 gate / release 提供真实验收证据 |
| debug-runtime-feedback-loop | 实践项目中的 Beacon 生命周期运行事件 | debug issues、ideas、iteration inputs | 反哺下一轮 init / prototype / qa / implement 设计与实现 |

---

## Beacon 生命周期接管视角

如果从“Beacon 如何接管项目开发”来看，五条线的顺序应理解为：

### Phase 1：接入项目
- `init-progressive-architecture-blueprint`

### Phase 2：定义需求与界面基线
- `prototype-baseline`

### Phase 3：落地实现并形成技术归档
- `implement-technical-architecture-archive`

### Phase 4：执行真实验收
- `qa-command-browser-acceptance`

### Phase 5：收集使用摩擦并推动下一版演进
- `debug-runtime-feedback-loop`

也就是：

```text
init
→ 需求/原型基线
→ 实现
→ QA / gate
→ debug feedback
→ next version planning
```

---

## v1.1.8 期望结果

Beacon v1.1.8 完成后，应支持：

```text
prototype create/review/freeze
→ prototype baseline
→ prototype bind
→ implement
→ prototype verify-impl
→ prototype debug
→ quality / accept
```

并且：

- 原型主题色、排版、间距、阴影、动效要求可被正式冻结；
- 每个关键页面/状态/断点都可绑定到真实实现路径；
- 差异不是“感觉不像”，而是有 reason code / diff report / evidence；
- baseline 在任意阶段重写后，可重新进入闭环，不会造成漂移失控。

更完整地说，v1.1.8 的最终目标不是只补 5 个点，而是形成一个新的项目接管主干：

```text
beacon init
→ project onboarding / architecture blueprint / version blueprint
→ prototype baseline
→ implement + technical archive
→ qa + browser evidence + session
→ gate / release
→ debug feedback → next version
```

---

## 本版新增物料

- `version/beacon-v1.1.8-prototype-baseline.md`
- `research/gstack-gap-analysis.md`
- `research/three-track-closure-audit.md`
- `prd/beacon-prototype-baseline.md`
- `prd/beacon-debug-runtime-feedback-loop.md`
- `prd/beacon-qa-command-browser-acceptance.md`
- `prd/beacon-implement-technical-architecture-archive.md`
- `prd/beacon-init-progressive-architecture-blueprint.md`
- `user-story/beacon-prototype-baseline.md`
- `user-story/beacon-debug-runtime-feedback-loop.md`
- `user-story/beacon-qa-command-browser-acceptance.md`
- `user-story/beacon-implement-technical-architecture-archive.md`
- `user-story/beacon-init-progressive-architecture-blueprint.md`
- `qa/test-cases/beacon-prototype-baseline.md`
- `qa/test-cases/beacon-debug-runtime-feedback-loop.md`
- `qa/test-cases/beacon-qa-command-browser-acceptance.md`
- `qa/test-cases/beacon-implement-technical-architecture-archive.md`
- `qa/test-cases/beacon-init-progressive-architecture-blueprint.md`
- `qa/test-cases/index.md`
- `execution/index.md`
- `execution/technical-implementation-archive-blueprint.md`
- `execution/init-architecture-blueprint-main-doc.md`

---

## 一句话总结

> v1.1.8 要把 Beacon 的原型基线、实践反馈 debug、QA/浏览器验收、implement 技术归档、init 架构主入口五条能力线一起冻结成下一轮实现输入。

## 参考分析输入

本版已直接分析本地 gstack 源码，并沉淀差距清单：

- `research/gstack-gap-analysis.md`
- `research/three-track-closure-audit.md`

重点结论：

- gstack 在 **持久浏览器 daemon / 登录态导入 / 状态化 QA / 工具自反馈** 上更成熟
- Beacon 在 **生命周期治理 / versioned materials / machine-backed truth** 上更强
- v1.1.8 的设计方向就是把两者优势拼起来，而不是单向照搬
