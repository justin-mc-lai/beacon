"""Beacon api-design command - API design documentation"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

from beacon.utils.versioning import resolve_target_version

app = typer.Typer(name="api-design", help="API design documentation")


@app.command()
def create(
    name: str = typer.Argument(..., help="API endpoint name"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Generate API design document"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)

    api_doc = f"""# API Design: {name}

**Endpoint**: {method} /{name.lower().replace('_', '-')}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status**: Draft

---

## Overview

Describe the purpose of this API endpoint.

## Request

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | Bearer token |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| - | - | - | TBD |

### Body

```json
{{
  "field": "value"
}}
```

## Response

### Success (200)

```json
{{
  "success": true,
  "data": {{}}
}}
```

### Error (4xx/5xx)

```json
{{
  "success": false,
  "error": "Error message"
}}
```

## Validation Rules

- Field validation rules here

## Examples

### Request

```bash
curl -X {method} \\
  -H "Authorization: Bearer <token>" \\
  /api/{name.lower().replace('_', '-')}
```

### Response

```json
{{
  "success": true,
  "data": {{}}
}}
```

"""
    output_path = (
        Path(output)
        if output
        else project_root / "docs" / "product" / resolved_version / "api" / f"{name.lower()}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(api_doc)

    typer.echo(f"✓ API design created: {output_path}")


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List existing API designs"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, None)
    api_dir = project_root / "docs" / "product" / resolved_version / "api"

    if not api_dir.exists():
        typer.echo("No API designs found")
        return

    apis = list(api_dir.glob("*.md"))
    typer.echo(f"API Designs ({len(apis)} found):")
    for api in apis:
        typer.echo(f"  - {api.stem}")


if __name__ == "__main__":
    app()
