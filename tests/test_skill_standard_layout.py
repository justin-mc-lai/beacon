from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_standard_skill_package_should_exist():
    base = ROOT / "skills" / "beacon"
    assert (base / "SKILL.md").exists()
    assert (base / "references" / "_sections.md").exists()
    assert (base / "references" / "usage-rules.md").exists()
    assert (base / "examples" / "basic-workflow.md").exists()
    assert (base / "scripts" / "run_beacon.sh").exists()
    assert (base / "metadata.json").exists()


def test_standard_skill_package_should_have_frontmatter_and_metadata():
    skill_text = (ROOT / "skills" / "beacon" / "SKILL.md").read_text(encoding="utf-8")
    assert skill_text.startswith("---\n")
    assert "name: beacon" in skill_text
    assert "description:" in skill_text

    metadata = json.loads((ROOT / "skills" / "beacon" / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["name"] == "beacon"
    assert metadata["version"] == "1.1.5"


def test_standard_skill_wrapper_script_should_launch_beacon_version():
    script = ROOT / "skills" / "beacon" / "scripts" / "run_beacon.sh"
    result = subprocess.run(["bash", str(script), "--version"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Beacon CLI v1.1.5" in result.stdout
