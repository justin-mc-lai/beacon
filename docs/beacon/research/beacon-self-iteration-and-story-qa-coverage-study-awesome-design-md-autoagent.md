# Research: Beacon self-iteration and story-qa coverage study from `awesome-design-md` and `autoagent`

**Date**: 2026-04-08  
**Intent**: fold two external references into Beacon's cross-version research set, then translate them into a concrete research/design direction for:

- Beacon 自迭代自身
- 基于用户故事的 QA 覆盖率基线

**Beacon first principle reminder**:

> Beacon 的根本不是通用 agent runtime，也不是通用 memory 系统。  
> Beacon 的根本是 `PRD → user-story → QA` 这条证据链。  
> 所有自迭代、资产化和覆盖率设计都必须围绕 `PRD/story` 锚点展开。

**Source directories**:

- canonical source map:
  [`./beacon-open-source-reference-source-map.md`](./beacon-open-source-reference-source-map.md)
- `awesome-design-md`:
  `/Users/apple/Developer/Personal/oss-sync/core-skills/awesome-design-md`
- `autoagent`:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/autoagent`
- adjacent autoresearch lineage already mirrored locally:
  `/Users/apple/Developer/Personal/oss-sync/automation/autoresearch/karpathy-autoresearch`

---

## 1. Executive summary

这两个仓库给 Beacon 的启发是互补的：

1. **`awesome-design-md`** 提供了“高质量、可移植、低摩擦资产面”的范式  
   它擅长把抽象能力压缩成：
   - 单一 artifact 类型
   - 固定目录结构
   - 低认知成本贡献入口

2. **`autoagent`** 提供了“极小试验面、自进化回路、keep/discard discipline”的范式  
   它擅长把自迭代问题压缩成：
   - 单一 subject surface
   - 单一主指标
   - 人改 `program.md`，agent 改 harness

对 Beacon 的翻译结论：

> Beacon 下一步如果要自迭代自身，并强化“按用户故事做 QA 覆盖率基线”，最稳的方向不是扩大 runtime，而是建立一个更清晰的 **asset plane + eval plane** 双层结构。

这里有一个必须先锁死的边界：

- `PRD` 定义产品意图与约束
- `user-story` 定义可交付、可验证的用户面
- `QA` 定义证据与放行闭环

所以 Beacon 的 asset plane 与 eval plane 都不应脱离这条主链单独优化。

---

## 2. Reference A: `awesome-design-md`

### 2.1 What it is

`awesome-design-md` 是一个设计资产仓库，不是 agent runtime。

它的核心模式非常简单：

- 一个站点一个目录
- 每个目录固定三件套：
  - `DESIGN.md`
  - `preview.html`
  - `preview-dark.html`
- 每个目录再配一个解释用 `README.md`

根 README 则回答三件事：

1. 这是什么
2. 怎么用
3. 资产清单有哪些

### 2.2 Why it works

它成功的关键不在复杂，而在：

1. **单一 artifact 类型**
   - `DESIGN.md`
2. **固定 package 结构**
   - design doc + preview + readme
3. **易复制**
   - “copy into your project root”
4. **易请求**
   - issue template 只围绕一个 artifact 类型展开

### 2.3 What Beacon should learn

Beacon 最该学的不是设计风格，而是：

#### A. 把抽象能力压缩成标准资产包

Beacon 现在有很多强能力：

- user story
- PRD
- test-case
- implementation plan
- review/gate
- design governance

但对外常常像“能力集合”，不像“易复制资产”。

可借鉴方向：

- 把特定能力输出打包成固定 artifact bundle
- 每类 bundle 提供：
  - machine form
  - human-readable form
  - preview/example

#### B. 对 Beacon 自身可迭代资产做 package 化

特别适合 package 化的不是所有文档，而是：

- QA policy pack
- design governance pack
- requirement rewrite pack
- scorecard pack
- example bundle

#### C. 为 QA 覆盖率建立可复制 baseline bundle

例如一个故事级 QA baseline 包可以固定包含：

- PRD markdown
- story markdown
- AC matrix json
- scenario map json
- qa9 matrix json
- coverage summary
- evidence expectation

如果要让团队真正复用，这种 bundle 比单篇文档更有用。

---

## 3. Reference B: `autoagent`

### 3.1 What it is

`autoagent` 不是通用 agent 平台，而是“像 autoresearch 一样，但针对 agent harness 本身做自迭代”的实验仓库。

它的核心结构很克制：

- `agent.py`
  - 单文件 harness under test
- `program.md`
  - 人类编辑的元指令/组织代码
- `tasks/`
  - benchmark task
- `results.tsv`
  - 实验账本

### 3.2 First-principles value

它最有价值的地方是把自迭代问题拆成两个面：

1. **subject surface**
   - `agent.py`
2. **org/program surface**
   - `program.md`

并且坚持：

- 单一主指标：`score`
- keep/discard 纪律
- benchmark-driven
- 不鼓励 task-specific hacks

### 3.3 What Beacon should learn

Beacon 最该学的是自迭代边界，而不是它的 agent harness 代码。

#### A. Beacon 自迭代也必须有极小 subject surface

Beacon 现在最容易失控的点是：

- “想优化很多东西”
- “把所有问题都丢给 learning loop”

正确做法应是：

- 每次只优化一种 policy surface
- 明确禁止直接改整个产品面

候选 subject surfaces：

- `qa_policy`
- `story_scenario_expansion`
- `coverage_thresholds`
- `design_review_thresholds`
- `rewrite_policy`
- `scorecard_policy`

#### B. 让人类改 `program surface`，让 agent 改 `subject surface`

Beacon 也应有类似 `program.md` 的组织说明层。

它负责：

- 实验目标
- budget
- benchmark corpus
- keep/discard 规则
- 允许编辑的 policy surface

而 agent 才去改被允许的 subject surface。

#### C. 用用户故事驱动 benchmark，而不是泛化 narrative

对 Beacon 来说，自迭代最稳的 benchmark 不是“整体感觉更好了”，而是：

- 某一批 PRD clauses
- 某一批 user story
- 某一批 AC
- 某一批 scenario families
- 某一批 verify evidence expectations

换句话说：

> Beacon 最值得优化的不是“更像一个聪明 agent”，而是“更稳定地把 `PRD → story → AC → scenarios → evidence → closure` 这条链做实”。

---

## 4. Joint reading: what these two references mean together

两者合起来，给 Beacon 一个非常清晰的方向：

### 4.1 `awesome-design-md` 解决资产面

它告诉 Beacon：

- 什么东西应该被包装成低摩擦、可复制资产

### 4.2 `autoagent` 解决实验面

它告诉 Beacon：

- 自迭代必须锁在极小且可比较的 subject surface 上

### 4.3 Beacon 应该形成的双层结构

```text
Layer A: Asset Plane
- standard bundles
- examples
- previewable / inspectable packages

Layer B: Eval Plane
- story-based benchmark corpus
- coverage scorecards
- keep/discard ledger
- bounded policy mutation
```

但这个双层结构的中心不是“任意资产”或“任意优化”，而是：

```text
PRD
→ story
→ QA baseline
→ evidence / closure
```

也就是说：

- asset plane 主要服务 `PRD/story/QA` 主链
- eval plane 主要评估 `PRD/story/QA` 主链是否更稳、更全、更少假完成

---

## 5. Design direction for Beacon self-iteration

## 5.1 Proposed self-iteration model

Beacon 自迭代应围绕以下对象，而不是围绕整仓自由演化：

### Program surface

人类编写：

- experiment directive
- target metric
- allowed subject surfaces
- benchmark corpus
- keep/discard rules

### Subject surface

agent 允许修改：

- qa policy config
- scenario generation policy
- coverage scoring thresholds
- review severity mapping
- rewrite prompts/policies

### Benchmark corpus

由用户故事、AC、scenario map、qa matrix 组成。

### Evidence plane

每次迭代必须产出：

- score
- diff
- keep/discard verdict
- changed surface list
- affected story/AC coverage

---

## 5.2 Proposed self-iteration constraints

为避免漂移，建议固定：

1. **单一主指标**
   - 建议首选：`false_complete_rate`

2. **辅助指标**
   - story coverage
   - AC coverage
   - scenario family coverage
   - evidence closure rate
   - operator load

3. **固定预算**
   - max iterations
   - max runtime
   - max command count
   - max changed surfaces

4. **keep/discard discipline**
   - gain > threshold → keep
   - no gain + simpler → keep
   - else discard

---

## 6. Design direction for story-based QA coverage baseline

## 6.1 Problem

Beacon 现在虽然已经有：

- user-story
- AC matrix
- scenario map
- QA9 matrix

但这些产物更多是“生成出来了”，还不够像一个可复用、可对比、可自进化的 baseline 包。

## 6.2 Proposed baseline model

建议把“用户故事基线 QA 覆盖率”正式定义成一个 bundle：

### Story QA Baseline Bundle

- `prd/<feature>.md`
- `user-story/<feature>.md`
- `.machine/user-story/<feature>.json`
- `qa/test-cases/<feature>.md`
- `.machine/qa/<feature>.ac-test-matrix.json`
- `.machine/qa/<feature>.story-scenario-map.json`
- `.machine/qa/<feature>.qa9-matrix.json`
- `coverage-baseline.json`
- `coverage-scorecard.md`

### Required baseline dimensions

1. PRD-to-story traceability
2. story coverage
3. AC coverage
4. executable test coverage
5. scenario family coverage
6. browser / non-browser coverage
7. evidence completeness
8. replayability completeness

## 6.3 Why this matters

一旦 QA baseline bundle 固定下来，Beacon 才能：

- 比较不同 rewrite/policy 是否保住了 PRD intent
- 比较不同 policy 的改进
- 找到 story-native blind spots
- 让自迭代真正有 benchmark target

---

## 7. Proposed concrete solution

## 7.1 Add an asset plane for QA baseline packs

建议新增一个资产面，例如：

```text
docs/beacon/<version>/qa/baselines/
```

每个 baseline pack 对应一个 feature 或一个 scene。

但 baseline pack 的锚点必须固定为：

```text
PRD
→ story
→ QA matrix
→ coverage/evidence scorecard
```

它像 `awesome-design-md` 的 `DESIGN.md + preview` 一样，应做到：

- 结构固定
- 易对比
- 易复用
- 易请求补全

## 7.2 Add a self-iteration plane for bounded policy experiments

建议新增一个实验面，例如：

```text
.beacon/state/eval-lab/
```

但不让它直接修改整仓，而是只允许改：

- `qa_policy`
- `scenario_policy`
- `coverage_policy`
- `review_policy`

## 7.3 Add a scorecard that maps policy change to story coverage gain

每次实验至少输出：

- changed policy surface
- affected stories
- affected ACs
- coverage delta
- false-complete delta
- keep/discard

这样自迭代才不是“模糊调优”，而是“对 story-native QA 能力的受控优化”。

---

## 8. Proposed implementation sequence

最稳的推进顺序是：

1. **定义 baseline bundle contract**
   - 把 story/QA coverage baseline 固定成标准包

2. **定义 scorecard contract**
   - 明确如何评价 coverage gain / false-complete reduction

3. **定义 allowed subject surfaces**
   - 明确自迭代允许改哪些 policy

4. **定义 experiment ledger**
   - 记录 keep/discard

5. **最后再接 agent-driven self-iteration**

不要反过来先上自进化运行时。

---

## 9. Final recommendation

这轮外部调研给 Beacon 的最稳建议是：

1. 从 `awesome-design-md` 学会把复杂能力打包成低摩擦资产
2. 从 `autoagent` 学会把自迭代限制在极小 subject surface
3. 把两者结合成 Beacon 的：
   - QA baseline asset plane
   - bounded self-iteration eval plane

一句话：

> Beacon 不应直接自改整个系统；它应先把“以 `PRD/story` 为锚的 QA baseline”做成固定资产包，再让 agent 只在少数 policy surface 上围绕这些 baseline 做受控迭代。
