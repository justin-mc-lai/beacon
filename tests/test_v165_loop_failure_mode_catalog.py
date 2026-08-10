from __future__ import annotations

from pathlib import Path

from beacon.utils.loop_failure_catalog import validate_failure_catalog
from beacon.utils.loop_readiness import build_loop_readiness_audit


ARCHIVE_CATALOG = Path(__file__).resolve().parents[1] / "docs/beacon/archive/v1.6.5/execution/loop-failure-modes.md"


def test_catalog_file_has_severity_sections() -> None:
    text = ARCHIVE_CATALOG.read_text(encoding="utf-8")
    assert "## S1 Annoying" in text
    assert "## S2 Harmful" in text
    assert "## S3 Critical" in text


def test_catalog_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "catalog.md"
    path.write_text("### x\n\n- id: x\n- severity: S1\n", encoding="utf-8")
    result = validate_failure_catalog(path)
    assert result["status"] == "fail"
    assert any(f["reason_code"] == "loop_failure_mode_required_field_missing" for f in result["findings"])


def test_catalog_contains_baseline_modes() -> None:
    result = validate_failure_catalog(ARCHIVE_CATALOG)
    assert result["status"] == "pass"
    assert {"truth-drift", "git-alignment-blocked", "stale-evidence-manifest", "infinite-fix-loop", "protected-path-attempt"}.issubset(set(result["mode_ids"]))


def test_invalid_severity_fails(tmp_path: Path) -> None:
    path = tmp_path / "catalog.md"
    path.write_text(
        """
### truth-drift

- id: truth-drift
- severity: S9
- symptom: x
- cause: x
- mitigation: x
- route: x
- evidence_expectation: x
""",
        encoding="utf-8",
    )
    result = validate_failure_catalog(path)
    assert any(f["reason_code"] == "loop_failure_mode_invalid_severity" for f in result["findings"])


def test_loop_audit_consumes_failure_catalog_status(tmp_path: Path) -> None:
    path = tmp_path / "docs/beacon/v1.6.5/execution/loop-failure-modes.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("### x\n\n- id: x\n- severity: S9\n", encoding="utf-8")
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5")
    signal = next(s for s in payload["signals"] if s["id"] == "failure_catalog")
    assert signal["status"] == "fail"
    assert signal["details"]["findings"]
