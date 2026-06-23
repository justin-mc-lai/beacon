#!/usr/bin/env python3
"""
generate-host-surfaces.py - Single-spec host surface generator for Beacon.

Reads beacon/version-truth.json as the canonical spec, then ensures each
supported host directory (.cursor, .trae, .windsurf, .codex, .agents ...)
has a correctly-linked skills/beacon symlink pointing to skills/beacon/.

This replaces manual maintenance of 10+ host-specific directories.

Usage:
    python3 scripts/generate-host-surfaces.py           # apply changes
    python3 scripts/generate-host-surfaces.py --dry-run # preview only
    python3 scripts/generate-host-surfaces.py --check   # exit 1 if any surface wrong (for CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_TRUTH_PATH = REPO_ROOT / "beacon" / "version-truth.json"
SKILLS_SOURCE = REPO_ROOT / "skills" / "beacon"

HOSTS = [
    ".agents",
    ".codex",
    ".cursor",
    ".trae",
    ".windsurf",
    ".opencode",
    ".pi",
    ".qoder",
    ".trellis",
    ".reasonix",
]


def load_version_truth() -> dict:
    if not VERSION_TRUTH_PATH.exists():
        print(f"ERROR version-truth.json not found at {VERSION_TRUTH_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(VERSION_TRUTH_PATH) as f:
        return json.load(f)


def get_version(truth: dict) -> str:
    v = truth.get("canonical_version") or truth.get("package_version") or truth.get("version")
    if not v:
        print("ERROR No version key found in version-truth.json", file=sys.stderr)
        sys.exit(1)
    return v


def check_surface(host: str) -> tuple[bool, str]:
    """Return (ok, message) for a host surface."""
    target = REPO_ROOT / host / "skills" / "beacon"
    if not target.exists() and not target.is_symlink():
        return False, f"missing   {target}"
    if target.is_symlink():
        resolved = target.resolve()
        if resolved == SKILLS_SOURCE.resolve():
            return True, f"OK linked correctly"
        return False, f"WARN symlink points to wrong target: {resolved}"
    if target.is_dir():
        return False, f"WARN is a real directory (not a symlink) — may cause duplicate discovery"
    return False, f"WARN unexpected state at {target}"


def generate_surface(host: str, dry_run: bool) -> bool:
    """Create or fix the symlink for one host. Returns True if ok after operation."""
    target_dir = REPO_ROOT / host / "skills"
    target = target_dir / "beacon"

    ok, msg = check_surface(host)
    print(f"  {host:20s}  {msg}")

    if ok:
        return True

    if dry_run:
        print(f"  {'':20s}  -> [DRY RUN] would link {target} -> {SKILLS_SOURCE}")
        return False

    # Real directory (not symlink) — do NOT auto-remove; warn and skip
    if target.exists() and not target.is_symlink():
        print(f"  {'':20s}  BLOCKED real directory present — run:")
        print(f"  {'':20s}  git rm -r --cached {host}/skills/beacon")
        return False

    # Remove stale symlink
    if target.is_symlink():
        target.unlink()

    target_dir.mkdir(parents=True, exist_ok=True)
    target.symlink_to(SKILLS_SOURCE.resolve())
    print(f"  {'':20s}  -> linked OK")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any surface is wrong (CI)")
    args = parser.parse_args()

    if not SKILLS_SOURCE.exists():
        print(f"ERROR Skills source not found: {SKILLS_SOURCE}", file=sys.stderr)
        return 1

    truth = load_version_truth()
    version = get_version(truth)

    print(f"Beacon host surface generator")
    print(f"Canonical version : v{version}")
    print(f"Skills source     : {SKILLS_SOURCE}")
    mode = "dry-run" if args.dry_run else "check-only" if args.check else "apply"
    print(f"Mode              : {mode}")
    print()

    results = []
    for host in HOSTS:
        if args.check:
            ok, msg = check_surface(host)
            print(f"  {host:20s}  {msg}")
            results.append(ok)
        else:
            ok = generate_surface(host, dry_run=args.dry_run)
            results.append(ok)

    total = len(results)
    passed = sum(results)
    print()
    status = "OK" if passed == total else "WARN"
    print(f"{status} {passed}/{total} host surfaces healthy")

    if args.check and passed < total:
        print("Run: python3 scripts/generate-host-surfaces.py  to fix")
        return 1

    print("Run 'beacon doctor verify-install' to confirm runtime health.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
