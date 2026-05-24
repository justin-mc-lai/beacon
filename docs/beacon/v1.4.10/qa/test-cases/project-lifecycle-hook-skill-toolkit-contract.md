# Test Cases: Project Lifecycle Hook Skill Toolkit Contract

**Feature**: `project-lifecycle-hook-skill-toolkit-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
| --- | --- | --- | --- | --- | --- |
| AC-001 | TC-HOOK-001 | topology | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "project_level_hook_truth"` | Hook contracts are discovered from `docs/beacon/hooks/<hook-id>.md` and not from `docs/beacon/<version>/hooks/`. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-001.json` |
| AC-002 | TC-HOOK-002 | contract | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "single_file_hook_contract"` | Hook Markdown frontmatter and body sections include required contract, admission, evidence, and failure-route fields. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-002.json` |
| AC-003 | TC-HOOK-003 | gate | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "finite_hook_code_taxonomy"` | Unknown hook codes fail closed; allowed hook codes pass. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-003.json` |
| AC-004 | TC-HOOK-004 | gate | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "hook_admission_requires_manual_confirmation"` | Side-effect hooks require `manual_confirmed` and cannot execute through hidden auto-run. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-004.json` |
| AC-005 | TC-HOOK-005 | topology | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "hook_evidence_topology"` | Hook evidence writes to `.beacon/state/hooks/...` and latest read model writes to `docs/beacon/.machine/hooks/...`. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-005.json` |
| AC-006 | TC-HOOK-006 | contract | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "human_toolkit_commands"` | Hook toolkit supports list, plan, dry-run, confirmed-run, disable, and status/explain behavior. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-006.json` |
| AC-007 | TC-HOOK-007 | fixture | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "fixture_hooks_are_not_global_defaults"` | Beacon install, Rolo UAT, and Rolo Debug Lab fixtures validate as examples but are not global defaults. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-007.json` |
| AC-008 | TC-HOOK-008 | boundary | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "hook_authority_boundary"` | Hook output cannot claim PRD, user-story, test-case, QA, release, gate, or freeze authority. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-008.json` |
| AC-009 | TC-HOOK-009 | fail-closed | `python3 -m pytest -q tests/test_v1410_project_lifecycle_hooks.py -k "unsafe_hook_requests_fail_closed"` | Hidden auto-run, arbitrary shell hooks, unknown hook codes, and missing failure routes fail closed with reason codes. | `.beacon/evidence/test-results/project-lifecycle-hook-skill-toolkit-contract/TC-HOOK-009.json` |

## Explicit Non Coverage

- These tests do not execute UAT deployment, global CLI installation, Debug Lab, implementation, QA, or release.
- These tests do not create canonical hook truth under `docs/beacon/<version>/hooks/`.
- These tests do not allow hook output to become requirement truth or formal lifecycle verdicts.
