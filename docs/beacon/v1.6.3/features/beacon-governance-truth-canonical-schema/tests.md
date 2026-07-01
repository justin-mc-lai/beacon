---
slug: beacon-governance-truth-canonical-schema
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-governance-truth-canonical-schema/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Governance Truth-Canonical Schema v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-GTC-001 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_assign_version_kv_recognizes_new_fields -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `_assign_version_kv` 对 key=`truth_canonical`/`runtime_mirror` 写入 contract 且不静默丢弃；`_parse_version_contracts` 从含双字段的 governance MD 解析出 `truth_canonical`/`runtime_mirror` 值 |
| AC-002 | TC-GTC-002 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_render_and_commit_roundtrip -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `render_governance_markdown` 回写双字段到 MD；`commit_governance_payload` 后 transaction_id/source_hash 重算且 sqlite projection sync（payload 含双字段） |
| AC-003 | TC-GTC-003 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_resolver_accepts_main_as_truth_canonical -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | contract 含 `truth_canonical: main` 时，`doctor branch-governance`/`git-alignment` resolver 接受 current_branch=main 为 truth canonical base，不再产生 `git_branch_target_mismatch` |
| AC-004 | TC-GTC-004 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_backward_compat_legacy_contract -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | contract 仅含旧 `per_service_canonical_branch`（无双字段）时，resolver 行为与改动前一致（基线快照对比，无新阻断） |
| AC-005 | TC-GTC-005 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_git_alignment_unblocked_v163 -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.3 contract 补双字段后，`beacon doctor verify-delivery --version v1.6.3` 的 git-alignment 不再 `blocked=true`（reason_codes 不含 git_branch_target_mismatch/git_branch_prefix_mismatch/git_version_ref_not_satisfied） |
| AC-006 | TC-GTC-006 | contract | `python3 -m pytest tests/test_v163_governance_truth_canonical_schema.py::test_no_worktree_admission_flow_break -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 双字段 contract 下 `beacon workspace admit`（dry-run）/`doctor branch-governance verify --version v1.6.3` 行为可解释且不误阻断（status=pass 或可解释 non-blocked reason） |

## 验证说明

- TC 文件 `tests/test_v163_governance_truth_canonical_schema.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001/002 用 `tmp_path` 构造 governance MD + 调用 `parse_governance_markdown`/`render_governance_markdown`/`commit_governance_payload` 断言字段持久化与 roundtrip。
- TC-003/004/005 用 `tmp_path` 项目 + monkeypatch resolver，对比双字段 vs 旧字段 resolver 输出。
- TC-006 用 `beacon workspace admit --dry-run` + `doctor branch-governance verify` 子进程断言流向不破坏。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..006 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
