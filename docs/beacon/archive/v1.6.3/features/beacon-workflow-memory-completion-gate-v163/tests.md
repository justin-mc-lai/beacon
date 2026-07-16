---
slug: beacon-workflow-memory-completion-gate-v163
version: v1.6.3
status: draft
revision_id: R1
language: zh
truth_ref: docs/beacon/archive/v1.6.3/features/beacon-workflow-memory-completion-gate-v163/truth.md
parser_contract: beacon-feature-package-v1
---

# 测试：Workflow Memory Completion Gate v1.6.3

## 覆盖矩阵

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-001 | TC-WM-001 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_no_run_resolved_warns -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | target_run_id=None → status=warn, blocked=False, reason_code=workflow_memory_no_run_resolved |
| AC-002 | TC-WM-002 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_run_without_transaction_fails -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | run 存在但无 transaction → status=fail, blocked=True, reason_code=workflow_memory_transaction_missing |
| AC-003 | TC-WM-003 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_gate_blocks_on_missing_transaction -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 有 run 无 transaction 时 gate issue blocked=True |
| AC-004 | TC-WM-004 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_fresh_project_not_blocked -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | 无 run 的 fresh project gate 不因 memory_transaction 误 block |
| AC-005 | TC-WM-005 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_existing_semantics_preserved -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | failed_transaction→fail, drift→fail, ok→pass 语义不变 |
| AC-006 | TC-WM-006 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_status_distinguishes_reason_codes -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | no-run vs run-without-tx 的 reason_code 不同 |
| AC-007 | TC-WM-007 | contract | `python3 -m pytest tests/test_v163_workflow_memory_completion_gate.py::test_pass_when_transaction_ok -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"` | run 且 transaction ok → status=pass, blocked=False |

## 验证说明

- TC 文件 `tests/test_v163_workflow_memory_completion_gate.py` 由 implement 阶段创建；Phase 实现前允许 tasks 标注 `BLOCKED:Phase-A`。
- TC-001/002/005/006/007 单元测试 `workflow_memory_transaction_contract`，用 `tmp_path` 构造 runs/transactions 目录；TC-003/004 集成 `check_workflow_memory_closure`（gate 段）。
- 每行 TC 的 Command 含 `pytest`，Assertion 在测试函数体内以 `assert` 表达。

## Must vs Should

| 优先级 | AC |
|--------|-----|
| Must | AC-001..007 |

---

**Revision:** R1 — truth.coverage；待 Round 5 verify-closure + Round 7 freeze。
