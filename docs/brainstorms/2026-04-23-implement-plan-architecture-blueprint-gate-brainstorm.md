---
date: 2026-04-23
topic: implement-plan-architecture-blueprint-gate
---

# Implement Plan Architecture Blueprint Gate

## What We're Building

我们要补的不是一个新命令，而是一条更稳定的 `implement plan` 技术交付基线。

当前 Beacon 在正式实现前，已经会生成 deterministic implementation contract、git workflow contract、implementation plan，也已经在 `implement run` 和 `release gate` 中消费这些信息。但同一组“实现服务名 / 开发 git 分支 / 是否使用 worktree / 可写服务范围”没有一个稳定的、面向人类审核的版本级锚点。`architecture-blueprint.md` 现在存在，却还没有承担这部分 plan-time truth。

目标是让 `implement plan` 在生成时就把这组前置实现基础信息写进 `docs/beacon/vx.y.z/execution/architecture-blueprint.md` 的固定模板块，并让 blueprint、deterministic contract、git workflow contract、implementation plan 在 gate 中严格一致。

## Why This Approach

我看下来有三个可选方向。

### Approach A: 继续以 feature contract 为主，blueprint 只做说明

保留当前逻辑，只在 `architecture-blueprint.md` 里补一段人工说明，不让它进入 gate。

**Pros:**
- 改动最小
- 不会影响当前 plan/run/release 流程

**Cons:**
- 仍然没有统一锚点
- drift 只能靠人工发现
- 不能满足“严格 gate 校验，确保一致”

**Best when:** 只想补文档，不想改 contract ownership。

### Approach B: 把 `architecture-blueprint.md` 提升为 plan-time human baseline mirror

在 `architecture-blueprint.md` 中新增固定模板块，记录版本级实现基线；`implement plan` 生成或校验这组字段，然后要求 deterministic contract、git workflow、implementation plan 与之对齐。

**Pros:**
- 同时满足人类可读和 gate 可校验
- 不需要新增第五份 contract
- 与当前 `implement` / `gate` 结构最兼容

**Cons:**
- 要定义 blueprint 与 feature-specific contract 的主从关系
- 需要补 cross-artifact consistency gate

**Best when:** 想最小成本把“说明文档”升级成“正式交付基线镜像”。

### Approach C: 新增独立的 implementation baseline contract

单独新增一份 plan-time baseline json/md，再让 blueprint 只引用它。

**Pros:**
- 机器真相更清晰
- 字段 schema 可以更强约束

**Cons:**
- 又增加一份 contract
- 人类面更分散
- 会削弱 blueprint 的价值

**Best when:** 目标是机器合同优先，而不是人类审核优先。

## Key Decisions

- 推荐 **Approach B**。
  - 原因：它最符合 Beacon 现在的产品方向，能把复杂度留在机器内部，同时不扩张公开命令面。

- `architecture-blueprint.md` 应新增固定模板块，而不是自由文本。
  - 原因：自由文本无法做稳定 gate。

- `implement plan` 应成为第一道一致性 gate，而不是等到 `release` 再发现 drift。
  - 原因：服务名、分支、worktree 这类问题本质上属于实现前置条件。

- gate 只要发现以下问题就阻断：
  - blueprint baseline 缺失
  - blueprint 与 deterministic contract 不一致
  - blueprint 与 git workflow contract 不一致
  - blueprint 与 implementation plan 不一致

- 建议 blueprint 固定模板至少包含：
  - `implementation_source_mode`
  - `workspace_root`
  - `base_branch`
  - `target_branch`
  - `branch_prefix`
  - `use_git_worktree`
  - `worktree_root`
  - `direct_delivery_services`
  - `writable_services`
  - `reference_only_services`
  - `isolation_strategy`

## Open Questions

- blueprint 应该承载版本级默认基线，还是每个 feature 的显式基线分块？
- 多 feature 同版本但服务范围不同的情况下，gate 应采用完全一致还是超集一致？
- technical review contract 是否要继续作为 git workflow seed 的唯一来源，还是改为由 blueprint baseline 统一派生？

## Next Steps

→ 先把这套结论固化进 `v1.3.7` 的 execution blueprint / PRD，再进入实现设计。
