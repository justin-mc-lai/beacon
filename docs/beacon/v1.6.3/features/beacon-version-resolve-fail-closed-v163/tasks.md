---
slug: beacon-version-resolve-fail-closed-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Version Resolve Fail-Closed v1.6.3

## Phase A — 消除硬编码 fallback

- [x] TC-VR-001..007 测试文件 `tests/test_v163_version_resolve_fail_closed.py` 创建（9 TC）
- [x] `beacon/utils/project_hooks.py` 新增 `_resolve_eval_version` 纯函数，调 `resolve_target_version`，消除 `:543` 硬编码 `v1.6.1` fallback

## Phase B — runtime↔docs 漂移守卫

- [x] post-release hook payload 加 `runtime_version`/`docs_version`/`drift` 字段
- [x] `resolve_target_version` 解析失败 → fail-closed `version_resolve_failed`（短路重操作）

## Phase C — agent_eval_kit 收敛

- [x] `is_live_runner_admitted` 提到模块级 import，hook 传 resolved `eval_version`（AC-005）
- [x] `AGENT_EVAL_VERSION` 常量保留作函数默认 fallback（UD-004，不改 11 处签名以控制范围）

## Phase D — 回归

- [x] TC-VR-006 runtime==docs 正常场景不误 block（drift=False）
- [x] TC-VR-007 runtime≠docs 合法 drift 不 block（drift informational）
- [x] 9/9 TC pass；51 个 project_hooks/agent_eval 回归测试无 break

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
