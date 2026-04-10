# Beacon v1.3.0 Architecture Blueprint

`v1.3.0` should add simplified Codex native subagents as a bounded stage capability.

## Core thesis

Beacon should not become a general multi-agent shell.

Beacon should become a better stage orchestrator with explicit, auditable worker lanes.

## Existing insertion points

### Planning ingress

- `beacon/commands/ask.py`
- `beacon/utils/intent_router.py`

This is where subagent-related planning prompts should be recognized and routed into `think`.

### Stage commands

- `beacon/commands/think.py`
- `beacon/commands/user_story.py`
- `beacon/commands/prd.py`
- `beacon/commands/test_case.py`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`

These should remain the only public stage owners.

### Existing coordination surfaces

- `beacon/utils/implement_native.py`
- `beacon/commands/team.py`
- `beacon/utils/project_skills.py`

These provide the closest existing seams for a bounded subagent adapter and evidence model.

## Proposed runtime shape

```text
stage command
-> decide single-surface vs subagent_mode
-> write subagent plan
-> run bounded role workers
-> persist worker evidence
-> compile worker output into canonical Beacon artifact
-> gate / release unchanged
```

## Minimal new building blocks

1. `beacon/utils/subagent_runtime.py`
   - role registry
   - plan writer
   - evidence writer
   - adapter response normalization
2. `.beacon/subagents/<feature>/<run>/`
   - runtime evidence
3. `docs/beacon/<version>/.machine/execution/`
   - optional summarized subagent contract metadata

## Guardrails

1. No implicit writeback from workers
2. No bypass of stage contracts
3. No generic arbitrary-shell DAG feature
4. No second memory plane outside Beacon runtime/artifacts
