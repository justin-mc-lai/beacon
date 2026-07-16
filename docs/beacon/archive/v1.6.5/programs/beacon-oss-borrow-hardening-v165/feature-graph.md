---
program_slug: beacon-oss-borrow-hardening-v165
version: v1.6.5
plan_mode: interactive
scope_mode: full_parity
lake_or_ocean: 海
program_phase: P3
p4_ack: true
research_ref: docs/beacon/archive/v1.6.5/research/beacon-oss-borrow-hardening-v165-research.md
---

# Feature Graph - v1.6.5 OSS Borrow Hardening

## Intent

v1.6.5 absorbs the accepted `treehouse` and `loop-engineering` lessons into Beacon's governed delivery infrastructure in one version line. The user decision is explicit:

- same-version delivery for all six phases;
- `protected path denylist` becomes a cross-version principle in `global-boundaries`;
- no MVP cut; phase boundaries exist only to keep each lake verifiable.

## First-Principles Split

The ocean breaks into two root problems:

1. Worktree lanes are currently treated as disposable execution scratch space, so repeated feature work loses cache, runtime ledger continuity, and lease visibility.
2. Loop readiness and loop safety are currently distributed across many gates and skill texts, so operators lack one machine-readable readiness surface and reusable loop governance primitives.

Each phase below is a lake: it has a narrow promise, behavior-level acceptance, and its own truth/tests package.

## Phase Graph

### Phase 1 - `beacon-workspace-pool-lease-v165`

Promise: add pooled worktree and durable lease semantics without breaking existing `dedicated-worktree` admission.

Acceptance themes:

- `worktree_mode=pooled` resolves to a reusable lane.
- `workspace admit` creates or reuses a pool entry and writes lease metadata.
- `workspace release` returns a lease to the pool without deleting the worktree.
- stale/corrupt lease state fails closed instead of allowing unsafe reuse.
- dedicated worktree behavior remains compatible.

Dependencies: none.

### Phase 2 - `beacon-loop-readiness-audit-v165`

Promise: add one readiness score that summarizes existing loop/gate signals for humans and CI.

Acceptance themes:

- `beacon doctor loop-audit` emits JSON score 0-100 and L0-L3 level.
- audit consumes existing signals where present: governance metadata, global boundaries, feature truth, QA/release surfaces, workspace admission, pattern registry, budget, run log, failure catalog.
- below-threshold audit exits with code 2 in strict mode and emits repair suggestions.
- score is advisory unless strict mode is explicitly requested.

Dependencies: none.

### Phase 3 - `beacon-loop-pattern-registry-v165`

Promise: move loop patterns out of prose-only skill text into a machine-readable registry.

Acceptance themes:

- version package contains `loop-patterns/registry.yaml`.
- registry records stable pattern id, cadence, risk, harness skills, state surface, phases, human gates, token cost, daily cap, and safety flags.
- validator rejects missing required fields and duplicate ids.
- loop-audit consumes registry presence and validation result.

Dependencies: Phase 2 consumes this when available, but this phase can be built independently.

### Phase 4 - `beacon-protected-path-denylist-v165`

Promise: add cross-version protected paths that automatic Beacon surfaces must fail closed on unless a human explicitly routes the work.

Acceptance themes:

- `global-boundaries.md` contains the protected path denylist principle.
- runtime matcher detects exact paths, globs, and path segments such as secrets, credentials, auth, payments, migrations, and environment files.
- hook/admission write checks return `protected_path_denylist` for blocked paths.
- protected checks are advisory for planner surfaces and fail-closed for write surfaces.

Dependencies: none, but it touches cross-version canonical guidance.

### Phase 5 - `beacon-loop-token-budget-v165`

Promise: make loop cost visible and enforce a soft stop/kill switch before loops run away.

Acceptance themes:

- pattern registry contains token cost and daily cap fields.
- budget utility records run cost estimates and daily totals in `.beacon/loop/budget-ledger.json`.
- `beacon status loop-budget` reports budget state.
- kill switch file or flag pauses automated loop execution with a stable reason code.

Dependencies: Phase 3 registry.

### Phase 6 - `beacon-loop-failure-mode-catalog-v165`

Promise: turn known loop failures into a governed catalog that QA/repair loops can consume.

Acceptance themes:

- version package contains `execution/loop-failure-modes.md`.
- catalog records severity, symptom, cause, mitigation, route, and evidence expectation.
- validator checks required sections for S1/S2/S3 failure modes.
- loop-audit includes catalog readiness as a signal.

Dependencies: Phase 3 registry and v1.6.4 defect-repair-loop taxonomy.

## Topological Order

```text
Phase 1 workspace pool/lease      (independent)
Phase 2 loop readiness audit      (independent)
Phase 3 pattern registry          -> Phase 5 token budget
Phase 4 protected path denylist   (independent, cross-version)
Phase 6 failure-mode catalog      (depends on Phase 3; consumes v1.6.4 repair taxonomy)
```

Recommended execution order: 1 -> 2 -> 3 -> 4 -> 5 -> 6.

## Source Capability Inventory

| Source capability | Beacon landing surface | Phase | Evidence expectation |
|---|---|---:|---|
| Worktree pool reuse | `workspace admit` / pool state | 1 | contract tests create, reuse, release |
| Durable lease | workspace pool lease JSON | 1 | stale/corrupt lease tests |
| In-use detection | workspace admission validation | 1 | blocked payload with reason code |
| Safe-by-default destroy/release | `workspace release` | 1 | release does not delete worktree |
| Loop readiness score | `doctor loop-audit` | 2 | JSON score + strict exit 2 |
| Pattern registry | `loop-patterns/registry.yaml` + validator | 3 | schema validation tests |
| Safety denylist | `global-boundaries` + runtime matcher | 4 | protected path tests |
| Token cost budget | loop budget ledger + status | 5 | daily cap + pause tests |
| Failure catalog | `execution/loop-failure-modes.md` + validator | 6 | required catalog field tests |

## Deferral Ledger

| ID | Capability | Decision |
|---|---|---|
| UD-001 | Same-version delivery for all six phases | accepted |
| UD-002 | Protected path denylist lands in `global-boundaries` | accepted |
| UD-003 | No cross-version deferral of token budget or failure catalog | accepted |
| UD-004 | External source artifacts are advisory; Beacon truth must rely on local verifiable acceptance | accepted |

Deferral ledger contains only accepted decisions.

## P4 Ack

P4 ack is accepted by user decision on 2026-07-09. Route each phase to `beacon-gen-truth` in topological order, with independent freeze gates before implementation.
