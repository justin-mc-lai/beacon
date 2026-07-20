"""Contract tests for beacon-host-subagent-lifecycle-keyword-v168."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.host_subagent_gate import (
    MINIMAL_SIX_ROLES,
    REASON_DEFAULT_OFF,
    REASON_FLAG_OFF,
    REASON_NEGATED,
    detect_satellite_parallel_intent,
    evaluate_host_subagent_gate,
    score_overlay_dimensions,
)
from beacon.utils.host_subagent_pack import install_subagent_pack, verify_subagent_agents

ROOT = Path(__file__).resolve().parents[1]


def test_kw_001_default_off() -> None:
    g = evaluate_host_subagent_gate("实现并验收登录")
    assert g["spawn"] is False
    assert g["host_agents"] is False
    assert g["single_thread"] is True
    assert g["reason_code"] == REASON_DEFAULT_OFF


def test_kw_002_global_on_default_pack() -> None:
    g = evaluate_host_subagent_gate("启用子代理协助完成目标")
    assert g["gate_on"] is True
    assert g["spawn"] is True
    assert "pack-default" in g["packs"]
    assert g["roles"]


def test_kw_003_research_pack() -> None:
    g = evaluate_host_subagent_gate("用子代理做调研搜索竞品")
    assert g["host_agents"] is True
    assert "pack-research" in g["packs"]
    assert "search-specialist" in g["roles"]


def test_kw_004_review_pack() -> None:
    g = evaluate_host_subagent_gate("子代理全面审查该方案 oracle challenge")
    assert "pack-review" in g["packs"]


def test_kw_005_qa_pack() -> None:
    g = evaluate_host_subagent_gate("子代理并行验收 correctness reviewer")
    assert "pack-qa" in g["packs"]
    assert "qa-expert" in g["roles"] or "code-reviewer" in g["roles"]


def test_kw_006_implement_pack() -> None:
    g = evaluate_host_subagent_gate("子代理并行实现 worker")
    assert "pack-implement" in g["packs"]


def test_kw_007_negate_and_flag_off() -> None:
    g = evaluate_host_subagent_gate("启用子代理但不要子代理")
    assert g["spawn"] is False
    assert g["reason_code"] == REASON_NEGATED
    g2 = evaluate_host_subagent_gate("子代理调研", flag=False)
    assert g2["reason_code"] == REASON_FLAG_OFF
    assert g2["spawn"] is False


def test_kw_008_parallel_only_not_host() -> None:
    g = evaluate_host_subagent_gate("多湖并行实现两个 feature")
    assert g["host_agents"] is False
    assert g["reason_code"] == REASON_DEFAULT_OFF
    assert detect_satellite_parallel_intent("多湖并行实现两个 feature") is True


def test_st_001_single_thread() -> None:
    g = evaluate_host_subagent_gate("普通交付")
    assert g["single_thread"] is True
    assert g["roles"] == []


def test_bd_001_cannot_complete() -> None:
    g = evaluate_host_subagent_gate("子代理")
    assert g["cannot_complete_goal"] is True
    assert g["cannot_auto_release"] is True


def test_bd_002_public_entry_skill() -> None:
    skill = (ROOT / "skills/beacon/beacon-goal/SKILL.md").read_text(encoding="utf-8")
    assert "beacon-loop-goal" in skill
    assert "Host subagent keyword gate" in skill or "子代理" in skill


def test_in_001_install_pack(tmp_path: Path) -> None:
    r = install_subagent_pack(tmp_path, host_runtime="codex", pack="minimal")
    assert r["status"] == "ok"
    assert r["role_count"] == 6
    for role in MINIMAL_SIX_ROLES:
        assert (tmp_path / ".codex" / "agents" / f"{role}.toml").is_file()
    r2 = install_subagent_pack(tmp_path, host_runtime="claude", pack="minimal")
    assert r2["status"] == "ok"
    assert (tmp_path / ".claude" / "agents" / "search-specialist.md").is_file()


def test_vr_001_verify_require_agents(tmp_path: Path) -> None:
    bad = verify_subagent_agents(tmp_path, host_runtime="codex")
    assert bad["status"] == "fail"
    install_subagent_pack(tmp_path, host_runtime="codex")
    good = verify_subagent_agents(tmp_path, host_runtime="codex")
    assert good["status"] == "pass"


def test_ex_001_examples_exist() -> None:
    ex = ROOT / "skills/beacon/examples"
    assert (ex / "subagent-keyword-off-30s.md").is_file()
    assert (ex / "subagent-review-on-30s.md").is_file()
    assert (ex / "subagent-research-on-30s.md").is_file()


def test_lm_001_v2_mirror() -> None:
    t = ROOT / "docs/beacon/v2.0.0/features/loom-host-subagent-lifecycle-keyword-v200/truth.md"
    assert t.is_file()
    text = t.read_text(encoding="utf-8")
    assert "AC-SA-KW" in text or "parity" in text.lower() or "同 AC" in text


def test_sc_001_score_overlay() -> None:
    dims = score_overlay_dimensions()
    assert abs(sum(dims.values()) - 1.0) < 1e-9
    assert "subagent_keyword_precision" in dims


def test_flag_on() -> None:
    g = evaluate_host_subagent_gate("plain", flag=True)
    assert g["reason_code"] == "subagent_flag_on"
    assert g["spawn"] is True
