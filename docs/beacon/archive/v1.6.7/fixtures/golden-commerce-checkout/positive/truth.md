---
slug: golden-commerce-checkout-positive
version: v1.6.7
status: frozen
revision_id: R0
language: zh
parser_contract: beacon-feature-package-v2
truth_source_model: feature_package_authoritative
fixture: true
domain_required: true
---

# Golden Fixture Truth: Commerce Checkout (Positive)

## Domain Model

| Entity | Key | Precedence |
|--------|-----|------------|
| Product | product_id | root catalog entity |
| Cart | cart_id | requires User session |
| Order | order_id | requires ≥1 OrderLine → Product.listed |
| OrderLine | order_line_id | requires Product |

## Domain FSM — Product

| State | From | Guard |
|-------|------|-------|
| draft | - | - |
| listed | draft | title+price present |
| archived | listed | - |

## Domain FSM — Order

| State | From | Guard | Side effects |
|-------|------|-------|--------------|
| draft | - | - | - |
| placed | draft | lines.non_empty ∧ all products.listed | reserve stock |
| paid | placed | payment.ok | capture payment |
| shipped | paid | - | create shipment |
| cancelled | draft, placed | !paid | release stock |

## Illegal transitions (must have TC)

- Order.placed without Product
- Order.paid from draft
- Order.shipped before paid

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-COM-001 | User can create listed Product |
| AC-COM-002 | User can place Order only with listed Product lines |
| AC-COM-003 | User can pay placed Order |
| AC-COM-004 | User can ship paid Order |
| AC-COM-005 | System rejects order without product (illegal) |
