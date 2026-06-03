"""Feature-centric package materialization and validation for v1.5.0."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import (
    feature_package_dir,
    feature_package_file,
    machine_requirement_file,
    qa_docs_file,
)
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version

REQUIRED_TRUTH_FRONTMATTER = ("slug", "version", "status", "language", "canonical_refs", "parser_contract")
PARSER_CONTRACT = "beacon-feature-package-v1"
ALLOWED_EVIDENCE_AUTHORITIES = {"support_advisory", "qa_verdict", "release_verdict"}
FORBIDDEN_EVIDENCE_FIELDS = ("final_verdict", "gate_truth", "release_ready", "qa_passed", "source_of_truth")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[(?P<mark>[ xX-])\]\s+`?(?P<id>[A-Z]+-\d{3,})`?\s+(?P<title>.+?)\s*$")


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def _canonical_ready_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 5, 1)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _slug(value: str) -> str:
    return feature_slug(value)


def package_paths(project_root: Path, *, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    return {
        "dir": feature_package_dir(project_root, version, slug),
        "truth": feature_package_file(project_root, version, slug, "truth.md"),
        "tests": feature_package_file(project_root, version, slug, "tests.md"),
        "tasks": feature_package_file(project_root, version, slug, "tasks.md"),
        "evidence": feature_package_file(project_root, version, slug, "evidence.md"),
    }


def _extract_ac_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower() for cell in cells]
        if "ac id" in lowered:
            in_table = True
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and cells and re.match(r"AC-\d{3}", cells[0]):
            rows.append(
                {
                    "ac_id": cells[0],
                    "theme": cells[1] if len(cells) > 1 else "",
                    "description": cells[2] if len(cells) > 2 else "",
                }
            )
    return rows


def _extract_test_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower() for cell in cells]
        if "ac id" in lowered and "tc id" in lowered:
            in_table = True
            headers = [cell.lower().replace(" ", "_") for cell in cells]
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and cells and re.match(r"AC-\d{3}", cells[0]):
            if headers and len(cells) > len(headers) and ("command" in headers or "planned_command" in headers):
                command_index = headers.index("command") if "command" in headers else headers.index("planned_command")
                tail_count = len(headers) - command_index - 1
                command_end = len(cells) - tail_count if tail_count else len(cells)
                cells = [
                    *cells[:command_index],
                    "|".join(cells[command_index:command_end]).strip(),
                    *cells[command_end:],
                ]
            row = {headers[index]: cells[index] if index < len(cells) else "" for index in range(len(headers))}
            rows.append(
                {
                    "ac_id": row.get("ac_id") or cells[0],
                    "tc_id": row.get("tc_id") or (cells[1] if len(cells) > 1 else ""),
                    "layer": row.get("layer") or (cells[2] if len(cells) > 2 else ""),
                    "command": row.get("command") or row.get("planned_command") or "",
                    "assertion": row.get("assertion") or (cells[4] if len(cells) > 4 else ""),
                    "evidence_path": row.get("evidence_path") or "",
                }
            )
    return rows


def _parse_frontmatter(markdown: str) -> tuple[dict[str, Any], str, list[str]]:
    if not markdown.startswith("---\n"):
        return {}, markdown, ["frontmatter_missing"]
    end = markdown.find("\n---", 4)
    if end < 0:
        return {}, markdown, ["frontmatter_unclosed"]
    raw = markdown[4:end].strip("\n")
    body = markdown[end + 4 :].lstrip("\n")
    data: dict[str, Any] = {}
    errors: list[str] = []
    current_key = ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = value.strip("\"'")
            else:
                data[current_key] = {}
            continue
        if line.startswith("  ") and current_key:
            parent = data.setdefault(current_key, {})
            if isinstance(parent, dict) and ":" in line:
                key, value = line.strip().split(":", 1)
                parent[key.strip()] = value.strip().strip("\"'")
            else:
                errors.append(f"frontmatter_nested_parse_failed: {line.strip()}")
            continue
        errors.append(f"frontmatter_parse_failed: {line.strip()}")
    return data, body, errors


def _parse_checkboxes(markdown: str) -> tuple[list[dict[str, str]], list[str]]:
    tasks: list[dict[str, str]] = []
    errors: list[str] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if "- [" not in line:
            continue
        match = CHECKBOX_RE.match(line)
        if not match:
            errors.append(f"malformed_checkbox: line {line_number}")
            continue
        mark = match.group("mark").lower()
        if mark == "x":
            status = "checked"
        elif mark == "-":
            status = "blocked"
        else:
            status = "unchecked"
        tasks.append({"id": match.group("id"), "title": match.group("title").strip(), "status": status})
    return tasks, errors


def _extract_evidence_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        lowered = [cell.lower().replace(" ", "_") for cell in cells]
        if "surface" in lowered and "authority" in lowered:
            in_table = True
            headers = lowered
            continue
        if in_table and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        if in_table and headers:
            row = {headers[index]: cells[index] if index < len(cells) else "" for index in range(len(headers))}
            if row.get("surface") or row.get("authority"):
                rows.append(row)
    return rows


def _canonical_refs(project_root: Path, *, version: str, slug: str) -> dict[str, str]:
    return {
        "prd": f"docs/beacon/{version}/prd/{slug}.md",
        "user_story": f"docs/beacon/{version}/user-story/{slug}.md",
        "test_case": f"docs/beacon/{version}/qa/test-cases/{slug}.md",
    }


def _render_frontmatter(*, slug: str, version: str, language: str, status: str) -> str:
    refs = _canonical_refs(Path("."), version=version, slug=slug)
    return "\n".join(
        [
            "---",
            f"slug: {slug}",
            f"version: {version}",
            f"status: {status}",
            f"language: {language}",
            "canonical_refs:",
            f"  prd: {refs['prd']}",
            f"  user_story: {refs['user_story']}",
            f"  test_case: {refs['test_case']}",
            f"parser_contract: {PARSER_CONTRACT}",
            "---",
        ]
    )


def render_truth_package(project_root: Path, *, version: str, feature: str) -> str:
    slug = _slug(feature)
    prd_path = project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"
    user_story_path = project_root / "docs" / "beacon" / version / "user-story" / f"{slug}.md"
    prd = _read_text(prd_path)
    user_story = _read_text(user_story_path)
    ac_rows = _extract_ac_rows(user_story) or [
        {"ac_id": match.group(0), "theme": "", "description": line.strip("- ")}
        for line in user_story.splitlines()
        for match in [re.search(r"AC-\d{3}", line)]
        if match
    ]
    lines = [
        _render_frontmatter(slug=slug, version=version, language="en", status="draft"),
        "",
        f"# Feature: {feature}",
        "",
        "## Overview",
        "",
        "This feature package is a v1.5.0 parallel read model. Canonical requirement truth remains in PRD, user-story, test-case, execution, and `.machine` surfaces.",
        "",
        "## Canonical References",
        "",
        f"- PRD: `docs/beacon/{version}/prd/{slug}.md`",
        f"- User Story: `docs/beacon/{version}/user-story/{slug}.md`",
        f"- Test Case: `docs/beacon/{version}/qa/test-cases/{slug}.md`",
        "",
        "## Acceptance Criteria",
        "",
        "| AC ID | Theme | Description |",
        "|-------|-------|-------------|",
    ]
    for row in ac_rows:
        lines.append(f"| {row['ac_id']} | {row.get('theme', '')} | {row.get('description', '')} |")
    lines.extend(["", "## Source Excerpt", "", "```markdown", prd[:4000].rstrip(), "```", ""])
    return "\n".join(lines)


def render_tests_package(project_root: Path, *, version: str, feature: str) -> str:
    slug = _slug(feature)
    qa_path = qa_docs_file(project_root, version, f"{slug}.md")
    qa = _read_text(qa_path)
    rows = _extract_test_rows(qa)
    lines = [
        f"# Tests: {feature}",
        "",
        "## Coverage Matrix",
        "",
        "| AC ID | TC ID | Layer | Assertion |",
        "|-------|-------|-------|-----------|",
    ]
    for row in rows:
        lines.append(f"| {row['ac_id']} | {row.get('tc_id', '')} | {row.get('layer', '')} | {row.get('assertion', '')} |")
    lines.extend(
        [
            "",
            "## Validation Note",
            "",
            "This file is a parallel test read model. Canonical test truth remains in `qa/test-cases/` and `.machine/qa/` in v1.5.0.",
            "",
        ]
    )
    return "\n".join(lines)


def render_tasks_package(project_root: Path, *, version: str, feature: str) -> str:
    _ = project_root
    _ = version
    return "\n".join(
        [
            f"# Tasks: {feature}",
            "",
            "## Task Ledger",
            "",
            "- [ ] TASK-001 Materialize feature package",
            "- [ ] TASK-002 Validate frontmatter and acceptance criteria",
            "- [ ] TASK-003 Validate checkbox ledger without gate bypass",
            "- [ ] TASK-004 Validate evidence authority labels",
            "- [ ] TASK-005 Run canonical implement and QA gates separately",
            "",
            "## Boundary",
            "",
            "Checkboxes are readable task-ledger inputs only. They do not mark implement, QA, or release complete without existing gate validation.",
            "",
        ]
    )


def render_evidence_package(project_root: Path, *, version: str, feature: str) -> str:
    slug = _slug(feature)
    return "\n".join(
        [
            f"# Evidence Index: {feature}",
            "",
            "## Evidence Index",
            "",
            "| Surface | Authority | Canonical Artifact | Status | Route |",
            "|---------|-----------|--------------------|--------|-------|",
            f"| beacon-deep | support_advisory | docs/beacon/{version}/research/{slug}.md | indexed | change |",
            f"| beacon-ceo-review | support_advisory | docs/beacon/{version}/change/{slug}.refreeze-summary.md | indexed | change |",
            f"| qa | qa_verdict | docs/beacon/{version}/.machine/qa/{slug}.qa9-matrix.json | linked | qa |",
            f"| release | release_verdict | docs/beacon/{version}/release/ | linked | release |",
            "",
            "## Boundary",
            "",
            "`evidence.md` is an index/read model. It must not contain final verdict, gate truth, or release readiness authority fields.",
            "",
        ]
    )


def materialize_feature_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    force: bool = False,
) -> dict[str, Any]:
    slug = _slug(feature)
    paths = package_paths(project_root, version=version, feature=feature)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    rendered = {
        "truth": render_truth_package(project_root, version=version, feature=feature),
        "tests": render_tests_package(project_root, version=version, feature=feature),
        "tasks": render_tasks_package(project_root, version=version, feature=feature),
        "evidence": render_evidence_package(project_root, version=version, feature=feature),
    }
    written: list[str] = []
    skipped: list[str] = []
    for key, content in rendered.items():
        path = paths[key]
        if path.exists() and not force:
            skipped.append(_rel(project_root, path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(_rel(project_root, path))
    validation = validate_feature_package(project_root, version=version, feature=feature, write_report=True)
    return {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "materialized",
        "package_dir": _rel(project_root, paths["dir"]),
        "written": written,
        "skipped": skipped,
        "validation": validation,
    }


def validate_feature_package(
    project_root: Path,
    *,
    version: str,
    feature: str,
    write_report: bool = False,
) -> dict[str, Any]:
    slug = _slug(feature)
    paths = package_paths(project_root, version=version, feature=feature)
    diagnostics: list[dict[str, Any]] = []
    truth = _read_text(paths["truth"])
    tests = _read_text(paths["tests"])
    tasks_md = _read_text(paths["tasks"])
    evidence = _read_text(paths["evidence"])

    for key in ("truth", "tests", "tasks", "evidence"):
        if not paths[key].exists():
            diagnostics.append({"severity": "error", "code": f"missing_{key}", "path": _rel(project_root, paths[key])})

    frontmatter, _body, frontmatter_errors = _parse_frontmatter(truth)
    for error in frontmatter_errors:
        diagnostics.append({"severity": "error", "code": error, "path": _rel(project_root, paths["truth"])})
    for key in REQUIRED_TRUTH_FRONTMATTER:
        if key not in frontmatter:
            diagnostics.append({"severity": "error", "code": f"frontmatter_missing_{key}", "path": _rel(project_root, paths["truth"])})
    if str(frontmatter.get("parser_contract") or "") != PARSER_CONTRACT:
        diagnostics.append({"severity": "error", "code": "parser_contract_mismatch", "path": _rel(project_root, paths["truth"])})
    if frontmatter.get("slug") and str(frontmatter.get("slug")) != slug:
        diagnostics.append({"severity": "error", "code": "frontmatter_slug_mismatch", "path": _rel(project_root, paths["truth"])})

    ac_rows = _extract_ac_rows(truth)
    if not ac_rows:
        diagnostics.append({"severity": "error", "code": "acceptance_criteria_table_missing", "path": _rel(project_root, paths["truth"])})

    test_rows = _extract_test_rows(tests)
    if not test_rows:
        diagnostics.append({"severity": "warn", "code": "tests_coverage_table_missing", "path": _rel(project_root, paths["tests"])})

    checkbox_rows, checkbox_errors = _parse_checkboxes(tasks_md)
    for error in checkbox_errors:
        diagnostics.append({"severity": "error", "code": error, "path": _rel(project_root, paths["tasks"])})
    if not checkbox_rows:
        diagnostics.append({"severity": "error", "code": "checkbox_ledger_missing", "path": _rel(project_root, paths["tasks"])})

    evidence_lower = evidence.lower()
    for field in FORBIDDEN_EVIDENCE_FIELDS:
        if field in evidence_lower:
            diagnostics.append({"severity": "error", "code": f"evidence_forbidden_gate_truth_field:{field}", "path": _rel(project_root, paths["evidence"])})
    evidence_rows = _extract_evidence_rows(evidence)
    if not evidence_rows:
        diagnostics.append({"severity": "error", "code": "evidence_authority_table_missing", "path": _rel(project_root, paths["evidence"])})
    for index, row in enumerate(evidence_rows, start=1):
        authority = str(row.get("authority") or "").strip()
        if authority not in ALLOWED_EVIDENCE_AUTHORITIES and authority not in {"requirement_truth", "acceptance_truth", "test_truth"}:
            diagnostics.append(
                {
                    "severity": "error",
                    "code": f"evidence_invalid_authority:{authority or '<empty>'}",
                    "path": _rel(project_root, paths["evidence"]),
                    "row": index,
                }
            )

    has_errors = any(item.get("severity") == "error" for item in diagnostics)
    payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "status": "blocked" if has_errors else "pass",
        "blocked": has_errors,
        "reason_code": "feature_package_validation_failed" if has_errors else "",
        "generated_at": now_iso(),
        "package_dir": _rel(project_root, paths["dir"]),
        "truth_frontmatter": frontmatter,
        "ac_count": len(ac_rows),
        "test_count": len(test_rows),
        "checkbox_count": len(checkbox_rows),
        "evidence_row_count": len(evidence_rows),
        "gate_authority": "canonical_surfaces_preserved",
        "checkbox_gate_bypass": False,
        "evidence_gate_truth": False,
        "diagnostics": diagnostics,
    }
    if _canonical_ready_supported(version):
        from beacon.utils.truth_map import (
            MACHINE_JSON_GENERATOR,
            MACHINE_JSON_ROLE,
            TRUTH_MAP_CONTRACT,
            TRUTH_PACKAGE_CONTRACT,
            resolve_feature_truth,
            truth_source_model_for_version,
        )

        resolved_truth = resolve_feature_truth(project_root, version=version, feature=slug)
        model = truth_source_model_for_version(version)
        payload.update(
            {
                "truth_map_contract": TRUTH_MAP_CONTRACT,
                "truth_source_model": model,
                "truth_package_contract": TRUTH_PACKAGE_CONTRACT,
                "machine_json_role": MACHINE_JSON_ROLE,
                "generated_by": MACHINE_JSON_GENERATOR,
                "truth_authority": "markdown_feature_package",
                "json_authority": False,
                "source_paths": resolved_truth.get("source_paths", {}),
                "source_hashes": resolved_truth.get("source_hashes", {}),
                "runtime_json_requires_markdown_twin": False,
            }
        )
    if write_report:
        report_path = machine_requirement_file(project_root, version, "feature-package-validation.json")
        write_json(report_path, payload)
        payload["report_path"] = _rel(project_root, report_path)
    return payload
