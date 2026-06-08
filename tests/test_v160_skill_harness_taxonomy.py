from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write_research(path: Path, *, decision: str = "queued", promotion_ref: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Planner Research",
                "",
                "- authority: support_advisory",
                "- status: queued",
                "- outcome: 收敛 Beacon v1.6.0 harness skill 边界",
                "- lake_or_ocean: lake，单 feature 可煮干",
                "- truth_refs: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md",
                "- source_refs: beacon/utils/agent_surface.py",
                "- evidence_refs: tests/test_v160_skill_harness_taxonomy.py",
                "- truth_gap: 无",
                "- test_gap: 无",
                "- implementation_risk: low",
                "- verification_risk: low",
                "- recommended_route: beacon-generator-truth-refreeze",
                f"- user_decision: {decision}",
                f"- promotion_ref: {promotion_ref}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_v160_skill_package_materialize_should_create_harness_only_package(tmp_path: Path) -> None:
    result = _invoke(
        [
            "skill",
            "package",
            "materialize",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"

    package_root = Path(payload["package_root"])
    skill_dirs = {item.name for item in package_root.iterdir() if item.is_dir()}
    assert "beacon-planner-source-driven" in skill_dirs
    assert "beacon-generator-implementation" in skill_dirs
    assert "beacon-evaluator-qa" in skill_dirs
    assert "beacon-governor-router" in skill_dirs
    assert all(name.startswith(("beacon-planner-", "beacon-generator-", "beacon-evaluator-", "beacon-governor-")) for name in skill_dirs)
    for old_name in ("beacon-brainstorm", "beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-implement", "beacon-qa", "beacon-release", "using-beacon"):
        assert old_name not in skill_dirs

    source_driven = (package_root / "beacon-planner-source-driven" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: beacon-planner-source-driven" in source_driven
    assert "Beacon v1.6.0 共享 Preamble" in source_driven
    assert "HARD GATE:" in source_driven
    assert "你正在运行 planner skill" in source_driven
    assert "outcome、truth/source/evidence refs、湖/海" in source_driven
    assert source_driven.index("Beacon v1.6.0 共享 Preamble") < source_driven.index("HARD GATE:")

    metadata = json.loads((package_root / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["version"] == "v1.6.0"
    assert metadata["source_kind"] == "generated_v160_harness_taxonomy"


def test_v160_skill_package_verify_should_fail_for_old_alias_and_missing_gate(tmp_path: Path) -> None:
    setup = _invoke(["skill", "package", "materialize", "--project-root", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert setup.exit_code == 0, setup.stdout
    package_root = Path(json.loads(setup.stdout)["package_root"])

    old_alias = package_root / "beacon-qa"
    old_alias.mkdir()
    (old_alias / "SKILL.md").write_text("---\nname: beacon-qa\n---\n# Old QA\n", encoding="utf-8")
    implementation_skill = package_root / "beacon-generator-implementation" / "SKILL.md"
    text = implementation_skill.read_text(encoding="utf-8")
    implementation_skill.write_text(text.replace("HARD GATE:", "SOFT GATE:", 1), encoding="utf-8")

    verify = _invoke(
        [
            "skill",
            "package",
            "verify",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--json",
        ]
    )
    assert verify.exit_code == 2, verify.stdout
    payload = json.loads(verify.stdout)
    checks = {item["name"]: item for item in payload["checks"]}
    assert "beacon-qa" in checks["v160_no_old_host_visible_aliases"]["details"]["old_aliases"]
    assert "beacon-generator-implementation" in checks["v160_shared_preamble_and_hard_gates"]["details"]["gate_errors"]


def test_v160_research_contract_allows_queued_but_blocks_promotion_without_user_acceptance(tmp_path: Path) -> None:
    research_path = tmp_path / "docs" / "beacon" / "v1.6.0" / "research" / "feature-x.md"
    _write_research(research_path)

    contract = _invoke(
        [
            "skill",
            "package",
            "verify-research",
            "feature-x",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--json",
        ]
    )
    assert contract.exit_code == 0, contract.stdout
    contract_payload = json.loads(contract.stdout)
    assert contract_payload["authority"] == "support_advisory"
    assert contract_payload["truth_authority"] is False
    assert contract_payload["promotion_gate"]["allowed"] is False

    promotion = _invoke(
        [
            "skill",
            "package",
            "verify-promotion",
            "feature-x",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--json",
        ]
    )
    assert promotion.exit_code == 2, promotion.stdout
    promotion_payload = json.loads(promotion.stdout)
    assert "user_decision_not_accepted_or_promoted" in promotion_payload["promotion_gate"]["reason_codes"]
    assert "promotion_ref_missing" in promotion_payload["promotion_gate"]["reason_codes"]


def test_v160_research_promotion_passes_with_accepted_decision_and_ref(tmp_path: Path) -> None:
    research_path = tmp_path / "docs" / "beacon" / "v1.6.0" / "research" / "feature-x.md"
    _write_research(
        research_path,
        decision="accepted",
        promotion_ref="docs/beacon/v1.6.0/features/feature-x/truth.md",
    )

    promotion = _invoke(
        [
            "skill",
            "package",
            "verify-promotion",
            "feature-x",
            "--project-root",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--json",
        ]
    )
    assert promotion.exit_code == 0, promotion.stdout
    payload = json.loads(promotion.stdout)
    assert payload["promotion_gate"]["allowed"] is True
    assert payload["truth_authority"] is False


def test_v160_route_prompt_outputs_required_planner_contract_fields() -> None:
    result = _invoke(
        [
            "skill",
            "package",
            "route-prompt",
            "分析 Beacon v1.6.0 整体 skill harness 重命名和验收",
            "--truth-refs",
            "docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md",
            "--source-refs",
            "beacon/utils/agent_surface.py",
            "--evidence-refs",
            "tests/test_v160_skill_harness_taxonomy.py",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    for key in (
        "outcome",
        "truth_refs",
        "source_refs",
        "evidence_refs",
        "lake_or_ocean",
        "truth_gap",
        "test_gap",
        "implementation_risk",
        "verification_risk",
        "recommended_route",
    ):
        assert key in payload
    assert payload["harness"] == "planner"
    assert payload["recommended_route"].startswith("beacon-planner-")


def test_v160_no_fake_delivery_rejects_placeholder_closure() -> None:
    result = _invoke(
        [
            "skill",
            "package",
            "verify-closure",
            "--payload-json",
            json.dumps({"implementation": "placeholder implementation", "assertions": "zero assertions"}),
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["closure_allowed"] is False
    assert "placeholder_implementation" in payload["detected"]
    assert "zero_assertions" in payload["detected"]
