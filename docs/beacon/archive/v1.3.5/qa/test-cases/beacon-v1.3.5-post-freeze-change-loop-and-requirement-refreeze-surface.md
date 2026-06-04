# Test Cases: beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface

## Overview

**Feature**: beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface  
**Test Type**: ALL  
**Version**: v1.3.5  
**Generated**: 2026-04-20 22:40  
**Purpose**: 验证 Beacon 冻结后需求调整闭环、生命周期状态机和 `beacon-change` 宿主路由语义。

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
| AC-001 | TC-001 | unit | `python3 -m pytest -q -k beacon_change_surface` | 不新增 Beacon 一级主命令，且 `beacon-change` 作为宿主子 skill 草案可被发现与引用 | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-001.json` |
| AC-002 | TC-002 | unit | `python3 -m pytest -q -k reopen_refreeze_flow` | 冻结后需求调整可形成 `reopen -> refresh -> re-freeze -> fix -> delta-run -> recheck` 的正式闭环 | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-002.json` |
| AC-003 | TC-003 | unit | `python3 -m pytest -q -k lifecycle_state_machine_doc` | 生命周期状态机文档覆盖状态、迁移、阻断与产物边界 | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-003.json` |
| AC-004 | TC-004 | unit | `python3 -m pytest -q -k revision_truth_binding` | implement / qa / release 只能绑定最新 frozen revision，旧 baseline 不得静默复用 | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-004.json` |
| AC-005 | TC-005 | unit | `python3 -m pytest -q -k help_status_change_route` | `help/status` 在冻结后 change intent 下稳定推荐 `beacon-change` | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-005.json` |
| AC-006 | TC-006 | unit | `python3 -m pytest -q -k release_revision_semantics` | `release` 能区分 initial / revised / hotfix delivery 的 gate 语义 | `.beacon/evidence/test-results/beacon-v1.3.5-post-freeze-change-loop-and-requirement-refreeze-surface/TC-006.json` |

---

## Scenario Notes

### TC-001 宿主 surface 克制

- 检查 `beacon-change` 只作为子 skill 草案存在。
- 检查 PRD 文档未引入新的 Beacon 一级命令。

### TC-002 需求调整再闭环

- 前置：feature 已冻结。
- 步骤：change intake -> reopen -> delta compile -> prototype refresh -> re-freeze。
- 断言：新的 revision baseline 被 materialize。

### TC-003 生命周期状态机文档完整

- 检查状态机至少覆盖：
  - `context_bootstrap`
  - `requirement_drafting`
  - `freeze_ready`
  - `prototype_freeze`
  - `change_requested`
  - `revision_reopened`
  - `delta_recompiled`
  - `re_freeze_ready`
  - `fix_in_progress`
  - `re_release_ready`

### TC-004 最新真相绑定

- 检查 revised baseline 生成后，旧 baseline 不再作为默认 implement/qa/release truth。

### TC-005 帮助路由稳定

- 检查冻结后 change intent 文案被稳定路由到 `beacon-change`，而不是随机落到 `beacon-prd`。

### TC-006 release 语义区分

- 检查 revised delivery / hotfix delivery 在 gate 说明中有正式字段或等价语义。

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | AC-001 |
| TC-002 | Pending | AC-002 |
| TC-003 | Pending | AC-003 |
| TC-004 | Pending | AC-004 |
| TC-005 | Pending | AC-005 |
| TC-006 | Pending | AC-006 |
