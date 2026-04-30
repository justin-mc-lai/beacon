---
date: 2026-04-23
topic: beacon-human-surface-closure-and-feature-intent-brainstorm-gap
---

# Beacon Human Surface Closure And Feature Intent Brainstorm Gap

## What We're Building

这次要澄清的不是 Beacon 主流程本身，而是：

> 现在 Beacon 暴露给人类的命令与 skills，是否已经足够闭环“任意任务开发”。

结论不是简单的“够”或“不够”。

当前 Beacon 的主生命周期已经相对完整：

```text
prd
-> user-story
-> test-case
-> prototype
-> implement
-> qa
-> release
+ help/status/doctor
```

再加上可见 sidecar：

- `beacon-change`
- `beacon-prd-bootstrap`
- `beacon-toolkit-lighthouse`
- `beacon-memory-friction-evolution`

它已经可以闭环“已知工作流内的开发任务”。

但这里还有一处轻微口径漂移需要记住：

- `beacon-prototype` skill 本身存在
- 但 `using-beacon` 当前公开路由目标没有把 `prototype` 列进去

这说明 Beacon 主生命周期定义已经闭环，但公开路由包装层还没有完全收口到同一口径。

但它还不能自然闭环“任意提示词驱动的开发任务”，尤其是这类真实入口：

- 用户给一个 prompt
- 已有冻结文档
- 已有实现代码
- 用户想先判断这是：
  - scope 内实现
  - scope 内澄清
  - requirement change
  - truth conflict

这一段现在没有一个清晰、可见、可审阅的人类面 sidecar。

`beacon-prd` 可以做 requirement 澄清，但它更偏 requirements drafting。
`beacon-change` 可以处理 frozen 之后的变更，但前提是用户已经知道“这是 change”。
`beacon-toolkit-lighthouse` 能分析代码和业务实现，但它明确是 read-only analysis，不负责把 prompt 和 frozen docs 做 feature-intent 级头暴收口。

所以当前 Beacon 更像：

> 生命周期闭环基本成立，但“实现前的 feature-intent 头暴与路由判断”还有一个可见缺口。

## Why This Approach

### Approach A: 继续让 `beacon-prd` 吸收这类头暴

把 prompt + frozen docs + codebase 的判断都放进 `beacon-prd`。

**Pros:**
- 不新增 skill
- requirement 相关工作都集中在一个入口

**Cons:**
- 会把 `prd` 变成过宽路由器
- 对“已经冻结、只是判断要不要 implement/change”的场景不够自然
- 会让用户误以为任何实现前分析都要回到 PRD

**Best when:** 需求仍然明显未收敛，确实还在 requirement 阶段。

### Approach B: 扩张 `beacon-toolkit-lighthouse`

让 Lighthouse 同时支持代码分析和 prompt/frozen-doc/feature-intent 头暴。

**Pros:**
- 复用现有分析 skill
- 继续保持 sidecar 属性

**Cons:**
- Lighthouse 当前定位是 repo/package/feature-slice 分析，不是 workflow 路由分析
- 会把“系统地图”和“需求/实现边界判断”混在一起
- 容易让 skill 边界变模糊

**Best when:** 只是想做静态分析，不关心后续是 implement 还是 change。

### Approach C: 新增一个可见但非主流程的 `feature-intent brainstorm` sidecar

新增一个专门 skill，输入是：

- 用户 prompt
- 冻结的 `prd / user-story / test-case`
- 可选 `prototype`
- 当前实现上下文

输出是：

- `in_scope_implementation`
- `clarification_within_scope`
- `requirement_change`
- `truth_conflict`

再给出建议路由：

- 继续 `beacon-implement`
- 转 `beacon-change`
- 回 `beacon-prd`

**Pros:**
- 恰好补上现在缺的那一段
- 不污染 `7+3` 主流程
- 和你刚定义的 implement prompt classification 完全对齐
- 适合在 Codex / Claude 内作为 host-visible sidecar 使用

**Cons:**
- 新增一个 skill 面
- 需要明确它和 `lighthouse`、`prd`、`change` 的边界

**Best when:** 用户已经有 prompt、有 frozen docs、有代码上下文，但还没决定应该 implement 还是 change。

推荐采用 **Approach C**。

## Key Decisions

- 决策 1：Beacon 当前的人类主面已经足以闭环 canonical lifecycle，但还不能自然闭环“任意 prompt 驱动的开发任务”。
- 决策 2：缺的不是新的主命令，而是一个可见、可审阅、非主流程的 sidecar skill。
- 决策 3：这个 sidecar 不应并入 `beacon-toolkit-lighthouse`，因为 Lighthouse 应继续专注于代码/系统/feature-slice 分析。
- 决策 4：这个 sidecar 也不应并入 `beacon-prd`，因为它的核心任务不是写需求，而是判断当前 prompt 是否仍落在 frozen truth 内。
- 决策 5：建议新增的 skill 应该围绕 `feature intent` 或 `implement intent` 命名，而不是叫通用 `brainstorm`，否则边界太宽。
- 决策 6：该 skill 的标准输出必须包含四类判定：
  - `in_scope_implementation`
  - `clarification_within_scope`
  - `requirement_change`
  - `truth_conflict`
- 决策 7：该 skill 的标准路由只允许三种：
  - 继续 `beacon-implement`
  - 转 `beacon-change`
  - 回 `beacon-prd`
- 决策 8：该 skill 应产生单一 Markdown 分析产物，既可写到 `.beacon/analysis/`，也可在 Beacon 源迭代时写到 `docs/beacon/<version>/execution/`。

## Proposed Skill Shape

建议新增 skill 名称优先考虑：

- `beacon-feature-intent-brainstorm`

备选：

- `beacon-implement-intent-brainstorm`
- `beacon-frozen-truth-intent-review`

推荐输入：

- `version`
- `feature`
- `prompt`
- frozen `prd / user-story / test-case`
- optional `prototype`
- optional code slice refs

推荐输出结构：

```text
1. Prompt Summary
2. Frozen Truth Refs
3. Implementation Context Refs
4. Scope Classification
5. Evidence
6. Risks
7. Recommended Route
```

## Open Questions

- 这个 skill 是否要允许读取 `prototype`，还是只看 `prd / user-story / test-case` 与代码上下文？
- 它的产物默认放 `.beacon/analysis/` 即可，还是在 Beacon 源迭代时也强制写入 `docs/beacon/<version>/execution/`？
- 它是否只输出分析结论，还是允许一键交给 `beacon-implement` / `beacon-change` 继续执行？

## Next Steps

→ 先把这个 sidecar 的边界冻结为“分析与路由，不直接改 truth，不直接执行 implement”

→ 再起一条 `v1.3.7` requirement 线，定义这个新 skill 的 PRD / user-story / test-case

→ 若要最小试点，优先做：

- skill 名称冻结
- 输入/输出 contract
- Markdown artifact 模板
- 和 `beacon-implement` / `beacon-change` 的 routing contract
