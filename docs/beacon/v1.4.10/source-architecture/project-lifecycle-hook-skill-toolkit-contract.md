# Source Architecture: Project Lifecycle Hook Skill Toolkit Contract

**Feature**: `project-lifecycle-hook-skill-toolkit-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## 1. Architecture Position

Project lifecycle hooks are project-level extensions opened at finite Beacon lifecycle boundaries. They are not lifecycle stages and they do not own requirement truth.

```text
Beacon lifecycle boundary
  -> hook discovery from docs/beacon/hooks/<hook-id>.md
  -> hook admission
  -> plan / dry-run / manual confirmed run
  -> hook evidence
  -> next route back to implement / qa / release
```

## 2. Source Modules Under Review

- `beacon/commands/skill.py`
- `beacon/utils/project_skills.py`
- `beacon/utils/skill_discovery.py`
- `beacon/utils/skill_admission.py`
- `beacon/utils/agent_surface.py`
- `beacon/utils/help_support.py`
- `beacon/utils/runtime.py`
- `skills/beacon/beacon-release/SKILL.md`
- `skills/beacon/beacon-implement/SKILL.md`
- `skills/beacon/beacon-qa/SKILL.md`

Future implementation may add:

- `beacon/commands/hooks.py`
- `beacon/utils/project_hooks.py`
- `skills/beacon/beacon-project-hooks/SKILL.md`
- `tests/test_v1410_project_lifecycle_hooks.py`

## 3. Hook Contract Root

Canonical hook files live at:

```text
docs/beacon/hooks/<hook-id>.md
```

Versioned docs may reference these hooks, but must not duplicate canonical hook definitions under:

```text
docs/beacon/<version>/hooks/
```

## 4. Hook Codes

Allowed hook codes:

| Hook code | Boundary | Purpose |
| --- | --- | --- |
| `post_implement_pre_qa` | implementation evidence bound, before QA | UAT delivery, environment refresh, API doc sync, smoke setup |
| `qa_diagnostics` | before QA or after QA blocked | Debug Lab, trace triage, environment diagnostics |
| `post_qa_pre_release` | QA pass/supplement ready, before release | external platform status, release supplement confirmation |
| `post_release` | release complete | local install, global skill sync, archive, notification |

## 5. Evidence Paths

Runtime evidence:

```text
.beacon/state/hooks/<hook-id>/<run-id>.json
```

Latest read model:

```text
docs/beacon/.machine/hooks/<hook-id>.latest.json
```

These files are evidence and read models only. They are not PRD, user-story, test-case, QA, release, gate, or freeze truth.

## 6. Admission

Admission must check:

- hook file exists and parses.
- hook id matches file name.
- hook code is allowed.
- hook is enabled.
- project / repo / feature selector applies.
- referenced skill or command template is available.
- trigger policy is safe for the hook side effects.
- required evidence outputs are declared.
- failure route is one of `implement`, `qa`, `release`, `change`, or `blocked`.

## 7. Trigger Policy

Allowed trigger policies:

- `dry_run_only`
- `manual_confirmed`
- `auto_allowed`

The P1 frozen scope permits `auto_allowed` only as a parsed value for future compatibility; side-effect hooks must require `manual_confirmed`, and hidden automatic execution must fail closed.

## 8. Decision Priority

1. Requirement truth remains in PRD, user-story, test-case, requirement clarity, and freeze.
2. Hook evidence never produces QA or release pass verdicts.
3. Side-effect hook execution requires explicit confirmation.
4. Project-specific fixture hooks are examples and tests, not Beacon global defaults.
5. Hook failures must route back to existing Beacon surfaces with reason codes.

## 9. Fixture Contracts

Fixture hooks used for tests and examples:

- `beacon-post-release-local-install`
- `rolo-post-implement-uat`
- `rolo-qa-debuglab`

These fixtures validate the contract shape and boundary behavior. They must not cause real installs, UAT deployments, or diagnostics during contract tests.
