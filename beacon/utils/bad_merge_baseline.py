"""Bad-merge rate baseline (v1.6.16 P5): measure auto-merge quality.

After auto-merge was enabled (v1.6.15, global-boundaries §4.1), there was no
baseline for "how often does a merged commit get reverted". This module scans
git history for merges into main and their reverts, computes a bad-merge rate
over a time window, and emits a baseline report with confidence.

Observation only — it never changes merge behavior.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA_BAD_MERGE = "bad-merge-baseline.v1"

REVERT_RE = re.compile(r"^Revert \"?(?P<reverted_title>.+?)\"?\s*$", re.IGNORECASE)
REVERT_FOOTER_RE = re.compile(r"This reverts commit\s+(?P<sha>[0-9a-f]{7,40})", re.IGNORECASE)


def _git(project_root: Path, args: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(project_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def collect_merges(project_root: Path, *, since: str | None = None, branch: str = "main") -> list[dict[str, str]]:
    """Scan merge commits into main (v1.6.15 era) and their revert status."""
    args = ["log", f"--merges", f"--pretty=format:%H|%s|%ad", f"--date=iso"]
    if since:
        args.append(f"--since={since}")
    args.append(branch)
    merges: list[dict[str, str]] = []
    for line in _git(project_root, args):
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, subject, date = parts[0].strip(), parts[1].strip(), parts[2].strip()
        merges.append({"sha": sha, "subject": subject, "date": date, "revert_of": "", "is_revert": False})
    # map reverts to their target
    revert_lines = _git(project_root, ["log", "--all", "--grep=Revert", "--pretty=format:%H|%s|%b"])
    for line in revert_lines:
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, subject, body = parts[0].strip(), parts[1].strip(), parts[2].strip()
        footer = REVERT_FOOTER_RE.search(body)
        target = footer.group("sha") if footer else ""
        for merge in merges:
            if target and merge["sha"].startswith(target):
                merge["revert_of"] = sha
                merge["is_revert"] = True
    return merges


def compute_bad_merge_rate(
    project_root: Path,
    *,
    since: str | None = None,
    window_days: int = 30,
    branch: str = "main",
    min_merges: int = 5,
) -> dict[str, Any]:
    """Compute bad-merge rate = reverted merges / total merges in window."""
    merges = collect_merges(project_root, since=since, branch=branch)
    if not merges:
        return {
            "schema": SCHEMA_BAD_MERGE,
            "status": "warned",
            "reason_code": "bad_merge_no_merges",
            "merges": 0,
            "reverts": 0,
            "bad_merge_rate": 0.0,
            "window_days": window_days,
            "confidence": "low",
        }
    total = len(merges)
    reverts = sum(1 for m in merges if m["is_revert"])
    rate = round(reverts / float(total), 4)
    confidence = "high" if total >= min_merges else "low"
    return {
        "schema": SCHEMA_BAD_MERGE,
        "status": "reported" if confidence == "high" else "warned",
        "reason_code": "" if confidence == "high" else "bad_merge_low_confidence",
        "merges": total,
        "reverts": reverts,
        "bad_merge_rate": rate,
        "window_days": window_days,
        "branch": branch,
        "confidence": confidence,
        "reverted_merges": [m["sha"] for m in merges if m["is_revert"]],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def emit_baseline_report(
    project_root: Path,
    *,
    since: str | None = None,
    window_days: int = 30,
    branch: str = "main",
    min_merges: int = 5,
) -> dict[str, Any]:
    """Produce a comparable baseline report (merges/reverts/rate/window/confidence)."""
    baseline = compute_bad_merge_rate(
        project_root,
        since=since,
        window_days=window_days,
        branch=branch,
        min_merges=min_merges,
    )
    baseline["report"] = {
        "merges": baseline["merges"],
        "reverts": baseline["reverts"],
        "bad_merge_rate": baseline["bad_merge_rate"],
        "window_days": baseline["window_days"],
        "confidence": baseline["confidence"],
        "baseline_id": f"bad-merge-{branch}-{window_days}d",
    }
    return baseline
