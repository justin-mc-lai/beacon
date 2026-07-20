# Change: loom-git-worktree-implement-harness R2 — branch ref hierarchy

- version: v2.0.0 (runtime shared with v1.6.8 path)
- date: 2026-07-20
- user: GO 1A leaf-only / 2A hard-stop admit fail / 3A gen-change+implement
- advisory: docs/beacon/v2.0.0/research/branch-ref-hierarchy-collision-admit-main-fallback-pln-review.md

## Intent

消除 `beacon/<version>` parent 与 `beacon/<version>/<feature>` children 的 Git 互斥冲突；
admit materialize 永远 leaf；admit 失败禁止 main 写实现。

## Downstream

refreeze → implement TASK-BR-* → pytest test_v200_branch_ref_hierarchy
