"""Tests for beacon-qa-chrome-extension-e2e-v164."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.utils.browser_task_compiler import default_browser_runner_command
from beacon.utils.playwright_extension import (
    HEADLESS_NEW_FLAG,
    LEGACY_HEADLESS_FLAG,
    REASON_EXTENSION_ID_MISMATCH,
    REASON_EXTENSION_LOAD_FAILED,
    REASON_SERVICE_WORKER_NOT_READY,
    build_chrome_launch_args,
    compute_extension_id_from_key,
    compute_extension_id_from_manifest,
    extension_page_url,
    popup_url,
    validate_extension_runner_context,
)
from beacon.utils.qa_acceptance import (
    BROWSER_EVIDENCE_AXES,
    BROWSER_RUNNER_REGISTRY,
    NON_ACCEPTANCE_EVIDENCE_KINDS,
    build_browser_evidence_contract,
    classify_evidence_kind,
    evidence_kind_accepts,
)

FIXTURE_EXT = Path(__file__).resolve().parent / "fixtures" / "chrome-ext"


def test_runner_registered() -> None:
    assert "playwright-extension" in BROWSER_RUNNER_REGISTRY
    command = default_browser_runner_command("playwright-extension", qa_type="functional")
    assert command
    assert "beacon.adapters.playwright_extension_runner" in command


def test_load_extension_passthrough(tmp_path: Path) -> None:
    ext_path = FIXTURE_EXT
    args = build_chrome_launch_args(extension_path=str(ext_path))
    assert any(arg.startswith("--load-extension=") for arg in args)
    bad_path = tmp_path / "missing-ext"
    context = validate_extension_runner_context(extension_path=str(bad_path))
    assert context["blocked"] is True
    assert context["reason_code"] == REASON_EXTENSION_LOAD_FAILED


def test_headless_new_mode() -> None:
    args = build_chrome_launch_args(extension_path=str(FIXTURE_EXT))
    assert HEADLESS_NEW_FLAG in args
    assert LEGACY_HEADLESS_FLAG not in args or args.count(LEGACY_HEADLESS_FLAG) == 0


def test_extension_id_fixed() -> None:
    manifest = json.loads((FIXTURE_EXT / "manifest.json").read_text(encoding="utf-8"))
    first = compute_extension_id_from_manifest(manifest)
    second = compute_extension_id_from_key(str(manifest["key"]))
    assert first
    assert first == second


def test_extension_page_navigation() -> None:
    manifest = json.loads((FIXTURE_EXT / "manifest.json").read_text(encoding="utf-8"))
    extension_id = compute_extension_id_from_manifest(manifest)
    url = extension_page_url(extension_id, "index.html")
    assert url.startswith("chrome-extension://")
    assert url.endswith("/index.html")


def test_popup_test() -> None:
    manifest = json.loads((FIXTURE_EXT / "manifest.json").read_text(encoding="utf-8"))
    extension_id = compute_extension_id_from_manifest(manifest)
    popup = popup_url(extension_id, tab_id=42)
    assert "popup.html" in popup
    assert "tab=42" in popup


def test_service_worker_target() -> None:
    context = validate_extension_runner_context(extension_path=str(FIXTURE_EXT), service_worker_ready=True)
    assert context["blocked"] is False
    blocked = validate_extension_runner_context(extension_path=str(FIXTURE_EXT), service_worker_ready=False)
    assert blocked["blocked"] is True
    assert blocked["reason_code"] == REASON_SERVICE_WORKER_NOT_READY


def test_fail_closed_no_false_pass(tmp_path: Path) -> None:
    for reason_code, payload in [
        (REASON_EXTENSION_LOAD_FAILED, {"runner": "playwright-extension", "extension_path": str(tmp_path / "bad")}),
        (
            REASON_EXTENSION_ID_MISMATCH,
            {
                "runner": "playwright-extension",
                "extension_path": str(FIXTURE_EXT),
                "expected_extension_id": "wrong-id",
            },
        ),
        (
            REASON_SERVICE_WORKER_NOT_READY,
            {"runner": "playwright-extension", "extension_path": str(FIXTURE_EXT), "service_worker_ready": False},
        ),
    ]:
        contract = build_browser_evidence_contract(
            {
                **payload,
                "run_id": "run-test",
                "source_command": "pytest",
                "target_url": "chrome-extension://x/index.html",
                "result_status": "pass",
                "accepted_test_ids": ["TC-CX-008"],
                "evidence_refs": ["evidence.json"],
            }
        )
        assert contract["blocked"] is True
        assert reason_code in contract["missing_fields"] or contract.get("extension_contract", {}).get("reason_code") == reason_code
    assert not evidence_kind_accepts(classify_evidence_kind("dry run only"))


def test_evidence_axes_extension() -> None:
    for axis in ("extension_page", "service_worker", "popup"):
        assert axis in BROWSER_EVIDENCE_AXES
    contract = build_browser_evidence_contract(
        {
            "runner": "playwright-extension",
            "extension_path": str(FIXTURE_EXT),
            "run_id": "run-test",
            "source_command": "pytest",
            "target_url": extension_page_url(compute_extension_id_from_manifest(json.loads((FIXTURE_EXT / "manifest.json").read_text())), "index.html"),
            "result_status": "pass",
            "accepted_test_ids": ["TC-CX-009"],
            "evidence_refs": ["evidence.json"],
            "extension_page": True,
            "service_worker": True,
            "popup": True,
        }
    )
    assert "extension_page" in contract["present_axes"]
    assert "service_worker" in contract["present_axes"]
    assert "popup" in contract["present_axes"]
    assert "dry_run" in NON_ACCEPTANCE_EVIDENCE_KINDS
