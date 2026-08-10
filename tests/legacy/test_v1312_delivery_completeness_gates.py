from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.revision_state import freeze_revision_state


runner = CliRunner()
VERSION = "v1.3.12"
FEATURE = "Delivery Completeness Feature"
SLUG = "delivery-completeness-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "release").mkdir(parents=True, exist_ok=True)
    (base / "source-architecture").mkdir(parents=True, exist_ok=True)
    (base / ".machine" / "prd").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "prd").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "state" / "prd-transactions").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "docs" / "beacon" / "global-boundaries.md").write_text("# Global Boundaries\n", encoding="utf-8")
    (base / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n", encoding="utf-8")
    (base / "execution" / "boundaries.md").write_text("# Boundaries\n", encoding="utf-8")
    (base / "execution" / "project-skill-qa-evolution-blueprint.md").write_text("# Skill Blueprint\n", encoding="utf-8")
    (base / "source-architecture" / "index.md").write_text("# Source Architecture\n", encoding="utf-8")
    (base / "release" / f"{VERSION}.md").write_text("# Release\n", encoding="utf-8")
    (base / "prd" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# PRD",
                "",
                "## 1. 问题",
                "- 需要把 requirement completeness 接入 prototype / qa / release。",
                "",
                "## 2. 目标",
                "- prototype/qa/release 都应读取同一份 completeness verdict。",
                "- 当 host downgrade 时必须显式可审计。",
                "",
                "## 3. 风险",
                "- 不允许 silent manual patch。",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _seed_prd_machine_mirrors(root: Path) -> None:
    prd_path = root / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md"
    markdown_raw = prd_path.read_text(encoding="utf-8")
    markdown = markdown_raw.strip()
    source_hash = "sha256:" + hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    compile_hash = hashlib.sha256(markdown_raw.encode("utf-8")).hexdigest()
    tx_id = "tx-v1312-delivery-001"
    (root / ".beacon" / "prd" / f"{SLUG}.json").write_text(
        json.dumps({"content": markdown}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.canonical.json").write_text(
        json.dumps({"markdown": markdown, "transaction": {"transaction_id": tx_id, "source_hash": source_hash}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.compile.json").write_text(
        json.dumps({"compile_hash": compile_hash, "contract_ok": True}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "prd-transactions" / f"latest-{SLUG}.json").write_text(
        json.dumps({"transaction_id": tx_id, "source_hash": source_hash}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _prepare_requirement_package(root: Path) -> None:
    _seed_docs(root)
    _seed_prd_machine_mirrors(root)
    result = _invoke(
        [
            "user-story",
            "create",
            FEATURE,
            "--project",
            str(root),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    result = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(root),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    freeze_revision_state(root, version=VERSION, feature=FEATURE)


def _force_completeness_blocked(root: Path) -> None:
    path = root / "docs" / "beacon" / VERSION / ".machine" / "requirement" / f"{SLUG}.completeness.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["completeness_verdict"] = "blocked"
    payload["unresolved_gap_count"] = 1
    payload["high_risk_unresolved_categories"] = ["critical-coverage-family-missing"]
    payload["readiness"] = {
        "freeze_ready": False,
        "prototype_ready": False,
        "implement_ready": False,
        "release_ready": False,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_v1312_prototype_should_block_when_requirement_completeness_is_blocked(tmp_path: Path) -> None:
    _prepare_requirement_package(tmp_path)
    _force_completeness_blocked(tmp_path)

    result = _invoke(
        [
            "prototype",
            "plan",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason_code"] == "requirement_completeness_blocked"
    assert payload["requirement_completeness_gate"]["stage_gates"]["stage_admission"]["status"] == "blocked"
    assert payload["requirement_completeness_gate"]["human_loop_handoff"]["action"] == "human_review"

    status_result = _invoke(
        [
            "prototype",
            "status",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert status_payload["requirement_completeness_gate"]["status"] == "blocked"
    assert status_payload["gate_ready"] is False


def test_v1312_qa_should_block_when_requirement_completeness_is_blocked(tmp_path: Path) -> None:
    _prepare_requirement_package(tmp_path)
    _force_completeness_blocked(tmp_path)

    result = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 2, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "requirement_completeness_blocked" in payload["reason_codes"]
    assert payload["requirement_completeness_gate"]["status"] == "blocked"


def test_v1312_release_scorecard_should_surface_requirement_completeness_and_disable_release_ready(tmp_path: Path) -> None:
    _prepare_requirement_package(tmp_path)
    _force_completeness_blocked(tmp_path)

    payload = build_release_scorecard(tmp_path, version=VERSION)
    assert payload["requirement_completeness"]["status"] == "blocked"
    assert payload["requirement_completeness"]["reason_code"] == "requirement_completeness_blocked"
    assert payload["requirement_completeness"]["stage_gates"]["unresolved_gap_governance"]["status"] == "blocked"
    assert payload["release_ready"] is False
