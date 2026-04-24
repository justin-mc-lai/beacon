---
date: 2026-04-24
topic: beacon-v1-3-8-truth-lifecycle
---

# Beacon v1.3.8 Truth Lifecycle Brainstorm

## What We're Building

`v1.3.8` 不应被理解成三条彼此独立的小优化，而更像 Beacon 的下一条版本级治理主线：

```text
truth admission
-> truth execution
-> truth retirement
```

对应到这次已经完成的三份 research，正好形成一条完整链路：

1. `PRD executable diagram truth layer`
   - 解决 truth admission
   - 让复杂业务 feature 在 freeze 前就进入“可执行真相面”
2. `post-freeze team -> ralph sequencing and host-prompt trace`
   - 解决 truth execution
   - 让冻结后的真实交付顺序、宿主提示词驱动面、执行证据闭环进入产品合同
3. `archive governance and historical requirement isolation`
   - 解决 truth retirement
   - 让历史 requirement 与历史 artifacts 正式退出当前生效面

所以 `v1.3.8` 最合理的版本主题不是“再补三个功能”，而是：

> 把 Beacon 从“当前时点谁是真相”推进到“真相如何进入、如何被执行、如何在历史上退场”的全生命周期治理。

## Why This Approach

### Approach A: 先只做 archive governance

优点：

- 直接响应“历史需求不要继续污染当前迭代”
- 版本主题最集中

缺点：

- 如果 admission 和 execution 还不够结构化，archive 归档的仍然只是低质量或弱结构 truth
- 只能解决“旧真相如何退场”，不能解决“新真相如何更稳进入系统”

### Approach B: 先只做 team/Ralph 和 prompt trace

优点：

- 最贴近 rolo 真实交付痛点
- 用户感知最强

缺点：

- 这更像 execution contract 增强，不足以构成 `v1.3.8` 的完整版本主线
- 不能解决历史失效隔离

### Approach C: 先只做 PRD diagram truth layer

优点：

- 最符合第一性原理，先把 truth 建模做对

缺点：

- 仍然缺少冻结后执行收口与历史退场机制
- 只改善入口，不改善版本闭环

### Recommended: Approach D: One Truth Lifecycle Release

把三条 research 合成一个版本主题，但保持它们是三个 feature line：

1. truth admission
2. truth execution
3. truth retirement

这样做的好处是：

- 逻辑完整
- 版本叙事清晰
- 不会把 `v1.3.8` 做成零散补丁集合

## Key Decisions

- `v1.3.8` 的主标题应围绕 `truth lifecycle governance`，而不是单个命令增强。
- 三条 feature 仍然保留，但不应平行散列；它们应被明确标注为：
  - admission
  - execution
  - retirement
- archive governance 应作为 `v1.3.8` 的最终收口层，因为它直接决定历史需求如何退出当前有效面。
- `team -> ralph` 与 `host_prompt_trace` 不应被理解为体验优化，而应被定义为 execution truth contract。
- PRD diagram truth layer 不应被理解为文档美化，而应被定义为 admission truth contract。
- `v1.3.8` 不应新增新的公开一级主生命周期 stage；仍然保持：
  - `prd -> user-story -> test-case -> prototype -> implement -> qa -> release`
- `beacon-brainstorm` 继续保持 read-only sidecar，只负责在 freeze 前或版本演进前做收敛，不直接改正式 truth。

## Suggested Feature Topology

### Feature 1

- name:
  - `beacon-v1.3.8-prd-executable-diagram-truth-layer`
- role:
  - truth admission
- core promise:
  - 复杂业务在 freeze 前必须进入“可执行真相面”

### Feature 2

- name:
  - `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`
- role:
  - truth execution
- core promise:
  - 冻结后的真实交付顺序和宿主驱动面必须进入 formal execution evidence

### Feature 3

- name:
  - `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`
- role:
  - truth retirement
- core promise:
  - 历史 truth 必须可追溯，但不能继续污染当前实现面

## Suggested Version Narrative

推荐把 `v1.3.8` 对外叙事统一成：

```text
Before v1.3.8:
Beacon knows how to freeze and verify truth.

After v1.3.8:
Beacon governs the whole truth lifecycle:
how truth enters,
how truth drives execution,
and how truth leaves the active plane without being lost.
```

## Open Questions

- `archive governance` 是不是要作为 `v1.3.8` 的唯一 release headline，而另外两条作为 supporting feature？
- `host_prompt_trace` 应该写到 `.beacon/implement/<run>/`，还是共享 `.beacon/state/` 平面？
- `PRD executable diagram truth layer` 是否只在复杂业务条件下触发，而不是所有 feature 默认开启？
- `archive plan` 是按 version 生成，还是 version + feature 双层生成？
- gate 是否在 `v1.3.8` 就阻断“历史 requirement 误入当前实现面”，还是先只做 warn + routing？

## Recommendation

推荐把 `v1.3.8` 定义成：

- version theme:
  - `Beacon Truth Lifecycle Governance`

推荐的 feature 顺序：

1. `beacon-v1.3.8-prd-executable-diagram-truth-layer`
2. `beacon-v1.3.8-post-freeze-team-ralph-sequencing-and-host-prompt-trace`
3. `beacon-v1.3.8-archive-governance-and-historical-requirement-isolation`

推荐的原因：

- 先把 truth admission 做结构化
- 再把 truth execution 做证据化
- 最后把 truth retirement 做治理化

这样 archive 不会归档一堆弱结构材料，execution 也不会继续建立在叙述型 truth 上。

## Next Steps

优先进入正式需求线时，建议不是三条一起平推，而是：

1. 先起 `v1.3.8` 版本级 PRD 总线
2. 在总线里定义三条 feature 的 admission / execution / retirement 关系
3. 再逐条拆到 feature PRD / user-story / test-case

如果要极简推进，第一条正式 PRD 应先写：

- `Beacon v1.3.8 truth lifecycle governance`

然后把三条 feature 作为内部分节或后续子线。
