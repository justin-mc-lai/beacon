from __future__ import annotations

import json
from pathlib import Path


def _seed_config(root: Path, *, version: str = "v1.1.1") -> Path:
    exec_dir = root / "docs" / "beacon" / version / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)
    path = exec_dir / "config.json"
    path.write_text(
        json.dumps(
            {
                "implementation": {
                    "root": str(root),
                    "include_paths": ["beacon", "tests"],
                    "exclude_paths": [".beacon", "dist"],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def test_implementation_scope_should_include_expected_paths(tmp_path: Path):
    path = _seed_config(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["implementation"]["include_paths"] == ["beacon", "tests"]


def test_implementation_scope_should_exclude_beacon_state(tmp_path: Path):
    path = _seed_config(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert ".beacon" in payload["implementation"]["exclude_paths"]
