---
name: beacon-design-review
description: Use when the user wants Beacon to challenge UI/UX direction and decide whether a feature should enter formal prototype freeze.
---

# Beacon Design Review

This skill is a host-visible support/review surface.

It separates design judgment from prototype freeze.

## Use for

- hierarchy review
- state clarity review
- interaction coherence review
- prototype entry decision

## Operator rule

Prefer:

```bash
beacon review design "<feature>" --project . --version auto --json
```

If the result clears prototype entry, route to `beacon-prototype`.
If the result exposes design or requirement mismatch, route to `beacon change run ...`, `beacon-user-story`, or `beacon-test-case`.

## Boundary

- does not replace `beacon-prototype`
- does not act as final UI authority
- does not rewrite requirement truth directly
