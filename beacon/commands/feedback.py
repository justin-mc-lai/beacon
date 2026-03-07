"""Beacon feedback command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import typer

from beacon.utils.memory import append_memory_entry, load_memory_entries
from beacon.utils.runtime import load_run_state, newest_run_id, now_iso, write_json
from beacon.utils.workflow_memory import append_lifecycle_event, compute_workflow_progress

app = typer.Typer(name="feedback", help="Feedback operations")


def _resolve_target_run_id(root: Path, run_id: str) -> str:
    if run_id and run_id != "latest":
        return run_id
    return newest_run_id(root) or "latest"


def _feedback_candidates_path(root: Path, run_id: str) -> Path:
    return root / ".beacon" / "state" / "feedback-candidates" / f"{run_id}.json"


def _feedback_apply_report_path(root: Path, run_id: str) -> Path:
    return root / ".beacon" / "state" / "feedback-apply-report" / f"{run_id}.json"


def _normalize_override_items(value: Optional[list[str]]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _normalize_cli_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _debug_feedback_path(root: Path, run_id: str) -> Path:
    return root / ".beacon" / "state" / "debug-feedback" / f"{run_id}.jsonl"


def _collect_debug_feedback_candidates(root: Path, run_id: str) -> list[dict[str, Any]]:
    path = _debug_feedback_path(root, run_id)
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            events.append(payload)

    candidates: list[dict[str, Any]] = []
    for event in events:
        block_reason = str(event.get("block_reason", "")).strip()
        boundary_state = str(event.get("boundary_state", "")).strip()
        intent = str(event.get("intent", "")).strip()
        confidence = float(event.get("confidence", 0.0) or 0.0)
        recommended_command = str(event.get("recommended_command", "")).strip()
        source = str(event.get("source", "")).strip() or "debug"

        reason_codes: set[str] = set()
        if block_reason:
            for item in block_reason.split(","):
                code = item.strip()
                if code:
                    reason_codes.add(code)
        if boundary_state == "mixed_need_confirm":
            reason_codes.add("boundary_mixed_ambiguous")
        if boundary_state == "out_of_scope" or intent == "outside-boundary":
            reason_codes.add("outside_beacon_boundary")
        if confidence < 0.62:
            reason_codes.add("low-confidence")
        if not recommended_command and intent:
            reason_codes.add("missing_intent_mapping")

        for code in sorted(reason_codes):
            candidates.append(
                {
                    "type": "reason_code",
                    "reason_code": code,
                    "note": f"Debug attribution: {code} (source={source})",
                    "source": "debug",
                    "evidence_ref": [str(path.relative_to(root))],
                }
            )

    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for row in candidates:
        key = (str(row.get("reason_code", "")).strip(), str(row.get("note", "")).strip())
        if key[0]:
            dedup[key] = row
    return list(dedup.values())


def _collect_reason_codes(root: Path, run_id: str, source: str) -> list[str]:
    reason_codes: list[str] = []
    source_l = str(source or "all").strip().lower()

    if source_l in {"all", "gate"}:
        gate_report = root / ".beacon" / "gate-report.json"
        if gate_report.exists():
            try:
                gate_payload = json.loads(gate_report.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                gate_payload = {}
            issues = gate_payload.get("issues")
            if isinstance(issues, list):
                for issue in issues:
                    if not isinstance(issue, dict):
                        continue
                    code = str(issue.get("reason_code", "")).strip()
                    if code:
                        reason_codes.append(code)

    if source_l in {"all", "auto-test", "workflow"}:
        progress = compute_workflow_progress(root, run_id=run_id if run_id != "latest" else None)
        stage_map = progress.get("stages", {}) if isinstance(progress.get("stages"), dict) else {}
        for stage, payload in stage_map.items():
            if not isinstance(payload, dict):
                continue
            if str(payload.get("status", "")) == "failed":
                reason_codes.append(f"{stage}_failed")
        auto_test_path = root / ".beacon" / "auto-test-status.json"
        if auto_test_path.exists():
            try:
                auto_payload = json.loads(auto_test_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                auto_payload = {}
            status = str(auto_payload.get("status", "")).strip().lower()
            if status and status != "passed":
                reason_codes.append("verify_not_passed")

    if source_l in {"all", "manual"}:
        manual_feedback = root / ".beacon" / "state" / "requirement-feedback" / f"{run_id}.json"
        if manual_feedback.exists():
            try:
                manual_payload = json.loads(manual_feedback.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                manual_payload = {}
            rows = manual_payload.get("feedback")
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    code = str(row.get("reason_code", "")).strip()
                    if code:
                        reason_codes.append(code)

    if source_l in {"all", "debug"}:
        debug_candidates = _collect_debug_feedback_candidates(root, run_id)
        reason_codes.extend(
            [
                str(item.get("reason_code", "")).strip()
                for item in debug_candidates
                if isinstance(item, dict)
            ]
        )

    if not reason_codes:
        reason_codes = ["workflow_feedback_sync"]
    return sorted(set(reason_codes))


def _apply_feedback_candidates(
    *,
    root: Path,
    run_id: str,
    candidates: list[dict[str, Any]],
    source_name: str,
    mem_type: str,
) -> dict[str, Any]:
    existing = load_memory_entries(root)
    existing_by_code: dict[str, dict[str, Any]] = {}
    for row in existing:
        if not isinstance(row, dict):
            continue
        codes = row.get("reason_codes")
        if not isinstance(codes, list):
            continue
        for code in codes:
            code_key = str(code).strip()
            if code_key and code_key not in existing_by_code:
                existing_by_code[code_key] = row

    report_rows: list[dict[str, Any]] = []
    assimilated = 0
    out_candidates_path = _feedback_candidates_path(root, run_id)
    evidence_ref = [str(out_candidates_path.relative_to(root))]
    for row in candidates:
        if not isinstance(row, dict):
            continue
        code = str(row.get("reason_code", "")).strip()
        if not code:
            continue
        original_reason_code = str(row.get("original_reason_code", "")).strip()
        if not original_reason_code:
            original_reason_code = code
        note = str(row.get("note", "")).strip() or f"Auto feedback: {code}"
        override_trace = row.get("override_trace")
        if isinstance(override_trace, dict) and original_reason_code and original_reason_code != code:
            note = f"{note} (override: {original_reason_code} -> {code})"
        revision_of = None
        if code in existing_by_code:
            revision_of = str(existing_by_code[code].get("memory_id", "") or "") or None
        entry = append_memory_entry(
            project_root=root,
            mem_type=mem_type,
            text=f"[feedback:{run_id}] {note}",
            source_session_id=run_id,
            source=source_name,
            evidence_ref=evidence_ref,
            confidence=0.72,
            tags=["feedback", "workflow-loop", code],
            reason_codes=[code],
            revision_of=revision_of,
            upsert=True,
        )
        assimilated += 1
        report_rows.append(
            {
                "reason_code": code,
                "original_reason_code": original_reason_code,
                "memory_id": entry.get("memory_id"),
                "revision_of": revision_of,
                "override_trace": override_trace if isinstance(override_trace, dict) else None,
                "status": "upserted" if revision_of else "added",
            }
        )

    report_payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "source": source_name,
        "status": "ok",
        "applied_count": assimilated,
        "items": report_rows,
        "updated_at": now_iso(),
    }
    out_report = _feedback_apply_report_path(root, run_id)
    write_json(out_report, report_payload)

    append_lifecycle_event(
        root,
        run_id=run_id,
        stage="feedback",
        event="feedback_memory_assimilated",
        source=source_name,
        evidence_ref=[str(out_candidates_path.relative_to(root)), str(out_report.relative_to(root))],
        details={"count": assimilated},
    )
    return report_payload


@app.command()
def extract(
    run_id: str = typer.Argument("latest", help="Run ID"),
    source: str = typer.Option("all", "--source", help="feedback source: gate|auto-test|manual|debug|all"),
    override: Optional[list[str]] = typer.Option(
        None,
        "--override",
        help="Override reason code mapping old:new (repeatable).",
    ),
    note: str = typer.Option("", "--note", help="Optional note appended to extracted candidates."),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Extract feedback candidates from gate/auto-test/manual sources."""
    root = Path(project_root) if project_root else Path.cwd()
    target = _resolve_target_run_id(root, run_id)
    state = load_run_state(root, target) if target != "latest" else None
    reason_codes = _collect_reason_codes(root, target, source)
    candidates: list[dict[str, Any]] = [
        {
            "type": "reason_code",
            "reason_code": code,
            "note": f"Auto-synced feedback from lifecycle/gate: {code}",
        }
        for code in reason_codes
    ]
    if str(source or "").strip().lower() in {"all", "debug"}:
        candidates.extend(_collect_debug_feedback_candidates(root, target))

    override_map: dict[str, str] = {}
    for item in _normalize_override_items(override):
        raw = str(item or "").strip()
        if ":" not in raw:
            continue
        old_code, new_code = raw.split(":", 1)
        old_code = old_code.strip()
        new_code = new_code.strip()
        if old_code and new_code:
            override_map[old_code] = new_code
    normalized_rows: list[dict[str, Any]] = []
    for row in candidates:
        if not isinstance(row, dict):
            continue
        current_code = str(row.get("reason_code", "")).strip()
        if not current_code:
            continue
        cloned = dict(row)
        if current_code in override_map:
            new_code = override_map[current_code]
            cloned["original_reason_code"] = current_code
            cloned["reason_code"] = new_code
            cloned["override_trace"] = {
                "from": current_code,
                "to": new_code,
                "ts": now_iso(),
            }
        note_text = _normalize_cli_text(note)
        if note_text:
            previous_note = str(cloned.get("note", "")).strip()
            cloned["note"] = f"{previous_note} | {note_text}" if previous_note else note_text
        normalized_rows.append(cloned)

    dedup_by_code: dict[str, dict[str, Any]] = {}
    for row in normalized_rows:
        code = str(row.get("reason_code", "")).strip()
        if not code:
            continue
        dedup_by_code[code] = row
    normalized_rows = list(dedup_by_code.values())

    payload = {
        "schema_version": "1.0",
        "run_id": target,
        "status": (state or {}).get("status", "unknown"),
        "source": source,
        "updated_at": now_iso(),
        "feedback": normalized_rows,
        "override_count": len(override_map),
    }
    out = _feedback_candidates_path(root, target)
    write_json(out, payload)
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"✓ Feedback candidates extracted: {out}")
        typer.echo(f"  count: {len(normalized_rows)}")


@app.command()
def apply(
    run_id: str = typer.Argument("latest", help="Run ID"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
    candidates: str = typer.Option("", "--candidates", help="Explicit feedback-candidates path"),
    override: Optional[list[str]] = typer.Option(
        None,
        "--override",
        help="Override reason code mapping old:new (repeatable).",
    ),
    note: str = typer.Option("", "--note", help="Optional note appended to candidate rows."),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Apply extracted feedback candidates into memory with revision semantics."""
    root = Path(project_root) if project_root else Path.cwd()
    target = _resolve_target_run_id(root, run_id)
    path = Path(candidates) if candidates else _feedback_candidates_path(root, target)
    if not path.exists():
        typer.echo(f"Missing feedback candidates: {path}", err=True)
        raise typer.Exit(2)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = {}
    rows = payload.get("feedback")
    if not isinstance(rows, list):
        rows = []
    override_map: dict[str, str] = {}
    for item in _normalize_override_items(override):
        raw = str(item or "").strip()
        if ":" not in raw:
            continue
        old_code, new_code = raw.split(":", 1)
        old_code = old_code.strip()
        new_code = new_code.strip()
        if old_code and new_code:
            override_map[old_code] = new_code

    note_text = _normalize_cli_text(note)
    if override_map or note_text:
        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            cloned = dict(row)
            code = str(cloned.get("reason_code", "")).strip()
            if code in override_map:
                new_code = override_map[code]
                cloned["original_reason_code"] = code
                cloned["reason_code"] = new_code
                cloned["override_trace"] = {
                    "from": code,
                    "to": new_code,
                    "ts": now_iso(),
                    "source": "feedback.apply.override",
                }
            if note_text:
                prev_note = str(cloned.get("note", "")).strip()
                cloned["note"] = f"{prev_note} | {note_text}" if prev_note else note_text
            normalized_rows.append(cloned)
        rows = normalized_rows

    report = _apply_feedback_candidates(
        root=root,
        run_id=target,
        candidates=rows,
        source_name="feedback.apply",
        mem_type="feedback",
    )
    if json_output:
        typer.echo(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"✓ Feedback applied: {_feedback_apply_report_path(root, target)}")
        typer.echo(f"  applied_count: {report.get('applied_count', 0)}")


@app.command()
def sync(
    run_id: str = typer.Argument("latest", help="Run ID"),
    project_root: str = typer.Option("", "--project-root", help="Project root path"),
):
    """Sync test feedback to requirements (extract + apply compatibility path)."""
    root = Path(project_root) if project_root else Path.cwd()
    target = _resolve_target_run_id(root, run_id)

    extract(
        run_id=target,
        source="all",
        project_root=str(root),
        json_output=False,
    )
    path = _feedback_candidates_path(root, target)
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("feedback")
    if not isinstance(rows, list):
        rows = []

    report = _apply_feedback_candidates(
        root=root,
        run_id=target,
        candidates=rows,
        source_name="feedback.sync",
        mem_type="insight",
    )
    feedback_dir = root / ".beacon" / "state" / "requirement-feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        feedback_dir / f"{target}.json",
        {
            "run_id": target,
            "updated_at": now_iso(),
            "status": "synced",
            "feedback": rows,
        },
    )
    typer.echo(f"Syncing feedback for run: {target}")
    typer.echo(
        json.dumps(
            {
                "synced": str(feedback_dir / f"{target}.json"),
                "run_id": target,
                "memory_assimilated": report.get("applied_count", 0),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    app()
