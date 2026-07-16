---
name: beacon-goal
description: Beacon Product Goal skill — run-until-done across truth→implement→qa→release. Discover is beacon-loop-goal; this skill finishes queue items with progressive skill load and optional parallel sub-agents (main-star/satellite worktrees).
metadata:
  version: "v1.6.7"
---

# Beacon Goal (Product Goal)

## Role

**Finish** work units from the goal queue until `done_when` is verified.

## Not this skill

- Discovery / triage heartbeat → use **`beacon-loop-goal`**
- Program ocean split → **`beacon-pln-program*`**
- Code-only multi-round repair → **`beacon-gen-implement --mode ralph`** (delegate only)

## Harness

Governor/orchestrator: routes and loads stage skills progressively. Does **not** self-certify QA/release.

## Progressive load (default)

| Stage | Load |
|-------|------|
| truth | beacon-gen-truth / change |
| implement | beacon-gen-implement (+ ralph if delegated) |
| qa | beacon-eval-qa (+ deep if needed) |
| release | beacon-eval-release (human gate) |

## Parallel

If intent/program requests subagents and lakes are independent:
`worktree_mode=main_star_satellite_pool` — one satellite worktree per lake; merge to main-star.

## CLI

```bash
beacon goal start|status|pause|resume|complete|tick --project . --version <v> ...
```

## Boundaries

- release always human-confirmed
- complete requires CLI verifier evidence
- satellites must not author package truth on truth_canonical
