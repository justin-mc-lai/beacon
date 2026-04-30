---
date: 2026-04-24
topic: beacon-v1-3-8-archive-command-integration
---

# Beacon v1.3.8 Archive Command Integration

## What We're Building

`beacon-v1.3.8-archive-governance-and-historical-requirement-isolation` 应该收敛成一个新增的人类可见子命令，而不是仅靠 `help`、`status`、`doctor`、`gate` 的隐式内部行为完成。

原因很直接：归档治理本质上是一个显式的人类治理动作。操作者需要明确触发“哪些 truth 继续 active，哪些 truth 退出当前 delivery plane，但保留可追溯性”。如果没有专门的人类命令，归档只会退化成内部状态字段，最终还是被历史需求继续污染当前版本。

但它也不能成为新的主生命周期 stage。`archive` 不是 `prd -> user-story -> test-case -> prototype -> implement -> qa -> release` 之间的新阶段，而是一个版本治理 support command，用于在版本推进、release 完成、change 收敛、版本切换时，对历史 truth 做正式退出与索引整理。

## Why This Approach

### Approach A: 新增顶层 `archive` 支持命令

推荐。

形态：

```text
beacon archive plan
beacon archive apply
beacon archive status
beacon archive explain
```

**Pros:**
- 人类心智清晰，`archive` 成为显式治理面，而不是分散在多个命令里的隐式副作用。
- 与 PRD 的“version archive plan / archive index / archive boundary”直接对齐。
- 便于 `help`、`status`、`brainstorm`、`implement`、`gate` 统一读取同一份 archive read model。

**Cons:**
- 会让 Beacon 的支持命令从 `7+3` 演进到 `7+4`。
- 需要重新定义 Beacon 对外公开的人类 surface 文案与 skill 路由。

**Best when:** 归档治理被认为是长期稳定的一等能力，而不是一次性迁移逻辑。

### Approach B: 挂到 `version archive` 下作为 version 子命令

可行，但不推荐作为主方案。

形态：

```text
beacon version archive plan
beacon version archive apply
```

**Pros:**
- 不新增顶层命令，表面更克制。
- 更强调 archive 是版本治理，而不是 feature stage。

**Cons:**
- 归档影响的不只是 version docs，还包括 feature truth、consumer boundary、gate 行为。
- 人类不容易把“历史需求退出当前生效面”直觉映射到 `version` 命名空间。
- 后续 `help/status` 推荐动作会更绕。

**Best when:** 团队坚持顶层 surface 必须极小，并接受 archive discoverability 降低。

### Approach C: 不新增命令，只让 `doctor/gate/status` 内部消费 archive

不推荐。

**Pros:**
- 表面最小。
- 初期实现成本最低。

**Cons:**
- 违反这条 PRD 的核心目标：归档治理缺少显式的人类触发面。
- 操作者不知道什么时候“正式归档”已经发生。
- archive plan / archive index 会持续漂浮在内部逻辑里，难以形成稳定操作规约。

**Best when:** 仅做一次性内部迁移，而不是产品能力。

## Recommendation

采用 **Approach A**：新增顶层 support command `archive`，但明确声明它不是主生命周期 stage。

推荐把 Beacon 的人类 surface 调整为：

```text
primary lifecycle:
prd -> user-story -> test-case -> prototype -> implement -> qa -> release

support:
help / status / doctor / archive
```

这样做的关键好处是：

1. 生命周期不被污染。
2. 归档治理成为正式、可解释、可审计的人类动作。
3. 其他消费面只读 archive truth，不各自发明 archive 逻辑。

## Key Decisions

- 决策 1：`archive` 应是顶层 support command，不应挂在 `release`、`version`、`doctor` 下面。
  理由：它横跨 version truth、feature truth、consumer boundary、gate behavior，是独立治理面。

- 决策 2：`archive` 默认先做 `plan`，再做 `apply`，不能直接 destructive apply。
  理由：归档治理需要先给出候选退出集、影响面、回溯引用，再由人类确认。

- 决策 3：`archive` 的 source of truth 必须是 machine-readable archive contract，而不是 markdown 文案。
  理由：PRD 明确要求主要消费面读取 archive boundary，不能靠文档解析。

- 决策 4：现有消费面不自己实现 archive 规则，只调用统一 archive resolver。
  理由：否则 `help/status/brainstorm/implement/gate` 会再次漂移。

- 决策 5：`archive` 先解决 requirement truth 归档，再逐步扩展到 technical archive / learnable memory。
  理由：YAGNI。先把“历史 requirement 不污染当前 delivery plane”做稳。

## Proposed Command Shape

最小可交付子命令集：

```text
beacon archive plan --project-root . --version v1.3.8 [--json]
beacon archive apply --project-root . --version v1.3.8 [--confirm]
beacon archive status --project-root . --version v1.3.8 [--json]
beacon archive explain --feature "<feature>" --project-root . --version v1.3.8 [--json]
```

### `archive plan`

职责：

- 生成版本级 archive candidate set
- 输出 `archive-plan` 与 `archive-index`
- 标出：
  - active feature set
  - superseded features
  - archived-learnable refs
  - archived-reference-only refs
  - excluded-from-current-delivery refs

默认行为：

- dry-run
- 不写 destructive state

### `archive apply`

职责：

- 将 `plan` 结果写入 machine-readable archive contract
- 更新 feature / version archive metadata
- 刷新 archive index

保护：

- 必须显式确认
- 如果 release/change/freeze 状态不满足，阻断 apply

### `archive status`

职责：

- 查看当前版本 archive governance 状态
- 展示 archive drift、未归档 superseded feature、consumer unresolved references

### `archive explain`

职责：

- 解释单个 feature 或单个历史文档为什么被判定为：
  - active
  - superseded
  - archived-learnable
  - archived-reference-only

## Proposed Runtime/Data Integration

### New Machine Truth

建议新增：

- `docs/beacon/<version>/.machine/archive/archive-plan.json`
- `docs/beacon/<version>/execution/archive-plan.md`
- `docs/beacon/<version>/.machine/archive/archive-index.json`
- `docs/beacon/<version>/execution/archive-index.md`
- `docs/beacon/<version>/.machine/archive/feature-archive-<feature_slug>.json`

最小字段：

```json
{
  "version": "v1.3.8",
  "status_model": [
    "active",
    "superseded",
    "archived-learnable",
    "archived-reference-only"
  ],
  "current_truth_root": "docs/beacon/v1.3.8",
  "archived_truth_roots": [],
  "active_features": [],
  "archived_features": [],
  "learnable_refs": [],
  "excluded_from_current_delivery": []
}
```

### Consumer Integration

`help/status/brainstorm/memory-friction-evolution/implement/gate` 不直接扫历史文档，而统一走：

```text
archive resolver
-> version archive index
-> feature archive metadata
-> current-delivery inclusion decision
```

### Human Routing

- `help` 在检测到“历史 truth 仍影响当前交付”时，推荐 `beacon archive plan`
- `status` 增加 `archive.health` / `archive.pending` / `archive.next_action`
- `gate` 增加 archive boundary drift 检查
- `release` 在版本完成后可推荐 archive plan，但不自动 apply

## Minimal Implementation Slice

第一阶段只做 4 件事：

1. 暴露 `archive` 顶层命令。
2. 提供 `plan/status/apply/explain` 四个子命令。
3. 落 archive machine truth 与 human projection。
4. 让 `help/status/gate/brainstorm/implement` 改为读统一 archive resolver。

先不做：

- 自动归档所有历史 implementation technical archive
- 复杂的 memory 自动重分类
- 跨版本批量 rewrite

## Open Questions

- `archive apply` 是否必须依赖 `release check pass`，还是允许在 version planning 期间先做局部归档？
- feature 级 archive metadata 应写到独立 `feature-archive-*.json`，还是合并进现有 revision/story state？
- `archived-learnable` 与 `archived-reference-only` 的判定规则是显式人工标记，还是支持一部分自动推导？

## Next Steps

→ 为 `archive` 新子命令起正式 execution blueprint 与 implementation plan。
