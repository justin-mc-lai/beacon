from __future__ import annotations

from pathlib import Path

from beacon.utils.delivery_baseline import (
    load_implementation_delivery_host,
    materialize_implementation_delivery_baseline,
    validate_architecture_blueprint_projection,
)


VERSION = "v1.3.12"


def _seed_blueprint_root(root: Path) -> None:
    execution = root / "docs" / "beacon" / VERSION / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    (execution / "architecture-blueprint.md").write_text(
        "\n".join(
            [
                f"# Beacon {VERSION} Architecture Blueprint",
                "",
                "## Version Theme",
                "",
                "- feature-aware architecture blueprint projection",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_v1312_architecture_blueprint_should_keep_multiple_feature_projections_without_overwrite(tmp_path: Path) -> None:
    _seed_blueprint_root(tmp_path)

    first_feature = "Beacon v1.3.12 feature-aware blueprint alpha"
    second_feature = "Beacon v1.3.12 feature-aware blueprint beta"

    materialize_implementation_delivery_baseline(
        tmp_path,
        version=VERSION,
        feature=first_feature,
        revision_id="R1",
        seed={
            "base_branch": "main",
            "target_branch": "beacon/v1.3.12",
            "branch_prefix": "beacon/",
            "service_directories": ["api"],
            "writable_services": ["api"],
            "reference_only_services": ["docs"],
        },
    )
    materialize_implementation_delivery_baseline(
        tmp_path,
        version=VERSION,
        feature=second_feature,
        revision_id="R1",
        seed={
            "base_branch": "main",
            "target_branch": "beacon/v1.3.12",
            "branch_prefix": "beacon/",
            "service_directories": ["web"],
            "writable_services": ["web"],
            "reference_only_services": ["docs"],
        },
    )

    blueprint = (tmp_path / "docs" / "beacon" / VERSION / "execution" / "architecture-blueprint.md").read_text(
        encoding="utf-8"
    )
    host = load_implementation_delivery_host(tmp_path, version=VERSION)

    assert "<!-- BEACON:IMPLEMENTATION-DELIVERY-HOST:START -->" in blueprint
    assert "<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.3.12-feature-aware-blueprint-alpha:START -->" in blueprint
    assert "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.3.12-feature-aware-blueprint-alpha:START -->" in blueprint
    assert "<!-- BEACON:TECHNICAL-DELTA-BLUEPRINT:beacon-v1.3.12-feature-aware-blueprint-beta:START -->" in blueprint
    assert "<!-- BEACON:IMPLEMENTATION-DELIVERY-BASELINE:beacon-v1.3.12-feature-aware-blueprint-beta:START -->" in blueprint
    assert "## Implementation Delivery Host" in blueprint
    assert blueprint.count("## Implementation Delivery Baseline") == 2
    assert blueprint.count("## Technical Delta Blueprint") == 2
    assert host["feature_count"] == 2
    assert host["feature_slugs"] == [
        "beacon-v1.3.12-feature-aware-blueprint-alpha",
        "beacon-v1.3.12-feature-aware-blueprint-beta",
    ]

    first_gate = validate_architecture_blueprint_projection(
        tmp_path,
        version=VERSION,
        feature=first_feature,
    )
    second_gate = validate_architecture_blueprint_projection(
        tmp_path,
        version=VERSION,
        feature=second_feature,
    )

    assert first_gate["status"] == "pass"
    assert first_gate["blocked"] is False
    assert second_gate["status"] == "pass"
    assert second_gate["blocked"] is False
