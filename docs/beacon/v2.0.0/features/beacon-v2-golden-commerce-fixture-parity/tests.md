---
slug: beacon-v2-golden-commerce-fixture-parity
version: v2.0.0
status: draft
revision_id: R1
truth_ref: docs/beacon/v2.0.0/features/beacon-v2-golden-commerce-fixture-parity/truth.md
parser_contract: beacon-feature-package-v2
---

# Tests: v2 Golden Commerce Fixture Parity

## Coverage Matrix

| AC ID | TC ID | Layer | Command | Assertion |
|-------|-------|-------|---------|-----------|
| AC-V2-GOLD-001 | TC-V2-GOLD-001 | contract | `python3 -m pytest tests/test_v200_golden_commerce.py::test_positive_package -q` | 正例包完整 |
| AC-V2-GOLD-002 | TC-V2-GOLD-002 | negative | `python3 -m pytest tests/test_v200_golden_commerce.py::test_negative_order_without_product -q` | 负例必失败 |
| AC-V2-GOLD-004 | TC-V2-GOLD-003 | contract | `python3 -m pytest tests/test_v200_golden_commerce.py::test_v2_index_resolves -q` | 索引可解析 |
