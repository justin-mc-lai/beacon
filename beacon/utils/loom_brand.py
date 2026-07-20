"""Loom brand surface contracts (v2.0.0 dual-install with Beacon).

UD-LOOM-001..010: Loom is the v2 evolution brand; Beacon remains production track.
Install must not overwrite the beacon launcher; state roots are isolated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA = "loom-brand-surface.v1"

# Locked naming matrix (AC-LOOM-BR-001) — dual runtime tracks
# Production: Python `beacon`. Evolution: Rust `beacon-v2` / brand alias `loom`.
# Python `loom-py` is optional debug facade only (must not own PATH name `loom`).
PIP_NAME = "loom"  # brand name
CLI_NAME = "loom"  # PATH product CLI = Rust binary
CLI_RUST_CANONICAL = "beacon-v2"
PYTHON_ESCAPE_CLI = "loom-py"
PUBLIC_SKILL = "loom-goal"
SUPPORT_SKILL = "loom-loop-goal"
STATE_ROOT_DIR = ".loom"
HOME_STATE = "~/.loom"
BEACON_CLI = "beacon"
BEACON_PUBLIC_SKILL = "beacon-goal"
BEACON_STATE_ROOT = ".beacon"
BACKEND = "rust"

REASON_REPLACE_BEACON = "loom_must_not_replace_beacon"
REASON_SHARED_STATE = "loom_beacon_shared_unlabeled_state"
REASON_EARLY_DEFAULT = "loom_early_default_replace_forbidden"


def naming_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "pip": PIP_NAME,
        "cli": CLI_NAME,
        "cli_rust_canonical": CLI_RUST_CANONICAL,
        "python_escape_cli": PYTHON_ESCAPE_CLI,
        "backend": BACKEND,
        "public_skill": PUBLIC_SKILL,
        "support_skill": SUPPORT_SKILL,
        "state_root": STATE_ROOT_DIR,
        "home_state": HOME_STATE,
        "beacon_cli": BEACON_CLI,
        "beacon_public_skill": BEACON_PUBLIC_SKILL,
        "beacon_state_root": BEACON_STATE_ROOT,
        "dual_install": True,
        "default_replace_beacon": False,
        "w4_early_default_forbidden": True,
        "path_governance": {
            "product_loom": "Rust binary from scripts/install-loom-cli.sh",
            "python_facade": "loom-py only; must not register console script name loom",
            "production_beacon": "Python beacon CLI — never overwritten by loom install",
        },
    }


def dual_install_names_ok() -> dict[str, Any]:
    contract = naming_contract()
    distinct = contract["cli"] != contract["beacon_cli"] and contract["pip"] != "beacon"
    return {
        "ok": distinct,
        "cli": contract["cli"],
        "beacon_cli": contract["beacon_cli"],
        "pip": contract["pip"],
        "blocked": not distinct,
        "reason_code": "" if distinct else REASON_REPLACE_BEACON,
    }


def state_roots(project_root: Path | None = None) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve() if project_root else None
    loom_local = (root / STATE_ROOT_DIR) if root else Path(STATE_ROOT_DIR)
    beacon_local = (root / BEACON_STATE_ROOT) if root else Path(BEACON_STATE_ROOT)
    isolated = str(loom_local) != str(beacon_local)
    return {
        "loom_project": str(loom_local),
        "beacon_project": str(beacon_local),
        "loom_home": HOME_STATE,
        "isolated": isolated,
        "blocked": not isolated,
        "reason_code": "" if isolated else REASON_SHARED_STATE,
    }


def install_must_not_overwrite_beacon(
    *,
    loom_bin: str = "loom",
    beacon_bin: str = "beacon",
    install_writes: list[str] | None = None,
) -> dict[str, Any]:
    """Simulate install path policy: loom install must not rewrite beacon launcher paths."""
    writes = list(install_writes or [])
    # Forbidden: writing a path that ends with /beacon or is exactly beacon when packaging loom
    collisions = []
    for w in writes:
        name = Path(w).name
        if name == BEACON_CLI or w.rstrip("/").endswith("/bin/beacon"):
            collisions.append(w)
    ok = loom_bin != beacon_bin and not collisions
    return {
        "ok": ok,
        "loom_bin": loom_bin,
        "beacon_bin": beacon_bin,
        "collisions": collisions,
        "blocked": not ok,
        "reason_code": "" if ok else REASON_REPLACE_BEACON,
        "illegal": "I-LOOM-BR-001" if not ok else "",
    }


def public_entry_contract() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "public_primary": PUBLIC_SKILL,
        "public_cli": f"{CLI_NAME} goal run",
        "support_only": [SUPPORT_SKILL],
        "single_entry": True,
        "dual_public_orchestration": False,
        "does_not_replace": BEACON_PUBLIC_SKILL,
    }


def docs_forbid_early_default(paths: list[Path]) -> dict[str, Any]:
    """Docs must not claim loom is the default replacement for beacon (W4)."""
    violations: list[dict[str, str]] = []
    banned = (
        "loom replaces beacon by default",
        "default alias beacon→loom",
        "BEACON_V2=1 by default",
        "默认用 loom 替换 beacon",
        "默认 alias beacon 到 loom",
    )
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in banned:
            if phrase.lower() in text:
                violations.append({"path": str(path), "phrase": phrase})
    return {
        "status": "pass" if not violations else "blocked",
        "blocked": bool(violations),
        "reason_code": REASON_EARLY_DEFAULT if violations else "",
        "violations": violations,
    }


def dual_matrix_checklist() -> dict[str, Any]:
    return {
        "rows": [
            {"id": "which-cli", "beacon": "beacon (Python)", "loom": "loom / beacon-v2 (Rust)"},
            {"id": "version", "beacon": "v1.6.8 production Python", "loom": "v2.0.0 evolution Rust"},
            {"id": "goal-entry", "beacon": "$beacon-goal / beacon goal", "loom": "$loom-goal / loom goal"},
            {"id": "release", "beacon": "human gate", "loom": "human gate"},
            {"id": "state-root", "beacon": ".beacon", "loom": ".loom"},
        ],
        "legal": ["dual install coexist"],
        "illegal": ["overwrite beacon path", "W4 early default replace"],
    }


def legal_illegal_rows() -> dict[str, Any]:
    return {
        "legal": [
            {"id": "TC-LOOM-BR-LEGAL-01", "path": "dual install", "assert": "beacon and loom binaries coexist"},
        ],
        "illegal": [
            {
                "id": "TC-LOOM-BR-ILLEGAL-01",
                "path": "overwrite",
                "assert": "install must not replace beacon path",
                "code": "I-LOOM-BR-001",
            },
        ],
    }
