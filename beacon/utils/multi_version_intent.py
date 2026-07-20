"""Multi-version intent recognition and dual-track execution planning.

Supports utterances like:
  - v1.6.8\\v2.0.0
  - v1.6.8/v2.0.0
  - v1.6.8 + v2.0.0
  - 双轨 v1.6.8 与 v2.0.0
  - 并行修复 v1.6.8 和 v2.0.0

Planning only assigns lakes/tracks; does not self-certify complete/release.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.story_state import feature_slug

SCHEMA_VERSION = "1.0"

# Capture vX.Y or vX.Y.Z (optional leading v)
_VERSION_TOKEN = re.compile(r"(?<![A-Za-z0-9])v?(?P<ver>\d+\.\d+(?:\.\d+)?)(?![0-9])", re.I)

# Explicit multi-version separators between version tokens
_MULTI_SEP = re.compile(
    r"(?P<a>v?\d+\.\d+(?:\.\d+)?)\s*(?:\\|\/|\||\+|＆|&|和|与|、|,|，)\s*(?P<b>v?\d+\.\d+(?:\.\d+)?)",
    re.I,
)

_PARALLEL_MARKERS = (
    "双轨",
    "并行",
    "parallel",
    "dual-track",
    "dual track",
    "multi-version",
    "多版本",
    "同时",
    "一并",
)

# Default dual-track repair lakes when user asks for dual-track fix without naming lakes
DEFAULT_TRACK_LAKES: dict[str, list[str]] = {
    "v1.6.8": [
        "beacon-worktree-progressive-skill-flow-v168",
        "beacon-longrun-contract-align-v168",
        "beacon-version-fleet-ops-v168",
    ],
    "v2.0.0": [
        "loom-git-worktree-implement-harness",
        "beacon-v2-goal-durable-longrun",
        "beacon-v2-version-fleet-ops",
    ],
}

TRACK_LABELS = {
    "v1.6.8": "production_beacon",
    "v2.0.0": "evolution_loom",
}


def _norm_version(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if not text.lower().startswith("v"):
        text = f"v{text}"
    # normalize v1.6 -> v1.6.0? keep as parsed; prefer three-part if two-part known
    parts = text[1:].split(".")
    if len(parts) == 2:
        # keep two-part for fleet lines that use v1.6.8 style only when third present
        return f"v{parts[0]}.{parts[1]}"
    return f"v{'.'.join(parts)}"


def extract_versions(utterance: str) -> list[str]:
    """Ordered unique versions found in utterance."""
    found: list[str] = []
    for m in _VERSION_TOKEN.finditer(str(utterance or "")):
        ver = _norm_version(m.group("ver"))
        if ver and ver not in found:
            found.append(ver)
    return found


def detect_multi_version_intent(utterance: str) -> dict[str, Any]:
    """Parse multi-version intent from one sentence.

    Returns schema:
      detected, parallel, versions[], separators[], markers[], confidence
    """
    text = str(utterance or "")
    versions = extract_versions(text)
    seps: list[str] = []
    for m in _MULTI_SEP.finditer(text):
        seps.append(m.group(0))
    markers = [m for m in _PARALLEL_MARKERS if m.lower() in text.lower() or m in text]
    # Backslash dual form explicit (CLI style v1.6.8\v2.0.0)
    if "\\" in text and len(versions) >= 2:
        if "backslash" not in seps:
            seps.append("backslash")
    parallel = len(versions) >= 2 and (
        bool(seps) or bool(markers) or "双轨" in text or "parallel" in text.lower()
    )
    detected = len(versions) >= 2 or (len(versions) == 1 and bool(markers) and "双轨" in text)
    if len(versions) >= 2:
        detected = True
    confidence = 0
    if len(versions) >= 2:
        confidence += 50
    if seps:
        confidence += 25
    if markers:
        confidence += 25
    confidence = min(100, confidence)
    return {
        "schema_version": SCHEMA_VERSION,
        "detected": detected and len(versions) >= 1,
        "parallel": parallel if len(versions) >= 2 else False,
        "versions": versions,
        "separators": seps,
        "markers": markers,
        "confidence": confidence,
        "utterance": text[:500],
    }


def _default_lakes_for_version(version: str) -> list[str]:
    ver = _norm_version(version)
    if ver in DEFAULT_TRACK_LAKES:
        return list(DEFAULT_TRACK_LAKES[ver])
    # fuzzy: v2* -> v2.0.0 defaults
    if ver.startswith("v2."):
        return list(DEFAULT_TRACK_LAKES["v2.0.0"])
    if ver.startswith("v1.6.8"):
        return list(DEFAULT_TRACK_LAKES["v1.6.8"])
    return []


def _discover_program_lakes(project_root: Path, version: str) -> list[str]:
    """Best-effort lakes from program feature-graph if present."""
    root = Path(project_root)
    programs = root / "docs" / "beacon" / version / "programs"
    if not programs.is_dir():
        return []
    lakes: list[str] = []
    for graph in programs.glob("*/feature-graph.json"):
        try:
            import json

            data = json.loads(graph.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for lake in data.get("lakes") or data.get("topology_order") or []:
            if isinstance(lake, dict):
                slug = str(lake.get("slug") or lake.get("feature") or "").strip()
            else:
                slug = str(lake).strip()
            if slug and slug not in lakes:
                lakes.append(feature_slug(slug))
        if lakes:
            break
    return lakes


def build_multi_version_execution_plan(
    project_root: Path,
    utterance: str,
    *,
    explicit_versions: list[str] | None = None,
    lake_overrides: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Decompose multi-version intent into per-track lake assignment + parallel policy."""
    intent = detect_multi_version_intent(utterance)
    versions = [_norm_version(v) for v in (explicit_versions or intent.get("versions") or []) if str(v).strip()]
    # dedupe preserve order
    seen: set[str] = set()
    ordered: list[str] = []
    for v in versions:
        if v not in seen:
            seen.add(v)
            ordered.append(v)

    tracks: list[dict[str, Any]] = []
    for ver in ordered:
        lakes = list((lake_overrides or {}).get(ver) or [])
        if not lakes:
            lakes = _default_lakes_for_version(ver)
        if not lakes:
            lakes = _discover_program_lakes(project_root, ver)[:6]
        track = {
            "version": ver,
            "track_label": TRACK_LABELS.get(ver, "custom"),
            "public_entry": "loom-goal" if ver.startswith("v2.") else "beacon-goal",
            "cli": "loom" if ver.startswith("v2.") else "beacon",
            "lakes": lakes,
            "worktree_mode": "main_star_satellite_pool" if len(lakes) > 1 else "single_worktree",
            "branch_pattern": f"beacon/{ver}/<feature-slug>",
            "may_write_truth_on_main_only": True,
            "implement_requires_admission": True,
            "status": "planned",
        }
        tracks.append(track)

    parallel = bool(intent.get("parallel")) and len(tracks) >= 2
    return {
        "schema_version": SCHEMA_VERSION,
        "intent": intent,
        "parallel_tracks": parallel,
        "tracks": tracks,
        "orchestration": {
            "mode": "parallel_version_tracks" if parallel else "single_version",
            "join_policy": "all_tracks_await_verifier_then_human_release",
            "forbidden": [
                "self_complete_any_track",
                "auto_release",
                "implement_on_main_without_admission",
                "create_parent_branch_with_children",
            ],
            "admit_rule": "leaf_only_beacon/<version>/<feature-slug>",
        },
        "recommended_commands": [
            {
                "version": t["version"],
                "admit": [
                    f"beacon workspace admit -p . -v {t['version']} --feature {lake} --json"
                    for lake in (t["lakes"][:2] or ["<feature>"])
                ],
                "goal": f"{t['cli']} goal run \"...\" --project . --version {t['version']}",
            }
            for t in tracks
        ],
    }


def apply_multi_version_to_goal_payload(
    project_root: Path,
    payload: dict[str, Any],
    utterance: str,
) -> dict[str, Any]:
    """Attach multi_version_plan onto goal run payload when detected."""
    plan = build_multi_version_execution_plan(project_root, utterance)
    if not plan.get("tracks"):
        return payload
    intent = plan.get("intent") or {}
    if not intent.get("detected") and len(plan.get("tracks") or []) < 2:
        return payload
    payload["multi_version_plan"] = plan
    payload["multi_version"] = {
        "enabled": True,
        "parallel": plan.get("parallel_tracks"),
        "versions": [t["version"] for t in plan.get("tracks") or []],
    }
    # If primary version empty, prefer first track
    if not payload.get("version") and plan.get("tracks"):
        payload["version"] = plan["tracks"][0]["version"]
    # Expand lakes when empty and multi-version parallel
    if plan.get("parallel_tracks") and not payload.get("lakes"):
        merged: list[str] = []
        for t in plan["tracks"]:
            for lake in t.get("lakes") or []:
                tagged = f"{t['version']}::{lake}"
                if tagged not in merged:
                    merged.append(tagged)
        payload["lakes"] = merged
        payload["one_lake_one_satellite"] = True
    return payload
