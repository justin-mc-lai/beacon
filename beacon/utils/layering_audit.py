"""Layering audit (v1.6.17 A2): map import dependencies, list God Modules,
detect layer violations. Observation only — never changes code structure.

Judgment: beacon has 232 flat `beacon/utils` modules with no explicit layering
(domain/service/adapter). This tool surfaces the dependency graph so the
maintainability risk can be assessed with data instead of intuition.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SCHEMA_LAYER_AUDIT = "layering-audit.v1"
GOD_MODULE_LINES = 2000

# command modules may depend on utils; utils must not depend on commands
LAYER_RULE = "commands -> utils (allowed); utils -> commands (violation)"


def _import_refs(text: str) -> set[str]:
    refs: set[str] = set()
    for m in re.finditer(r"from beacon\.(\w+)\.(\w+) import|import beacon\.(\w+)\.(\w+)", text):
        pkg, mod = m.group(1) or m.group(3), m.group(2) or m.group(4)
        if pkg in {"utils", "commands"}:
            refs.add(f"{pkg}.{mod}")
    return refs


def scan_import_graph(project_root: Path) -> dict[str, Any]:
    """Build import graph for beacon/utils and beacon/commands (AC-001)."""
    root = Path(project_root)
    modules: dict[str, dict[str, Any]] = {}
    for layer in ("utils", "commands"):
        layer_dir = root / "beacon" / layer
        if not layer_dir.exists():
            continue
        for f in sorted(layer_dir.glob("*.py")):
            if f.name.startswith("__"):
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            lines = len(text.splitlines())
            refs = _import_refs(text)
            modules[f"{layer}.{f.stem}"] = {
                "layer": layer,
                "lines": lines,
                "depends_on": sorted(refs),
            }
    return {
        "schema": SCHEMA_LAYER_AUDIT,
        "module_count": len(modules),
        "modules": modules,
    }


def list_god_modules(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """List modules above GOD_MODULE_LINES (AC-002)."""
    gods = []
    for name, info in graph.get("modules", {}).items():
        if int(info.get("lines") or 0) > GOD_MODULE_LINES:
            gods.append({"module": name, "lines": info["lines"], "layer": info["layer"]})
    return sorted(gods, key=lambda x: -x["lines"])


def detect_layer_violations(graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect utils -> commands imports (layer violation) (AC-003)."""
    violations = []
    for name, info in graph.get("modules", {}).items():
        if info.get("layer") != "utils":
            continue
        for dep in info.get("depends_on", []):
            if dep.startswith("commands."):
                violations.append({"from_module": name, "to_module": dep, "rule": LAYER_RULE})
    return sorted(violations, key=lambda x: x["from_module"])


def build_audit_report(project_root: Path) -> dict[str, Any]:
    """Produce maintainability risk report (AC-004)."""
    graph = scan_import_graph(project_root)
    gods = list_god_modules(graph)
    violations = detect_layer_violations(graph)

    total_modules = graph.get("module_count", 0)
    total_lines = sum(int(m.get("lines") or 0) for m in graph.get("modules", {}).values())
    god_share = round(sum(g["lines"] for g in gods) / float(total_lines or 1) * 100, 1) if gods else 0.0

    # risk: presence of god modules + layer violations + flat module count
    risk_level = "low"
    reasons = []
    if gods:
        risk_level = "medium"
        reasons.append(f"{len(gods)} God Modules (> {GOD_MODULE_LINES} lines, {god_share}% of code)")
    if violations:
        risk_level = "high"
        reasons.append(f"{len(violations)} layer violations (utils -> commands)")
    if total_modules > 200:
        if risk_level == "low":
            risk_level = "medium"
        reasons.append(f"{total_modules} flat modules without explicit layering")

    return {
        "schema": SCHEMA_LAYER_AUDIT,
        "module_count": total_modules,
        "total_lines": total_lines,
        "god_modules": gods,
        "god_module_count": len(gods),
        "god_share_percent": god_share,
        "layer_violations": violations,
        "layer_violation_count": len(violations),
        "risk_level": risk_level,
        "risk_reasons": reasons,
        "layering_rule": LAYER_RULE,
    }
