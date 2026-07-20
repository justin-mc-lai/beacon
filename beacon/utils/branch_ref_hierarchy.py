"""Git branch ref hierarchy hard gate (UD-BR-001..005).

Git cannot host both ref P and P/child. Beacon implement lanes must be leaf refs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug

REASON_HIERARCHY = "branch_ref_hierarchy_collision"
REASON_NO_MAIN_FALLBACK = "implement_on_canonical_without_admission"
REASON_ADMIT_REQUIRED = "workspace_admission_required_for_implement"


def _git(root: Path, *args: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return 1, "", str(exc)
    return int(proc.returncode or 0), str(proc.stdout or ""), str(proc.stderr or "")


def list_local_branches(project_root: Path) -> list[str]:
    code, out, _ = _git(project_root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    if code != 0:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def hierarchy_collision(project_root: Path, branch: str) -> dict[str, Any]:
    """Return collision detail if creating/checking out branch would violate ref hierarchy."""
    name = str(branch or "").strip()
    if not name:
        return {"collides": False, "reason_code": "", "conflicts": []}
    branches = list_local_branches(project_root)
    conflicts: list[str] = []
    # children of name exist → cannot create name as leaf parent
    prefix = name + "/"
    for b in branches:
        if b == name:
            continue
        if b.startswith(prefix):
            conflicts.append(b)
        # name is child of existing leaf parent
        if name.startswith(b + "/"):
            conflicts.append(b)
    if conflicts:
        return {
            "collides": True,
            "reason_code": REASON_HIERARCHY,
            "branch": name,
            "conflicts": sorted(set(conflicts)),
            "summary": f"git ref hierarchy collision for {name}: {', '.join(sorted(set(conflicts))[:8])}",
        }
    return {"collides": False, "reason_code": "", "branch": name, "conflicts": []}


def is_program_aggregation_branch(branch: str) -> bool:
    """True for beacon/<version> with no further slash segments (aggregation-only)."""
    parts = [p for p in str(branch or "").strip().split("/") if p]
    # beacon/v2.0.0 → 2 parts, second looks like version
    if len(parts) != 2:
        return False
    if parts[0] not in {"beacon", "loom"}:
        return False
    ver = parts[1]
    return ver.startswith("v") and any(ch.isdigit() for ch in ver)


def leaf_feature_branch(*, version: str, feature: str, pattern: str = "") -> str:
    """Always produce a leaf branch name (scheme A): beacon/<version>/<feature-slug>."""
    slug = feature_slug(feature)
    pat = str(pattern or "").strip()
    if pat:
        rendered = pat.replace("<feature-slug>", slug).replace("{feature-slug}", slug)
        # Pattern without slug placeholder that is aggregation-only → append slug
        if is_program_aggregation_branch(rendered) or (
            "<feature" not in pat.lower() and "{feature" not in pat.lower() and is_program_aggregation_branch(rendered)
        ):
            return f"{rendered.rstrip('/')}/{slug}"
        # Pattern is aggregation-like beacon/vX without placeholder
        if rendered.count("/") == 1 and rendered.startswith(("beacon/", "loom/")) and slug not in rendered.split("/")[-1]:
            # if last segment is version-like, append
            last = rendered.split("/")[-1]
            if last.startswith("v") and slug not in rendered:
                return f"{rendered}/{slug}"
        if slug and rendered.endswith("/" + slug) or rendered.endswith(slug):
            return rendered
        if "<feature" not in pat.lower() and "{feature" not in pat.lower() and slug not in rendered:
            return f"{rendered.rstrip('/')}/{slug}"
        return rendered
    ver = str(version or "").strip() or "v0.0.0"
    return f"beacon/{ver}/{slug}"


def ensure_leaf_checkout_branch(
    project_root: Path,
    *,
    version: str,
    feature: str,
    candidate: str,
    pattern: str = "",
) -> dict[str, Any]:
    """Rewrite aggregation or colliding candidates to a safe leaf branch."""
    leaf = leaf_feature_branch(version=version, feature=feature, pattern=pattern)
    cand = str(candidate or "").strip()
    chosen = leaf
    rewrote = False
    if not cand or is_program_aggregation_branch(cand):
        chosen = leaf
        rewrote = cand != chosen
    else:
        chosen = cand
        # if candidate collides, force leaf
        hit = hierarchy_collision(project_root, chosen)
        if hit.get("collides"):
            chosen = leaf
            rewrote = True
            # if leaf also collides (rare: leaf is parent of something), report
            hit2 = hierarchy_collision(project_root, chosen)
            if hit2.get("collides") and chosen in (hit2.get("conflicts") or []):
                pass
            elif hit2.get("collides") and any(
                str(c).startswith(chosen + "/") for c in (hit2.get("conflicts") or [])
            ):
                return {
                    "ok": False,
                    "reason_code": REASON_HIERARCHY,
                    "feature_branch": chosen,
                    "aggregation_branch": cand if is_program_aggregation_branch(cand) else "",
                    "rewrote": rewrote,
                    "collision": hit2,
                }
    hit = hierarchy_collision(project_root, chosen)
    # Creating a new leaf is OK even if parent doesn't exist; only block if children of chosen exist
    children = [c for c in (hit.get("conflicts") or []) if str(c).startswith(chosen + "/")]
    if children:
        return {
            "ok": False,
            "reason_code": REASON_HIERARCHY,
            "feature_branch": chosen,
            "aggregation_branch": cand if is_program_aggregation_branch(cand) else "",
            "rewrote": rewrote,
            "collision": {**hit, "conflicts": children},
        }
    return {
        "ok": True,
        "reason_code": "",
        "feature_branch": chosen,
        "aggregation_branch": cand if is_program_aggregation_branch(cand) else (
            f"beacon/{version}" if str(version).startswith("v") else ""
        ),
        "rewrote": rewrote or (cand != chosen),
        "collision": {"collides": False, "conflicts": []},
    }
