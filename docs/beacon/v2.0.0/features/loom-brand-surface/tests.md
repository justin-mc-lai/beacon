---
slug: loom-brand-surface
version: v2.0.0
status: frozen
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/loom-brand-surface/truth.md
---

# Tests: loom-brand-surface

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-LOOM-BR-001 | TC-LOOM-BR-001 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_naming_contract -q` | names locked |
| AC-LOOM-BR-002 | TC-LOOM-BR-002 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_dual_install_names -q` | distinct CLI names |
| AC-LOOM-BR-003 | TC-LOOM-BR-003 | negative | `python3 -m pytest tests/test_v200_loom_brand.py::test_no_replace_beacon -q` | install must not overwrite beacon |
| AC-LOOM-BR-004 | TC-LOOM-BR-004 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_loom_goal_facade -q` | loom-goal public primary |
| AC-LOOM-BR-005 | TC-LOOM-BR-005 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_beacon_preserved -q` | beacon-goal remains |
| AC-LOOM-BR-006 | TC-LOOM-BR-006 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_state_isolation -q` | .loom vs .beacon |
| AC-LOOM-BR-007 | TC-LOOM-BR-007 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_dual_matrix_doc -q` | matrix present |
| AC-LOOM-BR-008 | TC-LOOM-BR-008 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_examples -q` | 30s example |
| AC-LOOM-BR-009 | TC-LOOM-BR-009 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_no_early_default -q` | no default replace claim |
| AC-LOOM-BR-010 | TC-LOOM-BR-010 | contract | `python3 -m pytest tests/test_v200_loom_brand.py::test_legal_illegal_rows -q` | legal/illegal rows |

## Legal / Illegal

| TC ID | Path | Assertion |
|-------|------|-----------|
| TC-LOOM-BR-LEGAL-01 | dual install | beacon and loom binaries coexist |
| TC-LOOM-BR-ILLEGAL-01 | overwrite | install must not replace beacon path |
