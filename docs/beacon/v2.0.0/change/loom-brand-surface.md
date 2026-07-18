# Change: loom-brand-surface

- **version**: v2.0.0
- **kind**: new lake (User GO Loom 2026-07-18)
- **priority**: P0
- **depends_on**: []
- **date**: 2026-07-18

## Intent

Loom brand dual-install: package loom, CLI loom, $loom-goal; parallel with beacon; no default replace

## Downstream

freeze → implement → qa → release (dual-install; do not replace beacon)

## User GO

1. Brand Loom (`loom` + `$loom-goal`)
2. Parallel install with beacon, no default replace
3. Lakes: loom-brand-surface, loom-goal-optional-subagent, loom-goal-trace-bundle
