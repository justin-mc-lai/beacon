# Mode: loop-goal

> Archived from `loom-loop-goal` during 1+6 merge. This is progressive disclosure content for `loom-goal`.

# Loom Loop Goal — support only

**不是** `$loom-goal` 的替代。用户日常交付请用 `$loom-goal`。

Phase-1：行为与合同对齐 `$beacon-loop-goal`（发现队列、心跳），**禁止**要求用户先 loop 再 goal。

```text
❌ $loom-loop-goal → $loom-goal   # 禁止双 skill 流水线
✅ $loom-goal 一句话到验收
```

实现路由：复用 `skills/beacon/beacon-loop-goal` 与 `beacon goal consume-queue` 等 support 面。
