"""Beacon test-case command - Generate test cases."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="test-case", help="Generate test cases")


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _candidate_doc_paths(project_root: Path, version: str, category: str, slug: str) -> list[Path]:
    return [
        project_root / "docs" / "product" / version / category / f"{slug}.md",
        project_root / "docs" / "beacon" / version / category / f"{slug}.md",
    ]


def _read_first_existing(paths: list[Path]) -> tuple[Path | None, str]:
    for path in paths:
        if path.exists():
            return path, path.read_text(encoding="utf-8", errors="ignore")
    return None, ""


def _extract_ac_items(content: str, source: str) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    if not content.strip():
        return items

    # Markdown table pattern: | AC-001 | text | ...
    for line in content.splitlines():
        if "|" not in line:
            continue
        m = re.search(r"\b(AC-\d{3,})\b", line, flags=re.I)
        if not m:
            continue
        ac_id = m.group(1).upper()
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        text = cells[1] if len(cells) > 1 else line.strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "text": text, "source": source})

    # Fallback bullet/text pattern: AC-001: xxx
    for m in re.finditer(r"\b(AC-\d{3,})\b[:：]?\s*([^\n]+)", content, flags=re.I):
        ac_id = m.group(1).upper()
        text = m.group(2).strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "text": text, "source": source})

    return items


def _infer_layer_from_ac(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ("登录", "注册", "浏览", "表单", "submit", "form", "ui", "页面", "点击")):
        return "ui"
    if any(x in t for x in ("api", "接口", "http", "curl", "endpoint")):
        return "api-curl"
    if any(x in t for x in ("单元", "unit", "函数", "边界", "error", "异常", "校验", "security")):
        return "unit"
    # Default to unit for deterministic commandability in minimal setups.
    return "unit"


def _default_command_for_layer(layer: str) -> str:
    return {
        "ui": "python -m pytest -q -k ui",
        "api-curl": "bash -lc 'curl -sS http://127.0.0.1:8000/health'",
        "unit": "python -m pytest -q -k unit",
        "smoke": "python -m pytest -q -m smoke",
    }.get(layer, "python -m pytest -q")


def _default_assertion_for_layer(layer: str) -> str:
    return {
        "ui": "UI assertion + key action evidence",
        "api-curl": "HTTP status=2xx and response schema valid",
        "unit": "All assertions pass",
        "smoke": "Critical path pass",
    }.get(layer, "assertion defined")


def generate_test_cases(feature: str, test_type: str) -> list:
    """Generate legacy test case structure (kept for compatibility)."""
    cases = []

    if test_type in ("all", "smoke"):
        cases.extend(
            [
                {"id": "TC-001", "type": "smoke", "title": "Feature loads correctly", "status": "pending"},
                {"id": "TC-002", "type": "smoke", "title": "Core functionality works", "status": "pending"},
            ]
        )

    if test_type in ("all", "new"):
        cases.extend(
            [
                {"id": "TC-003", "type": "new", "title": "Happy path test", "status": "pending"},
                {"id": "TC-004", "type": "new", "title": "Edge case test", "status": "pending"},
            ]
        )

    if test_type in ("all", "regression"):
        cases.extend(
            [
                {
                    "id": "TC-005",
                    "type": "regression",
                    "title": "Existing functionality preserved",
                    "status": "pending",
                },
            ]
        )

    return cases


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    test_type: str = typer.Option("all", "--type", "-t", help="Test type: smoke/new/regression/all"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create test cases and executable AC matrix."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    feature_slug = _slug(feature)
    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()

    # Read ACs from existing user-story/prd docs
    us_path, us_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "user-story", feature_slug)
    )
    prd_path, prd_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "prd", feature_slug)
    )
    ac_items = _extract_ac_items(us_content, f"user-story:{us_path}" if us_path else "user-story:missing")
    ac_items.extend(_extract_ac_items(prd_content, f"prd:{prd_path}" if prd_path else "prd:missing"))
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]

    entries = []
    for idx, ac in enumerate(ac_items, start=1):
        layer = _infer_layer_from_ac(ac.get("text", ""))
        tc_id = f"TC-{idx:03d}"
        evidence_path = f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac["ac_id"],
                "layer": layer,
                "command": _default_command_for_layer(layer),
                "assertion": _default_assertion_for_layer(layer),
                "evidence_path": evidence_path,
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )

    matrix_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "generated_at": datetime.now().isoformat(),
        "entries": entries,
    }

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "qa" / "test-cases" / f"{feature_slug}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path = output_path.with_name(f"{feature_slug}.ac-test-matrix.json")
    matrix_path.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_rows = "\n".join(
        f"| {x['ac_id']} | {x['tc_id']} | {x['layer']} | `{x['command']}` | {x['assertion']} | `{x['evidence_path']}` |"
        for x in entries
    )
    result_rows = "\n".join(f"| {x['tc_id']} | Pending | from {x['ac_id']} |" for x in entries)

    md_content = f"""# Test Cases: {feature}

## Overview

**Feature**: {feature}
**Test Type**: {test_type.upper()}
**Version**: {resolved_version}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Memory Context**: {memory_context_path or 'N/A'}
**AC Matrix JSON**: {matrix_path}

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
{md_rows}

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
{result_rows}
"""

    output_path.write_text(md_content, encoding="utf-8")
    if not output:
        # Keep beacon docs path in sync with product docs path.
        beacon_output_path = project_root / "docs" / "beacon" / resolved_version / "qa" / "test-cases" / f"{feature_slug}.md"
        beacon_output_path.parent.mkdir(parents=True, exist_ok=True)
        beacon_output_path.write_text(md_content, encoding="utf-8")

        beacon_matrix_path = beacon_output_path.with_name(f"{feature_slug}.ac-test-matrix.json")
        beacon_matrix_path.write_text(
            json.dumps(matrix_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    typer.echo(f"✓ Test cases created: {output_path}")
    typer.echo(f"✓ AC matrix created: {matrix_path}")
    typer.echo(f"  Type: {test_type}")
    typer.echo(f"  Entries: {len(entries)}")


@app.command("list")
def list_tests(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all test cases."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    test_dir = project_root / "docs" / "product" / resolved_version / "qa" / "test-cases"

    if not test_dir.exists():
        typer.echo("No test cases found")
        return

    tests = list(test_dir.glob("*.md"))
    typer.echo(f"Test Cases ({len(tests)} found):")
    for test in tests:
        typer.echo(f"  - {test.name}")


@app.command()
def gate(
    feature: str = typer.Argument(..., help="Feature to check"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Run gate check for AC matrix coverage."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo(f"\nTest Coverage Gate: {feature}")
    typer.echo("=" * 40)

    slug = _slug(feature)
    test_dir = project_root / "docs" / "product" / resolved_version / "qa" / "test-cases"
    test_file = test_dir / f"{slug}.md"
    matrix_file = test_dir / f"{slug}.ac-test-matrix.json"

    if not test_file.exists():
        typer.echo(f"✗ FAIL: Test file not found: {test_file}")
        raise typer.Exit(1)
    typer.echo("✓ PASS: Test file exists")

    if not matrix_file.exists():
        typer.echo(f"✗ FAIL: AC matrix not found: {matrix_file}")
        raise typer.Exit(1)

    payload = json.loads(matrix_file.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        typer.echo(f"✗ FAIL: AC matrix empty: {matrix_file}")
        raise typer.Exit(1)

    required_fields = {"ac_id", "tc_id", "layer", "command", "assertion", "evidence_path"}
    broken = [
        idx + 1
        for idx, item in enumerate(entries)
        if not isinstance(item, dict) or not required_fields.issubset(set(item.keys()))
    ]
    if broken:
        typer.echo(f"✗ FAIL: AC matrix entries missing fields: {broken[:10]}")
        raise typer.Exit(1)

    typer.echo(f"✓ PASS: AC executable matrix entries={len(entries)}")
    typer.echo("\nGate Result: PASS")


if __name__ == "__main__":
    app()
