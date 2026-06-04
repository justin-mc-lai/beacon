# Beacon Research: UI/UX Externalization and Version-Level Requirement Visualization

> Date: 2026-05-21
> Scope: post-`v1.4.7` evolution direction
> Status: Research only
> Upstream route: `beacon-brainstorm` convergence output for later `beacon-change`
> Source refs:
> - `docs/brainstorms/2026-05-21-beacon-brainstorm-vnext-externalize-ui-ux-and-add-version-level-requirement-visualization.md`
> - `docs/beacon/global-boundaries.md`
> - `docs/beacon/archive/v1.4.7/SUMMARY.md`
> - `docs/beacon/archive/v1.4.7/execution/architecture-blueprint.md`
> - `skills/beacon/beacon-brainstorm/SKILL.md`
> - `skills/beacon/beacon-prototype/SKILL.md`
> - `skills/beacon/beacon-design-review/SKILL.md`
> - `/Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/ui-ux-dev/SKILL.md`
> - `docs/beacon/archive/v1.4.7/research/beacon-v1.4.7-agent-skills-lifecycle-and-meta-protocol-analysis.md`

---

## 1. Research Goal

This note answers three linked questions:

1. Should Beacon continue to maintain design/prototype execution capability internally?
2. If not, what must remain inside Beacon so UI/UX outputs can still enter governed requirement closure?
3. What new human-readable version-level requirement projections are needed so operators can understand a frozen version without reading the entire PRD / user-story / test-case package line by line?

This note is not canonical truth.
It is upstream convergence material for a later `beacon-change -> prd -> user-story -> test-case` transaction.

## 2. High-Level Judgment

The converged judgment is:

```text
UI/UX execution should move out of Beacon.
UI/UX requirement governance should stay inside Beacon.
Beacon should add version-level requirement visualization.
```

More concretely:

- Beacon should stop investing in redundant internal design execution capability.
- `ui-ux-dev` should become the stable human-facing UI/UX execution surface.
- Beacon should keep a narrow adapter layer that translates accepted design outputs into requirement-facing artifacts.
- Beacon should add business-flow / state-machine / requirement-map projections so humans can understand a version package at a glance.

## 3. Why Beacon Should Not Keep Expanding Internal Design Execution

### 3.1 Boundary conflict

Beacon's global boundaries require:

- compact main lifecycle
- support surfaces that do not become new stages
- complexity absorbed into machine surfaces, not human burden

A rich internal UI/UX execution plane pushes Beacon away from that identity.

### 3.2 Capability duplication

`ui-ux-dev` already defines a stable external UI/UX routing family:

- `explore`
- `system`
- `review`
- `polish`
- `extract`
- `library`

That surface exists specifically to avoid exposing raw upstream design skills while still preserving execution quality.

Continuing to build overlapping Beacon-native design execution creates:

- duplicated maintenance
- duplicated routing burden
- inconsistent human-facing entry points
- additional cognitive cost

### 3.3 Wrong locus of value

Beacon's real unique value is not "generate better UI".
Its unique value is:

- freeze requirement truth
- preserve anti-drift execution
- maintain evidence-backed QA/release closure
- keep auditable route and requirement lineage

Therefore, Beacon should govern how design outcomes enter truth, not compete to become the design execution engine.

## 4. Why `prototype` Should Be Retained but Redefined

`prototype` should not remain a design-generation surface.
But it also should not be deleted outright.

The irreducible value of `prototype` is that some features need a governed contract between design outcomes and requirement truth.

The recommended redefinition is:

```text
prototype = design-result adapter
```

Its future role should be:

- accept design exploration results coming from `ui-ux-dev`
- extract screen intent and UX reasoning that affect requirement closure
- formalize state visibility and interaction handoff in a freeze-facing way
- map those outputs back to PRD promises, user-story acceptance, and test-case coverage

In other words, `prototype` should become the requirement-facing bridge between:

```text
UI/UX direction
-> requirement projection
-> freeze-ready truth package
```

## 5. Version-Level Requirement Visualization Is a Missing Human Surface

Beacon already has strong machine-facing and truth-facing materials.
What is still weak is the human-readable projection for whole-version understanding.

Operators with limited working memory cannot reliably reason from:

- multiple PRD files
- multiple user-story files
- multiple test-case files
- scattered change/release notes

without a high-level projection.

The missing layer is not more truth.
It is a better human-readable version map.

## 6. Required Visualization Outputs

At minimum, Beacon should add three version-level projections.

### 6.1 Business Flow Outline

Purpose:

- explain what business/problem closure the version delivers
- show the main path, critical branches, and end states

This should answer:

- what starts the flow
- who/what participates
- what the major phases are
- where branching happens
- what completion looks like

### 6.2 Version State-Machine Overview

Purpose:

- explain how requirement/workflow states move through closure

This is not a UI widget-state diagram first.
It is a Beacon requirement/business closure state diagram first.

Candidate state families:

- drafted
- prd_frozen
- user_story_frozen
- test_case_frozen
- requirement_clarity_pass
- freeze_pass
- implement_in_progress
- qa_blocked
- qa_pass
- release_blocked
- release_ready
- refreeze_required
- archived

The exact taxonomy should be frozen later through change/PRD, but this is the minimum shape under study.

### 6.3 PRD / User-Story / Test-Case Map

Purpose:

- explain what each truth surface owns
- show how they connect for the full version

This should clarify:

- PRD = promise / goals / scope / boundaries
- User Story = actor goals / scenarios / acceptance criteria
- Test Case = scenario coverage / verification contract

And it should visually show how those surfaces compose into the version package.

## 7. Boundary of These Diagrams

These diagrams should be:

- human-readable projections
- explanation aids
- alignment aids
- freeze-facing inputs

They should not be:

- canonical truth by themselves
- machine writeback sources
- standalone gate sources

This preserves Beacon's single-truth rule.

## 8. Candidate Support Surface Direction

A new support direction is justified here because the need is not just documentation.
It is recurring, structured human understanding support for complex version closure.

The likely direction is a future support surface in one of these shapes:

- `requirement-visualization`
- `business-flow-review`
- `state-machine-review`

Its job would be to:

- help produce clean version-level business and state diagrams
- improve human understanding before truth freeze
- route findings back into `change`, `prd`, `user-story`, or `test-case`

It must remain:

- non-truth
- non-gate
- non-stage

## 9. Recommended vNext Feature Lines

### 9.1 UI/UX Externalization and Prototype Adapter

Suggested slug:

- `beacon-vnext-ui-ux-externalization-and-prototype-adapter`

Goal:

- move design execution responsibility to `ui-ux-dev`
- retain Beacon-side design-result governance

### 9.2 Version Requirement Visualization Contract

Suggested slug:

- `beacon-vnext-version-requirement-visualization-contract`

Goal:

- freeze the minimum human-readable projection package for full-version understanding

### 9.3 Business Flow and State-Machine Review Surface

Suggested slug:

- `beacon-vnext-business-flow-and-state-machine-review-surface`

Goal:

- provide a stable support route for complex requirement understanding and projection

## 10. Research Closure

The research conclusion is not "Beacon should do more design."

The research conclusion is:

```text
Beacon should own requirement-facing design governance,
not full UI/UX execution.
Beacon should add whole-version human-readable requirement projections.
```

That gives Beacon a cleaner identity:

```text
ui-ux-dev = UI/UX execution surface
Beacon prototype = design-result adapter
Beacon truth chain = prd -> user-story -> test-case
Beacon visualization = version-level human-readable projection
```

## 11. Next Route

Recommended next route:

1. `beacon-change`
2. freeze the new vNext feature line package
3. compile into:
   - PRD
   - user-story
   - test-case

Only after that should implementation begin.
