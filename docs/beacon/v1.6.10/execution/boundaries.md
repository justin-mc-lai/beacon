# Beacon v1.6.10 Execution Boundaries

## Canonical truth and implementation lanes

- Requirement truth, change, freeze, and refreeze are authored on governance `truth_canonical`.
- Implementation and QA writes require a real admitted git worktree before the first repository write.
- `cwd` must be the admitted worktree returned by Beacon. A branch name alone is not an execution lane.
- Parent truth reconcile and child service baseline reconcile are separate checks.

## Repository topologies

### single_repo

- One feature maps to one leaf branch and one real worktree.
- Admission records branch, worktree path, HEAD, canonical baseline, and reconcile result.

### monorepo / nested service repositories

- Governance declares participating services and writable bindings.
- Every writable service gets its own verified worktree entry in `service_worktree_map`.
- A parent worktree containing empty gitlinks does not satisfy child service admission.

### multi_git_workspace

- Each writable git root is verified independently.
- Reference-only services do not receive write authorization.

## Fail-closed rules

- `branch-only`, optional admission, or `skipped=true` never authorizes implementation writes.
- mkdir-only paths, empty gitlinks, missing worktree registration, stale seed facts, branch mismatch, cwd mismatch, HEAD drift, or baseline conflict block dispatch.
- Git hooks are defense-in-depth and cannot replace pre-write admission.
- Release remains human-confirmed.

