# Change: loom-goal-trace-bundle

- **version**: v2.0.0
- **kind**: new lake (User GO Loom 2026-07-18)
- **priority**: P1
- **depends_on**: ['loom-brand-surface', 'beacon-v2-goal-durable-longrun']
- **date**: 2026-07-18

## Intent

Driver turns write agent_trace.v1; goal trace CLI aggregates execution.jsonl + traces

## Downstream

freeze → implement → qa → release (dual-install; do not replace beacon)

## User GO

1. Brand Loom (`loom` + `$loom-goal`)
2. Parallel install with beacon, no default replace
3. Lakes: loom-brand-surface, loom-goal-optional-subagent, loom-goal-trace-bundle
