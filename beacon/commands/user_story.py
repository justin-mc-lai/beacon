"""Beacon user-story command - Generate user stories"""
import typer
from typing import Optional
import json
from pathlib import Path
from datetime import datetime
import os

from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version
from beacon.utils.story_state import ensure_story_state
from beacon.utils.revision_state import load_revision_state

app = typer.Typer(name="user-story", help="Generate user stories")


def generate_user_story(topic: str, project_root: Path) -> dict:
    """Generate user story structure"""
    # User story template
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

    return story


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
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

    story = generate_user_story(feature, project_root)

    # Generate markdown
    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
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
| Memory Context | {memory_context_path or 'N/A'} |
"""

    slug = feature.lower().replace(' ', '-')
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)
    else:
        output_path = project_root / "docs" / "beacon" / resolved_version / "user-story" / f"{slug}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md_content)

    ensure_story_state(project_root, resolved_version, feature)
    load_revision_state(project_root, version=resolved_version, feature=feature, create_if_missing=True)

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
