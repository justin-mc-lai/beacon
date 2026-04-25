---
name: beacon-brainstorm
description: Use when the user wants Beacon's built-in thinking sidecar to continue requirement brainstorming, converge gaps from docs/beacon/<version>, or explore project evolution without rewriting frozen truth or entering implementation.
---

# Beacon Brainstorm

Use this skill as a read-only Beacon thinking sidecar.

It is not a new main lifecycle stage. The default lifecycle remains:

```text
prd -> user-story -> test-case -> prototype -> implement -> qa -> release
```

## Use For

- Continuing requirement brainstorming from `docs/beacon/<version>/`.
- Finding missing questions before editing PRD, user-story, or test-case materials.
- Exploring project evolution ideas before promoting them into a formal Beacon change.
- Checking implementation prompts against frozen requirement evidence before `beacon-implement`.

## Thinking Protocol

Always apply:

- First principles: reduce the prompt to user outcome, evidence, and closure constraints.
- Socratic questioning: ask what must be true, what could falsify it, and which frozen evidence proves it.
- Occam's razor: remove redundant mechanisms, duplicate docs, and broad speculation.

## Operator Rule

Prefer the labs/hidden command:

```bash
bash skills/beacon/scripts/run_beacon.sh brainstorm run "<prompt>" \
  --project-root . \
  --version v1.3.8 \
  --mode requirement-convergence \
  --json
```

Supported modes:

- `requirement-convergence`
- `project-evolution`
- `implementation-readiness`
- `scope-simplification`

## Boundary

- Do not rewrite `docs/beacon/<version>/prd/`, `user-story/`, `qa/test-cases/`, `prototype/`, or `.machine/`.
- Do not execute implementation.
- If brainstorm changes frozen scope, route to `beacon-change`.
- If brainstorm only confirms frozen scope, route back to `beacon-implement`.
