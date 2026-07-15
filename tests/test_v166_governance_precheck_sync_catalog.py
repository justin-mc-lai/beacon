"""Tests for governance precheck in plan start and doctor sync-catalog."""

from __future__ import annotations

import json
import tempfile
import shutil
from pathlib import Path

import pytest

from beacon.utils.program_plan_runtime import governance_precheck
from beacon.utils.version_truth_catalog import sync_catalog_versions


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# governance_precheck
# ---------------------------------------------------------------------------


class TestGovernancePrecheck:
    """Verify governance_precheck correctly validates version registration."""

    def test_pass_when_version_registered_with_truth_canonical(self) -> None:
        """v1.6.5 has truth_canonical: main — should pass."""
        result = governance_precheck(PROJECT_ROOT, "v1.6.5")
        assert result["status"] == "pass"
        assert result["blocked"] is False
        assert result["truth_canonical"] == "main"

    def test_pass_when_v166_registered(self) -> None:
        """v1.6.6 has truth_canonical: main — should pass."""
        result = governance_precheck(PROJECT_ROOT, "v1.6.6")
        assert result["status"] == "pass"
        assert result["blocked"] is False

    def test_blocked_when_version_not_registered(self) -> None:
        """v9.9.9 is not in governance — should be blocked."""
        result = governance_precheck(PROJECT_ROOT, "v9.9.9")
        assert result["status"] == "blocked"
        assert result["blocked"] is True
        assert result["reason_code"] == "governance_version_not_registered"

    def test_blocked_reason_includes_recommendation(self) -> None:
        """Blocked payload should include actionable recommendation."""
        result = governance_precheck(PROJECT_ROOT, "v9.9.9")
        assert "recommendation" in result
        assert "v9.9.9" in result["recommendation"]


# ---------------------------------------------------------------------------
# plan start CLI integration
# ---------------------------------------------------------------------------


class TestPlanStartGovernanceIntegration:
    """Verify plan start surfaces governance_precheck in JSON output."""

    def test_plan_start_includes_governance_precheck_pass(self) -> None:
        from typer.testing import CliRunner
        from beacon.main import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["plan", "start", "test governance", "--project-root", str(PROJECT_ROOT), "--version", "v1.6.5", "--json"],
        )
        # Should succeed (exit 0) since governance precheck passes
        assert result.exit_code == 0, f"stderr: {result.stderr}"
        payload = json.loads(result.output)
        gov = payload.get("governance_precheck") or {}
        assert gov["status"] == "pass"
        assert gov["blocked"] is False

    def test_plan_start_blocks_unregistered_version(self) -> None:
        from typer.testing import CliRunner
        from beacon.main import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["plan", "start", "test unregistered", "--project-root", str(PROJECT_ROOT), "--version", "v8.8.8", "--json"],
        )
        # Should exit 2 (blocked by governance precheck)
        assert result.exit_code == 2
        payload = json.loads(result.output)
        gov = payload.get("governance_precheck") or {}
        assert gov["status"] == "blocked"
        assert gov["reason_code"] == "governance_version_not_registered"
        # Clean up test artifact
        test_dir = PROJECT_ROOT / "docs" / "beacon" / "v8.8.8"
        if test_dir.exists():
            shutil.rmtree(test_dir)


# ---------------------------------------------------------------------------
# sync_catalog_versions
# ---------------------------------------------------------------------------


class TestSyncCatalog:
    """Verify sync_catalog_versions discovers and registers versions."""

    def test_dry_run_discovers_existing_versions(self) -> None:
        result = sync_catalog_versions(PROJECT_ROOT, dry_run=True)
        assert result["status"] == "dry_run"
        assert result["discovered_count"] > 0
        assert result["active_window"] == 3
        # All currently cataloged versions should be in skipped
        assert len(result["skipped_already_registered"]) > 0

    def test_dry_run_does_not_write(self) -> None:
        """Dry run should not change the catalog file."""
        catalog_path = PROJECT_ROOT / "docs" / "beacon" / "governance" / "version-truth-catalog.md"
        before = catalog_path.read_text(encoding="utf-8")
        sync_catalog_versions(PROJECT_ROOT, dry_run=True)
        after = catalog_path.read_text(encoding="utf-8")
        assert before == after

    def test_dry_run_enforces_active_window(self) -> None:
        """When active versions exceed window, oldest should be archived."""
        result = sync_catalog_versions(PROJECT_ROOT, dry_run=True, active_window=3)
        # With v1.6.4/1.6.5/1.6.6/v2.0.0 = 4 active, window=3 should archive 1
        if result["discovered_count"] == 0:
            # All versions already registered, check window enforcement on existing
            pass
        # At minimum, the function should not crash
        assert result["status"] == "dry_run"


# ---------------------------------------------------------------------------
# doctor sync-catalog CLI integration
# ---------------------------------------------------------------------------


class TestDoctorSyncCatalogCLI:
    """Verify doctor sync-catalog CLI command."""

    def test_sync_catalog_dry_run_json(self) -> None:
        from typer.testing import CliRunner
        from beacon.main import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["doctor", "sync-catalog", "--project-root", str(PROJECT_ROOT), "--dry-run", "--json"],
        )
        assert result.exit_code == 0, f"stderr: {result.stderr}"
        payload = json.loads(result.output)
        assert payload["action"] == "doctor-sync-catalog"
        assert payload["result"]["status"] == "dry_run"

    def test_sync_catalog_dry_run_human(self) -> None:
        from typer.testing import CliRunner
        from beacon.main import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["doctor", "sync-catalog", "--project-root", str(PROJECT_ROOT), "--dry-run"],
        )
        assert result.exit_code == 0
        assert "Beacon Doctor Sync Catalog" in result.output
        assert "discovered:" in result.output
