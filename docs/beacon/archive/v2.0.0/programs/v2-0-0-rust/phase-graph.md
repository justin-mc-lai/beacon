# v2.0.0 Rust Program Phase Graph

## State Model

`state_machine_required`: true

```text
program_intent_captured
  -> canonical_truth_materialized
  -> canonical_refreeze_complete
  -> canonical_commit_ready
  -> feature_worktree_reconciled
  -> governance_verified
  -> workspace_admitted
  -> P0_running
  -> P1_running
  -> P2_running
  -> P3_running
  -> P4_running
  -> P6_running
  -> qa_evidence_ready
  -> release_candidate
```

## Lake Slices

| Slice | Phase | Required closure |
|---|---|---|
| Program admission | P0 entry | manifest, phase graph, run-state, admission gates, canonical truth baseline |
| Core/store kernel | P0 | five Rust core crates, no Python core crate, storage authority skeleton |
| Spine/projects | P1 | global DB read model, projects registry, JSON schema |
| Orchestrator/trace | P2 | decision packet, BranchContext, TraceSpine, Codex/Subprocess integration, standard flow admission |
| Gate/migration/agent parity | P3 | TIG, migration, Claude/ACP/ImplementHarness, remediation, QA evidence chain |
| Harness surface | P4 | exactly six public abilities, progressive disclosure, legacy removal |
| Benchmark/release closure | P6 | performance gates, E2E, QA evidence and release scorecard |

## Allowed Transitions

- P0 may start only after canonical truth and program admission pass.
- P1 may start only after P0 evidence is bound to AC/TC.
- P2 may start only after P1 spine/projects evidence is available.
- P3 may start only after P2 produces decision packet, BranchContext and TraceSpine behavior evidence.
- P4 may start only after P2/P3 harness boundary reason codes are available.
- P6 may start only after P0-P4 phase exits are not blocked.

## Invalid Transitions

- `program_intent_captured -> implement_resume` without canonical refreeze and commit.
- Any feature/dev worktree requirement revision bump.
- Any loop start without current `decision_packet.v1`.
- Any implement/qa-evidence/release action without TraceSpine completeness.
- Any release pass without human confirmation.

## Recovery And Resume

- Re-running an already completed standard-flow step returns `up_to_date` or `pass`.
- Stale feature-local refreeze/projection must be quarantined before merging canonical truth.
- Reason-only or machine-only refreeze is invalid and must be repaired through content-bearing canonical truth authoring.
