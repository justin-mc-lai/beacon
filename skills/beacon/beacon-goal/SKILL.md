---
name: beacon-goal
description: "【唯一公共入口】一句话目标 → 自动拆需求/编排/实现/验收直到 done。内部可委托 program、truth、implement(ralph)、qa、release；beacon-loop-goal 仅为 support 发现器，用户不必先调它。"
metadata:
  version: "v1.6.7"
  entry: public_primary
  role: product_goal_facade
---

# Beacon Goal — 唯一公共交付入口

## 你要什么就说什么

```text
$beacon-goal
目标：...
项目：.
版本：...
```

**一句话，跑到验收。** 不要先调 `$beacon-loop-goal`。

## 30 秒用法

见：`skills/beacon/examples/goal-one-shot-30s.md`

## 内部会加载什么（渐进，对用户不可见）

| 阶段 | 可能加载 |
|------|----------|
| 拆海 | beacon-pln-program* |
| 需求 | beacon-gen-truth / change |
| 实现 | beacon-gen-implement（+ ralph） |
| 验收 | beacon-eval-qa（+ deep） |
| 发布 | beacon-eval-release（人工门） |
| 发现队列 | beacon-loop-goal（**support only**） |

## 并行（可选）

意图含并行/subagent/多湖时：`main_star_satellite_pool` — 卫星 worktree 各啃一湖，合并回主星。

## CLI

```bash
beacon goal run "<目标>" --project . --version <v>
# 可选别名
beacon run "<目标>" --project . --version <v>
beacon goal status|pause|resume|complete|tick ...
```

## Hard rules

- 禁止自证完成；complete 需 CLI verifier
- release 默认人工确认
- 不得要求用户手搓双 skill 流水线

## Harness

Orchestrator/facade：可路由 generator/evaluator；**不**自己发 QA/release verdict。
