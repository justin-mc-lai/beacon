"""Runtime install truth diagnostics (v1.6.8 friction-closeout).

Makes CLI/version-truth/git HEAD/docs line observable so global installs
cannot silently drift with dirty feature branches.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from beacon.utils.versioning import load_version_truth, normalize_version

REASON_VERSION_DRIFT = "runtime_install_version_drift"
REASON_EDITABLE_DIRTY_BRANCH = "runtime_install_editable_on_feature_branch"
REASON_TRUTH_MISSING = "runtime_install_version_truth_missing"


def _run(cmd: list[str], *, cwd: Path | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "code": 127, "stdout": "", "stderr": str(exc)}


def _package_version() -> str:
    try:
        import beacon

        return str(getattr(beacon, "__version__", "") or "")
    except Exception:  # noqa: BLE001
        return ""


def _toolkit_version() -> str:
    try:
        import beacon

        return str(getattr(beacon, "__toolkit_version__", "") or "")
    except Exception:  # noqa: BLE001
        return ""


def _package_file() -> str:
    try:
        import beacon

        return str(Path(getattr(beacon, "__file__", "") or "").resolve())
    except Exception:  # noqa: BLE001
        return ""


def _git_probe(project_root: Path) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
    head = _run(["git", "rev-parse", "HEAD"], cwd=root)
    dirty = _run(["git", "status", "--porcelain"], cwd=root)
    return {
        "branch": branch.get("stdout") or "",
        "head": head.get("stdout") or "",
        "dirty": bool(str(dirty.get("stdout") or "").strip()),
        "ok": bool(branch.get("ok") and head.get("ok")),
    }


def _cli_which() -> dict[str, Any]:
    which_beacon = _run(["/bin/sh", "-lc", "command -v beacon || true"])
    which_cli = _run(["/bin/sh", "-lc", "command -v beacon-cli || true"])
    version = _run(["/bin/sh", "-lc", "beacon --version 2>/dev/null || true"])
    return {
        "beacon_path": which_beacon.get("stdout") or "",
        "beacon_cli_path": which_cli.get("stdout") or "",
        "beacon_version_output": version.get("stdout") or "",
    }


def _is_feature_branch(branch: str) -> bool:
    b = str(branch or "").strip()
    if not b or b in {"main", "master"}:
        return False
    # release/hotfix tags-ish branches may be ok; treat beacon/v* delivery and feature/* as non-prod
    if b.startswith("feature/") or b.startswith("beacon/v") or "/dev-" in b:
        return True
    return b not in {"main", "master"}


def diagnose_runtime_install(project_root: Path | str, *, production_branches: tuple[str, ...] = ("main", "master")) -> dict[str, Any]:
    """Return install truth triple: CLI, version-truth, git HEAD."""
    root = Path(project_root).expanduser().resolve()
    truth = load_version_truth(root) if (root / "beacon" / "version-truth.json").exists() or (root / "docs" / "beacon").exists() else {}
    if not truth and (root / "beacon" / "version-truth.json").exists():
        try:
            truth = json.loads((root / "beacon" / "version-truth.json").read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            truth = {}

    pkg = _package_version()
    toolkit = _toolkit_version()
    pkg_file = _package_file()
    git = _git_probe(root)
    cli = _cli_which()

    current_line = normalize_version(str(truth.get("current_runtime_release_line") or truth.get("runtime_version") or "")) or ""
    docs_line = normalize_version(str(truth.get("docs_default_line") or "")) or ""
    package_truth = str(truth.get("package_version") or "").strip()

    reasons: list[str] = []
    if not truth:
        reasons.append(REASON_TRUTH_MISSING)

    # Compare package semantic to truth package_version / toolkit line
    if package_truth and pkg and package_truth != pkg:
        reasons.append(REASON_VERSION_DRIFT)
    if current_line and toolkit and normalize_version(toolkit) != current_line:
        reasons.append(REASON_VERSION_DRIFT)

    # Editable install on feature branch is a production hazard
    editable = "site-packages" not in pkg_file.replace("\\", "/") and bool(pkg_file)
    # also detect pip editable path containing project root
    if root.as_posix() in pkg_file.replace("\\", "/"):
        editable = True
    branch = str(git.get("branch") or "")
    if editable and _is_feature_branch(branch) and branch not in production_branches:
        reasons.append(REASON_EDITABLE_DIRTY_BRANCH)

    # de-dupe
    reasons = list(dict.fromkeys(reasons))
    blocked = bool(reasons)

    repair: list[str] = []
    if REASON_VERSION_DRIFT in reasons:
        repair.append(f"cd {root} && git checkout main && python3 -m pip install -e . && beacon doctor sync-version-surfaces -p . && beacon doctor setup --force")
    if REASON_EDITABLE_DIRTY_BRANCH in reasons:
        repair.append(
            f"git checkout main && python3 -m pip install --force-reinstall -e {root}  # or install a release tag/wheel for production"
        )
    if REASON_TRUTH_MISSING in reasons:
        repair.append(f"ensure {root}/beacon/version-truth.json exists (Beacon self-repo) or run from project with version truth")

    return {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "ok": not blocked,
        "blocked": blocked,
        "reason_codes": reasons,
        "reason_code": reasons[0] if reasons else "",
        "recommended_command": repair[0] if repair else f"beacon doctor diagnose-runtime -p {root}",
        "repair_commands": repair,
        "cli": cli,
        "package": {
            "version": pkg,
            "toolkit_version": toolkit,
            "file": pkg_file,
            "editable_from_project": editable,
            "python": sys.executable,
        },
        "version_truth": {
            "package_version": package_truth,
            "runtime_version": str(truth.get("runtime_version") or ""),
            "docs_default_line": docs_line,
            "current_runtime_release_line": current_line,
            "planning_lines": list(truth.get("planning_lines") or []),
        },
        "git": git,
        "project_root": str(root),
        "policy": {
            "production_branches": list(production_branches),
            "note": "Production global CLI must not silently track dirty feature branches via editable install.",
        },
    }


def longrun_doctor(project_root: Path | str, *, run_id: str = "") -> dict[str, Any]:
    """Report longrun/bridge/supervise readiness for operators."""
    root = Path(project_root).expanduser().resolve()
    from beacon.utils.prod_ops_v168 import load_goal_ops_config, resolve_longrun_enabled
    from beacon.utils.goal_agent_driver import resolve_bridge_command

    cfg = load_goal_ops_config(root)
    resolved = resolve_longrun_enabled(root, cli_longrun=None)
    bridge = resolve_bridge_command(
        prompt_file=root / ".beacon" / "goal" / "doctor-prompt.txt",
        run_id=run_id or "doctor",
        project_root=root,
        bridge_cmd=None,
    )
    return {
        "schema_version": "1.0",
        "status": "pass" if bridge.get("ok") or not resolved.get("enabled") else "warn",
        "goal_ops_config": cfg,
        "longrun_resolved": resolved,
        "bridge": {
            "ok": bool(bridge.get("ok")),
            "mode": bridge.get("mode"),
            "reason_code": bridge.get("reason_code") or "",
            "hint": bridge.get("hint") or "",
        },
        "env_bridge": bool(str(os.environ.get("BEACON_HOST_GOAL_BRIDGE_CMD") or "").strip()),
        "recommended_command": (
            ""
            if bridge.get("ok") or not resolved.get("enabled")
            else 'export BEACON_HOST_GOAL_BRIDGE_CMD=\'codex exec -- "$(cat {prompt_file})"\''
        ),
    }
