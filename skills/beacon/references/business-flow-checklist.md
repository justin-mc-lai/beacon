# Business Flow Checklist

This is a non-canonical support reference for humans.

Use it when a feature depends on actors, steps, handoffs, or multi-stage outcomes and you want to know whether the business flow is clear enough.

## Checklist

- start state and end state are explicit
- actor handoffs are explicit
- major branches or exceptions are visible
- side effects and external dependencies are named
- the flow is readable enough to compile into `user-story` and `test-case`
- if the flow implies a different promised behavior, route to `beacon-change`

## Route Hint

- flow still unclear -> `beacon-brainstorm` or `beacon-prd`
- flow clear but acceptance weak -> `beacon-user-story` or `beacon-test-case`
