---
slug: golden-commerce-checkout-negative-no-product
version: v1.6.7
status: draft
fixture: true
expected_gate: freeze_or_qa_fail
parser_contract: beacon-feature-package-v2
---

# Tests: Negative Order Without Product

## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-NEG-001 | TC-NEG-001 | illegal | `fixture-check order.without_product` | must fail freeze or QA |
