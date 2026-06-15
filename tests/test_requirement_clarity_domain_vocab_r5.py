"""R5: requirement_clarity must not treat domain slug/path tokens as TODO placeholders."""

from __future__ import annotations

from pathlib import Path

from beacon.utils.requirement_clarity import (
    _line_has_inline_marker,
    _scan_file,
    build_requirement_clarity_gate_payload,
)

VERSION = "v1.6.0"
FEATURE = "go-todo-crud-smoke"


def test_line_has_inline_marker_uses_word_boundary_for_todo() -> None:
    assert not _line_has_inline_marker("slug: go-todo-crud-smoke")
    assert not _line_has_inline_marker("prd: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md")
    assert _line_has_inline_marker("TODO: clarify auth flow before freeze")


def test_scan_file_skips_yaml_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "truth.md"
    path.write_text(
        """---
slug: go-todo-crud-smoke
canonical_refs:
  prd: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md
---

# Go TODO CRUD Smoke

scope_mode = smoke
""",
        encoding="utf-8",
    )
    inline = [f for f in _scan_file(path) if f.get("kind") == "inline_marker"]
    assert inline == []


def test_go_todo_crud_smoke_clarity_gate_not_blocked_by_domain_vocab(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    feature_dir = (
        tmp_path
        / "docs/beacon/v1.6.0/features/go-todo-crud-smoke"
    )
    feature_dir.mkdir(parents=True)
    for name in ("truth.md", "tests.md", "tasks.md", "evidence.md"):
        (feature_dir / name).write_text(
            f"""---
slug: {FEATURE}
version: {VERSION}
status: draft
canonical_refs:
  prd: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md
  user_story: docs/beacon/v1.6.0/features/go-todo-crud-smoke/truth.md
  test_case: docs/beacon/v1.6.0/features/go-todo-crud-smoke/tests.md
parser_contract: beacon-feature-package-v1
truth_source_model: feature_package_authoritative
truth_map_contract: beacon-truth-map-v1
---

# Go TODO CRUD Smoke

scope_mode = smoke

## Acceptance

- AC-001: GET /todos returns 200.
""",
            encoding="utf-8",
        )
    (tmp_path / "docs/beacon/VERSION").write_text(f"{VERSION}\n", encoding="utf-8")

    payload = build_requirement_clarity_gate_payload(
        tmp_path,
        version=VERSION,
        feature=FEATURE,
    )
    inline = [
        f
        for f in payload.get("findings", [])
        if f.get("kind") == "inline_marker"
    ]
    assert inline == []
    assert payload.get("blocked") is not True
