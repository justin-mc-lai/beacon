# Beacon External Reference Study: StatsClaw + awesome-design-md

**Date**: 2026-04-06  
**Intent**: 用两个外部参考仓库校准 Beacon 的产品叙事、可复用资产形态、以及对外证据面。

---

## 1. Inputs

### Beacon current line

- `README.md`
- `docs/beacon/archive/v1.1.12/SUMMARY.md`
- `docs/beacon/archive/v1.1.12/execution/index.md`
- `docs/beacon/archive/v1.1.12/execution/architecture-blueprint.md`
- `docs/beacon/archive/v1.1.12/execution/prototype-design-governance-blueprint.md`

### External reference A: StatsClaw

- Homepage: `https://statsclaw.ai/`
- Paper shortlink: `https://bit.ly/statsclaw`
- Paper resolved PDF: `https://yiqingxu.org/papers/2026_statsclaw/statsclaw.pdf`
- Repo: `https://github.com/statsclaw/statsclaw`
- Current local mirror status:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/statsclaw`

Observed public repo surface on 2026-04-06:

- `statsclaw/statsclaw`
- `statsclaw/example-R2PY`
- `statsclaw/example-probit`
- `statsclaw/example-fect`
- `statsclaw/example-panelView`
- `statsclaw/example-workspace`
- `statsclaw/brain`
- `statsclaw/brain-seedbank`

### External reference B: awesome-design-md

- Repo: `https://github.com/VoltAgent/awesome-design-md`
- Current local mirror status:
  `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md`
- Canonical source map for future import:
  `docs/beacon/research/beacon-open-source-reference-source-map.md`

Key upstream evidence used by this study:

- `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md/README.md`
- `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md/CONTRIBUTING.md`
- `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md/.github/ISSUE_TEMPLATE/design-md-request.yml`
- `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md/design-md/voltagent/DESIGN.md`
- `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md/design-md/voltagent/README.md`

---

## 2. Executive read

StatsClaw 和 awesome-design-md 代表两种不同但互补的外部成功形态：

1. **StatsClaw** 把复杂能力压缩成一个非常清晰的产品故事:
   `统计包开发 + 多 agent 隔离验证 + examples + shared brain`
2. **awesome-design-md** 把抽象设计能力压缩成一个非常清晰的资产故事:
   `一组可复制进项目根目录的 DESIGN.md + 预览页 + 请求模板`

Beacon 当前的强项是治理闭环和版本化文档真相，但对外认知仍然更像“很强的内核”而不是“拿来就用的外部产品面”。

对 Beacon 最有价值的学习不是照抄架构，而是补齐两个对外面：

- **evidence surface**: 用样例仓库/样例工件证明能力真的跑通
- **asset surface**: 用可直接复用的设计/治理模板把抽象能力变成拷贝即用的资产

---

## 3. Reference findings

### 3.1 StatsClaw teaches Beacon to narrow the story

From `statsclaw/statsclaw` public README:

- 顶层定位非常集中: “statistical package development”
- 核心机制不是泛泛 agent，而是明确的 9 角色与隔离流水线
- 产物不是抽象原则，而是：
  - examples
  - workspace artifacts
  - brain repo
  - brain seedbank

Why this matters for Beacon:

- Beacon 当前 `README.md` 的能力面很强，但入口叙事同时覆盖 workflow、governance、profile-aware routing、typed learning plane、takeover baseline gate、prototype、qa、release 等多个层面。
- `docs/beacon/archive/v1.1.12/SUMMARY.md` 和 `execution/architecture-blueprint.md` 说明 Beacon 的核心其实已经很收敛：
  - requirement kernel
  - delivery evidence kernel
  - project execution adapters
  - learning plane
- 也就是说 Beacon 的**内部架构收敛度高于外部叙事收敛度**。

Learning:

- Beacon 对外应优先讲一个更窄的句子，例如：
  - evidence-first delivery governance for AI-assisted product work
  - 或 requirement-to-implementation governance kernel
- 其他能力继续保留，但应后置到 capability matrix，而不是和主叙事争抢首屏心智。

### 3.2 StatsClaw teaches Beacon to ship proof, not only doctrine

StatsClaw 的 README 把 examples 直接列为学习入口，并单独给出 `example-workspace` 展示真实 workflow artifacts。

Beacon 当前也有强文档资产，但主证据面仍以 `docs/beacon/archive/v1.1.12/...` 为主：

- `SUMMARY.md`
- `research/`
- `user-story/`
- `prd/`
- `qa/test-cases/`
- `execution/`
- `release/`

这对于已经相信 Beacon 的人很强，但对于新用户不够“可见”。

Learning:

- Beacon 应补一个和 `example-workspace` 对应的 **reference project gallery**。
- 每个 gallery 项应展示最少闭环：
  - 输入需求
  - 生成的 user story / PRD / test cases
  - implementation-plan
  - verify / gate output
  - release-ready evidence

Minimal Beacon shape:

- `examples/` or `reference-projects/`
- 每个例子带一页 “before task / generated artifacts / release evidence”

### 3.3 awesome-design-md teaches Beacon to package design governance as portable assets

From the public `awesome-design-md` repo materials used by this study:

- 仓库把 DESIGN.md 定义成“plain-text design system document that AI agents read”
- 每个站点目录都是固定三件套：
  - `DESIGN.md`
  - `preview.html`
  - `preview-dark.html`

Beacon 在 `docs/beacon/archive/v1.1.12/execution/prototype-design-governance-blueprint.md` 中已经定义了：

- design brief compiler
- design-system contract normalizer
- guideline auditor
- review outcome / keep-discard iteration

但 Beacon 当前更像“治理协议”，还不是“可复制的 design assets 提供者”。

Learning:

- Beacon 应该允许把其 design governance 输出打包成更直接的资产形态，而不只停在 JSON/contract/review artifacts。
- 对外最容易理解的资产形态就是：
  - `DESIGN.md`
  - style preview
  - brief summary

Minimal Beacon shape:

- 在 prototype/reference-pack 输出旁边，增加可选：
  - `DESIGN.md`
  - `preview.html`
  - `preview-dark.html`
- 使 `design brief` / `design-system contract` 可以投影到人和 agent 都好消费的 artifact，而不是只服务内部 gate。

### 3.4 awesome-design-md teaches Beacon to build a contribution funnel around one artifact type

awesome-design-md 的协作模型非常简单：

- `CONTRIBUTING.md` 只围绕改 DESIGN.md / 请求新 DESIGN.md
- `.github/ISSUE_TEMPLATE/design-md-request.yml` 只问：
  - website URL
  - delivery email
  - sponsor priority
  - additional details

这类单工件贡献入口的优点是：

- 认知负担低
- 社区知道该贡献什么
- 维护者知道该审核什么

Beacon 当前公开面仍偏“系统能力集合”，不够像“可参与的产品资产面”。

Learning:

- Beacon 可以围绕一类标准工件开放贡献入口，而不是一开始开放整个 workflow surface。
- 最适合的候选不是全部 docs，而是某个强复用产物，例如：
  - project profile templates
  - design governance packs
  - release evidence examples
  - requirement-to-implementation example bundles

### 3.5 Beacon should learn asset clarity from awesome-design-md, not visual mimicry

`design-md/voltagent/DESIGN.md` 的价值不在于视觉风格本身，而在于它把抽象审美决策压缩成 LLM 可直接消费的文本格式。

Beacon 已经在 `v1.1.12` 中强调：

- design brief
- design-system contract
- anti-generic restrictions
- web guideline audit

因此 Beacon 不需要把自己变成“设计灵感仓库”。
Beacon 真正要学的是：

- **把已有治理工件投影成更易消费的文本资产**
- **把复杂 pipeline 的价值投影成用户可复制的模板**

### 3.6 The two references together suggest a Beacon dual-surface strategy

StatsClaw 提供的是 **execution proof surface**。  
awesome-design-md 提供的是 **portable asset surface**。

Beacon 当前最缺的正是这两个 surface 的组合：

1. **Proof surface**:
   “Beacon 跑过哪些真实闭环？”
2. **Portable asset surface**:
   “Beacon 输出哪些可以直接拿走用的东西？”

Beacon 现在已有强 kernel：

- version truth
- profile-aware execution routing
- requirement-to-implementation closure
- design governance
- typed learning plane

下一步不应继续只加治理术语，而应把这些内核投影成两类外部可见物。

---

## 4. Concrete recommendations for Beacon

### Recommendation 1: Create a Beacon examples gallery

Add a small, curated gallery that mirrors StatsClaw's evidence discipline.

Suggested shape:

- `examples/greenfield-web-app/`
- `examples/takeover-product-slice/`
- `examples/prototype-to-implementation/`
- `examples/release-gate-closure/`

Each example should show:

- request
- generated requirement materials
- implementation-plan
- verify output
- gate/release output
- what Beacon itself did vs what project-specific adapter did

### Recommendation 2: Export design governance as a human/agent asset pack

Add an optional asset projection on top of current prototype outputs:

- `DESIGN.md`
- `preview.html`
- `preview-dark.html`
- `design-brief.md`

This would turn Beacon's design governance from “internal contract only” into “portable output users can reuse”.

### Recommendation 3: Split Beacon README into one primary narrative and one capability matrix

Borrow StatsClaw's narrative discipline.

Top section should answer only:

- Beacon is for what
- Beacon closes which loop
- Beacon does not replace what

Then move the rest into:

- release-line details
- capability matrix
- command catalog
- project profile / adapter model

### Recommendation 4: Open community contribution around one reusable artifact class

Borrow awesome-design-md's single-artifact contribution funnel.

Start with one of:

- profile template requests
- reference-project example requests
- design-governance pack requests
- release evidence fixture contributions

Do not start by asking the community to understand the entire Beacon kernel.

### Recommendation 5: Make “reference project” a first-class Beacon deliverable

StatsClaw's `example-workspace` works because it proves the artifact trail.

Beacon should make this explicit:

- “reference project” is a supported output form
- docs + machine artifacts + gate evidence can be bundled and published as one reusable package

This would align Beacon's strongest capability with a user-visible artifact.

---

## 5. What Beacon should not copy

### Do not copy StatsClaw's domain specialization

StatsClaw wins by being explicitly about statistical package development.
Beacon should not fake that level of domain focus if its actual product is governance + requirement-to-delivery closure.

### Do not copy awesome-design-md as a style-library business

Beacon should not become a repository of brand clones or visual presets.
Its advantage is governance, evidence, and bounded execution.

### Do not widen core with project-specific execution logic

`docs/beacon/archive/v1.1.12/execution/architecture-blueprint.md` is already correct:

- project execution adapters stay external
- Beacon core remains requirement kernel + delivery evidence kernel

The right move is better projection of outputs, not absorbing downstream implementation stacks.

---

## 6. Suggested next Beacon moves

### Near-term

1. Add one external-facing research or examples index page.
2. Add one reference project bundle that demonstrates full requirement → gate closure.
3. Add one design governance asset projection experiment:
   `DESIGN.md + previews`.

### Mid-term

1. Introduce a request template for example-pack or profile-pack contributions.
2. Publish a sharper README split:
   narrative / evidence / commands.
3. Define a stable portable artifact contract for design outputs and reference projects.

### Long-term

1. Treat Beacon outputs as a reusable product catalog, not only a runtime.
2. Build a small library of canonical example closures across project modes.
3. Let design/review/governance artifacts become shareable objects across projects and sessions.

---

## 7. Bottom line

Beacon already has a stronger governance kernel than both references.

What it can learn from them is not deeper internals, but better outward packaging:

- **from StatsClaw**: tighter story, stronger proof, examples as product evidence
- **from awesome-design-md**: one-asset contribution funnel, portable artifact packaging, copy-into-project usability

If Beacon absorbs those lessons, it stops looking like “a very capable internal doctrine” and starts looking like “a reusable evidence-first delivery product with visible outputs”.
