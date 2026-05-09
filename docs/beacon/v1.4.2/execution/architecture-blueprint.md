# Beacon v1.4.2 Architecture Blueprint

## Architecture Intent

`v1.4.2` strengthens Beacon's delivery evolution model by inserting an auditable test contract governance projection between frozen requirement truth and QA/release execution.

The architecture goal is:

> Every product feature change must produce a bounded test contract delta that can be classified, verified, surfaced to skills, and consumed by release gates without converting historical test drift into undifferentiated release failure.

## Layer Placement

The existing `v1.4.0` architecture remains authoritative:

```text
Truth Layer
-> Contract Layer
-> Kernel Services Layer
-> Surface Layer
-> Plugin / Projection Layer
```

`v1.4.2` adds a test governance projection under the Contract and Kernel Services layers:

```text
Markdown requirement truth
-> compiled feature contract
-> test contract index
-> lane-aware QA execution
-> release-facing scorecard/gate consumption
-> skill delivery guidance
```

## New Contract Family

### Test Contract Index

The `Test Contract Index` is a machine-readable projection with this minimum shape:

```json
{
  "schema_version": "1.0",
  "contract_kind": "beacon_test_contract_index",
  "version": "v1.4.2",
  "feature_slug": "beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance",
  "runtime_line": "v1.4.0",
  "docs_line": "v1.4.2",
  "feature_line_status": "planning_only",
  "truth_refs": {
    "prd": "docs/beacon/v1.4.2/prd/...",
    "user_story": "docs/beacon/v1.4.2/user-story/...",
    "test_case": "docs/beacon/v1.4.2/qa/test-cases/..."
  },
  "lanes": {
    "feature_release_facing": [],
    "current_runtime_contract": [],
    "generated_surface_sync": [],
    "compatibility_contract": [],
    "legacy_snapshot": []
  },
  "ac_to_test_refs": {},
  "reason_codes": []
}
```

## Lane Semantics

### feature_release_facing

Protects the current feature's frozen AC/TC and release evidence. This lane blocks the current feature release when missing or failing.

### current_runtime_contract

Protects the current runtime release line from planning-line contamination. This lane blocks when runtime version, docs default line, public surface, or current docs claims drift.

### generated_surface_sync

Protects generated and projected surfaces such as `SKILL.md`, `metadata.json`, managed context files, command tables, and agent surface state. This lane blocks when generated surface drift can misroute humans or agents.

### compatibility_contract

Protects explicitly supported historical behavior. This lane blocks only for behavior that Beacon still promises to support.

### legacy_snapshot

Protects historical materials as audit snapshots. This lane does not block current feature release unless a snapshot is explicitly promoted into compatibility scope.

## Kernel Ownership

- `doctor` owns index build and verification.
- `test-case` owns accepted AC/TC mapping and test delta adoption.
- `qa` owns lane execution, evidence pack, `coverage_current`, `coverage_gap`, and `continue_decision`.
- `release` owns lane status consumption and reason-code projection.
- `skill` surfaces own human/agent guidance but do not define release truth.

## Non-Goals

- No new public lifecycle stage.
- No second truth root.
- No blind full-suite release gate.
- No automatic rewriting of legacy tests.
- No promotion of `v1.4.2` to runtime release line during requirement freeze.

## Release-Facing Reason Codes

The release scorecard and strict gate should be able to surface:

- `test_contract_index_missing`
- `test_contract_index_stale`
- `ac_test_mapping_missing`
- `feature_release_lane_missing`
- `feature_release_lane_failed`
- `generated_surface_sync_drift`
- `planning_line_runtime_conflict`
- `unclassified_test_failure`
- `legacy_snapshot_misclassified_as_release_blocker`

## Skill Delivery Contract

Beacon skills must guide agents to:

1. identify the feature and version;
2. read `global-boundaries` and the feature truth package;
3. inspect the test contract index;
4. run or request the correct lane;
5. stop for repair on severe blockers;
6. route through `beacon help` for resume;
7. avoid claiming release readiness from unclassified full-suite output.

<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->
## Implementation Delivery Host

- version: `v1.4.2`
- feature_count: `1`
- transaction_id: `tx-0d13167df2a36f4aa`
- source_hash: `sha256:32d25665e3f67831310e707e163e3bf6f1bcba75a3a2b6188ca0c57f3bdcfc37`

### Registered Feature Baselines
- `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance` | revision=`R1` | branch=`beacon/v1.4.2` | writable_services=. | depends_on=- | baseline_ref=`docs/beacon/v1.4.2/.machine/execution/implementation-delivery-baseline-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.json`
<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:END -->

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- version: `v1.4.2`

### Source Refs
- prd: `docs/beacon/v1.4.2/prd/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- user_story: `docs/beacon/v1.4.2/user-story/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`
- test_case: `docs/beacon/v1.4.2/qa/test-cases/beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance.md`

### Delivery Change Surface
- none
### Available Entry Surfaces
- none
### Current Service Facts
- none

### Must Change
- none

### Can Reuse
- none

### No-Expand Guardrails
- none

### Compatibility Rules
- none

### Delivery Constraints
- none

### Implement Handoff
- none
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.4.2-beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance-R1`
- transaction_id: `tx-69c08fcf464205aa8`
- source_hash: `sha256:2b0aef1aa2d1afe9cc8ab7ead11c33af3070cf636a4aedbd8ce0fce833f4aae5`
- projection_seq: `1`
- version: `v1.4.2`
- feature: `beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.4.2`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs
- depends_on_features: -

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.4.2-contract-aligned-test-evolution-and-skill-delivery-governance:END -->
