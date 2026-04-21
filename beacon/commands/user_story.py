"""Beacon user-story command - Generate user stories"""
import typer
from typing import Optional
import json
from pathlib import Path
from datetime import datetime
import os

from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version
from beacon.utils.revision_state import load_revision_state
from beacon.utils.semantic_runtime import (
    build_mode_contract,
    build_semantic_capability_snapshot,
    load_host_response_json,
    normalize_requested_mode,
)
from beacon.utils.story_state import feature_slug, load_story_state, save_story_state, sync_story_state_from_docs

app = typer.Typer(name="user-story", help="Generate user stories")


def _coerce_story_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _extract_host_story_payload() -> dict:
    payload, _ = load_host_response_json("user-story")
    if not payload:
        return {}
    for candidate in (payload.get("story"), payload.get("payload"), payload):
        if isinstance(candidate, dict):
            return candidate
    return {}


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
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-user-story-compiler", "--model", help="Compiler model label for evidence"),
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
    fallback_reason = ""
    effective_mode = requested_mode
    semantic_payload: dict | None = None
    if requested_mode == "rule":
        effective_mode = "rule"
    elif bool(capability_snapshot.get("llm_disabled")):
        if requested_mode == "llm":
            typer.echo("LLM compile disabled by BEACON_USER_STORY_DISABLE_LLM.", err=True)
            raise typer.Exit(2)
        effective_mode = "rule"
        fallback_reason = "llm_disabled"
    elif bool(capability_snapshot.get("host_semantic_ready")):
        semantic_payload = _extract_host_story_payload()
        if semantic_payload:
            effective_mode = "host"
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
        fallback_reason = "llm_unavailable"

    story = generate_user_story(feature, project_root, semantic_payload=semantic_payload)

    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    compiler = build_mode_contract(
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        fallback_reason=fallback_reason,
        capability_snapshot=capability_snapshot,
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

    slug = feature_slug(feature)
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
    save_story_state(project_root, version=resolved_version, feature=feature, state=active_story)
    load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)

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
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
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


if __name__ == "__main__":
    app()
