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
        from beacon.utils.plan_goal_task_closure import materialize_deterministic_scaffold

        payload = materialize_deterministic_scaffold(
            project_root,
            version=resolved,
            feature=feature,
            force=force,
        )
        materialize = payload.get("materialize") or {}
        for written in materialize.get("written", []):
            typer.echo(f"✓ Created package truth: {written}")
        for skipped in materialize.get("skipped", []):
            typer.echo(f"- Preserved package truth: {skipped}")
        if payload.get("pass"):
            typer.echo(
                "✓ Deterministic scaffold ready (package_maturity=scaffold; Host LLM fill required before freeze)"
            )
        else:
            typer.echo(
                f"⚠ Scaffold gate: {payload.get('reason_code') or 'deterministic_scaffold_not_filled'}",
                err=True,
            )
        # always return scaffold payload path via optional env-free print for hosts
        if payload.get("recommend_freeze"):
            typer.echo("✗ Scaffold must not recommend freeze", err=True)
            raise typer.Exit(2)
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
    response_json: Optional[Path] = typer.Option(
        None,
        "--response-json",
        help="Optional truth-fill-response.v1 JSON (Host LLM). Overrides env host-response.",
    ),
    require_host_response: bool = typer.Option(
        False,
        "--require-host-response",
        help="Fail if host-response/bridge missing (no CLI semantic compile fallback)",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON pipeline result"),
) -> None:
    """Generate truth package. Use --intent-first to drive generation from user intent."""
    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    slug = feature.strip().lower().replace(" ", "-").replace("_", "-")

    # v1.6.11+: authoritative path = scaffold + fill-request + host/semantic response + transaction apply
    try:
        from beacon.utils.plan_goal_task_closure import (
            run_truth_gen_fill_pipeline,
            version_requires_task_closure,
        )
    except Exception:  # noqa: BLE001
        version_requires_task_closure = None  # type: ignore
        run_truth_gen_fill_pipeline = None  # type: ignore

    if version_requires_task_closure and version_requires_task_closure(resolved, slug):
        try:
            from beacon.utils.plan_goal_task_closure import ensure_truth_fill_host_bridge_defaults
            ensure_truth_fill_host_bridge_defaults()
        except Exception:
            pass
        if not utterance and not response_json:
            # allow env host response without utterance only if require_host not set... still need utterance for compile fallback
            if require_host_response:
                pass
            else:
                typer.echo("v1.6.11+ truth gen recommends --utterance (or provide host-response / --response-json).", err=True)
        explicit = None
        if response_json is not None:
            explicit = json.loads(Path(response_json).read_text(encoding="utf-8"))
        result = run_truth_gen_fill_pipeline(
            project_root,
            version=resolved,
            feature=slug,
            utterance=utterance or f"Generate package truth for {slug}",
            language=lang if lang in {"zh", "en", "bilingual"} else "zh",
            force_scaffold=True,
            explicit_response=explicit,
            allow_semantic_compile_fallback=not require_host_response,
            dry_run=dry_run,
        )
        if json_output:
            typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            steps = result.get("steps") or []
            for step in steps:
                if isinstance(step, dict):
                    typer.echo(f"- {step.get('name')}: {step.get('status')} {step.get('source') or step.get('detail') or ''}".rstrip())
            if result.get("pass"):
                for key, rel in (result.get("package_paths") or {}).items():
                    typer.echo(f"✓ {key}: {rel}")
                src = ((result.get("resolve") or {}).get("source") or "")
                transport = ((result.get("resolve") or {}).get("transport") or "")
                typer.echo(f"✓ fill transport: {transport} source={src}")
                if result.get("recommend_freeze"):
                    typer.echo("✓ truth review pass — freeze may be recommended after human ack")
                else:
                    typer.echo("⚠ filled via transaction; review/freeze still gated")
            else:
                typer.echo(
                    f"✗ truth fill pipeline blocked: {result.get('reason_code')}",
                    err=True,
                )
                raise typer.Exit(2)
        if result.get("blocked"):
            raise typer.Exit(2)
        return

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
    try:
        from beacon.utils.workspace_clean import verify_clean_workspace

        payload["clean_workspace_gate"] = verify_clean_workspace(
            project_root,
            version=resolved,
            feature=feature,
            profile="truth",
            strict=False,
        )
    except Exception as _cw_exc:  # noqa: BLE001
        payload["clean_workspace_gate"] = {
            "status": "blocked",
            "reason_code": "clean_workspace_gate_error",
            "error": str(_cw_exc),
        }
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
                    try:
                        from beacon.utils.workspace_clean import verify_clean_workspace

                        payload["clean_workspace_gate"] = verify_clean_workspace(
                            project_root,
                            version=resolved,
                            feature=feature,
                            profile="truth",
                            strict=False,
                        )
                    except Exception as _cw_exc:  # noqa: BLE001
                        payload["clean_workspace_gate"] = {
                            "status": "blocked",
                            "reason_code": "clean_workspace_gate_error",
                            "error": str(_cw_exc),
                        }
                    payload["humanizer_apply"] = applied
    except Exception as _hum_exc:  # noqa: BLE001
        payload["humanizer_apply"] = {"applied": False, "error": str(_hum_exc)}

    # v1.6.10 lifecycle agent_trace (path refs only; no full chat)
    try:
        from beacon.utils.agent_trace import (
            lifecycle_trace_fail_closed_enabled,
            record_lifecycle_stage_trace,
        )

        ok_trace = bool(payload.get("pass") or payload.get("review_gate_pass"))
        _fc = lifecycle_trace_fail_closed_enabled()
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
            fail_closed=_fc,
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
    # governed write: block when fail-closed and agent_trace did not land
    _at = payload.get("agent_trace") if isinstance(payload.get("agent_trace"), dict) else {}
    if str(_at.get("status") or "") != "pass":
        from beacon.utils.agent_trace import lifecycle_trace_fail_closed_enabled

        if lifecycle_trace_fail_closed_enabled():
            if not json_output:
                typer.echo(
                    f"✗ agent_trace fail-closed: {_at.get('reason_code') or 'agent_trace_missing'}",
                    err=True,
                )
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





@app.command("host-bridge", hidden=True)
def host_bridge(
    payload_json: str = typer.Argument("", help="Optional bridge request JSON; default reads stdin"),
) -> None:
    """Hidden host-native bridge for truth-fill-response.v1 (real host agent contract).

    Request (stdin/arg): truth-fill-request.v1 or gen pipeline wrapper
    Response (stdout JSON): truth-fill-response.v1
    """
    import sys
    from beacon.utils.plan_goal_task_closure import (
        SCHEMA_FILL_REQUEST,
        SCHEMA_FILL_RESPONSE,
        compile_intent_semantics_to_fill_response,
        normalize_host_fill_response,
    )

    raw = (payload_json or "").strip()
    if not raw:
        raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw else {}
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"invalid host-bridge json: {exc}", err=True)
        raise typer.Exit(2) from exc
    if not isinstance(payload, dict):
        typer.echo("host-bridge payload must be object", err=True)
        raise typer.Exit(2)

    # unwrap common wrappers from pipeline / host agent / fill-request CLI
    request = payload
    if isinstance(payload.get("fill_request"), dict):
        fr = payload["fill_request"]
        request = fr.get("request") if isinstance(fr.get("request"), dict) else fr
    elif isinstance(payload.get("request"), dict):
        request = payload["request"]

    def _stamp_bridge(resp: dict) -> dict:
        out = dict(resp)
        out["model"] = out.get("model") or "host-agent-pass-through"
        out["bridge"] = "beacon-truth-host-bridge"
        out.setdefault("request_schema", SCHEMA_FILL_REQUEST)
        out.setdefault("response_schema", SCHEMA_FILL_RESPONSE)
        out.setdefault(
            "host_agent_contract",
            {
                "input": "truth-fill-request.v1",
                "output": "truth-fill-response.v1",
                "forbidden": ["direct_markdown_overwrite", "legacy_prd_canonical_write"],
            },
        )
        return out

    # Pass-through: payload already is truth-fill-response.v1 (or host-agent equivalent).
    maybe = normalize_host_fill_response(payload)
    if maybe.get("schema") == SCHEMA_FILL_RESPONSE and (
        maybe.get("acceptance_criteria") or maybe.get("plain_language_l0")
    ):
        typer.echo(json.dumps(_stamp_bridge(maybe), ensure_ascii=False))
        return

    utterance = str(
        request.get("utterance")
        or payload.get("utterance")
        or (request.get("context") or {}).get("utterance")
        or ""
    ).strip()
    version = str(request.get("version") or payload.get("version") or "v1.6.11").strip()
    feature = str(
        payload.get("feature")
        or request.get("feature")
        or (request.get("program_refs") or {}).get("feature")
        or "feature"
    ).strip()
    language = "zh"
    hum = request.get("humanizer_profile") if isinstance(request.get("humanizer_profile"), dict) else {}
    if hum.get("language") in {"zh", "en", "bilingual"}:
        language = str(hum.get("language"))

    if not utterance:
        typer.echo("host-bridge requires utterance in request", err=True)
        raise typer.Exit(2)

    response = compile_intent_semantics_to_fill_response(
        utterance=utterance,
        feature=feature,
        version=version,
        language=language,
    )
    response["model"] = "beacon-truth-host-bridge"
    response["bridge"] = "beacon-truth-host-bridge"
    response["request_schema"] = SCHEMA_FILL_REQUEST
    response["response_schema"] = SCHEMA_FILL_RESPONSE
    # Host agent contract echo for debugging
    response["host_agent_contract"] = {
        "input": "truth-fill-request.v1",
        "output": "truth-fill-response.v1",
        "forbidden": ["direct_markdown_overwrite", "legacy_prd_canonical_write"],
    }
    typer.echo(json.dumps(response, ensure_ascii=False))


@app.command("fill-request")
def fill_request_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature slug"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    utterance: str = typer.Option(..., "--utterance", "-u", help="Goal/change utterance"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    revision_id: str = typer.Option("R2", "--revision-id", help="Target revision id"),
    program: str = typer.Option("", "--program", help="Optional program slug for PAC/program refs"),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit JSON (default true)"),
) -> None:
    """Build truth-fill-request.v1 from ContextEnvelope (CLI scaffold side)."""
    from beacon.utils.feature_package import package_paths
    from beacon.utils.plan_goal_task_closure import (
        build_context_envelope,
        build_truth_fill_request,
    )
    from beacon.utils.truth_map import FEATURE_SURFACES, _sha256

    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    paths = package_paths(project_root, version=resolved, feature=feature)
    source_hashes = {
        surface: (_sha256(paths[surface]) if paths[surface].exists() else "")
        for surface in FEATURE_SURFACES
    }
    if not all(source_hashes.values()):
        # ensure scaffold exists first
        from beacon.utils.plan_goal_task_closure import materialize_deterministic_scaffold

        materialize_deterministic_scaffold(project_root, version=resolved, feature=feature, force=False)
        source_hashes = {
            surface: (_sha256(paths[surface]) if paths[surface].exists() else "")
            for surface in FEATURE_SURFACES
        }
    program_slug = program.strip() or ""
    program_refs = {}
    pac_refs = ["PAC-016", "PAC-017", "PAC-018", "PAC-019", "PAC-021"]
    if program_slug:
        program_refs = {
            "manifest": f"docs/beacon/{resolved}/programs/{program_slug}/program-manifest.md",
            "feature_graph": f"docs/beacon/{resolved}/programs/{program_slug}/feature-graph.json",
        }
    envelope = build_context_envelope(
        utterance=utterance,
        version=resolved,
        baseline_commit=_git_head(project_root),
        truth_refs={
            "truth": f"docs/beacon/{resolved}/features/{feature}/truth.md",
            "tests": f"docs/beacon/{resolved}/features/{feature}/tests.md",
            "tasks": f"docs/beacon/{resolved}/features/{feature}/tasks.md",
            "evidence": f"docs/beacon/{resolved}/features/{feature}/evidence.md",
        },
        code_entries=["beacon/utils/plan_goal_task_closure.py", "beacon/commands/truth.py"],
        test_entries=["tests/test_v1611_plan_goal_task_closure.py"],
        change_history=[f"docs/beacon/{resolved}/change"],
        inherited_contracts=[
            "docs/beacon/v1.6.10/features/truth-core-authority-v1610/truth.md",
            "docs/beacon/v1.6.9/features/beacon-plan-goal-deep-integration-v169/truth.md",
        ],
        execution_authorities={
            "subagent_runtime": "host_or_fallback",
            "truth_canonical": "main",
            "worktree_governance": "workspace_admit",
            "trace_authority": "agent_trace.v1",
        },
        source_hashes=source_hashes,
        revision_id=revision_id,
        semantic_compiler_refs=[
            "beacon/utils/intent_first.py",
            "beacon/commands/user_story.py",
            "beacon/commands/prd.py",
        ],
        host_transport={"capability": "host-response", "precedence": ["host", "cli"]},
        humanizer_profile={"language": "zh", "preserve_machine_fields": True},
        program_refs=program_refs,
        pac_refs=pac_refs,
    )
    request = build_truth_fill_request(envelope)
    payload = {
        "schema_version": "1.0",
        "version": resolved,
        "feature": feature,
        "envelope": envelope,
        "fill_request": request,
        "status": "pass" if request.get("pass") else "blocked",
        "blocked": bool(request.get("blocked")),
        "reason_code": request.get("reason_code") or "",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"status": payload["status"], "reason_code": payload["reason_code"]}, ensure_ascii=False))
    if payload["blocked"]:
        raise typer.Exit(2)


@app.command("fill-apply")
def fill_apply_cmd(
    feature: str = typer.Option(..., "--feature", "-f", help="Feature slug"),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    request_json: Path = typer.Option(..., "--request-json", help="truth-fill-request.v1 JSON file"),
    response_json: Path = typer.Option(..., "--response-json", help="truth-fill-response.v1 JSON file"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    base_revision: str = typer.Option("R2", "--base-revision", help="Base revision"),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit JSON"),
) -> None:
    """Apply Host LLM structured fill via truth-fill-transaction.v1 (no free Markdown overwrite)."""
    from beacon.utils.plan_goal_task_closure import apply_structured_fill_transaction

    project_root = _resolve_root(project)
    resolved = resolve_target_version(project_root, version)
    request = json.loads(Path(request_json).read_text(encoding="utf-8"))
    response = json.loads(Path(response_json).read_text(encoding="utf-8"))
    # allow nested request payload from fill-request command output
    if request.get("fill_request") and isinstance(request.get("fill_request"), dict):
        nested = request["fill_request"]
        request = nested.get("request") if isinstance(nested.get("request"), dict) else nested
    if response.get("response") and isinstance(response.get("response"), dict):
        response = response["response"]
    result = apply_structured_fill_transaction(
        project_root,
        version=resolved,
        feature=feature,
        request=request,
        response=response,
        base_revision=base_revision,
    )
    payload = {
        "schema_version": "1.0",
        "version": resolved,
        "feature": feature,
        "result": result,
        "status": "pass" if result.get("pass") else "blocked",
        "blocked": bool(result.get("blocked")),
        "reason_code": result.get("reason_code") or "",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"status": payload["status"], "reason_code": payload["reason_code"]}, ensure_ascii=False))
    if payload["blocked"]:
        raise typer.Exit(2)


@app.command("fill-validate-response")
def fill_validate_response_cmd(
    response_json: Path = typer.Argument(..., help="truth-fill-response.v1 JSON file"),
    json_output: bool = typer.Option(True, "--json/--no-json", help="Emit JSON"),
) -> None:
    """Validate Host LLM truth-fill-response.v1 without writing files."""
    from beacon.utils.plan_goal_task_closure import (
        reject_false_completeness,
        validate_host_llm_full_package_fill,
    )

    response = json.loads(Path(response_json).read_text(encoding="utf-8"))
    if response.get("response") and isinstance(response.get("response"), dict):
        response = response["response"]
    filled = validate_host_llm_full_package_fill(response)
    false_c = reject_false_completeness(response)
    blocked = bool(filled.get("blocked") or false_c.get("blocked"))
    payload = {
        "schema_version": "1.0",
        "status": "blocked" if blocked else "pass",
        "blocked": blocked,
        "fill_validation": filled,
        "false_completeness": false_c,
        "reason_code": filled.get("reason_code") or false_c.get("reason_code") or "",
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(json.dumps({"status": payload["status"]}, ensure_ascii=False))
    if blocked:
        raise typer.Exit(2)


def _git_head(project_root: Path) -> str:
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except Exception:  # noqa: BLE001
        return "unknown"

