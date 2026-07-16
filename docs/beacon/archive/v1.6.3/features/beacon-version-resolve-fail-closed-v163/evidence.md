---
slug: beacon-version-resolve-fail-closed-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Version Resolve Fail-Closed v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/truth.md |
| tests.md | test_truth | docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tests.md |
| tasks.md | requirement_truth | docs/beacon/archive/v1.6.3/features/beacon-version-resolve-fail-closed-v163/tasks.md |

## Truth 阶段证据（已发生）

| Round | 产物 | 结果 |
|-------|------|------|
| R1 truth.define | truth.md | draft |
| R1 truth.coverage | tests.md | draft |
| R4 weak-assertion 扫描 | soft_tc_scan | pass |
| R5 deferral 扫描 | deferral_scan | pass |
| R5 verify-closure | closure_allowed | pass |
| R6 sync-requirement-clarity | blocked | none |
| R7 freeze | status | frozen |

## Implement 阶段证据（已发生）

- pytest junit：`tests/test_v163_version_resolve_fail_closed.py` 9 TC，9 passed
- 实现：
  - `beacon/utils/project_hooks.py` 新增 `_resolve_eval_version` 纯函数（调 `resolve_target_version`），消除硬编码 `v1.6.1` fallback
  - post-release hook payload 加 `runtime_version`/`docs_version`/`drift` 字段；resolve 失败 fail-closed `version_resolve_failed`
  - `is_live_runner_admitted` 提到模块级 import，hook 传 resolved 版本
- 回归：51 个 project_hooks/agent_eval 相关测试无 break；3 个 v1.6.3 包 verify-closure pass

## QA 阶段证据（qa 后追加）

- `beacon-eval-qa` verdict
