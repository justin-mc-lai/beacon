# Beacon Learn Command Contract

## Scope

- command surface: `beacon-learn`
- feature: `beacon-v1.4.3-governed-learning-recall-and-route-explainability`
- status: `implementation-spec-ready`

## Intent

Turn learning from passive storage into a governed default decision input that is visible, auditable, downgradeable, and removable.

## Invocation Contract

### Supported entry shapes

```text
beacon learn recall "<surface-or-feature>"
beacon learn audit "<surface-or-feature>"
beacon learn prune "<surface-or-feature>"
```

## Required Inputs

- target surface or feature
- current route context
- current truth refs or execution refs

## Optional Inputs

- learning topic filter
- freshness window
- confidence threshold
- explicit operator override

## Output Contract

The surface must always emit:

- `learning_candidates`
- `applied_learning`
- `suppressed_learning`
- `stale_learning`
- `conflicting_learning`
- `route_influence_summary`
- `recommended_route`
- `writeback_targets`
- `blocked_reason` or `none`

## Mode Semantics

- `recall`: fetch and apply relevant prior learning as default decision input
- `audit`: explain what learning was applied, skipped, downgraded, or in conflict
- `prune`: mark learning for downgrade, archive, or removal through governance path

## Injection Rules

- relevant learning should be injected by default into:
  - `help`
  - `status`
  - `ask`
  - `deep`
  - applicable requirement and support surfaces
- learning must be progressively disclosed, not dumped by default
- no learning may silently override current frozen truth

## Route Contract

- stale but still informative -> keep as warning/hint
- conflicting with current truth -> downgrade and flag
- invalidated by newer truth -> prune or archive
- useful route pattern -> attach to route explanation output

## Writeback Contract

`beacon-learn` may write:

- learning audit result
- downgrade recommendation
- prune recommendation
- route influence summary

It may not write:

- direct requirement truth changes
- direct release verdicts
- direct QA pass/fail verdicts

## Blocked Reasons

- `learning_index_missing`
- `route_context_missing`
- `truth_binding_missing`
- `learning_conflict_requires_operator_resolution`
- `audit_surface_unavailable`

## Boundary Rules

- learning remains advisory
- learning cannot become a second truth source
- learning must be explainable when applied
- learning must be degradable when stale

## Acceptance Hooks

- AC-001 through AC-005 for `beacon-v1.4.3-governed-learning-recall-and-route-explainability`
