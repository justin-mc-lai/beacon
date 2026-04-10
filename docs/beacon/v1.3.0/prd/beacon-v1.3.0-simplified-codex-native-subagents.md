# PRD: Beacon v1.3.0 Simplified Codex Native Subagents

**Feature**: Beacon v1.3.0 - Simplified Codex Native Subagents  
**Version**: v1.3.0  
**Date**: 2026-04-10  
**Status**: planning line

## 1. Problem

Beacon already structures product work well, but several stages still flatten inherently multi-lane work into one pass:

- research + critique in `think`
- structure + AC review in `user-story`
- requirement parsing + risk review in `prd`
- scenario generation + coverage audit in `test-case`
- verification + repair handoff in `qa`
- execute + review + test in `implement run`

Today there is no shared, explicit, Codex-native subagent contract across those stages.

## 2. Goal

Introduce a simplified Codex native subagent model that:

1. stays subordinate to Beacon stage commands
2. is explicit, bounded, and optional
3. writes run-scoped evidence
4. compiles back into canonical Beacon artifacts

## 3. Functional requirements

### FR-001 Stage-level `subagent_mode`

Selected stage commands must accept a bounded `subagent_mode`.

### FR-002 Role registry

Beacon must own a small built-in role registry for stage workers.

### FR-003 Plan artifact

Before delegation, Beacon must write a subagent plan artifact containing:

- stage
- role
- feature/version/run id
- allowed scope
- expected output schema

### FR-004 Evidence artifact

After delegation, Beacon must write subagent evidence artifacts under runtime storage before formal writeback.

### FR-005 Canonical writeback

`think`, `user-story`, `prd`, `test-case`, `qa`, and `implement run` must remain responsible for the final Beacon artifact writeback.

### FR-006 Adapter boundary

`implement run` must treat Codex-native delegation as an adapter, not as the new Beacon runtime core.

### FR-007 Planning prompt routing

`beacon ask` must route "next version / subagent evolution / research direction" prompts to planning-oriented surfaces instead of QA-oriented execution surfaces.

## 4. Source insertion points

Current files suggest the smallest path is:

- `beacon/utils/intent_router.py`
- `beacon/commands/ask.py`
- `beacon/commands/think.py`
- `beacon/commands/user_story.py`
- `beacon/commands/prd.py`
- `beacon/commands/test_case.py`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`
- `beacon/utils/implement_native.py`
- `beacon/utils/project_skills.py`
- `beacon/commands/team.py`

## 5. Non-goals

- generic task DAG orchestration for arbitrary shell work
- replacing project-skill orchestration
- forcing all projects to enable native subagents
- introducing a second release truth outside Beacon artifacts

## 6. Rollout strategy

1. planning line and artifact contract
2. shared subagent plan/evidence runtime helpers
3. `implement run` Codex-native adapter
4. `think / story / prd / test-case / qa` stage adoption
5. release/gate hardening
