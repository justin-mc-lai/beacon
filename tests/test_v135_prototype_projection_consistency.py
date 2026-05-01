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


def _prepare_v1310_sources_with_design_context(tmp_path: Path, feature_slug: str, version: str) -> None:
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
    assert (root / "automation-priority-matrix.json").exists()
    assert (root / "automation-priority-matrix.md").exists()

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
    assert theme["design_preset"] == "apple-inspired-design-md"
    assert theme["primary"] == "#0071E3"
    assert theme["secondary"] == "#F5F5F7"


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
    (root / "human-view" / "automation-priority-matrix.md").write_text("# automation\n", encoding="utf-8")
    (root / "human-view" / "wireframes" / "home.md").write_text("# home\n", encoding="utf-8")
    (root / "human-view" / "wireframes" / "management-overview.md").write_text("# overview\n", encoding="utf-8")
    for name in (
        "wireframe-manifest.json",
        "navigation-map.json",
        "state-flow-map.json",
        "component-catalog.json",
        "automation-priority-matrix.json",
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


def test_v135_prototype_status_should_report_legacy_single_file_source(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "legacy-admin-demo"
    feature = "Legacy Admin Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text("# Legacy Prototype\n", encoding="utf-8")

    status = evaluate_prototype_status(tmp_path, version, feature)
    assert status["status"] == "legacy_source_only"
    assert status["exists"] is True
    assert status["legacy_source_status"] == "present"
    assert status["legacy_source_path"] == legacy_doc


def test_v135_prototype_list_should_include_legacy_single_file_source(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "legacy-admin-demo"
    feature = "Legacy Admin Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text("# Legacy Prototype\n", encoding="utf-8")

    result = _invoke(["prototype", "list", "--project", str(tmp_path), "--version", version])
    assert result.exit_code == 0, result.stdout
    assert "legacy-admin-demo: legacy_source_only" in result.stdout
    assert str(legacy_doc) in result.stdout


def test_v135_load_source_documents_should_include_legacy_prototype_source(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "legacy-admin-demo"
    feature = "Legacy Admin Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text("# Legacy Prototype\n\n## Key Screens\n- Dashboard\n", encoding="utf-8")

    docs = load_source_documents(tmp_path, version, feature)
    doc_types = [doc["type"] for doc in docs]
    assert doc_types == ["user-story", "prd", "test-case", "prototype-source"]
    assert docs[-1]["path"] == legacy_doc


def test_v135_legacy_line_should_emit_ux_truth_when_explicitly_requested(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "legacy-ux-demo"
    feature = "Legacy UX Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Legacy Prototype

prototype_ux_prd_required: true
target_audience: B2B operator
primary_use_cases: review key pages, align implementation
operator_mental_state: needs quick confidence
usage_environment: desktop review and handoff
brand_tone: quiet, precise
density_preference: workbench-medium
design_preset: apple-inspired-design-md

## Pages
- Dashboard Page
- Detail Page

## Route Map
- Dashboard Page -> Detail Page
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    assert (root / "ux-prd.md").exists()
    assert (root / "DESIGN.md").exists()
    assert (root / "preview.html").exists()
    assert (root / "preview-dark.html").exists()

    status = evaluate_prototype_status(tmp_path, version, feature)
    assert status["legacy_source_status"] == "present"


def test_v135_explicit_page_meta_should_override_default_page_responsibility(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "page-meta-demo"
    feature = "Page Meta Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

## Pages
- Landing Page
- Verify Page

## Route Map
- Landing Page -> Verify Page

### Landing Page
- responsibility: First screen establishes trust and explains why a wholesale buyer should continue.
- sections: Hero promise | Trust proof | Language switcher | Registration CTA
- actions: Review trust proof -> Verify Page
- priority: P0
- platforms: Web, Mobile
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    landing = next(page for page in plan["page_specs"] if page["page_id"] == "landing-page")
    assert landing["priority"] == "P0"
    assert landing["platforms"] == ["Web", "Mobile"]
    assert landing["responsibility"].startswith("First screen establishes trust")
    assert landing["sections"][:2] == ["Hero promise", "Trust proof"]
    assert landing["actions"][0]["label"] == "Review trust proof"
    assert landing["page_intent_contract"]["why_this_page_exists"].startswith("First screen establishes trust")


def test_v135_explicit_page_meta_should_override_decision_supported_and_surface_type(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "surface-type-demo"
    feature = "Surface Type Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

prototype_ux_prd_required: true
product_surface_type: public-marketing-surface

## Pages
- Landing Page
- Verify Page

## Route Map
- Landing Page -> Verify Page

### Landing Page
- responsibility: Establish trust.
- decision_supported: Decide whether this supplier platform is credible enough to continue.
- sections: Hero | Trust proof
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    landing = next(page for page in plan["page_specs"] if page["page_id"] == "landing-page")
    assert plan["design_reasoning"]["product_surface_type"] == "public-marketing-surface"
    assert landing["page_intent_contract"]["decision_supported"] == "Decide whether this supplier platform is credible enough to continue."


def test_v135_explicit_page_meta_should_parse_business_states(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "business-state-demo"
    feature = "Business State Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

prototype_ux_prd_required: true

## Pages
- Orders List Page

### Orders List Page
- responsibility: Help operators prioritize orders that need intervention.
- states:
  - payment-risk | Payment Risk | Payment anomalies need manual review before fulfillment.
  - fulfillment-blocked | Fulfillment Blocked | Inventory or delivery constraints block shipment.
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    orders = next(page for page in plan["page_specs"] if page["page_id"] == "orders-list-page")
    state_ids = [state["id"] for state in orders["states"]]
    assert "payment-risk" in state_ids
    assert "fulfillment-blocked" in state_ids
    payment_risk = next(state for state in orders["states"] if state["id"] == "payment-risk")
    assert payment_risk["label"] == "Payment Risk"
    assert payment_risk["description"] == "Payment anomalies need manual review before fulfillment."
    assert payment_risk["state_visibility_contract"]["required_feedback"]


def test_v135_explicit_page_meta_should_parse_state_acceptance_refs(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "state-acceptance-demo"
    feature = "State Acceptance Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

prototype_ux_prd_required: true

## Pages
- Orders List Page

### Orders List Page
- actions: Review order detail -> Orders List Page
- states:
  - payment-risk | Payment Risk | Payment anomalies need manual review before fulfillment. | ac_refs=AC-001,AC-003 | tc_refs=TC-003,TC-007
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    orders = next(page for page in plan["page_specs"] if page["page_id"] == "orders-list-page")
    payment_risk = next(state for state in orders["states"] if state["id"] == "payment-risk")
    assert payment_risk["ac_refs"] == ["AC-001", "AC-003"]
    assert payment_risk["tc_refs"] == ["TC-003", "TC-007"]
    contract = payment_risk["state_visibility_contract"]
    assert contract["acceptance_refs"]["ac_refs"] == ["AC-001", "AC-003"]
    assert contract["acceptance_refs"]["tc_refs"] == ["TC-003", "TC-007"]
    assert contract["primary_actions"]


def test_v135_state_flow_map_should_propagate_state_acceptance_refs(tmp_path: Path):
    version = "v1.0.0"
    feature_slug = "state-flow-acceptance-demo"
    feature = "State Flow Acceptance Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

prototype_ux_prd_required: true

## Pages
- Orders List Page

### Orders List Page
- states:
  - payment-risk | Payment Risk | Payment anomalies need manual review before fulfillment. | ac_refs=AC-001,AC-003 | tc_refs=TC-003,TC-007
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    state_flow = json.loads((root / "state-flow-map.json").read_text(encoding="utf-8"))
    business_edge = next(edge for edge in state_flow["edges"] if edge["to"] == "orders-list-page:payment-risk")
    assert business_edge["ac_refs"] == ["AC-001", "AC-003"]
    assert business_edge["test_refs"] == ["TC-003", "TC-007"]
    state_flow_md = (root / "state-flow-map.md").read_text(encoding="utf-8")
    assert "AC-001, AC-003" in state_flow_md
    assert "TC-003, TC-007" in state_flow_md


def test_v1310_prototype_should_emit_ux_truth_and_design_assets(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "ux-truth-demo"
    feature = "UX Truth Demo"
    _prepare_v1310_sources_with_design_context(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    payload = json.loads(create.stdout)

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    canonical = json.loads((root / "canonical-envelope.json").read_text(encoding="utf-8"))
    plan = json.loads((root / "prototype-plan.json").read_text(encoding="utf-8"))
    assert canonical["design_context"]["explicit_context_complete"] is True
    assert canonical["design_reasoning"]["product_surface_type"]
    assert canonical["ux_contract"]["primary_decision"]
    assert plan["page_specs"][0]["page_intent_contract"]["decision_supported"]
    assert plan["page_specs"][0]["states"][0]["state_visibility_contract"]["required_feedback"]
    assert (root / "ux-prd.md").exists()
    assert (root / "DESIGN.md").exists()
    assert (root / "preview.html").exists()
    assert (root / "preview-dark.html").exists()
    assert "ux_prd" in payload["paths"]

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    review_payload = json.loads(review.stdout)
    assert review_payload["overall_status"] == "pass"
    failed_checks = {item["name"] for item in review_payload["checks"] if item["status"] == "fail"}
    assert "design_context_complete" not in failed_checks
    assert "ux_contract_complete" not in failed_checks


def test_v1310_prototype_review_should_fail_without_explicit_design_context(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "missing-design-context-demo"
    feature = "Missing Design Context Demo"
    _prepare_sources(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout

    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout
    payload = json.loads(review.stdout)
    assert payload["overall_status"] == "fail"
    failed_checks = {item["name"] for item in payload["checks"] if item["status"] == "fail"}
    assert "design_context_explicit" in failed_checks


def test_v1310_gate_should_block_missing_design_assets(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "missing-design-assets-demo"
    feature = "Missing Design Assets Demo"
    _prepare_v1310_sources_with_design_context(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    review = _invoke(["prototype", "review", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert review.exit_code == 0, review.stdout

    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    (root / "DESIGN.md").unlink()

    issues = check_prototype_contract(tmp_path, GateMode.STRICT, "prototype", version=version)
    reason_codes = {item.get("reason_code") for item in issues if isinstance(item, dict)}
    assert "prototype_design_asset_missing" in reason_codes


def test_v1310_component_catalog_should_emit_state_aware_feedback_contract(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "component-state-aware-demo"
    feature = "Component State Aware Demo"
    _prepare_v1310_sources_with_design_context(tmp_path, feature_slug, version)

    legacy_doc = tmp_path / "docs" / "beacon" / version / "prototype" / f"{feature_slug}.md"
    legacy_doc.parent.mkdir(parents=True, exist_ok=True)
    legacy_doc.write_text(
        """# Prototype

prototype_ux_prd_required: true

## Pages
- Checkout Page

### Checkout Page
- sections: Address Summary | Payment Method | Submit Bar
- states:
  - address-missing | Address Missing | User must add delivery address before order submission. | ac_refs=AC-201 | tc_refs=TC-008
  - payment-risk | Payment Risk | Payment needs manual verification before capture. | ac_refs=AC-101 | tc_refs=TC-004
""",
        encoding="utf-8",
    )

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    component_catalog = json.loads((root / "component-catalog.json").read_text(encoding="utf-8"))
    first_component = component_catalog["components"][0]
    assert first_component["state_feedback_responsibilities"]
    assert first_component["state_feedback_responsibilities"][0]["state_id"]
    assert first_component["ac_refs"]
    assert first_component["tc_refs"]


def test_v1310_state_flow_map_should_emit_cross_page_transition_contracts(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "cross-page-transition-demo"
    feature = "Cross Page Transition Demo"
    content = """# PRD

target_audience: Product owner and frontend implementer
primary_use_cases: freeze cross-page business transition, align qa
operator_mental_state: needs deterministic flow closure
usage_environment: desktop-first requirement review and workbench handoff
brand_tone: quiet, precise, operational
density_preference: workbench-medium
design_preset: apple-inspired-design-md
prototype_freeze_required: true

AC-001 cross page transition exists
TC-001 verify cross page contract

## Pages
- Cart Page
- Checkout Page

## Route Map
- Cart Page -> Checkout Page
"""
    for sub in ("user-story", "prd", "qa/test-cases"):
        target = tmp_path / "docs" / "beacon" / version / sub / f"{feature_slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    state_flow = json.loads((root / "state-flow-map.json").read_text(encoding="utf-8"))
    cross_page_edge = next(edge for edge in state_flow["edges"] if edge["kind"] == "cross-page-transition")
    assert cross_page_edge["from_page"] == "cart-page"
    assert cross_page_edge["to_page"] == "checkout-page"
    assert cross_page_edge["route_or_runtime_evidence"]


def test_v1310_prototype_should_emit_automation_priority_matrix(tmp_path: Path):
    version = "v1.3.10"
    feature_slug = "automation-priority-demo"
    feature = "Automation Priority Demo"
    _prepare_v1310_sources_with_design_context(tmp_path, feature_slug, version)

    create = _invoke(["prototype", "create", feature, "--project", str(tmp_path), "--version", version, "--json"])
    assert create.exit_code == 0, create.stdout
    root = tmp_path / "docs" / "beacon" / version / "prototype" / feature_slug
    matrix = json.loads((root / "automation-priority-matrix.json").read_text(encoding="utf-8"))
    classes = {item["priority_class"] for item in matrix["entries"]}
    assert "primary-automation" in classes or "release-blocker" in classes
    md = (root / "automation-priority-matrix.md").read_text(encoding="utf-8")
    assert "Priority Class" in md
