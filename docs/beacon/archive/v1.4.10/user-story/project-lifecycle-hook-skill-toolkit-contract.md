# User Story: Project Lifecycle Hook Skill Toolkit Contract

**Feature**: `project-lifecycle-hook-skill-toolkit-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Story

As a Beacon operator working in a real project, I want project-specific lifecycle boundary actions to be defined as governed Markdown hook contracts, so that UAT delivery, QA diagnostics, and post-release local installation can be planned, confirmed, evidenced, and routed without becoming hidden automation or requirement truth.

## Acceptance Criteria

| AC ID | Theme | Description |
| --- | --- | --- |
| AC-001 | project-level hook truth | Hook contracts live under `docs/beacon/hooks/<hook-id>.md`; version directories only hold research and requirement material. |
| AC-002 | single-file contract | Each hook is a single Markdown file with frontmatter and human-readable sections for purpose, admission, evidence, and failure route. |
| AC-003 | finite hook code taxonomy | Hooks are limited to `post_implement_pre_qa`, `qa_diagnostics`, `post_qa_pre_release`, and `post_release`. |
| AC-004 | admission and confirmation | Hook admission validates lifecycle binding, enabled state, skill availability, command template, trigger policy, required evidence, and failure route; side-effect hooks require manual confirmation. |
| AC-005 | evidence topology | Hook runs write `.beacon/state/hooks/<hook-id>/<run-id>.json` and `docs/beacon/.machine/hooks/<hook-id>.latest.json` as evidence/read models only. |
| AC-006 | human-facing toolkit | Operators can list, plan, dry-run, confirmed-run, disable, and inspect hook status without editing machine projections directly. |
| AC-007 | fixture hooks | The contract covers Beacon post-release local install, Rolo post-implement UAT, and Rolo QA Debug Lab as fixtures, not global defaults. |
| AC-008 | authority boundary | Hooks cannot rewrite PRD, user-story, test-case, freeze state, QA verdict, release verdict, or gate verdict. |
| AC-009 | fail-closed safety | Hidden auto-run, arbitrary shell hooks, unknown hook codes, and missing failure routes fail closed with explicit reason codes. |

## Non Goals

- This story does not execute hooks.
- This story does not install Beacon CLI or agent skills.
- This story does not deploy Rolo to UAT.
- This story does not run Rolo Debug Lab.
- This story does not create a new Beacon lifecycle stage.
- This story does not make hook evidence a release verdict.

## Boundary

Project lifecycle hooks are governed project extensions. They can prepare, diagnose, or supplement a lifecycle transition, but only existing Beacon truth, QA, release, and gate surfaces decide canonical closure.
