from __future__ import annotations

from pathlib import Path

from beacon.utils.loop_patterns import validate_pattern_registry
from beacon.utils.loop_readiness import build_loop_readiness_audit


ARCHIVE_REGISTRY = Path(__file__).resolve().parents[1] / "docs/beacon/archive/v1.6.5/loop-patterns/registry.yaml"


def _write_registry(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_registry_file_contains_required_patterns() -> None:
    result = validate_pattern_registry(ARCHIVE_REGISTRY)
    assert result["status"] == "pass"
    assert {"ralph", "team", "beacon-loop"}.issubset(set(result["pattern_ids"]))


def test_registry_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "registry.yaml"
    _write_registry(path, "patterns:\n  -\n    id: ralph\n")
    result = validate_pattern_registry(path)
    assert result["status"] == "fail"
    assert result["findings"][0]["reason_code"] == "loop_pattern_required_field_missing"


def test_duplicate_pattern_ids_block(tmp_path: Path) -> None:
    body = """
patterns:
  -
    id: x
    cadence: daily
    risk: low
    harness_skills: [generator]
    state_surface: .beacon/x
    phases: [run]
    human_gates: [qa]
    token_cost: 1
    daily_cap: 2
    safety: {}
  -
    id: x
    cadence: daily
    risk: low
    harness_skills: [generator]
    state_surface: .beacon/x
    phases: [run]
    human_gates: [qa]
    token_cost: 1
    daily_cap: 2
    safety: {}
"""
    path = tmp_path / "registry.yaml"
    _write_registry(path, body)
    result = validate_pattern_registry(path)
    assert result["status"] == "fail"
    assert any(f["reason_code"] == "loop_pattern_duplicate_id" for f in result["findings"])


def test_risk_values_are_governed(tmp_path: Path) -> None:
    path = tmp_path / "registry.yaml"
    _write_registry(path, """
patterns:
  -
    id: x
    cadence: daily
    risk: severe
    harness_skills: [generator]
    state_surface: .beacon/x
    phases: [run]
    human_gates: [qa]
    token_cost: 1
    daily_cap: 2
    safety: {}
""")
    result = validate_pattern_registry(path)
    assert any(f["reason_code"] == "loop_pattern_invalid_risk" for f in result["findings"])


def test_loop_audit_consumes_registry_status(tmp_path: Path) -> None:
    (tmp_path / "docs/beacon/v1.6.5/loop-patterns").mkdir(parents=True)
    (tmp_path / "docs/beacon/v1.6.5/loop-patterns/registry.yaml").write_text("patterns:\n  -\n    id: x\n", encoding="utf-8")
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5")
    registry_signal = next(s for s in payload["signals"] if s["id"] == "pattern_registry")
    assert registry_signal["status"] == "fail"
    assert registry_signal["details"]["findings"]
