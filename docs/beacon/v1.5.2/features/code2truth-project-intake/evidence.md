# Evidence: Code2Truth Project Intake

## Evidence Index

| Surface | Authority | Canonical Artifact | Status | Route |
|---------|-----------|--------------------|--------|-------|
| beacon-brainstorm | support_advisory | docs/beacon/v1.5.2/research/code2truth-project-intake.md | adopted | truth.define |
| source-architecture | support_advisory | docs/beacon/v1.5.2/source-architecture/code2truth-project-intake.md | indexed | truth.define |
| feature-package | requirement_truth | docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md | authoritative | truth.define |
| package-tests | test_truth | docs/beacon/v1.5.2/features/code2truth-project-intake/tests.md | authoritative | truth.coverage |
| package-tasks | support_advisory | docs/beacon/v1.5.2/features/code2truth-project-intake/tasks.md | task-intent-indexed | implement |
| qi-dev-understand-anything | support_advisory | /Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/qi-dev/qi-dev-understand-anything/SKILL.md | provider-indexed | source-driven |
| understand-anything-artifacts | support_advisory | .understand-anything/knowledge-graph.json; .understand-anything/graph-build-report.json | optional-provider-evidence | source-driven |
| doctor-governance | support_advisory | beacon doctor metadata verify --project-root . --version v1.5.2 --json | required-before-qa | qa |

## Decision Record

- Accepted: code can propose candidate truth, but user-confirmed Beacon package Markdown is formal truth.
- Accepted: `qi-dev-understand-anything` and similar tools are useful evidence providers, not truth authorities.
- Accepted: existing implementation may satisfy frozen truth without source changes.
- Accepted: `beacon implement` may close as no-op/evidence-only only when ACs are already proven by current behavior and evidence.
- Accepted: QA validates truth/evidence/governance/current behavior rather than code churn.
- Accepted: ambiguity, stale behavior, conflicting evidence, and low confidence fail closed.

## Boundary

`evidence.md` is an index/read model. It must not contain final verdict, gate truth, release readiness, or source-of-truth override fields.
