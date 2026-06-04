# Beacon v1.4.11 Source Architecture

## Scope

This version line starts the Markdown-first authority cleanup and legacy-burden reduction work.

The current implemented slice is:

```text
authority-vocabulary-and-baseline-inventory-contract
```

## Source Modules Under Review

- `beacon/utils/authority.py`
- `beacon/utils/baseline_inventory.py`
- `beacon/artifact-language-policy.json`
- `beacon/utils/artifact_language.py`
- `beacon/command_catalog.py`
- `beacon/cli_factory.py`
- `beacon/commands/implement/__init__.py`
- `beacon/utils/qa_runtime.py`
- `beacon/utils/material_audit.py`
- `beacon/utils/prototype_utils.py`
- `beacon/adapters/browser_runner_common.py`
- `beacon/utils/memory.py`
- `beacon/utils/intent_router.py`

## Architecture Position

The intended authority model is:

```text
human-reviewed Markdown requirement package
-> deterministic machine projection / read model
-> runtime evidence and QA/release status
```

Markdown requirement material remains requirement truth. Machine artifacts can support automation and auditability, but they do not override human-reviewed requirement truth.

## Current Slice

The current slice adds:

- authority role classification helpers;
- updated artifact language wording;
- baseline inventory generation for known compatibility and legacy surfaces;
- regression tests that prevent this slice from silently retiring existing compatibility behavior.

## Deferred Architecture Work

The following remain later slices:

- compatibility registry;
- command catalog cleanup;
- QA / PRD legacy mirror policy;
- implement package legacy loader migration;
- prototype / browser / memory / intent compatibility boundary split;
- test marker and directory re-layering.

