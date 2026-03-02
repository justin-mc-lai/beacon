from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_skill_md_should_have_yaml_frontmatter():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")

    lines = text.splitlines()
    assert len(lines) > 3
    assert lines[0] == "---"

    closing = next((i for i, line in enumerate(lines[1:], start=1) if line == "---"), None)
    assert closing is not None

    frontmatter = "\n".join(lines[1:closing])
    assert "name:" in frontmatter
    assert "description:" in frontmatter
