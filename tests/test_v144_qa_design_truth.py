from __future__ import annotations

import json
import hashlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.utils.story_state import sync_story_state_from_docs, freeze_story_state

runner = CliRunner()
VERSION = "v1.4.4"
FEATURE = "Beacon V144 QA Design Truth Demo"
SLUG = "beacon-v144-qa-design-truth-demo"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_sources(root: Path, *, design_preset: str = "") -> None:
    preset_line = f"design_preset: {design_preset}\n" if design_preset else ""
    prd = (
        f"# PRD: {FEATURE}\n\n"
        "## 1. Overview\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
        f"{preset_line}"
        "- target_audience: Product owner and QA operator\n"
        "- primary_use_cases: verify design truth blocking in QA\n"
        "- operator_mental_state: needs confident release decisions\n"
        "- usage_environment: desktop-first workbench\n"
        "- brand_tone: quiet, precise, operational\n"
        "- density_preference: workbench-medium\n\n"
        "## 2. Scope\n\n"
        "- In scope: QA consumes prototype design truth and blocks on drift.\n"
        "- Out of scope: changing design truth after freeze.\n\n"
        "## 3. Functional Requirements\n\n"
        "| FR ID | Related AC | Requirement |\n"
        "| --- | --- | --- |\n"
        "| FR-001 | AC-001 | Prototype emits governed design truth. |\n"
        "| FR-002 | AC-002 | Implement handoff preserves design truth. |\n"
        "| FR-003 | AC-003 | QA detects design truth drift and blocks release. |\n\n"
        "## 4. Acceptance Traceability\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | design-truth | Prototype design assets expose template and anti-AI baseline. |\n"
        "| AC-002 | implement-handoff | Implement-to-QA handoff carries frozen design truth. |\n"
        "| AC-003 | qa-verdict | QA consumes design truth and raises drift as stop_reason. |\n"
    )
    story = (
        f"# User Story: {FEATURE}\n\n"
        "## Story\n\n"
        "As a QA operator, I want QA to block release when design truth drifts from handoff.\n\n"
        "## Acceptance Criteria\n\n"
        "| AC ID | Theme | Description |\n"
        "| --- | --- | --- |\n"
        "| AC-001 | design-truth | Prototype design assets expose template and anti-AI baseline. |\n"
        "| AC-002 | implement-handoff | Implement-to-QA handoff carries frozen design truth. |\n"
        "| AC-003 | qa-verdict | QA consumes design truth and raises drift as stop_reason. |\n\n"
        "## Metadata\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
    )
    test_case = (
        f"# Test Cases: {FEATURE}\n\n"
        "## Coverage Matrix\n\n"
        "| TC ID | AC ID | Scenario | Layer | Expected |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| TC-001 | AC-001 | Prototype emits style-preset and design-lint-rules | integration | design truth available. |\n"
        "| TC-002 | AC-002 | Implement handoff preserves same design truth | integration | handoff contains design_truth. |\n"
        "| TC-003 | AC-003 | QA detects drift and blocks release | integration | design_truth_verdict.blocked=true. |\n\n"
        "## Metadata\n\n"
        f"- version: `{VERSION}`\n"
        f"- feature: `{FEATURE}`\n"
        "- status: `frozen`\n"
    )
    for rel, content in (
        (f"docs/beacon/{VERSION}/prd/{SLUG}.md", prd),
        (f"docs/beacon/{VERSION}/user-story/{SLUG}.md", story),
        (f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", test_case),
    ):
        _write(root, rel, content)
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")


def _seed_prd_machine_mirrors(root: Path) -> None:
    prd_path = root / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md"
    markdown_raw = prd_path.read_text(encoding="utf-8")
    markdown = markdown_raw.strip()
    source_hash = "sha256:" + hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    compile_hash = hashlib.sha256(markdown_raw.encode("utf-8")).hexdigest()
    tx_id = "tx-v144-prototype-001"
    _write(root, f".beacon/prd/{SLUG}.json", json.dumps({"content": markdown}, ensure_ascii=False, indent=2) + "\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/.machine/prd/{SLUG}.canonical.json",
        json.dumps({"markdown": markdown, "transaction": {"transaction_id": tx_id, "source_hash": source_hash}}, ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/.machine/prd/{SLUG}.compile.json",
        json.dumps({"compile_hash": compile_hash, "contract_ok": True}, ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        root,
        f".beacon/state/prd-transactions/latest-{SLUG}.json",
        json.dumps({"transaction_id": tx_id, "source_hash": source_hash}, ensure_ascii=False, indent=2) + "\n",
    )


def _setup_git(root: Path) -> None:
    import subprocess
    subprocess.run(["git", "init"], cwd=root, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=root, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "beacon/v1.4.4"], cwd=root, capture_output=True)


def _seed_implement_ready_package(root: Path) -> None:
    from beacon.utils.revision_state import freeze_revision_state
    _seed_sources(root)
    _seed_prd_machine_mirrors(root)
    _setup_git(root)
    # Sync and freeze story state directly from complete docs
    sync_story_state_from_docs(root, version=VERSION, feature=FEATURE)
    freeze_story_state(root, version=VERSION, feature=FEATURE)
    sync_story_state_from_docs(root, version=VERSION, feature=FEATURE)
    # Generate requirement completeness artifact via test-case create
    test_case = _invoke(["test-case", "create", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert test_case.exit_code == 0, test_case.stdout
    # Required formal documents for v1.4.4 material audit
    for rel in (
        f"docs/beacon/{VERSION}/execution/boundaries.md",
        f"docs/beacon/{VERSION}/execution/project-skill-qa-evolution-blueprint.md",
        f"docs/beacon/{VERSION}/source-architecture/index.md",
        f"docs/beacon/{VERSION}/release/index.md",
    ):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Required Beacon material\n", encoding="utf-8")
    revision_state = freeze_revision_state(root, version=VERSION, feature=FEATURE)
    from beacon.utils.technical_review_contract import materialize_technical_review_contract
    materialize_technical_review_contract(
        root,
        version=VERSION,
        feature=FEATURE,
        revision_id=str(revision_state.get("revision_id", "R1") or "R1"),
        force_refresh=True,
        contract_overrides={
            "review_status": "approved",
            "approved_by": "Beacon Tests",
        },
        source="test.v144.qa-design-truth",
    )


def _write_fake_runner_script(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        "request_file = sys.argv[1]\n"
        "result_file = sys.argv[2]\n"
        "with open(request_file, 'r') as f:\n"
        "    request = json.load(f)\n"
        "result = {\n"
        "    'schema_version': '1.0',\n"
        "    'status': 'completed',\n"
        "    'summary': 'implemented with governed design truth',\n"
        "    'changed_files': ['beacon/commands/implement.py'],\n"
        "    'verification': [{'command': 'echo ok', 'status': 'passed'}]\n"
        "}\n"
        "with open(result_file, 'w') as f:\n"
        "    json.dump(result, f, ensure_ascii=False, indent=2)\n",
        encoding="utf-8",
    )


def _write_fake_runner_config(root: Path) -> None:
    (root / "beacon.config.yaml").write_text(
        (
            "skill:\n"
            "  adapters:\n"
            "    fake:\n"
            "      adapter_type: command\n"
            "      runtime_family: fake\n"
            "      command: python3\n"
            "      args:\n"
            "        - \"{project_root}/runner.py\"\n"
            "        - \"{request_file}\"\n"
            "        - \"{result_file}\"\n"
        ),
        encoding="utf-8",
    )


def test_v144_qa_should_block_when_design_truth_preset_drift(tmp_path: Path) -> None:
    """AC-007: QA detects design preset drift between implement handoff and current prototype."""
    _seed_implement_ready_package(tmp_path)

    # Write fake runner before implement commands
    _write_fake_runner_script(tmp_path / "runner.py")
    _write_fake_runner_config(tmp_path)

    # Prototype creates restrained-product (default for v1.4.4)
    proto = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert proto.exit_code == 0, proto.stdout

    # Implement plan + run
    plan = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout

    # Fake runner that just writes success marker
    run = _invoke(["implement", "run", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--runner", "fake", "--json"])
    assert run.exit_code == 0, run.stdout

    # Tamper: change current prototype design preset to operator-console (drift)
    style_path = tmp_path / "docs" / "beacon" / VERSION / "prototype" / SLUG / "design-artifacts" / "style-preset.json"
    style = json.loads(style_path.read_text(encoding="utf-8"))
    style["payload"]["design_preset"] = "operator-console"
    style["payload"]["canonical_design_preset"] = "operator-console"
    style_path.write_text(json.dumps(style, ensure_ascii=False, indent=2), encoding="utf-8")

    # QA run with fake layer commands to skip real tests
    pass_layer = tmp_path / "pass.sh"
    pass_layer.write_text("#!/bin/sh\necho 'ok'", encoding="utf-8")

    qa = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {pass_layer}",
            "--layer-command",
            f"unit=sh {pass_layer}",
            "--json",
        ]
    )

    # Expect blocked due to design truth drift
    payload = json.loads(qa.stdout)
    verdict = payload.get("design_truth_verdict") or {}

    assert qa.exit_code == 2, f"expected blocked exit code, got {qa.exit_code}"
    assert payload.get("status") == "blocked"
    assert verdict.get("blocked") is True
    assert "design_truth_preset_drift" in (verdict.get("reason_codes") or [])
    assert payload.get("feature_scorecard", {}).get("release_ready") is False
    assert "design_truth_preset_drift" in (payload.get("feature_scorecard", {}).get("stop_reasons") or [])


def test_v144_qa_should_pass_when_design_truth_aligned(tmp_path: Path) -> None:
    """AC-007: QA passes when design truth remains aligned with handoff."""
    _seed_implement_ready_package(tmp_path)

    # Write fake runner before implement commands
    _write_fake_runner_script(tmp_path / "runner.py")
    _write_fake_runner_config(tmp_path)

    proto = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert proto.exit_code == 0, proto.stdout

    plan = _invoke(["implement", "plan", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--json"])
    assert plan.exit_code == 0, plan.stdout

    run = _invoke(["implement", "run", FEATURE, "--project-root", str(tmp_path), "--version", VERSION, "--runner", "fake", "--json"])
    assert run.exit_code == 0, run.stdout

    pass_layer = tmp_path / "pass.sh"
    pass_layer.write_text("#!/bin/sh\necho 'ok'", encoding="utf-8")

    qa = _invoke(
        [
            "qa",
            "run",
            FEATURE,
            "--project-root",
            str(tmp_path),
            "--version",
            VERSION,
            "--layer-command",
            f"contract=sh {pass_layer}",
            "--layer-command",
            f"unit=sh {pass_layer}",
            "--json",
        ]
    )

    payload = json.loads(qa.stdout)
    verdict = payload.get("design_truth_verdict") or {}

    # Should not be blocked by design truth
    assert verdict.get("blocked") is not True
    assert "design_truth_preset_drift" not in (verdict.get("reason_codes") or [])
