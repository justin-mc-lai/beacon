---
name: beacon-ceo-review
description: Use when the user wants a founder/CEO-grade challenge on a Beacon version or major feature before requirement truth is revised or implementation continues.
---

# Beacon CEO Review

This skill is a host-visible support/review surface.

It does not create a new lifecycle stage.
It challenges requirement direction, scope, and promise level, then routes accepted changes back into Beacon truth surfaces.

## Use for

- problem reframing
- scope challenge
- expand / hold / reduce / reframe judgment
- version-level promise review before implementation

## Operator rule

Prefer:

```bash
beacon review ceo "<feature>" --project . --version auto --focus full --json
```

If the result is `hold`, return to `beacon-implement`.
If the result is `expand`, `reduce`, or `reframe`, route to `beacon change run ...`.

## Boundary

- does not freeze truth directly
- does not replace `beacon-change`
- does not replace `beacon-prd`
