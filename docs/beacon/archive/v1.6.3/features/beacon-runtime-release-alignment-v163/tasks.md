---
slug: beacon-runtime-release-alignment-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-runtime-release-alignment-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Runtime Release Alignment v1.6.3

## Phase A — release gate drift 阻断

- [ ] TC-RA-001..007 测试文件 `tests/test_v163_runtime_release_alignment.py` 创建（BLOCKED:Phase-A）
- [ ] `beacon/commands/gate.py` 加 `check_runtime_release_alignment`（release stage，runtime≠docs → block）

## Phase B — hook runtime_alignment 步骤

- [ ] `beacon/utils/project_hooks.py` 加 runtime_alignment 步骤（检测+路由 sync-version-surfaces+payload）
- [ ] TC-RA-003/004 payload 含 runtime_alignment + recommended_command

## Phase C — 回归

- [ ] TC-RA-002 runtime==docs 不 block
- [ ] TC-RA-005 开发期 stage 不 block
- [ ] TC-RA-006 hook 无 pip install
- [ ] TC-RA-007 P0-1 守卫仍生效

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
