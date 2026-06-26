---
slug: beacon-spec-fingerprint-package-auth-paths-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-spec-fingerprint-package-auth-paths-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 任务账本：Spec Fingerprint Package-Auth Paths v1.6.3

## Phase A — _find_layer_files 分流

- [ ] TC-SF-001..007 测试文件 `tests/test_v163_spec_fingerprint_package_auth_paths.py` 创建（BLOCKED:Phase-A）
- [ ] `beacon/utils/v110_baseline.py _find_layer_files` 对 ≥v1.5.2 扫 features/<slug>/{truth,tests}.md

## Phase B — 验证 fingerprint 反映 truth

- [ ] TC-SF-003 改 truth.md 后 fingerprint hash 改变
- [ ] TC-SF-005 test_case 层保留 .machine/qa 扫描

## Phase C — 回归

- [ ] TC-SF-004 legacy 兼容
- [ ] TC-SF-006 v1.6.3 release gate 仍 pass
- [ ] TC-SF-007 v1.6.2 无回归

## checkbox 不自证 closure

checkbox 仅追踪实现进度；closure 以 tests.md 的 TC 全 pass + `beacon-eval-qa` verdict 为准。
