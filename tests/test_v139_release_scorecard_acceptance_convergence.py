from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.release_scorecard import build_release_scorecard


VERSION = "v1.3.9"
FEATURE = "Beacon v1.3.9 execution projection convergence and QA acceptance dual-write"
SLUG = "beacon-v1.3.9-execution-projection-convergence-and-qa-acceptance-dual-write"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_v139_release_scorecard_should_consume_qa_acceptance_envelope(tmp_path: Path) -> None:
    docs = tmp_path / "docs" / "beacon" / VERSION
    (docs / ".machine" / "execution").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".beacon").mkdir(parents=True, exist_ok=True)
    _write_json(tmp_path / ".beacon" / "gate-report.json", {"status": "Pass", "version": VERSION, "issues": []})
    _write_json(
        tmp_path / ".beacon" / "qa" / "status.json",
        {
            "feature": FEATURE,
            "version": VERSION,
            "status": "passed",
            "evidence_done": False,
            "execution_mode": "feature-aware",
        },
    )
    _write_json(
        docs / ".machine" / "execution" / f"qa-acceptance-{SLUG}.json",
        {
            "schema_version": "1.0",
            "artifact": "qa_acceptance_envelope",
            "version": VERSION,
            "feature": FEATURE,
            "feature_slug": SLUG,
            "verdict": "passed",
            "transaction_id": "tx-qa-acceptance-v139",
            "revision_delivery_status": "accepted",
        },
    )

    payload = build_release_scorecard(tmp_path, version=VERSION)

    assert payload["acceptance"]["source"] == "qa_acceptance_envelope"
    assert payload["qa"]["acceptance_transaction_id"] == "tx-qa-acceptance-v139"
    assert payload["qa"]["acceptance_verdict"] == "passed"
    assert payload["qa"]["evidence_done"] is True
