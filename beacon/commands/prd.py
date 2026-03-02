"""Beacon prd command - Generate PRD"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="prd", help="Generate Product Requirements Document")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create a PRD"""
    project_root = Path(project) if project else Path.cwd()

    md_content = f"""# PRD: {feature}

## 1. Overview

### Background
[Describe the context and motivation]

### Goals
- Primary goal: [What we want to achieve]
- Secondary goals: [Additional objectives]

### Non-Goals
- What we are NOT addressing in this version

## 2. User Stories

| As a | I want to | So that |
|------|-----------|---------|
| User | [action] | [benefit] |

## 3. Functional Requirements

### 3.1 Core Features
- [ ] Feature 1
- [ ] Feature 2

### 3.2 User Interactions
[Describe user flows]

### 3.3 Data Requirements
- Input: [What data is needed]
- Output: [What data is produced]
- Storage: [Data persistence requirements]

## 4. Non-Functional Requirements

### Performance
- Response time: < 500ms
- Throughput: [X] requests/second

### Security
- Authentication: [Method]
- Authorization: [Role-based/Resource-based]

### Compatibility
- Web: Chrome, Firefox, Safari (latest 2 versions)
- Mobile: iOS 15+, Android 12+

## 5. Technical Design

### Architecture
[High-level architecture]

### API Design
[API endpoints if applicable]

### Data Model
[Database schema if applicable]

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | High | [Mitigation] |

## 7. Success Metrics

- Metric 1: [Definition]
- Metric 2: [Definition]

## 8. Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Design | 1 week | Spec |
| Development | 2 weeks | Code |
| Testing | 1 week | Tests |

---

**Created**: {datetime.now().strftime('%Y-%m-%d')}
**Version**: 1.0.0
**Status**: Draft
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "prd" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ PRD created: {output_path}")


@app.command("list")
def list_prds(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all PRDs"""
    project_root = Path(project) if project else Path.cwd()
    prds_dir = project_root / "docs" / "product" / "latest" / "prd"

    if not prds_dir.exists():
        typer.echo("No PRDs found")
        return

    prds = list(prds_dir.glob("*.md"))
    typer.echo(f"PRDs ({len(prds)} found):")
    for prd in prds:
        typer.echo(f"  - {prd.name}")


if __name__ == "__main__":
    app()
