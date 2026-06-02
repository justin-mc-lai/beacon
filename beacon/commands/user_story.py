"""Beacon user-story command - Generate user stories"""
import typer
from typing import Optional
import json
import sys
from pathlib import Path
from datetime import datetime
import os

from beacon.utils.versioning import normalize_version, resolve_operational_docs_version, resolve_target_version
from beacon.utils.revision_state import load_revision_state
from beacon.utils.requirement_parsing import build_feature_ac_items, build_research_projection, extract_qa_case_rows
from beacon.utils.requirement_deepening import (
    requirement_deepening_supported,
    sync_requirement_deepening_artifacts,
)
from beacon.utils.semantic_runtime import (
    HOST_MODE_BRIDGE,
    HOST_MODE_RESPONSE,
    build_mode_contract,
    build_semantic_capability_snapshot,
    ensure_default_host_bridge_env,
    execute_host_bridge_command,
    host_dispatch_decision,
    load_host_response_json,
    normalize_requested_mode,
)
from beacon.utils.runtime import write_json
from beacon.utils.story_state import feature_slug, load_story_state, machine_story_path, save_story_state, sync_story_state_from_docs
from beacon.utils.truth_map import feature_package_authoritative, resolve_truth_read_refs

app = typer.Typer(name="user-story", help="Generate user stories")


def _research_truth_enabled(version: str) -> bool:
    normalized = normalize_version(version) or "v0.0.0"
    raw = normalized.lstrip("v")
    try:
        major, minor, patch = [int(part) for part in raw.split(".")]
    except Exception:  # noqa: BLE001
        return False
    return (major, minor, patch) >= (1, 3, 6)


def _coerce_story_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _merge_story_acceptance(base_story: dict, derived_story: dict) -> dict:
    merged = dict(base_story)
    merged_criteria = {
        key: _coerce_story_list((base_story.get("acceptance_criteria") or {}).get(key))
        for key in (base_story.get("acceptance_criteria") or {})
    }
    derived_criteria = derived_story.get("acceptance_criteria") if isinstance(derived_story.get("acceptance_criteria"), dict) else {}
    for key, current in merged_criteria.items():
        for item in _coerce_story_list(derived_criteria.get(key)):
            if item not in current:
                current.append(item)
        merged_criteria[key] = current
    merged["acceptance_criteria"] = merged_criteria
    if not any(merged_criteria.values()):
        merged["acceptance_criteria"] = dict(derived_criteria)
    if merged.get("as_a") == "user" and derived_story.get("as_a"):
        merged["as_a"] = derived_story.get("as_a")
    if merged.get("i_want") == f"to {str(merged.get('title') or '').lower()}" and derived_story.get("i_want"):
        merged["i_want"] = derived_story.get("i_want")
    if merged.get("so_that") == "I can achieve my goal" and derived_story.get("so_that"):
        merged["so_that"] = derived_story.get("so_that")
    merged["story_points"] = max(int(merged.get("story_points") or 0), int(derived_story.get("story_points") or 0), 3)
    if str(derived_story.get("priority") or "").strip().lower() == "high":
        merged["priority"] = "high"
    return merged


def _extract_host_story_payload() -> dict:
    payload, _ = load_host_response_json("user-story")
    if not payload:
        return {}
    for candidate in (payload.get("story"), payload.get("payload"), payload):
        if isinstance(candidate, dict):
            return candidate
    return {}


def _extract_host_story_payload_from_response_payload(payload: dict) -> dict:
    """Extract story dict from an already-parsed response-injection payload.

    v1.4.13: the response helper already parsed the JSON envelope; this walks
    the same candidate traversal as ``_extract_host_story_payload`` but
    accepts the dict directly so the dispatch site is explicit.
    """
    if not isinstance(payload, dict) or not payload:
        return {}
    for candidate in (payload.get("story"), payload.get("payload"), payload):
        if isinstance(candidate, dict):
            return candidate
    return {}


def _extract_host_story_payload_from_bridge_payload(payload: dict) -> dict:
    """Extract story dict from an already-parsed bridge-subprocess payload.

    v1.4.13: the bridge subprocess returns a dict with the same shape as a
    response injection envelope (``story`` / ``payload`` / top-level dict).
    We reuse the same traversal.
    """
    return _extract_host_story_payload_from_response_payload(payload)


def _load_bridge_payload(payload_json: str = "") -> dict:
    raw = str(payload_json or "").strip()
    if not raw:
        raw = sys.stdin.read().strip()
    if not raw:
        raise typer.BadParameter("bridge payload missing")
    try:
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"invalid bridge payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise typer.BadParameter("bridge payload must be a JSON object")
    return payload


def _build_story_host_bridge_request(feature: str, version: str, project_root: Path) -> dict:
    return {
        "schema_version": "1.0",
        "command_name": "user-story",
        "request_kind": "user-story-semantic-compile",
        "feature": feature,
        "version": version,
        "project_root": str(project_root),
    }


def _extract_host_story_payload_with_bridge(request_payload: dict) -> dict:
    payload, _ = execute_host_bridge_command("user-story", request_payload)
    for candidate in (
        payload.get("story") if isinstance(payload, dict) else None,
        payload.get("payload") if isinstance(payload, dict) else None,
        payload,
    ):
        if isinstance(candidate, dict):
            return candidate
    return _extract_host_story_payload()


@app.command("host-bridge", hidden=True)
def host_bridge(
    payload_json: str = typer.Argument("", help="Optional bridge request JSON; default reads stdin"),
):
    """Hidden host-native bridge endpoint for user-story semantic compile."""
    try:
        payload = _load_bridge_payload(payload_json)
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc
    if str(payload.get("request_kind") or "").strip() != "user-story-semantic-compile":
        typer.echo("unsupported user-story bridge request_kind", err=True)
        raise typer.Exit(2)
    bridge_project_root = Path(str(payload.get("project_root") or Path.cwd())).resolve()
    story = _generate_story_from_truth(
        str(payload.get("feature") or "").strip(),
        bridge_project_root,
        version=str(payload.get("version") or "auto").strip() or "auto",
    )
    typer.echo(json.dumps({"story": story, "model": "beacon-user-story-host-bridge"}, ensure_ascii=False))


def _read_requirement_truth(project_root: Path, version: str, feature: str) -> tuple[str, str, str, str]:
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    if feature_package_authoritative(resolved_version):
        refs = resolve_truth_read_refs(
            project_root,
            version=resolved_version,
            feature=slug,
            consumer="user-story",
        )["requirement_refs"]
        prd_path = project_root / refs["prd"]
        user_story_path = project_root / refs["user_story"]
        test_case_path = project_root / refs["test_case"]
    else:
        prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
        user_story_path = project_root / "docs" / "beacon" / resolved_version / "user-story" / f"{slug}.md"
        test_case_path = project_root / "docs" / "beacon" / resolved_version / "qa" / "test-cases" / f"{slug}.md"
    research_path = project_root / "docs" / "beacon" / resolved_version / "research" / f"{slug}.md"
    prd_text = prd_path.read_text(encoding="utf-8") if prd_path.exists() else ""
    user_story_text = user_story_path.read_text(encoding="utf-8") if user_story_path.exists() else ""
    test_case_text = test_case_path.read_text(encoding="utf-8") if test_case_path.exists() else ""
    research_text = research_path.read_text(encoding="utf-8") if research_path.exists() else ""
    return user_story_text, prd_text, test_case_text, research_text


def _keyword_bucket(text: str) -> str:
    lowered = str(text or "").lower()
    if any(token in lowered for token in ("性能", "并发", "latency", "timeout", "响应时间", "throughput")):
        return "performance"
    if any(token in lowered for token in ("安全", "权限", "auth", "token", "隐私", "风控")):
        return "security"
    if any(token in lowered for token in ("兼容", "ios", "android", "browser", "设备", "跨端")):
        return "compatibility"
    if any(token in lowered for token in ("异常", "错误", "失败", "恢复", "拦截", "重试")):
        return "error_handling"
    if any(token in lowered for token in ("页面", "交互", "按钮", "表单", "流程", "体验", "展示", "列表", "详情")):
        return "ux"
    if any(token in lowered for token in ("字段", "数据", "库存", "订单", "金额", "api", "接口", "同步")):
        return "data"
    return "functionality"


def _derive_story_actor(feature: str, prd_text: str, qa_text: str) -> str:
    corpus = f"{feature}\n{prd_text}\n{qa_text}".lower()
    if any(token in corpus for token in ("admin", "管理", "后台", "运营", "merchant", "seller")):
        return "operator"
    if any(token in corpus for token in ("顾客", "用户", "buyer", "customer", "shopper")):
        return "customer"
    return "user"


def _generate_story_from_truth(feature: str, project_root: Path, *, version: str) -> dict:
    story = generate_user_story(feature, project_root)
    user_story_text, prd_text, qa_text, research_text = _read_requirement_truth(project_root, version, feature)
    slug = feature_slug(feature)
    research_enabled = _research_truth_enabled(resolve_target_version(project_root, version))
    ac_items = build_feature_ac_items(
        user_story_content=user_story_text,
        prd_content=prd_text,
        qa_content=qa_text,
        research_content=research_text if research_enabled else "",
        user_story_source="user-story:host-bridge",
        prd_source="prd:host-bridge",
        qa_source="qa:test-cases:host-bridge",
        research_source=f"research:docs/beacon/{resolve_target_version(project_root, version)}/research/{slug}.md" if research_enabled else "research:missing",
    )
    qa_rows = extract_qa_case_rows(qa_text, "qa:test-cases:host-bridge")
    actor = _derive_story_actor(feature, prd_text, qa_text)
    story["as_a"] = actor
    story["i_want"] = f"to complete {feature.lower()}"
    story["so_that"] = "the frozen requirement flow can be executed and verified"
    criteria: dict[str, list[str]] = {key: [] for key in story["acceptance_criteria"]}
    for item in ac_items:
        text = str(item.get("text") or "").strip()
        bucket = _keyword_bucket(text)
        if text and text not in criteria[bucket]:
            criteria[bucket].append(text)
        for detail in item.get("details") or []:
            detail_text = str(detail or "").strip()
            if not detail_text:
                continue
            detail_bucket = _keyword_bucket(detail_text)
            if detail_text not in criteria[detail_bucket]:
                criteria[detail_bucket].append(detail_text)
    for row in qa_rows:
        expected = str(row.get("expected_result") or "").strip()
        if not expected:
            continue
        bucket = _keyword_bucket(expected)
        if expected not in criteria[bucket]:
            criteria[bucket].append(expected)
    story["acceptance_criteria"] = criteria
    story["story_points"] = max(3, min(8, len(ac_items) + (1 if qa_rows else 0)))
    if len(ac_items) >= 4 or len(qa_rows) >= 3:
        story["priority"] = "high"
    return story


def generate_user_story(topic: str, project_root: Path, *, semantic_payload: Optional[dict] = None) -> dict:
    """Generate user story structure"""
    story = {
        "title": topic,
        "as_a": "user",
        "i_want": f"to {topic.lower()}",
        "so_that": "I can achieve my goal",
        "acceptance_criteria": {
            "functionality": [],
            "data": [],
            "ux": [],
            "performance": [],
            "security": [],
            "compatibility": [],
            "error_handling": []
        },
        "story_points": 3,
        "priority": "medium",
        "status": "draft",
        "created_at": datetime.now().isoformat()
    }

    payload = semantic_payload if isinstance(semantic_payload, dict) else {}
    if payload:
        story["title"] = str(payload.get("title") or story["title"]).strip() or topic
        story["as_a"] = str(payload.get("as_a") or story["as_a"]).strip() or "user"
        story["i_want"] = str(payload.get("i_want") or story["i_want"]).strip() or story["i_want"]
        story["so_that"] = str(payload.get("so_that") or story["so_that"]).strip() or story["so_that"]
        story["story_points"] = int(payload.get("story_points") or story["story_points"])
        story["priority"] = str(payload.get("priority") or story["priority"]).strip() or story["priority"]
        story["status"] = str(payload.get("status") or story["status"]).strip() or story["status"]
        criteria = payload.get("acceptance_criteria")
        if isinstance(criteria, dict):
            for key in story["acceptance_criteria"]:
                story["acceptance_criteria"][key] = _coerce_story_list(criteria.get(key))

    return story


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-user-story-compiler", "--model", help="Compiler model label for evidence"),
    semantic: bool = typer.Option(False, "--semantic", help="Legacy compatibility flag for semantic compilation."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create a user story"""
    project_root = Path(project) if project else Path.cwd()
    try:
        resolved_version = resolve_operational_docs_version(
            project_root,
            version,
            command_name="user-story create",
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)

    try:
        requested_mode = normalize_requested_mode(mode)
    except ValueError:
        typer.echo("Invalid --mode. Use auto/llm/rule.", err=True)
        raise typer.Exit(2)
    capability_snapshot = build_semantic_capability_snapshot(
        "user-story",
        disable_env="BEACON_USER_STORY_DISABLE_LLM",
    )
    # v1.4.13: wire host bridge transport before capability snapshot
    # so that host_runtime_supported projects get the default bridge wired
    # up even when the user only sets BEACON_HOST_RUNTIME. Mirrors the
    # prd / test_case parity fix from issue #3.
    ensure_default_host_bridge_env("user-story", host_runtime=capability_snapshot.get("host_runtime"))
    capability_snapshot = build_semantic_capability_snapshot(
        "user-story",
        disable_env="BEACON_USER_STORY_DISABLE_LLM",
    )
    slug = feature_slug(feature)
    fallback_reason = ""
    effective_mode = requested_mode
    semantic_payload: dict | None = None
    fallback_semantic_payload: dict | None = {"track": "main", "family": "tooling_surface"} if semantic else None
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
    if not prd_path.exists():
        typer.echo(f"Missing PRD truth for {feature}: {prd_path}")
        raise typer.Exit(2)
    if requested_mode == "rule":
        effective_mode = "rule"
    elif bool(capability_snapshot.get("llm_disabled")):
        if requested_mode == "llm":
            typer.echo("LLM compile disabled by BEACON_USER_STORY_DISABLE_LLM.", err=True)
            raise typer.Exit(2)
        effective_mode = "rule"
        fallback_reason = "llm_disabled"
    elif bool(capability_snapshot.get("host_semantic_ready")):
        # v1.4.13: response injection wins over bridge subprocess.
        decision = host_dispatch_decision(
            "user-story",
            request_payload=_build_story_host_bridge_request(feature, resolved_version, project_root),
            capability_snapshot=capability_snapshot,
        )
        if decision["response_used"] and decision["response_payload"]:
            semantic_payload = _extract_host_story_payload_from_response_payload(
                decision["response_payload"]
            )
            if semantic_payload:
                effective_mode = HOST_MODE_RESPONSE
            else:
                # Response was injected but didn't carry a parseable story;
                # treat as a host compile failure (don't silently fall through
                # to the bridge subprocess, which would shadow the response).
                if requested_mode == "llm":
                    typer.echo("User story semantic compile requires host semantic response.", err=True)
                    raise typer.Exit(2)
                effective_mode = "rule"
                fallback_reason = "host_compile_failed"
        elif decision["mode"] == HOST_MODE_BRIDGE and decision["bridge_payload"]:
            semantic_payload = _extract_host_story_payload_from_bridge_payload(
                decision["bridge_payload"]
            )
            if semantic_payload:
                effective_mode = HOST_MODE_BRIDGE
            elif requested_mode == "llm":
                typer.echo("User story semantic compile requires host semantic response.", err=True)
                raise typer.Exit(2)
            else:
                effective_mode = "rule"
                fallback_reason = "host_compile_failed"
        else:
            if requested_mode == "llm":
                typer.echo("User story semantic compile requires host semantic response.", err=True)
                raise typer.Exit(2)
            effective_mode = "rule"
            fallback_reason = "host_compile_failed"
        # Record response_used flag back into the snapshot for downstream contract.
        response_used = bool(decision.get("response_used"))
        capability_snapshot = {**capability_snapshot, "response_used": response_used}
    else:
        effective_mode = "rule"
        fallback_reason = "llm_unavailable"
        if semantic and fallback_semantic_payload:
            semantic_payload = dict(fallback_semantic_payload)
    # v1.4.13: track generator_mode so downstream machine mirrors see it
    # consistently with prd / test_case.
    generator_mode = effective_mode

    user_story_text, prd_text, qa_text, research_text = _read_requirement_truth(project_root, resolved_version, feature)
    story = generate_user_story(feature, project_root, semantic_payload=semantic_payload)
    truth_story = _generate_story_from_truth(feature, project_root, version=resolved_version)
    story = _merge_story_acceptance(story, truth_story)
    research_projection = build_research_projection(
        research_content=research_text,
        research_source=f"research:docs/beacon/{resolved_version}/research/{slug}.md",
        feature=feature,
        version=resolved_version,
    )

    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    compiler = build_mode_contract(
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        fallback_reason=fallback_reason,
        capability_snapshot=capability_snapshot,
    )
    deepening_payload: dict = {}
    if requirement_deepening_supported(resolved_version):
        truth_refs = resolve_truth_read_refs(
            project_root,
            version=resolved_version,
            feature=slug,
            consumer="user-story",
        )["requirement_refs"] if feature_package_authoritative(resolved_version) else {
            "prd": f"docs/beacon/{resolved_version}/prd/{slug}.md",
            "user_story": f"docs/beacon/{resolved_version}/user-story/{slug}.md",
            "test_case": f"docs/beacon/{resolved_version}/qa/test-cases/{slug}.md",
        }
        deepening_payload = sync_requirement_deepening_artifacts(
            project_root,
            version=resolved_version,
            feature=feature,
            prd_content=prd_text,
            user_story_content=user_story_text,
            qa_content=qa_text,
            research_content=research_text,
            prd_source=f"prd:{truth_refs['prd']}",
            user_story_source=f"user-story:{truth_refs['user_story']}",
            qa_source=f"qa:test-cases:{truth_refs['test_case']}",
            research_source=f"research:docs/beacon/{resolved_version}/research/{slug}.md",
            compiler=compiler,
            target_artifact="user-story",
        )
    md_content = f"""# User Story: {story['title']}

## Story

**As a** {story['as_a']},
**I want** {story['i_want']},
**So that** {story['so_that']}

## Acceptance Criteria

- [ ] AC-001 正向流程: {chr(10).join(story['acceptance_criteria']['functionality']) or "TBD"}
- [ ] AC-002 数据要求: {chr(10).join(story['acceptance_criteria']['data']) or "TBD"}
- [ ] AC-003 用户体验: {chr(10).join(story['acceptance_criteria']['ux']) or "TBD"}
- [ ] AC-004 性能要求: {chr(10).join(story['acceptance_criteria']['performance']) or "TBD"}
- [ ] AC-005 安全要求: {chr(10).join(story['acceptance_criteria']['security']) or "TBD"}
- [ ] AC-006 兼容性: {chr(10).join(story['acceptance_criteria']['compatibility']) or "TBD"}
- [ ] AC-007 错误处理: {chr(10).join(story['acceptance_criteria']['error_handling']) or "TBD"}

## Metadata

| Field | Value |
|-------|-------|
| Priority | {story['priority']} |
| Story Points | {story['story_points']} |
| Status | {story['status']} |
| Created | {story['created_at']} |
| Requested Mode | {compiler['requested_mode']} |
| Effective Mode | {compiler['effective_mode']} |
| Fallback Reason | {compiler['fallback_reason'] or 'N/A'} |
| Memory Context | {memory_context_path or 'N/A'} |
"""
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)
    else:
        output_path = project_root / "docs" / "beacon" / resolved_version / "user-story" / f"{slug}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)

    sync_story_state_from_docs(project_root, resolved_version, feature)
    active_story = load_story_state(project_root, version=resolved_version, feature=feature, create_if_missing=True) or {}
    active_story.update(
        {
            "title": story["title"],
            "priority": story["priority"],
            "status": story["status"],
            "compiler": {
                **compiler,
                "model": model,
            },
        }
    )
    if deepening_payload:
        handoff = deepening_payload.get("human_loop_handoff") if isinstance(deepening_payload.get("human_loop_handoff"), dict) else {}
        active_story["supplement_contract"] = {
            "allowed_decisions": ["accepted", "rejected", "deferred"],
            "required_machine_trail": True,
            "writeback_required": True,
        }
        active_story["story_candidates"] = list(deepening_payload.get("story_candidates") or [])
        active_story["requirement_deepening_refs"] = dict(deepening_payload.get("paths") or {})
        active_story["requirement_completeness_verdict"] = str(
            (deepening_payload.get("completeness") or {}).get("completeness_verdict") or ""
        )
        active_story["supplement_focus_areas"] = [str(item).strip() for item in (handoff.get("focus_areas") or []) if str(item).strip()]
        active_story["supplement_recommended_command"] = str(handoff.get("recommended_command") or "")
        active_story["supplement_next_action"] = str(handoff.get("action") or "")
        active_story["supplement_task"] = dict(deepening_payload.get("supplement_task") or {})
        active_story["re_freeze_transaction"] = dict(deepening_payload.get("re_freeze_transaction") or {})
    active_story["research_projection"] = research_projection
    save_story_state(project_root, version=resolved_version, feature=feature, state=active_story)
    load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)
    machine_path = machine_story_path(project_root, resolved_version, feature)
    machine_payload = {}
    if machine_path.exists():
        try:
            machine_payload = json.loads(machine_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            machine_payload = {}
    if not isinstance(machine_payload, dict):
        machine_payload = {}
    machine_payload.update(
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "acceptance_criteria": story["acceptance_criteria"],
            "semantic_payload": semantic_payload or fallback_semantic_payload or {},
            "compiler": compiler,
            "output_path": str(output_path),
            "research_projection": research_projection,
        }
    )
    write_json(machine_path, machine_payload)

    legacy_story_json = project_root / ".beacon" / "user-story" / f"{slug}.json"
    write_json(
        legacy_story_json,
        {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "acceptance_criteria": story["acceptance_criteria"],
            "semantic_payload": semantic_payload or fallback_semantic_payload or {},
            "compiler": compiler,
            "output_path": str(output_path),
            "research_projection": research_projection,
        },
    )

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "status": "ok",
                    "feature": feature,
                    "feature_slug": slug,
                    "version": resolved_version,
                    "model": model,
                    **compiler,
                    "output_path": str(output_path),
                    "requirement_deepening": {
                        "enabled": bool(deepening_payload),
                        "paths": deepening_payload.get("paths", {}),
                        "story_candidate_count": len(deepening_payload.get("story_candidates", []) or []),
                        "completeness_verdict": (deepening_payload.get("completeness") or {}).get("completeness_verdict", ""),
                    },
                    "supplement_focus_areas": [
                        str(item).strip()
                        for item in ((deepening_payload.get("human_loop_handoff") or {}).get("focus_areas") or [])
                        if str(item).strip()
                    ],
                    "supplement_recommended_command": str((deepening_payload.get("human_loop_handoff") or {}).get("recommended_command") or ""),
                    "supplement_task": deepening_payload.get("supplement_task", {}),
                    "re_freeze_transaction": deepening_payload.get("re_freeze_transaction", {}),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return story
    typer.echo(f"✓ User story created: {output_path}")
    return story


@app.command("list")
def list_stories(
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all user stories"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    roots = [project_root / "docs" / "beacon" / resolved_version / "user-story"]
    stories = []
    for stories_dir in roots:
        if stories_dir.exists():
            stories.extend(stories_dir.glob("*.md"))
    if not stories:
        typer.echo("No user stories found")
        return
    # de-duplicate by filename
    unique = {p.name: p for p in stories}
    typer.echo(f"User Stories ({len(unique)} found):")
    for story in sorted(unique.values(), key=lambda p: p.name):
        typer.echo(f"  - {story.name}")


@app.command("sync-state")
def sync_state(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "--project-root", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Sync story state from docs."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    sync_story_state_from_docs(project_root, resolved_version, feature)
    typer.echo(f"✓ User story state synced: {feature}")


if __name__ == "__main__":
    app()
