# Beacon v1.3.10 Architecture Blueprint

## 主题

把真实项目中的 monorepo / repo-binding / branch-governance 风险收口成可事务化的项目版本元信息治理能力。

## 核心结构

1. canonical metadata envelope
2. human sink projection
3. machine sink projection
4. sqlite runtime projection
5. resolved metadata view for prompt/runtime/support surfaces

## 执行边界

- 核心 metadata 只表达 topology、service binding、participating services、per-service allowed working branch
- 项目级协作流通过项目内 skill / policy 扩展
- requirement package dual-write gate 属于全局执行门禁，而不是单一 feature 内部约定

## 关键门禁

- `doctor metadata verify`
- `doctor verify-materials --strict`
- `help/status` requirement package remediation routing
- `real-project-validation` remediation proof capture

<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:START -->
## Technical Delta Blueprint

- project_mode: `greenfield`
- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- version: `v1.3.10`

### Source Refs
- prd: `docs/beacon/v1.3.10/prd/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- user_story: `docs/beacon/v1.3.10/user-story/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`
- test_case: `docs/beacon/v1.3.10/qa/test-cases/beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance.md`

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
<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:END -->

<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:START -->
## Implementation Delivery Baseline

- baseline_id: `impl-delivery-baseline-v1.3.10-beacon-v1.3.10-project-topology-and-version-branch-metadata-transaction-governance-R2`
- transaction_id: `tx-7e4a107f30884e4a3`
- source_hash: `sha256:683819b4930b4ae2316210f02a051a5654e2d85ac9b264f21e864d2aec0e043d`
- projection_seq: `1`
- version: `v1.3.10`
- feature: `Beacon v1.3.10 project topology and version-branch metadata transaction governance`
- lifecycle_role: `pre-implement delivery blueprint projection`
- projection_refresh_trigger: `implement plan against the active frozen revision`
- branch_strategy: `single-branch`
- base_branch: `main`
- default_target_branch: `beacon/v1.3.10`
- branch_prefix: `beacon/`
- use_git_worktree: `False`
- worktree_root: `/Users/apple/Developer/Personal/products/beacon`
- workspace_root: `/Users/apple/Developer/Personal/products/beacon`

### Delivery Service Scope
- direct_delivery_services: .
- writable_services: .
- reference_only_services: docs

### Plan-Time Gate Contract
- canonical envelope is the only delivery baseline source.
- deterministic implementation contract, git workflow contract, and implementation plan are projections.
- gates must block if projection metadata or service/branch/worktree fields drift.
<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:END -->
