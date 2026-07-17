"""Google design.md lint integration for ship evidence."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.versioning import resolve_target_version

SCHEMA_VERSION = "1.0"
REASON_LINT_FAILED = "design_md_lint_failed"
REASON_LINT_MISSING = "design_md_lint_missing"
REASON_DESIGN_FILE_MISSING = "design_md_file_missing"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def design_md_lint_evidence_dir(project_root: Path) -> Path:
    return Path(project_root) / ".beacon" / "evidence" / "design-md-lint"


def resolve_design_md_path(project_root: Path, *, design_path: str = "") -> Path:
    root = Path(project_root).expanduser().resolve()
    if design_path:
        p = Path(design_path)
        return p if p.is_absolute() else (root / p)
    return root / "DESIGN.md"


def _run_google_lint(design_file: Path) -> dict[str, Any]:
    """Run npx @google/design.md lint; degrade gracefully if unavailable."""
    import os
    if str(os.environ.get("BEACON_DESIGN_MD_LINT_SKIP_NPX") or "").strip() in {"1", "true", "yes"}:
        return {
            "runner": "skipped",
            "available": False,
            "exit_code": 0,
            "stdout": "",
            "stderr": "skipped by BEACON_DESIGN_MD_LINT_SKIP_NPX",
            "findings": [],
            "summary": {"errors": 0, "warnings": 0, "info": 0},
            "fallback": "structural_only",
        }
    npx = shutil.which("npx")
    if not npx:
        return {
            "runner": "none",
            "available": False,
            "exit_code": 127,
            "stdout": "",
            "stderr": "npx not found",
            "findings": [],
            "summary": {"errors": 0, "warnings": 0, "info": 0},
            "fallback": "structural_only",
        }
    try:
        proc = subprocess.run(
            [npx, "--yes", "@google/design.md", "lint", str(design_file)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "runner": "npx @google/design.md lint",
            "available": True,
            "exit_code": 1,
            "stdout": "",
            "stderr": str(exc),
            "findings": [{"severity": "error", "message": str(exc)}],
            "summary": {"errors": 1, "warnings": 0, "info": 0},
            "fallback": "exception",
        }
    findings: list[dict[str, Any]] = []
    summary = {"errors": 0, "warnings": 0, "info": 0}
    parsed: dict[str, Any] = {}
    out = (proc.stdout or "").strip()
    # try JSON parse
    if out.startswith("{") or out.startswith("["):
        try:
            parsed = json.loads(out)
            if isinstance(parsed, dict):
                findings = list(parsed.get("findings") or [])
                if isinstance(parsed.get("summary"), dict):
                    summary = {
                        "errors": int(parsed["summary"].get("errors") or 0),
                        "warnings": int(parsed["summary"].get("warnings") or 0),
                        "info": int(parsed["summary"].get("info") or 0),
                    }
        except json.JSONDecodeError:
            parsed = {}
    # structural fallback when CLI prints non-json but exits non-zero
    if not findings and proc.returncode != 0:
        findings.append(
            {
                "severity": "error",
                "message": (proc.stderr or proc.stdout or "design.md lint failed")[:500],
            }
        )
        summary["errors"] = max(summary["errors"], 1)
    # count severities if findings present without summary
    if findings and summary["errors"] == 0 and summary["warnings"] == 0:
        for item in findings:
            sev = str(item.get("severity") or "").lower()
            if sev == "error":
                summary["errors"] += 1
            elif sev == "warning":
                summary["warnings"] += 1
            else:
                summary["info"] += 1
    return {
        "runner": "npx @google/design.md lint",
        "available": True,
        "exit_code": int(proc.returncode),
        "stdout": (proc.stdout or "")[:8000],
        "stderr": (proc.stderr or "")[:4000],
        "findings": findings,
        "summary": summary,
        "parsed": parsed if isinstance(parsed, dict) else {},
        "fallback": "",
    }


def _structural_lint(design_file: Path) -> dict[str, Any]:
    """Beacon-owned structural checks when google CLI missing or soft-fail."""
    text = design_file.read_text(encoding="utf-8") if design_file.exists() else ""
    findings: list[dict[str, Any]] = []
    if not text.strip():
        findings.append({"severity": "error", "message": "DESIGN.md empty"})
    if "---" not in text[:200]:
        findings.append({"severity": "warning", "path": "frontmatter", "message": "missing YAML front matter fence (google design.md style recommended)"})
    for section in ("## Overview", "## Colors", "## Typography", "## Components", "Do"):
        if section.lower() not in text.lower() and section.replace("## ", "").lower() not in text.lower():
            # softer: only warn for major sections
            if section in ("## Colors", "## Typography"):
                findings.append({"severity": "warning", "path": section, "message": f"recommended section missing: {section}"})
    if "colors:" not in text and "primary" not in text.lower():
        findings.append({"severity": "error", "path": "colors", "message": "no color tokens detected"})
    errors = sum(1 for f in findings if str(f.get("severity")) == "error")
    warnings = sum(1 for f in findings if str(f.get("severity")) == "warning")
    return {
        "runner": "beacon-structural",
        "available": True,
        "exit_code": 1 if errors else 0,
        "findings": findings,
        "summary": {"errors": errors, "warnings": warnings, "info": 0},
    }


def run_design_md_lint(
    project_root: Path,
    *,
    design_path: str = "",
    feature: str = "",
    version: str = "auto",
    require_google_cli: bool = False,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    design_file = resolve_design_md_path(root, design_path=design_path)
    slug = feature.strip() or "project"
    if not design_file.exists():
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_DESIGN_FILE_MISSING,
            "version": resolved,
            "feature": feature,
            "design_path": str(design_file),
            "findings": [{"severity": "error", "message": "DESIGN.md not found"}],
            "summary": {"errors": 1, "warnings": 0, "info": 0},
            "generated_at": _now_iso(),
        }
    else:
        google = _run_google_lint(design_file)
        structural = _structural_lint(design_file)
        # Prefer google findings when available and parseable; else structural.
        use_google = bool(google.get("available")) and (
            bool(google.get("findings")) or google.get("exit_code") == 0 or bool(google.get("parsed"))
        )
        if require_google_cli and not google.get("available"):
            chosen = {
                "runner": "required-google-missing",
                "findings": [{"severity": "error", "message": "npx/@google/design.md unavailable"}],
                "summary": {"errors": 1, "warnings": 0, "info": 0},
                "exit_code": 127,
            }
        elif use_google:
            chosen = google
            # merge structural errors if google returned empty success but structure bad
            if int(google.get("summary", {}).get("errors") or 0) == 0 and int(structural["summary"]["errors"]) > 0:
                chosen = {
                    **google,
                    "findings": list(google.get("findings") or []) + list(structural["findings"]),
                    "summary": {
                        "errors": int(structural["summary"]["errors"]),
                        "warnings": int(google.get("summary", {}).get("warnings") or 0) + int(structural["summary"]["warnings"]),
                        "info": int(google.get("summary", {}).get("info") or 0),
                    },
                    "hybrid": True,
                }
        else:
            chosen = structural

        errors = int((chosen.get("summary") or {}).get("errors") or 0)
        blocked = errors > 0
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "blocked" if blocked else "pass",
            "blocked": blocked,
            "reason_code": REASON_LINT_FAILED if blocked else "",
            "version": resolved,
            "feature": feature,
            "design_path": str(design_file.relative_to(root)) if str(design_file).startswith(str(root)) else str(design_file),
            "runner": chosen.get("runner"),
            "exit_code": chosen.get("exit_code"),
            "findings": chosen.get("findings") or [],
            "summary": chosen.get("summary") or {"errors": 0, "warnings": 0, "info": 0},
            "google": {k: google.get(k) for k in ("available", "runner", "exit_code", "fallback")},
            "generated_at": _now_iso(),
        }

    if write_evidence:
        out_dir = design_md_lint_evidence_dir(root)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{slug}.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        payload["evidence_path"] = str(out_path.relative_to(root))
        # latest pointer
        (out_dir / "latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
