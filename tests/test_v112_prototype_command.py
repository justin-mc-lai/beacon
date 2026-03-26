"""Prototype command contracts for Beacon prototype generation."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app

runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_contract_sources(tmp_path: Path, feature: str, version: str = "v1.1.2") -> None:
    slug = feature.lower().replace(" ", "-")
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# User Story: {feature}",
                "",
                "**As a** operations manager,",
                "**I want** a clear console,",
                "**So that** I can review delivery state.",
                "",
                "prototype_archetype: dashboard",
                "target_user: operations manager",
                "theme_mood: trustworthy",
                "theme_primary: #2563eb",
                "theme_secondary: #0f172a",
                "brand_keywords: trust, signal, review",
                "surface_style: elevated-clean",
                "sections: Delivery Overview, Review Queue, Escalations",
                "navigation: Overview, Review Queue, Escalations",
                "primary_entry: Overview",
                "primary_exit: Escalations",
                "primary_cta: Review blockers",
                "secondary_cta: Export report",
                "jump_map: Overview->Review Queue: Investigate pending blockers; Review Queue->Escalations: Escalate critical issues",
                "modal_map: Review blockers modal",
                "drawer_map: Escalation details drawer",
                "tab_map: Overview, Queue, States",
                "states: empty, loading, error, success, blocked",
            ]
        ),
        encoding="utf-8",
    )
    (prd_dir / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# PRD: {feature}",
                "",
                "prototype_archetype: dashboard",
                "theme_mood: trustworthy",
                "theme_primary: #1d4ed8",
                "theme_secondary: #111827",
                "brand_keywords: governance, control, review",
                "surface_style: elevated-clean",
                "sections: Delivery Overview, Review Queue, Escalations",
                "navigation: Overview, Review Queue, Escalations",
                "primary_entry: Overview",
                "primary_exit: Escalations",
                "primary_cta: Review blockers",
                "secondary_cta: Export report",
                "jump_map: Overview->Review Queue: Investigate pending blockers; Review Queue->Escalations: Escalate critical issues",
                "modal_map: Review blockers modal; Escalation summary modal",
                "drawer_map: Escalation details drawer",
                "tab_map: Overview, Queue, States",
                "states: empty, loading, error, success, blocked",
            ]
        ),
        encoding="utf-8",
    )


def test_prototype_help():
    result = _invoke(["prototype", "--help"])
    assert result.exit_code == 0
    assert "Generate and manage static UI prototypes" in result.stdout
    assert "review" in result.stdout


def test_prototype_create_generates_contract_driven_bootstrap_artifacts(tmp_path: Path):
    feature = "Login Feature"
    _prepare_contract_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0, result.stdout
    root = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / "login-feature"
    html_path = root / "index.html"
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "Bootstrap" in content
    assert "Review blockers" in content
    assert "Escalations" in content
    for extra in [
        "prototype-brief.json",
        "theme.json",
        "navigation-map.json",
        "interaction-map.json",
    ]:
        assert (root / extra).exists(), extra


def test_prototype_outputs_only_under_docs_beacon(tmp_path: Path):
    feature = "Orders Dashboard"
    _prepare_contract_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["paths"]["index_html"].startswith("docs/beacon/v1.1.2/prototype/")
    assert "docs/product" not in result.stdout
    assert payload["prototype_type"] == "dashboard"


def test_prototype_manifest_source_map_and_contract_artifacts(tmp_path: Path):
    feature = "Profile Center"
    _prepare_contract_sources(tmp_path, feature)
    result = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    root = tmp_path / "docs" / "beacon" / "v1.1.2" / "prototype" / "profile-center"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    source_map = json.loads((root / "source-map.json").read_text(encoding="utf-8"))
    freeze = json.loads((root / "freeze.json").read_text(encoding="utf-8"))
    brief = json.loads((root / "prototype-brief.json").read_text(encoding="utf-8"))
    theme = json.loads((root / "theme.json").read_text(encoding="utf-8"))
    navigation_map = json.loads((root / "navigation-map.json").read_text(encoding="utf-8"))
    interaction_map = json.loads((root / "interaction-map.json").read_text(encoding="utf-8"))
    assert manifest["ui_kit"] == "bootstrap-5.3.x"
    assert manifest["status"] == "draft"
    assert manifest["review_status"] == "missing"
    assert source_map["derived_from"] == ["user-story", "prd"]
    assert freeze["status"] == "draft"
    assert brief["prototype_archetype"] == "dashboard"
    assert theme["primary"]
    assert navigation_map["navigation_nodes"]
    assert interaction_map["ctas"]


def test_prototype_review_freeze_and_status_gate_ready(tmp_path: Path):
    feature = "Settings Screen"
    _prepare_contract_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"
    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", "v1.1.2", "--json"])
    status_payload = json.loads(status.stdout)
    assert status_payload["review_status"] == "pass"
    assert status_payload["gate_ready"] is True


def test_prototype_list_lists_existing_prototypes_with_review_state(tmp_path: Path):
    feature = "Risk Console"
    _prepare_contract_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    result = _invoke(["prototype", "list", "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 0
    assert "risk-console" in result.stdout
    assert "review=pass" in result.stdout


def test_prototype_create_requires_valid_contract_sources(tmp_path: Path):
    version = "v1.1.2"
    slug = "missing-feature"
    us_dir = tmp_path / "docs" / "beacon" / version / "user-story"
    prd_dir = tmp_path / "docs" / "beacon" / version / "prd"
    us_dir.mkdir(parents=True, exist_ok=True)
    prd_dir.mkdir(parents=True, exist_ok=True)
    (us_dir / f"{slug}.md").write_text("# User Story\n", encoding="utf-8")
    (prd_dir / f"{slug}.md").write_text("# PRD\n", encoding="utf-8")
    result = _invoke(["prototype", "create", "Missing Feature", "--project", str(tmp_path), "--version", version])
    assert result.exit_code == 2
    assert "Prototype Contract invalid" in result.stdout or "Prototype Contract invalid" in result.stderr


def test_prototype_freeze_requires_review_pass(tmp_path: Path):
    feature = "Billing Portal"
    _prepare_contract_sources(tmp_path, feature)
    _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    result = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", "v1.1.2"])
    assert result.exit_code == 2
    assert "Prototype review missing" in result.stdout or "Prototype review missing" in result.stderr
