"""Chrome extension e2e helpers for Beacon QA browser layer (v1.6.4)."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

HEADLESS_NEW_FLAG = "--headless=new"
LEGACY_HEADLESS_FLAG = "--headless"

REASON_EXTENSION_LOAD_FAILED = "extension_load_failed"
REASON_EXTENSION_ID_MISMATCH = "extension_id_mismatch"
REASON_SERVICE_WORKER_NOT_READY = "service_worker_not_ready"


def build_chrome_launch_args(*, extension_path: str, headless: bool = True) -> list[str]:
    args = [f"--load-extension={extension_path}"]
    if headless:
        args.append(HEADLESS_NEW_FLAG)
    return args


def validate_extension_package(path: Path) -> tuple[bool, str]:
    if not path.exists() or not path.is_dir():
        return False, REASON_EXTENSION_LOAD_FAILED
    manifest_path = path / "manifest.json"
    if not manifest_path.exists():
        return False, REASON_EXTENSION_LOAD_FAILED
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False, REASON_EXTENSION_LOAD_FAILED
    if not isinstance(payload, dict):
        return False, REASON_EXTENSION_LOAD_FAILED
    return True, ""


def compute_extension_id_from_manifest(manifest: dict[str, Any]) -> str:
    key_value = str(manifest.get("key") or "").strip()
    if not key_value:
        return ""
    return compute_extension_id_from_key(key_value)


def compute_extension_id_from_key(key_pem: str) -> str:
    raw = str(key_pem or "").strip()
    if not raw:
        return ""
    try:
        decoded = base64.b64decode(raw)
    except Exception:  # noqa: BLE001
        decoded = raw.encode("utf-8")
    digest = hashlib.sha256(decoded).digest()[:16]
    return "".join(chr(0x61 + (byte >> 4)) + chr(0x61 + (byte & 0x0F)) for byte in digest)


def extension_page_url(extension_id: str, page: str = "index.html") -> str:
    ext_id = str(extension_id or "").strip()
    page_name = str(page or "index.html").strip().lstrip("/")
    return f"chrome-extension://{ext_id}/{page_name}"


def popup_url(extension_id: str, *, tab_id: int | None = None) -> str:
    base = extension_page_url(extension_id, "popup.html")
    if tab_id is not None:
        return f"{base}?tab={tab_id}"
    return base


def validate_extension_runner_context(
    *,
    extension_path: str,
    expected_extension_id: str = "",
    service_worker_ready: bool = True,
) -> dict[str, Any]:
    path = Path(extension_path)
    ok, reason = validate_extension_package(path)
    if not ok:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": reason,
        }
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    extension_id = compute_extension_id_from_manifest(manifest)
    if expected_extension_id and extension_id != expected_extension_id:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_EXTENSION_ID_MISMATCH,
            "extension_id": extension_id,
            "expected_extension_id": expected_extension_id,
        }
    if not service_worker_ready:
        return {
            "schema_version": "1.0",
            "status": "blocked",
            "blocked": True,
            "reason_code": REASON_SERVICE_WORKER_NOT_READY,
            "extension_id": extension_id,
        }
    return {
        "schema_version": "1.0",
        "status": "pass",
        "blocked": False,
        "reason_code": "",
        "extension_id": extension_id,
        "launch_args": build_chrome_launch_args(extension_path=str(path)),
    }


def validate_extension_browser_evidence(payload: dict[str, Any] | None) -> dict[str, Any]:
    item = payload if isinstance(payload, dict) else {}
    runner = str(item.get("runner") or item.get("browser_runner") or "").strip().lower()
    if runner != "playwright-extension":
        return {"schema_version": "1.0", "status": "not_applicable", "blocked": False}
    extension_path = str(item.get("extension_path") or item.get("load_extension") or "").strip()
    context = validate_extension_runner_context(
        extension_path=extension_path,
        expected_extension_id=str(item.get("expected_extension_id") or "").strip(),
        service_worker_ready=bool(item.get("service_worker_ready", True)),
    )
    extension_axes = ("extension_page", "service_worker", "popup")
    present_axes = [axis for axis in extension_axes if bool(item.get(axis)) or axis in (item.get("axes") or [])]
    missing_axes = [axis for axis in extension_axes if axis not in present_axes]
    blocked = bool(context.get("blocked")) or bool(missing_axes)
    return {
        "schema_version": "1.0",
        "status": "valid" if not blocked else "invalid",
        "blocked": blocked,
        "reason_code": str(context.get("reason_code") or ""),
        "extension_id": str(context.get("extension_id") or ""),
        "present_axes": present_axes,
        "missing_axes": missing_axes,
        "launch_args": list(context.get("launch_args") or []),
    }
