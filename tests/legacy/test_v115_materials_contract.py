from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v115_summary_should_mark_implemented_release_ready_explicitly():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "SUMMARY.md").read_text(encoding="utf-8")
    assert "Implemented and Release-Ready" in text
    assert "implemented, release-ready" in text


def test_v115_execution_index_should_separate_human_and_machine_surfaces():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "execution" / "index.md").read_text(encoding="utf-8")
    assert "Human Primary Surface" in text
    assert "Machine Secondary Surface" in text
    assert "docs/beacon/v1.1.5/.machine/execution/" in text


def test_v115_release_should_limit_eval_lab_to_minimum_skeleton():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "release" / "v1.1.5.md").read_text(encoding="utf-8")
    assert "eval-lab" in text
    assert "最小骨架" in text


def test_v115_human_machine_prd_should_not_be_compatibility_first():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "prd" / "beacon-human-machine-artifact-layering.md").read_text(encoding="utf-8")
    assert "不做长期兼容方案" in text
    assert "execution/index.md" in text
    assert "qa/test-cases/index.md" in text


def test_v115_prompt_prd_should_define_progressive_disclosure_and_clarification_gate():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "prd" / "beacon-llm-skill-prompt-first-principles.md").read_text(encoding="utf-8")
    assert "渐进式披露" in text
    assert "澄清门" in text or "目标、动机、边界不清晰" in text
    assert "doctor" in text


def test_v115_eval_lab_prd_should_define_fixed_benchmark_and_keep_discard():
    text = (ROOT / "docs" / "beacon" / "v1.1.5" / "prd" / "beacon-autoresearch-eval-lab.md").read_text(encoding="utf-8")
    assert "固定 benchmark 面" in text
    assert "keep/discard" in text
    assert "整个 Beacon 业务代码树" in text


def test_v115_machine_execution_terminal_should_exist():
    terminal = ROOT / "docs" / "beacon" / "v1.1.5" / ".machine" / "execution" / "terminal.json"
    assert terminal.exists()
    text = terminal.read_text(encoding="utf-8")
    assert '"status": "Pass"' in text
    assert '"version": "v1.1.5"' in text
