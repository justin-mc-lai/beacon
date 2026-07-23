# Beacon v1.6.10 Project Skill and QA Evolution Blueprint

## Public lifecycle

```text
goal
  -> plan
  -> truth (canonical main)
  -> implement (shared admission)
  -> qa (independent verifier)
  -> release (human gate)
```

The public implement surface may select direct, team, or ralph execution, but selection does not change requirement truth or admission rules.

## Shared implement admission

All implementation routes consume one decision payload:

- `allow_implement`
- `reason_code` / `reason_codes`
- `topology_kind`
- `worktree_path` for single-repo
- `service_worktree_map` for writable service scopes
- parent and service reconcile evidence
- strict branch, cwd, and HEAD verification

Workers receive admitted paths; they do not create ad hoc folders or switch the primary checkout.

## QA obligations

- Run real Git tests for single-repo and nested child-repo monorepo fixtures.
- Assert parity across direct, goal, team, and ralph.
- Assert negative paths do not dispatch write callbacks.
- Revalidate admission artifacts before accepting implementation evidence.
- Keep QA verdicts independent from the implementation generator.

## Coding standard

- Prefer one policy function with small topology-specific helpers.
- Governance Markdown is authoritative; config and machine JSON are projections or defaults.
- Reason codes are stable machine contracts.
- Avoid drive-by refactors and compatibility branches for invalid active package shapes.

