# Beacon Design Review Command Contract

## Scope

- command surface: `beacon-design-review`
- feature: `beacon-v1.4.3-design-review-surface-and-prototype-governance`
- status: `implementation-spec-ready`

## Intent

Provide a dedicated UI/UX challenge surface so design judgment is separated from prototype freeze and prototype no longer acts as final design authority.

## Invocation Contract

### Supported entry shapes

```text
beacon design-review "<feature>"
beacon design-review "<feature>" --focus hierarchy
beacon design-review "<feature>" --focus states
beacon design-review "<feature>" --focus interaction
beacon design-review "<feature>" --focus evidence
```

## Required Inputs

- target feature slug
- bound truth refs:
  - PRD
  - user-story
  - test-case
- available UI evidence:
  - prototype docs
  - flow notes
  - route/state/interaction description

## Optional Inputs

- screenshots or mock refs
- prototype freeze refs
- prior learning refs
- prior friction notes

## Output Contract

The surface must always emit:

- `design_verdict`
  - `ready_for_prototype`
  - `needs_design_revision`
  - `prototype_not_required`
- `hierarchy_findings`
- `state_clarity_findings`
- `interaction_findings`
- `evidence_gap_summary`
- `route_decision`
- `writeback_targets`
- `blocked_reason` or `none`

## Prototype Layering Rules

- `design-review` happens before `prototype` when UX/UI handoff is needed
- `prototype` can be skipped when the feature has no real UI/UX surface
- `prototype` freeze cannot substitute for missing design judgment
- approved `design-review` does not itself freeze prototype truth

## Route Contract

- design-direction issue -> `beacon-change` or `beacon-prd`
- acceptance mismatch with UX state -> `beacon-user-story`
- scenario coverage gap -> `beacon-test-case`
- handoff-ready and UI surface exists -> `beacon-prototype`
- no UI surface exists -> bypass `prototype` and return to implementation path

## Writeback Contract

`beacon-design-review` may write:

- design challenge summary
- affected states/routes/components list
- next recommended route
- prototype trigger recommendation

It may not write:

- final product strategy truth
- final UI delivery truth
- frozen prototype package by itself

## Blocked Reasons

- `ux_evidence_missing`
- `state_model_missing`
- `prototype_semantics_overloaded`
- `interaction_contract_ambiguous`
- `truth_refs_incomplete`

## Boundary Rules

- cannot replace `prototype`
- cannot replace `prd`
- cannot act as visual approval authority for shipped UI
- cannot silently convert prototype notes into canonical design truth

## Acceptance Hooks

- AC-001 through AC-005 for `beacon-v1.4.3-design-review-surface-and-prototype-governance`
