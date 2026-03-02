"""Beacon user-story command - Generate user stories"""
import typer
from typing import Optional
import json
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="user-story", help="Generate user stories")


def generate_user_story(topic: str, project_root: Path) -> dict:
    """Generate user story structure"""
    output_dir = project_root / "docs" / "product" / "latest" / "user-story"
    output_dir.mkdir(parents=True, exist_ok=True)

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
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a user story"""
    project_root = Path(project) if project else Path.cwd()

    story = generate_user_story(feature, project_root)

    # Generate markdown
    md_content = f"""# User Story: {story['title']}

## Story

**As a** {story['as_a']},
**I want** {story['i_want']},
**So that** {story['so_that']}

## Acceptance Criteria

### Functionality
{chr(10).join(f"- [ ] {ac}" for ac in story['acceptance_criteria']['functionality']) or "- [ ] TBD"}

### Data
{chr(10).join(f"- [ ] {ac}" for ac in story['acceptance_criteria']['data']) or "- [ ] TBD"}

### User Experience
{chr(10).join(f"- [ ] {ac}" for ac in story['acceptance_criteria']['ux']) or "- [ ] TBD"}

### Performance
{chr(10).join(f"- [ ] {ac}" for ac in story['acceptance_criteria']['performance']) or "- [ ] TBD"}

### Security
{chr(10).join(f"- [ ] {ac}" for ac in story['acceptance_criteria']['security']) or "- [ ] TBD"}

## Metadata

| Field | Value |
|-------|-------|
| Priority | {story['priority']} |
| Story Points | {story['story_points']} |
| Status | {story['status']} |
| Created | {story['created_at']} |
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "user-story" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ User story created: {output_path}")
    return story


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all user stories"""
    project_root = Path(project) if project else Path.cwd()
    stories_dir = project_root / "docs" / "product" / "latest" / "user-story"

    if not stories_dir.exists():
        typer.echo("No user stories found")
        return

    stories = list(stories_dir.glob("*.md"))
    typer.echo(f"User Stories ({len(stories)} found):")
    for story in stories:
        typer.echo(f"  - {story.name}")


if __name__ == "__main__":
    app()
