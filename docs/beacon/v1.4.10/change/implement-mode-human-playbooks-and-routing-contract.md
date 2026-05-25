# Change: Implement Mode Human Playbooks And Routing Contract

**Feature**: `implement-mode-human-playbooks-and-routing-contract`  
**Version**: `v1.4.10`  
**Status**: `refreeze-input`  
**Date**: `2026-05-24`

## 1. Change Reason

Beacon already supports `beacon implement run ... --mode single|team|ralph`, but the human-facing contract still reads as one broad implementation surface. Operators repeatedly ask whether `single`, `team`, and `ralph` should become three separate human skills to make execution more stable.

The accepted research conclusion is the opposite: keep `beacon-implement` as the single public implementation entrypoint, and freeze explicit mode playbooks plus routing rules so users and skill evals can reason about each mode without creating new lifecycle surfaces.

## 2. Accepted Change

Freeze `implement-mode-human-playbooks-and-routing-contract` as the next P1 feature:

- `beacon-implement` remains the only public implementation skill.
- `single`, `team`, and `ralph` are implementation modes, not public lifecycle stages.
- Human-facing mode playbooks explain when to use each mode.
- Ralph is described as a closure controller after team/complex implementation evidence, not as a QA or release replacement.
- Help/status surfaces may recommend a mode, but must explain the reason and preserve the single public route.
- Skill Eval Kit must include route-stability cases proving prompts route to `beacon-implement` plus the right mode, not to nonexistent public skills.

## 3. Scope

### In Scope

- Human-facing playbooks for `single`, `team`, and `ralph`.
- One-public-entrypoint contract for `beacon-implement`.
- Mode admission and recommendation rules.
- Help/status mode explanation.
- Skill Eval Kit route-stability cases for implement mode prompts.
- Boundary text that prevents mode recommendations from changing frozen truth, QA verdicts, release verdicts, or gate verdicts.

### Out Of Scope

- Creating `beacon-implement-single`, `beacon-implement-team`, or `beacon-implement-ralph` public skills.
- Splitting CLI into three top-level implement commands.
- Making Ralph a formal QA or release authority.
- Implementing full Ralph Task Loop checkpoint/recovery controller.
- Adding automatic project skill injection or learn lifecycle behavior.
- Allowing support/research skills to execute implementation mode directly.

## 4. Route Decision

- This accepted research enters v1.4.10 as an independent P1 backlog feature.
- The first implementation should prioritize docs/playbooks, skill routing contract, help/status explanation, and Skill Eval Kit route stability.
- Runtime mode execution already exists and should be refined only where needed to expose stable human-facing evidence.
- Downstream implementation may start only after the refreeze transaction reports complete.

## 5. Freeze Deliverables

- `docs/beacon/v1.4.10/research/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/source-architecture/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/change/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/prd/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/user-story/implement-mode-human-playbooks-and-routing-contract.md`
- `docs/beacon/v1.4.10/qa/test-cases/implement-mode-human-playbooks-and-routing-contract.md`

## 6. Boundary

This change freezes requirement truth only. It does not execute implementation, run Ralph, run QA, pass release, or create new public lifecycle skills.
