from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.delivery_kernel import load_delivery_read_model
from beacon.utils.implementation_plan import compile_implementation_plan, load_implementation_plan_progress
from beacon.utils.qa_feature import build_feature_qa_plan, build_feature_qa_precision_artifacts
from beacon.utils.revision_state import freeze_revision_state
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs
from beacon.utils.technical_review_contract import materialize_technical_review_contract


runner = CliRunner()
VERSION = "v1.4.9"
FEATURE = "rules-encyclopedia-admin-closure"
SLUG = FEATURE


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_bmtop_docs(root: Path, *, qa_matrix: str | None = None) -> None:
    base = root / "docs" / "beacon" / VERSION
    _write(base / "SUMMARY.md", "# v1.4.9\n")
    _write(base / "execution" / "index.md", "# Execution Index\n")
    _write(
        base / "prd" / f"{SLUG}.md",
        "# PRD\n\n- AC-001: implementation evidence is bound.\n- AC-002: markdown matrix compiles.\n- AC-003: Go + UniApp runner profile is used.\n",
    )
    _write(
        base / "user-story" / f"{SLUG}.md",
        "# User Story\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | evidence | Implementation evidence marker exists. |\n"
        "| AC-002 | matrix | Markdown QA rows compile without fallback. |\n"
        "| AC-003 | runner | Go + UniApp commands are resolved. |\n",
    )
    _write(
        base / "research" / f"{SLUG}.md",
        "# Research\n\n"
        "## Decision Priority\n"
        "1. Markdown QA truth beats generated fallback.\n",
    )
    _write(
        base / "qa" / "test-cases" / f"{SLUG}.md",
        qa_matrix
        if qa_matrix is not None
        else "# Test Cases\n\n"
        "## Coverage Matrix\n\n"
        "| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| AC-001 | TC-RPQA-001 | contract | `python3 -c \"print('BEACON_ASSERTIONS: 1')\"` | marker written | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-001.json` |\n"
        "| AC-002 | TC-RPQA-002 | regression | `python3 -c \"print('BEACON_ASSERTIONS: 1')\"` | markdown matrix only | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-002.json` |\n"
        "| AC-003 | TC-RPQA-003 | integration | `go test ./...` | Go + UniApp runner profile | `.beacon/evidence/test-results/rules-encyclopedia-admin-closure/TC-RPQA-003.json` |\n",
    )


def test_markdown_matrix_compiles_without_fallback(tmp_path: Path) -> None:
    _seed_bmtop_docs(tmp_path)

    result = _invoke(["test-case", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout

    matrix_path = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json"
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    entries = payload["entries"]
    assert [item["tc_id"] for item in entries] == ["TC-RPQA-001", "TC-RPQA-002", "TC-RPQA-003"]
    assert "AC-004" not in {item["ac_id"] for item in entries}
    assert payload["markdown_matrix_contract"]["truth_mode"] == "markdown"
    assert payload["markdown_matrix_contract"]["enrichment_disabled"] is True
    assert not any("fallback" in str(item.get("source") or "").lower() for item in entries)


def test_markdown_matrix_parser_fail_closed(tmp_path: Path) -> None:
    _seed_bmtop_docs(
        tmp_path,
        qa_matrix=(
            "# Test Cases\n\n"
            "## Coverage Matrix\n\n"
            "| AC ID | Missing TC | Layer |\n"
            "| --- | --- | --- |\n"
            "| AC-001 | no-test-id | contract |\n"
        ),
    )

    result = _invoke(["test-case", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "markdown_matrix_projection_gap"
    diagnostics_path = tmp_path / payload["diagnostics_path"]
    assert diagnostics_path.exists()
    assert not (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json").exists()


def test_import_evidence_marker_written(tmp_path: Path) -> None:
    _seed_bmtop_docs(tmp_path)
    sync_story_state_from_docs(tmp_path, version=VERSION, feature=FEATURE)
    freeze_story_state(tmp_path, version=VERSION, feature=FEATURE)
    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    materialize_technical_review_contract(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
        revision_id="R1",
        force_refresh=True,
        contract_overrides={
            "review_status": "approved",
            "approved_by": "codex-test",
            "reviewed_at": "2026-05-23T00:00:00Z",
            "source": "human_approved",
        },
    )
    plan_code, plan_payload = compile_implementation_plan(tmp_path, version=VERSION, feature=FEATURE)
    assert plan_code == 0, plan_payload

    result = _invoke(
        [
            "implement",
            "import-evidence",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--source-ref",
            "docs/beacon/v1.4.9/execution/implementation-summary-rules-encyclopedia-admin-closure.md",
            "--changed-file",
            "backend/rules/handler.go",
            "--service-dir",
            "frontend/src/pages/rules",
            "--summary-ref",
            "docs/beacon/v1.4.9/execution/implementation-summary-rules-encyclopedia-admin-closure.md",
            "--approved-by",
            "codex-test",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["imported"] is True
    assert payload["prompt_boundary"]["status"] == "pass"
    assert payload["prompt_boundary"]["classification"] == "in_scope_implementation"
    assert payload["prompt_boundary"]["surface"] == "import-evidence"

    marker = json.loads((tmp_path / ".beacon" / "state" / f"implementation-{SLUG}.json").read_text(encoding="utf-8"))
    assert marker["summary_ref"].endswith("implementation-summary-rules-encyclopedia-admin-closure.md")
    assert marker["approved_by"] == "codex-test"
    assert "backend/rules/handler.go" in marker["changed_files"]
    assert "frontend/src/pages/rules" in marker["service_dirs"]
    assert marker["prompt_boundary"]["status"] == "pass"
    run_state = json.loads((tmp_path / ".beacon" / "implement" / payload["run_id"] / "state.json").read_text(encoding="utf-8"))
    assert run_state["status"] == "completed"
    assert run_state["mode"] == "import-evidence"
    assert run_state["prompt_boundary"]["status"] == "pass"
    read_model = load_delivery_read_model(tmp_path, version=VERSION, feature=FEATURE)
    assert read_model["implement"]["prompt_boundary"]["status"] == "pass"
    assert read_model["implement"]["prompt_boundary"]["surface"] == "import-evidence"
    progress = load_implementation_plan_progress(tmp_path, version=VERSION, feature=FEATURE)
    assert progress["status"] == "completed"
    assert progress["counts"]["completed"] == progress["counts"]["total"]


def test_implementation_evidence_marker_written(tmp_path: Path) -> None:
    test_import_evidence_marker_written(tmp_path)


def test_qa_blocks_when_marker_missing(tmp_path: Path) -> None:
    _seed_bmtop_docs(tmp_path)
    create = _invoke(["test-case", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout

    plan = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)
    assert plan["status"] == "blocked"
    assert "evidence_binding_missing" in plan["reason_codes"]
    assert plan["implementation_evidence_gate"]["blocked"] is True
    assert plan["qa_outcome_taxonomy"]["category"] == "admission_blocker"


def test_go_uniapp_runner_profile(tmp_path: Path) -> None:
    _seed_bmtop_docs(tmp_path)

    result = _invoke(["profile", "create", "bmtop", "bmtop-go-uniapp", "--example", "go-uniapp", "--project", str(tmp_path), "--json"])
    assert result.exit_code == 0, result.stdout
    show = _invoke(["profile", "show", "bmtop-go-uniapp", "--project", str(tmp_path), "--json"])
    assert show.exit_code == 0, show.stdout
    payload = json.loads(show.stdout)
    commands = payload["profile"]["qa_layer_commands"]
    assert "go test ./..." in commands["integration"]
    assert "npm run type-check --if-present" == commands["smoke"]
    assert "npm run build:mp-weixin --if-present" == commands["functional"]
    assert "npm run test:routes --if-present" == commands["regression"]


def test_admission_blocker_taxonomy(tmp_path: Path) -> None:
    _seed_bmtop_docs(tmp_path)
    create = _invoke(["test-case", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout
    import_result = _invoke(
        [
            "implement",
            "import-evidence",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--source-ref",
            "manual-implementation",
            "--changed-file",
            "backend/rules/handler.go",
            "--summary-ref",
            "docs/beacon/v1.4.9/execution/implementation-summary.md",
            "--approved-by",
            "codex-test",
            "--json",
        ]
    )
    assert import_result.exit_code == 0, import_result.stdout
    plan = build_feature_qa_plan(tmp_path, version=VERSION, feature=FEATURE, persist=False)
    per_item_results = [
        {
            "tc_id": "TC-RPQA-003",
            "source_tc_id": "TC-RPQA-003",
            "ac_id": "AC-003",
            "status": "blocked",
            "layer_status": "failed",
            "stderr": "testcontainers mysql startup timeout: connection refused",
            "evidence_ref": [],
        }
    ]
    _, _, scorecard, _, _ = build_feature_qa_precision_artifacts(
        tmp_path,
        feature=FEATURE,
        run_id="run-taxonomy",
        plan=plan,
        per_item_results=per_item_results,
        project_profile_gate={},
        qa_status={"status": "blocked", "qa9": {"tc_results": per_item_results}},
        exhaustiveness={"status": "passed"},
    )
    taxonomy = scorecard["qa_outcome_taxonomy"]
    assert taxonomy["primary_class"] == "environment_blocked"
    assert "environment_blocked" in scorecard["stop_reasons"]


def test_bmtop_fixture_prevents_false_closure() -> None:
    fixture_root = Path(__file__).resolve().parent / "fixtures" / "bmtop" / "rules-encyclopedia-admin-closure"
    assert (fixture_root / "prd.md").exists()
    assert (fixture_root / "user-story.md").exists()
    assert (fixture_root / "qa-test-cases.md").exists()
    fallback = json.loads((fixture_root / "ac-test-matrix-fallback.json").read_text(encoding="utf-8"))
    assert fallback["entries"][0]["assertion"] == "placeholder acceptance fallback"
