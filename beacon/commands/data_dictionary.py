"""Beacon data-dictionary command - Data dictionary generation"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="data-dictionary", help="Data dictionary")


@app.command()
def create(
    name: str = typer.Argument(..., help="Dictionary name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate data dictionary"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    dict_content = f"""# Data Dictionary: {name}

**Name**: {name}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Version**: 1.0.0

---

## Overview

Describe the purpose and scope of this data dictionary.

## Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUID | Yes | Auto | Unique identifier |
| name | String | Yes | - | Display name |
| description | String | No | - | Description text |
| status | Enum | Yes | active | Status: active/inactive/archived |
| created_at | DateTime | Yes | Auto | Creation timestamp |
| updated_at | DateTime | Yes | Auto | Last update timestamp |

## Relationships

| Relation | Type | Description |
|----------|------|-------------|
| - | - | TBD |

## Indexes

| Index | Fields | Unique |
|-------|--------|--------|
| primary | id | Yes |
| idx_name | name | No |

## Validation Rules

- name: 1-100 characters
- description: max 500 characters
- status: must be one of active, inactive, archived

## Notes

- Add any additional notes here

"""
    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "data-dictionary" / f"{name.lower()}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(dict_content)

    typer.echo(f"✓ Data dictionary created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List existing data dictionaries"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    dict_dir = project_root / "docs" / "product" / resolved_version / "data-dictionary"

    if not dict_dir.exists():
        typer.echo("No data dictionaries found")
        return

    dicts = list(dict_dir.glob("*.md"))
    typer.echo(f"Data Dictionaries ({len(dicts)} found):")
    for d in dicts:
        typer.echo(f"  - {d.stem}")


if __name__ == "__main__":
    app()
