"""Contract tests for beacon-plan-host-subagent-voltpack-v1610."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.host_subagent_gate import (
    PLAN_REVIEW_CORE_ROLES,
    PLAN_REVIEW_TEN_ROLES,
    evaluate_host_subagent_gate,
)
from beacon.utils.host_subagent_pack import install_subagent_pack, verify_subagent_agents
from beacon.utils.planner_review_runtime import build_planner_review_runtime_artifact
from beacon.utils.subagent_readiness import runtime_readiness_precheck

ROOT = Path(__file__).resolve().parents[1]


def test_keyword_off_default():
    g = evaluate_host_subagent_gate("实现用户登录并验收")
    assert g["spawn"] is False
    assert g["reason_code"] == "subagent_default_off"


def test_architecture_code_review_hits_pack_review():
    g = evaluate_host_subagent_gate("启用子代理做架构设计与代码审查全面分析")
    assert g["spawn"] is True
    assert "pack-review" in g["packs"]
    assert "architect-reviewer" in g["roles"]
    assert "code-reviewer" in g["roles"]
    assert set(PLAN_REVIEW_CORE_ROLES) <= set(g["roles"])


def test_parallel_alone_does_not_open_host_agents():
    g = evaluate_host_subagent_gate("并行实现多湖")
    assert g["host_agents"] is False
    assert g["spawn"] is False


def test_negate_wins():
    g = evaluate_host_subagent_gate("不要子代理 但启用子代理 全面审查")
    assert g["spawn"] is False


def test_global_on_without_stage_is_default_pack():
    g = evaluate_host_subagent_gate("启用子代理")
    assert g["packs"] == ["pack-default"]
    assert g["roles"] == ["search-specialist"]


def test_cannot_complete_goal_bound():
    g = evaluate_host_subagent_gate("启用子代理 全面审查")
    assert g["cannot_complete_goal"] is True


def test_plan_review_install_writes_ten_roles(tmp_path: Path):
    result = install_subagent_pack(tmp_path, host_runtime="codex", pack="plan-review")
    assert result["status"] == "ok"
    assert result["role_count"] == 10
    assert set(result["roles"]) == set(PLAN_REVIEW_TEN_ROLES)
    agents = tmp_path / ".codex" / "agents"
    for role in PLAN_REVIEW_TEN_ROLES:
        path = agents / f"{role}.toml"
        assert path.is_file()
        body = path.read_text(encoding="utf-8")
        assert "cannot_complete_goal" in body
        assert "cannot_write_truth" in body or "cannot_write_truth=true" in body


def test_hard_constraints_in_installed_files(tmp_path: Path):
    install_subagent_pack(tmp_path, host_runtime="codex", pack="plan-review")
    for role in PLAN_REVIEW_TEN_ROLES:
        body = (tmp_path / ".codex" / "agents" / f"{role}.toml").read_text(encoding="utf-8")
        assert "cannot_complete_goal" in body
        assert "cannot_write_truth" in body or "cannot_write_truth=true" in body


def test_minimal_pack_still_six(tmp_path: Path):
    result = install_subagent_pack(tmp_path, host_runtime="codex", pack="minimal")
    assert result["status"] == "ok"
    assert result["role_count"] == 6
    verify = verify_subagent_agents(tmp_path, host_runtime="codex", require_pack=True)
    assert verify["status"] == "pass"


def test_readiness_flat_skill_root_present():
    pre = runtime_readiness_precheck(ROOT, host_runtime="codex")
    # On this machine flat beacon-goal should satisfy skill_root
    skill_check = next(c for c in pre["checks"] if c["name"] == "skill_root_present")
    assert skill_check["ok"] is True, skill_check
    assert pre["status"] in {"pass", "blocked"}  # may still block on other items
    if pre["status"] == "blocked":
        assert "skill_root_present" not in pre.get("blocked_checks", [])


def test_planner_fallback_honest():
    payload = build_planner_review_runtime_artifact(
        project_root=ROOT,
        feature="beacon-plan-host-subagent-voltpack-v1610",
        version="v1.6.10",
        prompt="t",
        subagent_runtime_available=False,
        write=False,
    )
    assert payload["execution_mode"] == "single_process_multi_reviewer"
    assert payload["fallback_reason"]


def test_example_exists():
    path = ROOT / "skills/beacon/examples/subagent-plan-review-architecture-on-30s.md"
    assert path.is_file()


def test_truth_defers_full_dump():
    truth = (ROOT / "docs/beacon/v1.6.10/features/beacon-plan-host-subagent-voltpack-v1610/truth.md").read_text(
        encoding="utf-8"
    )
    assert "全量 VoltAgent" in truth
    assert "Non-goals" in truth or "non-goal" in truth.lower()


def test_plan_review_roles_count():
    assert len(PLAN_REVIEW_TEN_ROLES) == 10
    assert len(PLAN_REVIEW_CORE_ROLES) == 4
