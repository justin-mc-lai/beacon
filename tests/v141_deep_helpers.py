from __future__ import annotations

from pathlib import Path

from beacon.utils.revision_state import freeze_revision_state

VERSION = "v1.4.1"
FEATURE = "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure"
SLUG = "beacon-v1.4.1-deep-analysis-support-surface-and-risk-closure"


def seed_deep_project(root: Path, *, feature: str = FEATURE, docs_version: str = VERSION) -> Path:
    version_root = root / "docs" / "beacon" / docs_version
    slug = feature.lower().replace(" ", "-")
    (version_root / "prd").mkdir(parents=True, exist_ok=True)
    (version_root / "user-story").mkdir(parents=True, exist_ok=True)
    (version_root / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (version_root / "execution").mkdir(parents=True, exist_ok=True)
    (version_root / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (version_root / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (version_root / "prd" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# PRD: {feature}",
                "",
                "Status: freeze-ready",
                "",
                "## Scope",
                "This payment, order, wallet, ranking, scoring, identity binding, invitation, relationship chain, reporting, migration, multi-role, multi-state, state machine, fact source, attribution, and consistency feature requires deep analysis.",
                "",
                "## Diagram Truth",
                "- `branch-flow`",
                "  - `deep finding -> route decision -> existing Beacon surface -> closure evidence`",
                "- `state-machine`",
                "  - `deep_loop_open -> routed -> verified -> closed`",
                "- `decision-priority`",
                "  - `frozen truth > deep finding > projection > learning hint`",
                "- state axes: `deep_requirement_state`, `deep_finding_state`, `deep_delta_state`, `release_risk_state`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (version_root / "user-story" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# User Stories: {feature}",
                "",
                "## US-001",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | support-skill-boundary | beacon-deep is support surface |",
                "| AC-002 | public-entry | beacon deep run is public entry |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (version_root / "qa" / "test-cases" / f"{slug}.md").write_text(
        "\n".join(
            [
                f"# Test Cases: {feature}",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |",
                "| --- | --- | --- | --- | --- | --- |",
                "| AC-001 | TC-US001-001 | contract | pytest | support surface | .beacon/evidence/TC-US001-001.json |",
                "| AC-002 | TC-US001-002 | contract | pytest | public entry | .beacon/evidence/TC-US001-002.json |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    freeze_revision_state(root, version=docs_version, feature=feature)
    return version_root
