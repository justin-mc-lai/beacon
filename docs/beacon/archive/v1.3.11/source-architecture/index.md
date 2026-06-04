# Beacon v1.3.11 Source Architecture Index

## Source Areas

- `beacon/commands/prd.py`
- `beacon/commands/doctor.py`
- `beacon/utils/material_sync.py`
- `beacon/utils/material_audit.py`
- `beacon/utils/story_state.py`
- `beacon/utils/revision_state.py`
- `beacon/commands/status.py`
- `beacon/utils/help_support.py`

## Version Focus

`v1.3.11` 的源码收口重点有两类：

1. orchestration runtime requirement line
2. PRD freeze anti-drift / machine-mirror reconciliation line

## Expected Evidence

- PRD reconcile regression tests
- full mirror audit regression tests
- transaction latest/supersedes resolution tests
- stale mirror fail-closed tests
- doctor fallback routing / recovery tests
