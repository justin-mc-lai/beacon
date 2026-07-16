---
slug: golden-commerce-checkout-positive
status: draft
---

# Tests

| AC ID | TC ID | Path type | Assertion |
|-------|-------|-----------|-----------|
| AC-COM-001 | TC-COM-001 | legal | create listed product succeeds |
| AC-COM-002 | TC-COM-002 | legal walk | draft→placed with product succeeds |
| AC-COM-003 | TC-COM-003 | legal walk | placed→paid succeeds |
| AC-COM-004 | TC-COM-004 | legal walk | paid→shipped succeeds |
| AC-COM-005 | TC-COM-005 | illegal | place order without product fails |
| AC-COM-005 | TC-COM-006 | illegal | ship before paid fails |
