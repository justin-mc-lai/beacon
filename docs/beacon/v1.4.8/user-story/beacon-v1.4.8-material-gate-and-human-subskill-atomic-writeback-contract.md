# User Story: Beacon v1.4.8 物料强 Gate 与人类面子 Skill 原子写回契约

**Feature**: `beacon-v1.4.8-material-gate-and-human-subskill-atomic-writeback-contract`
**Version**: `v1.4.8`
**Revision**: `R3`
**Status**: `frozen`

## Story

**As a** Beacon maintainer, real-project operator, or human skill caller,
**I want** Beacon to require explicit material effects for every human-facing skill invocation and fail closed when required Beacon materials are missing or default-seeded,
**So that** implementation, QA, and release cannot proceed from silent assumptions, fragmented side documents, or advisory findings that were never adopted into governed materials.

## Acceptance Criteria

- AC-001 Beacon defines a required execution host surface contract for execution-bound features, including `execution/index.md`, `execution/architecture-blueprint.md`, delivery baseline, git workflow, and technical review contract.
- AC-002 Beacon blocks `implement` when architecture blueprint projection is missing, drifted, or not bound to the canonical execution host.
- AC-003 Beacon treats branch / service / worktree facts as explicit frozen facts, not as acceptable silent defaults.
- AC-004 Beacon marks `source=version_default`, `source=project_config_seed`, blank `approved_by`, blank `reviewed_at`, or missing managed projection as weak fact sources that cannot unlock implementation by themselves.
- AC-005 Beacon provides a per-subskill material effect registry covering host, truth, execution, gate, support, toolkit, compatibility, and project-local skills.
- AC-006 Beacon requires every human-facing subskill invocation to resolve to `writeback_completed`, `writeback_required`, `obligation_opened`, `truth_reopen_required`, `execution_host_update_required`, `evidence_update_required`, or `read_only_route_only`.
- AC-007 Beacon converts accepted support findings into explicit material updates, release blockers, or `artifact_update_obligations`.
- AC-008 Beacon keeps support surfaces advisory unless their findings are adopted through `change`, truth surfaces, execution host updates, evidence updates, or obligations.
- AC-009 Beacon makes `beacon-toolkit-branch-governance` write delivery service, branch, and worktree updates through canonical git workflow, technical review contract, execution host, service slice, and metadata surfaces.
- AC-010 Beacon blocks QA and release while blocking artifact update obligations remain open.
- AC-011 Beacon emits diagnostics that name the missing material, default-seeded field, unadopted support finding, open obligation, and recommended repair surface.
- AC-012 Beacon preserves the main lifecycle boundary and does not turn support or toolkit skills into truth sources, gate sources, or new lifecycle stages.

## Actor Semantics

1. Human skill caller
   - invokes a Beacon child skill
   - receives a material effect and next route
   - must not get silent success when the required material target is missing
2. Truth owner
   - owns PRD / user-story / test-case / change updates
   - decides whether accepted support findings alter canonical truth
3. Execution owner
   - consumes execution host, branch governance, delivery baseline, git workflow, and technical review contract
   - cannot implement from default branch/service/worktree assumptions
4. QA owner
   - consumes evidence, acceptance coverage, and artifact update obligations
   - blocks when obligations or evidence gaps remain open
5. Release owner
   - consumes QA proof, version-surface governance, and blocker state
   - cannot release from status-only or advisory-only signals

## Material Effect Semantics

- `writeback_completed`: skill produced the required material update.
- `writeback_required`: skill identified the material target but did not update it yet.
- `obligation_opened`: skill created a blocking follow-up obligation.
- `truth_reopen_required`: frozen truth must go through `beacon-change`.
- `execution_host_update_required`: execution host or delivery governance material must be updated.
- `evidence_update_required`: QA / release evidence must be updated.
- `read_only_route_only`: skill is advisory only and has named the next route.

## Boundary Notes

- support skill output is not canonical truth by itself
- default seed is not an approved delivery fact
- side dossier is not the canonical execution host
- status board is not a release verdict
- route recommendation is incomplete unless it names the next material target
- accepted finding must update a canonical material surface or open a blocking obligation
