---
slug: beacon-v2-ui-state-matrix-ship-gate
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-ui-state-matrix-ship-gate/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 UI State Matrix Ship Gate

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-UID-001 | TC-V2-UID-001 | contract | `python3 -m pytest tests/test_v200_ui_state_matrix.py::test_matrix_schema -q` | matrix 绑定 FSM |
| AC-V2-UID-003 | TC-V2-UID-002 | negative | `python3 -m pytest tests/test_v200_ui_state_matrix.py::test_missing_matrix_blocks_release -q` | 缺矩阵阻断 ship |
| AC-V2-UID-004 | TC-V2-UID-003 | negative | `python3 -m pytest tests/test_v200_ui_state_matrix.py::test_primitives_only_insufficient -q` | 仅 primitives 不足 |
| AC-V2-UID-008 | TC-V2-UID-004 | parity | `python3 -m pytest tests/test_v200_ui_state_matrix.py::test_v167_inherit -q` | v167 语义继承 |
