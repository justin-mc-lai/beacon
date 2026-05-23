# Source Architecture: Read-Only Support Research Write Topology Gate Contract

**Feature**: `read-only-support-research-write-topology-gate-contract`  
**Version**: `v1.4.9`

## 1. Runtime Surfaces

```text
beacon brainstorm run
  -> ordinary support research section upsert
  -> no docs/brainstorms fallback when version+feature are explicit

beacon review ceo / design
  -> support transaction receipt
  -> ordinary support research summary/index upsert

beacon deep run
  -> docs/beacon/<version>/deep/<feature>/
  -> docs/beacon/<version>/.machine/deep/<feature>/
  -> research Deep Summary index only

beacon recall governed
  -> learning audit or support transaction
  -> research Learning Influence Summary index only

material gate / requirement clarity
  -> fail closed on invalid support write topology

support topology pre-write gate
  -> resolve version + feature + support_surface_class
  -> select ordinary research / deep artifact / learning audit target
  -> block persistence when unresolved
  -> no legacy fallback persistence
```

## 2. Source Files To Inspect During Implementation

- `beacon/utils/brainstorm.py`
- `beacon/utils/support_surface_transactions.py`
- `beacon/utils/ceo_review_surface.py`
- `beacon/utils/design_review_surface.py`
- `beacon/utils/deep_loop.py`
- `beacon/utils/learn_surface.py`
- `beacon/utils/material_gate_contract.py`
- `beacon/utils/requirement_clarity.py`
- `beacon/utils/material_audit.py`
- `beacon/commands/gate.py`

## 3. Required Data Contracts

### 3.1 Support Research Section Record

Each ordinary support section must carry:

- `source_skill`
- `round_id`
- `feature`
- `version`
- `source_refs`
- `finding_summary`
- `route_decision`
- `material_effect`
- `adoption_status`
- `supersedes` when replacing a prior clarification

### 3.2 Deep Research Index

The research document stores only:

- `deep_artifact_root`
- `machine_artifact_root`
- `deep_requirement_state`
- `status`
- `route_decision`
- `release_supplement_ref`
- `adoption_status`

Detailed deep reports remain in the deep artifact family.

### 3.3 Learning Influence Index

The research document stores only:

- `learning_audit_ref`
- `applied_count`
- `stale_count`
- `conflicting_count`
- `suppressed_count`
- `policy`: learning is advisory; frozen truth wins

Raw learning candidates remain in learning audit or support transaction artifacts.

### 3.4 Support Topology Gate Diagnostic

Gate diagnostics must include:

- `reason_code`
- `policy_class`
- `source_skill`
- `expected_path`
- `actual_path`
- `feature`
- `version`
- `repair_route`

### 3.5 Pre-Write Target Decision

Every read-only support writeback must be preceded by a deterministic target decision:

```text
(version, feature, support_surface_class) -> governed write target
```

If any input is missing, ambiguous, or conflicts with the requested output path, Beacon must block persistence and return a repair route. It must not silently choose `docs/brainstorms/`, create a sibling research document, or relocate output after writing.

## 4. Boundary

This architecture freezes support write topology only. It does not authorize support skills to update PRD, user-story, test-case, freeze state, QA verdicts, or release verdicts.
