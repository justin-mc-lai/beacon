"""v1.4.11 memory/intent historical migration boundary contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beacon.compatibility.registry import registry_by_id
from beacon.utils.intent_router import (
    detect_intent,
    legacy_intent_router_compat_evidence,
    optimize_prompt_to_plan,
    route_legacy_intent_compat,
    route_intent,
)
from beacon.utils.memory import (
    append_memory_entry,
    export_legacy_projection,
    load_memory_entries,
    memory_migration_transaction_path,
    memory_v1_path,
)


def _write_legacy_decision(project_root: Path, content: str = "Legacy decision row") -> Path:
    memory_root = project_root / ".beacon" / "memory"
    memory_root.mkdir(parents=True, exist_ok=True)
    path = memory_root / "decisions.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "3.0",
                "decisions": [
                    {
                        "memory_id": "legacy-decision-001",
                        "decision": content,
                        "source_session_id": "legacy-session",
                        "source": "legacy-import",
                        "created_at": "2026-01-01T00:00:00+00:00",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.historical_fixture
def test_old_memory_rows_remain_importable(tmp_path: Path) -> None:
    _write_legacy_decision(tmp_path)

    rows = load_memory_entries(tmp_path, mem_type="decision")

    assert any(row["memory_id"] == "legacy-decision-001" for row in rows)
    assert memory_v1_path(tmp_path).exists()


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
@pytest.mark.migration
def test_first_migration_writes_transaction(tmp_path: Path) -> None:
    legacy_path = _write_legacy_decision(tmp_path)

    load_memory_entries(tmp_path)

    transaction_path = memory_migration_transaction_path(tmp_path)
    assert transaction_path.exists()
    transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
    assert transaction["migration_transaction_id"]
    assert transaction["compat_id"] == "memory-legacy-projection"
    assert str(legacy_path) in transaction["source_files"]
    assert transaction["imported_count"] == 1
    assert transaction["skipped_count"] == 0
    assert transaction["current_projection"] == "memory-v1"
    assert transaction["legacy_projection_written"] is False
    assert transaction["compat_mode"] is False


@pytest.mark.migration
def test_memory_v1_is_current_projection(tmp_path: Path) -> None:
    _write_legacy_decision(tmp_path)

    first = append_memory_entry(tmp_path, "decision", "Current decision")
    rows = load_memory_entries(tmp_path, mem_type="decision")

    assert memory_v1_path(tmp_path).exists()
    assert memory_migration_transaction_path(tmp_path).exists()
    assert any(row["memory_id"] == "legacy-decision-001" for row in rows)
    assert any(row["memory_id"] == first["memory_id"] for row in rows)


@pytest.mark.current_contract
def test_current_memory_write_does_not_write_legacy_projection_by_default(tmp_path: Path) -> None:
    legacy_path = tmp_path / ".beacon" / "memory" / "project-insights.json"

    append_memory_entry(tmp_path, "insight", "Current-only memory write")

    assert memory_v1_path(tmp_path).exists()
    assert not legacy_path.exists()


@pytest.mark.compat_contract
@pytest.mark.historical_fixture
def test_legacy_projection_requires_explicit_compat_mode(tmp_path: Path) -> None:
    append_memory_entry(tmp_path, "decision", "Compat export decision")

    with pytest.raises(PermissionError):
        export_legacy_projection(tmp_path)

    payload = export_legacy_projection(tmp_path, compat_mode=True)
    legacy_path = tmp_path / ".beacon" / "memory" / "decisions.json"
    legacy_payload = json.loads(legacy_path.read_text(encoding="utf-8"))
    assert payload["compat_id"] == "memory-legacy-projection"
    assert payload["compat_mode"] is True
    assert payload["legacy_projection_written"] is True
    assert legacy_payload["decisions"][0]["decision"] == "Compat export decision"


@pytest.mark.compat_contract
def test_legacy_intent_router_is_compat_classified() -> None:
    result = route_intent("create prd", mode="rule")

    assert result["compat_id"] == "intent-legacy-router"
    assert result["route_kind"] == "compat_router"
    assert result["current_route_claimed"] is False
    assert result["compat_evidence"]["recommended_current_route"] == "optimize_prompt_to_plan"


@pytest.mark.compat_contract
def test_old_intent_api_remains_callable_with_compat_admission() -> None:
    with pytest.raises(PermissionError):
        route_legacy_intent_compat("create prd")

    result = route_legacy_intent_compat("create prd", compat_mode=True)
    assert result["intent"] == "prd"
    assert result["compat_mode"] is True
    assert result["compat_id"] == "intent-legacy-router"


@pytest.mark.compat_contract
def test_legacy_route_does_not_claim_current_route(tmp_path: Path) -> None:
    registry = registry_by_id()
    legacy = detect_intent("create prd")
    current = optimize_prompt_to_plan("create prd for checkout", project_root=tmp_path, router_mode="rule")

    assert "intent-legacy-router" in registry
    assert legacy["current_route_claimed"] is False
    assert legacy_intent_router_compat_evidence()["current_route_claimed"] is False
    assert current["route_evidence"]["route_kind"] == "current_router"
    assert current["route_evidence"]["current_route_claimed"] is True
    assert current["route_evidence"]["legacy_router_used"] is False


@pytest.mark.compat_contract
def test_memory_registry_binding() -> None:
    registry = registry_by_id()

    entry = registry["memory-legacy-projection"]
    assert entry["surface"] == "memory"
    assert entry["current_replacement"] == "memory-v1 evidence-bound projection"
    assert "memory-migration-transaction-test" in entry["evidence_required"]


@pytest.mark.compat_contract
def test_intent_registry_binding() -> None:
    registry = registry_by_id()

    entry = registry["intent-legacy-router"]
    assert entry["surface"] == "intent"
    assert entry["current_replacement"] == "governed intent routing and support-surface routing"
    assert "legacy-router-admission-test" in entry["evidence_required"]


@pytest.mark.compat_contract
def test_no_unrelated_phase_behavior_changes() -> None:
    registry = registry_by_id()
    unrelated_ids = {
        "prototype-legacy-wireframe-source",
        "browser-fallback-command-name",
        "qa-auto-test-status-legacy-mirror",
        "prd-legacy-machine-mirror",
        "implement-legacy-cli-loader",
        "command-catalog-compat-deprecated-aliases",
    }

    assert unrelated_ids.issubset(set(registry))
