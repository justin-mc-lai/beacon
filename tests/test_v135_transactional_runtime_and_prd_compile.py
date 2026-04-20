from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app
from beacon.commands.gate import GateMode, check_runtime_projection_transaction_contract
from beacon.utils.runtime_projection import build_runtime_projection
from beacon.utils.runtime_projection_store import runtime_projection_transaction_contract, sync_projection


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path, version: str = "v1.3.5") -> None:
    base = root / "docs" / "beacon" / version
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution Index\n\n- A\n", encoding="utf-8")
    (base / "execution" / "architecture-blueprint.md").write_text("# Architecture\n\n- A\n", encoding="utf-8")


def test_v135_runtime_projection_should_mark_failed_transaction_when_sqlite_unavailable(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")

    envelope = build_runtime_projection(tmp_path, docs_version="v1.3.5")
    result = sync_projection(envelope)

    assert result["status"] == "failed_transaction"
    assert result["sqlite_status"] in {"failed", "unavailable"}
    assert "sqlite" in (result.get("failed_sinks") or [])
    assert result.get("transaction_id")
    assert Path(result["transaction_path"]).exists()


def test_v135_runtime_projection_contract_should_block_on_failed_transaction(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_DISABLE_SQLITE", "1")

    envelope = build_runtime_projection(tmp_path, docs_version="v1.3.5")
    sync_projection(envelope)

    contract = runtime_projection_transaction_contract(
        project_root=tmp_path,
        docs_version="v1.3.5",
        feature=None,
    )
    assert contract["status"] == "fail"
    assert contract["reason_code"] == "runtime_projection_failed_transaction"

    gate_issues = check_runtime_projection_transaction_contract(
        tmp_path,
        GateMode.STRICT,
        "release",
        "v1.3.5",
    )
    assert gate_issues
    assert gate_issues[0]["reason_code"] == "runtime_projection_failed_transaction"
    assert gate_issues[0]["blocked"] is True


def test_v135_runtime_projection_contract_should_match_requested_context_even_if_not_latest(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _seed_docs(tmp_path)
    ledger_root = tmp_path / "ledger"
    monkeypatch.setenv("BEACON_RUNTIME_LEDGER_ROOT", str(ledger_root))
    feature = "beacon-v1.3.5-transactional-multi-sink-consistency-and-llm-requirement-compiler"

    feature_envelope = build_runtime_projection(tmp_path, docs_version="v1.3.5", feature=feature)
    feature_sync = sync_projection(feature_envelope)
    assert feature_sync["status"] == "applied"

    # Write a newer transaction for a different projection context.
    global_envelope = build_runtime_projection(tmp_path, docs_version="v1.3.5", feature=None)
    global_sync = sync_projection(global_envelope)
    assert global_sync["status"] == "applied"

    feature_contract = runtime_projection_transaction_contract(
        project_root=tmp_path,
        docs_version="v1.3.5",
        feature=feature,
    )
    assert feature_contract["status"] == "pass"
    assert feature_contract["reason_code"] == "runtime_projection_transaction_ok"
    assert feature_contract["details"]["source_hash"] == feature_sync["source_hash"]

    global_contract = runtime_projection_transaction_contract(
        project_root=tmp_path,
        docs_version="v1.3.5",
        feature=None,
    )
    assert global_contract["status"] == "pass"
    assert global_contract["reason_code"] == "runtime_projection_transaction_ok"
    assert global_contract["details"]["source_hash"] == global_sync["source_hash"]


def test_v135_prd_create_llm_mode_should_emit_semantic_contract_and_machine_evidence(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.delenv("BEACON_PRD_DISABLE_LLM", raising=False)
    monkeypatch.delenv("BEACON_PRD_FORCE_INVALID_LLM_OUTPUT", raising=False)

    result = _invoke(
        [
            "prd",
            "create",
            "Beacon Transaction Contract",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--mode",
            "llm",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["generator_mode"] == "llm"
    assert payload["contract_ok"] is True

    prd_path = Path(payload["output_path"])
    compile_path = Path(payload["compile_path"])
    prd_text = prd_path.read_text(encoding="utf-8")
    compile_payload = json.loads(compile_path.read_text(encoding="utf-8"))

    assert "## 6. 边界 / 分层 / 恢复策略" in prd_text
    assert "待补充" not in prd_text
    assert compile_payload["generator_mode"] == "llm"
    assert compile_payload["contract_ok"] is True
    assert compile_payload["transaction_id"]
    assert compile_payload["sink_checksums"]["human"]
    assert compile_payload["sink_checksums"]["machine"]


def test_v135_prd_create_auto_mode_should_fallback_to_rule_when_llm_disabled(monkeypatch, tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    monkeypatch.setenv("BEACON_PRD_DISABLE_LLM", "1")

    result = _invoke(
        [
            "prd",
            "create",
            "Beacon Rule Fallback",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.5",
            "--mode",
            "auto",
            "--json",
        ]
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["generator_mode"] == "rule"
    assert payload["fallback_reason"] == "llm_disabled"
