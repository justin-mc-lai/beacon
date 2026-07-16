---
slug: beacon-post-release-hook-agent-coverage-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-post-release-hook-agent-coverage-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Post-Release Hook Agent Coverage v1.6.3

## Phase A — hook agent 循环全覆盖

- [ ] TC-HK-001..007 测试文件 `tests/test_v163_post_release_hook_agent_coverage.py` 创建（BLOCKED:Phase-A）
- [ ] `beacon/utils/project_hooks.py:520` agent 循环改为全 5 agent，复用 agent_surface 常量

## Phase B — drift 阻断验证

- [ ] TC-HK-003 drift 时 hook block
- [ ] TC-HK-002 payload 含 5 agent setup/verify

## Phase C — 回归

- [ ] TC-HK-004 claude 全局保留
- [ ] TC-HK-005 codex/claude force/strict 不变
- [ ] TC-HK-006 block reason_codes 语义不变
- [ ] TC-HK-007 常量复用无新硬编码

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
