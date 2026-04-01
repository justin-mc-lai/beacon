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
from beacon.utils.artifact_paths import qa_matrix_candidates
from beacon.utils.coverage import compute_coverage_metrics
from beacon.utils.learning_loop import requirement_rewrite_input_path
from beacon.utils.material_audit import build_material_audit
from beacon.utils.project_skills import evaluate_project_profile_gate
from beacon.utils.prototype_utils import evaluate_prototype_status
from beacon.utils.qa_runtime import load_qa_status
from beacon.utils.runtime import now_iso
from beacon.utils.story_state import load_story_state
from beacon.utils.writeback import (
    record_acceptance_writeback,
    record_verification_writeback,
    sync_acceptance_workflow_closure,
)
from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="review", help="Formal implementation-stage review actions")


def _slug(text: str) -> str:
    return "-".join(str(text or "").strip().lower().split())


def _feature_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    slug = _slug(feature)
    base = project_root / "docs" / "beacon" / version
    return {
        "base": base,
        "execution": base / "execution",
        "user_story": base / "user-story" / f"{slug}.md",
        "prd": base / "prd" / f"{slug}.md",
        "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        "ac_matrix": qa_matrix_candidates(project_root, version, slug, "ac-test-matrix")[0],
        "prototype_dir": base / "prototype" / slug,
        "implementation_marker": project_root / ".beacon" / "state" / f"implementation-{slug}.json",
        "implementation_summary": base / "execution" / f"implementation-summary-{slug}.json",
    }


def _write_review_artifacts(
    *,
    payload: dict[str, Any],
    markdown: str,
    execution_dir: Path,
    artifact_name: str,
) -> dict[str, str]:
    execution_dir.mkdir(parents=True, exist_ok=True)
    json_path = execution_dir / f"{artifact_name}.json"
    md_path = execution_dir / f"{artifact_name}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def _render_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- feature: `{payload.get('feature')}`",
        f"- version: `{payload.get('version')}`",
        f"- status: `{payload.get('status')}`",
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
    resolved_version = resolve_target_version(project_root, version)
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
    }
    artifact_name = f"review-spec-{_slug(feature)}"
    payload["artifacts"] = _write_review_artifacts(
        payload=payload,
        markdown=_render_markdown("Beacon Review Spec", payload),
        execution_dir=paths["execution"],
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
    resolved_version = resolve_target_version(project_root, version)
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
    }
    artifact_name = f"review-quality-{_slug(feature)}"
    payload["artifacts"] = _write_review_artifacts(
        payload=payload,
        markdown=_render_markdown("Beacon Review Quality", payload),
        execution_dir=paths["execution"],
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
    resolved_version = resolve_target_version(project_root, version)
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
        lifecycle_sync = sync_acceptance_workflow_closure(
            project_root,
            version=resolved_version,
            feature=feature,
        )
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
