---
slug: beacon-v2-truth-human-readable-i18n
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-truth-human-readable-i18n/truth.md
---

# Tests: beacon-v2-truth-human-readable-i18n

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-HR-001 | TC-V2-HR-001 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py::test_parity_upstream_ac -q` | parity map |
| AC-V2-HR-002 | TC-V2-HR-002 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py::test_self_l0 -q` | self L0 |
| AC-V2-HR-003 | TC-V2-HR-003 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py::test_shared_norms -q` | norms exist |
| AC-V2-HR-004 | TC-V2-HR-004 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py::test_axis_has_lake -q` | axis mount |
| AC-V2-HR-005 | TC-V2-HR-005 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py::test_reason_code_stable -q` | reason stable |
| AC-V2-HR-006 | TC-V2-HR-006 | contract | `python3 -m pytest tests/test_v200_truth_human_readable_i18n.py -q` | no second standard |
