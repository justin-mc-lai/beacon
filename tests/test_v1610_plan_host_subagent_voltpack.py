"""Contract tests for beacon-plan-host-subagent-voltpack-v1610."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from beacon.utils.host_subagent_gate import (
    DEFAULT_SPAWN_MAX,
    PLAN_REVIEW_CORE_ROLES,
    PLAN_REVIEW_TEN_ROLES,
    evaluate_host_subagent_gate,
    parse_subagent_count,
)
from beacon.utils.host_subagent_pack import install_subagent_pack, verify_subagent_agents
from beacon.utils.planner_review_runtime import build_planner_review_runtime_artifact
from beacon.utils.subagent_readiness import runtime_readiness_precheck

ROOT = Path(__file__).resolve().parents[1]


def test_keyword_off_default():
    g = evaluate_host_subagent_gate("实现用户登录并验收")
    assert g["spawn"] is False
    assert g["reason_code"] == "subagent_default_off"
    assert g["spawn_count"] == 0


def test_architecture_code_review_hits_pack_review():
    g = evaluate_host_subagent_gate("启用子代理做架构设计与代码审查全面分析")
    assert g["spawn"] is True
    assert "pack-review" in g["packs"]
    assert g["spawn_count"] == DEFAULT_SPAWN_MAX == 3
    assert g["roles"] == list(PLAN_REVIEW_CORE_ROLES)
    assert set(PLAN_REVIEW_CORE_ROLES) <= set(g["roles"])
    assert "architect-reviewer" in g["roles"]
    assert "code-reviewer" in g["roles"]
    assert "knowledge-synthesizer" in g["roles"]
    assert len(g["roles_catalog"]) == 10
    assert set(g["roles_catalog"]) == set(PLAN_REVIEW_TEN_ROLES)


def test_spawn_count_from_utterance_five():
    g = evaluate_host_subagent_gate("启用子代理做架构审查 开5个子代理")
    assert g["spawn"] is True
    assert g["spawn_count"] == 5
    assert g["spawn_count_source"] == "utterance"
    assert len(g["roles"]) == 5
    assert g["roles"][:3] == list(PLAN_REVIEW_CORE_ROLES)


def test_spawn_count_param_overrides_default():
    g = evaluate_host_subagent_gate(
        "启用子代理做架构设计与代码审查全面分析",
        subagent_count=2,
    )
    assert g["spawn_count"] == 2
    assert g["spawn_count_source"] == "param"
    assert g["roles"] == list(PLAN_REVIEW_CORE_ROLES[:2])


def test_spawn_count_clamps_above_catalog():
    g = evaluate_host_subagent_gate("启用子代理 全面审查", subagent_count=99)
    assert g["spawn_count"] == 10
    assert "clamped_max" in g["spawn_count_source"]
    assert len(g["roles"]) == 10


def test_spawn_count_env_cap(monkeypatch):
    monkeypatch.setenv("BEACON_SUBAGENT_MAX", "2")
    g = evaluate_host_subagent_gate("启用子代理 全面审查 开5个子代理")
    assert g["spawn_count"] == 2
    assert g["spawn_count_env_cap"] == 2


def test_parse_subagent_count_patterns():
    assert parse_subagent_count("subagent-count=7") == 7
    assert parse_subagent_count("开3个子代理") == 3
    assert parse_subagent_count("启动 4 个子代理") == 4
    assert parse_subagent_count("plain") is None


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
    assert g["spawn_count"] == 1  # catalog size 1, not forced to 3


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
        assert "\nmodel =" not in f"\n{body}"
        assert "\nmodel_reasoning_effort =" not in f"\n{body}"

    manifest = json.loads((agents / "beacon-pack-manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_policy"] == "inherit_parent"


def test_hard_constraints_in_installed_files(tmp_path: Path):
    install_subagent_pack(tmp_path, host_runtime="codex", pack="plan-review")
    for role in PLAN_REVIEW_TEN_ROLES:
        body = (tmp_path / ".codex" / "agents" / f"{role}.toml").read_text(encoding="utf-8")
        assert "cannot_complete_goal" in body
        assert "cannot_write_truth" in body or "cannot_write_truth=true" in body


def test_codex_pack_inherits_parent_model(tmp_path: Path):
    install_subagent_pack(tmp_path, host_runtime="codex", pack="plan-review")
    for role in PLAN_REVIEW_TEN_ROLES:
        body = (tmp_path / ".codex" / "agents" / f"{role}.toml").read_text(encoding="utf-8")
        assert not any(
            line.strip().startswith(("model =", "model_reasoning_effort ="))
            for line in body.splitlines()
        )


def test_minimal_pack_still_six(tmp_path: Path):
    result = install_subagent_pack(tmp_path, host_runtime="codex", pack="minimal")
    assert result["status"] == "ok"
    assert result["role_count"] == 6
    verify = verify_subagent_agents(tmp_path, host_runtime="codex", require_pack=True)
    assert verify["status"] == "pass"


def test_readiness_flat_skill_root_present():
    pre = runtime_readiness_precheck(ROOT, host_runtime="codex")
    skill_check = next(c for c in pre["checks"] if c["name"] == "skill_root_present")
    assert skill_check["ok"] is True, skill_check
    assert pre["status"] in {"pass", "blocked"}
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
    assert len(PLAN_REVIEW_CORE_ROLES) == 3
    assert DEFAULT_SPAWN_MAX == 3
