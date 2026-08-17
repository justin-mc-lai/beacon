---
slug: beacon-scheduled-task-agent-suspend-v169
version: v1.6.9
kind: evidence
status: implemented
---

# Evidence

- Unit: `pytest tests/test_v169_scheduled_task.py` → 7 passed
- Runtime: `beacon/utils/scheduled_task.py`, `beacon/commands/task.py`
- CLI: `beacon task create|list|get|wake|suspend|resume|log|events|install-timer|uninstall-timer|doctor`
- Execution logs: `.beacon/tasks/<id>/executions/ex-*.json` + `ex-*.log` + `events.jsonl`
- Dual package: v2.0.0 `loom-scheduled-task-agent-suspend-v200`
- UD-ST-010 execution log enforced on every wake
