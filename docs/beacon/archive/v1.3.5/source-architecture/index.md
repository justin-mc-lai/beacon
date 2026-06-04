# Beacon v1.3.5 Source Architecture Index

This index captures source surfaces related to the `v1.3.5` prototype wireframe freeze line.

## Command surfaces

- `beacon/commands/prototype.py` — prototype lifecycle entrypoint (`plan/create/review/freeze/status`)
- `beacon/commands/doctor.py` — material and context verification guardrail
- `beacon/commands/status.py` — lifecycle visibility and drift-facing summaries
- `beacon/commands/release.py` — release-line gating and checklist integration

## Prototype and closure utilities

- `beacon/utils/prototype_utils.py` — wireframe artifact generation and validation helpers
- `beacon/utils/prototype_support.py` — prototype package support and common contracts
- `beacon/utils/material_audit.py` — strict requirement-material completeness checks
- `beacon/utils/material_sync.py` — version material synchronization mechanics

## Context and consistency modules

- `beacon/utils/context_files.py` — managed context block read/write for runtime/docs version anchors
- `beacon/utils/doctor_orchestrator.py` — extensible doctor orchestration flow
- `beacon/utils/doctor_registry.py` — doctor responsibility registration
- `beacon/utils/doctor_diagnostics.py` — diagnosis payload/report surfaces

## Runtime projection surfaces (boundary-aware)

- `beacon/utils/runtime_projection.py` — normalized runtime projection envelope
- `beacon/utils/runtime_projection_store.py` — sqlite runtime projection persistence
- `beacon/utils/runtime_projection_board.py` — board-facing projection aggregation

## Skill routing surfaces

- `skills/beacon/beacon-prototype/SKILL.md` — host-visible prototype stage contract
- `skills/beacon/beacon-doctor/SKILL.md` — diagnosis/recovery surface
- `skills/beacon/beacon-release/SKILL.md` — release readiness surface
- `skills/beacon/beacon-status/SKILL.md` — stage snapshot surface

## Boundary note

`v1.3.5` formalizes prototype-stage requirement closure and anti-drift contracts.  
It does not declare final visual console delivery complete.
