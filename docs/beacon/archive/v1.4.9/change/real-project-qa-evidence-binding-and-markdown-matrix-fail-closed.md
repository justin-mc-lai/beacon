# Change: Real Project QA Evidence Binding and Markdown Matrix Fail-Closed

**Feature**: `real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`  
**Version**: `v1.4.9`  
**Status**: `refreeze-input`  
**Date**: `2026-05-23`

## 1. Change Reason

真实 BMTOP 项目 `rules-encyclopedia-admin-closure` 暴露出 Beacon `implement -> qa` 机器闭环缺陷：

- 已有实现摘要与代码证据，但 `beacon implement status <feature>` 返回 `implementation_run_not_found`。
- Markdown QA 已有人类验收矩阵，但 `.machine/qa/*.ac-test-matrix.json` 退回占位验收行。
- QA fallback command 与 Go + UniApp 项目现实脱节。
- Docker / testcontainers 等环境 blocker 与产品失败没有分层。

这不是新增分析体验需求，而是 P0 可信度修复。Beacon 如果继续新增 `qa-evo-deep` 或 Better Harness，但不先修复这些 P0 证据绑定缺陷，会给真实项目继续制造假稳定信号。

## 2. Accepted Change

本 change 将 v1.4.9 的后续优先级调整为：

1. 先冻结并实现 P0：`real-project-qa-evidence-binding-and-markdown-matrix-fail-closed`。
2. `better-harness-skill-eval-kit-and-source-driven-regression-core` 保留为后续 P1/P2 research/change 输入。
3. `qa-evo-deep` 只作为后续 QA support surface 候选，不得替代 P0 runtime 修复。

## 3. Scope

### In Scope

- implementation evidence writeback / import-evidence。
- Markdown QA -> machine AC matrix 编译，编译失败必须 fail closed。
- project runner profile，至少覆盖 Go + UniApp 命令矩阵。
- admission blocker taxonomy，区分 environment blocker 与 product failure。
- BMTOP case 进入 regression fixture。

### Out Of Scope

- 直接实现 Better Harness Skill Eval Kit。
- 直接新增主生命周期 stage。
- 让 `qa-evo-deep` 直接给 release verdict。
- 把 eval JSON 作为 requirement truth。
- 自动从所有历史 trace 生成 regression core。

## 4. Route Decision

- P0 runtime 修复进入 `beacon-change-refreeze v1.4.9`。
- Better Harness 继续留在 `docs/beacon/archive/v1.4.9/research/better-harness-skill-eval-kit-and-source-driven-regression-core.md`。
- `qa-evo-deep` 继续留在 research 层，后续若接受，应作为 QA support/profile，而不是 lifecycle stage。

## 5. Freeze Deliverables

- `docs/beacon/archive/v1.4.9/research/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/archive/v1.4.9/source-architecture/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/archive/v1.4.9/change/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/archive/v1.4.9/prd/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/archive/v1.4.9/user-story/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`
- `docs/beacon/archive/v1.4.9/qa/test-cases/real-project-qa-evidence-binding-and-markdown-matrix-fail-closed.md`

## 6. Boundary

This change refreshes requirement truth only. It does not execute implementation, QA, or release.
