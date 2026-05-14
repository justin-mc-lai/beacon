from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from beacon.utils.automation_summary import build_automation_summary_payload


def test_automation_summary_should_surface_reconciliation_requirements(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "feature": "feature-a",
                        "status": "blocked",
                        "continue_decision": "stop_for_repair",
                        "summary": {
                            "reconciliation_required": True,
                            "reconciliation_reason_code": "implementation_first_reconciliation_required",
                            "reconciliation_artifact_path": "docs/beacon/v1.4.6/.machine/change/feature-a-reconciliation.json",
                            "reconciliation_reprojection_targets": ["qa_proof", "release_facing_proof"],
                        },
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = build_automation_summary_payload(
        project_root=tmp_path,
        summary_kind="qa",
        job="nightly-qa",
        layer="qa",
        ledger_path=ledger_path,
    )

    assert payload["reconciliation"]["required_feature_count"] == 1
    assert payload["reconciliation"]["required_features"] == ["feature-a"]
    assert "qa_proof" in payload["reconciliation"]["reprojection_targets"]
    assert any(line == "reconciliation_required=feature-a" for line in payload["notification"]["lines"])


def test_feishu_post_should_append_reconciliation_summary_block() -> None:
    script_path = Path("/Users/apple/Developer/Personal/products/beacon/automation/jobs/beacon-notify-feishu-post.py")
    spec = importlib.util.spec_from_file_location("beacon_notify_feishu_post", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    payload = module.build_payload(
        title="Beacon",
        summary={
            "notification": {"title": "Beacon", "lines": ["status=blocked"]},
            "reconciliation": {
                "required_features": ["feature-a"],
                "reprojection_targets": ["qa_proof", "release_facing_proof"],
            },
        },
    )

    content = payload["content"]["post"]["zh_cn"]["content"]
    flattened = [item["text"] for row in content for item in row]
    assert "reconciliation_summary" in flattened
    assert "required_features=feature-a" in flattened
    assert "reprojection_targets=qa_proof, release_facing_proof" in flattened
