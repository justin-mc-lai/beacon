from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon import app
from beacon.utils import release_scorecard as release_scorecard_module
from beacon.utils.feature_package import materialize_feature_package, validate_feature_package


VERSION = "v1.5.0"
FEATURE = "Beacon v1.5.0 Parallel Plan B Document Capability"
SLUG = "beacon-v1.5.0-parallel-plan-b-document-capability"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# Beacon Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Beacon v1.5.0\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "\n".join(
            [
                "# PRD",
                "",
                "## Acceptance Criteria",
                "",
                "- AC-001: v1.5.0 supports `features/<slug>/{truth,tests,tasks,evidence}.md` as a parallel package.",
                "- AC-011: `truth.md` includes YAML frontmatter as parallel metadata.",
                "- AC-012: `tasks.md` includes checkbox rows without gate bypass.",
                "- AC-013: CLI validation reads package markdown deterministically.",
                "- AC-014: LLM-authored markdown advances only after CLI validation.",
                "- AC-015: `evidence.md` is not gate truth.",
                "- AC-016: Skills provide quick templates.",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "\n".join(
            [
                "# User Story",
                "",
                "## Acceptance Criteria",
                "",
                "| AC ID | Theme | Description |",
                "|-------|-------|-------------|",
                "| AC-001 | parallel-package | v1.5.0 supports feature package files. |",
                "| AC-011 | truth-frontmatter | `truth.md` includes YAML frontmatter as parallel metadata. |",
                "| AC-012 | checkbox-ledger | `tasks.md` includes checkbox rows without gate bypass. |",
                "| AC-013 | deterministic-parser | CLI validation reads package markdown deterministically. |",
                "| AC-014 | llm-write-boundary | LLM-authored markdown advances only after CLI validation. |",
                "| AC-015 | evidence-no-gate-truth | `evidence.md` is not gate truth. |",
                "| AC-016 | skill-template-examples | Skills provide quick templates. |",
            ]
        )
        + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "\n".join(
            [
                "# Test Cases",
                "",
                "## Coverage Matrix",
                "",
                "| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |",
                "|-------|-------|-------|-----------------|-----------|---------------|",
                "| AC-001 | TC-001 | integration | beacon materialize-feature-package | Creates four package files. | features/<slug>/ |",
                "| AC-011 | TC-011 | integration | validate truth.md | Frontmatter is parallel metadata. | truth.md |",
                "| AC-012 | TC-012 | integration | validate tasks.md | Checkbox rows do not bypass gates. | tasks.md |",
                "| AC-013 | TC-013 | unit | validate package | Diagnostics are deterministic. | .machine/requirement/ |",
                "| AC-014 | TC-014 | e2e | validate LLM markdown | State advances only after validation. | .machine/ |",
                "| AC-015 | TC-015 | unit | validate evidence.md | Gate truth field is rejected. | evidence.md |",
                "| AC-016 | TC-016 | integration | render skill templates | Templates are parser-compatible. | skills/ |",
            ]
        )
        + "\n",
    )


def test_materialize_feature_package_should_create_parallel_package_without_machine_replacement(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    payload = materialize_feature_package(tmp_path, version=VERSION, feature=FEATURE)

    package_dir = tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG
    assert payload["status"] == "materialized"
    assert (package_dir / "truth.md").exists()
    assert (package_dir / "tests.md").exists()
    assert (package_dir / "tasks.md").exists()
    assert (package_dir / "evidence.md").exists()
    assert (tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md").exists()
    assert payload["validation"]["status"] == "pass"
    assert payload["validation"]["truth_frontmatter"]["parser_contract"] == "beacon-feature-package-v1"
    assert payload["validation"]["gate_authority"] == "canonical_surfaces_preserved"


def test_validate_feature_package_should_reject_gate_truth_and_malformed_checkbox(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    materialize_feature_package(tmp_path, version=VERSION, feature=FEATURE)
    package_dir = tmp_path / "docs" / "beacon" / VERSION / "features" / SLUG
    (package_dir / "tasks.md").write_text("# Tasks\n\n- [done] TASK-001 invalid\n", encoding="utf-8")
    (package_dir / "evidence.md").write_text(
        "# Evidence\n\nfinal_verdict: pass\n\n| Surface | Authority | Canonical Artifact | Status | Route |\n"
        "|---------|-----------|--------------------|--------|-------|\n"
        "| qa | qa_verdict | docs/beacon/v1.5.0/.machine/qa/x.json | linked | qa |\n",
        encoding="utf-8",
    )

    payload = validate_feature_package(tmp_path, version=VERSION, feature=FEATURE, write_report=True)
    codes = {item["code"] for item in payload["diagnostics"]}

    assert payload["status"] == "blocked"
    assert payload["checkbox_gate_bypass"] is False
    assert payload["evidence_gate_truth"] is False
    assert "malformed_checkbox: line 3" in codes
    assert "checkbox_ledger_missing" in codes
    assert "evidence_forbidden_gate_truth_field:final_verdict" in codes
    assert (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "requirement" / "feature-package-validation.json").exists()


def test_cli_materialize_and_validate_feature_package_should_emit_json(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["materialize-feature-package", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["validation"]["status"] == "pass"

    validate_result = runner.invoke(
        app,
        ["validate-feature-package", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"],
    )
    assert validate_result.exit_code == 0, validate_result.stdout
    validate_payload = json.loads(validate_result.stdout)
    assert validate_payload["status"] == "pass"
    assert validate_payload["report_path"] == f"docs/beacon/{VERSION}/.machine/requirement/feature-package-validation.json"


def test_legacy_cli_surfaces_should_remain_available() -> None:
    runner = CliRunner()

    for command in ("prd", "user-story", "test-case", "prototype"):
        result = runner.invoke(app, [command, "--help"])
        assert result.exit_code == 0, command


def test_skill_templates_should_include_v150_package_examples() -> None:
    root = Path(__file__).resolve().parents[1]
    for rel in (
        "skills/beacon/beacon-prd/SKILL.md",
        "skills/beacon/beacon-test-case/SKILL.md",
        "skills/beacon/beacon-implement/SKILL.md",
        "skills/beacon/beacon-qa/SKILL.md",
    ):
        content = (root / rel).read_text(encoding="utf-8")
        assert "v1.5.0 Feature Package Quick Template" in content

    assert "parser_contract: beacon-feature-package-v1" in (root / "skills/beacon/beacon-prd/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "TASK-001" in (root / "skills/beacon/beacon-implement/SKILL.md").read_text(encoding="utf-8")
    assert "support_advisory" in (root / "skills/beacon/beacon-qa/SKILL.md").read_text(encoding="utf-8")


def test_current_v150_feature_package_validation_should_pass() -> None:
    root = Path(__file__).resolve().parents[1]

    payload = validate_feature_package(root, version=VERSION, feature=SLUG, write_report=True)

    assert payload["status"] == "pass"
    assert payload["gate_authority"] == "canonical_surfaces_preserved"
    assert payload["checkbox_gate_bypass"] is False
    assert payload["evidence_gate_truth"] is False
    assert payload["truth_frontmatter"]["parser_contract"] == "beacon-feature-package-v1"
    assert payload["truth_frontmatter"]["canonical_refs"]["prd"].endswith(f"/prd/{SLUG}.md")
    assert payload["truth_frontmatter"]["canonical_refs"]["user_story"].endswith(f"/user-story/{SLUG}.md")
    assert payload["truth_frontmatter"]["canonical_refs"]["test_case"].endswith(f"/qa/test-cases/{SLUG}.md")


def test_current_v150_package_should_keep_evidence_index_read_model_only() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "docs" / "beacon" / VERSION / "features" / SLUG / "evidence.md"
    content = evidence.read_text(encoding="utf-8")

    assert "| Surface | Authority | Canonical Artifact | Status | Route |" in content
    assert "final_verdict:" not in content
    assert "gate_truth:" not in content
    assert "release_ready:" not in content
    assert f"docs/beacon/{VERSION}/.machine/qa/{SLUG}.qa9-matrix.json" in content


def test_current_v150_package_should_keep_support_surfaces_advisory() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "docs" / "beacon" / VERSION / "features" / SLUG / "evidence.md"
    content = evidence.read_text(encoding="utf-8")

    assert "support_advisory" in content
    assert "| beacon-deep | support_advisory |" in content
    assert "| beacon-ceo-review | support_advisory |" in content
    assert "qa_verdict" in content
    assert "release_verdict" in content


def test_current_v150_materials_should_preserve_canonical_chain() -> None:
    root = Path(__file__).resolve().parents[1]
    base = root / "docs" / "beacon" / VERSION

    assert (base / "prd" / f"{SLUG}.md").exists()
    assert (base / "user-story" / f"{SLUG}.md").exists()
    assert (base / "qa" / "test-cases" / f"{SLUG}.md").exists()
    assert (base / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").exists()
    assert (base / ".machine" / "requirement" / "feature-package-validation.json").exists()

    summary = (base / "SUMMARY.md").read_text(encoding="utf-8")
    boundaries = (base / "execution" / "boundaries.md").read_text(encoding="utf-8")
    global_boundaries = (root / "docs" / "beacon" / "global-boundaries.md").read_text(encoding="utf-8")

    assert "不退役现有" in summary
    assert "parallel metadata" in boundaries
    assert "不能绕过 implement、QA 或 release gate" in boundaries
    assert "Beacon 可以有多个读面，但只能有一个提交真值" in global_boundaries


def test_current_v150_release_authority_should_remain_on_canonical_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]
    release_doc = root / "docs" / "beacon" / VERSION / "release" / f"{VERSION}.md"
    checklist = root / "docs" / "beacon" / VERSION / "release" / f"checklist-{VERSION}.md"
    evidence = root / "docs" / "beacon" / VERSION / "features" / SLUG / "evidence.md"
    cli_help = CliRunner().invoke(app, ["validate-feature-package", "--help"])

    assert cli_help.exit_code == 0
    assert "validate-feature-package" in cli_help.stdout
    assert "Release readiness is not derived from `features/<slug>/evidence.md`" in release_doc.read_text(encoding="utf-8")
    assert "`evidence.md` remains an index/read model" in checklist.read_text(encoding="utf-8")
    assert "release_verdict" in evidence.read_text(encoding="utf-8")


def test_v150_advisory_deep_loop_should_not_replace_release_gate_truth(tmp_path: Path) -> None:
    feature = "Beacon v1.5.0 Parallel Plan B Document Capability"
    _write(
        tmp_path,
        "docs/beacon/global-boundaries.md",
        "Deep is support advisory and cannot replace truth, QA, or release gate.\n",
    )
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "Deep remains support advisory. Release readiness stays on canonical release surfaces and is not gate truth here.\n",
    )
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/features/{SLUG}/evidence.md",
        "| Surface | Authority | Canonical Artifact | Status | Route |\n"
        "| beacon-deep | support_advisory | docs/beacon/v1.5.0/research/x.md | indexed | change |\n",
    )

    bridged = release_scorecard_module._apply_v150_support_advisory_deep_boundary(
        {"status": "blocked", "blocked": True, "reason_codes": ["deep_loop_unclosed"]},
        project_root=tmp_path,
        version=VERSION,
        feature=feature,
    )
    still_blocked = release_scorecard_module._apply_v150_support_advisory_deep_boundary(
        {
            "status": "blocked",
            "blocked": True,
            "reason_codes": ["deep_loop_unclosed", "deep_release_blocking_finding_open"],
        },
        project_root=tmp_path,
        version=VERSION,
        feature=feature,
    )

    assert bridged["blocked"] is False
    assert bridged["support_advisory_deep_boundary"]["reason_code"] == "deep_support_advisory_not_release_gate_truth"
    assert still_blocked["blocked"] is True
    assert "deep_release_blocking_finding_open" in still_blocked["reason_codes"]
