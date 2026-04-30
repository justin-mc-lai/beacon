from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.commands.gate import GateMode, check_prototype_contract
from beacon.main import app
from beacon.utils.prototype_utils import (
    _build_theme_payload,
    _write_prototype_projection_sqlite,
    evaluate_prototype_status,
    load_source_documents,
    prototype_files,
)


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _prepare_sources(tmp_path: Path, feature_slug: str, version: str) -> None:
    content = """# Feature

AC-001 prototype mode must be wireframe
AC-002 pages and navigation are frozen
TC-001 verify mode and files
TC-002 verify state and component mapping
首页
管理总览
项目详情
运行中心
恢复诊断
项目物料查看器
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def test_v135_create_review_freeze_should_emit_projection_consistency_payload(tmp_path: Path):
    version = "v1.3.5"
    feature_slug = "projection-consistency-demo"
    feature = "Projection Consistency Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    create_payload = json.loads(create.stdout)
    assert create_payload["prototype_mode"] == "wireframe"

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    assert (root / "canonical-envelope.json").exists()
    assert (root / "state-flow-map.json").exists()
    assert (root / "state-flow-map.md").exists()
    assert (root / "component-catalog.json").exists()
    assert (root / "component-catalog.md").exists()

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"
    assert review_payload["human_view_status"] == "pass"
    assert review_payload["machine_contract_status"] == "pass"
    assert review_payload["sqlite_projection_status"] == "pass"
    assert review_payload["drift_status"] == "consistent"

    freeze = _invoke(["prototype", "freeze", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert freeze.exit_code == 0, freeze.stdout
    freeze_payload = json.loads(freeze.stdout)
    assert freeze_payload["status"] == "frozen"
    assert freeze_payload["transaction"]["transaction_id"]

    status = _invoke(["prototype", "status", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert status.exit_code == 0, status.stdout
    status_payload = json.loads(status.stdout)
    assert status_payload["gate_ready"] is True
    assert status_payload["drift_status"] == "consistent"


def test_v135_prototype_should_derive_custom_pages_instead_of_fixed_management_template(tmp_path: Path):
    version = "v1.3.5"
    feature_slug = "checkout-surface-demo"
    feature = "Checkout Surface Demo"
    content = """# PRD

AC-001 checkout flow pages are frozen
AC-002 navigation is deterministic
TC-001 verify page freeze
TC-002 verify navigation closure

## Pages
- Login Page
- Cart Page
- Checkout Page

## Route Map
- Login Page -> Cart Page
- Cart Page -> Checkout Page
- Checkout Page -> Cart Page
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    required_pages = set(plan.get("required_pages") or [])
    assert required_pages == {"login-page", "cart-page", "checkout-page"}
    assert bool((plan.get("parser") or {}).get("fallback_used")) is False

    transitions = (plan.get("navigation") or {}).get("transitions") or []
    transition_pairs = {(item.get("from"), item.get("to")) for item in transitions if isinstance(item, dict)}
    assert ("login-page", "cart-page") in transition_pairs
    assert ("cart-page", "checkout-page") in transition_pairs


def test_v135_prototype_should_ignore_forbidden_management_pages_and_meta_labels(tmp_path: Path):
    version = "v1.3.8"
    feature_slug = "clipboard-surface-demo"
    feature = "Clipboard Surface Demo"
    content = """# PRD

## Prototype Freeze Contract

### 正式页面

- 历史记录主页
- 收藏片段页
- 设置页
- 收藏片段编辑弹层

### 明确禁止作为页面名的内容

- generic project dashboard
- project detail relay page
- runtime diagnostics center
- material viewer

## 路由

- 历史记录主页 -> 收藏片段页
- 收藏片段页 -> 设置页
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    required_pages = set(plan.get("required_pages") or [])
    assert "home" not in required_pages
    assert "project-detail" not in required_pages
    assert "runtime-center" not in required_pages
    assert "material-viewer" not in required_pages
    assert "generic-project-dashboard" not in required_pages
    assert len(required_pages) == 4


def test_v135_prototype_default_archetype_should_be_generic_wireframe(tmp_path: Path):
    version = "v1.3.8"
    feature_slug = "generic-archetype-demo"
    feature = "Generic Archetype Demo"
    content = """# PRD

## Pages
- Login Page
- Cart Page
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    docs = load_source_documents(tmp_path, version, feature)
    theme = _build_theme_payload(docs)
    assert theme["prototype_archetype"] == "generic-wireframe"


def test_v135_prototype_forbidden_page_review_should_fail_and_block_gate(tmp_path: Path):
    version = "v1.3.8"
    feature_slug = "forbidden-page-gate-demo"
    feature = "Forbidden Page Gate Demo"
    content = """# PRD

ui_visualization_required: true
prototype_freeze_required: true

原型阶段不应生成：

- generic project dashboard
- project detail relay page
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    root.mkdir(parents=True, exist_ok=True)
    (root / "prototype-plan.json").write_text(
        json.dumps(
            {
                "prototype_mode": "wireframe",
                "required_pages": ["home", "project-detail"],
                "required_states": ["ready"],
                "page_specs": [
                    {
                        "page_id": "home",
                        "states": [{"id": "ready"}],
                        "requirement_refs": {"user-story": ["x"], "prd": ["x"], "test-case": ["x"]},
                    },
                    {
                        "page_id": "project-detail",
                        "states": [{"id": "ready"}],
                        "requirement_refs": {"user-story": ["x"], "prd": ["x"], "test-case": ["x"]},
                    },
                ],
                "requirement_ids": {"ac_ids": [], "tc_ids": []},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "prototype_mode": "wireframe",
                "transaction": {
                    "transaction_id": "tx-forbidden-page-gate-demo",
                    "source_hash": "source-hash",
                    "projection_seq": "pp-forbidden-page-gate-demo",
                    "committed_at": "2026-04-27T00:00:00Z",
                    "sink_checksums": {"human": "h", "machine": "m", "sqlite": "s"},
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "source-map.json").write_text(json.dumps({"sources": ["docs/beacon"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "canonical-envelope.json").write_text(
        json.dumps(
            {
                "prototype_mode": "wireframe",
                "source_hash": "source-hash",
                "projection_seq": "pp-forbidden-page-gate-demo",
                "transaction_id": "tx-forbidden-page-gate-demo",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "state-flow-map.json").write_text(json.dumps({"nodes": [1], "edges": [1]}, ensure_ascii=False), encoding="utf-8")
    (root / "component-catalog.json").write_text(json.dumps({"components": []}, ensure_ascii=False), encoding="utf-8")
    (root / "route-closure-contract.json").write_text(json.dumps({"closure_cases": [{"from": "home", "to": "project-detail"}]}, ensure_ascii=False), encoding="utf-8")
    (root / "implementation-map.json").write_text(json.dumps({}, ensure_ascii=False), encoding="utf-8")
    (root / "wireframe-manifest.json").write_text("{}", encoding="utf-8")
    (root / "navigation-map.json").write_text("{}", encoding="utf-8")
    (root / "navigation-map.md").write_text("# nav\n", encoding="utf-8")
    (root / "state-flow-map.md").write_text("# state\n", encoding="utf-8")
    (root / "component-catalog.md").write_text("# components\n", encoding="utf-8")
    (root / "interaction-map.json").write_text("{}", encoding="utf-8")
    (root / "coverage-report.json").write_text(json.dumps({"required_pages": ["home", "project-detail"], "required_states": ["ready"]}, ensure_ascii=False), encoding="utf-8")
    (root / "wireframe-summary.md").write_text("# summary\n", encoding="utf-8")
    (root / "theme.json").write_text("{}", encoding="utf-8")
    (root / "tokens.css").write_text(":root {}", encoding="utf-8")
    (root / "platform-variants.json").write_text("{}", encoding="utf-8")
    (root / "pages").mkdir(exist_ok=True)
    (root / "page-specs").mkdir(exist_ok=True)
    (root / "pages" / "home.md").write_text("# home\n", encoding="utf-8")
    (root / "pages" / "project-detail.md").write_text("# detail\n", encoding="utf-8")
    (root / "page-specs" / "home.json").write_text("{}", encoding="utf-8")
    (root / "page-specs" / "project-detail.json").write_text("{}", encoding="utf-8")

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "fail"
    failed_checks = {item["name"] for item in review_payload["checks"] if item["status"] == "fail"}
    assert "forbidden_page_inventory_clear" in failed_checks

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues if isinstance(item, dict)}
    assert "prototype_forbidden_page_present" in reason_codes


def test_v135_prototype_status_should_accept_subdirectory_layout_bundle(tmp_path: Path):
    version = "v1.3.6"
    feature_slug = "subdir-layout-demo"
    feature = "Subdir Layout Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    (root / "human-view" / "wireframes").mkdir(parents=True, exist_ok=True)
    (root / "machine-view" / "page-specs").mkdir(parents=True, exist_ok=True)
    (root / "verification").mkdir(parents=True, exist_ok=True)
    (root / "assets").mkdir(parents=True, exist_ok=True)
    (root / "implementation").mkdir(parents=True, exist_ok=True)

    (root / "prototype-plan.json").write_text(
        json.dumps(
            {
                "required_pages": ["home", "management-overview"],
                "compiler": {},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "canonical-envelope.json").write_text("{}", encoding="utf-8")
    (root / "source-map.json").write_text("{}", encoding="utf-8")
    (root / "freeze.json").write_text(json.dumps({"status": "frozen"}), encoding="utf-8")
    (root / "human-view" / "wireframe-summary.md").write_text("# summary\n", encoding="utf-8")
    (root / "human-view" / "navigation-map.md").write_text("# nav\n", encoding="utf-8")
    (root / "human-view" / "state-flow-map.md").write_text("# state\n", encoding="utf-8")
    (root / "human-view" / "component-catalog.md").write_text("# components\n", encoding="utf-8")
    (root / "human-view" / "wireframes" / "home.md").write_text("# home\n", encoding="utf-8")
    (root / "human-view" / "wireframes" / "management-overview.md").write_text("# overview\n", encoding="utf-8")
    for name in (
        "wireframe-manifest.json",
        "navigation-map.json",
        "state-flow-map.json",
        "component-catalog.json",
        "interaction-map.json",
        "coverage-report.json",
        "route-closure-contract.json",
    ):
        (root / "machine-view" / name).write_text("{}", encoding="utf-8")
    (root / "machine-view" / "page-specs" / "home.json").write_text("{}", encoding="utf-8")
    (root / "machine-view" / "page-specs" / "management-overview.json").write_text("{}", encoding="utf-8")
    (root / "verification" / "prototype-review.json").write_text(
        json.dumps({"overall_status": "pass", "design_review_outcome": "pass"}),
        encoding="utf-8",
    )
    (root / "verification" / "prototype-review.md").write_text("# review\n", encoding="utf-8")
    (root / "assets" / "theme.json").write_text("{}", encoding="utf-8")
    (root / "assets" / "tokens.css").write_text(":root {}", encoding="utf-8")
    (root / "assets" / "platform-variants.json").write_text("{}", encoding="utf-8")
    (root / "implementation" / "implementation-map.json").write_text("{}", encoding="utf-8")

    transaction = {
        "transaction_id": "tx-subdir-layout-demo",
        "feature_slug": feature_slug,
        "version": version,
        "projection_seq": "pp-subdir-layout-demo",
        "source_hash": "source-hash",
        "committed_at": "2026-04-21T09:13:23Z",
        "status": "committed",
        "root_path": str(root),
        "sink_checksums": {
            "human": "human-checksum",
            "machine": "machine-checksum",
            "sqlite": "sqlite-checksum",
        },
    }
    _write_prototype_projection_sqlite(transaction)
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "status": "frozen",
                "review_status": "pass",
                "design_review_outcome": "pass",
                "transaction": transaction,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    files = prototype_files(tmp_path, version, feature)
    assert files["wireframe_summary"] == root / "human-view" / "wireframe-summary.md"
    assert files["review_json"] == root / "verification" / "prototype-review.json"
    assert files["pages_dir"] == root / "human-view" / "wireframes"
    assert files["page_specs_dir"] == root / "machine-view" / "page-specs"

    status = evaluate_prototype_status(tmp_path, version, feature)
    assert status["status"] == "frozen"
    assert status["human_view_status"] == "pass"
    assert status["machine_contract_status"] == "pass"
    assert status["sqlite_projection_status"] == "pass"
    assert "missing_artifact:wireframe_summary" not in status["inconsistent_reasons"]
    assert "missing_dir:pages_dir" not in status["inconsistent_reasons"]
    assert "missing_pages:home,management-overview" not in status["inconsistent_reasons"]
