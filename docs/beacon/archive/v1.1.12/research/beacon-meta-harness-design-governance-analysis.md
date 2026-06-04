# 调研：Beacon v1.1.12 从 Meta-Harness 借鉴 prototype design governance 的 harness 优化方法

**日期**：2026-04-01
**来源**：
- arXiv: `2603.28052`
- 论文标题：`Meta-Harness: End-to-End Optimization of Model Harnesses`
- Abs 页面：`https://arxiv.org/abs/2603.28052`
- HTML 正文：`https://arxiv.org/html/2603.28052v1`

**目标**：把 Meta-Harness 论文中关于 harness search、filesystem-based feedback、execution-trace diagnosis、Pareto frontier 与 proposer skill 设计的核心思想，转译成 Beacon `v1.1.12` 在 prototype design governance / bounded autoresearch 这条线上的正式研究输入。

---

## 1. 结论摘要

这篇论文对 Beacon `v1.1.12` 的价值，不在于“它又证明了 agent 可以自动改代码”，而在于它把一个更重要的事实讲清楚了：

> 当目标是提升 LLM 系统的整体表现时，真正应该被优化的往往不是模型权重，而是 harness，也就是决定“存什么、取什么、展示什么给模型”的那层代码与规则。

对 Beacon 来说，这直接对应：

- `v1.1.12` 不应把 autoresearch 理解成“让 agent 去改页面”
- 而应把它理解成“让 agent 在受限的 design/prototype harness 面上做外循环优化”

Meta-Harness 给出的最强证据有三类：

1. **优化对象要是 harness，不是成品页面**
   - 论文优化的是 retrieval、memory、prompt construction、orchestration 这类 harness 逻辑，而不是最终任务内容本身。
2. **反馈通道要保留原始 code / score / execution traces**
   - 论文核心设计不是 summary 更聪明，而是允许 proposer 通过 filesystem 选择性读取完整历史。
3. **外循环应最小化，诊断权交给 coding agent**
   - 论文刻意不把搜索逻辑硬编码进复杂元启发式，而是让 proposer 自己决定看哪些历史、修哪些 failure mode、改局部还是重写。

这与 Beacon `v1.1.12` 当前想做的方向高度同向：

- bounded autoresearch divergence
- design brief convergence
- design-system contract normalization
- guideline audit
- keep/discard-backed next iteration

更直接地说：

> Meta-Harness 为 Beacon `v1.1.12` 提供了比 `karpathy/autoresearch` 更贴近“agentic coding + harness engineering”场景的外部论据，说明 design governance 这条线应该优化的是原型生成与评审的 harness，而不是开放最终页面代码的无限自修改。

---

## 2. 调研对象与证据来源

本次结论直接基于论文正文与附录中的以下信息：

### 2.1 主方法定义

- harness 定义：决定模型“存什么、检索什么、向模型呈现什么”的代码层
- Meta-Harness 定义：对 harness 代码做 outer-loop search 的 agentic system

### 2.2 关键实验结果

- 在线文本分类：
  - 相比 state-of-the-art context management baseline 提升 `7.7` 个点
  - 同时使用 `4x` 更少的 context tokens
- retrieval-augmented math reasoning：
  - 在 `200` 道 IMO-level 问题上，平均提升 `4.7` 个点
  - 且跨 `5` 个 held-out models 迁移
- agentic coding：
  - 发现的 harness 超过 TerminalBench-2 上最佳人工基线

### 2.3 对 Beacon 特别重要的实现证据

- proposer 通过 filesystem 访问所有 prior candidates 的：
  - source code
  - evaluation scores
  - execution traces
- 在最重场景下：
  - proposer 每轮中位数读取 `82` 个文件
  - 每轮会参考 `20+` 个 prior candidates
  - 单次 evaluation 最多产生约 `10,000,000` tokens 的诊断信息
- appendix 明确给出 practical tips：
  - write a good skill
  - start with a strong baseline + hard search set
  - log everything in machine-readable form
  - small CLI for querying prior runs
  - automate evaluation outside the proposer

---

## 3. 第一性原理：它真正证明了什么

Meta-Harness 论文真正证明的，不是“更长上下文更好”，也不是“让 agent 更自由就一定更强”，而是：

### 3.1 Harness engineering 是独立优化对象

在论文里，被优化的不是模型参数，也不是单个 prompt 文本，而是完整 harness 程序。

也就是：

- 什么时候存历史
- 存成什么形式
- 什么时候检索
- 检索后怎么组织 prompt
- 状态如何更新

这对 Beacon 的翻译很直接：

- `v1.1.12` 被优化的对象不应是页面 HTML/CSS 本身
- 而应是：
  - design brief extractor
  - design-system normalizer
  - prototype plan compiler
  - guideline severity mapping
  - review threshold / keep-discard policy

换句话说：

> Beacon 的 design governance 闭环，本质上也是 harness engineering。

### 3.2 摘要化反馈不够，原始 trace 才能做因果诊断

论文反复强调，已有 text optimization 方法的问题不是完全没反馈，而是反馈被压得太狠：

- 只看当前 candidate
- 只看 scalar score
- 只看短模板或 summary

而 harness failure 往往是长链路效应：

- 早先一次 retrieval 选择
- 或一次 memory update
- 可能在很多步骤后才暴露出 failure

所以 proposer 必须能回到原始 trace 做因果诊断。

这对 Beacon 的含义是：

- `design_review_outcome` 不能只保留一句总结
- `web-guideline-review.json` 不能只留 pass/fail
- prototype evo 也不能只留最终 score

必须保留：

- 输入 requirement materials
- 生成的 design brief / design-system contract
- renderer 输出
- guideline findings
- visual review findings
- keep/discard decision evidence

### 3.3 外循环最小化，agent 决定怎么读历史

Meta-Harness 的一个关键姿态是：

- outer loop 只负责 propose / evaluate / log
- 不把“应该读哪一轮、应该选哪个 parent、应该走什么 mutation 模板”写死

诊断和 proposal 的主导权交给 coding agent。

这非常适合 Beacon `v1.1.12`，因为 design governance 的 failure mode 本来就多样：

- brief 太空
- style contract 太泛
- 某些页面共享 token 丢失
- 某些 rule severity 设错
- design review finding 没进入下一轮 rewrite

这些都不适合只靠单一模板修补。

---

## 4. Beacon v1.1.12 最值得吸收的 8 个借鉴点

## 4.1 优化 harness 面，而不是开放页面自改

Meta-Harness 优化的是 harness code，而不是 benchmark 内容本身。
Beacon `v1.1.12` 应借这一点，把 bounded autoresearch 的可编辑面限定在：

- design brief extraction rules
- design-system normalization rules
- page/state expansion heuristics
- guideline severity mapping
- review thresholds
- continue / keep / discard policy

不应先开放：

- arbitrary HTML self-edit
- unrestricted CSS rewrite
- full repo mutation

这与 `prd/beacon-prototype-design-governance-loop.md` 中的 FR-006 完全一致，而且被论文提供了更强外部依据。

## 4.2 Full-history filesystem 应成为正式反馈通道

论文最有价值的设计，不是“用了 coding agent”，而是：

- 把 prior candidates 的 code / scores / traces 全部写进 filesystem
- 让 proposer 自己通过 `grep`、`cat` 等方式选择性读取

这对 Beacon 的直接建议是：

`v1.1.12` 若要把 design governance 做成正式 evo 面，应形成统一 experience store，例如：

```text
.beacon/state/prototype-evo/
├── runs/<run_id>/
│   ├── candidate-config.json
│   ├── design-brief.json
│   ├── design-system-contract.json
│   ├── prototype-review.json
│   ├── web-guideline-review.json
│   ├── scorecard.json
│   └── traces/
├── frontier.json
└── keep-discard-log.jsonl
```

重点不是路径名字，而是语义：

- 历史不能只变成 release note
- 必须能被后续 proposer 重新查询

## 4.3 Raw execution traces 是关键，不是可选装饰

论文对照实验显示：

- scores-only 不够
- scores-plus-summary 仍不够
- full interface with raw execution traces 才是关键增益来源

对应到 Beacon：

- 如果只保存 `design_review_outcome=revise`
- 或只保存“审美不够 distinct”的一句总结

那么下一轮几乎无法做高质量 writeback。

Beacon 应要求保留至少这些原始证据：

- page-level render inputs
- page/state expansion diff
- rule-level findings
- severity mapping
- continue_decision reason
- keep/discard reason

## 4.4 设计治理应采用 Pareto frontier，而不必只选单一冠军

论文在多目标场景下明确使用 Pareto dominance。
这对 Beacon 很重要，因为 prototype design governance 天生不是单指标问题。

`v1.1.12` 的候选策略至少同时受这些维度约束：

- design quality
- guideline pass rate
- context cost
- render latency
- operator review load

因此更合理的做法不是只保留“总分最高”的一个策略，而是保留 frontier，例如：

- 最低上下文成本且 design 过线
- 最高设计质量但成本略高
- 最稳的 rule compliance 配置

这与现有 `execution/evo-scorecard-contract.md` 已有方向同向，但可进一步把 `prototype/design` 指标面收紧。

## 4.5 外循环要薄，真正变强的是 proposer

论文刻意避免把复杂 parent-selection、固定 mutation operator、手工总结器堆到外循环里。
它假设：

- coding agent 越强
- 同一 outer loop 就能自然变强

对 Beacon 的启发是：

- `v1.1.12` 不需要先做复杂的 prototype swarm scheduler
- 更应该先把 experience store、artifact model、scorecard 和边界定义好

也就是先把土壤铺平，而不是先做复杂编排。

## 4.6 Skill 文本是最强 steering surface 之一

附录 D 的一个非常重要结论是：

- skill text 的质量，往往比 iteration count 或 population size 更影响搜索质量

而且论文强调 skill 应该：

- 约束 forbidden surfaces
- 约束必须产出的 artifacts
- 约束优化目标
- 但不要替 proposer 提前决定诊断过程

这对 Beacon `v1.1.12` 非常关键，因为这条线本身就依赖 skill 组合：

- `frontend-design`
- `web-design-guidelines`
- prototype renderer / review surfaces

因此 Beacon 应把：

- 什么可以改
- 什么不能改
- 必须输出哪些 artifact
- 哪些 finding 会阻断 keep

写进 skill / execution contract，而不是写成模糊口号。

## 4.7 Search set 应小而难，不能大而糊

附录 D 建议：

- 从 baseline harness 开始
- search set 要对 baseline 足够难
- 规模要小到能高频实验，但足够区分优劣

对应到 Beacon：

prototype evo 不应拿全量页面漫灌评估，而应优先选：

- 最容易暴露 generic aesthetic 的页面
- 最容易丢失 token consistency 的页面
- 最容易触发 accessibility failure 的页面
- 最容易出现 state / route 漏洞的页面

也就是用“小而狠”的 benchmark set 来驱动 design governance 演化。

## 4.8 Queryable logs + evaluator separation 是正式基础设施

附录 D 另外两条建议也很适合 Beacon：

1. log everything in machine-readable form
2. automate evaluation outside the proposer

这意味着 Beacon 不应把 proposer 和 evaluator 混成一个角色。

建议保持：

- proposer：
  - 读历史
  - 提议修改哪一组 design/prototype harness policy
- evaluator：
  - 跑 renderer
  - 跑 guideline audit
  - 生成 scorecard
  - 写回 filesystem

同时补一个极小 CLI 面：

- `beacon prototype-evo frontier`
- `beacon prototype-evo top-k`
- `beacon prototype-evo diff <a> <b>`

这样 agent 才能低成本导航 prior runs。

---

## 5. 对 v1.1.12 的具体落地建议

## 5.1 把当前 evo contract 明确翻译成 prototype/design harness 面

仓库当前已经有：

- `execution/evo-harness-contract.md`
- `execution/evo-scorecard-contract.md`

它们证明 Beacon 已经有 evo 这层语言。
但若要与 Meta-Harness 对齐，`v1.1.12` 还应进一步把 subject surface 收紧到 prototype/design harness：

### 建议 subject surface

- `design_brief_extractor`
- `design_system_normalizer`
- `page_state_expansion_policy`
- `guideline_severity_mapping`
- `prototype_review_thresholds`

### 建议 program surface

- `benchmark_corpus`
- `scorecard_weights`
- `keep_discard_policy`
- `artifact_schema`

## 5.2 把 design governance history 正式变成可检索经验库

如果没有 filesystem history，下一轮就只能靠 narrative memory。
而 Meta-Harness 的核心恰恰证明：

> selective access to prior raw experience 比 summary-first 优化强很多。

因此 Beacon 应正式保留：

- candidate config
- source requirement refs
- design brief
- design system contract
- page/state diffs
- rule findings
- review outcome
- scorecard
- keep/discard verdict

## 5.3 Scorecard 应显式支持多目标前沿

`v1.1.12` 目前已有 single main KPI，但 design governance 这条线更适合：

- 保留主 KPI 作为硬决策主线
- 同时维护 Pareto frontier 作为候选策略库

例如：

- 主 KPI：`false_complete_rate`
- 支撑维度：
  - `guideline_critical_count`
  - `design_distinctness_score`
  - `token_consistency_rate`
  - `operator_load`
  - `context_cost`

这样既保留 keep/discard 简洁性，又不丢掉多目标优化的真实结构。

## 5.4 让 research 输入进入 design brief compiler，而不是只停在参考阅读

Meta-Harness 告诉我们，离线经验若能被转成统一目录结构，会帮助 proposer warm-start。
对 Beacon 的翻译是：

- 外部论文调研
- 历史 review finding
- 旧版本 implementation archive

都不应只是“给人读一遍”的材料。
它们应该被编译到：

- design brief compiler
- benchmark corpus
- review threshold tuning

也就是让 `research/` 进入真正的 harness input，而不是停在文档层。

---

## 6. 不应照搬的部分

## 6.1 不照搬“可全量改 harness code”心智

论文实验中每个 harness 是单文件 Python 程序，问题面比 Beacon prototype design governance 小得多。
Beacon 不能据此得出“所以可以开放整仓 prototype 自修改”。

应借的是：

- 小面
- 固定预算
- 可比较实验
- 完整 trace

不是：

- 任意修改生产代码

## 6.2 不让 proposer 直接接触 test-set truth

论文明确区分：

- search set
- final test-set evaluation

Beacon 也应避免：

- 用最终 gate case 直接反向调参
- 用 release 级样本做即时过拟合

否则 keep/discard 很容易退化成 benchmark memorization。

## 6.3 不把“agentic”误解为“无需显式边界”

Meta-Harness 的 proposer 虽然自由，但边界并不弱：

- skill 定义可改/不可改面
- evaluator 在 proposer 外部
- 最终由 frontier 和 test evaluation 决定

所以 Beacon 不应把这篇论文误译成：

- 更多自治
- 更少 contract

恰恰相反，它证明的是：

> 边界足够清晰时，agent 才能在边界内做更强的诊断和提议。

---

## 7. 结论

对 Beacon `v1.1.12` 来说，Meta-Harness 最值得吸收的一句话可以转译成：

> design governance 的自进化，不该先改页面，而该先改“如何从 requirement 到 prototype 到 review”的 harness。

更具体一点说：

> `v1.1.12` 应把 bounded autoresearch 从“补页面/补状态”的想法，升级为“在 design brief、design-system contract、guideline review 与 keep/discard 这些 harness 面上做 full-history、filesystem-backed、trace-aware 的外循环优化”。

如果 `v1.1.11` 解决的是：

```text
prototype 结构 truthful
```

那么这篇论文给 `v1.1.12` 的额外支撑是：

```text
prototype design governance 也应该作为 harness optimization 问题来设计
```

---

**落盘位置**：`docs/beacon/archive/v1.1.12/research/`
