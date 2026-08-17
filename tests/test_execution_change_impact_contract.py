from __future__ import annotations

import json
from pathlib import Path

from beacon.commands.workflow import _write_execution_governance_artifacts


ROOT = Path(__file__).resolve().parents[1]


def test_change_impact_should_record_layers_and_tasks():
    _write_execution_governance_artifacts(
        project_root=ROOT,
        version="v1.1.1",
        run_id="run-acceptance-change-impact",
        feature="beacon-strict-config-governance",
        workflow_status="completed",
    )
    path = ROOT / "docs" / "beacon" / "v1.1.1" / ".machine" / "execution" / "change-impact.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["changed_layers"]
    assert isinstance(payload["tasks"], list)
    # research is input-only; convergence flags require real machine evidence, not a seeded run
    assert payload["research_converged"] is False
    assert payload["main_chain_converged"] is False
