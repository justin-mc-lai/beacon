# Deterministic Implementation Contract Blueprint (v1.3.1)

## Purpose

`v1.3.1` requires each version line to complete a technical review before implementation.

That review must not stop at architecture commentary.

It must output a **deterministic implementation contract** that Beacon can later consume as implementation truth.

## Why this exists

Common failure mode:

1. requirements freeze
2. implementation starts
3. branch / worktree / service scope gets decided ad hoc
4. machine teams fill in uncertainty on the fly
5. delivery drifts across repos, services, or environments

`v1.3.1` rejects this pattern.

The implementation plane must be explicit before coding starts.

## Required fields

At minimum, each version-level technical review should resolve:

### 1. Version and feature identity

- `version`
- `feature`
- `docs_version`
- `revision_id`

### 2. Git contract

- `base_branch`
- `target_branch`
- `branch_prefix`
- `branch_strategy`
- `require_clean_worktree_for_switch`

### 3. Worktree contract

- `use_git_worktree`
- `worktree_root`
- `service_worktrees[]`
- `workspace_root`

### 4. Environment isolation contract

- `environment_mode`
- `isolation_strategy`
- `shared_resources_allowed`
- `protected_resources`

### 5. Service scope contract

- `service_directories[]`
- `writable_services[]`
- `reference_only_services[]`
- `excluded_services[]`

### 6. Multi-service dependency contract

- `gateway_services[]`
- `bff_services[]`
- `downstream_services[]`
- `shared_schema_or_contracts[]`
- `cross_service_change_order[]`

## Required decisions

The technical review must answer these questions before formal implementation:

1. Which branch should this version actually ship from?
2. Should worktrees be mandatory, optional, or forbidden?
3. Which directory or repo is the true write scope?
4. Which services are affected directly?
5. Which services are only references?
6. Which environment or data resources must stay isolated?
7. What is the allowed change order across services?

If any of these remain open, implementation is not deterministic yet.

## Freeze relationship

This contract sits **after** requirement clarification and **before** formal implementation.

```text
brainstorm / requirement review
→ PRD + user-story clarified
→ freeze
→ technical review
→ deterministic implementation contract
→ implement
```

If requirement ambiguity still exists:

- do not freeze

If technical review ambiguity still exists:

- do not implement

## Monorepo / multi-service rule

For monorepo or multi-service workspaces, a technical review must not stop at abstract module language.

It must identify concrete writable units.

### Example questions

- Which gateway service changes?
- Which BFF service changes?
- Which downstream services must be touched?
- Which services remain read-only references?
- Which service owns the formal API contract?
- Which service owns the persistence contract?

## Rolo-style example

For a `rolo`-style workspace, the contract should resolve something like:

```text
version: vX.Y.Z
feature: callback-rewrite-auth-closure

workspace_root: /path/to/rolo
base_branch: main
target_branch: feature/vX.Y.Z-callback-rewrite-auth-closure
use_git_worktree: true
worktree_root: /path/to/.worktrees/feature-vX.Y.Z-callback

gateway_services:
  - rolo-gateway

bff_services:
  - rolo-bff-order

downstream_services:
  - rolo-order-service
  - rolo-member-service

writable_services:
  - rolo-gateway
  - rolo-bff-order
  - rolo-order-service

reference_only_services:
  - rolo-member-service
  - rolo-common-contracts

environment_isolation:
  - isolated callback mock endpoint
  - isolated test database / redis namespace
```

This is the level of specificity `v1.3.1` wants.

## Human vs machine interpretation

For humans:

- this contract answers "what exactly are we changing?"

For Beacon runtime:

- this contract defines what implementation lanes are allowed to touch

Machine team freedom is still allowed, but only inside this deterministic boundary.

## Suggested machine-readable companion

Future runtime lines should consider materializing a machine-readable contract like:

```text
docs/beacon/<version>/.machine/execution/deterministic-implementation-contract-<feature>.json
```

with a human mirror like:

```text
docs/beacon/<version>/execution/deterministic-implementation-contract-<feature>.md
```

## Review gate recommendation

Implementation should be blocked when any of the following is unresolved:

- branch undecided
- worktree policy undecided
- writable service scope undecided
- environment isolation undecided
- monorepo service boundaries undecided

## Expected relationship to Beacon commands

Human-visible surface may stay simple:

- `prd`
- `user-story`
- `test-case`
- `implement`
- `qa`
- `release`

But Beacon internally should treat this contract as a prerequisite to `implement`.

