# Beacon v1.4.0 对 Gstack Plan/Review 命令硬对照矩阵与 Prototype 人类面缺口分析

**Date**: `2026-05-11`  
**Status**: `analysis-only / no requirement rewrite`  
**Scope**: `gstack plan/review command matrix + Beacon prototype surface gap + CEO/design-facing human-surface implications`

## 1. 这份笔记回答什么

这份笔记直接回答四个问题：

1. `gstack` 的每个 **plan/review 命令**，Beacon 现在是否有对应命令。
2. 如果没有，Beacon 是否至少有 skill 组合或 PRD 条款能覆盖部分能力。
3. 哪些命令是 Beacon **应该补的人类面缺口**，哪些则是 **不该补成公开主面**。
4. Beacon 当前 `prototype` 在实践中为什么会“语义越界”，以及为什么这进一步证明 Beacon 需要补 CEO / design review 型的人类面，而不是继续把这类职责压给 `prototype`。

---

## 2. 分类标准

这张表用四类：

- **有**
  - Beacon 当前已经存在接近等价的公开命令/skill，人类面定位也基本对得上。
- **半有**
  - Beacon 有能力碎片或组合路径，但没有一个同等明确的公开人类面。
- **没有**
  - Beacon 当前既没有直接命令，也没有足够稳定的公开组合可替代。
- **不该有**
  - 这类能力不是“做不到”，而是如果做成公开默认命令，会与 Beacon `minimal public surface / truth-first / gate-first` 方向冲突。

---

## 3. Gstack Plan/Review 命令 -> Beacon 对照矩阵

### 3.1 Plan 命令

| Gstack 命令 | Gstack 公开语义 | Beacon 当前命令 / skill | Beacon PRD / skill 锚点 | 分类 | 判断 |
|---|---|---|---|---|---|
| `/office-hours` | 重构问题定义、六个 forcing questions、逼出真实痛点 | `beacon-prd` + `beacon-brainstorm` | `beacon-prd` 明确负责 problem/scope/goals/boundaries；`beacon-brainstorm` 只读收敛 | **半有** | Beacon 有 requirement clarification，但没有 founder-conversation 入口 |
| `/plan-ceo-review` | 战略重审、scope challenge、`expansion / selective expansion / hold scope / reduction` | `beacon-prd` + `beacon-brainstorm` + `beacon-change` | `beacon-prd` 决定 problem/scope；`brainstorm` 只读收敛；`change` 处理冻结后 scope 变化 | **半有** | 能力存在于多个面，但没有一个公开的 CEO-grade 审视关口 |
| `/plan-eng-review` | 锁定 architecture / data flow / edge cases / tests | `beacon-user-story` + `beacon-test-case` + `beacon-deep` | `user-story` 编译 acceptance；`test-case` 编译场景；`deep` 做 state-machine / test-delta / risk 分析 | **半有** | 内核能力强，但公开心智不是“engineering review lane” |
| `/plan-design-review` | 设计维度评分、指出 AI slop、交互式设计判断 | `beacon-prototype` | `prototype` 是 requirement-driven wireframe freeze，不是最终设计审查 | **半有** | Beacon 有 UX/UI handoff 冻结层，但没有独立 design review 面 |
| `/plan-devex-review` | DX 审查、开发者路径、TTHW、docs/onboarding 体验规划 | 无直接等价 | 仅可勉强挂到 `qa / deep / real-project-validation` | **没有** | Beacon 当前没有公开 DX planning surface |
| `/autoplan` | CEO -> Design -> Eng review 自动串联 | 无直接等价 | Beacon 主链与 support surface 分层，不存在同类审查管线命令 | **没有** | Beacon 没有公开的一键 plan-review pipeline |

### 3.2 Review / Verification 命令

| Gstack 命令 | Gstack 公开语义 | Beacon 当前命令 / skill | Beacon PRD / skill 锚点 | 分类 | 判断 |
|---|---|---|---|---|---|
| `/review` | Staff engineer code review，查生产 bug、完整性缺口 | `beacon-qa` + `beacon-deep` | `qa` 负责 layered verdict；`deep` 负责结构性 QA feedback review | **半有** | Beacon 更偏 acceptance/release proof，不是公开 code review lane |
| `/investigate` | Debugger，铁律是不查明原因不修 | `beacon-doctor` + `beacon-deep` + `beacon-friction-intake` | `doctor` 修上下文/环境；`deep` 做复杂分析；`friction-intake` 记录摩擦 | **半有** | 有 diagnosis/analysis 面，但没有 debugger public lane |
| `/design-review` | 已实现 UI/UX 的审查与改正 | `beacon-prototype` + `beacon-qa` | `prototype` 看 requirement-to-UX handoff；`qa` 看 evidence/verdict | **半有** | Beacon 没有专门的 live design audit 命令 |
| `/devex-review` | 实际 onboarding / docs / developer experience live audit | `beacon-qa` + `beacon-real-project-validation` | `qa` 与 real-project-validation 可承接验证，但不以 DX 审核命名 | **半有** | 能验证，不等于有公开 DX review 面 |
| `/qa` | 浏览器验证、发现 bug、修复、回归 | `beacon-qa` | `beacon-qa` 是唯一公开 verification entry | **有** | 这是当前最强直接对应项，但 Beacon 的 browser/runtime dogfooding 厚度仍弱于 gstack |
| `/qa-only` | 只报告不改 | `beacon-qa` | `beacon-qa` 可承接只验不修语义，但无独立公开 lane | **半有** | 能做，但不是独立人类面 |
| `/cso` | 安全审计 | `beacon-deep` + `beacon-qa` | 可吸纳高风险分析与验证，但无专属 security review surface | **半有** | 安全能力可被容纳，缺公开命令人格与协议 |
| `/benchmark` | 性能基线前后对比 | `beacon-qa` + `beacon-deep` | 可被测试/分析吸收，但无性能专面 | **半有** | 能力可以存在，当前公开心智没有 |

### 3.3 Ship / Release / Follow-up 命令

| Gstack 命令 | Gstack 公开语义 | Beacon 当前命令 / skill | Beacon PRD / skill 锚点 | 分类 | 判断 |
|---|---|---|---|---|---|
| `/ship` | push、开 PR、补测试、审 coverage、交付前最后一公里 | `beacon-release` | `release` 做 readiness / no-go / proof chain | **半有** | Beacon 有 release governance，没有完整 ship executor |
| `/land-and-deploy` | merge、deploy、verify production | `beacon-release` + `beacon-real-project-validation` | 可做 proof，但不是默认 deploy runner | **半有** | Beacon 当前偏治理，不偏部署执行 |
| `/canary` | post-deploy monitoring | 无直接等价 | 无公开 post-deploy canary 面 | **没有** | 目前没有 |
| `/document-release` | 交付后文档同步 | `beacon-release` + `beacon-archive` | Release/Archive 触及发布与版本治理，但不是 doc sync lane | **半有** | 有文档治理，不等于有 release-doc sync 命令 |
| `/retro` | 周复盘、贡献/速度/测试健康趋势 | `beacon-friction-intake` + learning plane + `status` | 有摩擦和学习基座，但无 retro public surface | **半有** | 可沉淀，不是复盘命令 |
| `/learn` | 记忆管理、查看/裁剪/导出 learnings | learning plane kernel + future `ask/help` consumption | `LLM decision surface` PRD 已承认 learning 消费仍偏薄 | **半有** | 内核有，公开人类面不足 |

---

## 4. 哪些是 Beacon 应该补的，哪些不该补

### 4.1 明确属于“应该补的人类面缺口”

这些不是“最好有”，而是已经形成结构性缺口：

1. **CEO-grade review surface**
   - 对应 `gstack /plan-ceo-review`
   - 目标不是写 PRD，而是：
     - 重构问题定义
     - 挑战 scope
     - 做 expansion / reduction / hold scope 判断
     - 给出为什么当前提案还不够好的上位视角

2. **Design-grade review surface**
   - 对应 `gstack /plan-design-review`
   - 目标不是直接产出 UI，而是：
     - 判断 UX 路由、页面状态、交互层次是否成立
     - 把 AI slop 在 `implement` 前拦住
     - 让 `prototype` 回到 requirement handoff，而不是承担设计决策本身

3. **更直白的 plan review public mental model**
   - Beacon 现在公开主链强，但 review 关口弱
   - 用户知道怎么走 `prd -> story -> case`
   - 但不知道：
     - 谁来 challenge 当前方案
     - 谁来挑战 scope
     - 谁来从产品/设计视角否决“看似完整但方向不对”的计划

### 4.2 明确属于“现在不该补成公开默认命令”的

1. `/autoplan`
   - 原因：会把 Beacon 拉向“公开审查流水线产品”，冲淡主链与 truth governance

2. `/pair-agent`
   - 原因：多 agent 运行态协同不该成为 Beacon 默认人类心智

3. `/design-shotgun`
   - 原因：创意设计生成不是 Beacon 的核心定位

4. `/land-and-deploy` 作为默认公开主面
   - 原因：Beacon 当前应坚持 release governance，而不是产品默认部署编排器

---

## 5. 关键缺口：Beacon 确实少了公开的 CEO 审视面

用户指出的这组能力，当前 Beacon **确实没有一个单独公开的人类面来承接**：

- 重构问题定义
- 挑战 scope
- 做 `expansion / reduction / hold scope` 这类战略判断
- 用“创始人/CEO 审视”这个公开心智包装出来

这不是命名问题，而是**职责缺口**。

### 5.1 为什么 `brainstorm` 不能替代它

`beacon-brainstorm` 当前定位是：

- read-only sidecar
- first principles
- Socratic questioning
- Occam’s razor
- requirement convergence / project evolution

它能做：

- 发散
- 收敛
- 缺口识别
- 变更候选梳理

但它**不是一个明确的 strategic review surface**。

它缺少三层东西：

1. **公开 persona**
   - 用户不会自然把它理解成“请站在 CEO / founder 角度打掉我这个坏方案”

2. **显式 scope 操作语义**
   - 它没有 `expansion / hold / reduction` 这类对 scope 进行结构判断的公开协议

3. **前置否决式 review 心智**
   - 它更像分析/收敛辅助，不像“先给方案挑刺”的正式关口

### 5.2 为什么这对 Beacon 很重要

如果没有这层人类面，Beacon 的公开路径就会变成：

- `prd` 负责把东西写清楚
- `brainstorm` 负责发散收敛
- `prototype` 负责 UX/UI 语义冻结

问题是：

> 这里没有一个阶段公开负责“你的问题定义本身可能就错了，你的 scope 可能偏了，你的产品承诺面可能不成立”。

这会导致：

- PRD 很工整，但问题仍然定义错
- Prototype 很完整，但方向本身不值得交付
- Implement/QA/Release 都很严谨，但严谨地推进了一个不够好的提案

这正是 `gstack /plan-ceo-review` 的价值。

---

## 6. Prototype 为什么会在实践中“语义越界”

你指出的现象是：

> Beacon 当前 `prototype` 原型冻结，在实践中会把原型语义直接给到 UI、UX 交付物中，这是有问题的。

这个判断我认同，而且它不是偶发实现问题，更像是**产品面缺口向下游泄漏**。

### 6.1 Prototype 的正式定位本来不是这个

根据当前 `beacon-prototype` 与全局边界，`prototype` 本来应该是：

- conditionally triggered formal stage
- requirement-driven wireframe freeze
- UX/UI handoff contract
- route/state/interaction visibility freeze

而不是：

- 最终视觉审批
- 创意设计探索
- 设计方向决策器
- 产品战略 challenge 面

### 6.2 为什么实践中会越界

因为上游少了两个公开关口：

1. **CEO-grade 问题/范围审查**
2. **Design-grade 设计决策审查**

当这两个关口缺失时，系统会自然把压力转移到 `prototype`：

- “产品是不是这样做？” 没有 CEO 面回答  
  -> prototype 被迫承接产品方向判断

- “设计是不是这样表达？” 没有 design review 面回答  
  -> prototype 被迫承接设计判断

于是 `prototype` 从：

- `requirement-driven handoff bundle`

滑向：

- `半产品决策器 + 半设计定稿器 + 半交付资产生成器`

这就是语义越界。

### 6.3 结果是什么

结果通常有三种：

1. **原型被误当成 UI 交付物**
   - 让实现阶段直接消费它，导致 requirement freeze 和 UI delivery 混层

2. **原型承担了不该承担的“方向正确性”责任**
   - 但它本质上只适合承接 route/state/interaction handoff

3. **设计与产品审查滞后到 prototype 之后**
   - 于是很多本应前置否决的问题，被拖到 prototype 或 implement 才显形

---

## 7. 为什么参考 Gstack 的方式是合理的

这里“参考 gstack”不是说 Beacon 要复制 persona 产品叙事。  
真正合理的是借鉴它的**前置关口分工**：

- `office-hours` / `plan-ceo-review`
  - 负责问题重构与 scope challenge
- `plan-design-review`
  - 负责设计方向和交互质量判断
- `plan-eng-review`
  - 负责架构、边界、测试锁定

它的好处是：

- **产品问题** 在产品关口暴露
- **设计问题** 在设计关口暴露
- **工程问题** 在工程关口暴露
- `prototype` 和 `implement` 不用替上游背锅

Beacon 当前最该借的是这个结构。

---

## 8. 对 Beacon 的收敛建议

### 8.1 应补一个 CEO-grade 人类面

建议目标：

- 不是新主生命周期
- 是 support / review surface
- 明确公开做这些事：
  - 问题重构
  - scope challenge
  - `expand / hold / reduce`
  - promised surface / product direction 审视

最自然的产品叙事不是：

- “brainstorm 升级版”

而是：

- `beacon-ceo-review` 或同类命名的人类面

因为这里缺的正是**public mental model**。

### 8.2 应补一个 design-grade 人类面

建议目标：

- 与 `prototype` 分层
- 设计 review 面负责：
  - 设计方向
  - 页面层次
  - 状态可理解性
  - interaction coherence
- `prototype` 负责：
  - requirement-driven freeze bundle
  - 设计/UX handoff contract

换句话说：

> design review 决定“该怎么设计”，prototype 决定“已决定的设计/UX 语义如何被正式冻结和交接”。

### 8.3 不要再让 prototype 继续吸收这些职责

如果不补 CEO / design 人类面，未来 `prototype` 只会继续膨胀：

- 更像设计工具
- 更像产品审查工具
- 更像 UI 交付生成器

而这和 Beacon 当前全局约束是冲突的。

### 8.4 Beacon 的最优分工

更合理的前后关系应该是：

`prd`
-> `ceo-grade review`
-> `user-story`
-> `test-case`
-> `design-grade review`（仅当 UX/UI handoff 真实存在）
-> `prototype freeze`
-> `implement`
-> `qa`
-> `release`

注意：

- 这里补的是 **review surface**
- 不是新增 truth source
- 也不是把 `prototype` 变成设计生产器

---

## 9. 最终结论

### 9.1 硬判断

- `gstack /plan-ceo-review`：Beacon 当前 **半有**
  - 有能力碎片
  - 没有公开等价命令
  - 这是明确的人类面缺口

- `gstack /plan-design-review`：Beacon 当前 **半有**
  - `prototype` 承接了一部分
  - 但正因为没有 design review 面，`prototype` 在实践中越界

- `gstack /plan-eng-review`：Beacon 当前 **半有偏强**
  - requirement 三件套 + deep 已覆盖较多内核能力
  - 但公开心智不够直观

- `gstack /plan-devex-review`：Beacon 当前 **没有**

### 9.2 更重要的判断

Beacon 当前不是“缺更多命令”，而是：

> 缺少两个前置、公开、好理解的人类审查关口：  
> 一个负责 **CEO / founder 级问题与范围审查**，  
> 一个负责 **design / UX 级方向与交互审查**。

如果这两个关口继续缺席，`prototype` 就会不断被迫吸收不该属于它的职责，  
最终把：

- requirement freeze
- design review
- UI/UX deliverable semantics

混成一层。

这不是 `prototype` 做得不够强的问题，而是**上游人类面分工缺位**的问题。

---

## 10. References

- [beacon-v1.4.0-human-surface-and-subskill-benchmark-vs-gstack.md](./beacon-v1.4.0-human-surface-and-subskill-benchmark-vs-gstack.md)
- [`skills/beacon/beacon-prd/SKILL.md`](../../skills/beacon/beacon-prd/SKILL.md)
- [`skills/beacon/beacon-user-story/SKILL.md`](../../skills/beacon/beacon-user-story/SKILL.md)
- [`skills/beacon/beacon-test-case/SKILL.md`](../../skills/beacon/beacon-test-case/SKILL.md)
- [`skills/beacon/beacon-prototype/SKILL.md`](../../skills/beacon/beacon-prototype/SKILL.md)
- [`skills/beacon/beacon-qa/SKILL.md`](../../skills/beacon/beacon-qa/SKILL.md)
- [`skills/beacon/beacon-release/SKILL.md`](../../skills/beacon/beacon-release/SKILL.md)
- [`skills/beacon/beacon-brainstorm/SKILL.md`](../../skills/beacon/beacon-brainstorm/SKILL.md)
- [`skills/beacon/beacon-deep/SKILL.md`](../../skills/beacon/beacon-deep/SKILL.md)
- [`docs/beacon/global-boundaries.md`](../beacon/global-boundaries.md)
- [`docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`](../beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md)
- [`docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`](../beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md)
- [`/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/README.md`](/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/README.md)
