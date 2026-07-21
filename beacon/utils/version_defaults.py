"""Version defaults for goal (UD-VER) and hotfix baseline (UD-HF).

Normal no-version: planning line > runtime if exists, else patch+1.
Hotfix no-version: pin current_runtime_release_line (no bump).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.versioning import (
    current_runtime_release_version,
    discover_versions,
    load_version_truth,
    normalize_version,
    resolve_runtime_version,
)


def _version_key(version: str) -> tuple[int, ...]:
    text = (normalize_version(version) or "v0.0.0")[1:]
    parts: list[int] = []
    for part in text.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def bump_patch(version: str) -> str:
    """v1.6.8 → v1.6.9 (never silent major/minor)."""
    norm = normalize_version(version) or "v0.0.0"
    parts = norm[1:].split(".")
    while len(parts) < 3:
        parts.append("0")
    try:
        patch = int(parts[2]) + 1
    except ValueError:
        patch = 1
    return f"v{parts[0]}.{parts[1]}.{patch}"


def default_hotfix_baseline(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    runtime = current_runtime_release_version(root)
    source = "current_runtime_release_line"
    if not runtime:
        runtime = normalize_version(str(resolve_runtime_version(root, "auto") or "")) or "v0.0.0"
        source = "runtime_auto"
    return {
        "baseline": runtime,
        "source": source,
        "bump": False,
        "mode": "hotfix",
    }


def default_target_version(project_root: Path | str) -> dict[str, Any]:
    """UD-VER-001: planning preferred else patch+1 of runtime release line."""
    root = Path(project_root).expanduser().resolve()
    runtime = current_runtime_release_version(root) or normalize_version(
        str(resolve_runtime_version(root, "auto") or "")
    ) or "v0.0.0"
    truth = load_version_truth(root)
    planning = []
    for item in truth.get("planning_lines") or []:
        n = normalize_version(str(item or ""))
        if n:
            planning.append(n)
    scanned = discover_versions(root)
    higher = sorted(
        {
            v
            for v in (*planning, *scanned)
            if v and _version_key(v) > _version_key(runtime)
        },
        key=_version_key,
    )
    if higher:
        return {
            "version": higher[0],
            "source": "planning_or_docs_higher_than_runtime",
            "runtime_baseline": runtime,
            "candidates": higher,
            "mode": "normal",
        }
    bumped = bump_patch(runtime)
    return {
        "version": bumped,
        "source": "patch_bump",
        "runtime_baseline": runtime,
        "candidates": [bumped],
        "mode": "normal",
    }


def resolve_goal_version(
    project_root: Path | str,
    requested: str | None,
    *,
    goal_mode: str = "normal",
) -> dict[str, Any]:
    """Resolve version for goal facade.

    - hotfix: always pin production baseline (no bump); requested explicit still wins for docs line
      but baseline separate.
    - normal + auto/empty: default_target_version
    - normal + explicit: use explicit
    """
    root = Path(project_root).expanduser().resolve()
    raw = str(requested or "").strip().lower()
    mode = (goal_mode or "normal").strip().lower()
    if mode == "hotfix":
        base = default_hotfix_baseline(root)
        # docs/work version for hotfix stays on baseline (do not open next patch line)
        return {
            "version": base["baseline"],
            "source": f"hotfix:{base['source']}",
            "goal_mode": "hotfix",
            "hotfix_baseline": base["baseline"],
            "requested": requested or "",
        }
    if raw in {"", "auto", "latest"}:
        target = default_target_version(root)
        return {
            "version": target["version"],
            "source": target["source"],
            "goal_mode": "normal",
            "runtime_baseline": target.get("runtime_baseline"),
            "requested": requested or "auto",
        }
    from beacon.utils.versioning import resolve_target_version

    explicit = resolve_target_version(root, requested)
    return {
        "version": explicit,
        "source": "explicit",
        "goal_mode": mode,
        "requested": requested or "",
    }


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def hotfix_branch_name(baseline: str, utterance: str = "", *, feature: str = "") -> str:
    """Register-style branch: hotfix/v1.6.8-<slug>."""
    base = normalize_version(baseline) or "v0.0.0"
    raw = (feature or utterance or "incident").strip().lower()
    # take first meaningful chunk
    raw = raw.replace("生产：", "").replace("生产:", "")[:80]
    slug = _SLUG_RE.sub("-", raw).strip("-")[:40] or "incident"
    if slug.startswith("hotfix-"):
        slug = slug[len("hotfix-") :]
    return f"hotfix/{base}-{slug}"


def build_hotfix_branch_registry(
    project_root: Path | str,
    *,
    baseline: str,
    utterance: str = "",
    feature: str = "",
    forward_port_target: str = "main",
) -> dict[str, Any]:
    """Plan hotfix branch registration (mainline hotfix, not feature worktree lane)."""
    branch = hotfix_branch_name(baseline, utterance, feature=feature)
    base = normalize_version(baseline) or baseline
    return {
        "schema": "hotfix-branch-registry.v1",
        "branch": branch,
        "baseline_ref": base,
        "not_feature_worktree": True,
        "illegal_lanes": ["beacon/v*/feature-*", "loom/v*/feature-* long-dev lakes"],
        "forward_port_target": forward_port_target or "main",
        "recommended_commands": [
            f"git fetch --tags origin 2>/dev/null || true",
            f"git switch -c {branch} {base} 2>/dev/null || git switch -c {branch} main",
            "# implement on hotfix branch (not feature worktree stream)",
            f"git push -u origin {branch}",
            f"# after human release: forward-port to {forward_port_target or 'main'}",
        ],
        "pre_commit_note": "Business commits allowed on hotfix/*; bare main still blocked (UD-ENF-HF).",
    }
