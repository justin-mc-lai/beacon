from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.revision_state import freeze_revision_state


runner = CliRunner()
VERSION = "v1.3.12"
FEATURE = "Requirement Deepening Feature"
SLUG = "requirement-deepening-feature"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "user-story").mkdir(parents=True, exist_ok=True)
    (base / "qa" / "test-cases").mkdir(parents=True, exist_ok=True)
    (base / "research").mkdir(parents=True, exist_ok=True)
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
                "- 系统需要围绕 PRD 主动挖掘角色差异、状态转换、边界、异常、恢复与风险。",
                "",
                "## 2. 目标",
                "- 让 operator 和 user 在同一 requirement truth 上补齐决策。",
                "- 当 host 不可用时，必须记录 fallback 和 downgrade 影响。",
                "",
                "## 3. 风险",
                "- 不能新增新的 public stage。",
                "- 不能允许 silent manual patch。",
                "",
                "## 4. Open Questions",
                "- 如何保留 rejected 与 deferred 决策？",
                "- 状态机是否需要覆盖 blocked / downgrade / recovery？",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (base / "research" / f"{SLUG}.md").write_text(
        "\n".join(
            [
                "# Research",
                "",
                "## Business Flow",
                "- operator 审核后 user 才能继续下一步。",
                "",
                "## State Machine",
                "- draft -> reviewing -> approved -> rejected",
                "",
                "## Decision Priority",
                "- fallback 必须被显式记录并带恢复动作。",
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
    tx_id = "tx-v1312-001"

    (root / ".beacon" / "prd" / f"{SLUG}.json").write_text(
        json.dumps({"content": markdown}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.canonical.json").write_text(
        json.dumps(
            {
                "markdown": markdown,
                "transaction": {
                    "transaction_id": tx_id,
                    "source_hash": source_hash,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.compile.json").write_text(
        json.dumps(
            {
                "compile_hash": compile_hash,
                "contract_ok": True,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / ".beacon" / "state" / "prd-transactions" / f"latest-{SLUG}.json").write_text(
        json.dumps(
            {
                "transaction_id": tx_id,
                "source_hash": source_hash,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_v1312_user_story_should_generate_requirement_deepening_artifacts(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    result = _invoke(
        [
            "user-story",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requirement_deepening"]["enabled"] is True
    assert payload["requirement_deepening"]["story_candidate_count"] == 6
    assert payload["requirement_deepening"]["completeness_verdict"] in {"pass", "pass_with_downgrade"}
    assert payload["supplement_task"]["target_artifact"] == "user-story"
    assert payload["re_freeze_transaction"]["refreeze_required"] is True

    machine_root = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "requirement"
    envelope = json.loads((machine_root / f"{SLUG}.envelope.json").read_text(encoding="utf-8"))
    ledger = json.loads((machine_root / f"{SLUG}.candidate-ledger.json").read_text(encoding="utf-8"))
    decision_log = json.loads((machine_root / f"{SLUG}.supplement-decision-log.json").read_text(encoding="utf-8"))

    assert sorted(envelope["dimensions"].keys()) == sorted(
        [
            "actors",
            "boundary_conditions",
            "capability_differences",
            "exceptions",
            "happy_paths",
            "negative_paths",
            "open_questions",
            "recovery_paths",
            "risks",
            "state_machine",
        ]
    )
    assert (envelope.get("research_projection") or {}).get("present") is True
    assert "business_flow" in ((envelope.get("research_projection") or {}).get("sections") or {})
    assert ledger["entries"]
    assert {item["human_decision"] for item in decision_log["entries"]} <= {"accepted", "deferred"}

    story_state = json.loads(
        (tmp_path / "docs" / "beacon" / VERSION / ".machine" / "user-story" / f"{SLUG}.json").read_text(encoding="utf-8")
    )
    active_story = story_state["stories"][0]
    assert active_story["supplement_contract"]["allowed_decisions"] == ["accepted", "rejected", "deferred"]
    assert len(active_story["story_candidates"]) == 6
    supplement_task = json.loads((machine_root / f"{SLUG}.supplement-task.json").read_text(encoding="utf-8"))
    refreeze_transaction = json.loads((machine_root / f"{SLUG}.re-freeze-transaction.json").read_text(encoding="utf-8"))
    assert supplement_task["target_artifact"] == "user-story"
    assert supplement_task["writeback_target"].endswith(f"/user-story/{SLUG}.md")
    assert refreeze_transaction["refreeze_required"] is True
    assert refreeze_transaction["revalidate_required"] is True


def test_v1312_test_case_should_expand_requirement_coverage_and_story_map(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    user_story_result = _invoke(
        [
            "user-story",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert user_story_result.exit_code == 0, user_story_result.stdout

    result = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["requirement_deepening"]["enabled"] is True
    assert payload["requirement_deepening"]["coverage_family_count"] == 9
    assert payload["supplement_task"]["target_artifact"] == "test-case"
    assert payload["re_freeze_transaction"]["refreeze_required"] is True

    qa_root = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa"
    ac_matrix = json.loads((qa_root / f"{SLUG}.ac-test-matrix.json").read_text(encoding="utf-8"))
    qa9_matrix = json.loads((qa_root / f"{SLUG}.qa9-matrix.json").read_text(encoding="utf-8"))
    story_map = json.loads((qa_root / f"{SLUG}.story-scenario-map.json").read_text(encoding="utf-8"))

    assert len(ac_matrix["entries"]) >= 9
    assert len(ac_matrix["requirement_deepening"]["coverage_families"]) == 9
    assert len(qa9_matrix["coverage_families"]) == 9
    assert qa9_matrix["requirement_completeness_verdict"] in {"pass", "pass_with_downgrade"}
    assert len(story_map["requirement_deepening_story_families"]) == 6
    machine_root = tmp_path / "docs" / "beacon" / VERSION / ".machine" / "requirement"
    supplement_task = json.loads((machine_root / f"{SLUG}.supplement-task.json").read_text(encoding="utf-8"))
    refreeze_transaction = json.loads((machine_root / f"{SLUG}.re-freeze-transaction.json").read_text(encoding="utf-8"))
    assert supplement_task["target_artifact"] == "test-case"
    assert supplement_task["writeback_target"].endswith(f"/qa/test-cases/{SLUG}.md")
    assert refreeze_transaction["refreeze_required"] is True


def test_v1312_requirement_package_gate_and_implement_status_should_consume_completeness(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _seed_prd_machine_mirrors(tmp_path)

    user_story_result = _invoke(
        [
            "user-story",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert user_story_result.exit_code == 0, user_story_result.stdout
    test_case_result = _invoke(
        [
            "test-case",
            "create",
            FEATURE,
            "--project",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert test_case_result.exit_code == 0, test_case_result.stdout

    freeze_revision_state(tmp_path, version=VERSION, feature=FEATURE)
    run_id = "run-v1312-implement-001"
    state_dir = tmp_path / ".beacon" / "implement" / run_id
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "state.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run_id": run_id,
                "feature": FEATURE,
                "feature_slug": SLUG,
                "version": VERSION,
                "status": "completed",
                "runner": "native-single",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    assert gate["status"] == "pass"

    status_result = _invoke(
        [
            "implement",
            "status",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--json",
        ]
    )
    assert status_result.exit_code == 0, status_result.stdout
    status_payload = json.loads(status_result.stdout)
    assert status_payload["requirement_completeness"]["completeness_verdict"] in {"pass", "pass_with_downgrade"}
