from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_should_block_transient_runtime_artifacts():
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required = [
        ".omx/",
        ".beacon/iteration-governance/",
        ".beacon/state/workflow-hud/",
        ".beacon/runs/run-20*/",
        ".beacon/state/change-impact/run-20*.json",
        ".beacon/state/baselines/v*/bl-run-20*.json",
        ".beacon/state/spec-fingerprints/v*/run-20*.json",
        ".beacon/evidence/auto-test/run-20*/",
        ".beacon/implement/run-20*/",
        ".beacon/state/workflow-memory/run-20*/",
        ".beacon/flaky-history.json",
        ".beacon/state/evo/experiments/evo-20*.json",
        ".beacon/state/evo/ledger.jsonl",
        ".beacon/evidence/test-results/*",
        ".beacon/qa/features/*",
        ".tmp/",
    ]
    for item in required:
        assert item in text


def test_runtime_evidence_tracking_policy_should_document_tracked_and_ignored_surfaces():
    text = (
        ROOT
        / "docs"
        / "beacon"
        / "v1.1.10"
        / "execution"
        / "runtime-evidence-tracking-policy.md"
    ).read_text(encoding="utf-8")
    assert "## Track By Default" in text
    assert "## Ignore By Default" in text
    assert "run-v*" in text
    assert "run-20*" in text
    assert ".beacon/evidence/test-results/<current-release-feature>/TC-*.json" in text
    assert ".beacon/evidence/auto-test/run-20*/" in text
    assert ".beacon/implement/run-20*/" in text
    assert ".beacon/state/workflow-memory/run-20*/" in text
    assert ".beacon/evidence/test-results/*" in text


def test_only_current_release_test_results_should_remain_tracked():
    result = subprocess.run(
        ["git", "ls-files", ".beacon/evidence/test-results"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    tracked = {
        Path(line).parts[3]
        for line in result.stdout.splitlines()
        if line.strip()
    }
    assert tracked == {
        "beacon-prototype-frontend-route-closure",
        "beacon-qa-confidence-autoresearch-closure",
        "beacon-source-architecture-sync",
    }
