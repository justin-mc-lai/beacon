---
slug: beacon-truth-format-package-auth-skip-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-truth-format-package-auth-skip-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Truth Format Package-Auth Skip v1.6.3

## Phase A — compute_feature_paths 分流

- [x] TC-TF-001..007 测试文件 `tests/test_v163_truth_format_package_auth_skip.py` 创建（8 TC）
- [x] `beacon/utils/manifest.py compute_feature_paths` 对 ≥v1.5.2 返回 features/ 路径

## Phase B — manifest status 从 frontmatter

- [x] `beacon/utils/manifest.py sync_manifest` package-auth 包 status 取自 truth.md frontmatter
- [x] TC-TF-002 frozen 包 status=frozen

## Phase C — truth_format 跳过 package-auth

- [x] `beacon/utils/material_audit.py` truth_format 校验对 ≥v1.5.2 跳过（<v1.5.2 保持）
- [x] TC-TF-003/005 不报 truth_format_non_compliant

## Phase D — 回归

- [x] TC-TF-004 legacy 兼容（truth_format 现真正触发，非假 pass）
- [x] TC-TF-006 v1.6.2 无回归
- [x] TC-TF-007 feature_package.validate 仍调用
- [x] 8/8 TC pass；17 预存在失败均为旧包状态债（stash 对照 0 回归）
- [x] 实测：implement run 格式门禁通，只剩 implement_branch_guard（真实分支门禁）

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
