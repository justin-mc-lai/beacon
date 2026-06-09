from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.auto_test import (
    _mark_negative_expected_block_passed,
    _negative_expected_block_observed,
    _run_layer_command,
)
from beacon.utils.qa_feature import build_feature_qa_plan, materialize_feature_qa_matrix


runner = CliRunner()

ROOT = Path(__file__).resolve().parents[1]
PRESERVED_SOURCE_KIND = "migrated_v160_harness_taxonomy_preserve_skill_content"
LEGACY_SKILL_BASELINE = "main"


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
                "- recommended_route: beacon-gen-refreeze",
                f"- user_decision: {decision}",
                f"- promotion_ref: {promotion_ref}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_minimal_v160_skill_harness_package(root: Path) -> None:
    feature_root = root / "docs" / "beacon" / "v1.6.0" / "features" / "beacon-skill-harness-taxonomy-v160"
    feature_root.mkdir(parents=True, exist_ok=True)
    (feature_root / "truth.md").write_text(
        "\n".join(
            [
                "---",
                "slug: beacon-skill-harness-taxonomy-v160",
                "version: v1.6.0",
                "status: frozen",
                "language: zh",
                "canonical_refs:",
                "  prd: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md",
                "  user_story: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md",
                "  test_case: docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/tests.md",
                "parser_contract: beacon-feature-package-v1",
                "---",
                "",
                "# Beacon Skill Harness Taxonomy v1.6.0",
                "",
                "## 验收标准",
                "",
                "| AC ID | Theme | Description |",
                "|-------|-------|-------------|",
                "| AC-001 | skill-eval | Skill eval benchmark is feature-scoped. |",
                "| AC-002 | qa-scope | QA matrix does not fall back to whole-repo contract tests. |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (feature_root / "tests.md").write_text(
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Assertion |",
                "|-------|-------|-------|-----------|",
                "| AC-001 | TC-001 | contract | Skill eval benchmark artifact exists. |",
                "| AC-002 | TC-002 | integration | Feature-aware QA uses scoped commands. |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (feature_root / "tasks.md").write_text("# Tasks\n\n- [ ] TASK-001 Keep QA scoped.\n", encoding="utf-8")
    (feature_root / "evidence.md").write_text(
        "\n".join(
            [
                "# Evidence",
                "",
                "## Evidence Index",
                "",
                "| Surface | Authority | Canonical Artifact | Status | Route |",
                "|---------|-----------|--------------------|--------|-------|",
                "| qa | qa_verdict | .beacon/qa/features/beacon-skill-harness-taxonomy-v160/matrix.qa9.json | linked | qa |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    state_root = root / ".beacon" / "state"
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "implementation-beacon-skill-harness-taxonomy-v160.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": "run-impl-v160",
                "feature": "beacon-skill-harness-taxonomy-v160",
                "version": "v1.6.0",
                "status": "completed",
                "imported": True,
                "summary_ref": "docs/beacon/v1.6.0/change/beacon-skill-harness-taxonomy-v160.refreeze-summary.md",
                "source_refs": [".beacon/state/skill-eval/benchmarks/example/analysis/analysis.json"],
                "approved_by": "codex-test",
                "changed_files": ["beacon/utils/qa_feature.py"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    tests_dir = root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_v160_skill_harness_taxonomy.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    (tests_dir / "test_v1410_qa_evo_deep_skill_eval.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
    (tests_dir / "test_v147_change_refreeze_one_shot.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")


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
    assert "beacon-pln-source" in skill_dirs
    assert "beacon-gen-implement" in skill_dirs
    assert "beacon-eval-qa" in skill_dirs
    assert "beacon-gov-router" in skill_dirs
    assert all(name.startswith(("beacon-pln-", "beacon-gen-", "beacon-eval-", "beacon-gov-")) for name in skill_dirs)
    for old_name in ("beacon-brainstorm", "beacon-prd", "beacon-user-story", "beacon-test-case", "beacon-implement", "beacon-qa", "beacon-release", "using-beacon"):
        assert old_name not in skill_dirs

    source_driven = (package_root / "beacon-pln-source" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: beacon-pln-source" in source_driven
    assert "Beacon v1.6.0 共享 Preamble" in source_driven
    assert "HARD GATE:" in source_driven
    assert "你正在运行 planner skill" in source_driven
    assert "源码和证据锚定分析" in source_driven
    assert source_driven.index("Beacon v1.6.0 共享 Preamble") < source_driven.index("HARD GATE:")

    metadata = json.loads((package_root / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["version"] == "v1.6.0"
    assert metadata["source_kind"] == PRESERVED_SOURCE_KIND
    assert metadata["content_preservation"]["policy"].startswith("compact harness skill directories preserve full")

    implementation = (package_root / "beacon-gen-implement" / "SKILL.md").read_text(encoding="utf-8")
    assert "PRODUCT.md / DESIGN.md" in implementation
    assert "Beacon v1.6.0 共享 Preamble" in implementation
    assert len(implementation.splitlines()) > 170
    assert "`beacon-eval-qa`" in implementation
    assert "`beacon-qa`" not in "\n".join(line for line in implementation.splitlines() if "来源迁移" not in line and "migrated from" not in line)

    router = (package_root / "beacon-gov-router" / "SKILL.md").read_text(encoding="utf-8")
    assert "`beacon-gen-implement`" in router
    assert "`beacon-eval-release`" in router
    assert "`beacon-implement`" not in "\n".join(line for line in router.splitlines() if "来源迁移" not in line and "migrated from" not in line)

    qa = (package_root / "beacon-eval-qa" / "SKILL.md").read_text(encoding="utf-8")
    assert "`beacon-eval-qa-deep`" in qa
    assert "`beacon-eval-qa-evo-deep`" not in qa


def test_v160_packaged_skills_preserve_legacy_skill_content() -> None:
    pairs = [
        ("beacon-brainstorm", "beacon-pln-brainstorm", "read-only convergence surface"),
        ("beacon-implement", "beacon-gen-implement", "PRODUCT.md / DESIGN.md"),
        ("beacon-qa", "beacon-eval-qa", "QA reads frozen requirement truth"),
        ("beacon-release", "beacon-eval-release", "release readiness"),
        ("using-beacon", "beacon-gov-router", "host-native route constitution"),
    ]
    for old_id, new_id, preserved_phrase in pairs:
        old_text = subprocess.check_output(["git", "show", f"{LEGACY_SKILL_BASELINE}:skills/beacon/{old_id}/SKILL.md"], text=True)
        new_text = (ROOT / "skills" / "beacon" / new_id / "SKILL.md").read_text(encoding="utf-8")
        assert preserved_phrase in new_text
        assert "Beacon v1.6.0 共享 Preamble" in new_text
        assert "HARD GATE:" in new_text
        assert len(new_text.splitlines()) >= len(old_text.splitlines())

    truth_refs = ROOT / "skills" / "beacon" / "beacon-gen-truth" / "references"
    assert (truth_refs / "legacy-beacon-prd.md").exists()
    assert (truth_refs / "legacy-beacon-user-story.md").exists()
    assert (truth_refs / "legacy-beacon-test-case.md").exists()


def test_v160_skill_package_verify_should_fail_for_old_alias_and_missing_gate(tmp_path: Path) -> None:
    setup = _invoke(["skill", "package", "materialize", "--project-root", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert setup.exit_code == 0, setup.stdout
    package_root = Path(json.loads(setup.stdout)["package_root"])

    old_alias = package_root / "beacon-qa"
    old_alias.mkdir()
    (old_alias / "SKILL.md").write_text("---\nname: beacon-qa\n---\n# Old QA\n", encoding="utf-8")
    implementation_skill = package_root / "beacon-gen-implement" / "SKILL.md"
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
    assert "beacon-gen-implement" in checks["v160_shared_preamble_and_hard_gates"]["details"]["gate_errors"]


def test_v160_skill_package_verify_should_fail_for_stale_route_recommendation(tmp_path: Path) -> None:
    setup = _invoke(["skill", "package", "materialize", "--project-root", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert setup.exit_code == 0, setup.stdout
    package_root = Path(json.loads(setup.stdout)["package_root"])

    skill_file = package_root / "beacon-pln-source" / "SKILL.md"
    skill_file.write_text(
        skill_file.read_text(encoding="utf-8") + "\n- route to `beacon-qa` for formal verification.\n",
        encoding="utf-8",
    )

    verify = _invoke(["skill", "package", "verify", "--project-root", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert verify.exit_code == 2, verify.stdout
    payload = json.loads(verify.stdout)
    checks = {item["name"]: item for item in payload["checks"]}
    assert checks["v160_canonical_route_references"]["status"] == "fail"
    errors = checks["v160_canonical_route_references"]["details"]["route_errors"]
    assert "beacon-pln-source" in errors
    assert any("`beacon-qa` should be `beacon-eval-qa`" in item for item in errors["beacon-pln-source"])


def test_v160_feature_qa_matrix_replaces_feature_command_placeholder(tmp_path: Path) -> None:
    _write_minimal_v160_skill_harness_package(tmp_path)
    tests_path = tmp_path / "docs" / "beacon" / "v1.6.0" / "features" / "beacon-skill-harness-taxonomy-v160" / "tests.md"
    tests_path.write_text(
        "\n".join(
            [
                "# Tests",
                "",
                "| AC ID | TC ID | Layer | Command | Assertion |",
                "|-------|-------|-------|---------|-----------|",
                "| AC-014 | TC-014 | contract | `beacon skill package verify-research <feature> --project-root <project-root> --version <version> --json` | Research artifact is feature scoped. |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    plan = build_feature_qa_plan(
        tmp_path,
        version="v1.6.0",
        feature="beacon-skill-harness-taxonomy-v160",
        persist=True,
    )
    matrix_path = materialize_feature_qa_matrix(tmp_path, plan=plan)
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    command = matrix["entries"][0]["command"]

    assert "<feature>" not in command
    assert "<version>" not in command
    assert "<project-root>" not in command
    assert "verify-research beacon-skill-harness-taxonomy-v160" in command
    assert "--version v1.6.0" in command


def test_v160_auto_test_uses_structured_json_assertions_for_cli_evidence(tmp_path: Path) -> None:
    command = (
        "python3 -c 'import json; "
        "print(json.dumps({\"status\":\"pass\",\"ok\":True,\"checks\":[{\"name\":\"a\"},{\"name\":\"b\"}]}))'"
    )
    payload = _run_layer_command(
        layer="contract",
        command=command,
        project_root=tmp_path,
        layer_dir=tmp_path / ".beacon" / "evidence" / "auto-test" / "run-test" / "qa9-tc" / "TC-001",
        run_id="run-test",
        tc_id="TC-001",
        ac_id="AC-001",
    )

    assert payload["status"] == "passed"
    assert payload["assertion_count"] == 2
    assert payload["junit_valid"] is True
    assert (tmp_path / payload["junit_path"]).exists()


def test_v160_negative_promotion_gate_block_counts_as_negative_pass(tmp_path: Path) -> None:
    command = (
        "python3 -c 'import json, sys; "
        "print(json.dumps({\"status\":\"fail\",\"ok\":False,"
        "\"promotion_gate\":{\"status\":\"blocked\",\"allowed\":False,"
        "\"reason_codes\":[\"promotion_ref_missing\"]}})); sys.exit(2)' "
        "# verify-promotion"
    )
    layer_dir = tmp_path / ".beacon" / "evidence" / "auto-test" / "run-test" / "qa9-tc" / "TC-015"
    payload = _run_layer_command(
        layer="contract",
        command=command,
        project_root=tmp_path,
        layer_dir=layer_dir,
        run_id="run-test",
        tc_id="TC-015",
        ac_id="AC-015",
    )
    observed, reason_code = _negative_expected_block_observed(tmp_path, payload)
    updated = _mark_negative_expected_block_passed(
        project_root=tmp_path,
        layer_dir=layer_dir,
        run_payload=payload,
        reason_code=reason_code,
    )

    assert observed is True
    assert reason_code == "negative_promotion_gate_block_observed"
    assert updated["status"] == "passed"
    assert updated["original_exit_code"] == 2
    assert updated["assertion_count"] == 1
    assert updated["junit_valid"] is True


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
    assert payload["recommended_route"].startswith("beacon-pln-")


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


def test_v160_import_evidence_uses_compact_skill_routes(tmp_path: Path) -> None:
    _write_minimal_v160_skill_harness_package(tmp_path)

    result = _invoke(
        [
            "implement",
            "import-evidence",
            "beacon-skill-harness-taxonomy-v160",
            "--project",
            str(tmp_path),
            "--version",
            "v1.6.0",
            "--source-ref",
            "pytest: tests/test_v160_skill_harness_taxonomy.py",
            "--changed-file",
            "beacon/utils/agent_surface.py",
            "--summary-ref",
            "docs/beacon/v1.6.0/execution/implementation-summary-beacon-skill-harness-taxonomy-v160.md",
            "--approved-by",
            "codex-test",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["skill"] == "beacon-gen-implement"
    assert payload["next_route"]["target_surface"] == "beacon-eval-qa"

    marker = json.loads((tmp_path / ".beacon" / "state" / "implementation-beacon-skill-harness-taxonomy-v160.json").read_text(encoding="utf-8"))
    assert marker["skill"] == "beacon-gen-implement"


def test_v160_skill_eval_kit_uses_harness_routes_and_review_artifact(tmp_path: Path) -> None:
    init = _invoke(["skill", "eval-kit", "init", "--project", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert init.exit_code == 0, init.stdout
    init_payload = json.loads(init.stdout)
    assert init_payload["version"] == "v1.6.0"
    cases_payload = json.loads((tmp_path / init_payload["cases_path"]).read_text(encoding="utf-8"))
    routes = {case["expected_route"] for case in cases_payload["cases"]}
    assert "beacon-pln-source" in routes
    assert "beacon-gen-implement" in routes
    assert "beacon-eval-qa" in routes
    assert "beacon-gov-status" in routes
    assert "beacon-qa" not in routes

    run = _invoke(["skill", "eval-kit", "run", "--project", str(tmp_path), "--version", "v1.6.0", "--split", "all", "--json"])
    assert run.exit_code == 0, run.stdout
    run_payload = json.loads(run.stdout)
    assert run_payload["runtime_evidence_only"] is True
    assert run_payload["requirement_truth"] is False

    feedback_path = tmp_path / ".beacon" / "state" / "skill-eval" / "feedback.json"
    feedback_path.write_text(
        json.dumps({"reviews": [{"run_id": run_payload["run_id"], "feedback": "route stable"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    review = _invoke(["skill", "eval-kit", "review", "--project", str(tmp_path), "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["status"] == "pass"
    assert review_payload["review_model"] == "runs_outputs_grading_feedback"
    assert review_payload["runtime_evidence_only"] is True
    assert review_payload["requirement_truth"] is False
    assert review_payload["run_count"] == 1
    assert review_payload["runs"][0]["outputs"]
    assert review_payload["runs"][0]["grading"]["status"] == "pass"
    assert review_payload["feedback"]["reviews"][0]["feedback"] == "route stable"
    html = (tmp_path / review_payload["review_html_path"]).read_text(encoding="utf-8")
    assert "Beacon Skill Eval Review" in html
    assert "beacon-eval-qa" in html


def test_v160_feature_qa_matrix_uses_scoped_commands_for_skill_harness_package(tmp_path: Path) -> None:
    _write_minimal_v160_skill_harness_package(tmp_path)

    plan = build_feature_qa_plan(
        tmp_path,
        version="v1.6.0",
        feature="beacon-skill-harness-taxonomy-v160",
        persist=False,
    )
    matrix_path = materialize_feature_qa_matrix(tmp_path, plan=plan)
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    commands = {str(item["command"]) for item in matrix["entries"]}
    assert commands
    assert all("tests/test_v160_skill_harness_taxonomy.py" in command for command in commands)
    assert all("tests/test_v147_change_refreeze_one_shot.py" in command for command in commands)
    assert all("-k contract" not in command for command in commands)
    assert all("-k integration" not in command for command in commands)


def test_v160_skill_eval_benchmark_outputs_behavior_evidence_for_hard_gate_cases(tmp_path: Path) -> None:
    result = _invoke(["skill", "eval-kit", "benchmark", "--project", str(tmp_path), "--version", "v1.6.0", "--json"])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["runtime_evidence_only"] is True
    assert payload["requirement_truth"] is False
    assert payload["formal_verdict_authority"] is False
    assert payload["release_verdict_authority"] is False

    root = tmp_path / payload["root"]
    assert (root / "eval_metadata").is_dir()
    assert (root / "grading").is_dir()
    assert (root / "benchmark" / "benchmark.json").exists()
    assert (root / "analysis" / "analysis.json").exists()
    assert (root / "analysis" / "analysis.md").exists()

    expected_tc_ids = {"TC-006", "TC-007", "TC-008", "TC-009", "TC-010", "TC-011", "TC-017"}
    expected_behavior_ac_ids = {"AC-006", "AC-007", "AC-008", "AC-009", "AC-010", "AC-011", "AC-017"}
    expected_benchmark_contract_ac_ids = {"AC-018", "AC-019", "AC-020", "AC-021", "AC-022"}
    assert set(payload["covered_tc_ids"]) == expected_tc_ids
    assert set(payload["analysis"]["covered_tc_ids"]) == expected_tc_ids
    assert set(payload["analysis"]["covered_behavior_ac_ids"]) == expected_behavior_ac_ids
    assert set(payload["analysis"]["covered_benchmark_contract_ac_ids"]) == expected_benchmark_contract_ac_ids
    assert set(payload["covered_ac_ids"]) == expected_behavior_ac_ids | expected_benchmark_contract_ac_ids
    assert payload["analysis"]["static_only_ac_ids"] == []
    assert payload["analysis"]["recommended_route"] == "beacon-eval-qa"

    benchmark = json.loads((root / "benchmark" / "benchmark.json").read_text(encoding="utf-8"))
    assert benchmark["configs"]["with_skill"]["pass_rate"] == 1.0
    assert benchmark["configs"]["baseline"]["boundary_violation_count"] >= 1
    assert benchmark["delta"]["boundary_violation_count"] < 0
    assert benchmark["baseline_gate_authority"] is False

    tc011_grading = json.loads((root / "grading" / "tc-011-no-fake-delivery.with_skill.json").read_text(encoding="utf-8"))
    assert tc011_grading["fake_delivery_blocked"] is True
    assert "fake_delivery_closure_blocked" in tc011_grading["reason_codes"]
    assert tc011_grading["fake_delivery_critique"]

    tc017_grading = json.loads((root / "grading" / "tc-017-hard-gate-injection.with_skill.json").read_text(encoding="utf-8"))
    assert tc017_grading["hard_gate_verified"] is True
    assert "hard_gate_behavior_verified" in tc017_grading["reason_codes"]
