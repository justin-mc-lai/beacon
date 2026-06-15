from __future__ import annotations

from pathlib import Path

from beacon.commands.gate import REASON_CODES, GateMode, check_delivery_execution_artifacts


def test_delivery_checks_should_emit_reason_code_when_manifest_missing(tmp_path: Path):
    issues = check_delivery_execution_artifacts(tmp_path, GateMode.STRICT, "release", "v1.1.1")
    codes = {item["reason_code"] for item in issues}
    assert "execution_config_missing" in codes
    assert "delivery_manifest_missing" in codes


def test_tig_dc_reason_codes_registered():
    """TIG-DC reason codes must be present in the canonical REASON_CODES list."""
    assert "TRUTH_DETERMINISM_PLACEHOLDER" in REASON_CODES
    assert "TRUTH_DETERMINISM_HOLLOW_TEMPLATE" in REASON_CODES
