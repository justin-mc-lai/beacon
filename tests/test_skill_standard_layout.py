from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beacon import __toolkit_version__

ROOT = Path(__file__).resolve().parents[1]
CURRENT_SKILL_SURFACE = "v1.6.0"


def test_standard_skill_package_should_exist():
    base = ROOT / "skills" / "beacon"
    assert (base / "SKILL.md").exists()
    assert (base / "references" / "_sections.md").exists()
    assert (base / "references" / "usage-rules.md").exists()
    assert (base / "examples" / "basic-workflow.md").exists()
    assert (base / "examples" / "release-readiness.md").exists()
    assert (base / "examples" / "implementation-with-omx.md").exists()
    assert (base / "scripts" / "run_beacon.sh").exists()
    assert (base / "metadata.json").exists()


def test_standard_skill_package_should_have_frontmatter_and_metadata():
    skill_text = (ROOT / "skills" / "beacon" / "SKILL.md").read_text(encoding="utf-8")
    assert skill_text.startswith("---\n")
    assert "name: beacon" in skill_text
    assert "description:" in skill_text
    assert "docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md" in skill_text
    assert "docs/beacon/v1.6.0/execution/implementation-summary-beacon-skill-harness-taxonomy-v160.md" in skill_text
    assert "plan -> truth -> generate -> evaluate -> release" in skill_text
    assert "beacon skill package verify --project-root . --version v1.6.0 --package-root skills/beacon --json" in skill_text
    assert "placeholder implementation" in skill_text

    metadata = json.loads((ROOT / "skills" / "beacon" / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["name"] == "beacon"
    assert metadata["version"] == CURRENT_SKILL_SURFACE


def test_standard_skill_wrapper_script_should_launch_beacon_version():
    script = ROOT / "skills" / "beacon" / "scripts" / "run_beacon.sh"
    result = subprocess.run(["bash", str(script), "--version"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"Beacon CLI {__toolkit_version__}" in result.stdout


def test_standard_skill_wrapper_script_should_export_host_bridge_contract():
    script = ROOT / "skills" / "beacon" / "scripts" / "run_beacon.sh"
    text = script.read_text(encoding="utf-8")
    assert 'BEACON_HOST_RUNTIME' in text
    assert 'BEACON_HOST_PRD_BRIDGE_CMD' in text
    assert 'BEACON_HOST_USER_STORY_BRIDGE_CMD' in text
    assert 'BEACON_HOST_TEST_CASE_BRIDGE_CMD' in text
    assert 'BEACON_HOST_PROTOTYPE_BRIDGE_CMD' in text
    assert 'prd host-bridge' in text
    assert 'user-story host-bridge' in text
    assert 'test-case host-bridge' in text
    assert 'prototype host-bridge' in text


def test_basic_workflow_example_should_align_with_v115_docs_and_flow():
    example = (ROOT / "skills" / "beacon" / "examples" / "basic-workflow.md").read_text(encoding="utf-8")
    assert "../../../docs/beacon/v1.4.6/SUMMARY.md" in example
    assert "../../../docs/beacon/v1.4.6/execution/index.md" in example
    assert "release-readiness.md" in example
    assert "implementation-with-omx.md" in example
    assert "Beacon v1.4.6 release line" in example
    assert "workflow status" in example


def test_release_readiness_example_should_cover_doctor_gate_and_release():
    example = (ROOT / "skills" / "beacon" / "examples" / "release-readiness.md").read_text(encoding="utf-8")
    assert "../../../docs/beacon/v1.4.6/SUMMARY.md" in example
    assert "doctor verify-materials" in example
    assert "doctor repair-package" in example
    assert "gate check release" in example
    assert "release check v1.4.6 --project ." in example


def test_implementation_with_omx_example_should_cover_skill_and_implement_flow():
    example = (ROOT / "skills" / "beacon" / "examples" / "implementation-with-omx.md").read_text(encoding="utf-8")
    assert "../../../docs/beacon/v1.4.6/SUMMARY.md" in example
    assert "skill detect" in example
    assert "skill prefer omx" in example
    assert "implement list-runners" in example
    assert "--runner omx" in example
    assert "review spec" in example
