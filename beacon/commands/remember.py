"""Beacon remember command - PTK-aligned memory envelope."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.memory import (
    append_memory_entry,
    export_legacy_projection,
    load_memory_entries,
    normalize_memory_type,
    search_memory_entries,
)

app = typer.Typer(name="remember", help="Knowledge memory management")


@app.command()
def add(
    content: str = typer.Argument(..., help="Memory content to add"),
    tag: list[str] = typer.Option([], "--tag", "-t", help="Tag for the memory (repeatable)"),
    memory_type: str = typer.Option(
        "insight",
        "--type",
        "-y",
        help="Memory type: insight/decision/vocabulary/feedback",
    ),
    source_session_id: str = typer.Option("manual", "--source-session-id", help="Source session id"),
    source: str = typer.Option("remember", "--source", help="Human-readable source"),
    evidence_ref: list[str] = typer.Option([], "--evidence-ref", help="Evidence reference (repeatable)"),
    confidence: float = typer.Option(0.8, "--confidence", min=0.0, max=1.0, help="Confidence [0,1]"),
    upsert: bool = typer.Option(
        False,
        "--upsert/--no-upsert",
        help="Upsert by content_hash + source_session_id + source",
    ),
    revision_of: str = typer.Option("", "--revision-of", help="Previous memory_id to supersede"),
    reason_code: list[str] = typer.Option([], "--reason-code", help="Reason code tag (repeatable)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
):
    """Add a memory entry with unified memory envelope metadata."""
    project_root = Path(project) if project else Path.cwd()
    try:
        normalized_type = normalize_memory_type(memory_type)
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)

    entry = append_memory_entry(
        project_root=project_root,
        mem_type=normalized_type,
        text=content,
        source_session_id=source_session_id,
        source=source,
        evidence_ref=evidence_ref,
        confidence=confidence,
        tags=tag,
        upsert=upsert,
        revision_of=revision_of or None,
        reason_codes=reason_code or None,
    )

    typer.echo("✓ Memory added")
    typer.echo(f"  memory_id: {entry['memory_id']}")
    typer.echo(f"  type: {entry['type']}")
    if entry.get("tags"):
        typer.echo(f"  tags: {', '.join(entry['tags'])}")


@app.command("export-legacy-projection")
def export_legacy_projection_command(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    compat_mode: bool = typer.Option(False, "--compat-mode", help="Explicitly admit legacy memory projection write"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Export current memory-v1 into legacy memory files through explicit compatibility admission."""
    project_root = Path(project) if project else Path.cwd()
    try:
        payload = export_legacy_projection(project_root, compat_mode=compat_mode)
    except PermissionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    typer.echo("✓ Legacy memory projection exported")
    typer.echo(f"  compat_id: {payload['compat_id']}")
    typer.echo(f"  exported_count: {payload['exported_count']}")


@app.command()
def search(
    query: str = typer.Argument("", help="Search query (empty means all)"),
    memory_type: str = typer.Option("", "--type", "-y", help="Filter: insight/decision/vocabulary"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
    mode: str = typer.Option(
        "hybrid",
        "--mode",
        help="Search mode: keyword|semantic|hybrid",
    ),
    layer: str = typer.Option(
        "detail",
        "--layer",
        help="Result layer: index|timeline|detail",
    ),
    ids: str = typer.Option("", "--ids", help="Comma-separated memory ids for detail recall"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Search memories with source/evidence/session context."""
    project_root = Path(project) if project else Path.cwd()
    normalized_type = None
    if memory_type:
        try:
            normalized_type = normalize_memory_type(memory_type)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=2)

    results = search_memory_entries(
        project_root=project_root,
        query=query,
        mem_type=normalized_type,
        limit=limit,
        mode=mode,
        layer=layer,
        ids=[x.strip() for x in ids.split(",") if x.strip()],
    )

    if json_output:
        typer.echo(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        typer.echo("No memories found")
        return

    typer.echo(f"Found {len(results)} result(s):")
    for entry in results:
        typer.echo(f"\n- {entry.get('memory_id', '<unknown>')} [{entry.get('type', 'unknown')}]")
        typer.echo(f"  content: {entry.get('content', '')[:160]}")
        typer.echo(f"  source_session_id: {entry.get('source_session_id', 'manual')}")
        typer.echo(f"  source: {entry.get('source', 'remember')}")
        typer.echo(f"  confidence: {entry.get('confidence', 0.0)}")
        refs = entry.get("evidence_ref", [])
        if isinstance(refs, list) and refs:
            typer.echo(f"  evidence_ref: {', '.join(str(x) for x in refs)}")


@app.command("list")
def _list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project root"),
    memory_type: str = typer.Option("", "--type", "-y", help="Filter by type"),
):
    """List all memories."""
    project_root = Path(project) if project else Path.cwd()
    normalized_type = None
    if memory_type:
        try:
            normalized_type = normalize_memory_type(memory_type)
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=2)

    entries = load_memory_entries(project_root=project_root, mem_type=normalized_type)
    if not entries:
        typer.echo("No memories found")
        return

    typer.echo(f"Memories ({len(entries)} total):")
    for entry in entries:
        tags = entry.get("tags", [])
        tag_text = f" [{', '.join(tags)}]" if isinstance(tags, list) and tags else ""
        typer.echo(f"- {entry.get('memory_id')} ({entry.get('type')}) {entry.get('content', '')[:60]}{tag_text}")


if __name__ == "__main__":
    app()
