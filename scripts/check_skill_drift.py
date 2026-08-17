#!/usr/bin/env python3
"""Check Beacon skill drift across repo, local Claude installs, and legacy Codex duplicates."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "beacon" / "utils" / "skill_drift.py"
SPEC = importlib.util.spec_from_file_location("beacon_skill_drift", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise SystemExit(f"unable to load skill drift module from {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_skill_drift_report = MODULE.build_skill_drift_report


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=str(ROOT), help="Beacon project root")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = build_skill_drift_report(Path(args.project_root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Beacon Skill Drift Check")
        print("=" * 24)
        print(f"status: {payload['status']}")
        print(f"drift_count: {payload['drift_count']}")
        print(f"missing_count: {payload['missing_count']}")
        for item in payload.get("checks", []):
            if not isinstance(item, dict):
                continue
            print(f"- {item.get('name')}: {item.get('status')}")
    return 0 if str(payload.get("status")) == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
