---
name: loom-loop-goal
description: "【Loom support only】发现/排队/心跳。不是公共交付入口。内容路由到 beacon-loop-goal。"
metadata:
  version: "v2.0.0"
  entry: support_only
  brand: Loom
  dual_install_with: beacon-loop-goal
---

# Loom Loop Goal — support only

**不是** `$loom-goal` 的替代。用户日常交付请用 `$loom-goal`。

Phase-1：行为与合同对齐 `$beacon-loop-goal`（发现队列、心跳），**禁止**要求用户先 loop 再 goal。

```text
❌ $loom-loop-goal → $loom-goal   # 禁止双 skill 流水线
✅ $loom-goal 一句话到验收
```

实现路由：复用 `skills/beacon/beacon-loop-goal` 与 `beacon goal consume-queue` 等 support 面。
