# User Story: Implement Mode Human Playbooks And Routing Contract

**Feature**: `implement-mode-human-playbooks-and-routing-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Story

As a Beacon operator choosing how to implement a frozen feature, I want `single`, `team`, and `ralph` to be explained as modes under one `beacon-implement` skill, so that I can pick the right execution shape without creating new lifecycle surfaces or confusing Ralph with QA/release authority.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | one public entrypoint | `beacon-implement` remains the only public implementation skill; mode-specific public skills are not introduced. |
| AC-002 | mode playbooks | Human-facing playbooks define purpose, admission, command, evidence, and boundary for `single`, `team`, and `ralph`. |
| AC-003 | mode recommendation | Help/status can recommend `single`, `team`, or `ralph` based on scope, complexity, closure needs, and risk. |
| AC-004 | Ralph boundary | Ralph is documented as a closure controller that routes next action; it does not replace QA, release, gate, or frozen truth. |
| AC-005 | explainable command | Mode recommendations include the reason and canonical `beacon implement run "<feature>" --project . --version <version> --mode <mode>` command. |
| AC-006 | route stability eval | Skill Eval Kit includes cases for normal implementation, team/subagent implementation, and Ralph closure prompts. |
| AC-007 | nonexistent skill fail-closed | Prompts implying `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph` do not create or route to those public skills. |
| AC-008 | authority boundary | Mode playbooks and recommendations cannot rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict. |

## Non Goals

- This story does not split the public implementation skill.
- This story does not implement the full Ralph Task Loop checkpoint/recovery controller.
- This story does not run implementation, QA, or release.
- This story does not change requirement truth outside the governed refreeze chain.
- This story does not add learn/project-skill injection.

## Boundary

Implementation modes are execution-shape guidance under `beacon-implement`. They can influence route selection and evidence expectations, but they cannot become independent lifecycle truth or verdict surfaces.
