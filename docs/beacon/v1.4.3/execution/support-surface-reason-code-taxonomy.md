# Beacon Support Surface Reason Code Taxonomy

## Scope

- version: `v1.4.3`
- status: `implementation-spec-ready`

## Shared Reason Code Families

### Truth Binding

- `truth_refs_missing`
- `truth_binding_missing`
- `truth_refs_incomplete`

### Scope / Target

- `review_scope_ambiguous`
- `version_level_target_missing`
- `route_context_missing`

### Evidence Gaps

- `insufficient_promise_evidence`
- `ux_evidence_missing`
- `state_model_missing`
- `interaction_contract_ambiguous`

### Learning Governance

- `learning_index_missing`
- `conflicting_learning_requires_operator_resolution`
- `learning_conflict_requires_operator_resolution`
- `audit_surface_unavailable`

### Surface Boundary Violations

- `prototype_semantics_overloaded`
- `support_surface_truth_write_forbidden`
- `next_route_missing`

## Normalization Rules

- each transaction may contain multiple reason codes
- one code may be primary and the rest secondary
- primary reason code must drive blocked rendering
- reason codes must be machine-stable and ASCII-only

## Rendering Rules

Human-facing output should show:

- one primary blocked reason
- one short explanation
- one recommended next route

Machine-facing output should preserve:

- full reason code array
- primary reason code
- route metadata

## Governance Rule

No support surface may invent ad hoc freeform blocked messages without also emitting at least one normalized reason code.
