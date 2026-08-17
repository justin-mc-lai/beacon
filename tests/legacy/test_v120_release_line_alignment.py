from __future__ import annotations

import json
from pathlib import Path

from beacon import __toolkit_version__, __version__


def test_release_line_metadata_should_match_toolkit_version():
    root = Path(__file__).resolve().parents[1]
    truth = json.loads((root / "beacon" / "version-truth.json").read_text(encoding="utf-8"))

    assert truth["package_version"] == __version__
    assert truth["runtime_version"] == __toolkit_version__
    assert truth["docs_default_line"] == __toolkit_version__
    assert truth["current_runtime_release_line"] == __toolkit_version__
    assert truth["lines"][__toolkit_version__]["status"] == "current_runtime_release"


def test_current_release_line_should_have_required_docs_surfaces():
    root = Path(__file__).resolve().parents[1]
    docs_root = root / "docs" / "beacon" / __toolkit_version__

    required = [
        docs_root / "SUMMARY.md",
        docs_root / "execution" / "index.md",
        docs_root / "execution" / "architecture-blueprint.md",
        docs_root / "execution" / "boundaries.md",
        docs_root / "execution" / "project-skill-qa-evolution-blueprint.md",
        docs_root / "release" / f"{__toolkit_version__}.md",
    ]

    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    assert missing == []
