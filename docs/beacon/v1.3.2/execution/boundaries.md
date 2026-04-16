# Beacon v1.3.2 版本约束映射

本文件不再声明 Beacon 全局约束本体。

Beacon 的跨版本全局约束已上提到：

- [`docs/beacon/global-boundaries.md`](../../global-boundaries.md)

`v1.3.2` 在本版本中继续沿袭并具体化这些全局约束，特别是：

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
4. `v1.3.2` 只讨论 Beacon skill 在当前宿主中的原生 subagent/team 能力，不引入多运行时桥接叙事。

本版本的具体落点请继续阅读：

- [`./implement-execution-modes-blueprint.md`](./implement-execution-modes-blueprint.md)
- [`./implement-command-contract.md`](./implement-command-contract.md)
- [`./qa-iterative-browser-contract.md`](./qa-iterative-browser-contract.md)
- [`./ralph-closure-state-machine.md`](./ralph-closure-state-machine.md)
