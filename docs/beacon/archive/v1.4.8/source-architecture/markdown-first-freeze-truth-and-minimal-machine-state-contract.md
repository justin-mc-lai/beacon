# Source Architecture: Markdown-first Freeze Truth

**Feature**: `markdown-first-freeze-truth-and-minimal-machine-state-contract`
**Version**: `v1.4.8`
**Status**: `frozen`

## Current Runtime Surfaces

- `beacon/utils/material_audit.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/story_state.py`
- `beacon/utils/revision_state.py`
- `beacon/utils/requirement_deepening.py`
- `beacon/utils/material_sync.py`
- `beacon/commands/change.py`
- `beacon/commands/freeze.py`
- `beacon/commands/test_case.py`
- `beacon/commands/prd.py`
- `beacon/commands/implement.py`
- `beacon/commands/qa.py`
- `beacon/commands/release.py`

## Architecture Shift

Current implementation stores too much requirement truth in `.machine` artifacts.

The target architecture keeps:

- Markdown as canonical requirement truth.
- Deterministic Markdown parsers as gate readers.
- Minimal state JSON as cache and transaction state.
- Runtime JSON as process/evidence output only.

## Non-goals

- Do not remove runtime evidence JSON.
- Do not weaken gate fail-closed behavior.
- Do not rely on LLM interpretation for gate parsing.
- Do not allow Markdown format freedom where gate parsing requires strict structure.
