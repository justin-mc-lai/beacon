# Implement Ralph Mode

## Purpose

Use `ralph` as a closure controller when team or complex implementation evidence needs multi-round repair routing toward review, QA, or release.

## Admission

- Requirement truth is frozen.
- Team or complex implementation has produced evidence, but closure is not authoritative.
- Review quality, QA, or release next action must be routed.
- Ralph can record blocker, next action, round trace, and evidence refs.

## Command

```bash
beacon implement run "<feature>" --project . --version <version> --mode ralph
```

## Evidence

- Ralph round trace.
- Current blocker and next action.
- Recommended command for implement repair, QA, or release.

## Boundary

Ralph routes next action and evidence only; it never replaces QA, release, gate, or frozen truth.
