# Beacon v1.4.10 Source Architecture

## Scope

本版本 source architecture 描述一条 P0 子线：

- `qa-evo-deep-and-skill-eval-kit-v1410`

P1/P2 research inputs remain deferred:

- `project-lifecycle-hook-skill-toolkit-contract`
- `implement-mode-human-playbooks-and-routing-contract`
- Ralph Task Loop
- `beacon learn` context-to-project-skill injection

## Source Modules Under Review

- `skills/beacon/beacon-qa/SKILL.md`
- `skills/beacon/beacon-deep/SKILL.md`
- `skills/beacon/beacon-learn/SKILL.md`
- `skills/beacon/beacon-implement/SKILL.md`
- `beacon/commands/qa.py`
- `beacon/commands/implement.py`
- `beacon/utils/qa_matrix.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/support_research_topology.py`
- `beacon/utils/intent_router.py`
- `beacon/utils/host_prompt_trace.py`
- `beacon/utils/agent_surface.py`

## Architecture Position

Beacon v1.4.10 does not add a new lifecycle stage.

Target architecture:

```text
frozen requirement truth
-> QA evo-deep routeable findings
-> QA / implement / change / release route recommendation

human-facing skill or harness route
-> Skill Eval Kit case
-> regression core run
-> runtime evidence and scorecard
```

## Gate Boundary

- QA evo-deep output cannot claim release pass.
- QA round memory cannot satisfy acceptance without current evidence.
- Skill Eval Kit output cannot become requirement truth.
- Regression core failure blocks skill/harness readiness, not unrelated product truth.
- P1/P2 research inputs cannot silently expand v1.4.10 P0.

## Feature Architecture

- `docs/beacon/v1.4.10/source-architecture/qa-evo-deep-and-skill-eval-kit-v1410.md`
