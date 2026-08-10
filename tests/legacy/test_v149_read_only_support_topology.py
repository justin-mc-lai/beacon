from __future__ import annotations

from pathlib import Path

import pytest

from beacon.utils.brainstorm import run_beacon_brainstorm
from beacon.utils.deep_loop import run_deep_loop
from beacon.utils.learn_surface import run_governed_recall
from beacon.utils.requirement_clarity import build_requirement_clarity_gate_payload
from beacon.utils.support_research_topology import (
    assert_support_write_topology,
    resolve_support_write_topology,
    upsert_support_finding_section,
)


VERSION = "v1.4.9"
FEATURE = "read-only support research write topology gate contract"
SLUG = "read-only-support-research-write-topology-gate-contract"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path, *, version: str = VERSION, feature: str = FEATURE, include_research: bool = True) -> None:
    slug = feature.lower().replace(" ", "-")
    _write(root, "docs/beacon/global-boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{version}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{version}/execution/index.md", "# Execution\n")
    _write(root, f"docs/beacon/{version}/execution/architecture-blueprint.md", "# Architecture Blueprint\n")
    _write(
        root,
        f"docs/beacon/{version}/prd/{slug}.md",
        "\n".join(
            [
                f"# PRD: {feature}",
                "",
                "- AC-001: Ordinary support writes feature research.",
                "- AC-002: Deep writes detailed artifacts under deep.",
                "- AC-003: Learn writes learning audit.",
                "- AC-004: Brainstorms fallback is disallowed.",
                "- AC-005: Repeated clarification upserts rounds.",
                "- AC-006: Cross-version clarification records lineage.",
                "- AC-007: Topology gate reports expected and actual paths.",
                "- AC-008: Pre-write gate blocks unresolved support target.",
                "",
                "## Diagram Truth",
                "- `branch-flow`",
                "- `state-machine`",
                "- `decision-priority`",
                "- state axes: `support_surface_class`, `write_target`, `material_effect`, `adoption_status`, `version_lineage`",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{version}/user-story/{slug}.md",
        "\n".join(
            [
                "# Story",
                "",
                "| AC ID | Theme | Description |",
                "| --- | --- | --- |",
                "| AC-001 | ordinary support topology | ordinary support writes research |",
                "| AC-002 | deep topology | deep writes artifacts and research index |",
                "| AC-003 | learning topology | learn writes audit and research summary |",
                "| AC-004 | no fallback | brainstorm fallback blocked |",
                "| AC-005 | repeated clarification | same version appends rounds |",
                "| AC-006 | version lineage | cross version records lineage |",
                "| AC-007 | fail-closed gate | diagnostics include paths |",
                "| AC-008 | pre-write gate | unresolved target blocked |",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{version}/qa/test-cases/{slug}.md",
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |",
                "| --- | --- | --- | --- | --- | --- |",
                "| AC-001 | TC-001 | contract | pytest | ordinary support writes research | evidence |",
                "| AC-002 | TC-002 | contract | pytest | deep writes artifacts and research index | evidence |",
                "| AC-003 | TC-003 | contract | pytest | learn writes audit and research summary | evidence |",
                "| AC-004 | TC-004 | gate | pytest | brainstorm fallback blocked | evidence |",
                "| AC-005 | TC-005 | contract | pytest | same version appends rounds | evidence |",
                "| AC-006 | TC-006 | contract | pytest | cross version records lineage | evidence |",
                "| AC-007 | TC-007 | gate | pytest | diagnostics include expected actual repair | evidence |",
                "| AC-008 | TC-008 | gate | pytest | unresolved target blocked | evidence |",
            ]
        )
        + "\n",
    )
    _write(root, f"docs/beacon/{version}/source-architecture/{slug}.md", "# Source Architecture\n")
    if include_research:
        _write(
            root,
            f"docs/beacon/{version}/research/{slug}.md",
            "\n".join(
                [
                    f"# Research: {feature}",
                    "",
                    "## Architecture",
                    "- topology gate",
                    "",
                    "## Business Flow",
                    "- branch-flow",
                    "",
                    "## State Machine",
                    "- state-machine",
                    "",
                    "## Decision Priority",
                    "- decision-priority",
                    "",
                    "## Support Findings",
                    "",
                    "## Route Decisions",
                    "",
                    "## Version Evolution Notes",
                    "",
                    "## Promotion Log",
                    "",
                    "## Truth Bindings",
                    f"- prd_refs: `docs/beacon/{version}/prd/{slug}.md`",
                    f"- user_story_refs: `docs/beacon/{version}/user-story/{slug}.md`",
                    f"- test_case_refs: `docs/beacon/{version}/qa/test-cases/{slug}.md`",
                    "- coverage_notes: AC-001 through AC-008",
                    "- out_of_scope_notes: no direct truth writes",
                ]
            )
            + "\n",
        )


def test_ordinary_support_writes_feature_research(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    payload = run_beacon_brainstorm(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        prompt="clarify support topology",
    )

    assert payload["output_path"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"
    assert not (tmp_path / "docs/brainstorms").exists()
    text = (tmp_path / payload["output_path"]).read_text(encoding="utf-8")
    assert "### Brainstorm" in text
    assert "source_skill: `beacon-brainstorm`" in text


def test_runtime_supported_brainstorm_infers_contract_slug_to_research(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    payload = run_beacon_brainstorm(
        tmp_path,
        version=VERSION,
        prompt=f"现在核实 {SLUG} 为何头暴文档写错目录，并收敛下一步。",
    )

    assert payload["feature_inferred"] is True
    assert payload["feature"] == SLUG
    assert payload["output_path"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"
    assert not (tmp_path / "docs/brainstorms").exists()


def test_deep_writes_artifact_family_and_research_index(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    payload = run_deep_loop(tmp_path, version=VERSION, feature=FEATURE)

    assert (tmp_path / f"docs/beacon/{VERSION}/deep/{SLUG}/deep-analysis-report.md").exists()
    research = (tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md").read_text(encoding="utf-8")
    assert "## Deep Summary" in research
    assert f"deep_artifact_root: `docs/beacon/{VERSION}/deep/{SLUG}`" in research
    assert "deep_analysis_report" not in research
    assert payload["support_research_writeback"]["path"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"


def test_deep_summary_may_index_deep_artifact_names(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _write(tmp_path, f"docs/beacon/{VERSION}/deep/{SLUG}/deep-analysis-report.md", "# Deep\n")
    research_path = tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md"
    research_path.write_text(
        research_path.read_text(encoding="utf-8")
        + "\n## Deep Summary\n\n- `deep-analysis-report.md`\n",
        encoding="utf-8",
    )

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    diagnostics = payload["support_write_topology_contract"]["diagnostics"]
    assert not any(item["reason_code"] == "support_topology_deep_detail_in_research" for item in diagnostics)


def test_learn_writes_learning_audit_and_research_index(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    payload = run_governed_recall(tmp_path, version=VERSION, feature=FEATURE, mode="recall", limit=5)

    assert (tmp_path / f"docs/beacon/{VERSION}/learning/{SLUG}.md").exists()
    research = (tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md").read_text(encoding="utf-8")
    assert "## Learning Influence Summary" in research
    assert f"learning_audit_ref: `docs/beacon/{VERSION}/learning/{SLUG}.md`" in research
    assert "learning_candidates" not in research
    assert payload["support_research_writeback"]["learning_audit_ref"] == f"docs/beacon/{VERSION}/learning/{SLUG}.md"


def test_brainstorm_fallback_disallowed_for_version_feature(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _write(tmp_path, f"docs/brainstorms/{SLUG}-brainstorm.md", f"# Bad\n{FEATURE}\n{VERSION}\n")

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    diagnostics = payload["support_write_topology_contract"]["diagnostics"]
    assert diagnostics[0]["reason_code"] == "support_topology_legacy_brainstorm_fallback"
    assert diagnostics[0]["expected_path"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"


def test_featureless_legacy_brainstorm_truth_ref_does_not_block_feature(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _write(
        tmp_path,
        "docs/brainstorms/legacy-version-brainstorm.md",
        "\n".join(
            [
                "# Legacy Brainstorm",
                "",
                "- version: `v1.4.9`",
                "- feature: ``",
                "",
                f"- `{f'docs/beacon/{VERSION}/prd/{SLUG}.md'}`",
            ]
        ),
    )

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    diagnostics = payload["support_write_topology_contract"]["diagnostics"]
    assert not any(item["reason_code"] == "support_topology_legacy_brainstorm_fallback" for item in diagnostics)


def test_same_version_clarification_upserts_rounds(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    upsert_support_finding_section(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        surface="beacon-security-review",
        finding_summary="first pass",
        round_id="R1",
    )
    upsert_support_finding_section(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        surface="beacon-security-review",
        finding_summary="second pass",
        round_id="R2",
    )

    research_files = list((tmp_path / f"docs/beacon/{VERSION}/research").glob(f"{SLUG}*.md"))
    text = (tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md").read_text(encoding="utf-8")
    assert len(research_files) == 1
    assert "#### Round R1" in text
    assert "#### Round R2" in text


def test_cross_version_clarification_records_lineage(tmp_path: Path) -> None:
    previous = "v1.4.8"
    _seed_docs(tmp_path, version=previous, feature=FEATURE)
    _seed_docs(tmp_path, version=VERSION, feature=FEATURE, include_research=False)

    upsert_support_finding_section(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        surface="beacon-source-driven",
        finding_summary="new version pass",
    )

    text = (tmp_path / f"docs/beacon/{VERSION}/research/{SLUG}.md").read_text(encoding="utf-8")
    assert f"previous_research: `docs/beacon/{previous}/research/{SLUG}.md`" in text
    assert "carried_forward" in text
    assert "superseded" in text


def test_topology_gate_reports_expected_and_actual_paths(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _write(tmp_path, f"docs/beacon/{VERSION}/research/{SLUG}-sidecar.md", "# duplicate\n")

    payload = build_requirement_clarity_gate_payload(tmp_path, version=VERSION, feature=FEATURE)

    assert payload["blocked"] is True
    finding = next(item for item in payload["findings"] if item["kind"] == "support_write_topology_violation")
    assert finding["expected_path"] == f"docs/beacon/{VERSION}/research/{SLUG}.md"
    assert finding["actual_path"] == f"docs/beacon/{VERSION}/research/{SLUG}-sidecar.md"
    assert finding["repair_route"]


def test_pre_write_gate_blocks_unresolved_support_target(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    gate = resolve_support_write_topology(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        surface="beacon-brainstorm",
        actual_path=f"docs/brainstorms/{SLUG}.md",
    )

    assert gate["blocked"] is True
    assert gate["diagnostics"][0]["reason_code"] == "support_topology_actual_path_mismatch"
    with pytest.raises(ValueError):
        assert_support_write_topology(
            tmp_path,
            version=VERSION,
            feature=FEATURE,
            surface="beacon-brainstorm",
            actual_path=f"docs/brainstorms/{SLUG}.md",
        )
