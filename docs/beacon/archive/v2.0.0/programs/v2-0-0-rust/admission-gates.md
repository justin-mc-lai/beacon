# v2.0.0 Rust Program Admission Gates

## Program Admission Bundle

Before implementation resumes, the bundle must include:

- `program-manifest.md`
- `phase-graph.md`
- `program-run-state.json`
- `admission-gates.md`
- latest frozen truth package refs
- canonical truth baseline commit
- workspace admission artifact with `BranchContext.v1`

## Hard Gates

| Gate | Block reason |
|---|---|
| Program surface missing | `program_surface_missing` |
| Phase graph missing or invalid | `program_phase_graph_missing` |
| R revision narrative drift | `revision_authority_drift` |
| Canonical refreeze not committed | `canonical_refreeze_not_committed` |
| Feature branch missing truth baseline | `truth_baseline_not_merged` |
| Workspace admission missing | `workspace_admission_missing` |
| Decision packet missing or stale | `decision_packet_missing` |
| BranchContext mismatch | `branch_context_mismatch` |
| TraceSpine missing or incomplete | `trace_spine_incomplete` |
| Design required but unbound | `design_primitives_missing` |

## Design Gate

`design_required` is conditional. UI, visual or interaction delivery must bind `design_primitives.v1` before implement admission. Non-UI kernel work may proceed without design primitives only when the decision packet marks `design_required=false`.

## Evidence Rule

Program admission is not QA or release. It only permits implement to start after canonical truth, branch governance and trace preconditions are present.
