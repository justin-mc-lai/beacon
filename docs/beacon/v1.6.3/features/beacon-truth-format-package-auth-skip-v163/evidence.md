---
slug: beacon-truth-format-package-auth-skip-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 证据索引：Truth Format Package-Auth Skip v1.6.3

## Authority Surface

| surface | authority | artifact |
|---------|-----------|----------|
| truth.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md |
| tests.md | test_truth | docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tests.md |
| tasks.md | requirement_truth | docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/tasks.md |

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

- pytest junit：`tests/test_v163_truth_format_package_auth_skip.py` 8 TC，8 passed
- 实现：
  - `beacon/utils/manifest.py` compute_feature_paths 对 ≥v1.5.2 返回 features/ 路径；sync_manifest status 取自 truth.md frontmatter
  - `beacon/utils/material_audit.py` truth_format 校验对 ≥v1.5.2 跳过（<v1.5.2 保持，legacy 现真正触发）
- 回归：17 预存在失败均为旧包状态债（stash 对照 0 回归）
- 实测：v1.6.3 frozen 包 implement run 格式门禁通（`truth_format_non_compliant` 消除），只剩 `implement_branch_guard_blocked`（真实分支门禁）

## QA 阶段证据（qa 后追加）

- `beacon-eval-qa` verdict
