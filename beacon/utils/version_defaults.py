"""Dual-axis version defaults (UD-VER-AXIS).

Runtime = screwdriver (Beacon toolkit).
Project docs = workpiece serial (product delivery line under docs/beacon/<ver>/).

- external greenfield → v0.0.1 (NOT toolkit v1.6.x)
- external existing → patch+1 of project baseline
- beacon_self monorepo → monorepo planning/patch relative to toolkit release
- hotfix baseline → project production line; self uses current_runtime_release_line
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Literal

from beacon.utils.versioning import (
    current_runtime_release_version,
    discover_versions,
    load_version_truth,
    normalize_version,
    resolve_runtime_version,
)

ProjectKind = Literal["beacon_self", "external_greenfield", "external_existing"]

GREENFIELD_DEFAULT = "v0.0.1"
ALLOW_RUNTIME_AS_DOCS_ENV = "BEACON_ALLOW_RUNTIME_AS_DOCS_VERSION"


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
    """v0.2.3 → v0.2.4 (never silent major/minor)."""
    norm = normalize_version(version) or "v0.0.0"
    parts = norm[1:].split(".")
    while len(parts) < 3:
        parts.append("0")
    try:
        patch = int(parts[2]) + 1
    except ValueError:
        patch = 1
    return f"v{parts[0]}.{parts[1]}.{patch}"


def _toolkit_runtime(project_root: Path) -> str:
    root = Path(project_root).expanduser().resolve()
    # The runtime axis is the Beacon toolkit itself. Only the toolkit monorepo
    # may resolve it from its own version-truth; external projects must never
    # infer runtime from their product docs line under docs/beacon/<ver>/.
    if (root / "beacon" / "version-truth.json").is_file():
        runtime = current_runtime_release_version(root)
        if runtime:
            return runtime
    return normalize_version(str(resolve_runtime_version(root, "auto") or "")) or "v0.0.0"


def runtime_docs_override_enabled() -> bool:
    """True when the user explicitly forces runtime==docs on an external project."""
    return str(os.environ.get(ALLOW_RUNTIME_AS_DOCS_ENV, "")).strip().lower() in {"1", "true", "yes", "on"}


def project_docs_baseline(project_root: Path | str) -> str:
    """Dual-axis docs default when the caller omits -v.

    - external greenfield -> v0.0.1
    - external existing -> project delivery baseline (onboarding or largest docs line)
    - beacon_self -> toolkit runtime line (self docs lane tracks the runtime release)
    """
    root = Path(project_root).expanduser().resolve()
    info = classify_project(root)
    kind = str(info.get("project_kind") or "external_greenfield")
    if kind == "external_greenfield":
        return GREENFIELD_DEFAULT
    if kind == "external_existing":
        return _project_release_baseline(
            root,
            docs_versions=list(info.get("project_docs_versions") or []),
            onboarding_docs=str(info.get("onboarding_docs_version") or ""),
        )
    return _toolkit_runtime(root)


def external_dual_axis_violation(
    project_root: Path | str,
    docs_version: str | None,
    *,
    runtime_version: str | None = None,
) -> dict[str, Any]:
    """Describe whether an external project collapses docs_version onto the runtime axis."""
    root = Path(project_root).expanduser().resolve()
    info = classify_project(root)
    kind = str(info.get("project_kind") or "external_greenfield")
    docs = normalize_version(docs_version) or str(docs_version or "").strip()
    runtime = normalize_version(runtime_version) or _toolkit_runtime(root)
    violated = bool(kind.startswith("external") and docs and docs == runtime)
    override = runtime_docs_override_enabled()
    message = ""
    if violated and not override:
        message = (
            f"dual-axis collapse refused for {kind}: docs_version ({docs}) equals "
            f"Beacon runtime ({runtime}). Project docs must live on the product delivery "
            f"line (e.g. v0.0.1); set {ALLOW_RUNTIME_AS_DOCS_ENV}=1 to force."
        )
    return {
        "violated": violated,
        "blocked": violated and not override,
        "override_enabled": override,
        "project_kind": kind,
        "docs_version": docs,
        "runtime_version": runtime,
        "message": message,
        "override_env": ALLOW_RUNTIME_AS_DOCS_ENV,
    }


def guard_external_docs_axis(
    project_root: Path | str,
    docs_version: str | None,
    *,
    runtime_version: str | None = None,
    command_name: str = "",
) -> None:
    """Refuse external projects that resolve docs_version == Beacon runtime.

    beacon_self is exempt (self docs lane tracks the runtime release). The
    documented override is ALLOW_RUNTIME_AS_DOCS_ENV=1.
    """
    violation = external_dual_axis_violation(project_root, docs_version, runtime_version=runtime_version)
    if violation["blocked"]:
        prefix = f"{command_name}: " if command_name else ""
        raise ValueError(prefix + str(violation["message"]))
def classify_project(project_root: Path | str) -> dict[str, Any]:
    """Classify cwd project for version default policy."""
    root = Path(project_root).expanduser().resolve()
    reasons: list[str] = []

    # Strong self signals: this is the Beacon/Loom toolkit monorepo
    self_signals = [
        (root / "beacon" / "version-truth.json").is_file(),
        (root / "skills" / "beacon" / "beacon-goal" / "SKILL.md").is_file(),
        (root / "pyproject.toml").is_file()
        and "name = \"beacon\"" in (root / "pyproject.toml").read_text(encoding="utf-8", errors="replace")[:2000],
    ]
    if sum(1 for x in self_signals if x) >= 2:
        reasons.append("toolkit_monorepo_signals")
        return {
            "project_kind": "beacon_self",
            "reasons": reasons,
            "project_docs_versions": discover_versions(root),
            "runtime_version": _toolkit_runtime(root),
        }

    docs_versions = discover_versions(root)
    # onboarding / metadata may hold project docs version
    onboarding = root / ".beacon" / "state" / "project-onboarding.json"
    meta = root / ".beacon" / "project-metadata.json"
    onboarding_docs = ""
    if onboarding.is_file():
        try:
            import json

            payload = json.loads(onboarding.read_text(encoding="utf-8"))
            onboarding_docs = normalize_version(str((payload or {}).get("docs_version") or "")) or ""
        except Exception:  # noqa: BLE001
            onboarding_docs = ""

    if docs_versions or onboarding_docs:
        reasons.append("has_project_docs_or_onboarding")
        return {
            "project_kind": "external_existing",
            "reasons": reasons,
            "project_docs_versions": docs_versions,
            "onboarding_docs_version": onboarding_docs,
            "runtime_version": _toolkit_runtime(root),
        }

    reasons.append("no_project_docs_lines")
    return {
        "project_kind": "external_greenfield",
        "reasons": reasons,
        "project_docs_versions": [],
        "runtime_version": _toolkit_runtime(root),
    }


def _project_release_baseline(root: Path, *, docs_versions: list[str], onboarding_docs: str = "") -> str:
    """Best-effort current project delivery baseline (not toolkit runtime)."""
    if onboarding_docs:
        return onboarding_docs
    if not docs_versions:
        return GREENFIELD_DEFAULT
    return sorted(docs_versions, key=_version_key)[-1]


def default_hotfix_baseline(project_root: Path | str) -> dict[str, Any]:
    """Hotfix pins project production baseline; beacon_self uses toolkit release line."""
    root = Path(project_root).expanduser().resolve()
    kind_info = classify_project(root)
    kind = str(kind_info.get("project_kind") or "external_greenfield")
    runtime = str(kind_info.get("runtime_version") or _toolkit_runtime(root))

    if kind == "beacon_self":
        return {
            "baseline": runtime,
            "source": "current_runtime_release_line",
            "bump": False,
            "mode": "hotfix",
            "project_kind": kind,
            "runtime_version": runtime,
            "axis": "project_docs_pinned_to_toolkit_release_for_self",
        }

    docs_versions = list(kind_info.get("project_docs_versions") or [])
    onboarding = str(kind_info.get("onboarding_docs_version") or "")
    if kind == "external_greenfield" and not docs_versions and not onboarding:
        # No production line yet — still return v0.0.1 as placeholder baseline
        return {
            "baseline": GREENFIELD_DEFAULT,
            "source": "greenfield_no_release_yet",
            "bump": False,
            "mode": "hotfix",
            "project_kind": kind,
            "runtime_version": runtime,
            "axis": "project_docs",
            "note": "Greenfield has no production release; prefer normal first ship over hotfix.",
        }

    baseline = _project_release_baseline(root, docs_versions=docs_versions, onboarding_docs=onboarding)
    return {
        "baseline": baseline,
        "source": "project_delivery_baseline",
        "bump": False,
        "mode": "hotfix",
        "project_kind": kind,
        "runtime_version": runtime,
        "axis": "project_docs",
    }


def default_target_version(project_root: Path | str) -> dict[str, Any]:
    """Resolve project_docs_version when user omits -v (normal mode)."""
    root = Path(project_root).expanduser().resolve()
    kind_info = classify_project(root)
    kind = str(kind_info.get("project_kind") or "external_greenfield")
    runtime = str(kind_info.get("runtime_version") or _toolkit_runtime(root))

    if kind == "external_greenfield":
        return {
            "version": GREENFIELD_DEFAULT,
            "source": "external_greenfield_default",
            "project_kind": kind,
            "runtime_version": runtime,
            "runtime_baseline": runtime,
            "axis": "project_docs",
            "mode": "normal",
            "principle": "Runtime is screwdriver; project serial starts at v0.0.1",
        }

    if kind == "external_existing":
        docs_versions = list(kind_info.get("project_docs_versions") or [])
        onboarding = str(kind_info.get("onboarding_docs_version") or "")
        baseline = _project_release_baseline(root, docs_versions=docs_versions, onboarding_docs=onboarding)
        target = bump_patch(baseline)
        return {
            "version": target,
            "source": "external_project_patch_bump",
            "project_kind": kind,
            "project_baseline": baseline,
            "runtime_version": runtime,
            "runtime_baseline": runtime,
            "axis": "project_docs",
            "mode": "normal",
            "principle": "patch+1 relative to project delivery baseline, not toolkit runtime",
        }

    # beacon_self: monorepo planning / docs higher than toolkit release, else patch toolkit release
    truth = load_version_truth(root)
    planning: list[str] = []
    for item in truth.get("planning_lines") or []:
        n = normalize_version(str(item or ""))
        if n:
            planning.append(n)
    scanned = discover_versions(root)
    higher = sorted(
        {v for v in (*planning, *scanned) if v and _version_key(v) > _version_key(runtime)},
        key=_version_key,
    )
    if higher:
        return {
            "version": higher[0],
            "source": "beacon_self_planning_or_docs_higher_than_runtime",
            "project_kind": kind,
            "runtime_version": runtime,
            "runtime_baseline": runtime,
            "candidates": higher,
            "axis": "project_docs_self",
            "mode": "normal",
        }
    bumped = bump_patch(runtime)
    return {
        "version": bumped,
        "source": "beacon_self_patch_bump_of_runtime_release",
        "project_kind": kind,
        "runtime_version": runtime,
        "runtime_baseline": runtime,
        "candidates": [bumped],
        "axis": "project_docs_self",
        "mode": "normal",
    }


def resolve_goal_version(
    project_root: Path | str,
    requested: str | None,
    *,
    goal_mode: str = "normal",
) -> dict[str, Any]:
    """Resolve goal project_docs version + always report runtime axis."""
    root = Path(project_root).expanduser().resolve()
    raw = str(requested or "").strip().lower()
    mode = (goal_mode or "normal").strip().lower()
    runtime = _toolkit_runtime(root)
    kind_info = classify_project(root)

    if mode == "hotfix":
        base = default_hotfix_baseline(root)
        return {
            "version": base["baseline"],
            "source": f"hotfix:{base.get('source')}",
            "goal_mode": "hotfix",
            "hotfix_baseline": base["baseline"],
            "project_kind": base.get("project_kind") or kind_info.get("project_kind"),
            "runtime_version": runtime,
            "project_docs_version": base["baseline"],
            "axis": {
                "runtime_version": runtime,
                "project_docs_version": base["baseline"],
            },
            "requested": requested or "",
        }

    if raw in {"", "auto", "latest"}:
        target = default_target_version(root)
        ver = str(target.get("version") or GREENFIELD_DEFAULT)
        return {
            "version": ver,
            "source": target.get("source"),
            "goal_mode": "normal",
            "project_kind": target.get("project_kind") or kind_info.get("project_kind"),
            "runtime_version": runtime,
            "project_docs_version": ver,
            "runtime_baseline": target.get("runtime_baseline") or runtime,
            "axis": {
                "runtime_version": runtime,
                "project_docs_version": ver,
            },
            "requested": requested or "auto",
            "principle": target.get("principle") or "",
        }

    from beacon.utils.versioning import resolve_target_version

    explicit = resolve_target_version(root, requested)
    return {
        "version": explicit,
        "source": "explicit",
        "goal_mode": mode,
        "project_kind": kind_info.get("project_kind"),
        "runtime_version": runtime,
        "project_docs_version": explicit,
        "axis": {
            "runtime_version": runtime,
            "project_docs_version": explicit,
        },
        "requested": requested or "",
    }


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def hotfix_branch_name(baseline: str, utterance: str = "", *, feature: str = "") -> str:
    base = normalize_version(baseline) or "v0.0.0"
    raw = (feature or utterance or "incident").strip().lower()
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
    branch = hotfix_branch_name(baseline, utterance, feature=feature)
    base = normalize_version(baseline) or baseline
    kind = classify_project(project_root).get("project_kind")
    return {
        "schema": "hotfix-branch-registry.v1",
        "branch": branch,
        "baseline_ref": base,
        "project_kind": kind,
        "not_feature_worktree": True,
        "illegal_lanes": ["beacon/v*/feature-*", "loom/v*/feature-* long-dev lakes"],
        "forward_port_target": forward_port_target or "main",
        "recommended_commands": [
            "git fetch --tags origin 2>/dev/null || true",
            f"git switch -c {branch} {base} 2>/dev/null || git switch -c {branch} main",
            "# implement on hotfix branch (not feature worktree stream)",
            f"git push -u origin {branch}",
            f"# after human release: forward-port to {forward_port_target or 'main'}",
        ],
        "pre_commit_note": "Business commits allowed on hotfix/*; bare main still blocked (UD-ENF-HF).",
        "axis_note": "baseline is project_docs production line; toolkit runtime is separate screwdriver version",
    }
