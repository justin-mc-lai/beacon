"""v1.1.0 memory governance metrics contracts."""

from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.v110_metrics import compute_memory_governance_metrics


def test_memory_layers_should_expose_retention_and_dedup_metrics(tmp_path: Path):
    debug_dir = tmp_path / ".beacon" / "state" / "debug-feedback"
    candidate_dir = tmp_path / ".beacon" / "state" / "feedback-candidates"
    apply_dir = tmp_path / ".beacon" / "state" / "feedback-apply-report"
    lifecycle_index = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.index.json"

    debug_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    apply_dir.mkdir(parents=True, exist_ok=True)
    lifecycle_index.parent.mkdir(parents=True, exist_ok=True)

    (debug_dir / "run-001.jsonl").write_text(
        json.dumps({"run_id": "run-001", "source": "prompt.optimize"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (candidate_dir / "run-001.json").write_text(
        json.dumps({"run_id": "run-001", "feedback": [{"reason_code": "low-confidence"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (apply_dir / "run-001.json").write_text(
        json.dumps({"run_id": "run-001", "items": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    lifecycle_index.write_text(
        json.dumps({"dedupe_keys": ["a", "b"]}, ensure_ascii=False),
        encoding="utf-8",
    )

    metrics = compute_memory_governance_metrics(tmp_path)
    assert metrics.get("raw_debug_files") == 1
    assert metrics.get("raw_debug_events") == 1
    assert metrics.get("candidate_files") == 1
    assert metrics.get("apply_reports") == 1
    assert metrics.get("lifecycle_dedupe_keys") == 2
