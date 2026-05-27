"""Test marker governance helpers for Beacon v1.4.11 retirement slices."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


REQUIRED_TEST_MARKERS: tuple[str, ...] = (
    "current_contract",
    "projection_integrity",
    "compat_contract",
    "historical_fixture",
    "migration",
    "deprecated",
)

V1411_RETIREMENT_TEST_FILES: tuple[str, ...] = (
    "tests/test_v1411_authority_vocabulary_and_inventory.py",
    "tests/test_v1411_compatibility_registry_and_command_catalog.py",
    "tests/test_v1411_qa_prd_legacy_mirror_policy.py",
    "tests/test_v1411_implement_package_legacy_loader_retirement.py",
    "tests/test_v1411_beacon_design_product_prototype_rebuild.py",
    "tests/test_v1411_browser_fallback_deterministic_command.py",
    "tests/test_v1411_memory_intent_historical_migration_boundary.py",
)

LEGACY_DEFAULT_PATTERNS: tuple[str, ...] = (
    "--fallback-cmd",
    "legacy_source_only",
    "enabled_legacy_mirror",
    "legacy_only_qa_pass",
)

COMPAT_ID_RE = re.compile(r'"([a-z0-9]+(?:-[a-z0-9]+)+)"')
EVIDENCE_OR_TRANSACTION_RE = re.compile(r"(evidence|transaction|migration_transaction|writeback)")


def registered_pytest_markers(project_root: Path) -> set[str]:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return set()
    markers: set[str] = set()
    in_pytest_options = False
    in_markers = False
    for raw in pyproject.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_pytest_options = stripped == "[tool.pytest.ini_options]"
            in_markers = False
            continue
        if not in_pytest_options:
            continue
        if stripped.startswith("markers") and "=" in stripped:
            in_markers = "[" in stripped
            continue
        if in_markers:
            if stripped.startswith("]"):
                break
            text = stripped.rstrip(",").strip()
            if not text:
                continue
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
            name = text.split(":", 1)[0].strip()
            if name:
                markers.add(name)
    return markers


def _marker_name(call: ast.AST) -> str:
    node = call.func if isinstance(call, ast.Call) else call
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        current: ast.AST | None = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        dotted = ".".join(reversed(parts))
        prefix = "pytest.mark."
        if dotted.startswith(prefix):
            return dotted[len(prefix):]
    return ""


def _literal_string_args(call: ast.Call) -> set[str]:
    values: set[str] = set()
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            values.add(arg.value)
    return values


def _module_marker_names(tree: ast.Module) -> set[str]:
    markers: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "pytestmark" for target in node.targets):
            continue
        value = node.value
        nodes: list[ast.AST] = []
        if isinstance(value, (ast.Call, ast.Attribute)):
            nodes = [value]
        elif isinstance(value, (ast.List, ast.Tuple)):
            nodes = [item for item in value.elts if isinstance(item, (ast.Call, ast.Attribute))]
        for node in nodes:
            name = _marker_name(node)
            if name:
                markers.add(name)
    return markers


def _function_marker_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    markers: set[str] = set()
    for decorator in node.decorator_list:
        if not isinstance(decorator, (ast.Call, ast.Attribute)):
            continue
        name = _marker_name(decorator)
        if name:
            markers.add(name)
    return markers


def _function_text(source: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    lines = source.splitlines()
    start = max(1, int(getattr(node, "lineno", 1)))
    end = int(getattr(node, "end_lineno", start))
    return "\n".join(lines[start - 1:end])


def collect_test_marker_inventory(project_root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for rel in V1411_RETIREMENT_TEST_FILES:
        path = project_root / rel
        if not path.exists():
            files.append({"path": rel, "exists": False, "module_markers": [], "tests": []})
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        module_markers = _module_marker_names(tree)
        tests: list[dict[str, Any]] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                markers = sorted(module_markers | _function_marker_names(node))
                text = _function_text(source, node)
                tests.append(
                    {
                        "name": node.name,
                        "markers": markers,
                        "text": text,
                        "compat_ids": sorted(set(COMPAT_ID_RE.findall(text))),
                    }
                )
        files.append(
            {
                "path": rel,
                "exists": True,
                "module_markers": sorted(module_markers),
                "tests": tests,
            }
        )
    return {"schema_version": "1.0", "files": files}


def validate_test_marker_governance(project_root: Path, *, registry_ids: set[str] | None = None) -> dict[str, Any]:
    registered = registered_pytest_markers(project_root)
    inventory = collect_test_marker_inventory(project_root)
    registry_ids = set(registry_ids or set())
    issues: list[dict[str, Any]] = []

    missing_registered = sorted(set(REQUIRED_TEST_MARKERS) - registered)
    for marker in missing_registered:
        issues.append({"reason_code": "marker_not_registered", "marker": marker})

    classified_files = 0
    marker_counts = {marker: 0 for marker in REQUIRED_TEST_MARKERS}
    compat_tests: list[dict[str, str]] = []
    migration_tests: list[dict[str, str]] = []
    current_tests: list[dict[str, str]] = []
    historical_tests: list[dict[str, str]] = []
    deprecated_tests: list[dict[str, str]] = []
    projection_tests: list[dict[str, str]] = []

    for file_item in inventory["files"]:
        path = str(file_item["path"])
        if not file_item.get("exists"):
            issues.append({"reason_code": "v1411_test_file_missing", "path": path})
            continue
        file_marked = False
        for test in file_item.get("tests", []):
            markers = set(test.get("markers") or [])
            roles = markers & set(REQUIRED_TEST_MARKERS)
            if roles:
                file_marked = True
            else:
                issues.append({"reason_code": "test_missing_role_marker", "path": path, "test": test.get("name")})
            for marker in roles:
                marker_counts[marker] += 1
            row = {"path": path, "test": str(test.get("name") or "")}
            text = str(test.get("text") or "")
            compat_ids = set(test.get("compat_ids") or [])
            if "current_contract" in markers:
                current_tests.append(row)
                offenders = [
                    pattern
                    for pattern in LEGACY_DEFAULT_PATTERNS
                    if pattern in text and f"not in command" not in text and f'{pattern}" not in' not in text
                ]
                if offenders:
                    issues.append(
                        {
                            "reason_code": "current_contract_mentions_legacy_default_pattern",
                            "path": path,
                            "test": test.get("name"),
                            "patterns": offenders,
                        }
                    )
            if "compat_contract" in markers:
                compat_tests.append(row)
                registry_bound = bool(compat_ids & registry_ids) or any(
                    token in text
                    for token in (
                        "registry_by_id",
                        "validate_compatibility_registry",
                        "REQUIRED_REGISTRY_IDS",
                        "REQUIRED_HOTSPOTS",
                        "required_registry_ids_from_baseline",
                    )
                )
                if not registry_bound:
                    issues.append({"reason_code": "compat_contract_missing_compat_id", "path": path, "test": test.get("name")})
                elif compat_ids and registry_ids and not (compat_ids & registry_ids) and "registry_by_id" not in text:
                    issues.append(
                        {
                            "reason_code": "compat_contract_unregistered_compat_id",
                            "path": path,
                            "test": test.get("name"),
                            "compat_ids": sorted(compat_ids),
                        }
                    )
            if "historical_fixture" in markers:
                historical_tests.append(row)
                if "current_contract" in markers:
                    issues.append({"reason_code": "historical_fixture_marked_current_contract", "path": path, "test": test.get("name")})
            if "migration" in markers:
                migration_tests.append(row)
                if not EVIDENCE_OR_TRANSACTION_RE.search(text):
                    issues.append({"reason_code": "migration_missing_evidence_or_transaction_assertion", "path": path, "test": test.get("name")})
            if "deprecated" in markers:
                deprecated_tests.append(row)
                if "current_contract" in markers:
                    issues.append({"reason_code": "deprecated_marked_current_contract", "path": path, "test": test.get("name")})
            if "projection_integrity" in markers:
                projection_tests.append(row)
        if file_marked:
            classified_files += 1

    for marker, count in marker_counts.items():
        if count == 0:
            issues.append({"reason_code": "required_marker_has_no_tests", "marker": marker})

    summary = {
        "registered_markers": sorted(registered & set(REQUIRED_TEST_MARKERS)),
        "required_markers": list(REQUIRED_TEST_MARKERS),
        "classified_file_count": classified_files,
        "required_file_count": len(V1411_RETIREMENT_TEST_FILES),
        "marker_counts": marker_counts,
        "current_tests": current_tests,
        "compat_tests": compat_tests,
        "historical_fixture_tests": historical_tests,
        "migration_tests": migration_tests,
        "deprecated_tests": deprecated_tests,
        "projection_integrity_tests": projection_tests,
    }
    return {
        "schema_version": "1.0",
        "feature": "test-directory-marker-relayering-contract",
        "status": "pass" if not issues else "blocked",
        "blocked": bool(issues),
        "issues": issues,
        "summary": summary,
    }
