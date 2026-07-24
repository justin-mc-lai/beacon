---
slug: workspace-clean-exit-gate-v1610
version: v1.6.10
revision_id: R1
materials_status: current
---

# Tests: workspace-clean-exit-gate-v1610

| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-WC-001 | AC-WC-001 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_verify_clean_workspace_classifies_full_git_status` | full porcelain status is classified and unclassified dirty blocks |
| TC-WC-002 | AC-WC-002 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_dirty_manifest_roles_cover_required_classes` | manifest exposes canonical_truth/formal_evidence/machine_projection/host_projection/runtime_private/forbidden |
| TC-WC-003 | AC-WC-003 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_formal_manifest_rejects_untracked_runtime_refs` | runtime hook evidence cannot satisfy formal release evidence |
| TC-WC-004 | AC-WC-004 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_task_evidence_promotion_gate` | checked task requires tracked evidence; unchecked existing evidence reports orphan_evidence_unpromoted |
| TC-WC-005 | AC-WC-005 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_agent_trace_redline_blocks_raw_chat_and_secrets` | forbidden trace fields return agent_trace_redline_field and no file is written |
| TC-WC-006 | AC-WC-006 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_trace_digest_is_release_safe_and_raw_trace_private` | raw trace is runtime_private; digest has redaction_status=pass and sha256 |
| TC-WC-007 | AC-WC-007 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_post_release_local_install_does_not_dirty_original_root` | pre/post root snapshots match except ignored runtime state |
| TC-WC-008 | AC-WC-008 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_quiet_worktree_hidden_dirty_is_not_release_proof` | strict gate reports skip_worktree_hidden_dirty |
| TC-WC-017 | AC-WC-008 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_illegal_skip_worktree_transition_blocks_clean_proof` | illegal transition skip-worktree-hidden dirty → clean proof is blocked |
| TC-WC-009 | AC-WC-009 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_host_projection_requires_policy_or_surface_sync_commit` | host projection dirty blocks unless local-only or deterministic sync commit policy is satisfied |
| TC-WC-010 | AC-WC-010 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_lifecycle_exits_attach_clean_gate_bundle` | truth/freeze/qa/release/post-release profiles emit same clean gate schema |
| TC-WC-011 | AC-WC-011 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_main_push_profile_blocks_generator_dirty` | main-push blocks generator and unclassified dirty beyond staged business code |
| TC-WC-012 | AC-WC-012 | `pytest -q tests/test_v1610_workspace_clean_exit_gate.py::test_clean_workspace_does_not_authorize_release` | clean pass leaves release human confirmation required |
| TC-WC-013 | AC-WC-001..012 | `python3 -m pytest -q tests/test_v1610_workspace_clean_exit_gate.py` | exec suite covers clean-workspace exit gate |
| TC-WC-014 | AC-WC-005, AC-WC-006 | `rg -n "full_chat|agent_trace_redline_field|redaction_status" beacon/utils/agent_trace.py beacon/utils/workspace_clean.py` | trace redline and digest contract present |
| TC-WC-015 | AC-WC-007, AC-WC-010 | `rg -n "verify_clean_workspace|snapshot" beacon/utils/project_hooks.py beacon/commands/release.py beacon/commands/qa.py beacon/commands/truth.py` | lifecycle commands integrate clean gate |
| TC-WC-016 | AC-WC-002, AC-WC-003 | `rg -n "workspace-clean-manifest|formal_evidence|runtime_private" docs/beacon/governance/workspace-clean-manifest.md beacon/utils/workspace_clean.py` | dirty manifest policy is codified |

## Coverage Notes

- TC-WC-013 is the required execution-layer suite for this governance domain.
- Contract greps are secondary checks; they cannot replace the pytest suite.
- Release remains human-gated even when TC-WC-012 passes.
