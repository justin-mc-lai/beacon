---
slug: golden-commerce-checkout-positive
version: v1.6.7
status: draft
fixture: true
parser_contract: beacon-feature-package-v2
---

# Tests: Golden Commerce Checkout (Positive)

## Coverage Matrix

| AC ID | TC ID | Path type | Command | Assertion |
|-------|-------|-----------|---------|-----------|
| AC-COM-001 | TC-COM-001 | legal | `fixture-check product.listed` | create listed product succeeds |
| AC-COM-002 | TC-COM-002 | legal walk | `fixture-check order.place` | draft→placed with product succeeds |
| AC-COM-003 | TC-COM-003 | legal walk | `fixture-check order.pay` | placed→paid succeeds |
| AC-COM-004 | TC-COM-004 | legal walk | `fixture-check order.ship` | paid→shipped succeeds |
| AC-COM-005 | TC-COM-005 | illegal | `fixture-check order.place.without_product` | place order without product fails |
| AC-COM-005 | TC-COM-006 | illegal | `fixture-check order.ship.before_paid` | ship before paid fails |
