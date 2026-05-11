# Beacon v1.4.0 人类面与子 Skill 全面对标 Gstack

**Date**: `2026-05-11`  
**Scope**: `Beacon human surface + host-visible sub-skills vs garrytan/gstack current public skill surface`  
**Method**: `source-grounded comparison + Beacon frozen-material alignment`  
**Status**: `analysis-only / no requirement rewrite`

## 1. 目的

这份笔记的目标不是判断 Beacon 是否“应该变成另一个 gstack”，而是回答三个更具体的问题：

1. `gstack` 当前公开的人类面到底在做什么。
2. Beacon `v1.4.0` 当前的人类面、support surface、补充子 skill、advanced/internal skill，分别已经覆盖到哪里。
3. 哪些能力值得 Beacon 借鉴，哪些能力与 Beacon 当前 `truth-first / gate-first / minimal public surface` 方向存在结构性张力。

## 2. 事实基线

### 2.1 gstack 当前事实

基于 `garrytan/gstack` 当前 README 与本地 canonical mirror：

- 当前公开叙事已不是“15 个角色”，而是 **`23 specialists and 8 power tools`**。
- 当前公开主链是：
  - `Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect`
- 当前公开关键 skills 包括：
  - `/office-hours`
  - `/plan-ceo-review`
  - `/plan-eng-review`
  - `/plan-design-review`
  - `/plan-devex-review`
  - `/review`
  - `/investigate`
  - `/design-review`
  - `/devex-review`
  - `/design-shotgun`
  - `/design-html`
  - `/qa`
  - `/qa-only`
  - `/pair-agent`
  - `/cso`
  - `/ship`
  - `/land-and-deploy`
  - `/canary`
  - `/benchmark`
  - `/document-release`
  - `/retro`
  - `/browse`
  - `/learn`
- 当前 power tools 包括：
  - `/codex`
  - `/careful`
  - `/freeze`
  - `/guard`
  - `/unfreeze`
  - `/open-gstack-browser`
  - `/setup-deploy`
  - `/setup-gbrain`
  - `/gstack-upgrade`

核心判断：

> gstack 的真正产品单元不是“角色人格”，而是“专业关口 + 连续工作流 + 运行态证据 + 经验复用”。

### 2.2 Beacon v1.4.0 当前事实

基于 [`docs/beacon/global-boundaries.md`](../beacon/global-boundaries.md)、[`docs/beacon/v1.4.0/SUMMARY.md`](../beacon/v1.4.0/SUMMARY.md)、[`docs/beacon/v1.4.0/execution/architecture-blueprint.md`](../beacon/v1.4.0/execution/architecture-blueprint.md)、[`skills/beacon/SKILL.md`](../../skills/beacon/SKILL.md)：

- Beacon 公开主链仍固定为：
  - `prd -> user-story -> test-case -> implement -> qa -> release`
- `prototype` 是条件触发层，不是默认必经主链。
- `implement` 与 `qa` 仍是唯一公开执行入口。
- `help / status / doctor / archive` 是 support surface，不是新生命周期阶段。
- `ask / brainstorm / learning / tasks ledger / board` 不得成为新的 truth 源或 gate 真相。
- `v1.4.0` 正在强化两条与本次对标强相关的演进线：
  - `lightweight kernel and core surface refactor`
  - `llm decision surface and learning loop evolution`

核心判断：

> Beacon 的主产品不是“更强的 agent 编排”，而是“冻结真相、单向编译、执行护栏、可审计 support surface”。

## 3. Beacon 当前人类面全景

### 3.1 一级人类面

#### 主生命周期面

- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-prototype`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`

#### Support surface

- `beacon-help`
- `beacon-status`
- `beacon-doctor`
- `beacon-archive`

### 3.2 已公开的补充子 skill

- `beacon-prd-bootstrap`
- `beacon-brainstorm`
- `beacon-change`
- `beacon-deep`
- `beacon-friction-intake`
- `beacon-toolkit-lighthouse`
- `beacon-toolkit-metadata`
- `beacon-toolkit-branch-governance`
- `beacon-real-project-validation`
- `using-beacon`

### 3.3 这些 skill 的结构定位

| 层级 | Beacon 当前定位 | 说明 |
|---|---|---|
| 主交付链 | `prd / user-story / test-case / prototype? / implement / qa / release` | 唯一正式交付主链 |
| 支持链 | `help / status / doctor / archive` | 负责解释、路由、诊断、历史治理 |
| requirement 补充链 | `prd-bootstrap / brainstorm / change / deep` | 不能改写 frozen truth 纪律 |
| 治理 / 工具链 | `toolkit-lighthouse / toolkit-metadata / toolkit-branch-governance / friction-intake / real-project-validation` | 偏 analysis、metadata、governance、proof |

Beacon 当前的人类面不是“一个虚拟工程团队”，而是“一个被严格约束的交付治理系统”。

## 4. Gstack 与 Beacon 的结构性差异

### 4.1 gstack 的主轴

`gstack` 公开给用户的是一条高自治、高吞吐的 sprint 流水线：

- 问题重构
- 方案审查
- 设计审查
- 工程审查
- 运行态 QA
- 发版与部署
- 复盘与记忆

它强调：

- 单兵吞吐
- 并行 sprint
- 多专业判断关口
- 浏览器 / 部署 / 生产验证
- cross-model second opinion

### 4.2 Beacon 的主轴

Beacon 公开给用户的是一条 evidence-first delivery chain：

- requirement freeze
- acceptance traceability
- controlled implement entry
- controlled QA entry
- release governance

它强调：

- truth root 唯一性
- compiled contract 单向投影
- implement / qa 入口独占
- support surface 可解释但不掌真相
- learning / ask / brainstorm 不得篡位为真相源

### 4.3 一句话差异

- `gstack` 更像：`AI software factory`
- Beacon 更像：`AI-governed delivery kernel`

## 5. 一对一 / 一对多映射表

### 5.1 Gstack public sprint skills -> Beacon 当前对位面

| Gstack | 角色/意图 | Beacon 最接近面 | 对应关系 | 判断 |
|---|---|---|---|---|
| `/office-hours` | 问题重构、迫问真实需求 | `beacon-prd` + `beacon-brainstorm` | 一对多 | Beacon 有需求收敛能力，但缺少像 office-hours 一样更“对话化、强质询”的默认入口 |
| `/plan-ceo-review` | 战略 scope challenge | `beacon-prd` + `beacon-brainstorm` + `beacon-change` | 一对多 | Beacon 能做 scope 治理，但目前更偏文档真相治理，不像 gstack 那样公开为“创始人审查关口” |
| `/plan-eng-review` | 架构/测试/边界前置锁定 | `beacon-user-story` + `beacon-test-case` + `beacon-deep` | 一对多 | Beacon 的 requirement 三件套天然覆盖这层，但公开叙事不如 gstack 那样直观 |
| `/plan-design-review` | 设计质量与 AI slop 审核 | `beacon-prototype` | 弱对应 | Beacon 有 prototype 条件层，但没有公开的 design review persona 和视觉审查闭环 |
| `/plan-devex-review` | 开发者体验方案审查 | 无直接等价主 skill | 无直接对应 | Beacon 尚未把 DX review 独立成公开人类面 |
| `/review` | 实装后工程审查 | `beacon-qa` + `beacon-deep` | 弱一对多 | Beacon QA 更偏验收和交付闭环，不等于“代码 review/生产 bug review” |
| `/investigate` | 根因分析 | `beacon-doctor` + `beacon-deep` + `beacon-friction-intake` | 一对多 | Beacon 有诊断与深度分析面，但未包装成“debugger public lane” |
| `/design-review` | 已实现 UI 审核与修正 | `beacon-prototype` + `beacon-qa` | 弱对应 | Beacon 当前没有公开的设计验收专面 |
| `/devex-review` | 实际 onboarding 审计 | `beacon-qa` + `beacon-real-project-validation` | 弱对应 | 有现实验证能力，但不以 DX 审核的形态存在 |
| `/design-shotgun` | 多方案视觉探索 | 无直接对应 | 无直接对应 | Beacon 当前不应默认扩到创意设计生成面 |
| `/design-html` | 把设计转成实现 | `beacon-prototype` -> `beacon-implement` | 跨阶段间接对应 | Beacon 把 prototype 和 implement 明确分开，不会把“设计转实现”包装成一个公开 skill |
| `/qa` | 浏览器验证 + 修复 + 回归测试 | `beacon-qa` | 部分对应 | Beacon 有正式 QA 入口，但浏览器/真实运行态 dogfooding 还不是同等厚度 |
| `/qa-only` | 只报告不改 | `beacon-qa` | 部分对应 | Beacon 可以承载 report-only 语义，但没独立公开子面 |
| `/pair-agent` | 多 agent 浏览器协同 | 无直接对应 | 无直接对应 | Beacon 当前不以“多 agent 实时协同操作”作为人类主面 |
| `/cso` | 安全审计 | `beacon-deep` + `beacon-qa` | 弱对应 | Beacon 有安全验证容器，但没公开成独立 chief security lane |
| `/ship` | 开 PR、补测、推送 | `beacon-release` | 部分对应 | Beacon release 更偏 readiness/gate，不等于完整 ship automation |
| `/land-and-deploy` | merge + deploy + verify prod | `beacon-release` + `beacon-real-project-validation` | 弱一对多 | Beacon 当前更偏治理，不是默认 deploy runner |
| `/canary` | 发布后监控 | 无直接对应 | 无直接对应 | Beacon 当前没有公开 post-deploy canary 面 |
| `/benchmark` | 性能基线对比 | `beacon-qa` + `beacon-deep` | 弱对应 | 可被纳入验证，但不是公开的性能专面 |
| `/document-release` | 文档与交付同步 | `beacon-release` + `beacon-archive` | 弱对应 | Beacon 强调版本/真相治理，但没有 release doc sync 的单独公开动作 |
| `/retro` | 周期复盘 | `beacon-friction-intake` + `beacon-status` + learning plane | 一对多 | Beacon 具备摩擦沉淀与学习基座，但缺少一个清晰的复盘输出面 |
| `/browse` | 给 agent 眼睛 | 无直接对应 | 无直接对应 | 这是 gstack 的核心 runtime 差异之一 |
| `/learn` | 项目记忆治理 | learning plane kernel + `beacon-deep` + future support surface | 内核已有 / 人类面偏弱 | Beacon 已有 learning kernel，但对宿主的公开消费仍偏薄 |

### 5.2 Gstack power tools -> Beacon 当前对位面

| Gstack power tool | Beacon 最接近面 | 判断 |
|---|---|---|
| `/codex` | 无直接公开对位 | Beacon 还没有公开的 cross-model second-opinion 面 |
| `/careful` | `beacon-doctor` / branch governance / implement gate | Beacon 通过 gate 和 contract 限制风险，而不是 session safety tool |
| `/freeze` | `beacon-toolkit-branch-governance` / truth boundary | Beacon 偏 workflow boundary，不偏文件编辑 freeze |
| `/guard` | `implement gate + doctor + branch governance` | 同上，Beacon 通过前置 contract 做限制 |
| `/unfreeze` | 无直接公开对位 | Beacon 不以 session unlock 作为用户心智 |
| `/open-gstack-browser` | 无直接对位 | Beacon 当前没有把浏览器运行态做成公开主能力 |
| `/setup-deploy` | 无直接对位 | Beacon 当前不以部署平台接线为公开 skill |
| `/setup-gbrain` | 无直接对位 | Beacon 不以知识库安装器作为产品主面 |
| `/gstack-upgrade` | `beacon-doctor`（部分） | Beacon doctor 能处理材料/上下文/版本漂移，但不是自升级器 |

## 6. Beacon 当前最值得借鉴的点

### 6.1 借鉴点一：把“角色”翻译成“专业关口”

Beacon 不需要学 `23 specialists` 的表面形式，但值得学下面这层：

- 每个关键阶段都要有明确判断协议
- 用户能理解为什么下一步是这个 skill
- plan 阶段、runtime 阶段、release 阶段的关口区别要更可见

这与 Beacon 当前正在冻结的 `LLM decision surface` 高度一致。

### 6.2 借鉴点二：让 support surface 更会解释 route

`gstack` 很强的一点，是它把“为什么该走这一步”说得非常直白。

Beacon 当前 PRD 里已经明确要求：

- support surface 能解释为什么推荐这条 route
- `ask` 成为自然语言入口
- learning 进入渐进披露闭环

因此 gstack 给 Beacon 的启发不是“新增命令”，而是：

> 把现有 `help / status / ask / brainstorm / deep` 的解释能力做厚。

### 6.3 借鉴点三：把 learning 从内核能力变成默认决策输入

Beacon 当前已经正式承认这个缺口：

- learning plane 已存在
- 但还没有系统进入每个 skill 的默认消费路径

`gstack /learn` 给的启发很清楚：

- learning 不只是存储
- learning 必须在下一次相关决策中被主动召回
- learning 必须能被审计、降级、修剪

这与 Beacon 的 frozen direction 完全兼容。

### 6.4 借鉴点四：更强的人类可读进度投影

`gstack` 的 sprint 心智很强，因为用户始终知道当前在：

- plan
- review
- qa
- ship

Beacon 当前也在做 `implement tasks ledger projection`。  
这条线值得继续，因为它可以提升人类面可见性，而不破坏 canonical truth。

### 6.5 借鉴点五：把“真实运行态证据”抬升到更高优先级

`gstack` 的核心飞轮之一是：

- browser evidence
- interactive QA
- deployment verification
- canary

Beacon 当前有 `qa`、`release`、`real-project-validation`，但运行态证据的人类面还不够厚。  
这条线值得作为后续演进候选，但必须挂在 `qa / release` 公开入口之下，不能横向长出新主流程。

## 7. Beacon 当前不应照搬的点

### 7.1 不应照搬“角色化产品叙事”

Beacon 的差异化不是“更多 persona”，而是：

- 唯一 truth root
- contract 单向编译
- implement / qa gate 独占
- support surface 不掌真相

如果 Beacon 把自己包装成“23 个虚拟专家团队”，会稀释其真实产品优势。

### 7.2 不应照搬“高自治执行优先于治理”

`gstack` 的产品目标是吞吐。  
Beacon 的产品目标是受治理的交付闭环。

因此 Beacon 不能为了接近 gstack 的使用快感而放松：

- truth freeze
- gate verdict
- route boundary
- change/refreeze discipline

### 7.3 不应照搬“并行 sprint 作为公开默认心智”

Beacon 当前全局约束要求：

- 主链固定
- `implement` 与 `qa` 是唯一执行入口
- team/subagent/precheck 复杂度默认留在机器内部

这和 gstack 对并行 sprint、pair-agent、多 runtime worker 的公开鼓励方向并不一致。  
Beacon 可以内部吸收类似复杂度，但不应把它外翻成新的人类负担。

### 7.4 不应照搬“设计生成 / 浏览器运行时 / 部署接线”三件套作为默认产品面

这三块对 gstack 很关键，但对 Beacon 来说属于不同产品层：

- 设计生成偏 domain workflow
- 浏览器运行时偏 execution runtime tooling
- 部署接线偏 DevOps integration surface

Beacon 如果同时吸收，会明显冲淡 `evidence-first workflow kernel` 的边界。

## 8. 对 Beacon 人类面与子 Skill 的收敛判断

### 8.1 Beacon 当前人类面的真正短板

不是“skill 数量不够”，而是三件事：

1. **解释层偏薄**  
   很多能力已经存在，但用户不容易看出“为什么现在该用它”。

2. **learning 消费层偏薄**  
   learning 已存在，但还不是每个关键 skill 的默认输入。

3. **运行态验证层偏薄**  
   QA / release 已存在，但还不具备 gstack 那种强浏览器、强部署、强回归证据的公开肌肉。

### 8.2 Beacon 当前已经强于 gstack 的地方

1. **truth discipline 更强**
2. **requirement traceability 更正式**
3. **change / refreeze / archive 治理更系统**
4. **support surface 与主流程分层更清楚**
5. **更适合复杂项目中的多版本、branch governance、证据治理场景**

## 9. 推荐定位

最稳的产品叙事不是：

> “Beacon 也应该成为一个全能 AI 软件工厂”

而是：

> “Beacon 是把 AI 交付能力放进正式 requirement truth、contract、gate、archive 治理体系里的内核。”

在这个定位下，Beacon 对 gstack 的正确吸收方式是：

- 吸收 `decision surface thickness`
- 吸收 `route explainability`
- 吸收 `learning recall`
- 吸收 `human-readable progress`
- 吸收 `runtime evidence priority`

但不吸收：

- persona-first public narrative
- autonomy-first workflow philosophy
- browser/design/deploy 作为默认产品主轴

## 10. 建议的后续演进候选

以下候选与当前 `v1.4.0` 冻结方向兼容度最高：

### Candidate A: Support Surface Explainability Deepening

目标：

- 让 `help / status / ask / brainstorm` 更明确回答：
  - 为什么推荐这条 route
  - 为什么不是另一条
  - 当前缺什么证据
  - 下一步会产出什么

### Candidate B: Learning Consumption by Default

目标：

- 在 `prd / user-story / test-case / implement / qa / release` 启动时按需注入相关 learning
- 明确区分：
  - prior pattern
  - warning
  - stale learning
  - non-authoritative hint

### Candidate C: Runtime Evidence Thickening Under QA/Release

目标：

- 不新增主命令
- 但增强 `qa / release / real-project-validation` 的真实运行态证据能力
- 保持证据仍回写到现有 gate / release contract，而不是长出并行真相

### Candidate D: Public Benchmark Note for Skill Visibility Governance

目标：

- 把 Beacon 当前 skill catalog 分层说明清楚：
  - default visible
  - conditional recommendation
  - advanced/project-specific
  - proof/analysis only

这会直接提升 Beacon 的人类面理解成本表现。

## 11. 结论

`gstack` 给 Beacon 最大的启发，不是“多几个 skill”，也不是“做 23 个角色”。

真正值得吸收的是：

> 把 AI 从一个会响应的模型，升级成一个有专业关口、有解释能力、有经验复用、有运行态证据的交付系统。

而 Beacon 当前最有价值的坚持是：

> 这套交付系统必须受 frozen truth、compiled contract、implement/qa gate、archive governance 的严格约束。

因此，Beacon 的最优路径不是成为 `gstack with docs`，而是成为：

> `governed AI delivery kernel with a thicker human decision surface`

## 12. References

- [`docs/beacon/global-boundaries.md`](../beacon/global-boundaries.md)
- [`docs/beacon/v1.4.0/SUMMARY.md`](../beacon/v1.4.0/SUMMARY.md)
- [`docs/beacon/v1.4.0/execution/architecture-blueprint.md`](../beacon/v1.4.0/execution/architecture-blueprint.md)
- [`docs/beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md`](../beacon/v1.4.0/prd/beacon-v1.4.0-lightweight-kernel-and-core-surface-refactor.md)
- [`docs/beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md`](../beacon/v1.4.0/prd/beacon-v1.4.0-llm-decision-surface-and-learning-loop-evolution.md)
- [`docs/beacon/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md`](../beacon/v1.4.0/prd/beacon-v1.4.0-branch-governance-human-surface-and-implement-gate.md)
- [`skills/beacon/SKILL.md`](../../skills/beacon/SKILL.md)
- [`docs/brainstorms/2026-05-11-beacon-brainstorm-analyze-garrytan-gstack-current-repository-facts-its-professional-role-capabilit.md`](../brainstorms/2026-05-11-beacon-brainstorm-analyze-garrytan-gstack-current-repository-facts-its-professional-role-capabilit.md)
- [`docs/brainstorms/2026-05-11-beacon-brainstorm-converge-a-full-beacon-human-surface-and-sub-skill-benchmark-against-garrytan-gs.md`](../brainstorms/2026-05-11-beacon-brainstorm-converge-a-full-beacon-human-surface-and-sub-skill-benchmark-against-garrytan-gs.md)
- [`/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/README.md`](/Users/apple/Developer/Personal/oss-sync/agents/agent-skills/gstack/README.md)
- [`https://github.com/garrytan/gstack`](https://github.com/garrytan/gstack)
