# DESIGN.md (stub) — Golden Commerce Checkout

Minimal design stub for fixture lake AC-GOLD-006.

## Order state badges

| State | Color token | Label |
|-------|-------------|-------|
| draft | gray | Draft |
| placed | blue | Placed |
| paid | green | Paid |
| shipped | purple | Shipped |
| cancelled | red | Cancelled |

## Do

- Bind badge to Domain FSM Order state only
- Disable primary action when transition is illegal

## Don't

- Show "Ship" on unpaid orders
- Invent states not in Domain FSM
