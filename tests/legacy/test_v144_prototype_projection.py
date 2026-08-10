from __future__ import annotations

import json
import hashlib
from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


runner = CliRunner()
VERSION = "v1.4.4"
FEATURE = "Beacon V144 Prototype Projection Demo"
SLUG = "beacon-v144-prototype-projection-demo"


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_sources(root: Path, *, design_preset: str = "") -> None:
    preset_line = f"design_preset: {design_preset}\n" if design_preset else ""
    content = (
        "# Feature\n\n"
        "target_audience: Product owner and implementation operator\n"
        "primary_use_cases: freeze UX truth, align implement and qa, review hierarchy\n"
        "operator_mental_state: needs quick and confident delivery decisions\n"
        "usage_environment: desktop-first workbench review and handoff\n"
        "brand_tone: quiet, precise, operational\n"
        "density_preference: workbench-medium\n"
        f"{preset_line}"
        "prototype_freeze_required: true\n"
        "ui_visualization_required: true\n\n"
        "AC-001 design context is frozen\n"
        "AC-002 template baseline is frozen\n"
        "TC-001 verify prototype design assets\n"
        "TC-002 verify review gate\n\n"
        "## Pages\n"
        "- Home Page\n"
        "- Detail Page\n\n"
        "## Route Map\n"
        "- Home Page -> Detail Page\n"
    )
    _write(root, "docs/beacon/global-boundaries.md", "# boundaries\n")
    _write(root, f"docs/beacon/{VERSION}/SUMMARY.md", "# summary\n")
    _write(root, f"docs/beacon/{VERSION}/execution/index.md", "# execution\n")
    _write(root, f"docs/beacon/{VERSION}/execution/architecture-blueprint.md", "# blueprint\n")
    for sub in ("user-story", "prd", "qa/test-cases"):
        _write(root, f"docs/beacon/{VERSION}/{sub}/{SLUG}.md", content)


def _seed_prd_machine_mirrors(root: Path) -> None:
    prd_path = root / "docs" / "beacon" / VERSION / "prd" / f"{SLUG}.md"
    markdown_raw = prd_path.read_text(encoding="utf-8")
    markdown = markdown_raw.strip()
    source_hash = "sha256:" + hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    compile_hash = hashlib.sha256(markdown_raw.encode("utf-8")).hexdigest()
    tx_id = "tx-v144-prototype-001"
    _write(root, f".beacon/prd/{SLUG}.json", json.dumps({"content": markdown}, ensure_ascii=False, indent=2) + "\n")
    _write(
        root,
        f"docs/beacon/{VERSION}/.machine/prd/{SLUG}.canonical.json",
        json.dumps({"markdown": markdown, "transaction": {"transaction_id": tx_id, "source_hash": source_hash}}, ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        root,
        f"docs/beacon/{VERSION}/.machine/prd/{SLUG}.compile.json",
        json.dumps({"compile_hash": compile_hash, "contract_ok": True}, ensure_ascii=False, indent=2) + "\n",
    )
    _write(
        root,
        f".beacon/state/prd-transactions/latest-{SLUG}.json",
        json.dumps({"transaction_id": tx_id, "source_hash": source_hash}, ensure_ascii=False, indent=2) + "\n",
    )


def _prepare_requirement_package(root: Path, *, design_preset: str = "") -> None:
    _seed_sources(root, design_preset=design_preset)
    _seed_prd_machine_mirrors(root)
    user_story = _invoke(["user-story", "create", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert user_story.exit_code == 0, user_story.stdout
    test_case = _invoke(["test-case", "create", FEATURE, "--project", str(root), "--version", VERSION, "--json"])
    assert test_case.exit_code == 0, test_case.stdout


def test_v144_prototype_should_default_to_restrained_product_and_emit_design_contracts(tmp_path: Path) -> None:
    _prepare_requirement_package(tmp_path)

    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / VERSION / "prototype" / SLUG
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    style_preset = json.loads((root / "design-artifacts" / "style-preset.json").read_text(encoding="utf-8"))
    lint_rules = json.loads((root / "design-artifacts" / "design-lint-rules.json").read_text(encoding="utf-8"))
    implementation_index = json.loads((root / "implementation" / "index.json").read_text(encoding="utf-8"))

    assert plan["theme"]["design_preset"] == "restrained-product"
    assert plan["theme"]["canonical_design_preset"] == "restrained-product"
    assert plan["theme"]["preset_source"] == "apple"
    assert plan["theme"]["template_catalog_count"] == 3
    assert style_preset["payload"]["anti_ai_ui_contract"]["minimum_touch_target"] == "44x44"
    assert lint_rules["payload"]["canonical_design_preset"] == "restrained-product"
    assert "design-artifacts/style-preset.json" in implementation_index["allowed_inputs"]
    assert "design-artifacts/design-lint-rules.json" in implementation_index["allowed_inputs"]

    review = _invoke(["prototype", "review", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    failed_checks = {item["name"] for item in review_payload["checks"] if item["status"] == "fail"}
    assert "default_design_preset_stable" not in failed_checks


def test_v144_prototype_should_preserve_explicit_operator_console_preset(tmp_path: Path) -> None:
    _prepare_requirement_package(tmp_path, design_preset="operator-console")

    create = _invoke(["prototype", "create", FEATURE, "--project", str(tmp_path), "--version", VERSION, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / VERSION / "prototype" / SLUG
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))

    assert plan["theme"]["design_preset"] == "operator-console"
    assert plan["theme"]["canonical_design_preset"] == "operator-console"
    assert plan["theme"]["preset_source"] == "vercel"
