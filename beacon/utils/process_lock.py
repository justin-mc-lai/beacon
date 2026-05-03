"""Cross-process file lock helpers for Beacon runtime serialization."""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from beacon.utils.runtime import now_iso

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]


def _write_metadata(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@contextmanager
def project_process_lock(
    project_root: Path,
    *,
    name: str,
    owner: str,
    timeout_seconds: float = 1800.0,
    poll_interval_seconds: float = 0.2,
    metadata: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Acquire a project-scoped advisory process lock.

    The lock is implemented as a POSIX `flock` over `.beacon/locks/<name>.lock`.
    """
    if fcntl is None:  # pragma: no cover
        yield {
            "status": "unsupported",
            "lock_name": name,
            "owner": owner,
        }
        return

    lock_dir = project_root / ".beacon" / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{name}.lock"
    meta_path = lock_dir / f"{name}.json"

    handle = lock_path.open("a+", encoding="utf-8")
    acquired = False
    started = time.monotonic()

    try:
        while True:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                if (time.monotonic() - started) >= timeout_seconds:
                    raise TimeoutError(
                        f"timeout waiting for project lock '{name}' at {lock_path}"
                    )
                time.sleep(max(poll_interval_seconds, 0.05))

        payload = {
            "schema_version": "1.0",
            "lock_name": name,
            "owner": owner,
            "pid": os.getpid(),
            "acquired_at": now_iso(),
            "metadata": metadata or {},
        }
        _write_metadata(meta_path, payload)
        yield {
            "status": "acquired",
            "lock_name": name,
            "lock_path": str(lock_path),
            "metadata_path": str(meta_path),
            "owner": owner,
        }
    finally:
        if acquired:
            try:
                if meta_path.exists():
                    meta_path.unlink()
            except OSError:
                pass
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        handle.close()
