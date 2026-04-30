---
date: 2026-04-22
topic: beacon-official-product-language-contract-for-prototype-and-implement
---

# Beacon Official Product Language Contract For Prototype And Implement

## What We're Building

Beacon 现在已经具备两段关键能力：

- `prototype` 能把 `prd / user-story / test-case` 编译成 wireframe freeze，并产出 `page_specs / states / analysis / canonical-envelope`
- `implement` 能绑定 `PRD + User Story + Test Case + Prototype` 并进入正式实现

但两段之间还缺一层稳定的“官方产品语汇 contract”。

这个问题不是在抽象讨论里暴露出来的，而是在做 Beacon 看板时被真实暴露出来的：

- 看板需要对外表达稳定、正式、可信的产品语义
- 但 Beacon 当前给 LLM 的前序语义约束还不够稳定
- 导致产出的页面语言仍然容易回落到内部工程词、临时描述和系统生成感

所以本质问题不是“某个页面文案不够官方”，而是：

> Beacon 还没有把“官方语义预生成 + 生命周期接入 + 语义描述管理”做成内建产品能力。

当前验证结果说明，问题不在于 Beacon 没有 requirement compile 或 freeze 能力，而在于它还没有先把“前端应该如何官方表达需求理解”冻结出来：

- `prototype` 已经有 `page_specs`、状态、页面分析等承载位，但仍直接暴露 `prototype / implement / runtime / blocker` 一类内部词
- `implement` 已经会绑定 `prototype_dir`，但没有要求实现阶段优先消费一份统一的前台命名、状态命名和页面叙事 contract
- 现有 requirement clarity / prototype review 主要检查完整性和 traceability，没有检查“产品语义是否官方化”

所以这次要增强的不是页面 copy 微调，而是新增一层：

> 让 Beacon 在 `prototype` 之前先产出一版官方产品语汇，并要求 `prototype` 与 `implement` 后续持续复用同一份语汇真相。

## Why This Approach

### Approach A: 继续在 `prototype` 或前端页面里逐页修文案

按页面逐个替换 `runtime / implement / team / ralph` 之类词，让页面看起来更像正式产品。

**Pros:**
- 改动最小
- 局部页面见效快

**Cons:**
- 只能修结果，不能修编译链
- 下一次生成 wireframe 或进入实现时还会重新泄漏内部语义
- 无法形成可复用的产品能力

**Best when:** 目标只是快速修一批现有页面文案。

### Approach B: 在 requirement truth 与 `prototype` 之间新增官方语汇 contract

先把页面命名、状态系统、角色叙事、前台禁用词、内部词翻译规则冻结成一份正式 contract，再由 `prototype` 和 `implement` 共同消费。

**Pros:**
- 能把“需求理解”先编译成官方前台语言
- `prototype` 和 `implement` 会共享同一份语义真相
- 最符合 Beacon 当前的 canonical / projection / gate 思路

**Cons:**
- 比改文案更慢一步
- 需要额外定义 contract 和 gate

**Best when:** 目标是把 Beacon 做成稳定的正式产品，而不是一次性页面优化。

### Approach C: 把官方命名交给 UI 实现阶段自行决定

保留 requirement truth 和 prototype freeze，不新增语言 contract，让设计或前端在实现阶段临时决定页面叫法和状态词。

**Pros:**
- Beacon 核心改动最少
- UI 团队自由度高

**Cons:**
- `prototype -> implement` 会重新断链
- 需求理解与最终前台表达可能漂移
- QA 很难验证“前台语义是否对齐原始需求”

**Best when:** Beacon 只负责工程执行，不负责产品语言一致性。

### Approach D: 把官方语义预生成与管理并入 Beacon 生命周期

不把它视为单独一份静态词典，而是把它做成 Beacon requirement compiler 的正式能力：

- 先从 `prd / user-story / test-case` 生成一版 `official semantic layer`
- 再让 `prototype` 消费这层语义生成 wireframe freeze
- 再让 `implement / qa / release` 继续引用同一份语义真相
- 同时允许通过变更流程做受控更新，而不是散落到页面代码里各自改写

**Pros:**
- 能真正让 Beacon 吸收这项能力，而不是停留在文档建议
- 让 LLM 在进入页面生成前就拿到规范语义
- 让官方表达变成 lifecycle asset，而不是 UI 层临时产物

**Cons:**
- 范围比单纯命名 contract 更大
- 需要新增产物、字段和 gate

**Best when:** 目标是提升 Beacon 整体产出质量和正式产品能力。

推荐采用 **Approach D**。

## Key Decisions

- 决策 1：Beacon 需要把 `official semantic layer` 做成内建新增特性。它不是 UI 附属物，也不是外部 skill 能力，而是 requirement compile 的正式中间产物。
- 决策 2：这层语义产物位置在 `prd / user-story / test-case` 之后、`prototype` 之前，并持续贯穿 `implement / qa / release`。
- 决策 3：LLM 在进入 `prototype` 或前端实现之前，必须先消费这份预生成语义，而不是直接从 requirement 原文和局部 prompt 临时翻译。
- 决策 4：这份语义层必须是 canonical 驱动的正式产物，而不是前端实现时临时写出来的 copy note。
- 决策 5：`prototype` 必须显式消费这份语义层，用它生成页面名称、状态标签、角色语气、关键信息块名称和禁止词替代语。
- 决策 6：`implement` 必须把这份语义层作为正式输入之一，和 `prototype freeze` 一起约束 UI 文案、页面标题、状态系统和交付叙事。
- 决策 7：`qa` 与 `release` 不能只检查功能闭环，也要检查官方语义是否保持一致，避免前台表达在后续实现中漂移。
- 决策 8：首页、项目详情、物料查看器默认使用官方产品语义；`team / ralph / subagent / session metadata` 等内部词只允许在 `运行中心 / 恢复诊断` 等二级面显式出现。
- 决策 9：`prototype` 这个词在 Beacon 工作流里可以保留，但前台页面默认不直接展示为用户主语义；对前端更合适的官方表达应是 `页面结构冻结` 或 `页面方案冻结`。
- 决策 10：`implement` 对前台更合适的官方表达不是“Implement”，而是 `正式实现`、`交付实现` 或等价稳定说法。

## Semantic Layer Scope

这层能力至少要管理四类内容：

1. 语义预生成
   - 从 requirement truth 中预生成官方页面名、官方状态名、官方模块名、官方动作名、官方风险名
2. 语义约束
   - 明确哪些内部词不能默认上屏，哪些词必须翻译后才能进入人类面
3. 语义投影
   - 把同一份语义投影到 `prototype`、实现 handoff、QA 校验、人类可读物料
4. 语义变更管理
   - 当官方表达需要升级时，通过受控变更刷新，而不是在页面代码、文案和原型里各自漂移

## External Skill Augmentation

Beacon 原本就有桥接外部 skill 的能力，这次不应忽略这条基础，而应继续往下推。

已核实的事实是：

- Beacon 已有 `skill registry / bind / profile orchestration` 能力
- 外部 skill 已经可以通过 `registry` 进入 `project_skills`
- 运行前已有 `supported_stages / capabilities / evidence_contract` 校验边界
- 这说明 Beacon 不是不能桥接外部 skill，而是还没有把“外部设计 skill”正式纳入 `prototype / implement` 的增强链

所以这里要补的不是“能否执行第三方命令”，而是：

> 如何把外部设计 skill 变成 Beacon 生命周期内的受控增强面，而不是随机外挂。

### Official Default Bridge Skill

这次约束要明确：

- `semantic` 是 Beacon 内建新增特性
- `design skill` 通过外部 bridge 接入
- 官方指定默认桥接 skill 是 `Leonxlnx/taste-skill`

基于已核实的公开仓库，`taste-skill` 当前公开提供的 skill 包括：

- `taste-skill`
- `gpt-taste`
- `redesign-skill`
- `soft-skill`
- `output-skill`
- `minimalist-skill`
- `brutalist-skill`
- `stitch-skill`

其中对 Beacon 来说应明确默认值：

- 默认 bridge repository: `https://github.com/Leonxlnx/taste-skill`
- 默认 bridge skill: `taste-skill`

其余变体如 `gpt-taste`、`redesign-skill`、`stitch-skill` 应视为可选 profile，不应覆盖默认桥接口径。

### What External Skills Should Do

对 Beacon 来说，外部 design skill 的合理职责应是：

- 帮助 `prototype` 提升页面语义、信息架构和设计系统一致性
- 帮助 `implement` 生成更高质量的前端设计约束、组件口径或审美 review

它们不应负责：

- 替代 Beacon 内建 `semantic layer`
- 直接决定 release 是否通过
- 绕过 Beacon 的 canonical / review / gate
- 把 `prototype` 或 `implement` 变成任意第三方 skill 调度器

## Skill Integration Model

建议把外部 skill 接入定义成三层：

1. Skill installation / discovery
   - 允许用户通过外部工具安装 skill，例如 `npx skills add ...`
   - Beacon 只负责发现、登记、校验，不负责把安装动作变成主流程的一部分
2. Capability-bounded binding
   - 外部 skill 必须声明：
     - `supported_stages`
     - `capabilities`
     - `evidence_contract`
   - 只有满足当前节点要求时，才能绑定到 `prototype / implement / qa` 内部节点
3. Canonical writeback
   - 外部 skill 的结果不能直接成为 Beacon 真相
   - 必须先归一化成 Beacon 可审核的 semantic/design envelope，再进入 canonical 和各类 sink

### Discovery And Binding Flow

建议的场景链是：

1. 用户在宿主侧安装外部 skill
   - 例如 `npx skills add https://github.com/Leonxlnx/taste-skill --skill taste-skill`
2. Beacon 在标准 skill 目录发现它
   - 如 `~/.agents/skills/`、`~/.codex/skills/`
3. Beacon 把该 skill 录入 `project_skills.registry`
   - 并补齐 `entry / supported_stages / capabilities / evidence_contract`
4. Beacon 通过 `profile` 或 feature binding 决定该 skill 参与哪个阶段
5. 真正执行时，外部 skill 只在 `prototype / implement / qa` 的内部节点中被调用
6. 结果必须被 Beacon 归一化、审阅、写回，不允许直接跳过 canonical

这里的边界要刻意保持：

- 安装动作属于外部生态，不属于 Beacon 主流程
- Beacon 的职责是 discovery、boundary validation、binding、writeback
- 对人类而言，仍然只看到 `prototype`、`implement`、`qa` 等主命令

## Prototype And Implement Scenarios

建议优先覆盖四类场景：

### Scenario A: `prototype` 的设计语义增强

适合接入：

- `taste-skill`
- `gpt-taste`
- `redesign-skill`

用途：

- 在 Beacon 内建 `semantic layer` 已经产出官方语义后
- 再用默认 `taste-skill` 桥接增强页面气质、设计系统语气和信息架构表达
- 最终仍回写到 Beacon 的 `prototype` freeze

### Scenario B: `prototype` 的设计系统语义增强

适合接入：

- `stitch-skill`
- `soft-skill`
- `minimalist-skill`

用途：

- 抽取品牌色、排版、语气、视觉节奏
- 但结果必须回写成 Beacon 的 `semantic-contract` / `semantic-usage-guidelines`

### Scenario C: `implement` 的前端 taste review 增强

适合接入：

- `taste-skill`
- `gpt-taste`
- `soft-skill`
- `minimalist-skill`
- `brutalist-skill`

用途：

- 在 `implement` 内部给前端实现增加审美和产品表达 review
- 输出结构化建议、风险、禁止词、改进方向

### Scenario D: `implement` 的 design-to-component 增强

适合接入：

- `stitch-skill`
- 其他 design-to-code / design-rule skill

用途：

- 帮助把设计语义约束进一步投影为组件层建议
- 但正式代码实现和验收仍由 Beacon `implement / qa` 收口

## Lifecycle Integration

建议接入方式：

- `prd / user-story / test-case`
  - 继续提供 requirement truth
- `prototype`
  - 对人类仍保持唯一公开入口
  - 在其内部前置新增 `official semantic layer` 预生成与校验
  - 可按 capability-bound 方式调用默认 `taste-skill` 或其变体增强设计质量
  - 使用 `official semantic layer + requirement truth` 生成 wireframe freeze
- `implement`
  - 使用 `prototype freeze + official semantic layer` 约束正式实现
  - 可按 capability-bound 方式调用默认 `taste-skill` 或其变体辅助前端交付
- `qa`
  - 检查功能闭环和语义闭环是否同时成立
- `release`
  - 只有功能、语义、投影三者一致时才可判定正式发布通过

边界规则：

- `official semantic layer` 是机器内部 requirement compiler 能力，不是新的公开一级命令，也不是新的公开主流程阶段
- 对人类仍保持 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- `semantic` 只应作为 `prototype`、`implement`、`qa` 的内嵌前置动作与共享资产存在
- `taste-skill` 是默认外部设计桥接 skill，但只应作为这些阶段内部的增强面，不得升级为新的对外主流程

## Skill Capability Proposal

为了让外部 skill 能稳定接入，建议 Beacon 增补一组面向语义/设计的标准 capability：

- `semantic-generation`
- `semantic-normalization`
- `design-system-synthesis`
- `wireframe-enhancement`
- `frontend-taste-review`
- `design-to-component`
- `ui-copy-governance`

建议的 stage 对齐：

- `prototype`
  - `semantic-generation`
  - `semantic-normalization`
  - `design-system-synthesis`
  - `wireframe-enhancement`
- `implementation`
  - `frontend-taste-review`
  - `design-to-component`
  - `ui-copy-governance`

建议的 evidence contract：

- `semantic_contract`
- `semantic_dictionary`
- `semantic_review`
- `design_system_profile`
- `wireframe_enhancement_report`
- `frontend_taste_review`
- `component_projection_hint`

## Official Vocabulary V1

建议先冻结一版最小官方语汇：

| Internal term | Official product label |
|---|---|
| `prototype` | `页面结构冻结` |
| `implement` | `正式实现` |
| `qa` | `交付验证` |
| `release` | `正式发布` |
| `runtime` | `执行态` |
| `team` | `协同执行` |
| `ralph` | `自主修复闭环` |
| `single` | `单线执行` |
| `blocker` | `阻塞项` |
| `debug issues` | `交付风险` |
| `fallback_reason` | `执行约束` |
| `management-overview` | `项目总览` |
| `project-detail` | `项目详情` |
| `runtime-center` | `执行中心` |
| `material-viewer` | `物料查看器` |

规则：

- 前台页面默认显示右侧官方语汇
- 左侧内部词只保留在 machine-readable contract、实现映射、诊断页面和技术证据中
- 同一页面不混用中英双套主语义

## Semantic Management Output

这层能力最终不应只输出一份 Markdown 词典，而应该至少有：

- `semantic-contract.json`
  - machine-readable canonical 语义真相
- `semantic-dictionary.md`
  - 人类可审核词典
- `semantic-usage-guidelines.md`
  - 页面、状态、风险、动作的使用规则
- `semantic-review.json`
  - 语义 gate 结果，供 `prototype / implement / qa / release` 消费
- `design-skill-evidence.json`
  - 外部设计/语义 skill 的结构化输出与来源记录
- `skill-augmentation-report.md`
  - 说明哪些外部 skill 参与了增强、增强了什么、哪些结论被 Beacon 接纳

## Open Questions

- 官方主语言是否确定为正式中文优先，英文只保留品牌名和极少量辅助信息。
- `runtime-center` 的官方前台名称最终是 `执行中心` 还是 `交付中心`。
- `prototype` 在产品面是否统一翻译为 `页面结构冻结`，还是保留 `方案冻结`。
- `implement` 在管理端状态标签里是使用 `正式实现`，还是使用更偏交付语义的 `交付实现`。

## Next Steps

→ 先冻结 `official product language contract` 的字段结构  
→ 再把它接入 `prototype plan/create/review`  
→ 然后把它接入 `implement` 的 preflight、handoff 和 UI 实现约束  
→ 最后再进入具体页面和前端代码的重写
