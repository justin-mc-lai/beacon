# Research: EmbodiSkill / SkillEvolver 对 Beacon QA 归因底座的借鉴

**Feature**: `embodiskill-skillevolver-qa-attribution-foundation`  
**Version**: `v1.4.10`  
**Status**: `research-input`  
**Date**: `2026-05-25`

## 1. 背景

Beacon 是“真相唯一”的交付协议：frozen requirement truth 位于 `docs/beacon/<version>/`，实现、QA、release 都必须回绑到这条 truth chain。这个架构的稳定性高度依赖 `beacon-qa` 的验收能力。

当前 `beacon-qa` 已经有 layered proof、truth drift route-back、implementation gap route-back、runner admission blocker 等边界，但后续仍需要一个更稳定的底座能力：

> QA 发现问题后，先判断证据链断点属于哪一类，再给出 verdict / route，而不是直接把所有异常都判成产品失败或 release blocker。

这份 research 基于两篇 self-evolving skill 论文，提炼 Beacon 可借鉴的 QA 归因底座，不是 v1.4.10 已冻结 requirement。

## 2. 参考论文与本地来源

### 2.1 入口文章

- 微信文章：`清华连发2篇自进化Skill，Agent彻底活了`
- 本地位置：`/Users/apple/Developer/Personal/personal-brain/sources/web/mp-weixin-qq-com-2-skill-agent.md`
- Web note：`/Users/apple/Developer/Personal/personal-brain/sources/web-notes/mp-weixin-qq-com-2-skill-agent/2026-05-25-101116.md`

### 2.2 EmbodiSkill

- 论文标题：`EmbodiSkill: Skill-Aware Reflection for Self-Evolving Embodied Agents`
- arXiv: `https://arxiv.org/abs/2605.10332`
- 本地 PDF：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10332-embodiskill.pdf`
- 本地 HTML：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10332-embodiskill.html`
- 本地 source tar：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10332-embodiskill-source.tar`
- 本地 arXiv 抓取笔记：`/Users/apple/Developer/Personal/personal-brain/sources/web/arxiv-org-embodiskill-skill-aware-reflection-for-self-evolving-embodied-agents.md`

EmbodiSkill 的关键能力是 skill-aware reflection：失败后不是马上改 skill，而是先判断失败是 skill 本身错了，还是 agent 没按有效 skill 执行。

论文中的四类 reflection：

- `Discovery`: 成功轨迹暴露新 skill 内容。
- `Optimization`: 成功轨迹显示已有 skill 可优化。
- `SkillDefect`: 失败来自 skill 内容错误、缺漏或不够具体。
- `ExecutionLapse`: skill 内容有效，但 agent 执行时没落实。

### 2.3 SkillEvolver

- 论文标题：`SkillEvolver: Skill Learning as a Meta-Skill`
- arXiv: `https://arxiv.org/abs/2605.10500`
- 本地 PDF：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10500-skillevolver.pdf`
- 本地 HTML：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10500-skillevolver.html`
- 本地 source tar：`/Users/apple/Developer/Personal/personal-brain/sources/papers/2605.10500-skillevolver-source.tar`
- 本地 arXiv 抓取笔记：`/Users/apple/Developer/Personal/personal-brain/sources/web/arxiv-org-skillevolver-skill-learning-as-a-meta-skill.md`

SkillEvolver 的关键能力是把 skill learning 做成 meta-skill：通过真实部署试验、成功/失败轨迹对比、局部 patch、独立 auditor，让 skill artifact 逐步进化，而不更新模型权重。

关键机制：

- strategy-diversified exploration：显式生成多种策略，而不是只调采样温度。
- deployment-grounded trial：把候选 skill 交给新的 Domain-Skill Agent 真正执行。
- contrastive skill update：比较高 reward 与低 reward 轨迹，把差异转成 skill patch。
- independent audit：检查泄漏、硬编码、未抽象、主入口不可见、silent bypass 等问题。

### 2.4 本地综合分析笔记

- 笔记：`/Users/apple/Developer/Personal/personal-brain/sources/paper-notes/2026-05-25-self-evolving-agent-skills.md`

该笔记给出两篇论文的方法摘要、实验结果、局限和对自研 agent skill 的初步映射。

## 3. 对 Beacon 的核心判断

Beacon 更应该优先吸收 EmbodiSkill，而不是直接照搬 SkillEvolver。

原因：

1. Beacon 是 truth-and-delivery meta-protocol，核心风险是边界漂移，不是缺少自动生成 skill。
2. Beacon QA 是 release 前证据闭环的关键入口，QA 误判会直接破坏“真相唯一”。
3. EmbodiSkill 的失败归因能力正好对应 Beacon QA 的关键问题：发现异常后，要区分 truth drift、implementation gap、coverage gap、runner blocker、QA 执行失误、QA skill 缺陷。
4. SkillEvolver 的自动 patch 能力更适合后续阶段，用于生成改进 proposal，而不是第一阶段直接自动改 Beacon skill。

因此推荐顺序是：

```text
先引入 EmbodiSkill 式 QA 归因层
  -> 稳定 failure family / route-back / evidence reason code
再引入 SkillEvolver 式 trace 对比与 patch proposal
  -> 仅生成候选改动，不直接落地
最后引入 independent auditor
  -> 防止 Beacon meta-protocol 被污染
```

## 4. Beacon QA Attribution Layer 候选设计

建议在 `beacon-qa` 中引入一个前置判断层：

```text
QA evidence attribution layer
```

中文可以叫：

- QA 证据归因层
- 验收归因层
- Failure Attribution Layer

它不替代 `beacon qa run`，也不产生 release verdict。它只负责在 QA verdict 前分类证据断点。

### 4.1 最小 failure taxonomy

候选 reason codes：

```text
implementation_gap
truth_drift
coverage_gap
execution_lapse
skill_defect
runner_admission_blocker
evidence_insufficient
```

含义：

- `implementation_gap`: frozen truth 没变，实现没有满足 AC，应 route back 到 `beacon-implement`。
- `truth_drift`: frozen truth 已不成立，应 route back 到 `beacon-change`。
- `coverage_gap`: test-case / acceptance truth 不足，应 route back 到 `beacon-test-case`。
- `execution_lapse`: QA 规则有效，但本轮 agent 没按规则验收，应重跑或记录 QA 执行注意事项。
- `skill_defect`: `beacon-qa` skill / checklist / route rule 本身有缺陷，应生成 skill patch proposal。
- `runner_admission_blocker`: runner / auth / environment admission 不成立，应 blocked / skip，并记录机器可读 reason。
- `evidence_insufficient`: 证据不足，不能 pass，也不能 release。

### 4.2 Route-back matrix

| Failure family | Route | Gate meaning |
| --- | --- | --- |
| `implementation_gap` | `beacon-implement` | implementation repair required |
| `truth_drift` | `beacon-change` | frozen truth must be reopened |
| `coverage_gap` | `beacon-test-case` | acceptance coverage insufficient |
| `execution_lapse` | continue / rerun QA | QA execution issue, not product failure |
| `skill_defect` | research / change proposal for Beacon skill | Beacon skill improvement candidate |
| `runner_admission_blocker` | blocked / skip | runner admission issue, not product verdict |
| `evidence_insufficient` | continue QA | no release-facing closure |

### 4.3 输出要求

QA attribution 输出至少包含：

```yaml
failure_family: implementation_gap | truth_drift | coverage_gap | execution_lapse | skill_defect | runner_admission_blocker | evidence_insufficient
affected_ac_ids: [...]
evidence_refs: [...]
route_recommendation: beacon-implement | beacon-change | beacon-test-case | beacon-qa | blocked
verdict_boundary: advisory | qa_input | release_blocker_input
notes: ...
```

其中：

- `affected_ac_ids` 不能为空，除非是 runner admission blocker。
- `evidence_refs` 必须指向当前 QA evidence，不允许只引用历史记忆。
- `verdict_boundary` 必须说明该归因是否只是 advisory，还是 formal QA input。

## 5. 与现有 v1.4.10 QA 能力的关系

当前 v1.4.10 已有：

- `beacon-qa` layered proof。
- `beacon-qa-evo-deep` 作为 support analysis。
- `qa-evo-deep-evidence-bound-ac-aware-closure` 要求 deep findings 绑定 AC 和 evidence refs。
- Skill Eval Kit / route stability regression。

本 research 不替代这些能力，而是补一个前置底座：

```text
formal QA evidence
  -> attribution layer
  -> routeable QA verdict / blocked state
  -> release consumes only closed layered proof
```

与 `qa-evo-deep` 的区别：

- `qa-evo-deep` 更像深分析 support surface，覆盖状态机、业务流、权限、数据一致性等。
- `QA attribution layer` 更像 formal QA verdict 前的分类器，负责把失败归因到正确 route。

与 Skill Eval Kit 的区别：

- Skill Eval Kit 评测 Beacon skill / harness 行为是否稳定。
- QA attribution layer 评估当前 feature 的 QA 证据链断点。

## 6. 对 Beacon “真相唯一交付”的价值

Beacon 的主链是：

```text
research -> prd -> user-story -> test-case -> implement -> qa -> release
```

其中 QA 是 truth 和 release 之间的关键门。如果 QA 不能稳定归因，真相唯一会被以下方式破坏：

- 把 truth drift 当成 implementation bug 修。
- 把 coverage gap 当成产品 fail。
- 把 runner admission blocker 当成功能失败。
- 把 QA 执行遗漏当成规则缺陷。
- 把 support finding 当成 QA verdict。
- 把一层证据通过当成 release-ready。

引入 EmbodiSkill 式归因后，QA 的职责更明确：

> QA 不只是判 pass/fail，而是先判证据链断在哪里，再把问题送回正确 surface。

这直接强化 Beacon 的 stable truth delivery：

- truth drift 不会被实现层掩盖。
- coverage gap 不会污染 execution verdict。
- runner blocker 不会变成 false product failure。
- QA skill 缺陷可以被隔离成 Beacon 自身改进候选。
- release 只消费已归因、已闭环的 QA evidence。

## 7. SkillEvolver 可作为后续增强，而不是第一步

SkillEvolver 对 Beacon 的后续价值在于自动生成 skill improvement proposal。

可借鉴机制：

1. 收集 QA 成功 / 失败 traces。
2. 对比正确 route 与错误 route。
3. 找出哪些 failure family 高频出现。
4. 生成局部 patch proposal：
   - 修改 `beacon-qa/SKILL.md` 的 route-back rules。
   - 补充 `references/qa-layer-checklist.md`。
   - 增加 Skill Eval Kit route stability cases。
   - 优化 child skill `description`，避免 silent bypass。
5. 独立 auditor 检查 proposal 是否破坏 Beacon authority boundary。

但第一阶段不建议自动落地 patch，原因：

- Beacon 是 meta-protocol，改错影响所有 child skill。
- 自动 patch 容易把单项目特例写成全局规则。
- QA / release boundary 一旦污染，会破坏真相唯一交付。

因此推荐：

```text
SkillEvolver-like loop = patch proposal only
manual review / change-refreeze required before becoming truth
```

## 8. Auditor 候选检查项

如果后续实现 SkillEvolver-like proposal flow，independent auditor 至少检查：

- 是否把 support surface 提升成 truth source。
- 是否让 `qa-evo-deep` 产生 QA/release verdict。
- 是否绕过 `beacon-change` 改 frozen truth。
- 是否把 runner blocker 写成产品失败。
- 是否把单项目 case 写成通用 Beacon 规则。
- 是否新增主 lifecycle stage。
- 是否破坏 `prd -> user-story -> test-case -> implement -> qa -> release` 主链。
- 是否缺少 AC / evidence refs。
- 是否存在 silent bypass：规则内容正确，但 skill description 无法触发。

## 9. 建议的后续 feature 切分

### P0 候选：`qa-evidence-attribution-layer`

目标：

- 在 `beacon-qa` 中引入 formal QA verdict 前的 attribution layer。
- 输出 `failure_family`、`affected_ac_ids`、`evidence_refs`、`route_recommendation`。
- 保证 truth drift、implementation gap、coverage gap、runner blocker 分流稳定。

不做：

- 不自动修改 skill。
- 不新增 lifecycle stage。
- 不让 support surface 变成 gate。
- 不直接改变 release verdict 规则。

### P1 候选：`qa-attribution-regression-kit`

目标：

- 为常见 QA 失败归因建立 regression fixtures。
- 覆盖 truth drift / implementation gap / coverage gap / runner blocker / evidence insufficient。
- 纳入 Skill Eval Kit route stability。

### P2 候选：`beacon-skill-evolution-proposal-loop`

目标：

- 从 QA traces 中生成 Beacon skill patch proposal。
- 使用 independent auditor 检查 authority boundary。
- 只产出 research / change input，不直接改 frozen truth。

## 10. Decision Priority

如果后续进入 change/refreeze，建议采用以下优先级：

1. Authority boundary violation blocks first。
2. Frozen truth drift routes to `beacon-change`。
3. Missing / weak acceptance coverage routes to `beacon-test-case`。
4. Implementation evidence gap routes to `beacon-implement`。
5. Runner admission blocker returns `blocked/skip` with reason code。
6. QA execution lapse triggers rerun / procedure note，不算 product fail。
7. Beacon skill defect becomes research / change proposal，不在 QA 中静默修 truth。
8. Release only consumes layered QA proof after attribution is closed。

## 11. 结论

EmbodiSkill 对 Beacon 的最直接价值是失败归因：把 QA 问题拆成 truth、implementation、coverage、runner、execution lapse、skill defect 等可路由类型，避免 QA 误判污染“真相唯一”的交付链。

SkillEvolver 对 Beacon 的价值在后续：基于真实 QA traces 生成 skill patch proposal，并通过 independent auditor 防止 Beacon meta-protocol 被污染。

推荐先做：

```text
QA evidence attribution layer
```

而不是先做自动 skill evolution。

这条路径最符合 Beacon 的核心目标：保持 truth 唯一、QA 证据闭环、release 判断稳定。
