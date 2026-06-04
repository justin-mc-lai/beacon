# Beacon v1.3.10 Boundaries

## In Scope

- project-level topology metadata
- version-scoped service participation and allowed working branch contracts
- deterministic human support surface via `beacon doctor metadata ...`
- requirement package dual-write gate for `freeze / implement / qa / release`
- help/status/report/proof remediation convergence

## Out of Scope

- project-wide Git workflow engine
- automatic branch switching or hidden repo mutation
- CI/CD orchestration
- promoting `doctor sync-materials` back into normal change-loop mainline

## Explicit Constraints

- no new public top-level Beacon command
- no sqlite-only truth source
- no prompt-side re-inference when resolved metadata view already exists
