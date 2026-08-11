# Cursor agent root switch failure (2026-08-11)

## Symptom

When attempting to switch agent root into an admitted worktree, the control plane returned:

- `Failed to checkout migrated branch "main"`
- `fatal: 'main' is already used by worktree at '<repo-root>'`

## Root Cause

Git worktree semantics allow one checked-out branch per worktree attachment.
The root workspace already owns `main`, while the target lane is a feature worktree.
The move operation attempted an unnecessary `git checkout main` in the target worktree and collided with the existing main attachment.

## Impact

- Agent root migration fails even though the feature worktree exists and is healthy.
- Admission output may show `workspace_admission_worktree_failed` despite successful lane creation.

## Immediate Recovery

1. Keep using the admitted worktree path directly for commands and edits.
2. Do not re-checkout `main` inside feature worktrees.
3. Bind branch metadata to the admitted feature lane.

## Product Fix Direction

- Root mover should honor target lane branch (`beacon/v.../...`) and skip forced checkout to `main`.
- If target path is already a valid worktree, use no-op migration or branch-aware fast path.
- On timeout after `git worktree add`, re-probe `git worktree list` before returning failure.

## Verification

- `git worktree list` contains target lane.
- Target lane branch is checked out in that worktree.
- Agent operations proceed with `working_directory=<admitted_worktree>`.
