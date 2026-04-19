# Boundaries: Beacon v1.3.4 Global Runtime Projection and PocketBase Control Plane

**Version**: `v1.3.4`  
**Status**: `release-line bounded`  
**Date**: `2026-04-19`

## 1. One-line boundary

`v1.3.4` adds a machine-local global runtime projection and a visual control plane for Beacon, but it does not replace project-local requirement truth.

```text
truth
  = docs/beacon/<version> + project .beacon
projection
  = sqlite ledger
visual control plane
  = PocketBase-backed Beacon 管理看板
```

## 2. In scope

- cross-project registration for Beacon-managed repositories and workspaces
- normalized runtime projection for `single`, `team`, and `ralph`
- lifecycle aggregation across `prd -> user-story -> test-case -> implement -> qa -> release`
- project health snapshots, blocker observation, and degraded-state reporting
- bounded session metadata for Codex and Claude runs
- deterministic projection write path shared by sqlite and PocketBase mirrors
- doctor/context alignment for split `runtime_version` and `docs_version`
- real-project validation against:
  - `beacon`
  - `rolo`
  - `slow_uni_bmtop`
  - `shopxo_canada`

## 3. Out of scope

- moving formal requirement truth into sqlite or PocketBase
- making PocketBase the source of release or acceptance truth
- absorbing `omc`, `omx`, or other non-Beacon runtimes into the board
- exposing raw host interaction streams, full transcripts, or tmux internals
- adding a new public top-level command family outside existing Beacon surfaces
- treating runtime cache absence as a project-loss condition

## 4. Truth boundary

The following remain authoritative:

- `docs/beacon/<version>/`
- project-local `.beacon/`
- managed Beacon context in `AGENTS.md` / `CLAUDE.md`

The following are projections only:

- sqlite runtime ledger
- PocketBase collections and mirror records
- derived health summaries and board cards

## 5. Runtime evidence boundary

### Formal machine evidence

The following are allowed to enter git when they are part of bounded delivery evidence:

- `docs/beacon/<version>/.machine/user-story/*.json`
- `docs/beacon/<version>/.machine/qa/*.ac-test-matrix.json`
- `docs/beacon/<version>/.machine/qa/*.story-scenario-map.json`
- `docs/beacon/<version>/.machine/execution/*.json`
- `docs/beacon/<version>/.machine/change/*.json`

### Ephemeral runtime cache

The following remain machine-local and may be missing, stale, or rebuilt:

- `.beacon/state/`
- `.beacon/implement/`
- `.beacon/team/`
- `.beacon/debug/`
- `.beacon/evidence/`
- raw host-session and HUD traces

## 6. Determinism boundary

Projection writes must follow one normalized envelope:

1. scan project truth and git/worktree facts
2. run preflight conflict detection
3. emit a normalized projection envelope with stable `source_hash`
4. write the same normalized payload into sqlite and PocketBase mirrors

If branch/worktree/runtime facts conflict, the system may only emit:

- `partial`
- `conflicted`
- `rejected`

It must not silently guess a clean state.

## 7. Human-surface boundary

Human-visible default output must stay lifecycle-first:

- project
- version
- feature
- stage
- progress
- blocker
- next step

Detailed runtime information is secondary and belongs in runtime drilldown only.

## 8. Recovery boundary

If sqlite or PocketBase is unavailable:

- Beacon work must continue from local truth
- board status becomes `degraded` or `rebuild-required`
- doctor may recommend rebuild or projection refresh
- requirement delivery remains valid if local materials are intact

## 9. Release-line guardrail

`v1.3.4` is a docs/runtime supplement line around a `v1.3.3` runtime release base.  
This line is allowed to ship bounded runtime projection and governance improvements without claiming that PocketBase owns formal delivery truth.
