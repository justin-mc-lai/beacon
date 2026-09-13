"""Regression for issue #25: name the expected evidence filename on width mismatch.

The AC evidence filename contract is ``AC-<index:03d>.json``. A 4-digit sibling
(``AC-0018.json``) used to be reported only as "evidence missing".
"""

from __future__ import annotations

from pathlib import Path

from beacon.utils.feature_package import evaluate_task_ac_evidence_bindings


def _tasks(task_body: str) -> str:
    return task_body


def test_width_mismatch_names_expected_and_found(tmp_path: Path) -> None:
    ev_dir = tmp_path / ".beacon" / "evidence" / "implement" / "demo"
    ev_dir.mkdir(parents=True)
    (ev_dir / "AC-0018.json").write_text('{"ok": true}', encoding="utf-8")
    tasks_md = (
        "- [x] TASK-001 Implement · ac=AC-018 · "
        "evidence=`.beacon/evidence/implement/demo/AC-018.json`\n"
    )

    result = evaluate_task_ac_evidence_bindings(tmp_path, tasks_md=tasks_md, version="v1.6.17")

    assert result["pass"] is False
    text = "\n".join(str(item.get("text") or "") for item in result["findings"])
    assert "AC-018.json" in text
    assert "AC-0018.json" in text
    assert "width mismatch" in text


def test_truly_missing_still_reports_missing(tmp_path: Path) -> None:
    tasks_md = (
        "- [x] TASK-001 Implement · ac=AC-018 · "
        "evidence=`.beacon/evidence/implement/demo/AC-018.json`\n"
    )

    result = evaluate_task_ac_evidence_bindings(tmp_path, tasks_md=tasks_md, version="v1.6.17")

    assert result["pass"] is False
    text = "\n".join(str(item.get("text") or "") for item in result["findings"])
    assert "evidence missing" in text
    assert "width mismatch" not in text
