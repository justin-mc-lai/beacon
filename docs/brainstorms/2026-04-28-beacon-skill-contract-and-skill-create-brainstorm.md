---
date: 2026-04-28
topic: beacon-skill-contract-and-skill-create
---

# Beacon Skill Contract And Skill Create Brainstorm

## What We're Building

现在 Beacon 已经支持通过 `implement --skill` 指定 skill，这意味着 skill 不再只是“给 Codex/Claude 的通用提示资源”，而开始进入 Beacon 的正式实现面。

一旦 skill 进入 `beacon implement`，它就不应该只是一个松散的外部 prompt 包，而应该满足 Beacon 的最小契约：

- 输入怎么进入
- 输出怎么落盘
- 证据怎么回链
- stop / resume 怎么定义
- 哪些 host runtime 支持

否则 `--skill` 虽然存在，但它只能算“手工指定一个适配器”，还不能算高兼容的正式实现面。

这次问题的核心不是“要不要支持 skill”，而是：

1. Beacon skill 是否应该满足 Beacon 规范
2. 是否需要 Beacon 自有 `skill create` / `skill contract` 子 skill
3. 如何让 Beacon 不只局限编码能力，而能稳定支持非编码 deliverable surface

## Why This Approach

### Approach A: 继续把 skill 当松散外部适配器

`implement --skill` 保留，但不要求统一 contract。不同项目自己约定输入输出。

**Pros:**
- 实现最省
- 现有 skill 生态几乎不用动

**Cons:**
- Beacon 无法稳定验证 skill-backed runs
- 非编码场景仍会退化成“人工知道怎么做，Beacon 只负责转发”
- `codex` / `claude` 兼容语义会继续漂移

**Best when:** 你只想把 skill 当 prompt shortcut，而不是正式实现面。

### Approach B: 给 skill 引入 Beacon 最小 contract，但不提供官方 create 能力

定义一份文档规范，让项目自己手工按 Beacon contract 写 skill。

**Pros:**
- 能统一最小真相
- 不强迫马上造新命令

**Cons:**
- adoption 慢
- 容易出现“规范写了，但没人按规范建 skill”

**Best when:** 你先想验证 contract 是否稳定。

### Approach C: 定义 Beacon skill contract，并提供 Beacon 自有 `skill create` 子 skill

把 “Beacon-friendly skill” 当成正式一等对象，但仍隐藏在最小人类面之后。

**Pros:**
- skill 从一开始就按 Beacon truth/build/run/evidence 模型生成
- 更容易支持非编码实现面
- 更容易统一 `codex` / `claude` 差异

**Cons:**
- 需要新增一层规范和脚手架
- 要处理与现有 Codex 官方 `skill-creator`、Anthropic `skill-creator` 的关系

**Best when:** 你要把 `implement --skill` 真正做成高兼容实现面。

我推荐 **Approach C**。

## Key Decisions

- 决定 1：一旦 skill 被 Beacon 作为 `implement` surface 消费，它就应该满足 Beacon contract。
  原因：否则它只是外部 prompt 包，不是正式可验证实现面。

- 决定 2：需要一个 Beacon 自有的 `skill create` 子 skill，但它不取代通用 `skill-creator`。
  原因：通用 skill creator 关注“如何创建一个 skill”，Beacon 关注“如何创建一个可被 Beacon 生命周期消费的 skill”。

- 决定 3：Beacon skill contract 必须优先服务 `implement --skill`，再逐步扩到 `qa` / `doctor` / `archive-validation`。
  原因：先从已有最明确入口做稳，再横向扩展。

- 决定 4：Codex 与 Claude Code 要在 Beacon skill contract 中显式分流。
  原因：两者都能执行 skill，但 execution semantics、workspace assumptions、resume 模式不同。

- 决定 5：Beacon 不新增新的公开一级主命令来暴露 skills。
  原因：skills 是扩展层，不应破坏最小人类面。

## Beacon Skill 是否应该满足 Beacon 规范

答案是：**应该，但只要求满足 Beacon 的最小 contract，不要求把所有 skill 都重写成 Beacon 内建格式。**

最小 contract 至少应包含：

### 1. Input Contract

- skill_id
- supported_stages
- supported_host_runtimes
- required_inputs
- optional_inputs
- prompt_boundary_policy

### 2. Output Contract

- output_artifact_family
- machine sinks
- human-readable sinks
- completion criteria
- stop_state semantics
- next_action semantics

### 3. Evidence Contract

- requirement_refs
- evidence_refs
- traceability_refs
- verification obligations

### 4. Runtime Contract

- supports_codex
- supports_claude
- repo_local_required
- workspace_state_required
- context_resume_supported
- handoff_targets

没有这些，Beacon 就很难：

- 做 `team/ralph` 调度
- 做 `qa` handoff
- 做 `release` 收口
- 判断是否真的“实现完成”

## 是否需要 Beacon 自有 `skill create`

答案也是：**需要。**

但这个 `skill create` 不应该是通用 skill creator 的重复品，而应该是：

- `beacon-friendly skill scaffold`
- 或 `beacon skill contract bootstrap`

它要解决的不是：

- 如何写一个通用技能

而是：

- 如何写一个能被 `beacon implement --skill` 直接消费的 skill

### 它应该自动生成什么

一个 Beacon 自有 `skill create` 最小应生成：

1. `SKILL.md`
   - 描述这个 skill 的用途和触发场景

2. `beacon-skill-contract.json` 或等价 machine file
   - host runtime compatibility
   - supported lifecycle stages
   - input/output/evidence contract
   - stop/resume semantics

3. 可选的 `scripts/` / `references/` / `assets/`
   - 供 skill 实现真正执行逻辑

4. 可选的 Beacon projection docs
   - 例如如何被 `implement --skill`、`qa --skill` 消费

### 它不应该做什么

- 不应该新增 Beacon 一级公开命令面
- 不应该替代 Codex 官方 skill creator 的通用能力
- 不应该要求所有现有外部 skill 立即迁移

## 和现有 `skill-creator` 的关系

### Codex / Anthropic skill creator

它们解决的是：

- 如何创建一个通用 skill
- 如何组织 `SKILL.md`、resources、scripts、assets

### Beacon 自有 skill create

它要解决的是：

- 如何创建一个 **可被 Beacon 生命周期消费** 的 skill

所以关系应该是：

```text
generic skill creator
-> creates a skill-shaped package

beacon skill create
-> creates a beacon-compatible skill contract package
```

换句话说：

- 通用 skill creator = 结构脚手架
- Beacon skill create = 生命周期兼容脚手架

## `implement --skill` 是否能支持非编码场景

答案是：**可以，而且应该。**

但前提不是“多加几个说明文档”，而是把 skill-backed implement surface 正式化。

### 适合的非编码场景

- 长文内容生产
- 知识库整理
- 研究资料编译
- Story/workbench 型资产更新
- 运营/配置/规则类交付物

### Beacon 要补的不是新 mode，而是新 contract

不建议新增：

- `mode=skill`

因为这会把实现形态和 skill 适配层混在一起。

更合理的是保留：

- `single`
- `team`
- `ralph`

再让：

- `--skill`

成为实现面适配层。

即：

```text
execution mode = single / team / ralph
surface adapter = code-native / skill-backed
```

## Codex / Claude Code 兼容增强应该怎么分

### Codex 侧

更适合：

- repo-local execution
- patch / file edit
- workspace-aware skill
- long-running skill with artifact family sync

Beacon skill contract 里应强调：

- changed_files
- workspace artifacts
- stop_state
- resumable workbench sinks

### Claude Code 侧

更适合：

- reasoning-heavy orchestration
- convergence / review / explain sidecar
- prompt-boundary-sensitive skill
- context-driven resume

Beacon skill contract 里应强调：

- explanation quality
- prompt/context inheritance
- reviewability
- handoff readability

### 共享面

两边都必须一致的：

- requirement truth
- evidence refs
- acceptance semantics
- transaction lineage

## Open Questions

- Beacon 自有 `skill create` 是做成正式命令，还是先做成内部 skill surface 更稳妥
- `beacon-skill-contract.json` 是否足够，还是需要 human-readable 镜像文档
- skill-backed `qa` 是否也需要和 `implement --skill` 共用同一 contract 文件

## Next Steps

→ 最合理的后续不是直接编码，而是新增一条 Beacon requirement 子线：

1. `beacon skill contract for implement surfaces`
2. `beacon skill create scaffold`
3. `codex / claude host-runtime compatibility for skill-backed runs`

如果只做一个最小版本，我建议先做：

- `Beacon 自有 skill create`
- 输出一份 `beacon-compatible skill contract`
- 先让 `implement --skill` 真正支持非编码工作台场景
