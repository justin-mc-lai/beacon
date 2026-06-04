"""Beacon release command - Release checklist"""
import typer
from typing import Any, Optional
from pathlib import Path
from datetime import datetime
import json
import re

from beacon.utils.artifact_paths import (
    change_docs_file,
    change_file_output,
    machine_change_dir,
    release_checklist_file,
    release_gate_report_file,
)
from beacon.utils.delivery_baseline import load_implementation_delivery_host
from beacon.utils.implementation_plan import load_implementation_plan_progress
from beacon.utils.material_audit import build_requirement_package_gate
from beacon.utils.memory import append_memory_entry
from beacon.utils.project_metadata import metadata_machine_path, verify_project_metadata
from beacon.utils.project_hooks import build_lifecycle_hook_advisory
from beacon.utils.release_scorecard import build_ceo_challenge_coverage, build_release_scorecard
from beacon.utils.v115_delivery import refresh_evidence_manifest
from beacon.utils.revision_state import load_revision_state
from beacon.utils.runtime_projection_store import runtime_projection_transaction_contract
from beacon.utils.story_state import feature_slug
from beacon.utils.technical_review_contract import load_technical_review_contract
from beacon.utils.version_surface import version_surface_repair_commands
from beacon.utils.writeback import acceptance_projection_transaction_contract
from beacon.utils.skill_decision_surface import attach_skill_decision_surface
from beacon.utils.versioning import (
    project_release_feature_enabled,
    project_runtime_feature_enabled,
    resolve_runtime_version,
    resolve_target_version,
)
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="release", help="Release checklist")
_TECHNICAL_ARCHIVE_RE = re.compile(r"^technical-implementation-(?P<slug>.+)\.json$")
BROWSER_RELEASE_GUIDANCE: dict[str, tuple[str, str]] = {
    "protected_surface_session_bridge_missing": (
        "Protected live surface has no session bridge.",
        "Attach a logged-in browser session via `beacon qa session` or provide storage state / cookies before rerunning QA.",
    ),
    "protected_surface_runner_priority_unavailable": (
        "Protected live surface did not have an attached-session runner available.",
        "Prefer `web-access`, `agent-browser`, or Playwright attach/CDP for this surface instead of a bare runner.",
    ),
    "browser_evidence_placeholder_only": (
        "Browser evidence is placeholder-only and does not count as real browser QA closure.",
        "Rerun with a real browser-attached path and collect browser pack, transcript, and replay evidence.",
    ),
    "browser_runtime_admission_missing": (
        "Browser runtime admission evidence is missing from release-facing QA proof.",
        "Rebuild the test contract index and rerun QA so protected-surface admission is recorded in evidence.",
    ),
    "browser_runner_learning_missing": (
        "Runner learning note is missing for a blocked browser QA path.",
        "Regenerate QA evidence so the blocker is written into `.machine/learning/qa/` before release review.",
    ),
}


def _with_release_surface(
    payload: dict[str, Any],
    *,
    reason_code: str = "",
    recommended_command: str = "",
    blocked: Optional[bool] = None,
) -> dict[str, Any]:
    blocked_value = bool(str(payload.get("status", "")).lower() == "blocked") if blocked is None else blocked
    return attach_skill_decision_surface(
        payload,
        stage="release",
        reason_code=reason_code or str(payload.get("reason_code", "") or ""),
        recommended_command=recommended_command or str(payload.get("recommended_command", "") or ""),
        blocked=blocked_value,
        dual_read_required=True,
    )


def _parse_semver_tuple(value: str) -> tuple[int, int, int]:
    text = str(value or "").strip().lower().lstrip("v")
    try:
        major, minor, patch = text.split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _extract_run_id(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    direct = str(payload.get("run_id", "")).strip()
    if direct:
        return direct
    execution = payload.get("execution")
    if isinstance(execution, dict):
        return str(execution.get("run_id", "")).strip()
    return ""


def _extract_version(payload: dict) -> str:
    if not isinstance(payload, dict):
        return ""
    direct = str(payload.get("version", "")).strip()
    if direct:
        return direct
    details = payload.get("details")
    if isinstance(details, dict):
        detail_version = str(details.get("version", "")).strip()
        if detail_version:
            return detail_version
    execution = payload.get("execution")
    if isinstance(execution, dict):
        return str(execution.get("version", "")).strip()
    return ""


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _select_gate_report_path(project_root: Path, *, version: str) -> Path:
    release_gate = release_gate_report_file(project_root)
    generic_gate = project_root / ".beacon" / "gate-report.json"
    for candidate in (release_gate, generic_gate):
        payload = _load_json(candidate)
        if not payload:
            continue
        artifact_version = _extract_version(payload)
        stage = str(payload.get("stage") or "").strip().lower()
        if artifact_version == version and stage in {"", "release"}:
            return candidate
    if release_gate.exists():
        return release_gate
    return generic_gate


def _dedupe_strings(values: list) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _payload_without_generated_at(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {}
    normalized = dict(payload)
    normalized.pop("generated_at", None)
    return normalized


def _browser_release_blockers(release_scorecard: dict[str, Any]) -> list[dict[str, str]]:
    raw_codes = release_scorecard.get("browser_release_reason_codes") if isinstance(release_scorecard, dict) else []
    codes = _dedupe_strings(raw_codes if isinstance(raw_codes, list) else [])
    blockers: list[dict[str, str]] = []
    for code in codes:
        summary, repair = BROWSER_RELEASE_GUIDANCE.get(
            code,
            ("Browser QA release blocker remains open.", "Rerun browser QA with attached-session evidence and refresh release proof."),
        )
        blockers.append(
            {
                "reason_code": code,
                "summary": summary,
                "repair": repair,
            }
        )
    return blockers


def _browser_release_recommended_command(project_root: Path, *, version: str, feature: str) -> str:
    quoted_feature = f'"{feature}"' if feature else '""'
    return f"beacon qa run {quoted_feature} --project {project_root} --version {version}"


def _feature_change_paths(project_root: Path, version: str, slug: str) -> tuple[Path, Path]:
    return (
        change_docs_file(project_root, version, f"{slug}.md"),
        change_file_output(project_root, version, f"{slug}.json"),
    )


def _render_feature_change_markdown(payload: dict) -> str:
    def _section(title: str, items: list[str]) -> list[str]:
        lines = ["", f"## {title}"]
        if not items:
            lines.append("- none")
            return lines
        for item in items:
            lines.append(f"- {item}")
        return lines

    lines = [
        "# Beacon Feature Change Document",
        "",
        f"- feature: `{payload.get('feature', '')}`",
        f"- feature_slug: `{payload.get('feature_slug', '')}`",
        f"- version: `{payload.get('version', '')}`",
        f"- status: `{payload.get('status', '')}`",
        "",
        "## Scope",
        f"- {payload.get('summary') or 'No summary provided'}",
    ]
    lines.extend(_section("Added", [str(x) for x in payload.get("added", [])]))
    lines.extend(_section("Removed / Reduced", [str(x) for x in payload.get("removed", [])]))
    lines.extend(_section("Fixed", [str(x) for x in payload.get("fixed", [])]))
    lines.extend(_section("Traceability Refs", [f"`{x}`" for x in payload.get("traceability_refs", [])]))
    return "\n".join(lines) + "\n"


def _materialize_feature_change_if_missing(project_root: Path, *, version: str, payload: dict) -> None:
    slug = str(payload.get("feature_slug") or "").strip()
    if not slug:
        return
    md_path, json_path = _feature_change_paths(project_root, version, slug)
    if not json_path.exists():
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if not md_path.exists():
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(_render_feature_change_markdown(payload), encoding="utf-8")


def _feature_change_payloads(project_root: Path, version: str) -> list[dict]:
    root = machine_change_dir(project_root, version)
    items: list[dict] = []
    seen_slugs: set[str] = set()

    if root.exists():
        for path in sorted(root.glob("*.json")):
            if path.name == f"{version}.json":
                continue
            if path.name.endswith(".refreeze-transaction.json") or path.name.endswith("-reconciliation.json"):
                continue
            payload = _load_json(path)
            if not payload:
                continue
            if str(payload.get("version") or "").strip() not in {"", version}:
                continue
            slug = str(payload.get("feature_slug") or "").strip()
            if slug:
                seen_slugs.add(slug)
            items.append(payload)

    exec_root = project_root / "docs" / "beacon" / version / ".machine" / "execution"
    if exec_root.exists():
        for path in sorted(exec_root.glob("technical-implementation-*.json")):
            match = _TECHNICAL_ARCHIVE_RE.match(path.name)
            if not match:
                continue
            slug = str(match.group("slug") or "").strip()
            if not slug or slug in seen_slugs:
                continue
            payload = _load_json(path)
            if not payload:
                continue
            if str(payload.get("version") or "").strip() not in {"", version}:
                continue
            revision_cleanup = payload.get("revision_cleanup") if isinstance(payload.get("revision_cleanup"), dict) else {}
            added = [str(item).strip() for item in payload.get("additions", []) if str(item).strip()]
            removed = [
                *[str(item).strip() for item in payload.get("deletions", []) if str(item).strip()],
                *[str(item).strip() for item in revision_cleanup.get("removed_surfaces", []) if str(item).strip()],
                *[
                    str(item.get("label", "") or item.get("text", "") or item.get("id", "") or "").strip()
                    for item in (revision_cleanup.get("removed_requirement_surfaces") if isinstance(revision_cleanup.get("removed_requirement_surfaces"), list) else [])
                    if isinstance(item, dict) and str(item.get("label", "") or item.get("text", "") or item.get("id", "") or "").strip()
                ],
            ]
            fixed = [
                *[str(item).strip() for item in payload.get("modifications", []) if str(item).strip()],
                *[str(item).strip() for item in payload.get("refactors", []) if str(item).strip()],
            ]
            changed_files = [str(item).strip() for item in payload.get("changed_files", []) if str(item).strip()]
            if not added and not removed and not fixed and changed_files:
                fixed = [f"Updated `{item}`" for item in changed_files]
            items.append(
                {
                    "schema_version": "1.0",
                    "version": version,
                    "feature": str(payload.get("feature") or slug),
                    "feature_slug": slug,
                    "status": str(payload.get("status") or "completed"),
                    "summary": str(payload.get("implementation_scope_summary") or payload.get("business_goal_summary") or payload.get("summary") or "").strip(),
                    "added": added,
                    "removed": removed,
                    "fixed": fixed,
                    "traceability_refs": [
                        str(path.relative_to(project_root)),
                        f"docs/beacon/{version}/.machine/execution/technical-implementation-{slug}.json",
                        f"docs/beacon/{version}/.machine/execution/implementation-summary-{slug}.json",
                        f"docs/beacon/{version}/execution/implementation-brief-{slug}.md",
                    ],
                }
            )
            _materialize_feature_change_if_missing(project_root, version=version, payload=items[-1])
            seen_slugs.add(slug)
    return items


def _normalize_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _render_ceo_challenge_release_section(release_scorecard: dict[str, Any]) -> str:
    ceo_review = release_scorecard.get("ceo_review") if isinstance(release_scorecard.get("ceo_review"), dict) else {}
    coverage = (
        release_scorecard.get("ceo_challenge_coverage")
        if isinstance(release_scorecard.get("ceo_challenge_coverage"), dict)
        else build_ceo_challenge_coverage(ceo_review)
    )
    covered_axes = [str(item).strip() for item in (coverage.get("covered_axes") or []) if str(item).strip()]
    missing_axes = [str(item).strip() for item in (coverage.get("missing_axes") or []) if str(item).strip()]
    needs_challenge = bool(coverage.get("needs_challenge", False))
    return (
        "## CEO Challenge Coverage\n\n"
        f"- status: `{str(coverage.get('status') or 'missing')}`\n"
        f"- decision: `{str(coverage.get('decision') or 'none')}`\n"
        f"- covered_axes: `{', '.join(covered_axes) or 'none'}`\n"
        f"- missing_axes: `{', '.join(missing_axes) or 'none'}`\n"
        f"- needs_challenge: `{needs_challenge}`\n"
        f"- gap_status: `{str(coverage.get('gap_status') or 'warn')}`\n"
        f"- next_route: `{str(coverage.get('latest_next_route') or 'none')}`\n"
    )


def _feature_order_sort_key(item: dict) -> tuple[str, str, str, str]:
    return (
        str(item.get("frozen_at") or ""),
        str(item.get("reviewed_at") or ""),
        str(item.get("updated_at") or ""),
        str(item.get("feature_slug") or ""),
    )


def _analyze_feature_implementation_order(project_root: Path, *, version: str, feature_payloads: list[dict]) -> dict:
    if not feature_payloads:
        return {
            "status": "empty",
            "feature_count": 0,
            "ordered_feature_slugs": [],
            "waves": [],
        }

    host = load_implementation_delivery_host(project_root, version=version)
    host_features = host.get("features") if isinstance(host.get("features"), list) else []
    host_by_slug = {
        str(item.get("feature_slug") or "").strip(): item
        for item in host_features
        if isinstance(item, dict) and str(item.get("feature_slug") or "").strip()
    }

    enriched: list[dict] = []
    for payload in feature_payloads:
        feature = str(payload.get("feature") or "").strip()
        slug = str(payload.get("feature_slug") or "").strip()
        if not slug:
            continue
        host_entry = host_by_slug.get(slug) if isinstance(host_by_slug.get(slug), dict) else {}
        revision = load_revision_state(project_root, version=version, feature=feature or slug, create_if_missing=False)
        contract = load_technical_review_contract(project_root, version=version, feature=feature or slug)
        plan_progress = load_implementation_plan_progress(project_root, version=version, feature=feature or slug)
        direct_services = (
            _normalize_string_list(host_entry.get("direct_delivery_services"))
            or _normalize_string_list(host_entry.get("writable_services"))
            or
            _normalize_string_list(contract.get("direct_delivery_services"))
            or _normalize_string_list(contract.get("service_directories"))
            or _normalize_string_list(contract.get("writable_services"))
        )
        writable_services = (
            _normalize_string_list(host_entry.get("writable_services"))
            or _normalize_string_list(contract.get("writable_services"))
            or list(direct_services)
        )
        explicit_deps = (
            _normalize_string_list(payload.get("depends_on_features"))
            or _normalize_string_list(host_entry.get("depends_on_features"))
        )
        enriched.append(
            {
                "feature": feature or slug,
                "feature_slug": slug,
                "summary": str(payload.get("summary") or "").strip(),
                "direct_delivery_services": direct_services,
                "writable_services": writable_services,
                "depends_on_features": explicit_deps,
                "revision_id": str(revision.get("revision_id") or ""),
                "frozen_at": str(revision.get("frozen_at") or host_entry.get("updated_at") or ""),
                "reviewed_at": str(contract.get("reviewed_at") or host_entry.get("updated_at") or ""),
                "updated_at": str(plan_progress.get("updated_at") or host_entry.get("updated_at") or payload.get("updated_at") or ""),
                "plan_status": str(plan_progress.get("status") or ""),
                "baseline_ref": str(host_entry.get("baseline_ref") or ""),
            }
        )

    ordered_inputs = sorted(enriched, key=_feature_order_sort_key)
    computed: dict[str, dict] = {}
    ordered_slugs: list[str] = []
    for item in ordered_inputs:
        slug = str(item.get("feature_slug") or "")
        explicit_deps = [dep for dep in _normalize_string_list(item.get("depends_on_features")) if dep in computed]
        conflict_deps: list[str] = []
        item_services = set(_normalize_string_list(item.get("writable_services")) or _normalize_string_list(item.get("direct_delivery_services")))
        if not explicit_deps and item_services:
            for prior_slug in reversed(ordered_slugs):
                prior = computed.get(prior_slug) or {}
                prior_services = set(
                    _normalize_string_list(prior.get("writable_services")) or _normalize_string_list(prior.get("direct_delivery_services"))
                )
                if item_services.intersection(prior_services):
                    conflict_deps = [prior_slug]
                    break
        deps = explicit_deps or conflict_deps
        wave = 1
        if deps:
            wave = max(int((computed.get(dep) or {}).get("wave") or 1) for dep in deps) + 1
        reason = "parallel_no_conflict"
        if explicit_deps:
            reason = "explicit_feature_dependency"
        elif conflict_deps:
            reason = "shared_delivery_service_conflict"
        computed[slug] = {
            **item,
            "depends_on_features": deps,
            "wave": wave,
            "parallelizable": not deps,
            "reason_code": reason,
        }
        ordered_slugs.append(slug)

    waves_map: dict[int, list[dict]] = {}
    for slug in ordered_slugs:
        item = computed[slug]
        waves_map.setdefault(int(item["wave"]), []).append(
            {
                "feature": item["feature"],
                "feature_slug": slug,
                "depends_on_features": item["depends_on_features"],
                "direct_delivery_services": item["direct_delivery_services"],
                "writable_services": item["writable_services"],
                "parallelizable": item["parallelizable"],
                "reason_code": item["reason_code"],
            }
        )
    waves = [
        {
            "wave": wave,
            "parallelizable": len(items) > 1 and all(bool(item.get("parallelizable")) for item in items),
            "features": items,
        }
        for wave, items in sorted(waves_map.items())
    ]
    return {
        "status": "analyzed",
        "feature_count": len(ordered_slugs),
        "ordered_feature_slugs": ordered_slugs,
        "waves": waves,
    }


def _build_version_change_payload(project_root: Path, *, version: str) -> dict:
    project_root = project_root.expanduser().resolve()
    feature_payloads = _feature_change_payloads(project_root, version)
    features = []
    added: list[str] = []
    removed: list[str] = []
    fixed: list[str] = []
    traceability_refs: list[str] = []

    for payload in feature_payloads:
        feature = str(payload.get("feature") or "").strip()
        slug = str(payload.get("feature_slug") or "").strip()
        features.append(
            {
                "feature": feature,
                "feature_slug": slug,
                "summary": str(payload.get("summary") or "").strip(),
                "status": str(payload.get("status") or "").strip(),
            }
        )
        added.extend([f"[{slug}] {item}" for item in payload.get("added", []) if str(item).strip()])
        removed.extend([f"[{slug}] {item}" for item in payload.get("removed", []) if str(item).strip()])
        fixed.extend([f"[{slug}] {item}" for item in payload.get("fixed", []) if str(item).strip()])
        traceability_refs.extend(
            [str(item).strip() for item in payload.get("traceability_refs", []) if str(item).strip()]
        )
        traceability_refs.append(str(change_file_output(project_root, version, f"{slug}.json").relative_to(project_root)))
        traceability_refs.append(str(change_docs_file(project_root, version, f"{slug}.md").relative_to(project_root)))
    implementation_order = _analyze_feature_implementation_order(
        project_root,
        version=version,
        feature_payloads=feature_payloads,
    )

    return {
        "schema_version": "1.0",
        "version": version,
        "status": "generated",
        "artifact_role": "version_aggregate_projection",
        "projection_role": {
            "artifact_role": "version_aggregate_projection",
            "truth_source": False,
            "gate_source": False,
            "lifecycle_stage": False,
            "release_publish_action": False,
        },
        "truth_authority": False,
        "lifecycle_stage": False,
        "release_publish_action": False,
        "feature_count": len(features),
        "features": features,
        "implementation_order": implementation_order,
        "added": _dedupe_strings(added),
        "removed": _dedupe_strings(removed),
        "fixed": _dedupe_strings(fixed),
        "traceability_refs": _dedupe_strings(traceability_refs),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _stabilize_version_change_payload(project_root: Path, *, version: str, payload: dict) -> dict:
    existing_payload = _load_json(change_file_output(project_root, version, f"{version}.json"))
    existing_generated_at = str(existing_payload.get("generated_at") or "").strip()
    if (
        existing_generated_at
        and _payload_without_generated_at(existing_payload) == _payload_without_generated_at(payload)
    ):
        stabilized = dict(payload)
        stabilized["generated_at"] = existing_generated_at
        return stabilized
    return payload


def _render_version_change_markdown(payload: dict) -> str:
    def _section(title: str, items: list[str]) -> list[str]:
        lines = ["", f"## {title}"]
        if not items:
            lines.append("- none")
            return lines
        for item in items:
            lines.append(f"- {item}")
        return lines

    features = payload.get("features") if isinstance(payload.get("features"), list) else []
    lines = [
        f"# Beacon {payload.get('version')} Change Document",
        "",
        f"**Version**: `{payload.get('version')}`",
        f"**Status**: `{payload.get('status')}`",
        "**Artifact Role**: `version aggregate projection / release-facing read model`",
        "**Truth Source**: `false`",
        f"**Generated**: {payload.get('generated_at')}",
        "",
        "## Scope",
        f"- feature packages included: {len(features)}",
    ]
    if features:
        lines.append("")
        lines.append("## Feature Packages")
        for item in features:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("feature_slug") or "").strip()
            summary = str(item.get("summary") or "").strip()
            lines.append(f"- `{slug}`: {summary or 'No summary provided'}")
    implementation_order = payload.get("implementation_order") if isinstance(payload.get("implementation_order"), dict) else {}
    waves = implementation_order.get("waves") if isinstance(implementation_order.get("waves"), list) else []
    lines.append("")
    lines.append("## Implementation Order")
    if not waves:
        lines.append("- none")
    else:
        for wave in waves:
            if not isinstance(wave, dict):
                continue
            wave_no = int(wave.get("wave") or 0)
            parallel = bool(wave.get("parallelizable"))
            lines.append(f"- wave {wave_no}: `{'parallel' if parallel else 'serial'}`")
            for item in wave.get("features", []):
                if not isinstance(item, dict):
                    continue
                slug = str(item.get("feature_slug") or "").strip()
                deps = _normalize_string_list(item.get("depends_on_features"))
                services = _normalize_string_list(item.get("writable_services")) or _normalize_string_list(item.get("direct_delivery_services"))
                reason = str(item.get("reason_code") or "").strip()
                suffix_parts: list[str] = []
                if deps:
                    suffix_parts.append(f"depends_on={', '.join(deps)}")
                if services:
                    suffix_parts.append(f"services={', '.join(services)}")
                if reason:
                    suffix_parts.append(f"reason={reason}")
                suffix = f" ({'; '.join(suffix_parts)})" if suffix_parts else ""
                lines.append(f"  - `{slug}`{suffix}")

    lines.extend(_section("Added", [str(x) for x in payload.get("added", [])]))
    lines.extend(_section("Removed / Reduced", [str(x) for x in payload.get("removed", [])]))
    lines.extend(_section("Fixed", [str(x) for x in payload.get("fixed", [])]))
    lines.extend(_section("Traceability Refs", [f"`{x}`" for x in payload.get("traceability_refs", [])]))
    return "\n".join(lines) + "\n"


@app.command()
def create(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create release checklist"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    version_change_payload = _build_version_change_payload(project_root, version=resolved_version)
    version_change_payload = _stabilize_version_change_payload(
        project_root,
        version=resolved_version,
        payload=version_change_payload,
    )
    version_change_md = change_docs_file(project_root, resolved_version, f"{resolved_version}.md")
    version_change_json = change_file_output(project_root, resolved_version, f"{resolved_version}.json")
    version_change_md.parent.mkdir(parents=True, exist_ok=True)
    version_change_json.parent.mkdir(parents=True, exist_ok=True)
    version_change_md.write_text(_render_version_change_markdown(version_change_payload), encoding="utf-8")
    version_change_json.write_text(json.dumps(version_change_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    version_change_md_ref = str(version_change_md.relative_to(project_root))
    version_change_json_ref = str(version_change_json.relative_to(project_root))
    release_scorecard = build_release_scorecard(project_root, version=resolved_version)
    ceo_challenge_section = _render_ceo_challenge_release_section(release_scorecard)

    release_content = f"""# Release Checklist: {resolved_version}

**Version**: {resolved_version}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status**: Pending

---

## Pre-Release Checks

- [ ] All tests passing
- [ ] Code coverage >= 80%
- [ ] No critical bugs open
- [ ] Security scan completed
- [ ] Performance benchmarks passed
- [ ] Documentation updated

## Build

- [ ] Build successful
- [ ] No linting errors
- [ ] Type checks passing

## Deployment

- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Database migrations tested

## Release

- [ ] Production deployment
- [ ] Health checks passing
- [ ] Rollback plan ready

## Change Documents

- [x] Version change document generated: `{version_change_md_ref}`
- [x] Version change machine payload generated: `{version_change_json_ref}`
- [ ] Release reviewer confirmed included feature packages match intended scope

---

{ceo_challenge_section}

---

## Notes

"""
    output_paths = (
        [Path(output)]
        if output
        else [
            release_checklist_file(project_root, resolved_version),
        ]
    )
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(release_content, encoding="utf-8")
    output_path = output_paths[0]

    rel = str(output_path.relative_to(project_root))
    evidence_refs = [rel, version_change_md_ref, version_change_json_ref]
    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.create] release checklist created for {resolved_version}",
        source_session_id=f"release:{resolved_version}",
        source="release.create",
        evidence_ref=evidence_refs,
        confidence=0.8,
        tags=["release", "workflow-loop"],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{resolved_version}",
        stage="release",
        event="release_decision_recorded",
        source="release.create",
        evidence_ref=evidence_refs,
        details={"action": "create", "version": resolved_version},
    )

    typer.echo(f"✓ Release checklist created: {output_path}")


@app.command()
def check(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Check release conditions"""
    project_root = (Path(project) if project else Path.cwd()).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    if metadata_machine_path(project_root).exists():
        metadata_verdict = verify_project_metadata(project_root, version=resolved_version)
        if str(metadata_verdict.get("status") or "").lower() == "fail":
            failing_checks = [
                item for item in metadata_verdict.get("checks", [])
                if isinstance(item, dict) and str(item.get("status") or "").lower() == "fail"
            ]
            payload = _with_release_surface({
                "schema_version": "1.0",
                "version": resolved_version,
                "status": "blocked",
                "reason_code": "project_metadata_contract_blocked",
                "project_metadata_verification": metadata_verdict,
                "recommended_command": f"beacon doctor metadata verify --project-root {project_root} --version {resolved_version}",
            }, blocked=True)
            if json_output:
                typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                typer.echo("Beacon release blocked: project metadata contract blocked")
                for item in failing_checks:
                    typer.echo(
                        f"- {item.get('name')}: {json.dumps(item.get('details', {}), ensure_ascii=False, sort_keys=True)}"
                    )
            raise typer.Exit(code=1)
    requirement_package_gate = build_requirement_package_gate(
        project_root,
        version=resolved_version,
        feature="",
        strict=True,
    )
    requirement_evidence_refs = [
        "docs/beacon/"
        f"{resolved_version}/.machine/requirement/feature-package-validation.json",
    ]
    for package in requirement_package_gate.get("packages", []) if isinstance(requirement_package_gate.get("packages"), list) else []:
        if not isinstance(package, dict):
            continue
        feature_slug_value = str(package.get("slug") or package.get("feature_slug") or "").strip()
        if feature_slug_value:
            requirement_evidence_refs.append(
                "docs/beacon/"
                f"{resolved_version}/.machine/requirement/{feature_slug_value}.freeze-state.json"
            )
    refresh_evidence_manifest(
        project_root,
        refs=requirement_evidence_refs,
        version=resolved_version,
    )
    requirement_package_gate_blocked = str(requirement_package_gate.get("status") or "").lower() == "blocked"
    if requirement_package_gate_blocked and json_output:
        payload = _with_release_surface({
            "schema_version": "1.0",
            "version": resolved_version,
            "status": "blocked",
            "reason_code": str(requirement_package_gate.get("reason_code") or "requirement_package_contract_blocked"),
            "requirement_package_gate": requirement_package_gate,
            "recommended_command": str(
                requirement_package_gate.get("recommended_command")
                or f"beacon doctor verify-materials --project-root {project_root} --version {resolved_version} --strict"
            ),
        }, blocked=True)
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo("Beacon release blocked: requirement package contract blocked")
        raise typer.Exit(code=2)
    release_scorecard = build_release_scorecard(project_root, version=resolved_version)
    change_documents = release_scorecard.get("change_documents") if isinstance(release_scorecard.get("change_documents"), dict) else {}
    prompt_boundary = release_scorecard.get("prompt_boundary") if isinstance(release_scorecard.get("prompt_boundary"), dict) else {}
    browser_release_blockers = _browser_release_blockers(release_scorecard)
    version_surface_governance = (
        release_scorecard.get("version_surface_governance")
        if isinstance(release_scorecard.get("version_surface_governance"), dict)
        else {}
    )
    feature_qa_scorecard = (
        release_scorecard.get("feature_qa_scorecard")
        if isinstance(release_scorecard.get("feature_qa_scorecard"), dict)
        else {}
    )
    enforce_change_documents = project_release_feature_enabled(
        project_root,
        "v1.3.1",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    enforce_release_scorecard = project_release_feature_enabled(
        project_root,
        "v1.3.6",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    enforce_prompt_boundary = project_release_feature_enabled(
        project_root,
        "v1.3.7",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    enforce_acceptance_transaction = project_release_feature_enabled(
        project_root,
        "v1.3.9",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    authoritative_release_ready = bool(release_scorecard.get("release_ready", False))
    scorecard_authoritative = authoritative_release_ready and bool(
        ((release_scorecard.get("qa") or {}) if isinstance(release_scorecard.get("qa"), dict) else {}).get("feature")
    )
    authoritative_qa_ready = bool(
        ((release_scorecard.get("qa") or {}) if isinstance(release_scorecard.get("qa"), dict) else {}).get("release_ready", False)
    )

    auto_test_path = project_root / ".beacon" / "auto-test-status.json"
    gate_report_path = _select_gate_report_path(project_root, version=resolved_version)
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    coverage_summary_path = project_root / ".beacon" / "coverage-summary.json"

    checks: list[tuple[str, str, str]] = []
    evidence_refs: list[str] = []

    if requirement_package_gate_blocked:
        checks.append(
            (
                "requirement package contract",
                "fail",
                str(requirement_package_gate.get("reason_code") or "requirement_package_contract_blocked"),
            )
        )

    auto_test_ok = False
    auto_test_status = "missing"
    auto_test_run_id = ""
    auto_test_version = ""
    if auto_test_path.exists():
        try:
            auto_test_payload = json.loads(auto_test_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            auto_test_payload = {}
        auto_test_status = str(auto_test_payload.get("status", "")).strip().lower() or "unknown"
        auto_test_ok = auto_test_status == "passed"
        auto_test_run_id = _extract_run_id(auto_test_payload)
        auto_test_version = _extract_version(auto_test_payload)
        evidence_refs.append(str(auto_test_path.relative_to(project_root)))
    checks.append(("auto-test status passed", "pass" if auto_test_ok else "fail", f"status={auto_test_status}"))
    checks.append(
        (
            "auto-test version matches release version",
            "pass" if bool(auto_test_version) and auto_test_version == resolved_version else "fail",
            f"artifact_version={auto_test_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
        (
            "auto-test run_id present",
            "pass" if bool(auto_test_run_id) else "fail",
            f"run_id={auto_test_run_id or 'missing'}",
        )
    )

    scorecard_gate = release_scorecard.get("gate") if isinstance(release_scorecard.get("gate"), dict) else {}
    qa_summary = release_scorecard.get("qa") if isinstance(release_scorecard.get("qa"), dict) else {}
    authoritative_feature = str(qa_summary.get("feature") or "").strip()
    gate_ok = False
    gate_status = "missing"
    gate_coverage_full: Optional[bool] = None
    gate_run_id = ""
    gate_version = ""
    if gate_report_path.exists():
        try:
            gate_payload = json.loads(gate_report_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            gate_payload = {}
        gate_status = str(gate_payload.get("status", "")).strip()
        gate_ok = gate_status.lower() == "pass"
        gate_run_id = _extract_run_id(gate_payload)
        gate_version = _extract_version(gate_payload)
        coverage_payload = gate_payload.get("coverage")
        if isinstance(coverage_payload, dict) and "full_coverage" in coverage_payload:
            gate_coverage_full = bool(coverage_payload.get("full_coverage"))
        evidence_refs.append(str(gate_report_path.relative_to(project_root)))
    if scorecard_gate:
        gate_status = str(scorecard_gate.get("status") or gate_status or "unknown")
        gate_ok = gate_status.lower() == "pass"
        if scorecard_gate.get("run_id"):
            gate_run_id = str(scorecard_gate.get("run_id") or gate_run_id)
        if scorecard_gate.get("artifact_version"):
            gate_version = str(scorecard_gate.get("artifact_version") or gate_version)
    checks.append(("gate report pass", "pass" if gate_ok else "fail", f"status={gate_status or 'unknown'}"))
    checks.append(
        (
            "gate report version matches release version",
            "pass" if bool(gate_version) and gate_version == resolved_version else "fail",
            f"artifact_version={gate_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
            ( 
                "gate report run_id matches auto-test",
                "pass" if (
                    bool(gate_run_id)
                    and bool(auto_test_run_id)
                    and (
                        gate_run_id == auto_test_run_id
                        or ((scorecard_authoritative or authoritative_qa_ready) and gate_ok and auto_test_ok)
                    )
                ) else "fail",
                (
                    f"gate_run_id={gate_run_id or 'missing'}, auto_test_run_id={auto_test_run_id or 'missing'}"
                    + (
                    ", authoritative_release_scorecard=true"
                    if (scorecard_authoritative or authoritative_qa_ready) and gate_ok and auto_test_ok
                    else ""
                )
            ),
        )
    )

    manifest_ok = False
    manifest_entries = 0
    manifest_run_id = ""
    manifest_version = ""
    if manifest_path.exists():
        try:
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            manifest_payload = {}
        entries = manifest_payload.get("entries")
        if isinstance(entries, list):
            manifest_entries = len(entries)
            manifest_ok = manifest_entries > 0
        manifest_run_id = _extract_run_id(manifest_payload)
        manifest_version = _extract_version(manifest_payload)
        evidence_refs.append(str(manifest_path.relative_to(project_root)))
    checks.append(("evidence manifest present", "pass" if manifest_ok else "fail", f"entries={manifest_entries}"))
    checks.append(
        (
            "evidence manifest version matches release version",
            "pass" if bool(manifest_version) and manifest_version == resolved_version else "fail",
            f"artifact_version={manifest_version or 'missing'}, expected={resolved_version}",
        )
    )
    expected_run_id = auto_test_run_id or gate_run_id
    checks.append(
            (
                "evidence manifest run_id matches test artifacts",
                "pass" if (
                    bool(manifest_run_id)
                    and bool(expected_run_id)
                    and (
                    manifest_run_id == expected_run_id
                    or (
                        scorecard_authoritative
                        and bool(authoritative_feature)
                        and manifest_ok
                    )
                )
                ) else "fail",
                (
                    f"manifest_run_id={manifest_run_id or 'missing'}, expected={expected_run_id or 'missing'}"
                    + (
                    ", authoritative_release_scorecard=true"
                    if scorecard_authoritative and bool(authoritative_feature) and manifest_ok
                    else ""
                )
            ),
        )
    )

    coverage_ok = False
    coverage_detail = "missing"
    coverage_version = ""
    coverage_run_id = ""
    if coverage_summary_path.exists():
        try:
            coverage_payload = json.loads(coverage_summary_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            coverage_payload = {}
        coverage_version = _extract_version(coverage_payload)
        coverage_run_id = _extract_run_id(coverage_payload)
        rate = coverage_payload.get("coverage_rate")
        if isinstance(rate, (int, float)):
            coverage_ok = float(rate) >= 0.8
            coverage_detail = f"coverage_rate={float(rate):.4f}"
        elif "full_coverage" in coverage_payload:
            coverage_ok = bool(coverage_payload.get("full_coverage"))
            coverage_detail = f"full_coverage={coverage_ok}"
        evidence_refs.append(str(coverage_summary_path.relative_to(project_root)))
    elif gate_coverage_full is not None:
        coverage_ok = bool(gate_coverage_full)
        coverage_detail = f"gate_report.coverage.full_coverage={coverage_ok}"
    if not coverage_ok and (scorecard_authoritative or authoritative_qa_ready):
        coverage_current = (
            feature_qa_scorecard.get("coverage_current")
            if isinstance(feature_qa_scorecard.get("coverage_current"), dict)
            else {}
        )
        executed = int(coverage_current.get("executed_scenarios") or 0)
        required = int(coverage_current.get("required_scenarios") or 0)
        coverage_rate = coverage_current.get("coverage_rate")
        if required > 0 and executed >= required:
            coverage_ok = True
            coverage_detail = (
                f"feature_scorecard.coverage_current={executed}/{required} "
                f"({coverage_rate if coverage_rate is not None else 'n/a'}), authoritative_release_scorecard=true"
            )
    checks.append(("coverage artifact ready", "pass" if coverage_ok else "fail", coverage_detail))
    if coverage_summary_path.exists():
        checks.append(
            (
                "coverage summary version matches release version",
                "pass" if bool(coverage_version) and coverage_version == resolved_version else "fail",
                f"artifact_version={coverage_version or 'missing'}, expected={resolved_version}",
            )
        )
        checks.append(
            (
                "coverage summary run_id matches test artifacts",
                "pass" if (
                    bool(coverage_run_id)
                    and bool(expected_run_id)
                    and (
                        coverage_run_id == expected_run_id
                        or (
                            scorecard_authoritative
                            and bool(authoritative_feature)
                            and coverage_ok
                        )
                    )
                ) else "fail",
                (
                    f"coverage_run_id={coverage_run_id or 'missing'}, expected={expected_run_id or 'missing'}"
                    + (
                        ", authoritative_release_scorecard=true"
                        if scorecard_authoritative and bool(authoritative_feature) and coverage_ok
                        else ""
                    )
                ),
            )
        )

    if _parse_semver_tuple(resolved_version) >= (1, 3, 5):
        try:
            runtime_tx_contract = runtime_projection_transaction_contract(
                project_root=project_root,
                docs_version=resolved_version,
                feature=None,
            )
        except Exception:  # noqa: BLE001
            runtime_tx_contract = {
                "status": "warn",
                "reason_code": "runtime_projection_drift",
            }
        runtime_tx_status = str(runtime_tx_contract.get("status") or "").lower()
        runtime_tx_ok = runtime_tx_status != "fail"
        checks.append(
            (
                "runtime projection transaction contract",
                "pass" if runtime_tx_ok else "fail",
                f"status={runtime_tx_contract.get('status') or 'unknown'}, reason={runtime_tx_contract.get('reason_code') or '-'}",
            )
        )

    if enforce_acceptance_transaction:
        acceptance = release_scorecard.get("acceptance") if isinstance(release_scorecard.get("acceptance"), dict) else {}
        qa_summary = release_scorecard.get("qa") if isinstance(release_scorecard.get("qa"), dict) else {}
        acceptance_feature = str(acceptance.get("feature") or qa_summary.get("feature") or "").strip()
        acceptance_tx_contract = acceptance_projection_transaction_contract(
            project_root,
            version=resolved_version,
            feature=acceptance_feature,
        ) if acceptance_feature else {
            "status": "warn",
            "reason_code": "acceptance_feature_missing",
        }
        acceptance_tx_ok = str(acceptance_tx_contract.get("status") or "warn").lower() == "pass"
        checks.append(
            (
                "acceptance projection transaction contract",
                "pass" if acceptance_tx_ok else "fail",
                f"status={acceptance_tx_contract.get('status') or 'unknown'}, reason={acceptance_tx_contract.get('reason_code') or '-'}",
            )
        )

    if metadata_machine_path(project_root).exists():
        metadata_verdict = verify_project_metadata(project_root, version=resolved_version)
        metadata_ok = str(metadata_verdict.get("status") or "").lower() != "fail"
        failing_checks = [
            f"{item.get('name')}={item.get('details', {})}"
            for item in metadata_verdict.get("checks", [])
            if isinstance(item, dict) and str(item.get("status") or "").lower() == "fail"
        ]
        checks.append(
            (
                "project metadata contract",
                "pass" if metadata_ok else "fail",
                "; ".join(failing_checks) if failing_checks else f"status={metadata_verdict.get('status') or 'unknown'}",
            )
        )

    if enforce_change_documents:
        change_md_ref = str(change_documents.get("markdown_path") or "")
        change_json_ref = str(change_documents.get("json_path") or "")
        projection_reason = str(change_documents.get("reason_code") or "-")
        projection_repairs = [
            str(item).strip()
            for item in (change_documents.get("repair_commands") if isinstance(change_documents.get("repair_commands"), list) else [])
            if str(item).strip()
        ]
        projection_repair = projection_repairs[0] if projection_repairs else ""
        if change_md_ref:
            evidence_refs.append(change_md_ref)
        if change_json_ref:
            evidence_refs.append(change_json_ref)
        checks.append(
            (
                "version change markdown exists",
                "pass" if bool(change_documents.get("markdown_exists", False)) else "fail",
                f"path={change_md_ref or 'missing'}",
            )
        )
        checks.append(
            (
                "version change payload exists",
                "pass" if bool(change_documents.get("json_exists", False)) else "fail",
                f"path={change_json_ref or 'missing'}",
            )
        )
        checks.append(
            (
                "version change payload matches release version",
                "pass" if bool(change_documents.get("version_match", False)) else "fail",
                f"feature_count={change_documents.get('feature_count', 0)}",
            )
        )
        checks.append(
            (
                "version change document includes current feature",
                "pass" if bool(change_documents.get("includes_current_feature", False)) else "fail",
                (
                    f"current_feature={change_documents.get('current_feature_slug') or 'none'}, "
                    f"reason={projection_reason}, repair={projection_repair or 'none'}"
                ),
            )
        )

    if enforce_release_scorecard:
        semantic = release_scorecard.get("semantic") if isinstance(release_scorecard.get("semantic"), dict) else {}
        semantic_status = str(semantic.get("status") or "unknown")
        semantic_reason = str(semantic.get("reason_code") or "")
        checks.append(
            (
                "release scorecard ready",
                "pass" if bool(release_scorecard.get("release_ready", False)) else "fail",
                f"feature={release_scorecard.get('qa', {}).get('feature') or 'none'}, semantic_reason={semantic_reason or '-'}",
            )
        )
        if semantic:
            checks.append(
                (
                    "semantic contract ready",
                    "pass" if semantic_status == "pass" else "fail",
                    f"status={semantic_status}, reason={semantic_reason or '-'}",
                )
            )

        ceo_challenge_coverage = (
            release_scorecard.get("ceo_challenge_coverage")
            if isinstance(release_scorecard.get("ceo_challenge_coverage"), dict)
            else {}
        )
        checks.append(
            (
                "ceo challenge coverage current",
                "warn" if bool(ceo_challenge_coverage.get("needs_challenge", False)) else "pass",
                (
                    f"status={ceo_challenge_coverage.get('status') or 'missing'}, "
                    f"missing_axes={','.join(str(item) for item in (ceo_challenge_coverage.get('missing_axes') or [])) or 'none'}, "
                    f"decision={ceo_challenge_coverage.get('decision') or 'none'}"
                ),
            )
        )

    if bool(version_surface_governance.get("configured", False)):
        repair_commands = version_surface_repair_commands(project_root)
        checks.append(
            (
                "version surface governance pass",
                "pass" if not bool(version_surface_governance.get("blocked", False)) else "fail",
                (
                    f"status={version_surface_governance.get('status') or 'unknown'}, "
                    f"reason={version_surface_governance.get('reason_code') or '-'}, "
                    f"manifest_path={version_surface_governance.get('manifest_path') or 'missing'}, "
                    f"repair={repair_commands[0]}, verify={repair_commands[1]}"
                ),
            )
        )

    if enforce_prompt_boundary:
        prompt_boundary_status = str(prompt_boundary.get("status") or "missing")
        prompt_boundary_reason = str(prompt_boundary.get("reason_code") or "")
        prompt_boundary_classification = str(prompt_boundary.get("classification") or "")
        prompt_boundary_surface = str(prompt_boundary.get("surface") or "")
        checks.append(
            (
                "implement prompt boundary verdict pass",
                "pass"
                if prompt_boundary_status.lower() == "pass" and not bool(prompt_boundary.get("blocked", False))
                else "fail",
                (
                    f"status={prompt_boundary_status}, "
                    f"classification={prompt_boundary_classification or '-'}, "
                    f"surface={prompt_boundary_surface or '-'}, "
                    f"reason={prompt_boundary_reason or '-'}"
                ),
            )
        )

    all_passed = True
    failed_checks: list[str] = []
    warning_checks: list[str] = []
    check_records: list[dict[str, Any]] = []
    for check_name, status_label, detail in checks:
        passed = status_label != "fail"
        check_records.append(
            {
                "name": check_name,
                "status": status_label,
                "passed": bool(passed),
                "detail": detail,
            }
        )
        if status_label == "warn":
            warning_checks.append(check_name)
        if status_label == "fail":
            all_passed = False
            failed_checks.append(check_name)

    recommended_command = ""
    if browser_release_blockers:
        recommended_command = _browser_release_recommended_command(
            project_root,
            version=resolved_version,
            feature=authoritative_feature,
        )
    elif enforce_change_documents and any(
        name.startswith("version change ") for name in failed_checks
    ):
        repair_commands = change_documents.get("repair_commands") if isinstance(change_documents.get("repair_commands"), list) else []
        recommended_command = next((str(item).strip() for item in repair_commands if str(item).strip()), "")

    status = "pass" if all_passed else "blocked"
    lifecycle_hook_advisory = (
        build_lifecycle_hook_advisory(
            project_root,
            version=resolved_version,
            feature=authoritative_feature,
            hook_code="post_release",
            boundary_stage="release",
        )
        if all_passed
        else {
            "schema_version": "1.0",
            "status": "not_applicable",
            "blocked": False,
            "hook_code": "post_release",
            "boundary_stage": "release",
            "version": resolved_version,
            "feature": authoritative_feature,
            "hook_count": 0,
            "hooks": [],
            "side_effect_executed": False,
            "truth_authority": False,
            "runtime_evidence_only": True,
            "verdict_authority": "none",
            "support_evidence_only": True,
        }
    )
    payload = _with_release_surface({
        "version": resolved_version,
        "runtime_version": resolved_runtime,
        "project_root": str(project_root),
        "status": status,
        "release_ready": all_passed,
        "failed_checks": failed_checks,
        "warning_checks": warning_checks,
        "checks": check_records,
        "browser_release_blockers": browser_release_blockers,
        "recommended_command": recommended_command,
        "lifecycle_hook_advisory": lifecycle_hook_advisory,
    }, blocked=status == "blocked", recommended_command=recommended_command)

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"Checking release conditions for {resolved_version}")
        typer.echo("=" * 40)
        for record in check_records:
            marker = "✓ PASS" if record["status"] == "pass" else "⚠ WARN" if record["status"] == "warn" else "✗ FAIL"
            typer.echo(f"{marker}: {record['name']} ({record['detail']})")
        if all_passed:
            typer.echo("\n✓ Release conditions met")
            if warning_checks:
                typer.echo(f"Warnings: {', '.join(warning_checks)}")
            if lifecycle_hook_advisory.get("recommended_command"):
                typer.echo("\nPost-release hook advisory:")
                for item in lifecycle_hook_advisory.get("hooks", []):
                    if not isinstance(item, dict):
                        continue
                    typer.echo(
                        f"- {item.get('hook_id')}: plan={item.get('plan_status')} "
                        f"policy={item.get('trigger_policy')} support_evidence_only=true"
                    )
                typer.echo(f"Recommended command: {lifecycle_hook_advisory.get('recommended_command')}")
        else:
            typer.echo("\n✗ Some checks failed")
            if browser_release_blockers:
                typer.echo("\nBrowser blockers:")
                for item in browser_release_blockers:
                    typer.echo(f"- {item['reason_code']}: {item['summary']}")
                    typer.echo(f"  repair: {item['repair']}")
                if recommended_command:
                    typer.echo(f"Recommended command: {recommended_command}")
            elif recommended_command:
                typer.echo(f"Recommended command: {recommended_command}")

    append_memory_entry(
        project_root=project_root,
        mem_type="decision",
        text=f"[release.check] version={resolved_version} status={status}",
        source_session_id=f"release:{resolved_version}",
        source="release.check",
        evidence_ref=sorted(set(evidence_refs)),
        confidence=0.75,
        tags=["release", "gate", status],
    )
    append_lifecycle_event(
        project_root,
        run_id=f"release:{resolved_version}",
        stage="release",
        event="release_decision_recorded",
        source="release.check",
        evidence_ref=sorted(set(evidence_refs)),
        details={
            "action": "check",
            "version": resolved_version,
            "status": status,
            "failed_checks": failed_checks,
        },
    )
    if not all_passed:
        raise typer.Exit(1)


@app.command()
def scorecard(
    version: str = typer.Argument(..., help="Release version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show a release scorecard combining gate, QA, exhaustiveness, and learning signals."""
    project_root = Path(project) if project else Path.cwd()
    payload = build_release_scorecard(project_root, version=version)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo(f"Release Scorecard: {payload['version']}")
    typer.echo("=" * 40)
    typer.echo(f"Release ready: {payload['release_ready']}")
    typer.echo(f"Gate: {payload['gate']['status']} (blocked={payload['gate']['blocked_count']})")
    typer.echo(
        f"QA: {payload['qa']['status']} evidence_done={payload['qa']['evidence_done']} mode={payload['qa']['execution_mode']}"
    )
    if payload["qa"].get("project_profile_gate_status"):
        typer.echo(
            f"Project QA Gate: status={payload['qa'].get('project_profile_gate_status')} profile={payload['qa'].get('project_profile_id') or '-'}"
        )
    exhaustiveness = payload.get("exhaustiveness", {})
    if isinstance(exhaustiveness, dict) and exhaustiveness:
        typer.echo(
            f"Exhaustiveness: status={exhaustiveness.get('status')} score={exhaustiveness.get('score')} threshold={exhaustiveness.get('threshold')}"
        )
        typer.echo(f"Missing axes: {', '.join(exhaustiveness.get('missing_axes', [])) or '-'}")
    feature_scorecard = payload.get("feature_qa_scorecard", {})
    if isinstance(feature_scorecard, dict) and feature_scorecard:
        typer.echo(
            "Feature QA Scorecard: "
            f"confidence_min={feature_scorecard.get('release_confidence_min')} "
            f"review_required={feature_scorecard.get('review_required_count')} "
            f"needs_replay={feature_scorecard.get('needs_replay_count')}"
        )
        typer.echo(
            f"Continue decision: {feature_scorecard.get('continue_decision', '')} backfill_required={feature_scorecard.get('test_case_backfill_required', False)}"
        )
    browser_release_blockers = payload.get("browser_release_reason_codes") if isinstance(payload.get("browser_release_reason_codes"), list) else []
    if browser_release_blockers:
        typer.echo(f"Browser release blockers: {', '.join(str(item) for item in browser_release_blockers if str(item).strip())}")
        for item in _browser_release_blockers(payload):
            typer.echo(f"- {item['reason_code']}: {item['summary']}")
            typer.echo(f"  repair: {item['repair']}")
        qa_feature = str(payload.get("qa", {}).get("feature") or "") if isinstance(payload.get("qa"), dict) else ""
        typer.echo(
            f"Recommended command: {_browser_release_recommended_command(project_root, version=str(payload.get('version') or version), feature=qa_feature)}"
        )
    prototype_projection = payload.get("prototype_projection", {})
    if isinstance(prototype_projection, dict) and prototype_projection:
        typer.echo(
            "Prototype Projection: "
            f"status={prototype_projection.get('status')} "
            f"review_status={prototype_projection.get('review_status')} "
            f"gate_ready={prototype_projection.get('gate_ready')} "
            f"drift_status={prototype_projection.get('drift_status')}"
        )
    requirement_completeness = payload.get("requirement_completeness", {})
    if isinstance(requirement_completeness, dict) and requirement_completeness:
        typer.echo(
            "Requirement Completeness: "
            f"status={requirement_completeness.get('status')} "
            f"blocked={requirement_completeness.get('blocked')} "
            f"reason={requirement_completeness.get('reason_code') or '-'}"
        )
    decision_summary = payload.get("learning_scorecard", {}).get("decision_summary", {}) if isinstance(payload.get("learning_scorecard"), dict) else {}
    typer.echo(
        "Learning scorecard: "
        f"keep={decision_summary.get('keep', 0)} "
        f"review={decision_summary.get('review', 0)} "
        f"discard={decision_summary.get('discard', 0)}"
    )
    latest_experiment = payload.get("latest_experiment", {})
    if isinstance(latest_experiment, dict) and latest_experiment:
        typer.echo(
            "Latest experiment: "
            f"run_id={latest_experiment.get('run_id', '-')} "
            f"main_kpi_score={latest_experiment.get('main_kpi_score', '-')} "
            f"delta={((latest_experiment.get('score_delta') or {}).get('main_kpi_score', '-'))}"
        )


if __name__ == "__main__":
    app()
