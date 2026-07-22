"""v1.6.10: humanizer llm/rules, real exec TC, task AC evidence bind."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.feature_package import (
    evaluate_task_ac_evidence_bindings,
    parse_task_ac_evidence_binding,
    render_tasks_package,
    render_tests_package,
)
from beacon.utils.humanizer_config import apply_humanizer_l0, polish_l0_text
from beacon.utils.humanizer_llm import should_use_llm, vendor_humanizer_skills_into_beacon
from beacon.utils.truth_review_gate import _is_docs_only_command, evaluate_truth_review_gate


def test_rules_engine_expands_slop():
    out = polish_l0_text("这标志着 赋能 系统。此外，值得注意的是很好。\n", language="zh")
    assert "标志着" not in out
    assert "能做" in out


def test_should_use_llm_auto_without_key(monkeypatch):
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    monkeypatch.delenv("BEACON_HUMANIZER_LLM_MODE", raising=False)
    monkeypatch.delenv("BEACON_LLM_MODE", raising=False)
    assert should_use_llm({"llm_mode": "auto"}) is False
    monkeypatch.setenv("BEACON_LLM_API_KEY", "sk-test")
    assert should_use_llm({"llm_mode": "auto"}) is True
    assert should_use_llm({"llm_mode": "rules"}) is False


def test_apply_humanizer_records_rules_engine(monkeypatch):
    monkeypatch.delenv("BEACON_LLM_API_KEY", raising=False)
    md = """---
language: zh
---
## 人话

标志着 赋能

## Acceptance Criteria

| AC ID | Description |
|-------|-------------|
| AC-001 | x |
"""
    r = apply_humanizer_l0(md, profile={"language": "zh", "skill_text": "skill", "preserve_machine_fields": True, "config": {"llm_mode": "rules"}})
    assert r.get("applied")
    assert "rules" in (r.get("engines") or [])
    assert "Acceptance Criteria" in r["truth_md"]


def test_vendor_skill_into_beacon(tmp_path: Path):
    src = tmp_path / "oss/Humanizer-zh/SKILL.md"
    src.parent.mkdir(parents=True)
    src.write_text("# humanizer-zh\nfulltext\n", encoding="utf-8")
    # create fake project with skills path
    (tmp_path / "skills/beacon/references/truth-humanizer").mkdir(parents=True)
    out = vendor_humanizer_skills_into_beacon(tmp_path, zh_source=src, en_source=None)
    assert out["written"]
    vendored = tmp_path / "skills/beacon/references/truth-humanizer/vendor/Humanizer-zh/SKILL.md"
    assert vendored.is_file()
    assert "fulltext" in vendored.read_text(encoding="utf-8")


def test_weak_print_not_exec_layer():
    assert _is_docs_only_command("python3 -c 'print(0)'") is True
    assert _is_docs_only_command("python3 -m pytest -q tests/ -k x --tb=no") is False
    assert _is_docs_only_command("python3 -m beacon doctor --help") is False


def test_domain_requires_real_exec_not_print():
    truth = """---
domain_required: true
package_maturity: filled
---
# T
## 人话
支付
- 能做：付
- 不能做：跳
- 怎样算完：paid
## Intent Coverage Matrix
| intent_id | source | strength | landing | status |
|-----------|--------|----------|---------|--------|
| INT-01 | prompt | must | AC-001 | covered |
## 用户旅程
1. pay
## Acceptance Criteria
| AC ID | Description |
|-------|-------------|
| AC-001 | pay
## FSM 五元组
| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| created | pay | ok | paid | x |
### invalid / illegal
- paid→created
"""
    weak = """| TC ID | AC ID | Command | Assertion |
|-------|-------|---------|-----------|
| TC-001 | AC-001 | `rg -n pay t.md` | y |
| TC-E | AC-001 | `python3 -c 'print(0)'` | exit 0 |
"""
    r = evaluate_truth_review_gate(truth_md=truth, tests_md=weak, version="v1.6.10", feature="pay")
    assert r["pass"] is False
    assert any(f.get("kind") == "domain_exec_tc_missing" for f in r.get("findings") or [])

    strong = weak.replace("`python3 -c 'print(0)'`", "`python3 -m pytest -q tests/ --tb=no`")
    r2 = evaluate_truth_review_gate(truth_md=truth, tests_md=strong, version="v1.6.10", feature="pay")
    assert r2["pass"] is True


def test_render_tests_uses_pytest_not_print0(tmp_path: Path):
    tests = render_tests_package(tmp_path, version="v1.6.10", feature="demo")
    assert "pytest" in tests
    assert "print(0)" not in tests
    assert "TC-EXEC-PYTEST" in tests or "TC-EXEC-CLI" in tests


def test_tasks_bind_ac_and_evidence(tmp_path: Path):
    d = tmp_path / "docs/beacon/v1.6.10/features/pay"
    d.mkdir(parents=True)
    (d / "truth.md").write_text(
        """---
slug: pay
---
## Acceptance Criteria
| AC ID | Description |
|-------|-------------|
| AC-001 | pay ok
""",
        encoding="utf-8",
    )
    tasks = render_tasks_package(tmp_path, version="v1.6.10", feature="pay")
    assert "task_source: acceptance_criteria" in tasks
    assert "ac=AC-001" in tasks
    assert "evidence=`" in tasks
    assert ".beacon/evidence/implement/pay/AC-001.json" in tasks
    bind = parse_task_ac_evidence_binding(
        "Implement AC-001: pay ok · ac=AC-001 · evidence=`.beacon/evidence/implement/pay/AC-001.json`"
    )
    assert bind["ac_id"] == "AC-001"
    assert bind["evidence_path"].endswith("AC-001.json")

    # checked without file → fail
    checked = tasks.replace("- [ ] TASK-001", "- [x] TASK-001", 1)
    gate = evaluate_task_ac_evidence_bindings(tmp_path, tasks_md=checked, version="v1.6.10")
    assert gate["pass"] is False
    assert gate["checked_bad"] >= 1

    # write evidence → pass
    ev = tmp_path / ".beacon/evidence/implement/pay/AC-001.json"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(json.dumps({"ac_id": "AC-001", "status": "pass"}), encoding="utf-8")
    # still other unchecked tasks with bindings - only checked need files
    gate2 = evaluate_task_ac_evidence_bindings(tmp_path, tasks_md=checked, version="v1.6.10")
    assert gate2["checked_bad"] == 0
    assert gate2["pass"] is True
