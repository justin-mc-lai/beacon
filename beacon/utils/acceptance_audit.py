"""Acceptance regression audit helpers."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version

_EXEC_MATRIX = "*.ac-test-matrix.json"
_PYTEST_SUMMARY = re.compile(
    r"(?P<passed>\d+)\s+passed(?:,\s*(?P<failed>\d+)\s+failed)?(?:,\s*(?P<skipped>\d+)\s+skipped)?(?:,\s*(?P<errors>\d+)\s+errors?)?",
    re.IGNORECASE,
)


def parse_pytest_summary(output: str) -> dict[str, Any]:
    text = str(output or "")
    match = None
    for candidate in _PYTEST_SUMMARY.finditer(text):
        match = candidate
    if not match:
        return {
            "status": "unknown",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "summary_line": "",
        }
    passed = int(match.group("passed") or 0)
    failed = int(match.group("failed") or 0)
    skipped = int(match.group("skipped") or 0)
    errors = int(match.group("errors") or 0)
    total = passed + failed + skipped + errors
    status = "pass" if failed == 0 and errors == 0 and passed > 0 else "blocked"
    return {
        "status": status,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "total": total,
        "summary_line": match.group(0),
    }


def run_regression_command(project_root: Path, command: str) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=project_root,
        shell=True,
        text=True,
        capture_output=True,
    )
    summary = parse_pytest_summary(f"{result.stdout}\n{result.stderr}")
    summary.update(
        {
            "command": command,
            "exit_code": int(result.returncode),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    )
    if result.returncode != 0 and summary["status"] == "pass":
        summary["status"] = "blocked"
    return summary


def _iter_exec_matrix_paths(project_root: Path) -> list[Path]:
    root = project_root / "docs" / "beacon"
    return sorted(list(root.glob(f"v*/qa/test-cases/{_EXEC_MATRIX}")) + list(root.glob(f"v*/.machine/qa/{_EXEC_MATRIX}")))


def _feature_from_matrix(path: Path) -> str:
    return path.name.replace(".ac-test-matrix.json", "")


def _matrix_entry_count(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    entries = payload.get("entries")
    return len(entries) if isinstance(entries, list) else 0


def collect_executable_specs(project_root: Path) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for path in _iter_exec_matrix_paths(project_root):
        version_name = path.parents[2].name if path.parents[1].name != ".machine" else path.parents[3].name
        specs.append(
            {
                "version": version_name,
                "feature": _feature_from_matrix(path),
                "entries": _matrix_entry_count(path),
                "path": str(path.relative_to(project_root)),
            }
        )
    return specs


def collect_legacy_manual_specs(project_root: Path) -> list[str]:
    qa_dir = project_root / "docs" / "beacon" / "v1.0.0" / "qa" / "test-cases"
    if not qa_dir.exists():
        return []
    return sorted(str(path.relative_to(project_root)) for path in qa_dir.glob("*.md") if path.is_file())


def collect_release_evidence(project_root: Path, *, version: str, feature: str | None = None) -> dict[str, Any]:
    auto_test_path = project_root / ".beacon" / "auto-test-status.json"
    gate_report_path = project_root / ".beacon" / "gate-report.json"
    coverage_path = project_root / ".beacon" / "coverage-summary.json"

    auto_test = json.loads(auto_test_path.read_text(encoding="utf-8")) if auto_test_path.exists() else {}
    gate = json.loads(gate_report_path.read_text(encoding="utf-8")) if gate_report_path.exists() else {}
    coverage = json.loads(coverage_path.read_text(encoding="utf-8")) if coverage_path.exists() else compute_coverage_metrics(project_root, version=version, feature=feature)
    return {
        "auto_test_status": auto_test,
        "gate_report": gate,
        "coverage_summary": coverage,
    }


def build_acceptance_audit_payload(
    project_root: Path,
    *,
    version: str,
    feature: str,
    regression: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    executable_specs = collect_executable_specs(project_root)
    release = collect_release_evidence(project_root, version=resolved_version, feature=feature)
    coverage = release["coverage_summary"]
    total_entries = sum(int(item.get("entries") or 0) for item in executable_specs)
    gate = release["gate_report"] if isinstance(release["gate_report"], dict) else {}
    auto_test = release["auto_test_status"] if isinstance(release["auto_test_status"], dict) else {}
    qa9_summary = ((auto_test.get("qa9") or {}).get("summary") if isinstance(auto_test, dict) else {}) or {}
    regression_payload = regression or {
        "status": "unknown",
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "total": 0,
        "summary_line": "",
        "command": "",
        "exit_code": None,
    }
    return {
        "schema_version": "1.0",
        "generated_at": now_iso(),
        "version": resolved_version,
        "feature": feature,
        "regression": regression_payload,
        "release_evidence_run_id": str(auto_test.get("run_id", "") or gate.get("run_id", "")).strip(),
        "gate_status": str(gate.get("status", "unknown") or "unknown"),
        "auto_test_status": str(auto_test.get("status", "unknown") or "unknown"),
        "coverage": coverage,
        "qa9_summary": qa9_summary,
        "executable_specs": executable_specs,
        "executable_specs_total": len(executable_specs),
        "executable_entries_total": total_entries,
        "legacy_manual_specs": collect_legacy_manual_specs(project_root),
    }


def render_acceptance_audit_markdown(payload: dict[str, Any]) -> str:
    regression = payload.get("regression", {}) if isinstance(payload, dict) else {}
    coverage = payload.get("coverage", {}) if isinstance(payload, dict) else {}
    qa9 = payload.get("qa9_summary", {}) if isinstance(payload, dict) else {}
    lines = [
        f"# Beacon {payload.get('version', '')} Acceptance Regression Audit",
        "",
        f"- Date: {str(payload.get('generated_at', '')).split('T')[0]}",
        f"- Feature: {payload.get('feature', '')}",
        f"- Final regression command: `{regression.get('command') or 'not-run'}`",
        f"- Final regression result: **{regression.get('summary_line') or regression.get('status', 'unknown')}**",
        f"- Release gate evidence run_id: `{payload.get('release_evidence_run_id', '')}`",
        "",
        "> This audit is a **snapshot document**. Refresh it after any new full-regression or release-gate run so the counts and evidence links stay current.",
        "",
        "## 1. Acceptance conclusion",
        "",
        f"- regression_status: `{regression.get('status', 'unknown')}`",
        f"- auto_test_status: `{payload.get('auto_test_status', 'unknown')}`",
        f"- gate_status: `{payload.get('gate_status', 'unknown')}`",
        f"- coverage_full: `{coverage.get('full_coverage')}`",
        f"- qa9_cases: `{qa9.get('passed', 0)}/{qa9.get('cases_total', 0)}`",
        "",
        "## 2. Maintained executable test-spec coverage",
        "",
        "| Version | Feature | Executable entries |",
        "|---|---|---:|",
    ]
    for item in payload.get("executable_specs", []):
        lines.append(f"| {item.get('version')} | {item.get('feature')} | {item.get('entries')} |")
    lines.extend(
        [
            f"|  | **Total** | **{payload.get('executable_entries_total', 0)}** |",
            "",
            "## 3. Legacy manual reference specs",
            "",
        ]
    )
    legacy = payload.get("legacy_manual_specs", [])
    if legacy:
        for item in legacy:
            lines.append(f"- `{item}`")
    else:
        lines.append("- (none)")
    lines.extend(
        [
            "",
            "## 4. Release evidence",
            "",
            f"- auto-test status: `{payload.get('auto_test_status', 'unknown')}`",
            f"- gate status: `{payload.get('gate_status', 'unknown')}`",
            f"- story/ac/tc coverage: `{coverage.get('story_coverage')}` / `{coverage.get('ac_coverage')}` / `{coverage.get('tc_coverage')}`",
            f"- full coverage: `{coverage.get('full_coverage')}`",
            "",
            "## 5. Final decision",
            "",
            "**Pass** — when regression, auto-test, and gate are all green. Otherwise Blocked.",
            "",
        ]
    )
    return "\n".join(lines)


def write_acceptance_audit(project_root: Path, payload: dict[str, Any]) -> dict[str, str]:
    version = str(payload.get("version", "") or "")
    execution_roots = [project_root / "docs" / "beacon" / version / "execution"]
    written: dict[str, str] = {}
    markdown = render_acceptance_audit_markdown(payload)
    for root in execution_roots:
        root.mkdir(parents=True, exist_ok=True)
        md_path = root / "acceptance-regression-audit.md"
        json_path = root / "acceptance-regression-audit.json"
        md_path.write_text(markdown, encoding="utf-8")
        write_json(json_path, payload)
        written[str(md_path.relative_to(project_root))] = str(md_path)
        written[str(json_path.relative_to(project_root))] = str(json_path)
    _update_evidence_manifest(
        project_root,
        sorted(written.keys()),
        run_id=str(payload.get("release_evidence_run_id", "") or "").strip(),
        version=str(payload.get("version", "") or "").strip(),
    )
    return written


def _update_evidence_manifest(
    project_root: Path,
    evidence_refs: list[str],
    *,
    run_id: str,
    version: str,
) -> None:
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    payload: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                payload = loaded
        except Exception:
            payload = {}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    by_path: dict[str, dict[str, Any]] = {
        str(item.get("path")): item
        for item in entries
        if isinstance(item, dict) and str(item.get("path", "")).strip()
    }
    by_path = {
        ref_path: item
        for ref_path, item in by_path.items()
        if (project_root / ref_path).exists() and (project_root / ref_path).is_file()
    }
    for ref in evidence_refs:
        ref_path = str(ref or "").strip()
        if not ref_path:
            continue
        full = project_root / ref_path
        if not full.exists() or not full.is_file():
            continue
        by_path[ref_path] = {
            "path": ref_path,
            "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            "updated_at": now_iso(),
        }
    output_payload: dict[str, Any] = {
        "entries": list(by_path.values()),
        "updated_at": now_iso(),
    }
    if run_id:
        output_payload["run_id"] = run_id
    if version:
        output_payload["version"] = version
    write_json(manifest_path, output_payload)
