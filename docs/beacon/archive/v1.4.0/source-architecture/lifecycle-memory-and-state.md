# Beacon v1.4.0 Lifecycle, Memory, And State

## Main State Surfaces

- `beacon/utils/story_state.py`
- `beacon/utils/revision_state.py`
- `beacon/utils/workflow_memory.py`
- `beacon/utils/qa_runtime.py`
- `beacon/utils/control_plane.py`
- `beacon/utils/learning_loop.py`

## Runtime Roots

- `.beacon/qa/`
- `.beacon/qa/sessions/`
- `.beacon/implement/<run_id>/`
- `.beacon/state/`
- `.beacon/debug/`

## Closure Sequence

```text
draft → frozen → implemented → verified → accepted/released
```
