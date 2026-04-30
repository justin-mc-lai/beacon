---
date: 2026-04-28
topic: beacon-skill-contract-without-wrapper
---

# Beacon Skill Contract Without Wrapper Brainstorm

## What We're Building

这次要澄清的不是“要不要支持 skill”，而是：

- Beacon 需要不需要再造一个自己的 `skill create`
- Beacon 如何在不替代 Codex / Claude 的 skill creator 的前提下，把 `implement --skill` 变成高兼容、可验证、可收口的正式实现面

当前结论是：

> **Beacon 不应该再做一个新的 skill creator 包装层。**

因为这会把一个已经由宿主生态解决的问题，再复制一遍，而且复制得不会更好。

Beacon 真正缺的不是 “如何创建 skill”，而是：

- skill 被 Beacon 调用时，应该满足什么 contract
- Beacon 如何读取 skill contract
- Beacon 如何把 skill-backed run 纳入 requirement / evidence / acceptance / release 闭环

所以正确方向不是：

```text
beacon skill create
-> 包一层 codex / claude 的 skill creator
```

而是：

```text
codex / claude 继续负责创建 skill
beacon 负责定义 skill contract
implement --skill 负责消费 contract
qa / release / gate 负责验证 contract 产物
```

## Why This Approach

### Approach A: Beacon 自己再做一层 `skill create` 包装器

让用户通过 Beacon 去调用 Codex / Claude 现有的 skill creator，或生成一套 Beacon 专用 skill 脚手架。

**Pros:**
- 表面上入口统一
- 看起来“Beacon 也有自己的 skill 创建能力”

**Cons:**
- 本质重复造轮子
- 需要同时追宿主 skill 目录结构、frontmatter、资源布局的变化
- Beacon 会被迫承担不属于自己职责的“skill authoring UX”
- 很容易形成三套规范：
  - Codex skill 规范
  - Claude skill 规范
  - Beacon skill 规范

**Best when:** 你真的要做一个新的通用 skill 平台。但 Beacon 不是这个产品。

### Approach B: Beacon 只定义 `skill contract`，不创建 skill

宿主仍然用自己的 skill creator 建 skill，Beacon 只要求：

- 如果这个 skill 要被 `implement --skill` 消费
- 那它必须声明一份 Beacon 可读 contract

**Pros:**
- 职责边界清楚
- 与 Codex / Claude 生态兼容
- Beacon 只做自己最擅长的：
  - lifecycle contract
  - evidence contract
  - release contract

**Cons:**
- 初次接入要多补一份 contract
- 需要把“已有 skill”升级成“Beacon-compatible skill”

**Best when:** 你要高兼容性，而且不想让 Beacon 变成新的 skill 平台。

我推荐 **Approach B**。

## Key Decisions

- 决定 1：Beacon 不做新的 skill creator 包装器。
  原因：这会复制宿主生态的创建层，而 Beacon 真正应该治理的是执行层和验证层。

- 决定 2：Beacon 只定义 `Beacon-compatible skill contract`。
  原因：一旦 skill 被 `implement --skill` 调用，它就不再只是提示资源，而是正式实现面的一部分。

- 决定 3：Codex / Claude 各自的 skill creator 继续保留原生职责。
  原因：skill authoring 属于宿主能力，Beacon 不应侵入。

- 决定 4：Beacon 要补的是 `skill registration + validation + projection + release consumption`。
  原因：这才是 Beacon 生命周期真正缺失的环节。

## 为什么“再做一个 Beacon skill create”不合理

### 1. 职责错位

Codex / Claude 的 skill creator 解决的是：

- skill folder 结构
- `SKILL.md`
- resources / scripts / assets

Beacon 要解决的是：

- skill 被 lifecycle 消费时的 contract
- skill-backed implement 的 stop/resume/evidence/output 语义

这不是同一个层级。

### 2. 会引入双重甚至三重规范

如果 Beacon 再包一层 skill create，很容易变成：

- 原生 skill 规范
- Beacon 包装 skill 规范
- 项目自己再补一层约定

结果是复杂度更高，而不是兼容性更高。

### 3. 会让 Beacon 偏离最小人类面

Beacon 当前应该坚持：

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

如果再往外推一个 skill-creation UX，Beacon 就开始侵入“宿主开发环境管理”，这不是它现在的核心定位。

## Beacon 真正应该提供什么

### 1. Skill Contract Schema

例如：

```json
{
  "schema_version": "1.0",
  "skill_id": "inkos-novel-iteration",
  "supported_stages": ["implement"],
  "supported_host_runtimes": ["codex", "claude"],
  "surface_kind": "skill-backed-implement",
  "input_contract": {},
  "output_contract": {},
  "evidence_contract": {},
  "resume_contract": {}
}
```

### 2. Skill Registration

Beacon 需要知道：

- 这个 skill 在项目里是否存在
- 适用于哪个 stage
- 支持哪个 host runtime
- 需要哪些 artifacts

这应进入：

- `beacon.config.yaml`
- 或单独的 `beacon-skill-contract.json`

### 3. Skill Validation

Beacon 应提供的不是 `create`，而是：

- `validate`
- `explain`
- `project-skill readiness`

比如：

- 这个 skill 能不能被 `implement --skill` 调用
- 缺哪些 contract 字段
- 对 `codex` 支持是否完整
- 对 `claude` 支持是否完整

### 4. Skill-backed Execution Projection

Beacon 要把 skill-backed run 投影进：

- implementation summary
- technical archive
- handoff
- QA matrix
- acceptance envelope

这才是闭环关键。

## Codex / Claude 的调用封装应该怎么做

不是“封装 skill 创建”，而是“封装 skill 消费”。

### Codex 路径

`implement --skill` 在 `codex` 下更适合：

- repo-local execution
- 文件/脚本/workspace 状态强绑定
- artifact family 同步

Beacon 应补：

- `supports_codex = true`
- `workspace_state_required`
- `changed_files`
- `resumable_artifact_family`

### Claude 路径

`implement --skill` 在 `claude` 下更适合：

- reasoning-heavy orchestration
- prompt-boundary-sensitive execution
- 更偏 explain/review/long-context sidecar

Beacon 应补：

- `supports_claude = true`
- `context_resume_supported`
- `human_explanation_required`
- `prompt_boundary_policy`

### 共用封装层

两边都必须被 Beacon 统一消费：

- requirement truth
- evidence refs
- output contract
- handoff envelope
- acceptance semantics

## 最小高兼容方案

我建议 `v1.3.9` 只做这四件事：

1. 定义 `Beacon-compatible skill contract`
2. 让 `beacon.config.yaml` 或 skill sidecar 注册该 contract
3. 让 `implement --skill` 消费这个 contract
4. 让 `qa / release / gate` 验证由 contract 承诺的 artifacts 和 evidence

不做：

- Beacon 自有 `skill create` 包装器
- 复制 Codex / Claude 的 skill authoring 工作流

## Open Questions

- `Beacon-compatible skill contract` 是放项目根 `beacon.config.yaml` 里更合适，还是放到 skill 自己目录下更合适
- 是否需要一个只读命令，如 `beacon implement explain-skill`，帮助操作者理解当前 skill contract
- `qa --skill` 是否要和 `implement --skill` 共用同一 contract，还是拆成两个 surface contract

## Next Steps

→ 如果继续，不建议直接做 `skill create`，而建议新增 requirement 子线：

1. `beacon skill contract for implement surfaces`
2. `host-runtime compatibility for skill-backed runs`
3. `skill-backed evidence / acceptance closure`
