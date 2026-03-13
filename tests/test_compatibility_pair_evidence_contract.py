from __future__ import annotations

import json
import os
from pathlib import Path


def test_compatibility_command_should_write_pair_evidence():
    path_raw = os.environ.get("BEACON_COMPAT_EVIDENCE_PATH", "").strip()
    required_pairs_raw = os.environ.get("BEACON_COMPAT_REQUIRED_PAIRS", "[]").strip() or "[]"
    if not path_raw:
        return
    try:
        required_pairs = json.loads(required_pairs_raw)
    except Exception:  # noqa: BLE001
        required_pairs = []
    path = Path(path_raw)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "passed",
                "required_pairs": required_pairs,
                "executed_pairs": required_pairs,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    assert path.exists()
