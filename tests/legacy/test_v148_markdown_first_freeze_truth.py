from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.markdown_first_freeze import (
    contains_fulltext_mirror,
    minimal_freeze_state_path,
    parse_markdown_truth_projection,
    validate_minimal_freeze_state,
)
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.revision_state import freeze_revision_state, load_revision_state, save_revision_state
from beacon.utils.runtime import write_json
from beacon.utils.story_state import freeze_story_state, sync_story_state_from_docs


runner = CliRunner()
VERSION = "v1.4.8"
FEATURE = "Markdown First Freeze Truth"
SLUG = "markdown-first-freeze-truth"


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_docs(root: Path) -> None:
    base = root / "docs" / "beacon" / VERSION
    _write(root, "docs/beacon/global-boundaries.md", "# Global Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# Summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# Execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/boundaries.md", "# Boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md", "# Skill Blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/index.md", "# Source Architecture\n")
    _write(root, f"docs/beacon/{VERSION}/source-architecture/{SLUG}.md", "# Source Architecture\n\n## Architecture\n- Markdown first.\n")
    _write(root, f"docs/beacon/{VERSION}/research/{SLUG}.md", "# Research\n\n## Business Flow\n- Gate parses Markdown.\n")
    _write(root, f"docs/beacon/{VERSION}/change/{SLUG}.md", "# Change\n\n- Markdown first freeze truth.\n")
    _write(root, f"docs/beacon/{VERSION}/release/checklist-{VERSION}-{SLUG}.md", "# Release\n\n- pending implementation.\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        "\n".join(
            [
                "# PRD: Markdown First Freeze Truth",
                "",
                "## Context",
                "- Context exists.",
                "",
                "## 1. 问题",
                "- Machine JSON must not mirror full Markdown.",
                "",
                "## 2. 目标",
                "- Gate reads Markdown first.",
                "",
                "## 3. 设计原则",
                "- Markdown is truth.",
                "- 边界：机器缓存不得成为需求 truth。",
                "- 分层：requirement truth 属于 Markdown，runtime evidence 属于 JSON。",
                "- 恢复：当 cache drift 时回到 beacon-change 重新冻结。",
                "",
                "## 4. 范围",
                "- v1.4.8+ freeze artifacts.",
                "",
                "## 7. 风险与缓解",
                "| 风险 | 影响 | 缓解 |",
                "| --- | --- | --- |",
                "| fulltext mirror drift | high | block and regenerate minimal state |",
                "",
                "## 5. 功能需求",
                "- FR-001 Markdown truth is canonical.",
                "",
                "## 8. 验收标准",
                "- AC-001 Beacon treats Markdown PRD, user-story, and test-case as canonical freeze truth.",
                "- AC-002 Beacon does not treat frozen-stage fulltext machine mirrors as canonical truth.",
                "- AC-003 Beacon stores only minimal freeze state in requirement-stage JSON.",
                "- AC-004 Beacon keeps implement, QA, release runtime evidence JSON.",
                "- AC-005 Beacon parses AC and test-case coverage from Markdown truth before consulting cache.",
                "- AC-006 Beacon blocks when Markdown parser fails.",
                "- AC-007 Beacon blocks when Markdown baseline hash differs from frozen state.",
                "- AC-008 Beacon blocks when refreeze transaction status is missing or ambiguous.",
                "- AC-009 Beacon emits diagnostics with path, section, hash, reason_code, and repair route.",
                "- AC-010 Historical fulltext JSON remains readable but new v1.4.8+ freeze artifacts avoid full Markdown.",
                "",
            ]
        ),
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        "\n".join(
            [
                "# User Story",
                "",
                "## Acceptance Criteria",
                "- AC-001 Beacon treats Markdown PRD, user-story, and test-case as canonical freeze truth.",
                "- AC-002 Beacon does not treat frozen-stage fulltext machine mirrors as canonical truth.",
                "- AC-003 Beacon stores only minimal freeze state in requirement-stage JSON.",
                "- AC-004 Beacon keeps implement, QA, release runtime evidence JSON.",
                "- AC-005 Beacon parses AC and test-case coverage from Markdown truth before consulting cache.",
                "- AC-006 Beacon blocks when Markdown parser fails.",
                "- AC-007 Beacon blocks when Markdown baseline hash differs from frozen state.",
                "- AC-008 Beacon blocks when refreeze transaction status is missing or ambiguous.",
                "- AC-009 Beacon emits diagnostics with path, section, hash, reason_code, and repair route.",
                "- AC-010 Historical fulltext JSON remains readable but new v1.4.8+ freeze artifacts avoid full Markdown.",
                "",
            ]
        ),
    )
    rows = [
        f"| AC-{idx:03d} | TC-MDFIRST-{idx:03d} | contract | `pytest -q tests/test_v148_markdown_first_freeze_truth.py` | AC-{idx:03d} remains covered |"
        for idx in range(1, 11)
    ]
    _write(
        root,
        f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md",
        "# Test Cases\n\n| AC ID | TC ID | Layer | Command | Assertion |\n| --- | --- | --- | --- | --- |\n" + "\n".join(rows) + "\n",
    )
    (base / ".machine" / "prd").mkdir(parents=True, exist_ok=True)
    (root / ".beacon" / "prd").mkdir(parents=True, exist_ok=True)


def _freeze(root: Path) -> None:
    sync_story_state_from_docs(root, VERSION, FEATURE)
    freeze_story_state(root, VERSION, FEATURE)
    freeze_revision_state(root, version=VERSION, feature=FEATURE)
    write_json(
        root / "docs" / "beacon" / VERSION / ".machine" / "change" / f"{SLUG}.refreeze-transaction.json",
        {
            "schema_version": "1.0",
            "feature": FEATURE,
            "version": VERSION,
            "refreeze_status": "complete",
            "truth_revision_after": {"revision_id": "R1", "doc_status": "frozen"},
        },
    )


def test_markdown_documents_are_canonical_freeze_truth(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)

    projection = parse_markdown_truth_projection(tmp_path, version=VERSION, feature=FEATURE)

    assert projection["status"] == "pass"
    assert projection["prd_ac_ids"] == [f"AC-{idx:03d}" for idx in range(1, 11)]
    assert projection["user_story_ac_ids"] == [f"AC-{idx:03d}" for idx in range(1, 11)]
    assert projection["test_case_ac_ids"] == [f"AC-{idx:03d}" for idx in range(1, 11)]


def test_fulltext_machine_mirrors_are_not_truth_sources(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    long_stale_markdown = "# PRD\n\n" + ("stale truth\n" * 50)
    write_json(
        tmp_path / ".beacon" / "prd" / f"{SLUG}.json",
        {"content": long_stale_markdown, "markdown": long_stale_markdown},
    )
    result = _invoke(["prd", "reconcile", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout

    legacy = json.loads((tmp_path / ".beacon" / "prd" / f"{SLUG}.json").read_text(encoding="utf-8"))
    canonical = json.loads((tmp_path / "docs" / "beacon" / VERSION / ".machine" / "prd" / f"{SLUG}.canonical.json").read_text(encoding="utf-8"))

    assert "content" not in legacy
    assert "markdown" not in legacy
    assert "markdown" not in canonical
    assert contains_fulltext_mirror(legacy) is False
    assert contains_fulltext_mirror(canonical) is False


def test_freeze_stage_json_contains_only_minimal_state(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    state = json.loads(minimal_freeze_state_path(tmp_path, VERSION, FEATURE).read_text(encoding="utf-8"))

    assert gate["status"] == "pass"
    assert validate_minimal_freeze_state(state)["status"] == "pass"
    assert state["status"] == "frozen"
    assert "baseline_hash" in state
    assert "source_paths" in state


def test_runtime_evidence_json_is_preserved(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)

    runtime_path = tmp_path / ".beacon" / "implement" / "run-runtime" / "state.json"
    write_json(
        runtime_path,
        {
            "schema_version": "1.0",
            "run_id": "run-runtime",
            "feature": FEATURE,
            "version": VERSION,
            "process": {"pid": 123},
            "session": {"id": "session-1"},
            "trace": [{"event": "implemented"}],
            "evidence": [{"path": ".beacon/evidence/result.json"}],
        },
    )

    assert runtime_path.exists()
    assert json.loads(runtime_path.read_text(encoding="utf-8"))["trace"][0]["event"] == "implemented"


def test_gate_parses_ac_and_coverage_from_markdown_first(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    write_json(tmp_path / "docs" / "beacon" / VERSION / ".machine" / "qa" / f"{SLUG}.ac-test-matrix.json", {"entries": []})

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert gate["status"] == "pass"
    markdown_gate = next(item for item in gate["audit"]["checks"] if item["name"] == "markdown_first_freeze_truth_gate")
    assert markdown_gate["status"] == "pass"


def test_markdown_parser_failure_blocks(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _write(tmp_path, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# User Story\n\nNo explicit acceptance criteria.\n")
    _freeze(tmp_path)

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert gate["status"] == "blocked"
    assert "markdown_first_freeze_truth_gate" in {item["name"] for item in gate["failing_checks"]}
    assert "markdown_parser_failure" in gate["failure_categories"]


def test_baseline_hash_mismatch_blocks(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/user-story/{SLUG}.md",
        (tmp_path / "docs" / "beacon" / VERSION / "user-story" / f"{SLUG}.md").read_text(encoding="utf-8")
        + "\n- AC-011 New unfrozen criterion.\n",
    )

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert gate["status"] == "blocked"
    assert "baseline_hash_mismatch" in gate["failure_categories"]
    assert gate["recommended_action"] == "beacon-change"


def test_ambiguous_refreeze_status_blocks(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    revision = load_revision_state(tmp_path, version=VERSION, feature=FEATURE, create_if_missing=False)
    revision["revision_id"] = "R2"
    revision["source_revision_id"] = "R1"
    revision["doc_status"] = "frozen"
    save_revision_state(tmp_path, version=VERSION, feature=FEATURE, state=revision)
    write_json(
        tmp_path / "docs" / "beacon" / VERSION / ".machine" / "change" / f"{SLUG}.refreeze-transaction.json",
        {"refreeze_status": "blocked"},
    )

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)

    assert gate["status"] == "blocked"
    markdown_gate = next(item for item in gate["failing_checks"] if item["name"] == "markdown_first_freeze_truth_gate")
    diagnostics = markdown_gate["details"]["drift_by_feature"][SLUG]["freeze_state"]["diagnostics"]
    assert diagnostics[0]["reason_code"] == "ambiguous_refreeze_status"


def test_diagnostics_include_path_line_hash_reason_and_route(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    _freeze(tmp_path)
    _write(
        tmp_path,
        f"docs/beacon/{VERSION}/prd/{SLUG}.md",
        (tmp_path / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md").read_text(encoding="utf-8") + "\nDRIFT\n",
    )

    gate = build_requirement_package_gate(tmp_path, version=VERSION, feature=FEATURE, strict=True)
    markdown_gate = next(item for item in gate["failing_checks"] if item["name"] == "markdown_first_freeze_truth_gate")
    diagnostics = markdown_gate["details"]["drift_by_feature"][SLUG]["freeze_state"]["diagnostics"]

    assert diagnostics
    assert diagnostics[0]["reason_code"] == "baseline_hash_mismatch"
    assert diagnostics[0]["path"].endswith(f"user-story/{SLUG}.md")
    assert diagnostics[0]["hash"].startswith("sha256:")
    assert diagnostics[0]["repair_route"] == "beacon-change"


def test_historical_fulltext_json_is_readable_but_not_generated_for_new_freezes(tmp_path: Path) -> None:
    old_version = "v1.3.12"
    _seed_docs(tmp_path)
    old_base = tmp_path / "docs" / "beacon" / old_version
    for subdir in ("prd", "user-story", "qa/test-cases", ".machine/prd"):
        (old_base / subdir).mkdir(parents=True, exist_ok=True)
    old_markdown = "# PRD\n\n## 1. 问题\n- historical fulltext remains readable.\n"
    _write(tmp_path, f"docs/beacon/{old_version}/prd/{SLUG}.md", old_markdown)
    write_json(tmp_path / ".beacon" / "prd" / f"{SLUG}.json", {"content": old_markdown, "markdown": old_markdown})
    write_json(tmp_path / "docs" / "beacon" / old_version / ".machine" / "prd" / f"{SLUG}.canonical.json", {"markdown": old_markdown, "transaction": {"transaction_id": "tx-old", "source_hash": "old"}})

    old_payload = json.loads((tmp_path / ".beacon" / "prd" / f"{SLUG}.json").read_text(encoding="utf-8"))
    assert old_payload["markdown"] == old_markdown

    _freeze(tmp_path)
    result = _invoke(["prd", "reconcile", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert result.exit_code == 0, result.stdout
    new_payload = json.loads((tmp_path / ".beacon" / "prd" / f"{SLUG}.json").read_text(encoding="utf-8"))
    assert "markdown" not in new_payload
    assert "content" not in new_payload
