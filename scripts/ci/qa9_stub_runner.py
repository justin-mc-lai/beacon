#!/usr/bin/env python3
"""Deterministic QA9 stub command for strict acceptance smoke.

This runner creates:
- junit.xml at BEACON_JUNIT_PATH
- optional compatibility pair evidence at BEACON_COMPAT_EVIDENCE_PATH
- structured assertion marker in stdout
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _write_junit(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '<testsuite name="beacon-qa9-stub" tests="1" failures="0" errors="0" skipped="0"></testsuite>\n',
        encoding="utf-8",
    )


def _write_compatibility_evidence(path: Path) -> None:
    raw_pairs = os.environ.get("BEACON_COMPAT_REQUIRED_PAIRS", "[]")
    try:
        required_pairs = json.loads(raw_pairs)
    except Exception:  # noqa: BLE001
        required_pairs = []
    if not isinstance(required_pairs, list):
        required_pairs = []
    normalized = []
    for item in required_pairs:
        if not isinstance(item, dict):
            continue
        browser = str(item.get("browser") or "").strip().lower()
        device = str(item.get("device") or "").strip().lower()
        if browser and device:
            normalized.append({"browser": browser, "device": device})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "source": "qa9_stub_runner",
                "run_id": os.environ.get("BEACON_RUN_ID", ""),
                "executed_pairs": normalized,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    junit_path = Path(os.environ.get("BEACON_JUNIT_PATH", ".beacon/junit.xml"))
    _write_junit(junit_path)

    compat_path_raw = str(os.environ.get("BEACON_COMPAT_EVIDENCE_PATH", "")).strip()
    if compat_path_raw:
        _write_compatibility_evidence(Path(compat_path_raw))

    # Structured assertion marker consumed by auto-test parser.
    print("BEACON_ASSERTIONS=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

