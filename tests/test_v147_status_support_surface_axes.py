from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.7"
FEATURE = "beacon-v1.4.7-status-surface-ceo-review-axes"
SLUG = "beacon-v1.4.7-status-surface-ceo-review-axes"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_feature_docs(root: Path) -> None:
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    _write(root, f"docs/beacon/{VERSION}/prd/{SLUG}.md", "# prd\n")
    _write(root, f"docs/beacon/{VERSION}/user-story/{SLUG}.md", "# story\n")
    _write(root, f"docs/beacon/{VERSION}/qa/test-cases/{SLUG}.md", "# test\n")


