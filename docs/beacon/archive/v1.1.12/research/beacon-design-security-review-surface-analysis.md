# Beacon Design Security Review Surface Analysis

**Version**: `v1.1.12`
**Question**: software-design security should live where?

## Conclusion

Beacon should **not** copy gstack `cso` as a new top-level command.

Beacon should add software-design security under:

```text
review design
```

because Beacon's job is requirement/prototype/evidence governance, not infra-first repository security operations.

## Why not a top-level `cso`

gstack `cso` is infrastructure-first:

- secrets archaeology
- dependency/supply-chain review
- CI/CD and pipeline risk
- runtime security posture

Beacon should not absorb that whole surface.

If Beacon adds a top-level `cso`, it starts to blur:

- requirement kernel
- review/gate evidence kernel
- project runtime / infra security tooling

That is exactly the boundary `v1.1.12` is trying to tighten.

## Why `review design`

The new security questions are design-review questions:

1. does this prototype expose privileged actions without actor/role boundaries
2. does an upload flow exist without size/type/validation constraints
3. are token/password/secret surfaces described without masking or storage guidance
4. do external integrations appear without trust-boundary checks
5. do sensitive actions lack audit/evidence trace requirements

These are:

- downstream of user-story / PRD
- upstream of freeze / gate
- naturally consumed by review artifacts

So they belong in `review`, not in a new product surface.

## Recommended Beacon shape

```text
prototype create
→ prototype review
→ review design
→ gate
```

Where:

- `prototype review` handles design-governance and web-guideline truth
- `review design` adds cso-inspired software-design security findings
- `gate` consumes both as release inputs

## Scope boundary

`review design` should cover:

- privileged-action boundary clarity
- upload / file-surface constraints
- secret-handling surface clarity
- external integration trust boundaries
- auditability / evidence trace expectations

It should **not** become:

- dependency scanner
- secrets scanner
- infra / CI/CD audit
- repo-wide OWASP runtime assessor

Those belong to project-specific security workflows outside Beacon core.
