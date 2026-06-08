# Research: code2truth-project-intake

**Feature**: `code2truth-project-intake`
**Version**: `v1.5.2`
**Status**: `support-research`

## Support Findings

### Brainstorm

#### Round 2026-06-05T09:09:04.093493+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-05T09:09:04.093493+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-test-case
- finding_summary: Treat this as an evolution candidate. Capture options in brainstorm output first, then route accepted scope through beacon-prd or beacon-change.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/v1.5.2/SUMMARY.md`, `docs/beacon/v1.5.2/execution/index.md`, `docs/beacon/v1.5.2/execution/architecture-blueprint.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/tests.md`

## Deep Summary

#### Round 2026-06-05T09:31:44.526655+00:00

- source_skill: `beacon-brainstorm`
- round_id: `2026-06-05T09:31:44.526655+00:00`
- material_effect: `read_only_route_only`
- adoption_status: `route_only`
- route_decision: beacon-test-case
- finding_summary: Converge missing or ambiguous requirement points into explicit questions and candidate decisions before editing frozen truth.
- source_refs: `docs/beacon/global-boundaries.md`, `docs/beacon/v1.5.2/SUMMARY.md`, `docs/beacon/v1.5.2/execution/index.md`, `docs/beacon/v1.5.2/execution/architecture-blueprint.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/truth.md`, `docs/beacon/v1.5.2/features/code2truth-project-intake/tests.md`
### External code-map providers

`code2truth-project-intake` should explicitly support third-party or adjacent local code-map tools as evidence providers instead of pretending Beacon must infer the entire project graph by itself.

Recommended provider model:

- Beacon-native providers:
  - `beacon-source-driven`: source-anchored reasoning discipline.
  - `beacon lighthouse`: repository/file/system map support.
  - `beacon source-architecture`: Beacon-managed architecture projection.
  - `truth-map`: package-authoritative destination resolver.
- Local/third-party providers:
  - `qi-dev-understand-anything`: deterministic code-node/import graph provider for local repositories.

`qi-dev-understand-anything` is useful because it can run the mirrored Understand-Anything graph tooling through:

```bash
/Users/apple/.codex/skills/qi-dev/scripts/qi_dev.sh understand-anything analyze <project-root>
```

It can produce:

- `.understand-anything/intermediate/scan-result.json`
- `.understand-anything/intermediate/import-map.json`
- `.understand-anything/intermediate/batches.json`
- `.understand-anything/intermediate/structure-result.json`
- `.understand-anything/knowledge-graph.json`
- `.understand-anything/graph-build-report.json`
- `.understand-anything/meta.json`

Adoption rule:

- Treat these artifacts as deterministic repository navigation evidence: files, modules, functions, classes, exports, `contains`, and `imports` relationships.
- Do not treat them as full business semantics unless a separate semantic analysis phase has been run and accepted.
- Every candidate truth claim derived from these artifacts must still cite concrete source refs and confidence.
- Low-confidence, ambiguous, stale, or conflicting graph evidence must fail closed into questions or candidate notes, not authoritative truth.

This keeps the user mental model simple:

```text
code maps and graphs help Beacon understand the project faster,
but accepted Beacon package truth is still the only formal truth.
```

### Candidate skill shape

If promoted into a formal Beacon feature, the support skill should expose a provider-aware intake flow:

```bash
beacon code2truth intake <project-root> \
  --version v1.5.2 \
  --feature-scope auto \
  --provider beacon,lighthouse,source-architecture,understand-anything \
  --json
```

Expected behavior:

1. Detect available providers without requiring the user to remember every tool.
2. Prefer Beacon-native providers when enough.
3. Use `qi-dev-understand-anything` when present for deterministic code graph enrichment.
4. Store external graph refs in support research or evidence index, not directly in package truth.
5. Generate candidate `truth.md`, `tests.md`, `tasks.md`, and `evidence.md` drafts only after confidence and authority classification are explicit.
6. Route accepted output back through `beacon-truth` / `beacon-change-refreeze` before freeze.

### Closed-loop convergence

The intended closed loop is valid when the project already contains working behavior and the user's goal is to bring that behavior under Beacon v1.5.2 truth governance:

```text
existing implementation
  -> source/code-map evidence
  -> candidate truth reconstruction
  -> user confirmation
  -> frozen Beacon package truth
  -> implement no-op or evidence-only execution
  -> beacon QA verifies truth/evidence/governance
```

This is not `code is truth`. The correct rule is:

```text
code can propose candidate truth;
user-confirmed and frozen Beacon package Markdown is formal truth.
```

`beacon implement` can be a no-code-change pass only when all of these are true:

- `features/<slug>/truth.md` and `features/<slug>/tests.md` exist and are resolver-selected as package-authoritative truth.
- Candidate truth claims are backed by source refs, provider artifacts, tests, CLI behavior, or runtime evidence.
- The user has accepted the reconstructed behavior as intended product truth, not merely observed implementation behavior.
- No acceptance criterion requires a new or changed code path.
- Ambiguous, stale, conflicting, or low-confidence behavior has been excluded, downgraded to open questions, or routed through change.
- `tasks.md` marks implementation work as satisfied by existing code, with evidence refs instead of fake code churn.

In that case, implementation closure should write or update execution evidence and task state, not force source changes for their own sake.

QA then validates the delivery by checking:

- truth-map resolves the frozen package as authority.
- `truth.md` acceptance claims trace to source/evidence.
- `tests.md` includes coverage rows for reconstructed behavior and negative/ambiguous paths.
- provider artifacts are cited as evidence, not authority.
- `tasks.md` records no-op implementation completion with evidence.
- governance / doctor verification passes.
- existing code behavior satisfies the frozen package truth.

If any acceptance criterion cannot be proven from current code or evidence, `implement` is not no-op; the feature must either change code or return to truth/change for scope correction.

## Learning Influence Summary

## Route Decisions

## Version Evolution Notes

## Promotion Log
