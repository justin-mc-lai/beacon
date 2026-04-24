"""Beacon release command - Release checklist"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json
import re

from beacon.utils.artifact_paths import change_docs_file, change_file_output, machine_change_dir
from beacon.utils.memory import append_memory_entry
from beacon.utils.release_scorecard import build_release_scorecard
from beacon.utils.runtime_projection_store import runtime_projection_transaction_contract
from beacon.utils.versioning import project_runtime_feature_enabled, resolve_runtime_version, resolve_target_version
from beacon.utils.workflow_memory import append_lifecycle_event

app = typer.Typer(name="release", help="Release checklist")
_TECHNICAL_ARCHIVE_RE = re.compile(r"^technical-implementation-(?P<slug>.+)\.json$")


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
            added = [str(item).strip() for item in payload.get("additions", []) if str(item).strip()]
            removed = [str(item).strip() for item in payload.get("deletions", []) if str(item).strip()]
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
                        f"docs/beacon/{version}/execution/technical-implementation-{slug}.md",
                        f"docs/beacon/{version}/.machine/execution/implementation-summary-{slug}.json",
                        f"docs/beacon/{version}/execution/implementation-summary-{slug}.md",
                    ],
                }
            )
            _materialize_feature_change_if_missing(project_root, version=version, payload=items[-1])
            seen_slugs.add(slug)
    return items


def _build_version_change_payload(project_root: Path, *, version: str) -> dict:
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

    return {
        "schema_version": "1.0",
        "version": version,
        "status": "generated",
        "feature_count": len(features),
        "features": features,
        "added": _dedupe_strings(added),
        "removed": _dedupe_strings(removed),
        "fixed": _dedupe_strings(fixed),
        "traceability_refs": _dedupe_strings(traceability_refs),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


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
    version_change_md = change_docs_file(project_root, resolved_version, f"{resolved_version}.md")
    version_change_json = change_file_output(project_root, resolved_version, f"{resolved_version}.json")
    version_change_md.parent.mkdir(parents=True, exist_ok=True)
    version_change_json.parent.mkdir(parents=True, exist_ok=True)
    version_change_md.write_text(_render_version_change_markdown(version_change_payload), encoding="utf-8")
    version_change_json.write_text(json.dumps(version_change_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    version_change_md_ref = str(version_change_md.relative_to(project_root))
    version_change_json_ref = str(version_change_json.relative_to(project_root))

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

## Notes

"""
    output_paths = (
        [Path(output)]
        if output
        else [
            project_root / "docs" / "beacon" / resolved_version / "release" / f"{resolved_version}.md",
        ]
    )
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(release_content)
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
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Check release conditions"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    resolved_runtime = resolve_runtime_version(project_root, "auto")
    release_scorecard = build_release_scorecard(project_root, version=resolved_version)
    change_documents = release_scorecard.get("change_documents") if isinstance(release_scorecard.get("change_documents"), dict) else {}
    feature_qa_scorecard = (
        release_scorecard.get("feature_qa_scorecard")
        if isinstance(release_scorecard.get("feature_qa_scorecard"), dict)
        else {}
    )
    enforce_change_documents = project_runtime_feature_enabled(
        project_root,
        "v1.3.1",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    enforce_release_scorecard = project_runtime_feature_enabled(
        project_root,
        "v1.3.6",
        docs_version=resolved_version,
        runtime_version=resolved_runtime,
    )
    authoritative_release_ready = bool(release_scorecard.get("release_ready", False))

    typer.echo(f"Checking release conditions for {resolved_version}")
    typer.echo("=" * 40)

    auto_test_path = project_root / ".beacon" / "auto-test-status.json"
    gate_report_path = project_root / ".beacon" / "gate-report.json"
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    coverage_summary_path = project_root / ".beacon" / "coverage-summary.json"

    checks: list[tuple[str, bool, str]] = []
    evidence_refs: list[str] = []

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
    checks.append(("auto-test status passed", auto_test_ok, f"status={auto_test_status}"))
    checks.append(
        (
            "auto-test version matches release version",
            bool(auto_test_version) and auto_test_version == resolved_version,
            f"artifact_version={auto_test_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
        (
            "auto-test run_id present",
            bool(auto_test_run_id),
            f"run_id={auto_test_run_id or 'missing'}",
        )
    )

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
    checks.append(("gate report pass", gate_ok, f"status={gate_status or 'unknown'}"))
    checks.append(
        (
            "gate report version matches release version",
            bool(gate_version) and gate_version == resolved_version,
            f"artifact_version={gate_version or 'missing'}, expected={resolved_version}",
        )
    )
    checks.append(
        (
            "gate report run_id matches auto-test",
            (
                bool(gate_run_id)
                and bool(auto_test_run_id)
                and (
                    gate_run_id == auto_test_run_id
                    or (enforce_release_scorecard and authoritative_release_ready and gate_ok and auto_test_ok)
                )
            ),
            (
                f"gate_run_id={gate_run_id or 'missing'}, auto_test_run_id={auto_test_run_id or 'missing'}"
                + (
                    ", authoritative_release_scorecard=true"
                    if enforce_release_scorecard and authoritative_release_ready and gate_ok and auto_test_ok
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
    checks.append(("evidence manifest present", manifest_ok, f"entries={manifest_entries}"))
    checks.append(
        (
            "evidence manifest version matches release version",
            bool(manifest_version) and manifest_version == resolved_version,
            f"artifact_version={manifest_version or 'missing'}, expected={resolved_version}",
        )
    )
    expected_run_id = auto_test_run_id or gate_run_id
    checks.append(
        (
            "evidence manifest run_id matches test artifacts",
            bool(manifest_run_id) and bool(expected_run_id) and manifest_run_id == expected_run_id,
            f"manifest_run_id={manifest_run_id or 'missing'}, expected={expected_run_id or 'missing'}",
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
    if not coverage_ok and enforce_release_scorecard and authoritative_release_ready:
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
    checks.append(("coverage artifact ready", coverage_ok, coverage_detail))
    if coverage_summary_path.exists():
        checks.append(
            (
                "coverage summary version matches release version",
                bool(coverage_version) and coverage_version == resolved_version,
                f"artifact_version={coverage_version or 'missing'}, expected={resolved_version}",
            )
        )
        checks.append(
            (
                "coverage summary run_id matches test artifacts",
                bool(coverage_run_id) and bool(expected_run_id) and coverage_run_id == expected_run_id,
                f"coverage_run_id={coverage_run_id or 'missing'}, expected={expected_run_id or 'missing'}",
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
                runtime_tx_ok,
                f"status={runtime_tx_contract.get('status') or 'unknown'}, reason={runtime_tx_contract.get('reason_code') or '-'}",
            )
        )

    if enforce_change_documents:
        change_md_ref = str(change_documents.get("markdown_path") or "")
        change_json_ref = str(change_documents.get("json_path") or "")
        if change_md_ref:
            evidence_refs.append(change_md_ref)
        if change_json_ref:
            evidence_refs.append(change_json_ref)
        checks.append(
            (
                "version change markdown exists",
                bool(change_documents.get("markdown_exists", False)),
                f"path={change_md_ref or 'missing'}",
            )
        )
        checks.append(
            (
                "version change payload exists",
                bool(change_documents.get("json_exists", False)),
                f"path={change_json_ref or 'missing'}",
            )
        )
        checks.append(
            (
                "version change payload matches release version",
                bool(change_documents.get("version_match", False)),
                f"feature_count={change_documents.get('feature_count', 0)}",
            )
        )
        checks.append(
            (
                "version change document includes current feature",
                bool(change_documents.get("includes_current_feature", False)),
                f"current_feature={change_documents.get('current_feature_slug') or 'none'}",
            )
        )

    if enforce_release_scorecard:
        semantic = release_scorecard.get("semantic") if isinstance(release_scorecard.get("semantic"), dict) else {}
        semantic_status = str(semantic.get("status") or "unknown")
        semantic_reason = str(semantic.get("reason_code") or "")
        checks.append(
            (
                "release scorecard ready",
                bool(release_scorecard.get("release_ready", False)),
                f"feature={release_scorecard.get('qa', {}).get('feature') or 'none'}, semantic_reason={semantic_reason or '-'}",
            )
        )
        if semantic:
            checks.append(
                (
                    "semantic contract ready",
                    semantic_status == "pass",
                    f"status={semantic_status}, reason={semantic_reason or '-'}",
                )
            )

    all_passed = True
    failed_checks: list[str] = []
    for check_name, passed, detail in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        typer.echo(f"{status}: {check_name} ({detail})")
        if not passed:
            all_passed = False
            failed_checks.append(check_name)

    if all_passed:
        typer.echo("\n✓ Release conditions met")
        status = "pass"
    else:
        typer.echo("\n✗ Some checks failed")
        status = "blocked"

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
