"""Tests for governance truth-canonical schema (F2 R1, AC-001..006).

global-boundaries §4.2 truth-on-main: governance contract must express
truth_canonical (main) / runtime_mirror (beacon/v<x>) so that git-alignment
accepts main as the truth canonical branch and does not block truth-plane work.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from beacon.utils.git_alignment import collect_git_alignment
from beacon.utils.project_governance import (
    _assign_version_kv,
    commit_governance_payload,
    parse_governance_markdown,
    render_governance_markdown,
)


# ---- AC-001: schema-parse — _assign_version_kv recognizes new fields ----

def test_assign_version_kv_recognizes_new_fields() -> None:
    """_assign_version_kv persists truth_canonical/runtime_mirror, not silently dropped."""
    contract: dict = {}
    _assign_version_kv(contract, "truth_canonical", "main")
    _assign_version_kv(contract, "runtime_mirror", "beacon/v1.6.3")
    assert contract["truth_canonical"] == "main"
    assert contract["runtime_mirror"] == "beacon/v1.6.3"


def test_parse_version_contracts_reads_dual_fields(tmp_path: Path) -> None:
    """_parse_version_contracts parses truth_canonical/runtime_mirror from governance MD."""
    md = (
        "---\n"
        "schema_version: \"1.0\"\n"
        "project_root: \"/tmp/x\"\n"
        "topology_kind: \"single_repo\"\n"
        "default_execution_service: \"beacon\"\n"
        "transaction_id: \"tx-x\"\n"
        "committed_at: \"\"\n"
        "source_hash: \"\"\n"
        "event_type: \"update\"\n"
        "parser_contract: \"beacon-project-governance-v1\"\n"
        "---\n\n"
        "# Project Version Governance\n\n"
        "## Version Contracts\n\n"
        "### v1.6.3\n"
        "- participating_services: `beacon`\n"
        "- branch_guard_mode: `strict`\n"
        "- validation_state: `active`\n"
        "- per_service_canonical_branch:\n"
        "  - `beacon`: `beacon/v1.6.3`\n"
        "- truth_canonical: `main`\n"
        "- runtime_mirror: `beacon/v1.6.3`\n"
    )
    payload = parse_governance_markdown(md, project_root=tmp_path)
    contract = payload["version_scoped_metadata"]["v1.6.3"]
    assert contract["truth_canonical"] == "main"
    assert contract["runtime_mirror"] == "beacon/v1.6.3"


# ---- AC-002: schema-render — render + commit roundtrip ----

def test_render_and_commit_roundtrip(tmp_path: Path) -> None:
    """render_governance_markdown writes dual fields; commit_governance_payload roundtrips."""
    payload = parse_governance_markdown(
        "---\n"
        "schema_version: \"1.0\"\n"
        "project_root: \"" + str(tmp_path) + "\"\n"
        "topology_kind: \"single_repo\"\n"
        "default_execution_service: \"beacon\"\n"
        "transaction_id: \"\"\n"
        "committed_at: \"\"\n"
        "source_hash: \"\"\n"
        "event_type: \"update\"\n"
        "parser_contract: \"beacon-project-governance-v1\"\n"
        "---\n\n"
        "# Project Version Governance\n\n"
        "## Version Contracts\n\n"
        "### v1.6.3\n"
        "- participating_services: `beacon`\n"
        "- branch_guard_mode: `strict`\n"
        "- validation_state: `active`\n"
        "- per_service_canonical_branch:\n"
        "  - `beacon`: `beacon/v1.6.3`\n"
        "- truth_canonical: `main`\n"
        "- runtime_mirror: `beacon/v1.6.3`\n",
        project_root=tmp_path,
    )
    rendered = render_governance_markdown(payload)
    assert "- truth_canonical: `main`" in rendered
    assert "- runtime_mirror: `beacon/v1.6.3`" in rendered
    # commit roundtrips: re-parse the rendered MD and recover the fields + transaction
    result = commit_governance_payload(tmp_path, payload, event_type="update")
    assert result["transaction_id"].startswith("tx-project-governance-")
    assert result["source_hash"]
    reparsed = parse_governance_markdown(
        (tmp_path / "docs" / "beacon" / "governance" / "project-version-governance.md").read_text(encoding="utf-8")
        if (tmp_path / "docs" / "beacon" / "governance" / "project-version-governance.md").exists()
        else rendered,
        project_root=tmp_path,
    )
    rc = reparsed["version_scoped_metadata"]["v1.6.3"]
    assert rc["truth_canonical"] == "main"
    assert rc["runtime_mirror"] == "beacon/v1.6.3"


# ---- AC-003: resolver-truth-canonical — accepts main ----

def test_resolver_accepts_main_as_truth_canonical(tmp_path: Path) -> None:
    """collect_git_alignment with truth_canonical=main accepts current_branch=main."""
    with patch("beacon.utils.git_alignment.git_output", side_effect=_git_stub_current_main), \
         patch("beacon.utils.git_alignment.git_repo_exists", return_value=True):
        result = collect_git_alignment(
            tmp_path, "v1.6.3", allow_tag=True, require_exact_branch=False, truth_canonical="main"
        )
    assert result["on_truth_canonical"] is True
    assert "git_branch_target_mismatch" not in result["reason_codes"]
    assert "git_branch_prefix_mismatch" not in result["reason_codes"]
    assert result["version_ref_satisfied"] is True
    assert result["blocked"] is False


# ---- AC-004: backward-compat — legacy contract behavior unchanged ----

def test_backward_compat_legacy_contract(tmp_path: Path) -> None:
    """Without truth_canonical, resolver behavior is unchanged (legacy per_service_canonical_branch)."""
    with patch("beacon.utils.git_alignment.git_output", side_effect=_git_stub_current_main), \
         patch("beacon.utils.git_alignment.git_repo_exists", return_value=True):
        # legacy: no truth_canonical → main is NOT accepted, mismatch reported (baseline behavior)
        legacy = collect_git_alignment(
            tmp_path, "v1.6.3", allow_tag=True, require_exact_branch=False, truth_canonical=""
        )
    assert legacy["on_truth_canonical"] is False
    assert "git_branch_target_mismatch" in legacy["reason_codes"]
    assert "git_branch_prefix_mismatch" in legacy["reason_codes"]
    # and on the canonical branch itself (beacon/v1.6.3) legacy still passes
    with patch("beacon.utils.git_alignment.git_output", side_effect=_git_stub_current_v163), \
         patch("beacon.utils.git_alignment.git_repo_exists", return_value=True):
        canonical = collect_git_alignment(
            tmp_path, "v1.6.3", allow_tag=True, require_exact_branch=False, truth_canonical=""
        )
    assert canonical["blocked"] is False
    assert "git_branch_target_mismatch" not in canonical["reason_codes"]


# ---- AC-005: git-alignment-unblock — v1.6.3 contract unblocked ----

def test_git_alignment_unblocked_v163(tmp_path: Path) -> None:
    """v1.6.3 contract with truth_canonical=main → git-alignment not blocked on main."""
    with patch("beacon.utils.git_alignment.git_output", side_effect=_git_stub_current_main), \
         patch("beacon.utils.git_alignment.git_repo_exists", return_value=True):
        result = collect_git_alignment(
            tmp_path, "v1.6.3", allow_tag=True, require_exact_branch=False, truth_canonical="main"
        )
    assert result["blocked"] is False
    for rc in ("git_branch_target_mismatch", "git_branch_prefix_mismatch", "git_version_ref_not_satisfied"):
        assert rc not in result["reason_codes"], f"unexpected {rc}"


# ---- AC-006: no-flow-break — workspace admit / branch-governance flow intact ----

def test_no_worktree_admission_flow_break(tmp_path: Path) -> None:
    """Dual-field contract does not break collect_git_alignment determinism / shape."""
    with patch("beacon.utils.git_alignment.git_output", side_effect=_git_stub_current_v163), \
         patch("beacon.utils.git_alignment.git_repo_exists", return_value=True):
        result = collect_git_alignment(
            tmp_path, "v1.6.3", allow_tag=True, require_exact_branch=False, truth_canonical="main"
        )
    # on beacon/v1.6.3 with truth_canonical declared, still passes (canonical branch is valid)
    assert result["blocked"] is False
    # shape preserved — all expected keys present
    for key in ("base_branch", "target_branch", "current_branch", "reason_codes", "blocked", "on_truth_canonical"):
        assert key in result


# ---- git stubs ----

def _git_stub_current_main(project_root, *args, **kw):  # noqa: ANN001
    if "rev-parse" in args and "--abbrev-ref" in args:
        return "main"
    if "rev-parse" in args:
        return "deadbeef"
    if "remote" in args:
        return "https://github.com/x/y.git"
    if "describe" in args:
        return ""
    return ""


def _git_stub_current_v163(project_root, *args, **kw):  # noqa: ANN001
    if "rev-parse" in args and "--abbrev-ref" in args:
        return "beacon/v1.6.3"
    if "rev-parse" in args:
        return "deadbeef"
    if "remote" in args:
        return "https://github.com/x/y.git"
    if "describe" in args:
        return ""
    return ""
