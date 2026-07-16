---
slug: beacon-qa-business-state-machine-v164
version: v1.6.4
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.4/features/beacon-qa-business-state-machine-v164/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：QA Business State Machine v1.6.4

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-SM-001 | contract | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_fsm_extract_from_truth -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 从 truth.md State Machine 段落 + AC 提取 FSM（states + transitions + boundary + unreachable）；提取失败（段落缺失/格式错）→ block，reason_code 含 `fsm_extract_failed` |
| AC-002 | TC-SM-002 | contract | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_state_coverage_model -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 状态覆盖模型：每条转换至少 1 TC；边界态（初始/终态/非法转换目标）有覆盖；未覆盖转换标记 gap |
| AC-003 | TC-SM-003 | contract | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_state_machine_coverage_field -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | `build_qa_profile_completeness` 输出含 `state_machine_coverage`（转换覆盖率 + 边界态覆盖 + 不可达态列表 + gap）；projection 同步 |
| AC-004 | TC-SM-004 | contract | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_boundary_coverage_derivation -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 从 FSM 自动推导边界 TC（初始态进入 / 终态退出 / 非法转换拒绝）；边界态未覆盖 → 标记 `boundary_gap` |
| AC-005 | TC-SM-005 | contract | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_unreachable_state_reject -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 不可达态被触达 → fail-closed block，reason_code 含 `unreachable_state_reached`；evidence 不被记为 pass |
| AC-006 | TC-SM-006 | integration | `python3 -m pytest tests/test_v164_qa_business_state_machine.py::test_confidence_chain_integration -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 状态覆盖缺口削弱对应层置信度（`state_machine_gap` 标记接入 Phase 2 `confidence_chain`）；与 Phase 2 字段共存 |

## 验证说明

- TC 文件 `tests/test_v164_qa_business_state_machine.py` 由 implement 阶段创建；实现前 tasks 允许标注 `BLOCKED:implement`。
- TC-001..005 为 contract 层（构造 truth.md FSM 段落 fixture + 调用提取/覆盖函数断言）。
- TC-006 为 integration 层，需 Phase 2 `confidence_chain` 字段（import 校验共存）。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..006 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
