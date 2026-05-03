from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from beacon.utils.process_lock import project_process_lock


def test_project_process_lock_should_timeout_when_already_held(tmp_path: Path) -> None:
    with project_process_lock(tmp_path, name="qa-feature-aware", owner="holder"):
        with pytest.raises(TimeoutError):
            with project_process_lock(
                tmp_path,
                name="qa-feature-aware",
                owner="contender",
                timeout_seconds=0.1,
                poll_interval_seconds=0.05,
            ):
                pass


def test_project_process_lock_should_serialize_followup_acquisition(tmp_path: Path) -> None:
    events: list[str] = []

    def worker() -> None:
        with project_process_lock(
            tmp_path,
            name="qa-feature-aware",
            owner="worker",
            timeout_seconds=1.0,
            poll_interval_seconds=0.05,
        ):
            events.append("worker-acquired")

    with project_process_lock(tmp_path, name="qa-feature-aware", owner="holder"):
        thread = threading.Thread(target=worker)
        thread.start()
        time.sleep(0.15)
        assert events == []
    thread.join(timeout=2.0)
    assert events == ["worker-acquired"]
