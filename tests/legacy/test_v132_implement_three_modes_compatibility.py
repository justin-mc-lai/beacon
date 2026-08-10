from __future__ import annotations

import json
import os
from pathlib import Path

from beacon.adapters import browser_use_runner
from beacon.utils.browser_task_compiler import build_browser_task, write_browser_task


def _write_pass_script(root: Path, name: str = "compat-pass.sh") -> Path:
    script = root / name
    script.write_text("#!/bin/sh\nset -eu\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    return script


def test_v132_compatibility_browser_runner_should_accept_compiled_task_and_write_artifacts(tmp_path: Path):
    tc_dir = tmp_path / "evidence" / "tc"
    fallback = _write_pass_script(tmp_path)
    layer_dir = tc_dir / "explore"
    layer_dir.mkdir(parents=True, exist_ok=True)
    task = build_browser_task(
        item={
            "feature": "beacon-v1.3.2-implement-three-modes-and-iterative-browser-qa",
            "ac_id": "AC-007",
            "tc_id": "TC-033-COMPAT",
            "source_tc_id": "TC-033",
            "scenario_id": "SC-033",
            "scenario_family": "compatibility",
            "assertion": "跨浏览器兼容性验证可以通过 browser runner fallback 稳定落证",
            "exploratory_runner": "browser-use",
            "deterministic_runner": "playwright",
            "replay_required": False,
        },
        qa_type="compatibility",
        mode="compatibility",
        project_root=tmp_path,
    )
    task_path = write_browser_task(tc_dir=tc_dir, payload=task)
    original_layer_dir = os.environ.get("BEACON_LAYER_DIR")
    os.environ["BEACON_LAYER_DIR"] = str(layer_dir)
    try:
        code = browser_use_runner.main(
            [
                "--mode",
                "compatibility",
                "--task-file",
                str(task_path),
                "--fallback-cmd",
                f"sh {fallback}",
                "--project-root",
                str(tmp_path),
            ]
        )
    finally:
        if original_layer_dir is None:
            os.environ.pop("BEACON_LAYER_DIR", None)
        else:
            os.environ["BEACON_LAYER_DIR"] = original_layer_dir
    assert code == 0
    report = json.loads((layer_dir / "browser-runner-report.json").read_text(encoding="utf-8"))
    assert report["artifact_refs"]["task_ref"]
    assert report["mode"] == "compatibility"
    assert (layer_dir / "action-transcript.json").exists()
