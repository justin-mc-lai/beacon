from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_sources(tmp_path: Path, feature_slug: str, version: str) -> None:
    content = """# Feature

target_audience: Product owner and frontend implementer
primary_use_cases: freeze UX truth, align implement and qa, review page hierarchy
operator_mental_state: needs fast and confident delivery decisions
usage_environment: desktop-first requirement review and workbench handoff
brand_tone: quiet, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md
prototype_freeze_required: true

AC-001 design context is frozen
AC-101 design reasoning is frozen
AC-201 ux contract exists
TC-001 verify ux assets
TC-002 verify review gate

## Pages
- Home Page
- Detail Page

## Route Map
- Home Page -> Detail Page
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def test_v136_status_should_report_sink_drift_and_reconcile_action(tmp_path: Path):
    version = "v1.3.11"
    feature_slug = "runtime-reconcile-demo"
    feature = "Runtime Reconcile Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["design_context"]["brand_tone"] = "drifted-tone"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    payload = json.loads(status.stdout)
    assert payload["drift_type"] == "sink-drift"
    assert payload["reason_code"] == "prototype_sink_drift"
    assert payload["next_action"] == "prototype reconcile"
    assert payload["canonical_truth_source"] == "prototype-brief"


def test_v136_reconcile_should_repair_machine_sinks_without_overwriting_pages(tmp_path: Path):
    version = "v1.3.11"
    feature_slug = "runtime-reconcile-demo"
    feature = "Runtime Reconcile Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    page_path = root / "pages" / "home-page.md"
    sentinel = "\n<!-- preserved-human-copy -->\n"
    page_path.write_text(page_path.read_text(encoding="utf-8") + sentinel, encoding="utf-8")

    canonical_path = root / "canonical-envelope.json"
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    canonical["design_reasoning"]["interaction_model"] = "drifted-model"
    canonical_path.write_text(json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8")

    reconcile = _invoke(["prototype", "reconcile", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert reconcile.exit_code == 0, reconcile.stdout
    payload = json.loads(reconcile.stdout)
    assert payload["status"] == "reconciled"
    assert payload["repair_path"] == "nondestructive-reconcile"

    repaired_canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    assert repaired_canonical["design_reasoning"]["interaction_model"] != "drifted-model"
    assert sentinel.strip() in page_path.read_text(encoding="utf-8")

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["reason_code"] == ""
    assert status_payload["drift_type"] == ""


def test_v136_freeze_should_repair_transaction_header_drift(tmp_path: Path):
    version = "v1.3.11"
    feature_slug = "runtime-freeze-repair-demo"
    feature = "Runtime Freeze Repair Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    assert json.loads(review.stdout)["overall_status"] == "pass"

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["transaction"]["source_hash"] = "broken-source-hash"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    payload = json.loads(freeze.stdout)
    assert payload["status"] == "frozen"

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["status"] == "frozen"
    assert status_payload["gate_ready"] is True


def test_v136_gate_should_use_specific_prototype_drift_reason_code(tmp_path: Path):
    version = "v1.3.11"
    feature_slug = "runtime-gate-drift-demo"
    feature = "Runtime Gate Drift Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["design_context"]["density_preference"] = "drifted-density"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues if isinstance(item, dict)}
    assert "prototype_sink_drift" in reason_codes

