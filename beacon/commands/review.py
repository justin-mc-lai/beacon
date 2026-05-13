"""Beacon review command - implementation-stage spec/quality writeback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.artifact_update_obligations import (
    blocking_obligations,
    load_artifact_update_obligations,
    update_artifact_update_obligation,
)
from beacon.utils.artifact_paths import execution_file_candidates, execution_file_output, human_execution_dir, human_execution_file, qa_matrix_candidates
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.implementation_plan import (
    implementation_plan_supported,
    load_implementation_plan_progress,
)
from beacon.utils.learning_loop import requirement_rewrite_input_path
from beacon.utils.material_audit import build_material_audit
from beacon.utils.project_skills import evaluate_project_profile_gate
from beacon.utils.prototype_support import feature_requires_prototype
from beacon.utils.prototype_utils import (
    build_anti_ai_ui_contract,
    build_design_template_catalog,
    evaluate_prototype_status,
    normalize_design_preset_choice,
    review_prototype_bundle,
)
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.requirement_closure import build_requirement_closure
from beacon.utils.runtime_projection_store import runtime_projection_transaction_contract
from beacon.utils.runtime import now_iso
from beacon.utils.ceo_review_surface import run_ceo_review
from beacon.utils.design_review_surface import write_design_review_transaction
from beacon.utils.story_state import load_story_state
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.workflow_memory import resolve_workflow_run_id
from beacon.utils.writeback import (
    record_acceptance_writeback,
    record_verification_writeback,
    sync_acceptance_workflow_closure,
)
from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version

app = typer.Typer(name="review", help="Formal implementation-stage review actions")


def _slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _feature_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "base": base,
        "execution": human_execution_dir(project_root, version),
        "user_story": base / "user-story" / f"{slug}.md",
        "prd": base / "prd" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "ac_matrix": qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0],
        "prototype_dir": base / "prototype" / slug,
        "implementation_marker": project_root / ".beacon" / "state" / f"implementation-{slug}.json",
        "implementation_summary": execution_file_candidates(project_root, version, f"implementation-summary-{slug}.json")[0],
    }


def _resolve_acceptance_workflow_run_id(project_root: Path, version: str, feature: str) -> str:
    run_id = resolve_workflow_run_id(project_root, version=version, feature=feature)
    if run_id:
        return run_id
    execution_root = project_root / "docs" / "beacon" / version / ".machine" / "execution"
    for candidate in (
        execution_root / "terminal.json",
        execution_root / "delivery-manifest.json",
    ):
        payload = _read_json_if_exists(candidate)
        value = str(payload.get("run_id", "") or "").strip()
        resolved = resolve_workflow_run_id(project_root, run_id=value, version=version, feature=feature)
        if resolved:
            return resolved
    return ""


def _write_review_artifacts(
    *,
    project_root: Path,
    version: str,
    payload: dict[str, Any],
    markdown: str,
    artifact_name: str,
) -> dict[str, str]:
    json_path = execution_file_output(project_root, version, f"{artifact_name}.json")
    md_path = human_execution_file(project_root, version, f"{artifact_name}.md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    refresh_evidence_manifest(
        project_root,
        refs=[
            str(json_path.relative_to(project_root)),
            str(md_path.relative_to(project_root)),
        ],
        version=version,
    )
    return {"json": str(json_path), "markdown": str(md_path)}


def _resolved_operational_version(project_root: Path, version: str, command_name: str) -> str:
    try:
        return resolve_operational_docs_version(project_root, version, command_name=command_name)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc


def _render_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- version: `{payload.get('version')}`",
        f"- status: `{payload.get('status')}`",
        f"- gate_ready: `{payload.get('gate_ready')}`",
    ]
    if "gate_ready" in payload:
        lines.append(f"- gate_ready: `{payload.get('gate_ready')}`")
    lines.extend(["", "## Issues"])
    issues = payload.get("issues", [])
    if issues:
        for item in issues:
            lines.append(f"- `{item.get('reason_code', 'review_issue')}`: {item.get('message', '')}")
    else:
        lines.append("- none")
    recommendations = payload.get("recommendations", [])
    lines.extend(["", "## Recommendations"])
    if recommendations:
        for item in recommendations:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    requirement_closure = payload.get("requirement_closure", {}) if isinstance(payload.get("requirement_closure"), dict) else {}
    if requirement_closure.get("enabled"):
        lines.extend(
            [
                "",
                "## Requirement Closure",
                f"- status: `{requirement_closure.get('status', 'unknown')}`",
                f"- covered_ac_ids: `{', '.join(requirement_closure.get('coverage', {}).get('covered_ac_ids', []))}`",
            ]
        )
    return "\n".join(lines) + "\n"


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _design_security_review(paths: dict[str, Path]) -> dict[str, Any]:
    texts: list[str] = []
    for key in ("user_story", "prd"):
        path = paths[key]
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
    joined = "\n".join(texts)
    normalized = joined.lower()
    findings: list[dict[str, Any]] = []

    def add_finding(*, reason_code: str, severity: str, message: str, evidence: list[str]) -> None:
        findings.append(
            {
                "reason_code": reason_code,
                "severity": severity,
                "message": message,
                "evidence": evidence,
            }
        )

    has_upload_surface = any(token in normalized for token in ("upload", "上传", "file", "附件", "asset"))
    has_upload_constraints = any(
        token in normalized
        for token in ("mime", "format", "大小", "size", "virus", "scan", "extension", "格式", "max ")
    )
    if has_upload_surface and not has_upload_constraints:
        add_finding(
            reason_code="upload_constraints_missing",
            severity="high",
            message="upload-like surfaces appear in the design, but file constraints and validation boundaries are unspecified",
            evidence=[str(paths["user_story"].name), str(paths["prd"].name)],
        )

    privileged_action = any(
        token in normalized
        for token in ("approve", "release", "delete", "admin", "review", "publish", "审核", "发布", "删除", "审批")
    )
    role_boundary_defined = any(
        token in normalized
        for token in ("role", "permission", "authorization", "auth", "actor", "权限", "角色", "授权")
    )
    if privileged_action and not role_boundary_defined:
        add_finding(
            reason_code="privileged_action_role_boundary_missing",
            severity="high",
            message="privileged actions are present, but actor/role boundaries are not explicit in the requirement materials",
            evidence=[str(paths["user_story"].name), str(paths["prd"].name)],
        )

    secret_surface = any(
        token in normalized
        for token in ("token", "secret", "api key", "password", "credential", "密钥", "令牌", "密码")
    )
    secret_handling_defined = any(
        token in normalized
        for token in ("mask", "redact", "rotate", "vault", "encrypt", "secure storage", "脱敏", "加密")
    )
    if secret_surface and not secret_handling_defined:
        add_finding(
            reason_code="secret_handling_unspecified",
            severity="high",
            message="credential-like surfaces are mentioned without masking, rotation, or secure-storage guidance",
            evidence=[str(paths["user_story"].name), str(paths["prd"].name)],
        )

    external_surface = any(
        token in normalized
        for token in ("oauth", "webhook", "third-party", "external", "payment", "integration", "回调", "第三方", "外部")
    )
    trust_boundary_defined = any(
        token in normalized
        for token in ("trust boundary", "callback validation", "signature", "origin", "boundary", "边界", "签名", "来源校验")
    )
    if external_surface and not trust_boundary_defined:
        add_finding(
            reason_code="integration_trust_boundary_unspecified",
            severity="medium",
            message="external integration surfaces appear in the design, but trust-boundary validation is not explicit",
            evidence=[str(paths["user_story"].name), str(paths["prd"].name)],
        )

    audit_required = has_upload_surface or privileged_action
    audit_defined = any(
        token in normalized
        for token in ("audit", "log", "evidence", "trace", "history", "审计", "日志", "证据", "追踪")
    )
    if audit_required and not audit_defined:
        add_finding(
            reason_code="audit_trace_missing",
            severity="medium",
            message="the design includes sensitive actions but does not describe auditability or evidence trace requirements",
            evidence=[str(paths["user_story"].name), str(paths["prd"].name)],
        )

    severity_counts = {
        "high": sum(1 for item in findings if item.get("severity") == "high"),
        "medium": sum(1 for item in findings if item.get("severity") == "medium"),
    }
    status = "pass"
    if severity_counts["high"] > 0:
        status = "fail"
    elif severity_counts["medium"] > 0:
        status = "warn"
    return {
        "mode": "cso-inspired-design-review",
        "status": status,
        "security_dimensions": [
            "privileged_action_boundaries",
            "upload_and_file_constraints",
            "secret_handling_surfaces",
            "external_integration_boundaries",
            "auditability_and_evidence",
        ],
        "severity_counts": severity_counts,
        "findings": findings,
    }


def _design_requirement_review(paths: dict[str, Path]) -> dict[str, Any]:
    texts: list[str] = []
    evidence_refs: list[str] = []
    for key in ("user_story", "prd", "test_case"):
        path = paths[key]
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
            evidence_refs.append(str(path.name))
    joined = "\n".join(texts)
    lowered = joined.lower()

    findings: list[dict[str, Any]] = []

    def add_finding(*, reason_code: str, severity: str, message: str) -> None:
        findings.append(
            {
                "reason_code": reason_code,
                "severity": severity,
                "message": message,
                "evidence": evidence_refs,
            }
        )

    has_page_signal = any(
        token in lowered
        for token in (
            "page",
            "screen",
            "ui",
            "ux",
            "wireframe",
            "route",
            "navigation",
            "state",
            "component",
            "页面",
            "界面",
            "交互",
            "原型",
            "路由",
            "导航",
            "状态",
            "组件",
        )
    )
    has_hierarchy_signal = any(
        token in lowered
        for token in ("hierarchy", "information architecture", "layout", "section", "层级", "布局", "信息架构")
    )
    has_state_signal = any(
        token in lowered
        for token in ("state", "empty", "loading", "error", "success", "状态", "空态", "加载", "异常", "错误")
    )
    has_interaction_signal = any(
        token in lowered
        for token in ("click", "tap", "submit", "interaction", "flow", "trigger", "点击", "提交", "交互", "流程")
    )

    if has_page_signal and not has_hierarchy_signal:
        add_finding(
            reason_code="page_hierarchy_unspecified",
            severity="medium",
            message="UI/UX-related requirement materials mention pages or surfaces, but information hierarchy remains implicit.",
        )
    if has_page_signal and not has_state_signal:
        add_finding(
            reason_code="state_model_missing",
            severity="high",
            message="UI/UX-related requirement materials mention pages or routes, but user-visible states are not explicit.",
        )
    if has_page_signal and not has_interaction_signal:
        add_finding(
            reason_code="interaction_contract_ambiguous",
            severity="medium",
            message="UI/UX-related requirement materials mention pages or surfaces, but interaction triggers and transitions are ambiguous.",
        )

    status = "pass"
    if any(str(item.get("severity", "")).lower() == "high" for item in findings):
        status = "fail"
    elif findings:
        status = "warn"
    return {
        "mode": "requirement-driven-design-review",
        "status": status,
        "findings": findings,
        "ui_surface_detected": has_page_signal,
        "hierarchy_signal": has_hierarchy_signal,
        "state_signal": has_state_signal,
        "interaction_signal": has_interaction_signal,
    }


def _recommended_design_preset(text: str) -> str:
    lowered = str(text or "").lower()
    if any(token in lowered for token in ("admin", "console", "dashboard", "operator", "workbench", "management", "管理")):
        return "operator-console"
    if any(token in lowered for token in ("docs", "document", "summary", "report", "reader", "editorial", "material", "文档", "总结", "报告")):
        return "editorial-calm"
    return "restrained-product"


def _design_baseline_review(paths: dict[str, Path], version: str) -> dict[str, Any]:
    texts: list[str] = []
    for key in ("user_story", "prd", "test_case"):
        path = paths[key]
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
    joined = "\n".join(texts)
    lowered = joined.lower()
    template_catalog = build_design_template_catalog(version)
    anti_ai_contract = build_anti_ai_ui_contract(version)
    import re
    preset_match = re.search(r"design_preset\s*[:=]\s*([A-Za-z0-9_-]+)", joined, re.IGNORECASE)
    override_match = re.search(r"design_preset_override_reason\s*[:=]\s*(.+)", joined, re.IGNORECASE)
    requested_preset = str(preset_match.group(1)).strip() if preset_match else ""
    override_reason = str(override_match.group(1)).strip() if override_match else ""
    normalized = normalize_design_preset_choice(version, requested_preset, override_reason)
    recommended = _recommended_design_preset(joined)
    findings: list[dict[str, Any]] = []

    def add_finding(*, reason_code: str, severity: str, message: str) -> None:
        findings.append({"reason_code": reason_code, "severity": severity, "message": message})

    for token, reason_code in (
        ("gradient text", "anti_ai_gradient_text_requested"),
        ("purple gradient", "anti_ai_purple_gradient_requested"),
        ("glassmorphism", "anti_ai_glassmorphism_requested"),
        ("card inside card", "anti_ai_nested_card_requested"),
        ("accent side stripe", "anti_ai_accent_stripe_requested"),
        ("bounce", "anti_ai_bounce_motion_requested"),
        ("elastic", "anti_ai_elastic_motion_requested"),
    ):
        if token in lowered:
            add_finding(reason_code=reason_code, severity="medium", message=f"requirement materials reference discouraged anti-AI pattern: {token}")
    if requested_preset and not normalized.get("design_preset_valid") and not override_reason:
        add_finding(
            reason_code="design_preset_not_in_fixed_catalog",
            severity="medium",
            message="design preset is outside the fixed template catalog and does not record an explicit override reason",
        )
    selected_canonical = str(normalized.get("canonical_design_preset") or normalized.get("design_preset") or "").strip()
    if requested_preset and not override_reason and selected_canonical and selected_canonical != recommended:
        add_finding(
            reason_code="design_template_fit_mismatch",
            severity="medium",
            message=f"selected template `{selected_canonical}` does not match the inferred surface baseline `{recommended}`",
        )
    status = "pass"
    if findings:
        status = "warn"
    return {
        "mode": "anti-ai-template-baseline-review",
        "status": status,
        "template_catalog_count": int(template_catalog.get("template_count") or 0),
        "template_catalog": template_catalog,
        "anti_ai_ui_contract": anti_ai_contract,
        "requested_design_preset": requested_preset,
        "selected_design_preset": str(normalized.get("design_preset") or ""),
        "canonical_design_preset": str(normalized.get("canonical_design_preset") or ""),
        "recommended_design_preset": recommended,
        "override_reason": override_reason,
        "findings": findings,
    }


def _render_design_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Beacon Review Design",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- version: `{payload.get('version')}`",
        f"- status: `{payload.get('status')}`",
        f"- design_review_outcome: `{payload.get('design_review_outcome')}`",
        f"- prototype_review_status: `{payload.get('prototype_review_status')}`",
        "",
        "## Issues",
    ]
    issues = payload.get("issues", []) if isinstance(payload.get("issues"), list) else []
    if issues:
        for item in issues:
            lines.append(f"- `{item.get('reason_code', 'review_issue')}` [{item.get('severity', 'medium')}]: {item.get('message', '')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Security Design Findings"])
    security_review = payload.get("security_design_review", {}) if isinstance(payload.get("security_design_review"), dict) else {}
    findings = security_review.get("findings", []) if isinstance(security_review.get("findings"), list) else []
    if findings:
        for item in findings:
            lines.append(f"- `{item.get('reason_code')}` [{item.get('severity')}]: {item.get('message')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Recommendations"])
    recommendations = payload.get("recommendations", []) if isinstance(payload.get("recommendations"), list) else []
    if recommendations:
        for item in recommendations:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


@app.command("spec")
def review_spec(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review spec drift after implementation and write formal review artifacts."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "review spec")
    paths = _feature_paths(project_root, resolved_version, feature)
    issues: list[dict[str, Any]] = []
    recommendations: list[str] = []

    required_docs = {
        "user_story_missing": paths["user_story"],
        "prd_missing": paths["prd"],
        "test_case_missing": paths["test_case"],
        "ac_matrix_missing": paths["ac_matrix"],
    }
    for reason_code, path in required_docs.items():
        if not path.exists():
            issues.append(
                {
                    "reason_code": reason_code,
                    "severity": "critical",
                    "message": f"required artifact missing: {path.relative_to(project_root)}",
                }
            )

    if not paths["implementation_marker"].exists():
        issues.append(
            {
                "reason_code": "implementation_review_marker_missing",
                "severity": "warn",
                "message": f"implementation marker missing: {paths['implementation_marker'].relative_to(project_root)}",
            }
        )
        recommendations.append("Run workflow implementation stage with an explicit external command before spec review.")

    if paths["prototype_dir"].exists():
        proto_status = evaluate_prototype_status(project_root, resolved_version, feature)
        if proto_status.get("stale"):
            issues.append(
                {
                    "reason_code": "prototype_spec_drift_detected",
                    "severity": "warn",
                    "message": "prototype bundle is stale relative to current requirement artifacts",
                }
            )
            recommendations.append("Regenerate or review the prototype bundle to realign with PRD/User Story/Test Case.")
        if str(proto_status.get("review_status", "")) == "fail":
            issues.append(
                {
                    "reason_code": "prototype_review_failed",
                    "severity": "warn",
                    "message": "prototype review is failing; prototype may not reflect current requirement contracts",
                }
            )

    try:
        runtime_tx_contract = runtime_projection_transaction_contract(
            project_root=project_root,
            docs_version=resolved_version,
            feature=feature,
        )
    except Exception:  # noqa: BLE001
        runtime_tx_contract = {"status": "warn"}
    if str(runtime_tx_contract.get("status") or "").lower() == "fail":
        issues.append(
            {
                "reason_code": str(runtime_tx_contract.get("reason_code") or "runtime_projection_failed_transaction"),
                "severity": "critical",
                "message": str(runtime_tx_contract.get("message") or "runtime projection transaction contract failed"),
                "details": runtime_tx_contract.get("details", {}),
            }
        )
        recommendations.append("Run `beacon doctor rebuild-runtime-ledger --project-root . --version <version>` and clear failed runtime transaction before spec/release.")

    implementation_summary = {}
    if paths["implementation_summary"].exists():
        try:
            loaded_summary = json.loads(paths["implementation_summary"].read_text(encoding="utf-8"))
            if isinstance(loaded_summary, dict):
                implementation_summary = loaded_summary
        except Exception:  # noqa: BLE001
            implementation_summary = {}
    artifact_updates = implementation_summary.get("artifact_updates") if isinstance(implementation_summary, dict) else {}
    if isinstance(artifact_updates, dict):
        for artifact, value in artifact_updates.items():
            if isinstance(value, dict) and bool(value.get("required")):
                recommendations.append(
                    f"Update `{artifact}` after implementation: {value.get('reason', 'implementation summary requested writeback')}"
                )
    rewrite_input = requirement_rewrite_input_path(project_root, version=resolved_version, feature=feature)
    if rewrite_input.exists():
        try:
            learning_input = json.loads(rewrite_input.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            learning_input = {}
        rewrite_targets = learning_input.get("rewrite_targets") if isinstance(learning_input, dict) else {}
        if isinstance(rewrite_targets, dict):
            for section in ("prd", "test_case", "version_research"):
                for item in rewrite_targets.get(section, []) if isinstance(rewrite_targets.get(section), list) else []:
                    recommendations.append(f"[{section}] {item}")

    plan_progress = (
        load_implementation_plan_progress(project_root, version=resolved_version, feature=feature)
        if implementation_plan_supported(resolved_version)
        else {}
    )
    if plan_progress and str(plan_progress.get("status", "")).strip().lower() == "blocked":
        issues.append(
            {
                "reason_code": "implementation_plan_blocked",
                "severity": "warn",
                "message": f"implementation plan has blocked tasks: {plan_progress.get('blocked_task_ids', [])}",
            }
        )
        recommendations.append("Resolve blocked implementation plan tasks before final release gate.")

    requirement_closure = build_requirement_closure(
        project_root,
        resolved_version,
        feature,
        implementation_summary=implementation_summary,
    )
    if requirement_closure.get("enabled"):
        issues.extend(requirement_closure.get("issues", []))
        for item in requirement_closure.get("issues", []):
            if not isinstance(item, dict):
                continue
            reason_code = str(item.get("reason_code", "") or "").strip()
            if reason_code == "user_story_acceptance_missing":
                recommendations.append("补齐 User Story / PRD 中可解析的 AC，确保 review-spec 可以抽取 acceptance 条目。")
            elif reason_code in {"test_case_traceability_missing", "prd_user_story_test_case_traceability_broken"}:
                recommendations.append("补齐 Test Case 或 AC-Test Matrix，让每个 AC 都有可追踪测试覆盖。")
            elif reason_code == "implementation_requirement_traceability_missing":
                recommendations.append("通过 implement 生成带 requirement_traceability 的标准 implementation summary。")
            elif reason_code == "implementation_delivery_summary_missing":
                recommendations.append("补齐 delivery_surfaces 固定结构，确保 single/team/ralph 输出同形摘要。")
            elif reason_code == "revision_cleanup_delta_missing":
                recommendations.append("先重新 freeze 当前 changed revision，生成最新 revision delta，再重新生成 implement plan。")
            elif reason_code == "superseded_surface_cleanup_missing":
                recommendations.append("在 implementation summary 中补齐 revision_cleanup，明确旧实现已删除或被保留及其依据。")
            elif reason_code == "superseded_surface_retention_unjustified":
                recommendations.append("为保留的 legacy surface 写出 cleanup rationale，说明为什么它仍被最新 frozen truth 保留。")

    status = "pass"
    if any(item.get("severity") == "critical" for item in issues):
        status = "fail"
    elif issues:
        status = "warn"

    payload = {
        "schema_version": "1.0",
        "review_type": "spec",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "generated_at": now_iso(),
        "status": status,
        "issues": issues,
        "recommendations": recommendations,
        "artifact_updates": artifact_updates if isinstance(artifact_updates, dict) else {},
        "implementation_plan_progress": plan_progress,
        "requirement_closure": requirement_closure,
    }
    artifact_name = f"review-spec-{_slug(feature)}"
    payload["artifacts"] = _write_review_artifacts(
        project_root=project_root,
        version=resolved_version,
        payload=payload,
        markdown=_render_markdown("Beacon Review Spec", payload),
        artifact_name=artifact_name,
    )

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Review spec complete: {status}")
    typer.echo(f"✓ Review report: {paths['execution'] / f'{artifact_name}.md'}")


@app.command("quality")
def review_quality(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review verify output and gate readiness after quality verification."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "review quality")
    paths = _feature_paths(project_root, resolved_version, feature)
    issues: list[dict[str, Any]] = []
    recommendations: list[str] = []

    auto_test_status_path = project_root / ".beacon" / "auto-test-status.json"
    qa_status = load_qa_status(project_root)
    verify_status = "missing"
    if auto_test_status_path.exists():
        try:
            auto_test_status = json.loads(auto_test_status_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_test_status = {}
        verify_status = str(auto_test_status.get("status", "missing") or "missing").lower()
    else:
        auto_test_status = {}

    if verify_status != "passed":
        issues.append(
            {
                "reason_code": "verify_not_passed",
                "severity": "critical",
                "message": f"verify evidence status is {verify_status}",
            }
        )
        recommendations.append("Run or refresh verify/auto-test evidence before quality review.")
    evidence_done = bool(qa_status.get("evidence_done", False)) if isinstance(qa_status, dict) and qa_status else verify_status == "passed"
    if not evidence_done:
        issues.append(
            {
                "reason_code": "evidence_not_closed",
                "severity": "critical",
                "message": "implementation_done may be true but evidence_done is still false",
            }
        )
        recommendations.append("Close feature QA evidence and writeback obligations before quality review passes.")

    obligations = load_artifact_update_obligations(project_root, feature=feature)
    open_obligations = [
        item
        for item in blocking_obligations(obligations)
        if str(item.get("artifact", "")).strip().lower() != "review_quality"
    ]
    if open_obligations:
        issues.append(
            {
                "reason_code": "artifact_updates_pending",
                "severity": "critical",
                "message": f"artifact update obligations still open: {[item.get('artifact') for item in open_obligations]}",
            }
        )
        recommendations.append("Resolve artifact writeback obligations before treating quality review as gate-ready.")

    material_audit = build_material_audit(project_root, version=resolved_version, strict=False)
    if str(material_audit.get("status", "fail")).lower() == "fail":
        issues.append(
            {
                "reason_code": "formal_package_closure_missing",
                "severity": "critical",
                "message": "formal package closure is incomplete for current version",
            }
        )

    prototype_gate_ready = None
    if paths["prototype_dir"].exists():
        proto_status = evaluate_prototype_status(project_root, resolved_version, feature)
        prototype_gate_ready = bool(proto_status.get("gate_ready"))
        if not prototype_gate_ready:
            issues.append(
                {
                    "reason_code": "prototype_gate_not_ready",
                    "severity": "warn",
                    "message": "prototype exists but is not gate-ready",
                }
            )
            recommendations.append("Review/freeze the prototype bundle before final gate.")

    try:
        runtime_tx_contract = runtime_projection_transaction_contract(
            project_root=project_root,
            docs_version=resolved_version,
            feature=feature,
        )
    except Exception:  # noqa: BLE001
        runtime_tx_contract = {"status": "warn"}
    if str(runtime_tx_contract.get("status") or "").lower() == "fail":
        issues.append(
            {
                "reason_code": str(runtime_tx_contract.get("reason_code") or "runtime_projection_failed_transaction"),
                "severity": "critical",
                "message": str(runtime_tx_contract.get("message") or "runtime projection transaction contract failed"),
                "details": runtime_tx_contract.get("details", {}),
            }
        )
        recommendations.append("Rebuild runtime ledger and ensure transaction metadata consistency before quality gate.")

    coverage = compute_coverage_metrics(project_root, version=resolved_version, feature=feature)
    if not bool(coverage.get("full_coverage")):
        issues.append(
            {
                "reason_code": "coverage_incomplete",
                "severity": "warn",
                "message": (
                    f"coverage incomplete: story={coverage.get('implemented_story')}/{coverage.get('planned_story')}, "
                    f"ac={coverage.get('tested_ac')}/{coverage.get('total_ac')}, "
                    f"tc={coverage.get('executed_tc')}/{coverage.get('total_tc')}"
                ),
            }
        )

    project_gate = evaluate_project_profile_gate(project_root, version=resolved_version, feature=feature)
    if project_gate.get("status") == "blocked":
        for gate_issue in project_gate.get("issues", []):
            if not isinstance(gate_issue, dict):
                continue
            issues.append(
                {
                    "reason_code": str(gate_issue.get("reason_code", "required_evidence_missing")),
                    "severity": "critical",
                    "message": str(gate_issue.get("message", "project profile evidence gate blocked")),
                }
            )
        if project_gate.get("profile_id"):
            recommendations.append(
                f"Run `beacon verify run \"{feature}\" --project \"{project_root}\" --version {resolved_version} --profile {project_gate.get('profile_id')}` to satisfy project-specific verification."
            )

    plan_progress = (
        load_implementation_plan_progress(project_root, version=resolved_version, feature=feature)
        if implementation_plan_supported(resolved_version)
        else {}
    )
    if plan_progress:
        if str(plan_progress.get("status", "")).strip().lower() == "blocked":
            issues.append(
                {
                    "reason_code": "implementation_plan_blocked",
                    "severity": "critical",
                    "message": f"implementation plan has blocked tasks: {plan_progress.get('blocked_task_ids', [])}",
                    "blocked": True,
                }
            )
            recommendations.append("Clear blocked implementation plan tasks before quality review can pass.")
        elif int((plan_progress.get("counts") or {}).get("completed", 0) or 0) < int((plan_progress.get("counts") or {}).get("total", 0) or 0):
            issues.append(
                {
                    "reason_code": "implementation_plan_incomplete",
                    "severity": "warn",
                    "message": f"implementation plan progress incomplete: {plan_progress.get('counts', {})}",
                    "blocked": False,
                }
            )

    gate_ready = not any(item.get("severity") == "critical" for item in issues)
    status = "pass" if gate_ready and not issues else ("fail" if not gate_ready else "warn")

    payload = {
        "schema_version": "1.0",
        "review_type": "quality",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "generated_at": now_iso(),
        "status": status,
        "gate_ready": gate_ready,
        "verify_status": verify_status,
        "prototype_gate_ready": prototype_gate_ready,
        "project_profile_gate": project_gate,
        "issues": issues,
        "recommendations": recommendations,
        "evidence_done": evidence_done,
        "artifact_update_obligations": obligations,
        "implementation_plan_progress": plan_progress,
    }
    artifact_name = f"review-quality-{_slug(feature)}"
    payload["artifacts"] = _write_review_artifacts(
        project_root=project_root,
        version=resolved_version,
        payload=payload,
        markdown=_render_markdown("Beacon Review Quality", payload),
        artifact_name=artifact_name,
    )
    if gate_ready:
        update_artifact_update_obligation(
            project_root,
            feature=feature,
            artifact="review_quality",
            status="completed",
            note="review quality passed and gate_ready=true",
        )

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Review quality complete: {status}")
    typer.echo(f"✓ Review report: {paths['execution'] / f'{artifact_name}.md'}")


@app.command("design")
def review_design(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Review prototype design quality plus cso-inspired software-design security signals."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    paths = _feature_paths(project_root, resolved_version, feature)
    issues: list[dict[str, Any]] = []
    recommendations: list[str] = []
    truth_missing = False
    required_docs = {
        "user_story_missing": paths["user_story"],
        "prd_missing": paths["prd"],
        "test_case_missing": paths["test_case"],
    }
    for reason_code, path in required_docs.items():
        if not path.exists():
            truth_missing = True
            issues.append(
                {
                    "reason_code": reason_code,
                    "severity": "critical",
                    "message": f"required artifact missing: {path.relative_to(project_root)}",
                }
            )

    prototype_required = feature_requires_prototype(project_root, resolved_version, feature)
    prototype_exists = paths["prototype_dir"].exists()
    requirement_design_review = _design_requirement_review(paths)
    design_baseline_review = _design_baseline_review(paths, resolved_version)

    prototype_payload: dict[str, Any] = {}
    prototype_review_status = "not_required"
    design_review_outcome = "missing"
    if prototype_exists:
        try:
            prototype_payload = review_prototype_bundle(project_root, resolved_version, feature)
        except (FileNotFoundError, ValueError) as exc:
            issues.append(
                {
                    "reason_code": "prototype_review_unavailable",
                    "severity": "critical",
                    "message": str(exc),
                }
            )
        else:
            prototype_review_status = str(prototype_payload.get("overall_status", "missing") or "missing")
            design_review_outcome = str(prototype_payload.get("design_review_outcome", "missing") or "missing")
            if design_review_outcome == "blocked":
                issues.append(
                    {
                        "reason_code": "design_review_blocked",
                        "severity": "critical",
                        "message": "prototype design review is blocked by critical guideline or design-governance findings",
                    }
                )
            elif design_review_outcome == "revise":
                issues.append(
                    {
                        "reason_code": "design_review_revise",
                        "severity": "warn",
                        "message": "prototype design review requires revision before freeze/gate",
                    }
                )
    else:
        if prototype_required:
            prototype_review_status = "missing"
            issues.append(
                {
                    "reason_code": "prototype_missing",
                    "severity": "warn" if not truth_missing else "critical",
                    "message": "this feature still requires a prototype bundle before formal prototype freeze.",
                }
            )
            recommendations.append("Run `beacon prototype create ...` after design-review findings are accepted.")
        else:
            prototype_review_status = "not_required"
            design_review_outcome = "prototype_not_required"

    for finding in requirement_design_review.get("findings", []):
        if not isinstance(finding, dict):
            continue
        severity = str(finding.get("severity", "medium") or "medium")
        issues.append(
            {
                "reason_code": str(finding.get("reason_code", "ux_evidence_missing") or "ux_evidence_missing"),
                "severity": "critical" if severity == "high" else "warn",
                "message": str(finding.get("message", "") or ""),
            }
        )

    for finding in design_baseline_review.get("findings", []):
        if not isinstance(finding, dict):
            continue
        severity = str(finding.get("severity", "medium") or "medium")
        issues.append(
            {
                "reason_code": str(finding.get("reason_code", "design_baseline_missing") or "design_baseline_missing"),
                "severity": "critical" if severity == "high" else "warn",
                "message": str(finding.get("message", "") or ""),
            }
        )

    security_design_review = _design_security_review(paths)
    for finding in security_design_review.get("findings", []):
        if not isinstance(finding, dict):
            continue
        severity = str(finding.get("severity", "medium") or "medium")
        issues.append(
            {
                "reason_code": str(finding.get("reason_code", "design_security_gap") or "design_security_gap"),
                "severity": "critical" if severity == "high" else "warn",
                "message": str(finding.get("message", "") or ""),
            }
        )
    if security_design_review.get("severity_counts", {}).get("high"):
        recommendations.append("Add explicit role/auth boundaries, sensitive-surface controls, and validation constraints to the user-story/PRD.")
    if security_design_review.get("severity_counts", {}).get("medium"):
        recommendations.append("Backfill auditability, trust-boundary, and evidence-trace rules before release gate.")
    if requirement_design_review.get("findings"):
        recommendations.append("Backfill page hierarchy, state model, and interaction contract details into PRD/user-story/test-case before prototype freeze.")
    if design_baseline_review.get("findings"):
        recommendations.append("Align the feature to the fixed template catalog and remove discouraged anti-AI visual patterns unless an explicit override is justified.")
    if design_review_outcome == "blocked":
        recommendations.append("Fix critical design guideline findings before design/governance freeze.")
    elif design_review_outcome == "revise":
        recommendations.append("Apply the suggested design iteration writeback and rerun `beacon review design`.")

    gate_ready = not any(item.get("severity") == "critical" for item in issues)
    if gate_ready:
        if prototype_required:
            design_review_outcome = "ready_for_prototype"
        elif design_review_outcome in {"missing", ""}:
            design_review_outcome = "prototype_not_required"
    status = "pass" if gate_ready and not issues else ("fail" if not gate_ready else "warn")
    payload = {
        "schema_version": "1.0",
        "review_type": "design",
        "feature": feature,
        "feature_slug": _slug(feature),
        "version": resolved_version,
        "generated_at": now_iso(),
        "status": status,
        "gate_ready": gate_ready,
        "prototype_review_status": prototype_review_status,
        "design_review_outcome": design_review_outcome,
        "prototype_required": prototype_required,
        "prototype_review": {
            "overall_status": prototype_payload.get("overall_status", ""),
            "iteration_writeback_path": prototype_payload.get("iteration_writeback_path", ""),
        },
        "requirement_design_review": requirement_design_review,
        "design_baseline_review": design_baseline_review,
        "security_design_review": security_design_review,
        "issues": issues,
        "recommendations": recommendations,
    }
    artifact_name = f"review-design-{_slug(feature)}"
    payload["artifacts"] = _write_review_artifacts(
        project_root=project_root,
        version=resolved_version,
        payload=payload,
        markdown=_render_design_markdown(payload),
        artifact_name=artifact_name,
    )
    payload["support_surface_transaction"] = write_design_review_transaction(
        project_root,
        version=resolved_version,
        feature=feature,
        status=status,
        design_verdict=(
            "prototype_not_required"
            if gate_ready and not prototype_required
            else "ready_for_prototype"
            if gate_ready and prototype_required
            else "needs_design_revision"
        ),
        issues=issues,
        prototype_exists=prototype_exists,
        evidence_refs=[
            str(payload["artifacts"]["markdown"]),
            str(payload["artifacts"]["json"]),
        ],
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Review design complete: {status}")
    typer.echo(f"✓ Review report: {paths['execution'] / f'{artifact_name}.md'}")


@app.command("ceo")
def review_ceo(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    focus: str = typer.Option("full", "--focus", help="Focus: problem|scope|promise|full"),
    decision: str = typer.Option("", "--decision", help="Optional explicit decision: expand|hold|reduce|reframe"),
    change_intent: str = typer.Option("", "--change-intent", help="Optional operator change-intent hint"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Run version-level CEO review over frozen requirement materials."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = run_ceo_review(
        project_root,
        version=resolved_version,
        feature=feature,
        focus=focus,
        decision=decision,
        change_intent=change_intent,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ CEO review complete: {payload.get('status')}")
    next_route = payload.get("next_route", {}) if isinstance(payload.get("next_route"), dict) else {}
    if next_route.get("command"):
        typer.echo(f"✓ Next route: {next_route.get('command')}")


@app.command("accept")
def review_accept(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    reviewer: str = typer.Option("qa", "--reviewer", help="Acceptance actor"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Formally accept current active revision after verify evidence passes."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = _resolved_operational_version(project_root, version, "review accept")
    story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    items = [item for item in story.get("items", []) if isinstance(item, dict)]
    ac_ids = [str(item.get("id", "")) for item in items if str(item.get("kind", "")) == "ac"]
    test_ids = [str(item.get("id", "")) for item in items if str(item.get("kind", "")) == "test"]
    auto_test_path = project_root / ".beacon" / "auto-test-status.json"
    verify_passed = False
    if auto_test_path.exists():
        try:
            auto_payload = json.loads(auto_test_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_payload = {}
        verify_passed = str(auto_payload.get("status", "")).lower() == "passed"
    if verify_passed:
        record_verification_writeback(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id="review.accept",
            verified_item_ids=[*ac_ids, *test_ids],
            failed_item_ids=[],
            evidence_ref=[str(auto_test_path.relative_to(project_root))],
        )
    obligations = load_artifact_update_obligations(project_root, feature=feature)
    pending_non_acceptance = blocking_obligations(obligations)
    enforce_v119_obligations = tuple(int(part) for part in resolved_version.lstrip("v").split(".")[:3]) >= (1, 1, 9)
    if enforce_v119_obligations and pending_non_acceptance:
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason": "artifact_updates_pending",
            "issues": pending_non_acceptance,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("✗ Review accept blocked: unresolved artifact update obligations")
        raise typer.Exit(2)
    try:
        project_gate = evaluate_project_profile_gate(project_root, version=resolved_version, feature=feature)
        if project_gate.get("status") == "blocked":
            payload = {
                "schema_version": "1.0",
                "feature": feature,
                "version": resolved_version,
                "status": "blocked",
                "reason": "project_profile_gate_blocked",
                "issues": project_gate.get("issues", []),
                "profile_id": project_gate.get("profile_id", ""),
            }
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo("✗ Review accept blocked: project profile evidence gate failed")
            raise typer.Exit(2)
        result = record_acceptance_writeback(project_root, version=resolved_version, feature=feature, accepted_by=reviewer)
        workflow_run_id = _resolve_acceptance_workflow_run_id(project_root, resolved_version, feature)
        lifecycle_sync = sync_acceptance_workflow_closure(
            project_root,
            version=resolved_version,
            feature=feature,
            run_id=workflow_run_id or None,
        )
        if workflow_run_id:
            from beacon.commands.workflow import (
                _sync_terminal_manifest,
                _write_execution_governance_artifacts,
                _write_workflow_terminal_artifacts,
            )
            from beacon.utils.v110_baseline import record_baseline_snapshot

            _write_execution_governance_artifacts(
                project_root=project_root,
                version=resolved_version,
                run_id=workflow_run_id,
                feature=feature,
                workflow_status="completed",
            )
            _write_workflow_terminal_artifacts(
                project_root=project_root,
                version=resolved_version,
                run_id=workflow_run_id,
                feature=feature,
                workflow_status="completed",
                reason="review_accept_completed",
            )
            _sync_terminal_manifest(project_root, version=resolved_version, run_id=workflow_run_id)
            refreshed_sync = sync_acceptance_workflow_closure(
                project_root,
                version=resolved_version,
                feature=feature,
                run_id=workflow_run_id,
                source="review.accept.sync",
            )
            lifecycle_sync = {
                **lifecycle_sync,
                **refreshed_sync,
                "synced_stages": sorted(
                    {
                        *(
                            lifecycle_sync.get("synced_stages", [])
                            if isinstance(lifecycle_sync.get("synced_stages"), list)
                            else []
                        ),
                        *(
                            refreshed_sync.get("synced_stages", [])
                            if isinstance(refreshed_sync.get("synced_stages"), list)
                            else []
                        ),
                    }
                ),
            }
            record_baseline_snapshot(
                project_root,
                run_id=workflow_run_id,
                version=resolved_version,
                feature=feature,
                workflow_status="completed",
            )
            _sync_terminal_manifest(project_root, version=resolved_version, run_id=workflow_run_id)
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "accepted",
            "reviewer": reviewer,
            "story_status": result.get("story", {}).get("status", ""),
            "revision_status": result.get("revision", {}).get("delivery_status", ""),
            "workflow_run_id": lifecycle_sync.get("run_id", ""),
            "workflow_closure_complete": lifecycle_sync.get("closure_complete", False),
            "workflow_gate_pass": lifecycle_sync.get("gate_pass", False),
            "workflow_missing_stages": lifecycle_sync.get("missing_closure_stages", []),
            "workflow_synced_stages": lifecycle_sync.get("synced_stages", []),
            "implementation_plan_progress": (
                load_implementation_plan_progress(project_root, version=resolved_version, feature=feature)
                if implementation_plan_supported(resolved_version)
                else {}
            ),
        }
        update_artifact_update_obligation(
            project_root,
            feature=feature,
            artifact="acceptance",
            status="completed",
            note=f"accepted by {reviewer}",
        )
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            return
        typer.echo(f"✓ Review accept complete: {payload['status']}")
    except ValueError as exc:
        payload = {
            "schema_version": "1.0",
            "feature": feature,
            "version": resolved_version,
            "status": "blocked",
            "reason": str(exc),
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"✗ Review accept blocked: {exc}")
        raise typer.Exit(2)


@app.command("writeback")
def review_writeback(
    feature: str = typer.Argument(..., help="Feature name"),
    artifact: str = typer.Argument(..., help="Artifact obligation name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    status: str = typer.Option("completed", "--status", help="New obligation status"),
    note: str = typer.Option("", "--note", help="Writeback note"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Resolve or update a formal artifact writeback obligation."""
    project_root = Path(project) if project else Path.cwd()
    payload = update_artifact_update_obligation(
        project_root,
        feature=feature,
        artifact=artifact,
        status=status,
        note=note,
    )
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo(f"✓ Artifact writeback updated: {artifact} -> {status}")
