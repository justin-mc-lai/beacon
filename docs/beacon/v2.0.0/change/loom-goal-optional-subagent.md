# Change: loom-goal-optional-subagent

- **version**: v2.0.0
- **kind**: new lake (User GO Loom 2026-07-18)
- **priority**: P0
- **depends_on**: ['loom-brand-surface', 'beacon-v2-main-star-satellite-pool', 'beacon-v2-product-goal-orchestrator']
- **date**: 2026-07-18

## Intent

Opt-in subagent fan-out on goal: parallel_plan → worktree → spawn → merge_to_star; omx/omc behavior checklist parity

## Downstream

freeze → implement → qa → release (dual-install; do not replace beacon)

## User GO

1. Brand Loom (`loom` + `$loom-goal`)
2. Parallel install with beacon, no default replace
3. Lakes: loom-brand-surface, loom-goal-optional-subagent, loom-goal-trace-bundle
