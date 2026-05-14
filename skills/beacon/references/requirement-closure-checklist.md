# Requirement Closure Checklist

This is a non-canonical support reference for humans.

Use it to quickly check whether requirement truth is actually closed enough to continue.

## Checklist

- problem, user outcome, and business promise are explicit
- scope boundary is explicit
- out-of-scope is explicit
- acceptance can be compiled into `user-story` and `test-case`
- ambiguous terms have been resolved or explicitly parked
- if frozen truth must change, route to `beacon-change`

## Route Hint

- still unclear -> `beacon-prd`
- promise clear but acceptance weak -> `beacon-user-story`
- acceptance clear but verifiable scenarios weak -> `beacon-test-case`
