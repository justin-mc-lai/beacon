# PRD: Beacon Prototype Design Governance Loop（v1.1.12）

## 1. Problem Statement

`v1.1.11` 已经把 Prototype 升级为 page-level reference pack compiler，但当前闭环仍然偏结构真值，而不是真正的设计真值。

目前存在的缺口：

1. design direction 没有 first-class artifact
2. visual system 与 prototype contract 之间缺乏正式绑定
3. web accessibility / interaction guideline 仍未进入强门禁
4. design review finding 不会正式回流下一轮 iteration
5. autoresearch 还没有 bounded 地优化 prototype/design 质量
6. version truth 仍然分散在 skill / runtime / docs 多个口径
7. navigator 仍默认把项目导回 Beacon native 通用执行面
8. project skill orchestration 还缺 capability boundary
9. learning plane 还没有 typed subject surfaces
10. takeover current-state baseline 还不是 runtime gate

结果是 Beacon 可能生成：

- 结构上完整
- review 上 pass
- 但视觉上通用、风格弱、规则覆盖不完整
- 或者被错误地路由到 native implementation / review path
- 或者在未冻结 takeover 基线前提前扩张实现面

这会导致“reference pack 看似可用，实际设计质量并不稳定”。

## 2. Product Principles

1. design truth is part of delivery truth
2. generation guidance 与 review guidance 必须分层
3. bounded autoresearch only
4. review findings 必须机器可消费
5. aesthetics 不应凌驾于 accessibility / interaction truth 之上
6. design system 必须单源约束 prototype pages
7. version truth must be single-sourced
8. Beacon core routes into project execution adapters; it does not absorb them
9. learning plane must optimize judgement surfaces, not execution surfaces
10. takeover current-state truth must freeze before implementation expansion

## 3. Goals

1. 把 design brief 变成 prototype generation 前的正式工件
2. 把 `frontend-design` 变成 Beacon prototype 的 generation-side contract
3. 把 `web-design-guidelines` 变成 Beacon prototype 的 review-side contract
4. 把 `description-as-design` 变成正式 generation mode，而不是松散 prompt 口号
5. 让 autoresearch 有界地补全页面、状态、设计和规则缺口
6. 让 design finding 能驱动下一轮 keep/discard 和 rewrite input
7. 把版本真相做成单一 machine-readable source
8. 让 navigator 先看 profile / stage binding 再给下一步动作
9. 把 project skill orchestration 收缩回 capability-bounded adapter
10. 把 learning plane subject surface typed 化
11. 让 takeover baseline 缺失成为 runtime 级阻断项

## 4. Non-goals

1. 不做设计画布编辑器
2. 不把设计审查等同于像素级 Figma diff
3. 不开放整仓 frontend 自主修改面
4. 不让 aesthetic preference 覆盖 requirement truth
5. 不把 Beacon core 做成任意 shell orchestration 平台
6. 不让 autoresearch 直接学习 gateway/UAT/pipeline/secret 等项目执行面

## 5. Functional Requirements

### FR-001 新增 Design Brief 编译层

新增工件：

- `design-brief.json`

至少包含：

- target audience
- product tone
- visual direction
- typography intent
- palette intent
- motion intent
- differentiation anchor
- constraints
- design_generation_mode
- interactive_prototype_required
- guidance_anchors
- design_mode_references

### FR-002 新增 Design System Contract

新增工件：

- `design-system-contract.json`

至少包含：

- approved font families
- token palette
- spacing rhythm
- radius / shadow rules
- motion rules
- component material rules
- anti-generic restrictions

### FR-002A 新增 Unified Directory + UI Style Analysis

`prototype` 必须把 `index.html` 提升为正式的统一目录页 contract，而不只是生成副产物。

同时新增：

- `ui-style-analysis.json`
- `ui-style-analysis.md`

至少表达：

- unified directory page
- required page/state links
- current visual system summary
- secondary build required artifacts
- extension rules for 二开 / agent continuation

### FR-003 `frontend-design` 进入 generation 面

`prototype plan/create` 应可消费：

- 结构化 requirement materials
- design brief
- design system contract

其职责是生成：

- clear aesthetic direction
- consistent visual system
- non-generic page composition
- description-as-design friendly prompt surface

### FR-003A 参考 GemDesign/Figma 的工作方式，但坚持 Beacon 内生生成

Beacon 不需要成为 Figma 本体，也不需要复刻 `design.gemcoder.com`。

它要借鉴的是这类系统的方法论：

- 上游输入以自然语言 / user story / PRD blocks 为主
- 中间层通过 design brief + design system contract 收敛
- 下游输出是可交互、高保真、可冻结的 reference pack

但真正的原型生成执行面仍是 Beacon 内部的 LLM-driven pipeline。

也就是说，Beacon 需要明确支持：

- `design_generation_mode=description-as-design`
- `design_mode_references=["GemDesign-style ...", "Figma-style ..."]`
- interactive prototype as a first-class Beacon delivery artifact

### FR-004 `web-design-guidelines` 进入 review 面

Beacon 必须在 review 阶段拉取最新 guideline rules，并生成：

- `web-guideline-review.json`
- `web-guideline-review.md`

至少检查：

- skip link / heading hierarchy
- visible focus
- reduced motion
- form label / aria-label
- semantic action/navigation elements
- URL-reflected state
- icon decoration semantics
- image dimensions / loading strategy

### FR-004A Design security 进入 `review design`

Beacon 参考 gstack `cso` 的思路，但不复制它的 infra-first 形态。

在 Beacon 里，软件设计安全应收敛为 `review design` 的正式子面。

至少检查：

- privileged action / role boundary
- upload/file constraints
- secret-handling surfaces
- external integration trust boundary
- auditability / evidence trace

### FR-005 Review 输出继续决策

设计审查后必须给出：

- `design_review_outcome`
- `continue_decision`
- `must_fix_findings`
- `suggested_iteration_inputs`

### FR-006 Bounded Autoresearch Loop

autoresearch 只允许优化：

- page inventory expansion heuristics
- state expansion heuristics
- design brief extraction rules
- design-system normalization rules
- guideline severity mapping
- review thresholds

禁止直接开放：

- arbitrary page HTML self-edit
- unrestricted CSS self-rewrite
- full repository mutation

### FR-007 Keep / Discard Ledger

新增账本或等价记录：

- `.beacon/state/eval-lab/design-keep-discard-log.jsonl`

每轮必须记录：

- changed policy surface
- benchmark outcome
- keep/review/discard
- evidence refs

### FR-008 Freeze / Gate 需要设计真值

`prototype freeze` 与 gate 不应只看结构 review pass，还必须看：

- web guideline critical findings 是否为 0
- design review outcome 是否允许放行
- design-system contract 是否与生成物一致
- description-as-design / interactive prototype contract 是否被保留到冻结态

### FR-009 单一版本真相源

Beacon 必须引入 machine-readable version truth source，至少同时表达：

- current package/runtime line
- current accepted docs line
- active planning line
- line closure status (`planning` / `partial-runtime-facts` / `runtime-closed`)

要求：

- `SKILL.md`
- runtime version export
- help/status payload
- release docs
- docs current-line resolver

都必须从同一 truth source 派生，而不是各自维护描述。

### FR-010 navigator 必须 profile-aware first

help / doctor / status 在推荐 implement / verify / review / gate 前，必须先解析：

- version truth
- project mode (`greenfield` / `takeover` / `project-profiled`)
- feature/profile binding
- stage-local execution surface
- profile gate result

只有缺少 binding 时，才能降级到 Beacon native 通用路径。

### FR-011 Project Execution Adapter Capability Boundary

project skill orchestration 在运行前必须显式校验：

- `supported_stages`
- `capabilities`
- `requires_env`
- `evidence_contract`
- required evidence / required cases alignment

若 node 声明与 skill registry 不一致，系统应：

- blocked
- record reason code
- refuse execution

不得把 profile node 直接当成任意 shell command surface。

### FR-012 Typed Learning Plane Surfaces

learning plane 至少拆分为以下 typed mutation surfaces：

- `qa_policy`
- `design_policy`
- `contract_policy`
- `debug_policy`
- `rewrite_policy`
- `benchmark_policy`

`v1.1.12` 的 design governance 相关 surface 至少应包含：

- design brief extraction rules
- design-system normalization rules
- guideline severity mapping
- review thresholds
- contract drift rules

禁止将以下内容纳入 trainable subject surface：

- project execution command templates
- gateway / UAT / pipeline commands
- secrets / cookies / storage state
- arbitrary repo implementation code

### FR-013 Takeover Baseline Runtime Gate

当 project mode=`takeover` 时，进入 implement 之前必须验证：

- `execution/architecture-blueprint.md`
- `execution/current-state-service-map.md`
- `execution/refactor-boundaries.md`
- current baseline freeze

任一缺失都必须 blocked，并返回 takeover-specific next action。

### FR-014 Project Docs 只作为只读 Contract Inputs

project-specific boundary / service-slice / QA evolution materials 可以进入：

- profile gate
- contract drift detection
- verify/review/gate inputs

但不得自动升格为：

- Beacon core 默认执行动作
- learning plane trainable execution surface
- 通用 native runner 的替代实现

## 6. Suggested Artifact Model

```text
docs/beacon/<version>/prototype/<feature>/
  prototype-plan.json
  design-brief.json
  design-system-contract.json
  theme.json
  tokens.css
  web-guideline-review.json
  web-guideline-review.md
  prototype-review.json
  pages/
  states/

.beacon/state/version-truth/
  current.json

.beacon/state/profile-routing/
  <feature>.json

.beacon/state/takeover-gates/
  <feature>.json
```

## 7. Review/Gate Truth Model

Prototype design governance 至少要回答：

1. 设计方向是否被明确编译
2. 页面是否消费共享设计系统
3. 页面是否落入 generic-style anti-pattern
4. guideline failures 是否存在高严重度阻断项
5. 哪些 finding 必须回流到下一轮 iteration
6. 当前版本真相是否单源且无歧义
7. 当前任务是否被路由到正确 project execution surface
8. learning plane 是否只改 typed judgement surfaces
9. takeover baseline 是否已冻结

## 8. Success Standard

这条线完成时，Beacon 应能稳定做到：

- 在生成前说明将采用的设计方向
- 在生成后说明页面是否遵循共享 design system
- 在评审后说明哪些 guideline finding 阻断 release
- 在下一轮中把这些 finding 回流到 bounded autoresearch 面
- 在执行前说明为什么当前任务走 Beacon native 或 project adapter
- 在任何时候说明当前 planning line / runtime line / docs line 的真实关系
