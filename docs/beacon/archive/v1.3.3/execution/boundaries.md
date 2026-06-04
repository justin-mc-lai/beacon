# Beacon v1.3.3 版本约束映射

本文件不再声明 Beacon 全局约束本体。

Beacon 的跨版本全局约束已上提到：

- [`docs/beacon/global-boundaries.md`](../../global-boundaries.md)

`v1.3.3` 在本版本中继续沿袭并具体化这些全局约束，特别是：

1. 人类主流程仍保持：

```text
prd
→ user-story
→ test-case
→ implement
→ qa
→ release
```

2. `team/subagent/precheck` 的复杂度默认留在机器内部。
3. `implement` 与 `qa` 仍是人类唯一主执行入口。
4. 瘦身目标只能做 core 收口，不得借机扩张新的公开主面。
5. 外部 skill / runner / orchestration 只能退到 compatibility plane，不得重新回到默认主叙事。

本版本的具体落点请继续阅读：

- [`./architecture-blueprint.md`](./architecture-blueprint.md)
- [`../prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md`](../prd/beacon-v1.3.3-core-slimming-and-external-skill-demotion.md)
- [`./beacon-v1.3.3-core-slimming-and-external-skill-demotion-slimming-checklist.md`](./beacon-v1.3.3-core-slimming-and-external-skill-demotion-slimming-checklist.md)
