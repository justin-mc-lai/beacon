# Beacon v1.3.8 Architecture Blueprint

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.3.8-beacon-v1.3.8-archive-governance-and-historical-requirement-isolation-R2`
- transaction_id: `tx-82d57a6881e17c9ee`
- source_hash: `sha256:c67925f85ec3fff974729b80e6fa96854627a5e47542a62a887690cf4b1a89b3`
- projection_seq: `1`
- version: `v1.3.8`
- feature: `Beacon v1.3.8 archive governance and historical requirement isolation`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.3.8`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `.`
- workspace_root: `.`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->
