"""Beacon remember command - Knowledge memory"""
import typer
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

app = typer.Typer(name="remember", help="Knowledge memory management")


MEMORY_FILE = "memory.json"


def get_memory_path(project_root: Path) -> Path:
    """Get memory file path"""
    return project_root / ".beacon" / MEMORY_FILE


def load_memory(project_root: Path) -> dict:
    """Load memory data"""
    memory_path = get_memory_path(project_root)
    if memory_path.exists():
        return json.loads(memory_path.read_text())
    return {"entries": []}


def save_memory(project_root: Path, memory: dict):
    """Save memory data"""
    memory_path = get_memory_path(project_root)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(memory, indent=2, ensure_ascii=False))


@app.command()
def add(
    content: str = typer.Argument(..., help="Memory content to add"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Tag for the memory"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Add a new memory"""
    project_root = Path(project) if project else Path.cwd()
    memory = load_memory(project_root)

    entry = {
        "id": len(memory["entries"]) + 1,
        "content": content,
        "tag": tag,
        "created_at": datetime.now().isoformat(),
    }

    memory["entries"].append(entry)
    save_memory(project_root, memory)

    typer.echo(f"✓ Memory added (ID: {entry['id']})")
    if tag:
        typer.echo(f"  Tag: {tag}")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
):
    """Search memories"""
    project_root = Path(project) if project else Path.cwd()
    memory = load_memory(project_root)

    if not memory["entries"]:
        typer.echo("No memories found")
        return

    # Search in content and tags
    query_lower = query.lower()
    results = [
        e for e in memory["entries"]
        if query_lower in e.get("content", "").lower() or
           (e.get("tag") and query_lower in e["tag"].lower())
    ]

    if not results:
        typer.echo(f"No results for '{query}'")
        return

    typer.echo(f"Found {len(results)} result(s):")
    for entry in results[:limit]:
        typer.echo(f"\n  ID: {entry['id']}")
        if entry.get("tag"):
            typer.echo(f"  Tag: {entry['tag']}")
        typer.echo(f"  Content: {entry['content'][:100]}...")
        typer.echo(f"  Created: {entry['created_at']}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List all memories"""
    project_root = Path(project) if project else Path.cwd()
    memory = load_memory(project_root)

    entries = memory["entries"]
    if tag:
        entries = [e for e in entries if e.get("tag") == tag]

    if not entries:
        typer.echo("No memories found")
        return

    typer.echo(f"Memories ({len(entries)} total):")
    for entry in entries:
        tag_str = f" [#{entry.get('tag')}]" if entry.get("tag") else ""
        typer.echo(f"  {entry['id']}. {entry['content'][:60]}...{tag_str}")


if __name__ == "__main__":
    app()
