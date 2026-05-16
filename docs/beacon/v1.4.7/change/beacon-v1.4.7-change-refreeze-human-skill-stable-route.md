# Change: beacon-v1.4.7-change-refreeze-human-skill-stable-route

**Feature**: `beacon-v1.4.7-change-refreeze-human-skill-stable-route`
**Version**: `v1.4.7`
**Date**: `2026-05-16`
**Status**: `implemented-and-verified`
**Track**: `change-refreeze + human-skill-routing`

## Trigger

Brainstorm concluded that `beacon change ... --refreeze-chain` is a valid machine route but too hidden as a human-facing route for change 一键冻结 / refreeze intent.

## Accepted Direction

Add a new narrow human-facing support skill:

```text
beacon-change-refreeze
```

The skill must route to:

```text
beacon change ... --refreeze-chain
```

It must not introduce a new lifecycle stage, truth source, gate source, or second refreeze implementation.

## Scope

- add packaged skill file under `skills/beacon/beacon-change-refreeze/SKILL.md`
- add local agent skill file under `.agents/skills/beacon-change-refreeze/SKILL.md`
- make the skill discoverable for stable human refreeze language
- make deep/change documentation able to route to `beacon-change-refreeze`
- preserve existing refreeze transaction implementation

## Non-Scope

- no new primary command
- no change to canonical truth ownership
- no automatic PRD/user-story/test-case writing from the skill
- no implementation, QA, or release execution
- no replacement for `beacon-change`

## Required Boundary

`beacon-change-refreeze` is a route wrapper and boundary explainer. The only machine execution path remains `beacon change ... --refreeze-chain`.

## Traceability

- PRD: `docs/beacon/v1.4.7/prd/beacon-v1.4.7-change-refreeze-human-skill-stable-route.md`
- User Story: `docs/beacon/v1.4.7/user-story/beacon-v1.4.7-change-refreeze-human-skill-stable-route.md`
- Test Cases: `docs/beacon/v1.4.7/qa/test-cases/beacon-v1.4.7-change-refreeze-human-skill-stable-route.md`
- Upstream refreeze contract: `docs/beacon/v1.4.7/prd/beacon-v1.4.7-change-refreeze-one-shot-requirement-closure.md`
- Brainstorm artifact: `docs/brainstorms/2026-05-16-beacon-brainstorm-v1.4.7-change-一键冻结是否应该暴露为新的稳定可命中的人类面子-skill-而不是只作为-beacon-change-内的-refreeze-cha.md`
