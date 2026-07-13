from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from beacon.utils.loop_readiness import REQUIRED_SIGNAL_IDS, build_loop_readiness_audit, readiness_level


def test_loop_audit_json_shape(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "beacon", "doctor", "loop-audit", "--project-root", str(tmp_path), "--version", "v1.6.5", "--json"],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    for key in ("schema_version", "score", "level", "signals", "findings", "suggestions", "version"):
        assert key in payload


def test_score_level_thresholds() -> None:
    assert readiness_level(0) == "L0"
    assert readiness_level(39) == "L0"
    assert readiness_level(40) == "L1"
    assert readiness_level(59) == "L1"
    assert readiness_level(60) == "L2"
    assert readiness_level(79) == "L2"
    assert readiness_level(80) == "L3"


def test_signal_inventory_contains_required_signals(tmp_path: Path) -> None:
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5")
    signals = {signal["id"]: signal for signal in payload["signals"]}
    assert set(REQUIRED_SIGNAL_IDS).issubset(signals)
    for signal in signals.values():
        assert "status" in signal
        assert "weight" in signal
        assert "reason_code" in signal


def test_strict_below_threshold_blocks(tmp_path: Path) -> None:
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5", strict=True, threshold=80)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "loop_readiness_below_threshold"


def test_suggestions_are_ordered_and_actionable(tmp_path: Path) -> None:
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5")
    assert payload["suggestions"]
    assert all(item.get("command") or item.get("route") for item in payload["suggestions"])


def test_non_strict_is_report_only(tmp_path: Path) -> None:
    payload = build_loop_readiness_audit(tmp_path, version="v1.6.5", strict=False, threshold=80)
    assert payload["status"] == "report_only"
    assert payload["blocked"] is False
    assert payload["release_verdict"] is False
