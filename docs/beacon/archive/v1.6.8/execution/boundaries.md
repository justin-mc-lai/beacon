# Workflow Boundaries (v1.6.8)

- program: beacon-prod-ops-hardening-v168
- version: v1.6.8
- workflow_status: delivery
- guardrail: workflow/gate consume only main-chain docs; research is input-only.

## Public entry

- Single facade: `$beacon-goal` / `beacon goal run`
- Hotfix mode: `beacon goal run "…" --mode hotfix --from-version <tag>`
- Longrun: project `goal.longrun_default` (default true for new projects)

## In scope (this version line)

1. version fleet + dual-version productization
2. release profile full/hotfix + evidence self-heal
3. hotfix lane with forward-port + rollback_notes
4. longrun default + auto driver/supervise
5. GoalRun main-axis mount for ops lakes
6. v2/Loom ops philosophy parity (no default replace)

## Out of scope

- Cloud CD engine
- Auto production rollback execution
- Default `BEACON_V2=1` / replacing Beacon with Loom
- Second public skill entry replacing `beacon-goal`
- Submachine self-complete of GoalRun / auto `release_confirmed`

## Material authority

- Feature truth: `docs/beacon/archive/v1.6.8/features/<slug>/`
- Program graph: `docs/beacon/archive/v1.6.8/programs/beacon-prod-ops-hardening-v168/`
- Global boundaries: `docs/beacon/global-boundaries.md`
- Version governance: `docs/beacon/governance/project-version-governance.md`

## Gate contract

- `beacon release check v1.6.8` fail-closed on incomplete formal package
- Evidence repair may write `.beacon` (UD-V168-004); does not rewrite requirement truth
- Human release gate remains mandatory for toolkit publish
