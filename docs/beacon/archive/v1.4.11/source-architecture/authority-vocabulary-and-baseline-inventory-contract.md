# Source Architecture: Authority Vocabulary and Baseline Inventory Contract

**Feature**: `authority-vocabulary-and-baseline-inventory-contract`  
**Version**: `v1.4.11`  
**Status**: `refreeze-input`

## Architecture

This feature touches documentation contracts and low-risk vocabulary/inventory surfaces only.

Primary code areas for later implementation:

| Area | Role | Current Risk |
| --- | --- | --- |
| `beacon/artifact-language-policy.json` | artifact language and sync wording policy | machine artifact wording conflicts with Markdown-first authority |
| `beacon/utils/artifact_language.py` | default policy and human rendering | default fallback repeats machine-as-truth wording |
| `beacon/command_catalog.py` | command layer catalog | central source for compat/deprecated command inventory |
| `beacon/cli_factory.py` | Typer command registration | hidden aliases and compatibility commands must be inventoried |
| `beacon/commands/implement/__init__.py` | implement package bridge | dynamic legacy loader must be inventoried, not removed in this slice |
| `beacon/utils/qa_runtime.py` | QA status persistence | canonical status and legacy mirror behavior must be inventoried |
| `beacon/utils/material_audit.py` | material drift and mirror audit | PRD legacy mirror behavior must be inventoried |
| `beacon/utils/prototype_utils.py` | prototype status and legacy source | high-risk surface, inventory only |
| `beacon/adapters/browser_runner_common.py` | browser runner evidence | fallback naming must be inventoried |
| `beacon/utils/memory.py` | memory v1 migration | legacy memory migration must be inventoried |
| `beacon/utils/intent_router.py` | intent routing compatibility | legacy router facade must be inventoried |

## Business Flow

```text
scan known surfaces
  -> classify artifact role and compatibility role
  -> write markdown inventory
  -> write machine-readable inventory JSON
  -> verify no behavior-changing runtime code was retired
```

## State Machine

```text
not_inventoried
  -> inventory_generated
  -> inventory_validated
  -> ready_for_compat_registry
```

Blocked states:

- `runtime_behavior_changed`: this feature must fail QA if it changes behavior beyond wording and inventory generation.
- `unknown_surface_unclassified`: this feature must fail QA if known hotspots are missing from inventory.

## Decision Priority

1. Inventory before retirement.
2. Wording fix before registry.
3. Registry before behavior change.
4. Behavior change only in later frozen features.
