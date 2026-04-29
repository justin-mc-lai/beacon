---
name: beacon-memory-friction-evolution
description: Use when the user wants Beacon to analyze memory signals, debug friction, or evolution candidates without entering the main 6+3 workflow surface.
---

# Beacon Memory Friction Evolution

This skill routes optional analysis work through Beacon's `memory-friction-evolution` toolkit surface.
For the new primary friction-governance entry, prefer `beacon-friction-intake`.

## Use for

- memory signal digestion
- debug friction clustering
- evolution candidate ranking
- writeback planning for recurring feedback
- deciding whether a friction pattern should be kept, reviewed, or discarded

## Operator rule

Keep this skill outside the main workflow by default.

Prefer:

- `beacon friction-intake run ...` for the primary scan/capture governance flow
- `beacon memory-friction-evolution run ...`
- or `bash skills/beacon/scripts/run_beacon.sh memory-friction-evolution run ...`

Default expectations:

- produce an analysis artifact under `.beacon/analysis/`
- capture candidate evidence refs from `.beacon/memory/` and `.beacon/debug/`
- keep writeback optional, explicit, and reviewable
- distinguish memory-driven candidates from debug/friction-driven candidates

Do not automatically route into:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

unless the user explicitly asks to carry the findings into the main Beacon lifecycle.

## Recommended command shapes

```bash
bash skills/beacon/scripts/run_beacon.sh memory-friction-evolution run \
  --project-root . \
  --version v1.3.6 \
  --mode both \
  --json
```

```bash
bash skills/beacon/scripts/run_beacon.sh memory-friction-evolution run \
  --project-root . \
  --version v1.3.6 \
  --mode friction \
  --with-lighthouse \
  --top-n 3 \
  --json
```

## Recommended output shape

```markdown
# Memory/Friction Evolution Report

## Inputs
## Turn Decisions
## Top Candidates
## Final Decision
```
