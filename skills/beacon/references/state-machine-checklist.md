# State Machine Checklist

This is a non-canonical support reference for humans.

Use it when a feature depends on state transitions, visibility rules, or lifecycle conditions and you want to know whether the state model is explicit enough.

## Checklist

- important states are named
- transitions are explicit
- invalid or blocked transitions are visible
- side effects on transition are visible
- the state model is clear enough for implementation and QA
- if the state model changes promised behavior or acceptance, route to `beacon-change`

## Route Hint

- state model still unclear -> `beacon-deep` or `beacon-brainstorm`
- state model clear but execution not done -> `beacon-implement`
- state model clear but verification weak -> `beacon-qa`
