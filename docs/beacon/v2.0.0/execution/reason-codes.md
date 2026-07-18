# Beacon v2 reason codes (kernel)

| Code | Domain |
|------|--------|
| `trace_spine_missing` | TraceSpine hard gate |
| `trace_hash_chain_invalid` | TraceSpine |
| `trace_event_to_evidence_break` | TraceSpine |
| `trace_context_binding_incomplete` | TraceSpine AC-132 |
| `branch_context_missing` | BranchContext |
| `workspace_admission_missing` | Workspace |
| `truth_canonical_branch_mismatch` | Canonical truth branch |
| `branch_context_protected_path_write` | Branch governance |
| `standard_flow_order_violation` | Standard flow |
| `standard_flow_verification_incomplete` | Admission bundle |
| `canonical_refreeze_not_committed` | Baseline commit |
| `stale_feature_local_refreeze` | Feature quarantine |
| `truth_baseline_not_merged` | Feature admission |
| `dual_track_mixed_source` | Dual-track |
| `cross_track_fallback_forbidden` | Dual-track |
| `early_default_beacon_v2_forbidden` | W4 |
| `empty_refreeze_reason_only` | Refreeze AC-137 |
| `empty_refreeze_machine_only` | Refreeze |
| `revision_authority_drift` | Refreeze |
| `decision_packet_missing` | Loop admission |
| `intent_low_confidence_freeze_block` | Intent |
| `harness_boundary_violation` | Harness AC-130 |
| `stagnation_requires_trace_run_id` | Stagnation |
| `stagnation_repeat_failure` | Stagnation |
| `auto_release_confirmed_forbidden` | Release human gate |
| `gitscope_branch_context_parity_failed` | Git probe |
