# Golden Commerce Checkout Fixture

Canonical full-product freeze example for Beacon agents.

## Layout

- `positive/` — valid Product → Cart → Order FSM world
- `negative-order-without-product/` — must fail freeze or QA

## Domain summary (positive)

### Entity precedence

1. Product must exist and be `listed` before OrderLine references it
2. Order must be `placed` before `paid`
3. Order must be `paid` before `shipped`

### Order FSM

| State | Allowed from | Guards | Illegal examples |
|-------|--------------|--------|------------------|
| draft | - | - | - |
| placed | draft | cart.non_empty ∧ product.listed | place without product |
| paid | placed | payment.ok | pay from draft |
| shipped | paid | - | ship before paid |
| cancelled | draft, placed | !paid | cancel after paid (v1: block) |

## Skill usage

Point `skills/beacon/examples/full-product-domain-freeze.md` here as the recommended complete demonstration.
