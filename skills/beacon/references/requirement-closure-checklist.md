# Requirement Closure Checklist

This is a non-canonical support reference for humans.

Use it to quickly check whether requirement truth is actually closed enough to continue.

## Checklist

- requirement chain is explicit: `research -> prd -> user-story -> test-case -> requirement_clarity -> freeze`
- problem, user outcome, and business promise are explicit
- scope boundary is explicit
- out-of-scope is explicit
- acceptance can be compiled into `user-story` and `test-case`
- ambiguous terms have been resolved or explicitly parked
- every upstream AC can be projected into `test-case` truth
- if frozen truth must change, route to `beacon-change`

## Route Hint

- still unclear -> `beacon-prd`
- promise clear but acceptance weak -> `beacon-user-story`
- acceptance clear but verifiable scenarios weak -> `beacon-test-case`
