"""Architecture blueprint gate (issue #19, v1.6.17 batch2 P1).

Fail-closed when execution/architecture-blueprint.md is placeholder (all none).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.feature_package import package_paths
from beacon.utils.versioning import resolve_target_version

REASON_ARCH_INCOMPLETE = "architecture_blueprint_incomplete"
BLUEPRINT_FIELDS = ("Source Refs", "Must Change", "Can Reuse", "No-Expand Guardrails", "Compatibility Rules")

def _read_blueprint(project_root: Path, version: str) -> str:
    p = project_root / "docs" / "beacon" / version / "execution" / "architecture-blueprint.md"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")

def check_architecture_blueprint(project_root: Path, *, version: str = "auto") -> dict[str,Any]:
    root = Path(project_root).expanduser().resolve()
    ver = resolve_target_version(root, version)
    text = _read_blueprint(root, ver)
    if not text:
        return {"blocked": False, "status":"not_required", "reason_code":"", "findings":[]}
    # ponytail: treat all-none blueprint as incomplete; real blueprint must fill at least one field
    none_count = sum(1 for f in BLUEPRINT_FIELDS if re.search(rf"###\s*{re.escape(f)}\s*\n- none", text, re.I))
    if none_count >= len(BLUEPRINT_FIELDS):
        return {"blocked": True, "status":"blocked", "reason_code": REASON_ARCH_INCOMPLETE,
                "findings":[{"kind":"blueprint_placeholder","text":"architecture-blueprint.md is placeholder (all none)"}]}
    return {"blocked": False, "status":"pass", "reason_code":"", "findings":[]}
