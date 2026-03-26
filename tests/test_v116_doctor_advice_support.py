from __future__ import annotations

from pathlib import Path

from beacon.utils.doctor_diagnostics import build_doctor_advice_payload
from beacon.utils.revision_state import freeze_revision_state


FEATURE = "Doctor Advice Feature"
SLUG = "doctor-advice-feature"
VERSION = "v1.1.6"


def _seed_docs(root: Path) -> None:
    us = root / "docs" / "beacon" / VERSION / "user-story"
    us.mkdir(parents=True, exist_ok=True)
    (us / f"{SLUG}.md").write_text(
        """# User Story\n\n| AC ID | Theme | Description |\n| --- | --- | --- |\n| AC-001 | Lifecycle | Freeze before implement |\n""",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / "prd").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / VERSION / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)


def test_doctor_advice_should_merge_diagnostics_with_next_step(tmp_path: Path):
    _seed_docs(tmp_path)
    payload = build_doctor_advice_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["feature"] == FEATURE
    assert payload["next_step"]["action"] == "freeze"
    assert payload["blocked"] is True
    assert payload["scores"]["readiness_score"] == 0 or payload["scores"]["readiness_score"] < 70

    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    payload = build_doctor_advice_payload(tmp_path, version=VERSION, feature=FEATURE)
    assert payload["next_step"]["action"] == "implement"
    assert "diagnostics" in payload
