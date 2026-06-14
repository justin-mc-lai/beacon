# Execution Index v1.6.0

## Feature

- `beacon-skill-harness-taxonomy-v160`

## Execution Surfaces

- `execution/beacon-loop-usage.md` — **beacon-loop / beacon-run operator guide**（含从小到大示例）
- `execution/beacon-loop-state-spine.md` — loop 进度 spine 语义与 `spine show`
- `execution/boundaries.md`
- `execution/project-skill-qa-evolution-blueprint.md`
- `execution/architecture-blueprint.md`
- `source-architecture/index.md`
- `release/v1.6.0.md`

## Implementation Gate Position

v1.6.0 implementation consumes package-authoritative truth from:

```text
features/<slug>/{truth,tests,tasks,evidence}.md
```

The skill harness rename is a breaking migration. It must not be implemented until the feature package truth and coverage are frozen.
