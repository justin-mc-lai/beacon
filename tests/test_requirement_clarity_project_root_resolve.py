from __future__ import annotations

import json
from pathlib import Path

from beacon.utils.acceptance_kit import load_acceptance_kit
from beacon.utils.brainstorm import run_beacon_brainstorm
from beacon.utils.requirement_clarity import (
    build_requirement_clarity_gate_payload,
    materialize_requirement_clarity,
)
from beacon.utils.story_state import feature_slug


VERSION = "v1.5.2"
FEATURE = "path-resolve-smoke"
SLUG = feature_slug(FEATURE)


def _seed_v152_feature_package(root: Path) -> None:
    beacon_docs = root / "docs" / "beacon"
    beacon_docs.mkdir(parents=True, exist_ok=True)
    (beacon_docs / "VERSION").write_text(f"{VERSION}\n", encoding="utf-8")
    feature_dir = root / "docs" / "beacon" / VERSION / "features" / SLUG
    feature_dir.mkdir(parents=True, exist_ok=True)
    (feature_dir / "truth.md").write_text(
        "\n".join(
            [
                "# Truth",
                "",
                "## Scope",
                "",
                "Path normalization smoke feature.",
            ]
        ),
        encoding="utf-8",
    )
    (feature_dir / "tests.md").write_text("# Tests\n\n- TC-001 smoke\n", encoding="utf-8")
    kit_dir = root / "docs" / "beacon" / VERSION / ".machine" / "execution"
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / f"acceptance-kit-{SLUG}.json").write_text(
        json.dumps({"layers": {"skill-contract": {"status": "pass"}}}),
        encoding="utf-8",
    )


def test_requirement_clarity_should_resolve_relative_project_root(tmp_path: Path, monkeypatch) -> None:
    _seed_v152_feature_package(tmp_path)
    monkeypatch.chdir(tmp_path)

    payload = build_requirement_clarity_gate_payload(Path("."), version=VERSION, feature=FEATURE)
    assert payload["report_json_path"]
    assert not Path(payload["report_json_path"]).is_absolute()

    materialized = materialize_requirement_clarity(Path("."), version=VERSION, feature=FEATURE)
    assert materialized["report"]["json"]
    assert (tmp_path / materialized["report"]["json"]).exists()


def test_acceptance_kit_should_resolve_relative_project_root(tmp_path: Path, monkeypatch) -> None:
    _seed_v152_feature_package(tmp_path)
    monkeypatch.chdir(tmp_path)

    kit = load_acceptance_kit(Path("."), version=VERSION, feature=FEATURE)
    assert kit["_machine_path"]
    assert not Path(kit["_machine_path"]).is_absolute()


def test_brainstorm_should_resolve_relative_project_root(tmp_path: Path, monkeypatch) -> None:
    _seed_v152_feature_package(tmp_path)
    monkeypatch.chdir(tmp_path)

    payload = run_beacon_brainstorm(
        Path("."),
        version=VERSION,
        prompt="Path normalization smoke for requirement clarity relative_to bug.",
        mode="requirement-convergence",
        feature=FEATURE,
    )
    assert payload["artifact"] == "beacon_brainstorm"
    assert payload["version"] == VERSION
    assert payload["feature_slug"] == SLUG
