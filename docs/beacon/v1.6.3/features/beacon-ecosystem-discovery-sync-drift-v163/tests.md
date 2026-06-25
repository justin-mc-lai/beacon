---
slug: beacon-ecosystem-discovery-sync-drift-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/v1.6.3/features/beacon-ecosystem-discovery-sync-drift-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Ecosystem Discovery & Sync Drift Repair v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-EC-001 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_manifest_sync_discovers_features_dir -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | manifest sync 对 ≥v1.5.2 扫到 features/<slug>/ 下的包 |
| AC-002 | TC-EC-002 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_sync_materials_rebuilds_hash -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | sync-materials 后 truth-map verify 无 machine_json_source_hash_stale |
| AC-003 | TC-EC-003 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_freeze_rebuilds_machine -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | freeze 后 .machine source hash 与 frozen truth 一致 |
| AC-004 | TC-EC-004 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_legacy_manifest_sync_unchanged -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | <v1.5.2 manifest sync 仍只扫旧目录 |
| AC-005 | TC-EC-005 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_no_regression_v162 -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.2 feature 包修复后仍 pass |
| AC-006 | TC-EC-006 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_no_regression_v163_packages -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | v1.6.3 四个 frozen 包 truth-map verify pass |
| AC-007 | TC-EC-007 | contract | `python3 -m pytest tests/test_v163_ecosystem_discovery_sync_drift.py::test_discover_features_finds_packages -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | _discover_features 经 manifest 发现 features/ 包 |

## 验证说明

- TC 文件 `tests/test_v163_ecosystem_discovery_sync_drift.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/004/007 用 `tmp_path` 构造版本目录树测扫描逻辑；TC-002/003 用 tmp_path + monkeypatch 测 sync/freeze 行为；TC-005/006 对本项目真实包断言。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
