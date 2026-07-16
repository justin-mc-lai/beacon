---
slug: golden-commerce-checkout-negative-no-product
version: v1.6.7
status: draft
revision_id: R0
language: zh
parser_contract: beacon-feature-package-v2
fixture: true
expected_gate: freeze_or_qa_fail
domain_required: true
---

# Negative Fixture: Order Without Product

## Intentional defect

Acceptance claims "user can place order" **without** Domain Model Product precedence or illegal-transition coverage.

## Expected system behavior

- freeze blocked with domain_fsm / entity_precedence reason, **or**
- QA fails illegal path TC

This fixture must never pass full product goal done_when.
