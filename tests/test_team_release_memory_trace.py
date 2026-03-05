"""Team/release/bridge memory trace tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _find_team_name(project_root: Path) -> str:
    team_root = project_root / ".beacon" / "team"
    teams = sorted([p.name for p in team_root.iterdir() if p.is_dir()])
    assert teams
    return teams[-1]


def _load_memory_sources(project_root: Path) -> list[str]:
    memory_root = project_root / ".beacon" / "memory"
    sources: list[str] = []
    for file_name, key in (
        ("project-insights.json", "insights"),
        ("decisions.json", "decisions"),
        ("vocabulary.json", "terms"),
    ):
        path = memory_root / file_name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get(key, []):
            if isinstance(row, dict):
                sources.append(str(row.get("source", "")))
    return sources


def _seed_release_artifacts(project_root: Path) -> None:
    beacon_dir = project_root / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    (beacon_dir / "auto-test-status.json").write_text(
        json.dumps({"status": "passed", "updated_at": "2026-03-05T00:00:00Z"}),
        encoding="utf-8",
    )
    (beacon_dir / "gate-report.json").write_text(
        json.dumps(
            {
                "stage": "release",
                "mode": "strict",
                "status": "Pass",
                "issues": [],
                "coverage": {"full_coverage": True},
                "updated_at": "2026-03-05T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (beacon_dir / "evidence-manifest.json").write_text(
        json.dumps({"entries": [{"path": ".beacon/auto-test-status.json", "sha256": "x"}]}),
        encoding="utf-8",
    )


def test_team_release_and_bridge_should_leave_memory_trace(tmp_path: Path):
    started = _invoke(["team", "start", "Lifecycle Memory Delivery", "--members", "3", "--project", str(tmp_path)])
    assert started.exit_code == 0
    team_name = _find_team_name(tmp_path)

    assert _invoke(
        ["team", "review", "spec", "pass", "--reviewer", "pm", "--team", team_name, "--project", str(tmp_path)]
    ).exit_code == 0
    assert _invoke(
        ["team", "review", "quality", "pass", "--reviewer", "qa", "--team", team_name, "--project", str(tmp_path)]
    ).exit_code == 0
    assert _invoke(["team", "evaluate", "0", "0", "--team", team_name, "--project", str(tmp_path)]).exit_code == 0

    assert _invoke(["release", "create", "v1.2.3", "--project", str(tmp_path)]).exit_code == 0
    _seed_release_artifacts(tmp_path)
    assert _invoke(["release", "check", "v1.2.3", "--project", str(tmp_path)]).exit_code == 0

    assert _invoke(["ralph-bridge", "start", "work", "--project", str(tmp_path)]).exit_code == 0
    assert _invoke(["ralph-bridge", "stop", "--project", str(tmp_path)]).exit_code == 0

    sources = _load_memory_sources(tmp_path)
    assert any(s.startswith("team.") for s in sources)
    assert "release.create" in sources
    assert "release.check" in sources
    assert "ralph-bridge.start" in sources
    assert "ralph-bridge.stop" in sources

    lifecycle_file = tmp_path / ".beacon" / "memory" / "workflow-lifecycle.json"
    assert lifecycle_file.exists()
    lifecycle = json.loads(lifecycle_file.read_text(encoding="utf-8"))
    events = lifecycle.get("items", [])
    assert any(item.get("event") == "team_review_submitted" for item in events if isinstance(item, dict))
    assert any(item.get("event") == "release_decision_recorded" for item in events if isinstance(item, dict))
