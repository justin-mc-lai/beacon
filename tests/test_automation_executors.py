from __future__ import annotations

from beacon.utils.automation_executors import build_executor_capability_matrix, executor_capability, normalize_executor


def test_executor_capability_matrix_should_reflect_tiered_support() -> None:
    matrix = build_executor_capability_matrix()
    by_name = {item["executor"]: item for item in matrix}

    assert by_name["codex"]["tier"] == "native"
    assert by_name["codex"]["beacon_runtime_execution"] is True
    assert by_name["claude"]["tier"] == "native"
    assert by_name["claude"]["beacon_runtime_execution"] is True
    assert by_name["cursor"]["status"] == "supported-via-adapter"
    assert by_name["cursor"]["beacon_runtime_execution"] is False
    assert by_name["windsurf"]["tier"] == "assisted"
    assert by_name["trae"]["tier"] == "experimental"


def test_normalize_executor_should_fallback_to_codex() -> None:
    assert normalize_executor("cursor") == "cursor"
    assert normalize_executor("unknown") == "codex"
    assert executor_capability("trae")["status"] == "scaffold-only"
