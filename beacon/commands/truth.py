"""Beacon truth CLI: init, verify, show for v1.4.12+."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.manifest import add_feature, load_manifest_or_fail, ManifestMissingError
from beacon.utils.feature_package import materialize_feature_package, validate_feature_package
from beacon.utils.truth_format import (
    validate_prd_format,
    validate_test_case_format,
    validate_user_story_format,
)
from beacon.utils.truth_map import feature_package_authoritative
from beacon.utils.truth_template import (
    render_prd_template,
    render_test_case_template,
    render_user_story_template,
)
from beacon.utils.versioning import resolve_target_version
from beacon.utils.intent_first import (
    capture_intents_from_utterance,
    derive_ac_from_intent,
    render_intent_first_truth,
    render_intent_first_tests,
    render_intent_first_tasks,
    render_intent_first_evidence,
)
from beacon.utils.truth_integrity import build_truth_integrity_gate

app = typer.Typer(
    name="truth",
    help="Truth triptych template and format management.",
    no_args_is_help=True,
)


def _resolve_root(project: Optional[str]) -> Path:
    return Path(project).resolve() if project else Path.cwd()


def _write_truth_file(path: Path, content: str, *, force: bool = False) -> Path:
    """Write truth content to file, creating parent dirs as needed."""
    if path.exists() and not force:
        typer.echo(f"File already exists: {path}. Use --force to overwrite.", err=True)
        raise typer.Exit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


@app.command("init")
def init_cmd(
    kind: str = typer.Argument("all", help="Kind: prd, user-story, test-case, or all"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en|zh"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
) -> None:
    """Initialize truth files."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    if lang not in ("en", "zh"):
        typer.echo(f"Invalid --lang: {lang}. Must be 'en' or 'zh'.", err=True)
        raise typer.Exit(2)

    if feature_package_authoritative(resolved):
        if kind not in {"all", "package"}:
            typer.echo(
                f"v1.5.2+ truth init writes the authoritative feature package; unsupported kind: {kind}",
                err=True,
            )
            raise typer.Exit(2)
        payload = materialize_feature_package(project_root, version=resolved, feature=feature, force=force)
        for path in payload.get("written", []):
            typer.echo(f"✓ Created package truth: {path}")
        for path in payload.get("skipped", []):
            typer.echo(f"- Preserved package truth: {path}")
        return

    base = project_root / "docs" / "beacon" / resolved
    kinds = ["prd", "user-story", "test-case"] if kind == "all" else [kind]
    written: list[str] = []

    for k in kinds:
        if k == "prd":
            content = render_prd_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "prd" / f"{slug}.md"
        elif k == "user-story":
            content = render_user_story_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "user-story" / f"{slug}.md"
        elif k == "test-case":
            content = render_test_case_template(feature_slug=slug, version=resolved, lang=lang)
            path = base / "qa" / "test-cases" / f"{slug}.md"
        else:
            typer.echo(f"Unknown kind: {k}. Use prd, user-story, test-case, or all.", err=True)
            raise typer.Exit(2)

        _write_truth_file(path, content, force=force)
        written.append(str(path))
        typer.echo(f"✓ Created {k}: {path}")

    # Register in manifest if init all
    if kind == "all":
        try:
            add_feature(project_root, resolved, feature, language=lang)
            typer.echo(f"✓ Registered feature '{slug}' in manifest")
        except Exception as e:
            typer.echo(f"⚠ Manifest registration skipped: {e}", err=True)


@app.command("verify")
def verify_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    strict: bool = typer.Option(False, "--strict", help="Fail on any non-compliance"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
) -> None:
    """Verify truth format compliance."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")
    base = project_root / "docs" / "beacon" / resolved

    if feature_package_authoritative(resolved):
        payload = validate_feature_package(project_root, version=resolved, feature=feature, write_report=True)
        status = str(payload.get("status") or "unknown")
        if status != "pass":
            typer.echo(f"✗ feature package: {status}", err=True)
            for issue in payload.get("diagnostics", []):
                typer.echo(f"  - {issue.get('code', 'unknown')}", err=True)
            raise typer.Exit(2)
        typer.echo(f"✓ Feature package truth passes validation for feature '{slug}'")
        return

    # Try to get paths from manifest first, fall back to fixed paths
    try:
        manifest = load_manifest_or_fail(project_root, resolved)
        feature_entry = None
        for f in manifest.get("features", []):
            if f.get("slug") == slug:
                feature_entry = f
                break
        if feature_entry:
            paths = {
                "prd": project_root / feature_entry.get("truth_paths", {}).get("prd", ""),
                "user_story": project_root / feature_entry.get("truth_paths", {}).get("user_story", ""),
                "test_case": project_root / feature_entry.get("truth_paths", {}).get("test_case", ""),
            }
        else:
            paths = {
                "prd": base / "prd" / f"{slug}.md",
                "user_story": base / "user-story" / f"{slug}.md",
                "test_case": base / "qa" / "test-cases" / f"{slug}.md",
            }
    except ManifestMissingError:
        paths = {
            "prd": base / "prd" / f"{slug}.md",
            "user_story": base / "user-story" / f"{slug}.md",
            "test_case": base / "qa" / "test-cases" / f"{slug}.md",
        }

    all_pass = True

    for kind, path in paths.items():
        if not path.exists():
            typer.echo(f"✗ {kind}: file not found: {path}", err=True)
            all_pass = False
            continue

        content = path.read_text(encoding="utf-8")

        if kind == "prd":
            result = validate_prd_format(content, strict=strict)
        elif kind == "user_story":
            result = validate_user_story_format(content, strict=strict)
        else:
            result = validate_test_case_format(content, strict=strict)

        status = result.get("status", "unknown")
        if status == "pass":
            typer.echo(f"✓ {kind}: format compliant ({', '.join(result.get('sections_found', [])[:5])}...)")
        else:
            typer.echo(f"✗ {kind}: format non-compliant", err=True)
            for issue in result.get("issues", []):
                typer.echo(f"  - {issue}", err=True)
            all_pass = False

    if not all_pass:
        raise typer.Exit(2)
    typer.echo(f"✓ All truth documents pass format verification for feature '{slug}'")


@app.command("show")
def show_cmd(
    kind: str = typer.Argument(..., help="Kind: prd, user-story, or test-case"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en|zh"),
) -> None:
    """Show the expected template specification without reading files."""
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    if lang not in ("en", "zh"):
        typer.echo(f"Invalid --lang: {lang}. Must be 'en' or 'zh'.", err=True)
        raise typer.Exit(2)

    if kind == "prd":
        content = render_prd_template(feature_slug=slug, version=version, lang=lang)
    elif kind == "user-story":
        content = render_user_story_template(feature_slug=slug, version=version, lang=lang)
    elif kind == "test-case":
        content = render_test_case_template(feature_slug=slug, version=version, lang=lang)
    else:
        typer.echo(f"Unknown kind: {kind}. Use prd, user-story, or test-case.", err=True)
        raise typer.Exit(2)

    typer.echo(content)


@app.command("gen")
def gen_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature name"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    utterance: str = typer.Option("", "--utterance", "-u", help="User utterance / intent description"),
    intent_first: bool = typer.Option(False, "--intent-first", help="Use intent-first protocol instead of template-driven generation"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files"),
    lang: str = typer.Option("en", "--lang", "-l", help="Language: en|zh"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview output without writing files"),
) -> None:
    """Generate truth package. Use --intent-first to drive generation from user intent."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    if intent_first:
        if not utterance:
            typer.echo("--intent-first requires --utterance (user intent description).", err=True)
            raise typer.Exit(2)

        # Phase 1: Intent Capture
        intents = capture_intents_from_utterance(utterance)
        if not intents:
            typer.echo("No intents captured from utterance. Provide a more descriptive statement.", err=True)
            raise typer.Exit(2)

        typer.echo(f"Captured {len(intents)} intent(s) from utterance:")
        for idx, intent in enumerate(intents, start=1):
            typer.echo(f"  {idx}. {intent.text}")

        # Phase 3: Structured Truth Derivation
        ac_rows = [derive_ac_from_intent(intent, idx) for idx, intent in enumerate(intents, start=1)]
        truth_content = render_intent_first_truth(feature, resolved, intents, utterance)
        tests_content = render_intent_first_tests(feature, ac_rows, version=resolved)
        tasks_content = render_intent_first_tasks(feature, ac_rows)
        evidence_content = render_intent_first_evidence(feature)
    else:
        # Template-driven fallback (delegates to init logic)
        if feature_package_authoritative(resolved):
            typer.echo("Template-driven gen not supported for feature-package-authoritative versions. Use --intent-first.", err=True)
            raise typer.Exit(2)
        from beacon.utils.truth_template import (
            render_prd_template,
            render_user_story_template,
            render_test_case_template,
        )
        truth_content = render_prd_template(feature_slug=slug, version=resolved, lang=lang)
        tests_content = render_test_case_template(feature_slug=slug, version=resolved, lang=lang)
        tasks_content = ""
        evidence_content = ""

    # Write or preview
    feature_dir = project_root / "docs" / "beacon" / resolved / "features" / slug
    paths = {
        "truth": feature_dir / "truth.md",
        "tests": feature_dir / "tests.md",
        "tasks": feature_dir / "tasks.md",
        "evidence": feature_dir / "evidence.md",
    }

    if dry_run:
        typer.echo("\n--- Dry-run preview (truth.md) ---")
        typer.echo(truth_content[:800] + "\n...")
        typer.echo("--- End preview ---")
        return

    for key, content in (("truth", truth_content), ("tests", tests_content), ("tasks", tasks_content), ("evidence", evidence_content)):
        if not content:
            continue
        path = paths[key]
        if path.exists() and not force:
            typer.echo(f"File already exists: {path}. Use --force to overwrite.", err=True)
            raise typer.Exit(2)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        typer.echo(f"✓ Created {key}: {path}")

    # v1.6.10+ HARD post-write: humanizer fulltext + truth review (no freeze recommend on fail)
    from beacon.utils.versioning import normalize_version as _norm_v

    def _sv(v: str) -> tuple[int, int, int]:
        n = (_norm_v(v) or "v0.0.0").lstrip("v").split(".")
        try:
            return int(n[0]), int(n[1]), int(n[2] if len(n) > 2 else 0)
        except Exception:
            return 0, 0, 0

    if _sv(resolved) >= (1, 6, 10):
        from beacon.utils.truth_gen_postwrite import run_truth_gen_postwrite_gates

        post = run_truth_gen_postwrite_gates(
            project_root,
            version=resolved,
            feature=slug,
            written=[str(p) for p in paths.values() if p.exists()],
            language=lang,
        )
        hum = post.get("humanizer") if isinstance(post.get("humanizer"), dict) else {}
        if hum.get("fulltext_loaded"):
            typer.echo(
                f"✓ Humanizer fulltext loaded: {hum.get('language')} chars={hum.get('skill_chars')} path={hum.get('skill_path')}"
            )
        elif hum.get("blocked"):
            typer.echo(
                f"✗ Humanizer blocked: {hum.get('reason_code')} path={hum.get('skill_path')}",
                err=True,
            )
        trg = post.get("truth_review_gate") if isinstance(post.get("truth_review_gate"), dict) else {}
        if trg.get("pass"):
            typer.echo("✓ truth review pass — freeze may be recommended")
            typer.echo("  next: beacon freeze (only after human ack)")
        else:
            typer.echo(
                f"✗ truth review failed: {trg.get('reason_code') or 'truth_review_gate_failed'} — do NOT freeze",
                err=True,
            )
            for f in trg.get("findings") or []:
                if isinstance(f, dict):
                    typer.echo(f"  - [{f.get('kind')}] {f.get('text')}", err=True)
            typer.echo("  next: fix truth/tests then `beacon truth review`", err=True)
            raise typer.Exit(2)
        if post.get("blocked") and not trg.get("pass"):
            raise typer.Exit(2)
        if post.get("blocked") and hum.get("blocked"):
            raise typer.Exit(2)

    # Phase 4: Determinism Verification (TIG-DC)
    if intent_first:
        gate = build_truth_integrity_gate(project_root, version=resolved, feature=slug, mode="block")
        dc = gate.get("determinism_check", {})
        typer.echo(f"\nTIG-DC check: placeholder={dc.get('placeholder_count', 0)}, hollow={dc.get('hollow_template_count', 0)}")
        if gate["blocked"]:
            typer.echo(f"✗ TIG-DC blocked: {gate.get('reason_code', '')}", err=True)
            for f in gate.get("findings", []):
                if isinstance(f, dict):
                    typer.echo(f"  - {f.get('kind')}: {f.get('text', '')[:80]}", err=True)
            raise typer.Exit(2)
        typer.echo("✓ TIG-DC passed — truth is deterministic.")



@app.command("review")
def review_cmd(
    feature: str = typer.Argument(..., help="Feature slug"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    json_output: bool = typer.Option(False, "--json", help="JSON report"),
    write_report: bool = typer.Option(True, "--write-report/--no-write-report", help="Persist gate report under .machine"),
) -> None:
    """Truth Review Gate: Check A/B/C/D + Humanizer L0 apply before freeze (v1.6.10+)."""
    from beacon.utils.truth_review_gate import run_truth_review_gate

    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    payload = run_truth_review_gate(
        project_root,
        version=resolved,
        feature=feature,
        write_report=write_report,
    )
    # A/B/C pass → Humanizer apply L0 (preserve machine fields); may re-run gate
    try:
        checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
        abc = bool(payload.get("abc_pass"))
        if not abc and checks:
            abc = all(
                bool((checks.get(k) or {}).get("pass"))
                for k in ("A_intent_coverage", "B_fsm_audit", "C_testability")
            )
        if abc:
            from beacon.utils.humanizer_config import apply_humanizer_l0_to_path, resolve_humanizer_profile

            prof = resolve_humanizer_profile(project_root)
            if prof.get("ok"):
                applied = apply_humanizer_l0_to_path(
                    project_root,
                    version=resolved,
                    feature=feature,
                    profile=prof,
                )
                payload["humanizer_apply"] = applied
                if applied.get("applied") and write_report:
                    payload = run_truth_review_gate(
                        project_root,
                        version=resolved,
                        feature=feature,
                        write_report=True,
                    )
                    payload["humanizer_apply"] = applied
    except Exception as _hum_exc:  # noqa: BLE001
        payload["humanizer_apply"] = {"applied": False, "error": str(_hum_exc)}

    # v1.6.10 lifecycle agent_trace (path refs only; no full chat)
    try:
        from beacon.utils.agent_trace import record_lifecycle_stage_trace

        ok_trace = bool(payload.get("pass") or payload.get("review_gate_pass"))
        payload["agent_trace"] = record_lifecycle_stage_trace(
            project_root,
            harness="truth",
            stage="truth-review",
            feature_slug=feature,
            event_type="gate_verdict",
            summary=f"truth review {'pass' if ok_trace else 'fail'}: {feature}",
            reason_code="" if ok_trace else str(payload.get("reason_code") or "truth_review_gate_failed"),
            payload={
                "review_gate_pass": ok_trace,
                "report_path": payload.get("report_path"),
                "version": resolved,
            },
            fail_closed=False,
        )
    except Exception as _trc_exc:  # noqa: BLE001
        payload["agent_trace"] = {"status": "blocked", "reason_code": "agent_trace_append_failed", "error": str(_trc_exc)}

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        ok = bool(payload.get("pass") or payload.get("review_gate_pass"))
        if ok:
            typer.echo(f"✓ truth review pass: {feature} ({resolved})")
            checks = payload.get("checks") if isinstance(payload.get("checks"), dict) else {}
            for key, val in checks.items():
                if isinstance(val, dict):
                    status = "pass" if val.get("pass") else ("skip" if val.get("skipped") else "fail")
                    typer.echo(f"  - {key}: {status}")
            if payload.get("report_path"):
                typer.echo(f"  report: {payload.get('report_path')}")
        else:
            typer.echo(
                f"✗ truth review failed: {payload.get('reason_code') or 'truth_review_gate_failed'} feature={feature}",
                err=True,
            )
            for f in payload.get("findings") or []:
                if isinstance(f, dict):
                    typer.echo(f"  - [{f.get('kind')}] {f.get('text')}", err=True)
            raise typer.Exit(2)
    if not bool(payload.get("pass") or payload.get("review_gate_pass")):
        raise typer.Exit(2)


@app.command("prose-check")
def prose_check_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature slug"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    strict: bool = typer.Option(False, "--strict", help="Require four-question cues in L0"),
    json_output: bool = typer.Option(False, "--json", help="JSON payload"),
) -> None:
    """Check truth.md human-readable L0 + language (Humanizer-oriented gate)."""
    from beacon.utils.feature_package import package_paths
    from beacon.utils.truth_human_readable import check_truth_file

    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    paths = package_paths(project_root, version=resolved, feature=feature)
    truth_path = paths["truth"]
    if not truth_path.exists():
        payload = {
            "ok": False,
            "blocked": True,
            "reason_code": "truth_missing",
            "path": str(truth_path),
            "version": resolved,
            "feature": feature,
        }
        if json_output:
            typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            typer.echo(f"✗ truth missing: {truth_path}", err=True)
        raise typer.Exit(2)
    result = check_truth_file(truth_path, strict_four_q=strict)
    from beacon.utils.humanizer_config import resolve_humanizer_profile
    humanizer = resolve_humanizer_profile(project_root, language=str(result.get("language") or "zh"))
    payload = {
        "ok": bool(result.get("ok")),
        "blocked": not bool(result.get("ok")),
        "reason_code": result.get("reason_code") or "",
        "version": resolved,
        "feature": feature,
        "humanizer": {
            "language": humanizer.get("language"),
            "skill_path": humanizer.get("skill_path"),
            "skill_exists": humanizer.get("skill_exists"),
            "ok": humanizer.get("ok"),
            "reason_code": humanizer.get("reason_code") or "",
        },
        "path": (
            str(truth_path.relative_to(project_root))
            if str(truth_path.resolve()).startswith(str(project_root.resolve()))
            else str(truth_path)
        ),
        "language": result.get("language"),
        "l0_headings": result.get("l0_headings") or list((result.get("l0") or {}).keys()),
        "detail": result.get("detail") or result.get("missing") or result.get("missing_cues"),
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            typer.echo(f"✓ prose-check pass: {feature} ({payload.get('language')}) L0={payload.get('l0_headings')}")
        else:
            typer.echo(
                f"✗ prose-check blocked: {payload.get('reason_code')} feature={feature}",
                err=True,
            )
            raise typer.Exit(2)

