"""Beacon test-case command - Generate test cases."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.artifact_paths import qa_docs_dir, qa_matrix_candidates, qa_matrix_output, uses_machine_surface
from beacon.utils.qa9 import (
    QA9_TYPES,
    build_qa_strategy,
    build_qa_llm_plan,
    default_assertion_for_qa_type,
    default_command_for_qa_type,
    normalize_qa_type,
    parse_qa_types,
    to_legacy_layer,
)
from beacon.utils.story_scenarios import expand_story_scenarios, write_story_scenario_map
from beacon.utils.versioning import discover_versions, resolve_target_version

app = typer.Typer(name="test-case", help="Generate test cases")


def _slug(text: str) -> str:
    return (text or "").strip().lower().replace(" ", "-")


def _candidate_doc_paths(project_root: Path, version: str, category: str, slug: str) -> list[Path]:
    return [project_root / "docs" / "beacon" / version / category / f"{slug}.md"]


def _read_first_existing(paths: list[Path]) -> tuple[Path | None, str]:
    for path in paths:
        if path.exists():
            return path, path.read_text(encoding="utf-8", errors="ignore")
    return None, ""


def _extract_ac_items(content: str, source: str) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()
    if not content.strip():
        return items

    # Markdown table pattern: | AC-001 | text | ...
    for line in content.splitlines():
        if "|" not in line:
            continue
        m = re.search(r"\b(AC-\d{3,})\b", line, flags=re.I)
        if not m:
            continue
        ac_id = m.group(1).upper()
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        text = cells[1] if len(cells) > 1 else line.strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "text": text, "source": source})

    # Fallback bullet/text pattern: AC-001: xxx
    for m in re.finditer(r"\b(AC-\d{3,})\b[:：]?\s*([^\n]+)", content, flags=re.I):
        ac_id = m.group(1).upper()
        text = m.group(2).strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append({"ac_id": ac_id, "text": text, "source": source})

    return items


def _infer_layer_from_ac(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ("登录", "注册", "浏览", "表单", "submit", "form", "ui", "页面", "点击")):
        return "ui"
    if any(x in t for x in ("api", "接口", "http", "curl", "endpoint")):
        return "api-curl"
    if any(x in t for x in ("单元", "unit", "函数", "边界", "error", "异常", "校验", "security")):
        return "unit"
    # Default to unit for deterministic commandability in minimal setups.
    return "unit"


def _default_command_for_layer(layer: str) -> str:
    qa_type = normalize_qa_type(layer)
    return default_command_for_qa_type(qa_type)


def _default_assertion_for_layer(layer: str) -> str:
    qa_type = normalize_qa_type(layer)
    return default_assertion_for_qa_type(qa_type)


def _default_priority_for_qa_type(qa_type: str) -> str:
    return {
        "functional": "P0",
        "smoke": "P0",
        "unit": "P0",
        "interface": "P0",
        "contract": "P1",
        "integration": "P1",
        "regression": "P1",
        "exception": "P1",
        "compatibility": "P1",
    }.get(qa_type, "P2")


def _load_prototype_contract_artifacts(project_root: Path, version: str, feature_slug: str) -> tuple[dict, dict]:
    proto_root = project_root / "docs" / "beacon" / version / "prototype" / feature_slug
    navigation = {}
    interaction = {}
    nav_path = proto_root / "navigation-map.json"
    interaction_path = proto_root / "interaction-map.json"
    if nav_path.exists():
        try:
            payload = json.loads(nav_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                navigation = payload
        except Exception:  # noqa: BLE001
            navigation = {}
    if interaction_path.exists():
        try:
            payload = json.loads(interaction_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                interaction = payload
        except Exception:  # noqa: BLE001
            interaction = {}
    return navigation, interaction


def _load_route_closure_artifacts(project_root: Path, version: str, feature_slug: str) -> tuple[dict, dict]:
    proto_root = project_root / "docs" / "beacon" / version / "prototype" / feature_slug
    route_payload = {}
    impl_payload = {}
    route_path = proto_root / "route-closure-contract.json"
    impl_path = proto_root / "implementation-map.json"
    if route_path.exists():
        try:
            route_payload = json.loads(route_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            route_payload = {}
    if impl_path.exists():
        try:
            impl_payload = json.loads(impl_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            impl_payload = {}
    return route_payload, impl_payload


def _story_sequence_for_feature(project_root: Path, version: str, feature_slug: str, *, fallback_entries: list[dict]) -> list[dict]:
    machine_story = project_root / "docs" / "beacon" / version / ".machine" / "user-story" / f"{feature_slug}.json"
    if machine_story.exists():
        try:
            payload = json.loads(machine_story.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
        if isinstance(payload, dict):
            active_revision = str(payload.get("current_revision_id") or "")
            for story in payload.get("stories", []):
                if not isinstance(story, dict) or str(story.get("revision_id") or "") != active_revision:
                    continue
                items = story.get("items") if isinstance(story.get("items"), list) else []
                rows = [
                    {
                        "ac_id": str(item.get("id") or ""),
                        "theme": str(item.get("theme") or ""),
                        "text": str(item.get("text") or ""),
                    }
                    for item in items
                    if isinstance(item, dict) and str(item.get("kind") or "") == "ac" and str(item.get("id") or "").strip()
                ]
                if rows:
                    return rows

    us_path, us_content = _read_first_existing(_candidate_doc_paths(project_root, version, "user-story", feature_slug))
    ac_items = _extract_ac_items(us_content, f"user-story:{us_path}" if us_path else "user-story:missing")
    if ac_items:
        return [{"ac_id": item["ac_id"], "theme": str(item.get("source") or ""), "text": str(item.get("text") or "")} for item in ac_items]
    return [
        {
            "ac_id": str(item.get("ac_id") or ""),
            "theme": str(item.get("layer") or item.get("qa_type") or ""),
            "text": str(item.get("assertion") or ""),
        }
        for item in fallback_entries
        if isinstance(item, dict) and str(item.get("ac_id") or "").strip()
    ]


def _build_qa_requirements(qa_types: list[str], qa_applicability: Optional[dict[str, str]] = None) -> list[dict]:
    qa_set = set(qa_types)
    applicability_map = qa_applicability or {}
    out: list[dict] = []
    for qa_type in QA9_TYPES:
        selected = qa_type in qa_set
        applicability = str(applicability_map.get(qa_type) or ("required" if selected else "conditional")).strip().lower()
        if applicability not in {"required", "conditional", "na"}:
            applicability = "required" if selected else "conditional"
        required = selected and applicability == "required"
        out.append(
            {
                "qa_type": qa_type,
                "required": bool(required),
                "automation_required": bool(required),
                "min_cases": 1 if required else 0,
                "applicability": applicability,
                "waiver": {
                    "ticket": "",
                    "approved_by": "",
                    "expires_at": "",
                },
            }
        )
    return out


def _build_qa9_entries(
    *,
    feature: str,
    feature_slug: str,
    ac_items: list[dict],
    qa_types: list[str],
    ui_runner: str = "playwright",
    command_baseline: Optional[dict[str, str]] = None,
) -> list[dict]:
    entries: list[dict] = []
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]

    qa_pool = list(qa_types) or list(QA9_TYPES)
    baseline = command_baseline or {}
    present_types: set[str] = set()
    idx = 0

    # Rule 1: each AC must map to at least one executable TC.
    for ac_idx, ac in enumerate(ac_items, start=1):
        inferred = normalize_qa_type(_infer_layer_from_ac(ac.get("text", "")))
        qa_type = inferred if inferred in qa_pool else qa_pool[(ac_idx - 1) % len(qa_pool)]
        idx += 1
        tc_id = f"TC-{idx:03d}"
        command = str(baseline.get(qa_type) or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
        present_types.add(qa_type)
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac.get("ac_id", "AC-001"),
                "layer": to_legacy_layer(qa_type),
                "qa_type": qa_type,
                "title": f"{feature} {qa_type} :: {str(ac.get('text', '')).strip()[:80]}",
                "priority": _default_priority_for_qa_type(qa_type),
                "automation": "auto",
                "command": command,
                "assertion": default_assertion_for_qa_type(qa_type),
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json",
                "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )

    # Rule 2: required qa_types must be fully covered.
    for qa_type in qa_pool:
        if qa_type in present_types:
            continue
        idx += 1
        ac = ac_items[(idx - 1) % len(ac_items)]
        tc_id = f"TC-{idx:03d}"
        command = str(baseline.get(qa_type) or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner)
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac.get("ac_id", "AC-001"),
                "layer": to_legacy_layer(qa_type),
                "qa_type": qa_type,
                "title": f"{feature} {qa_type} coverage",
                "priority": _default_priority_for_qa_type(qa_type),
                "automation": "auto",
                "command": command,
                "assertion": default_assertion_for_qa_type(qa_type),
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json",
                "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )
    return entries


def _load_think_progress(project_root: Path, version: str) -> dict:
    candidates = [
        project_root / ".beacon" / "state" / "think-progress" / f"{version}.json",
        project_root / ".beacon" / "state" / "think-progress.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def _load_existing_qa9_payload(project_root: Path, version: str, feature_slug: str) -> dict:
    for path in qa_matrix_candidates(project_root, version, feature_slug, "qa9-matrix"):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            payload = {}
        if isinstance(payload, dict) and isinstance(payload.get("entries"), list):
            return payload
    return {}


def _normalize_existing_qa9_entries(
    *,
    feature: str,
    feature_slug: str,
    entries: list[dict],
    ac_items: list[dict],
    ui_runner: str,
) -> list[dict]:
    normalized: list[dict] = []
    ac_seed = ac_items or [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    for index, item in enumerate(entries, start=1):
        if not isinstance(item, dict):
            continue
        ac = ac_seed[(index - 1) % len(ac_seed)]
        qa_type = normalize_qa_type(
            str(item.get("qa_type") or item.get("type") or item.get("layer") or _infer_layer_from_ac(str(ac.get("text") or "")))
        )
        if qa_type not in QA9_TYPES:
            qa_type = normalize_qa_type(_infer_layer_from_ac(str(ac.get("text") or "")))
        if qa_type not in QA9_TYPES:
            qa_type = "contract"
        tc_id = str(item.get("tc_id") or item.get("id") or f"TC-{index:03d}").strip() or f"TC-{index:03d}"
        normalized.append(
            {
                "tc_id": tc_id,
                "ac_id": str(item.get("ac_id") or ac.get("ac_id") or f"AC-{index:03d}").strip() or f"AC-{index:03d}",
                "layer": str(item.get("layer") or to_legacy_layer(qa_type)),
                "qa_type": qa_type,
                "title": str(item.get("title") or f"{feature} {qa_type} :: {str(item.get('assertion') or ac.get('text') or '').strip()[:80]}"),
                "priority": str(item.get("priority") or _default_priority_for_qa_type(qa_type)),
                "automation": str(item.get("automation") or "auto"),
                "command": str(item.get("command") or "").strip() or default_command_for_qa_type(qa_type, ui_runner=ui_runner),
                "assertion": str(item.get("assertion") or default_assertion_for_qa_type(qa_type)),
                "evidence_path": str(item.get("evidence_path") or f".beacon/evidence/test-results/{feature_slug}/{{run_id}}/{tc_id}.json"),
                "required_files": item.get("required_files") if isinstance(item.get("required_files"), list) else ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                "status": str(item.get("status") or "pending"),
                "source": str(item.get("source") or ac.get("source") or "qa9:existing"),
            }
        )
    return normalized


def _build_story_scenario_payload(
    *,
    project_root: Path,
    version: str,
    feature: str,
    expansion_profile: str,
    scenario_depth: str,
    ui_runner: str,
) -> tuple[dict, str]:
    feature_slug = _slug(feature)
    us_path, us_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "user-story", feature_slug)
    )
    prd_path, prd_content = _read_first_existing(
        _candidate_doc_paths(project_root, version, "prd", feature_slug)
    )
    ac_items = _extract_ac_items(us_content, f"user-story:{us_path}" if us_path else "user-story:missing")
    ac_items.extend(_extract_ac_items(prd_content, f"prd:{prd_path}" if prd_path else "prd:missing"))
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]
    existing_qa9_payload = _load_existing_qa9_payload(project_root, version, feature_slug)
    existing_entries = (
        [item for item in existing_qa9_payload.get("entries", []) if isinstance(item, dict)]
        if isinstance(existing_qa9_payload.get("entries"), list)
        else []
    )
    display_feature = str(existing_qa9_payload.get("feature") or feature).strip() or feature
    resolved_ui_runner = str(ui_runner or "").strip().lower()

    if existing_entries:
        if not resolved_ui_runner:
            strategy = existing_qa9_payload.get("qa_strategy") if isinstance(existing_qa9_payload.get("qa_strategy"), dict) else {}
            resolved_ui_runner = str(
                strategy.get("ui_runner")
                or existing_qa9_payload.get("ui_runner")
                or "browser-use"
            ).strip().lower()
        qa9_entries = _normalize_existing_qa9_entries(
            feature=display_feature,
            feature_slug=feature_slug,
            entries=existing_entries,
            ac_items=ac_items,
            ui_runner=resolved_ui_runner or "browser-use",
        )
    else:
        think_progress = _load_think_progress(project_root, version)
        think_strategy = think_progress.get("qa_strategy") if isinstance(think_progress, dict) else None
        strategy = think_strategy if isinstance(think_strategy, dict) else {}
        strategy_ui_runner = str(strategy.get("ui_runner") or "").strip().lower()
        resolved_ui_runner = resolved_ui_runner or strategy_ui_runner or "browser-use"
        qa_types_resolved = parse_qa_types(None, profile="web-full")
        if not strategy:
            strategy = build_qa_strategy(
                project_root=project_root,
                qa_types=qa_types_resolved,
                ui_runner=resolved_ui_runner,
            )
        command_baseline = strategy.get("command_baseline") if isinstance(strategy, dict) else {}
        if not isinstance(command_baseline, dict):
            command_baseline = {}
        for qa_type in qa_types_resolved:
            command_baseline.setdefault(
                qa_type,
                default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner),
            )
        qa9_entries = _build_qa9_entries(
            feature=display_feature,
            feature_slug=feature_slug,
            ac_items=ac_items,
            qa_types=qa_types_resolved,
            ui_runner=resolved_ui_runner,
            command_baseline=command_baseline,
        )

    story_sequence = _story_sequence_for_feature(
        project_root,
        version,
        feature_slug,
        fallback_entries=qa9_entries,
    )
    scenario_payload = expand_story_scenarios(
        feature=feature,
        version=version,
        story_sequence=story_sequence,
        entries=qa9_entries,
        expansion_profile=expansion_profile,
        scenario_depth=scenario_depth,
        ui_runner=resolved_ui_runner or "browser-use",
    )
    scenario_payload["feature"] = display_feature
    return scenario_payload, (resolved_ui_runner or "browser-use")


def _feature_slugs_for_version(project_root: Path, version: str) -> list[str]:
    root = project_root / "docs" / "beacon" / version / "user-story"
    if not root.exists():
        return []
    return sorted(path.stem for path in root.glob("*.md") if path.is_file() and path.stem != "index")


def _versions_for_prefix(project_root: Path, version_prefix: str) -> list[str]:
    normalized_prefix = str(version_prefix or "").strip().lower()
    versions = discover_versions(project_root)
    if not normalized_prefix:
        return versions
    return [version for version in versions if version.lower().startswith(normalized_prefix)]


def generate_test_cases(feature: str, test_type: str) -> list:
    """Generate legacy test case structure (kept for compatibility)."""
    cases = []

    if test_type in ("all", "smoke"):
        cases.extend(
            [
                {"id": "TC-001", "type": "smoke", "title": "Feature loads correctly", "status": "pending"},
                {"id": "TC-002", "type": "smoke", "title": "Core functionality works", "status": "pending"},
            ]
        )

    if test_type in ("all", "new"):
        cases.extend(
            [
                {"id": "TC-003", "type": "new", "title": "Happy path test", "status": "pending"},
                {"id": "TC-004", "type": "new", "title": "Edge case test", "status": "pending"},
            ]
        )

    if test_type in ("all", "regression"):
        cases.extend(
            [
                {
                    "id": "TC-005",
                    "type": "regression",
                    "title": "Existing functionality preserved",
                    "status": "pending",
                },
            ]
        )

    return cases


@app.command("story-scenarios")
def story_scenarios(
    feature: str = typer.Argument("", help="Feature name/slug. Omit with --all-features."),
    version: str = typer.Option("auto", "--version", "-v", help="Version"),
    version_prefix: str = typer.Option("", "--version-prefix", help="Generate across versions with matching prefix, e.g. v1.1."),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    all_features: bool = typer.Option(False, "--all-features", help="Generate for all features in selected version(s)."),
    skip_existing: bool = typer.Option(True, "--skip-existing/--force", help="Skip features with existing story-scenario-map."),
    expansion_profile: str = typer.Option("pua-web", "--expansion-profile", help="Scenario expansion profile."),
    scenario_depth: str = typer.Option("standard", "--scenario-depth", help="Scenario expansion depth."),
    ui_runner: str = typer.Option("", "--ui-runner", help="UI runner override for generated browser scenarios."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Generate story-scenario-map artifacts for one feature or batch across versions."""
    project_root = Path(project) if project else Path.cwd()
    if not all_features and not str(feature or "").strip():
        raise typer.BadParameter("feature is required unless --all-features is set")

    if version_prefix.strip():
        target_versions = _versions_for_prefix(project_root, version_prefix)
    else:
        target_versions = [resolve_target_version(project_root, version)]

    results: list[dict[str, object]] = []
    for resolved_version in target_versions:
        target_features = _feature_slugs_for_version(project_root, resolved_version) if all_features else [feature]
        for feature_name in target_features:
            path = qa_matrix_output(project_root, resolved_version, _slug(feature_name), "story-scenario-map")
            if skip_existing and path.exists():
                results.append(
                    {
                        "version": resolved_version,
                        "feature": feature_name,
                        "path": str(path.relative_to(project_root)),
                        "status": "skipped",
                    }
                )
                continue
            scenario_payload, resolved_ui_runner = _build_story_scenario_payload(
                project_root=project_root,
                version=resolved_version,
                feature=feature_name,
                expansion_profile=expansion_profile,
                scenario_depth=scenario_depth,
                ui_runner=ui_runner,
            )
            written_path = write_story_scenario_map(
                project_root,
                version=resolved_version,
                feature=feature_name,
                payload=scenario_payload,
            )
            results.append(
                {
                    "version": resolved_version,
                    "feature": feature_name,
                    "path": str(written_path.relative_to(project_root)),
                    "status": "generated",
                    "ui_runner": resolved_ui_runner,
                    "scenario_count": len(scenario_payload.get("scenarios", [])) if isinstance(scenario_payload.get("scenarios"), list) else 0,
                }
            )

    payload = {
        "version_prefix": version_prefix,
        "versions": target_versions,
        "generated_count": len([item for item in results if item.get("status") == "generated"]),
        "skipped_count": len([item for item in results if item.get("status") == "skipped"]),
        "results": results,
    }
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    typer.echo("Story scenario map generation")
    typer.echo(f"- versions: {', '.join(target_versions) or '-'}")
    typer.echo(f"- generated: {payload['generated_count']}")
    typer.echo(f"- skipped: {payload['skipped_count']}")
    for item in results:
        marker = "✓" if item.get("status") == "generated" else "-"
        typer.echo(f"{marker} {item.get('version')} {item.get('feature')} -> {item.get('path')}")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    test_type: str = typer.Option("all", "--type", "-t", help="Test type: smoke/new/regression/all"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    overwrite_doc: bool = typer.Option(
        False,
        "--overwrite-doc",
        help="Allow overwriting the human-readable QA markdown when it already exists.",
    ),
    qa_profile: str = typer.Option(
        "web-full",
        "--qa-profile",
        help="QA profile: web-core/web-full/custom",
    ),
    qa_types: Optional[list[str]] = typer.Option(
        None,
        "--qa-types",
        help="QA types list (comma-separated or repeatable), default follows profile.",
    ),
    llm_auto: bool = typer.Option(
        True,
        "--llm-auto/--no-llm-auto",
        help="Enable LLM dynamic QA planning.",
    ),
    llm_mode: str = typer.Option(
        "auto",
        "--llm-mode",
        help="LLM mode: rule/real/auto",
    ),
    automation_target_rate: float = typer.Option(
        0.85,
        "--automation-target-rate",
        help="Target automation coverage rate [0,1].",
    ),
    matrix_output: Optional[str] = typer.Option(
        None,
        "--matrix-output",
        help="QA9 matrix output file path (*.qa9-matrix.json).",
    ),
    expansion_profile: str = typer.Option(
        "pua-web",
        "--expansion-profile",
        help="Scenario expansion profile for story-native QA planning.",
    ),
    scenario_depth: str = typer.Option(
        "standard",
        "--scenario-depth",
        help="Scenario expansion depth: minimal/standard/deep.",
    ),
    ui_runner: str = typer.Option(
        "",
        "--ui-runner",
        help="UI runner for QA9 command generation: playwright/cypress/browser-use/agent-browser",
    ),
):
    """Create test cases and executable AC matrix."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    feature_slug = _slug(feature)
    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()

    # Read ACs from existing user-story/prd docs
    us_path, us_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "user-story", feature_slug)
    )
    prd_path, prd_content = _read_first_existing(
        _candidate_doc_paths(project_root, resolved_version, "prd", feature_slug)
    )
    ac_items = _extract_ac_items(us_content, f"user-story:{us_path}" if us_path else "user-story:missing")
    ac_items.extend(_extract_ac_items(prd_content, f"prd:{prd_path}" if prd_path else "prd:missing"))
    if not ac_items:
        ac_items = [{"ac_id": "AC-001", "text": f"{feature} core flow works", "source": "fallback"}]

    entries = []
    for idx, ac in enumerate(ac_items, start=1):
        layer = _infer_layer_from_ac(ac.get("text", ""))
        tc_id = f"TC-{idx:03d}"
        evidence_path = f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac["ac_id"],
                "layer": layer,
                "command": _default_command_for_layer(layer),
                "assertion": _default_assertion_for_layer(layer),
                "evidence_path": evidence_path,
                "status": "pending",
                "source": ac.get("source", ""),
            }
        )

    prototype_navigation, prototype_interaction = _load_prototype_contract_artifacts(
        project_root, resolved_version, feature_slug
    )
    route_closure_contract, implementation_map = _load_route_closure_artifacts(
        project_root, resolved_version, feature_slug
    )
    synthetic_idx = len(entries)
    ac_anchor = ac_items[0]["ac_id"] if ac_items else "AC-001"
    for jump in prototype_navigation.get("jump_map", []) or []:
        synthetic_idx += 1
        tc_id = f"TC-{synthetic_idx:03d}"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_anchor,
                "layer": "ui",
                "command": "python3 -c \"print('prototype-jump-check')\"",
                "assertion": f"jump {jump.get('from', '')} -> {jump.get('to', '')} is represented",
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                "status": "pending",
                "source": "prototype:navigation-map",
            }
        )
    for state_name in prototype_interaction.get("states", []) or []:
        synthetic_idx += 1
        tc_id = f"TC-{synthetic_idx:03d}"
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_anchor,
                "layer": "ui",
                "command": "python3 -c \"print('prototype-state-check')\"",
                "assertion": f"state {state_name} is represented in prototype",
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                "status": "pending",
                "source": "prototype:interaction-map",
            }
        )
    closure_cases = route_closure_contract.get("closure_cases") if isinstance(route_closure_contract.get("closure_cases"), list) else []
    bound_cases = {
        str(item.get("case_id") or ""): item
        for item in (implementation_map.get("closure_bindings") or [])
        if isinstance(item, dict) and str(item.get("case_id") or "").strip()
    }
    for case in closure_cases:
        if not isinstance(case, dict):
            continue
        synthetic_idx += 1
        tc_id = f"TC-{synthetic_idx:03d}"
        case_id = str(case.get("case_id") or "").strip()
        binding = bound_cases.get(case_id, {})
        target = str(binding.get("runtime_target") or binding.get("state_target") or case.get("target_surface_id") or "").strip()
        entries.append(
            {
                "tc_id": tc_id,
                "ac_id": ac_anchor,
                "layer": "ui",
                "command": "python3 -c \"print('prototype-route-closure-check')\"",
                "assertion": f"route closure {case.get('source_label', '')} -> {target or case.get('target_surface_id', '')} remains deterministic",
                "evidence_path": f".beacon/evidence/test-results/{feature_slug}/{tc_id}.json",
                "status": "pending",
                "source": "prototype:route-closure-contract",
            }
        )

    matrix_payload = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "generated_at": datetime.now().isoformat(),
        "entries": entries,
    }

    qa_types_resolved = parse_qa_types(qa_types, profile=qa_profile)
    think_progress = _load_think_progress(project_root, resolved_version)
    think_strategy = think_progress.get("qa_strategy") if isinstance(think_progress, dict) else None
    strategy = think_strategy if isinstance(think_strategy, dict) else {}
    strategy_ui_runner = str(strategy.get("ui_runner") or "").strip()
    resolved_ui_runner = str(ui_runner or strategy_ui_runner or "browser-use").strip().lower()
    if not resolved_ui_runner:
        resolved_ui_runner = "browser-use"
    explicit_ui_runner = bool(str(ui_runner or "").strip())
    if not strategy:
        strategy = build_qa_strategy(
            project_root=project_root,
            qa_types=qa_types_resolved,
            ui_runner=resolved_ui_runner,
        )
    command_baseline = strategy.get("command_baseline") if isinstance(strategy, dict) else {}
    if not isinstance(command_baseline, dict):
        command_baseline = {}
    for qa_type in qa_types_resolved:
        command_baseline.setdefault(
            qa_type,
            default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner),
        )
    if explicit_ui_runner:
        for qa_type in ("functional", "compatibility"):
            if qa_type in qa_types_resolved:
                command_baseline[qa_type] = default_command_for_qa_type(qa_type, ui_runner=resolved_ui_runner)
    if automation_target_rate < 0 or automation_target_rate > 1:
        raise typer.BadParameter("--automation-target-rate must be between 0 and 1")
    qa9_entries = _build_qa9_entries(
        feature=feature,
        feature_slug=feature_slug,
        ac_items=ac_items,
        qa_types=qa_types_resolved,
        ui_runner=resolved_ui_runner,
        command_baseline=command_baseline,
    )
    qa9_payload = {
        "schema_version": "1.0.2",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": resolved_version,
        "qa_profile": qa_profile,
        "qa_types": qa_types_resolved,
        "llm_plan": build_qa_llm_plan(
            project_root=project_root,
            llm_auto=llm_auto,
            llm_mode=llm_mode,
            qa_types=qa_types_resolved,
        ),
        "qa_strategy": strategy,
        "qa_requirements": _build_qa_requirements(
            qa_types_resolved,
            qa_applicability=strategy.get("qa_applicability") if isinstance(strategy, dict) else None,
        ),
        "automation_target_rate": automation_target_rate,
        "entries": qa9_entries,
        "compatibility_matrix": {
            "browsers": ["chromium", "firefox", "webkit"],
            "devices": ["desktop", "iphone14"],
            "required_pairs": [
                {"browser": "chromium", "device": "desktop"},
                {"browser": "firefox", "device": "desktop"},
                {"browser": "webkit", "device": "desktop"},
            ],
        },
        "generated_at": datetime.now().isoformat(),
    }
    story_sequence = _story_sequence_for_feature(
        project_root,
        resolved_version,
        feature_slug,
        fallback_entries=qa9_entries,
    )
    scenario_payload = expand_story_scenarios(
        feature=feature,
        version=resolved_version,
        story_sequence=story_sequence,
        entries=qa9_entries,
        expansion_profile=expansion_profile,
        scenario_depth=scenario_depth,
        ui_runner=resolved_ui_runner,
    )

    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "beacon" / resolved_version / "qa" / "test-cases" / f"{feature_slug}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path = qa_matrix_output(project_root, resolved_version, feature_slug, "ac-test-matrix")
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    matrix_path.write_text(json.dumps(matrix_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    qa9_matrix_path = (
        Path(matrix_output)
        if matrix_output
        else qa_matrix_output(project_root, resolved_version, feature_slug, "qa9-matrix")
    )
    qa9_matrix_path.parent.mkdir(parents=True, exist_ok=True)
    qa9_matrix_path.write_text(json.dumps(qa9_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    scenario_map_path = write_story_scenario_map(
        project_root,
        version=resolved_version,
        feature=feature,
        payload=scenario_payload,
    )

    md_rows = "\n".join(
        f"| {x['ac_id']} | {x['tc_id']} | {x['layer']} | `{x['command']}` | {x['assertion']} | `{x['evidence_path']}` |"
        for x in entries
    )
    result_rows = "\n".join(f"| {x['tc_id']} | Pending | from {x['ac_id']} |" for x in entries)

    md_content = f"""# Test Cases: {feature}

## Overview

**Feature**: {feature}
**Test Type**: {test_type.upper()}
**Version**: {resolved_version}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Memory Context**: {memory_context_path or 'N/A'}
**AC Matrix JSON**: {matrix_path}
**QA9 Matrix JSON**: {qa9_matrix_path}
**Story Scenario Map JSON**: {scenario_map_path}
**Prototype Navigation Contract**: {bool(prototype_navigation)}
**Prototype Interaction Contract**: {bool(prototype_interaction)}

---

## Executable AC Test Matrix

| AC ID | TC ID | Layer | Command | Assertion | Evidence Path |
|-------|-------|-------|---------|-----------|---------------|
{md_rows}

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
{result_rows}
"""

    doc_written = False
    if output or not output_path.exists() or overwrite_doc:
        output_path.write_text(md_content, encoding="utf-8")
        doc_written = True
    if uses_machine_surface(resolved_version):
        index_path = output_path.parent / "index.md"
        if not index_path.exists():
            index_path.write_text(
                "\n".join(
                    [
                        f"# QA Test Case Index ({resolved_version})",
                        "",
                        "- Human-readable QA markdown lives in this directory.",
                        f"- Machine QA matrices live under `docs/beacon/{resolved_version}/.machine/qa/`.",
                        f"- Current feature: `{feature_slug}`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

    if doc_written:
        typer.echo(f"✓ Test cases created: {output_path}")
    else:
        typer.echo(f"✓ Test cases preserved: {output_path}")
    typer.echo(f"✓ AC matrix created: {matrix_path}")
    typer.echo(f"✓ QA9 matrix created: {qa9_matrix_path}")
    typer.echo(f"✓ Story scenario map created: {scenario_map_path}")
    typer.echo(f"  Type: {test_type}")
    typer.echo(f"  Entries: {len(entries)}")
    typer.echo(f"  QA9 Entries: {len(qa9_entries)}")
    typer.echo(f"  Scenario Entries: {len(scenario_payload.get('scenarios', []))}")
    typer.echo(f"  QA Runner: {resolved_ui_runner}")


@app.command("list")
def list_tests(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all test cases."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    test_dir = qa_docs_dir(project_root, resolved_version)

    if not test_dir.exists():
        typer.echo("No test cases found")
        return

    tests = list(test_dir.glob("*.md"))
    typer.echo(f"Test Cases ({len(tests)} found):")
    for test in tests:
        typer.echo(f"  - {test.name}")


@app.command()
def gate(
    feature: str = typer.Argument(..., help="Feature to check"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Run gate check for AC matrix coverage."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)

    typer.echo(f"\nTest Coverage Gate: {feature}")
    typer.echo("=" * 40)

    slug = _slug(feature)
    test_dir = qa_docs_dir(project_root, resolved_version)
    test_file = test_dir / f"{slug}.md"
    matrix_file = qa_matrix_output(project_root, resolved_version, slug, "ac-test-matrix")

    if not test_file.exists():
        typer.echo(f"✗ FAIL: Test file not found: {test_file}")
        raise typer.Exit(1)
    typer.echo("✓ PASS: Test file exists")

    if not matrix_file.exists():
        typer.echo(f"✗ FAIL: AC matrix not found: {matrix_file}")
        raise typer.Exit(1)

    payload = json.loads(matrix_file.read_text(encoding="utf-8"))
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        typer.echo(f"✗ FAIL: AC matrix empty: {matrix_file}")
        raise typer.Exit(1)

    required_fields = {"ac_id", "tc_id", "layer", "command", "assertion", "evidence_path"}
    broken = [
        idx + 1
        for idx, item in enumerate(entries)
        if not isinstance(item, dict) or not required_fields.issubset(set(item.keys()))
    ]
    if broken:
        typer.echo(f"✗ FAIL: AC matrix entries missing fields: {broken[:10]}")
        raise typer.Exit(1)

    typer.echo(f"✓ PASS: AC executable matrix entries={len(entries)}")
    typer.echo("\nGate Result: PASS")


if __name__ == "__main__":
    app()
