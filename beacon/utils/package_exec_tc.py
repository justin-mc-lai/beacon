"""Execute package tests.md exec-layer TCs (v1.6.10+).

Shape gates live in truth_review_gate; this module runs real commands and
writes evidence under .beacon/evidence/test-results/<slug>/.
"""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.feature_package import package_paths
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_review_gate import (
    _is_docs_only_command,
    extract_test_rows,
    truth_review_gate_supported,
)
from beacon.utils.versioning import normalize_version, resolve_target_version

SCHEMA = "package-exec-tc.v1"


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def _domain_required(truth_md: str) -> bool:
    return bool(re.search(r"(?m)^domain_required:\s*(true|yes|1)\s*$", truth_md, re.I))


def list_exec_tc_rows(tests_md: str) -> list[dict[str, str]]:
    rows = extract_test_rows(tests_md)
    out: list[dict[str, str]] = []
    for row in rows:
        cmd = (row.get("command") or "").strip()
        assertion = (row.get("assertion") or "").strip()
        if not cmd or not assertion:
            continue
        if _is_docs_only_command(cmd):
            continue
        out.append(row)
    return out


def _run_command(command: str, *, cwd: Path, timeout_s: float = 120.0) -> dict[str, Any]:
    cmd = command.strip().strip("`")
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return {
            "exit_code": int(proc.returncode),
            "stdout": (proc.stdout or "")[-4000:],
            "stderr": (proc.stderr or "")[-4000:],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "exit_code": 124,
            "stdout": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr": "timeout",
            "timed_out": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {"exit_code": 1, "stdout": "", "stderr": str(exc), "timed_out": False}


def _assertion_pass(*, assertion: str, exit_code: int, domain_required: bool) -> bool:
    a = (assertion or "").lower()
    if "exit_code==0" in a or a.strip() in {"exit 0", "exit_code=0"}:
        return exit_code == 0
    if "exit_code_in_0_or_5" in a or "0_or_5" in a or "no_tests" in a:
        # domain lakes: bare "no tests" is not success
        if domain_required:
            return exit_code == 0
        return exit_code in {0, 5}
    if "import_beacon_ok" in a:
        return exit_code == 0
    if "review_json" in a:
        return exit_code in {0, 2}  # review may fail closed but must emit
    # default: require zero
    return exit_code == 0


def run_package_exec_tcs(
    project_root: Path,
    *,
    version: str,
    feature: str,
    write_evidence: bool = True,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = feature_slug(feature)
    if not truth_review_gate_supported(resolved) and _semver_tuple(resolved) < (1, 6, 10):
        return {
            "schema": SCHEMA,
            "skipped": True,
            "reason": "version_below_v1.6.10",
            "pass": True,
            "blocked": False,
        }

    paths = package_paths(root, version=resolved, feature=slug)
    tests_md = paths["tests"].read_text(encoding="utf-8") if paths["tests"].is_file() else ""
    truth_md = paths["truth"].read_text(encoding="utf-8") if paths["truth"].is_file() else ""
    domain = _domain_required(truth_md)
    rows = list_exec_tc_rows(tests_md)
    results: list[dict[str, Any]] = []
    evidence_dir = root / ".beacon" / "evidence" / "test-results" / slug
    if write_evidence:
        evidence_dir.mkdir(parents=True, exist_ok=True)

    if not rows:
        return {
            "schema": SCHEMA,
            "version": resolved,
            "feature": slug,
            "pass": not domain,
            "blocked": domain,
            "reason_code": "domain_exec_tc_missing" if domain else "",
            "domain_required": domain,
            "executed": [],
            "message": "no exec-layer TC rows to run",
        }

    failed = 0
    for row in rows:
        tc_id = row.get("tc_id") or "TC-EXEC"
        cmd = (row.get("command") or "").strip().strip("`")
        assertion = row.get("assertion") or ""
        run = _run_command(cmd, cwd=root, timeout_s=timeout_s)
        ok = _assertion_pass(assertion=assertion, exit_code=run["exit_code"], domain_required=domain)
        if not ok:
            failed += 1
        item = {
            "tc_id": tc_id,
            "ac_id": row.get("ac_id") or row.get("ac_ids") or "",
            "command": cmd,
            "assertion": assertion,
            "pass": ok,
            **run,
        }
        results.append(item)
        if write_evidence:
            ev_path = evidence_dir / f"{tc_id}.json"
            ev_path.write_text(
                json.dumps(
                    {
                        "schema": "package-exec-tc-result.v1",
                        "feature": slug,
                        "version": resolved,
                        "evaluated_at": now_iso(),
                        **item,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            item["evidence_path"] = str(ev_path.relative_to(root))

    overall = failed == 0
    return {
        "schema": SCHEMA,
        "version": resolved,
        "feature": slug,
        "pass": overall,
        "blocked": not overall,
        "reason_code": "" if overall else "package_exec_tc_failed",
        "domain_required": domain,
        "failed_count": failed,
        "executed": results,
        "evaluated_at": now_iso(),
    }
