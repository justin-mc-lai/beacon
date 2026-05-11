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
