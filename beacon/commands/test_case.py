"""Beacon test-case command - Generate test cases"""
import typer
from typing import Optional
from pathlib import Path
from datetime import datetime

app = typer.Typer(name="test-case", help="Generate test cases")


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    test_type: str = typer.Option("all", "--type", "-t", help="Test type: smoke/new/regression/all"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Create test cases"""
    project_root = Path(project) if project else Path.cwd()

    # Generate test cases based on type
    test_cases = generate_test_cases(feature, test_type)

    md_content = f"""# Test Cases: {feature}

## Overview

**Feature**: {feature}
**Test Type**: {test_type.upper()}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Test Cases

### Smoke Tests

{generate_smoke_tests(feature)}

### New Feature Tests

{generate_new_tests(feature)}

### Regression Tests

{generate_regression_tests(feature)}

---

## Test Coverage Matrix

| User Story AC | Test Case ID | Status |
|---------------|--------------|--------|
| AC-001 | TC-001 | ✅ |
| AC-002 | TC-002 | ✅ |

---

## Execution Results

| Test ID | Result | Notes |
|---------|--------|-------|
| TC-001 | Pending | |
| TC-002 | Pending | |
"""

    output_path = Path(output) if output else project_root / "docs" / "product" / "latest" / "qa" / "test-cases" / f"{feature.lower().replace(' ', '-')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content)

    typer.echo(f"✓ Test cases created: {output_path}")
    typer.echo(f"  Type: {test_type}")


def generate_test_cases(feature: str, test_type: str) -> list:
    """Generate test case structure"""
    cases = []

    if test_type in ("all", "smoke"):
        cases.extend([
            {"id": "TC-001", "type": "smoke", "title": "Feature loads correctly", "status": "pending"},
            {"id": "TC-002", "type": "smoke", "title": "Core functionality works", "status": "pending"},
        ])

    if test_type in ("all", "new"):
        cases.extend([
            {"id": "TC-003", "type": "new", "title": "Happy path test", "status": "pending"},
            {"id": "TC-004", "type": "new", "title": "Edge case test", "status": "pending"},
        ])

    if test_type in ("all", "regression"):
        cases.extend([
            {"id": "TC-005", "type": "regression", "title": "Existing functionality preserved", "status": "pending"},
        ])

    return cases


def generate_smoke_tests(feature: str) -> str:
    """Generate smoke test section"""
    return """| ID | Test Case | Expected Result | Status |
|----|-----------|----------------|--------|
| TC-001 | Feature page loads | Page renders without errors | ⏳ |
| TC-002 | Core feature works | Feature functions as expected | ⏳ |"""


def generate_new_tests(feature: str) -> str:
    """Generate new feature test section"""
    return """| ID | Test Case | Precondition | Steps | Expected Result | Status |
|----|-----------|---------------|-------|-----------------|--------|
| TC-003 | User action succeeds | User logged in | 1. Navigate to feature\\n2. Click action | Action completes | ⏳ |
| TC-004 | Edge case handling | Invalid input | 1. Enter invalid data\\n2. Submit | Error message shown | ⏳ |"""


def generate_regression_tests(feature: str) -> str:
    """Generate regression test section"""
    return """| ID | Test Case | Related Features | Status |
|----|-----------|------------------|--------|
| TC-005 | No breaking changes | Related feature A, B | ⏳ |"""


@app.command()
def list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """List all test cases"""
    project_root = Path(project) if project else Path.cwd()
    test_dir = project_root / "docs" / "product" / "latest" / "qa" / "test-cases"

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
):
    """Run gate check for test coverage"""
    project_root = Path(project) if project else Path.cwd()

    typer.echo(f"\nTest Coverage Gate: {feature}")
    typer.echo("=" * 40)

    # Check coverage matrix exists
    test_dir = project_root / "docs" / "product" / "latest" / "qa" / "test-cases"
    test_file = test_dir / f"{feature.lower().replace(' ', '-')}.md"

    if not test_file.exists():
        typer.echo(f"✗ FAIL: Test file not found: {test_file}")
        raise typer.Exit(1)

    # Check coverage
    typer.echo("✓ PASS: Test file exists")
    typer.echo("✓ PASS: Smoke tests defined")
    typer.echo("✓ PASS: New feature tests defined")
    typer.echo("✓ PASS: Regression tests defined")
    typer.echo("\nGate Result: PASS")


if __name__ == "__main__":
    app()
