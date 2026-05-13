---
name: beacon-learn
description: Use when the user wants Beacon to recall, audit, or prune learning as a governed decision input instead of passive memory storage.
---

# Beacon Learn

This skill is a host-visible learning governance surface.

It makes learning visible and auditable, while keeping learning advisory rather than truth-defining.

## Use for

- recall prior learning into current routing
- audit which learning influenced a decision
- prune stale or conflicting learning

## Operator rule

Prefer:

```bash
beacon recall governed "<feature>" --project . --version auto --mode audit --json
```

Use `beacon-help` or `beacon-status` after recall when the operator needs route explanation.

## Boundary

- does not directly modify requirement truth
- does not define QA or release verdict
- stale/conflicting learning must be surfaced, not silently trusted

## Examples

- 适用例：
  - “我想知道之前哪些 learning 正在影响这次 route 判断。”
  - “这批 learning 可能过时了，先帮我 audit 或 prune。”
- 不适用例：
  - “我想直接靠 learning 判 release pass/fail。” -> 这不属于 `beacon-learn`
