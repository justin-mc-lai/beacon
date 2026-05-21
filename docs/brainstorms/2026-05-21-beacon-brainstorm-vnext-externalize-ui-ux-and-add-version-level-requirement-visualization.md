# Beacon Brainstorm

## prompt_summary
确认 Beacon 下一阶段演进方向：结合新的 `ui-ux-dev` 框架，评估是否应停止在 Beacon 内冗余维护 design / prototype 设计执行能力；改为由 `ui-ux-dev` 承担 UI/UX 探索、系统推荐、review、开源库分析，再把结果接入 Beacon requirement 物料。与此同时，重新分析 Beacon 版本级 requirement 三件套的人类理解面，要求至少补齐：版本级业务流程大纲图、状态机总图、PRD / user-story / test-case 三件套映射图，用于后续 `beacon-change -> prd -> user-story -> test-case` 的上游输入。

- date: `2026-05-21`
- version_context: `v1.4.7`
- mode: `project-evolution`
- canonical_mode: `project-evolution`

## version_material_refs
- `docs/beacon/global-boundaries.md`
- `docs/beacon/v1.4.7/SUMMARY.md`
- `docs/beacon/v1.4.7/execution/index.md`
- `docs/beacon/v1.4.7/execution/architecture-blueprint.md`
- `docs/beacon/v1.4.7/execution/human-skill-reference.md`
- `skills/beacon/SKILL.md`
- `skills/beacon/using-beacon/SKILL.md`
- `skills/beacon/beacon-brainstorm/SKILL.md`
- `skills/beacon/beacon-prototype/SKILL.md`
- `skills/beacon/beacon-design-review/SKILL.md`
- `/Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/ui-ux-dev/SKILL.md`
- `docs/beacon/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`

## confirmed_facts
- Beacon 主链必须保持 `prd -> user-story -> test-case -> implement -> qa -> release` 收敛。
- `prototype` 只允许作为条件触发层存在，不能变成所有 feature 的常驻 stage。
- `design-review`、`brainstorm`、`deep` 等都属于 support surface，不是新的 lifecycle stage。
- `ui-ux-dev` 已经提供独立的 UI/UX intent router，面向 `explore / system / review / polish / extract / library` 六个设计意图域。
- Beacon 当前已实现 design / prototype 能力，但现状使用体验不好，不适合作为继续扩张 Beacon 的主要方向。
- `beacon-brainstorm` 对复杂 feature 的 human closure contract 已经明确要求 business flow explanation、state-machine explanation 等人类可读闭环材料。

## assumptions_under_test
- Beacon 内建 design / prototype 执行能力的长期维护成本，高于其对 requirement closure 的新增价值。
- UI/UX 执行能力外部化后，Beacon 仍需要保留“设计结果进入 requirement truth”的治理接入层。
- 当前 Beacon requirement 三件套对机器面较强，但对人类脑容量不友好，缺少版本级大纲图投影。

## first_principles_breakdown
- 用户结果：人类需要快速看懂一个版本到底在解决什么业务问题、主流程是什么、状态如何流动、三件套各自负责什么。
- 证据约束：设计探索可以外包，但 requirement truth 不能外包；最终仍要收回 `prd / user-story / test-case`。
- 闭环约束：UI/UX 不能成为新 stage；图面也不能成为 canonical truth，只能作为 human-readable projection。

## socratic_questions
- Beacon 保留 design / prototype 的真正不可替代价值是什么：做设计，还是治理设计结果进入 requirement truth？
- 如果设计执行权完全外移，Beacon 是否还能保持对页面意图、状态切换、交互契约的冻结能力？
- 版本级 requirement 三件套为什么难以被人理解：是 truth 不够，还是缺少业务流程图与状态机图投影？
- 哪些图面是大纲级必须产物，哪些细节不应进入版本级 freeze 面？

## redundancy_cuts
- 不继续把 Beacon 演进成完整 UI/UX 工具箱。
- 不在 Beacon 内重复实现 `explore / system / review / polish / library` 这类设计执行能力。
- 不把版本图面扩展成新的 truth source；图面只做投影、对齐、解释。

## option_space

### Option A: 继续增强 Beacon 内建设计能力

优点：
- 设计与 requirement 物料都在 Beacon 内

缺点：
- 与 `ui-ux-dev` 明显重叠
- 违反 Beacon 主链收敛与复杂度内收原则
- 高概率继续积累“有能力但不好用”的 support 面

判断：
- 不推荐

### Option B: 完全删除 design / prototype

优点：
- 结构最干净

缺点：
- Beacon 会失去“设计结果进入 requirement truth”这一层接入治理
- 页面意图、状态可见性、交互 handoff 缺少明确落点

判断：
- 不推荐

### Option C: 外部化 UI/UX 执行，Beacon 保留 prototype adapter + requirement visualization

结构：

```text
ui-ux-dev
-> 设计探索 / 设计系统 / 开源库分析 / review / polish
-> 产出设计方向与设计结果
-> Beacon prototype adapter
-> 编译进 prd / user-story / test-case / requirement_clarity / freeze
```

同时新增：

```text
版本级业务流程大纲图
版本级状态机总图
版本级 PRD / user-story / test-case 映射图
```

判断：
- 推荐

## converged_direction

### 1. Beacon 不再承担主要 UI/UX 执行面

后续 UI/UX 设计探索、设计系统推荐、开源库对比、视觉 review、polish、截图拆解，应统一路由到 `ui-ux-dev`。

Beacon 内现有 `design` 能力不再继续作为重点建设方向。
`beacon-design-review` 若保留，应降级为 very-thin route / governance bridge，而不是继续演进为完整设计能力面。

### 2. `prototype` 不删除，但降级重定义为 adapter

`prototype` 后续的主要职责不是“生成设计”，而是“治理设计结果如何进入 Beacon requirement truth”。

它应承接并编译的对象包括：
- 页面/流程大纲
- screen intent
- 状态可见性
- 关键交互 handoff
- 与 PRD promise/scope 的映射
- 与 user-story acceptance 的映射
- 与 test-case coverage 的映射

### 3. 正式补齐版本级 requirement visualization

Beacon 应新增一个版本级 human-readable projection 套件，至少包含：

1. 版本级业务流程大纲图
2. 版本级状态机总图
3. 版本级三件套映射图

这三类图只做：
- 对齐
- 解释
- 投影

不做：
- canonical truth
- gate verdict
- machine writeback source

### 4. 新增一个专门 support surface 或 requirement support 套件

建议后续收成一个 requirement-visualization / business-flow / state-machine review 方向的 support surface。

它的职责是：
- 帮复杂 feature 或整版版本生成板正清晰的大纲图
- 帮人类快速建立业务理解
- 作为 `change -> prd -> user-story -> test-case` 的上游人类闭环材料

## candidate_vnext_feature_lines

### Feature 1
- slug: `beacon-vnext-ui-ux-externalization-and-prototype-adapter`
- goal: 外部化 UI/UX 执行权，Beacon 仅保留设计结果治理与 prototype adapter

### Feature 2
- slug: `beacon-vnext-version-requirement-visualization-contract`
- goal: 为版本级 requirement 三件套补齐业务流程图、状态机图、三件套映射图

### Feature 3
- slug: `beacon-vnext-business-flow-and-state-machine-review-surface`
- goal: 为复杂 feature / 整版 freeze 提供稳定的人类理解 support surface

## gap_list
- 还缺一份正式 research note，把 `ui-ux-dev` 外部化与 Beacon requirement visualization 的边界说清楚
- 还缺对 `prototype` 未来 contract 的精确定义：哪些输入必需，哪些输出是 freeze-facing
- 还缺版本级状态机的最小 canonical state taxonomy
- 还缺三件套映射图的标准投影格式

## recommended_next_route
- 先写 research closure
- 然后进入 `beacon-change`
- 再冻结新的 PRD / user-story / test-case

## closure_statement
这轮 brainstorm 不建议继续在 Beacon 内冗余演进 design 执行能力。推荐方向是：UI/UX 执行外部化到 `ui-ux-dev`，Beacon 自身收敛成 design-result adapter + requirement visualization kernel。
