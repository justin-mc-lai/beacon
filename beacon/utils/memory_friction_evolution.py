"""Memory/Friction evolution toolkit utilities for v1.3.3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from beacon.utils.archive_governance import load_archive_read_model
from beacon.utils.lighthouse import generate_lighthouse_artifact
from beacon.utils.memory import append_memory_entry, load_memory_entries
from beacon.utils.runtime import now_iso, read_json, utc_compact_ts, write_json
from beacon.utils.versioning import resolve_target_version

SUPPORTED_MFE_MODES: tuple[str, ...] = ("memory", "friction", "both")
MFE_TOOL = "beacon-memory-friction-evolution"


def _analysis_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "analysis"


def _state_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "memory-friction-evolution"


def _latest_state_path(project_root: Path) -> Path:
    return _state_dir(project_root) / "latest.json"


def _trim(value: str, *, limit: int = 140) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _candidate_id(category: str, summary: str) -> str:
    digest = hashlib.sha256(f"{category}::{summary}".encode("utf-8")).hexdigest()[:12]
    return f"{category}:{digest}"


def _recommendation(*, score: int, recurrence: int) -> str:
    if score >= 75 or recurrence >= 3:
        return "keep"
    if score >= 45 or recurrence == 2:
        return "review"
    return "discard"


def _merge_candidate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for item in rows:
        candidate_id = str(item.get("candidate_id") or "").strip()
        if not candidate_id:
            continue
        if candidate_id not in merged:
            merged[candidate_id] = {
                **item,
                "evidence_refs": sorted(
                    {
                        str(ref).strip()
                        for ref in (item.get("evidence_refs") or [])
                        if str(ref).strip()
                    }
                ),
            }
            continue
        current = merged[candidate_id]
        current["score"] = max(int(current.get("score") or 0), int(item.get("score") or 0))
        current["recurrence_count"] = max(
            int(current.get("recurrence_count") or 1),
            int(item.get("recurrence_count") or 1),
        )
        refs = {
            str(ref).strip()
            for ref in (current.get("evidence_refs") or [])
            if str(ref).strip()
        }
        refs.update(
            {
                str(ref).strip()
                for ref in (item.get("evidence_refs") or [])
                if str(ref).strip()
            }
        )
        current["evidence_refs"] = sorted(refs)
        if len(str(item.get("friction_summary") or "").strip()) > len(str(current.get("friction_summary") or "").strip()):
            current["friction_summary"] = str(item.get("friction_summary") or "").strip()

    out = list(merged.values())
    out.sort(
        key=lambda row: (
            -int(row.get("score") or 0),
            -int(row.get("recurrence_count") or 0),
            str(row.get("candidate_id") or ""),
        )
    )
    return out


def _memory_candidates(project_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows = load_memory_entries(project_root)
    candidates: list[dict[str, Any]] = []
    evidence_refs: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        content = str(row.get("content") or "").strip()
        if not content:
            continue
        reason_codes = [
            str(code).strip()
            for code in (row.get("reason_codes") or [])
            if str(code).strip()
        ]
        category = reason_codes[0] if reason_codes else f"memory-{str(row.get('type') or 'signal').strip()}"
        summary = _trim(content, limit=120)
        refs = [str(ref).strip() for ref in (row.get("evidence_ref") or []) if str(ref).strip()]
        if refs:
            evidence_refs.extend(refs)
        score = int(max(1.0, min(100.0, float(row.get("confidence", 0.5) or 0.5) * 100.0)))
        recurrence = max(1, len(reason_codes))
        recommended = (
            f'beacon recall search "{category}" --type feedback --mode hybrid --project . --limit 5'
            if reason_codes
            else "beacon recall search --type feedback --mode hybrid --project . --limit 5"
        )
        candidates.append(
            {
                "candidate_id": _candidate_id("memory", f"{category}:{summary}"),
                "category": "memory_signal",
                "friction_summary": summary,
                "evidence_refs": refs,
                "score": score,
                "recurrence_count": recurrence,
                "recommendation": _recommendation(score=score, recurrence=recurrence),
                "recommended_command": recommended,
            }
        )
    return _merge_candidate_rows(candidates), sorted(set(evidence_refs))


def _friction_candidates_from_issues(project_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    issues_root = project_root / ".beacon" / "debug" / "issues"
    candidates: list[dict[str, Any]] = []
    refs: list[str] = []
    for path in sorted(issues_root.glob("*.json")) if issues_root.exists() else []:
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        reason_code = str(payload.get("reason_code") or path.stem).strip()
        count = int(payload.get("count") or 1)
        summary = _trim(str(payload.get("sample") or reason_code), limit=120)
        rel = str(path.relative_to(project_root))
        refs.append(rel)
        score = max(20, min(100, 30 + count * 15))
        candidates.append(
            {
                "candidate_id": _candidate_id("friction", reason_code),
                "category": "debug_policy",
                "friction_summary": summary,
                "evidence_refs": [rel],
                "score": score,
                "recurrence_count": max(1, count),
                "recommendation": _recommendation(score=score, recurrence=max(1, count)),
                "recommended_command": f'beacon debug project-feed "{reason_code}" --project-root . --json',
            }
        )
    return _merge_candidate_rows(candidates), sorted(set(refs))


def _lighthouse_mode(target: str) -> str:
    return "feature-slice" if str(target or "").strip() else "system-architecture-map"


def _render_markdown(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    decision = payload.get("decision") if isinstance(payload.get("decision"), dict) else {}
    inputs = payload.get("inputs") if isinstance(payload.get("inputs"), dict) else {}
    turns = payload.get("turns") if isinstance(payload.get("turns"), list) else []
    lines = [
        "# Memory/Friction Evolution Report",
        "",
        f"- run_id: `{payload.get('run_id', '')}`",
        f"- docs_version: `{payload.get('docs_version', '')}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- generated_at: `{payload.get('generated_at', '')}`",
        f"- max_turns: `{payload.get('max_turns', 0)}`",
        "",
        "## Inputs",
        f"- memory_refs: `{len(inputs.get('memory_refs', []))}`",
        f"- debug_refs: `{len(inputs.get('debug_refs', []))}`",
        f"- lighthouse_ref: `{inputs.get('lighthouse_ref', '')}`",
        "",
        "## Turn Decisions",
    ]
    if not turns:
        lines.append("- none")
    else:
        for turn in turns:
            if not isinstance(turn, dict):
                continue
            lines.append(
                "- "
                f"turn={turn.get('turn')} "
                f"candidates={turn.get('candidates_considered')} "
                f"should_exit={turn.get('should_exit')}"
            )
    lines.extend(["", "## Top Candidates"])
    if not candidates:
        lines.append("- none")
    else:
        for item in candidates:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"`{item.get('candidate_id', '')}` "
                f"[{item.get('recommendation', '')}] "
                f"score={item.get('score', 0)} "
                f"summary={item.get('friction_summary', '')}"
            )
            lines.append(f"  - command: `{item.get('recommended_command', '')}`")
            refs = item.get("evidence_refs") if isinstance(item.get("evidence_refs"), list) else []
            lines.append(f"  - evidence_refs: {', '.join(f'`{ref}`' for ref in refs) if refs else 'none'}")
    lines.extend(
        [
            "",
            "## Final Decision",
            f"- should_exit: `{decision.get('should_exit', True)}`",
            f"- next_prompt: `{decision.get('next_prompt', '')}`",
            "",
        ]
    )
    return "\n".join(lines)


def run_memory_friction_evolution(
    project_root: Path,
    *,
    version: str,
    mode: str,
    top_n: int = 5,
    max_turns: int = 3,
    with_lighthouse: bool = False,
    lighthouse_target: str = "",
    writeback: bool = False,
) -> dict[str, Any]:
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode not in SUPPORTED_MFE_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    if int(max_turns) < 1:
        raise ValueError("--max-turns must be >= 1")
    if int(top_n) < 1:
        raise ValueError("--top-n must be >= 1")

    resolved_version = resolve_target_version(project_root, version)
    run_id = f"mfe-{utc_compact_ts()}"
    generated_at = now_iso()
    archive_boundary = load_archive_read_model(project_root, version=resolved_version)

    memory_candidates: list[dict[str, Any]] = []
    memory_refs: list[str] = []
    friction_candidates: list[dict[str, Any]] = []
    friction_refs: list[str] = []
    if normalized_mode in {"memory", "both"}:
        memory_candidates, memory_refs = _memory_candidates(project_root)
    if normalized_mode in {"friction", "both"}:
        friction_candidates, friction_refs = _friction_candidates_from_issues(project_root)

    candidates = _merge_candidate_rows([*memory_candidates, *friction_candidates])
    turns: list[dict[str, Any]] = []
    working = list(candidates)
    limit = int(top_n)
    guard = int(max_turns)
    for turn in range(1, guard + 1):
        should_exit = len(working) <= limit or turn >= guard
        turns.append(
            {
                "turn": turn,
                "candidates_considered": len(working),
                "should_exit": should_exit,
                "recommended_command": str((working[0] if working else {}).get("recommended_command") or ""),
            }
        )
        if should_exit:
            break
        # Deterministic convergence: trim low-score tail before next turn.
        working = working[: max(limit, len(working) - 1)]

    final_candidates = working[:limit]
    decision = {
        "next_prompt": str((final_candidates[0] if final_candidates else {}).get("recommended_command") or "beacon debug harvest --project-root . --json"),
        "should_exit": True,
    }

    lighthouse_ref = ""
    if with_lighthouse:
        lighthouse_payload = generate_lighthouse_artifact(
            project_root,
            target=lighthouse_target or None,
            mode=_lighthouse_mode(lighthouse_target),
            version=resolved_version,
            output_path=str(_analysis_dir(project_root) / f"memory-friction-evolution-{run_id}-lighthouse.md"),
            write_versioned_output=False,
        )
        lighthouse_ref = str(Path(str(lighthouse_payload.get("output_path", ""))).relative_to(project_root))

    writeback_entries: list[str] = []
    if writeback:
        for row in final_candidates:
            if str(row.get("recommendation") or "") not in {"keep", "review"}:
                continue
            refs = [str(ref).strip() for ref in (row.get("evidence_refs") or []) if str(ref).strip()]
            if lighthouse_ref:
                refs.append(lighthouse_ref)
            entry = append_memory_entry(
                project_root=project_root,
                mem_type="feedback",
                text=(
                    f"[memory-friction-evolution] {row.get('friction_summary', '')} | "
                    f"recommendation={row.get('recommendation', '')} | "
                    f"command={row.get('recommended_command', '')}"
                ),
                source_session_id=run_id,
                source="memory-friction-evolution.writeback",
                evidence_ref=sorted(set(refs)),
                confidence=max(0.1, min(1.0, float(row.get("score", 0)) / 100.0)),
                tags=["memory-friction-evolution", str(row.get("category") or "")],
                reason_codes=[str(row.get("category") or "memory-friction-evolution")],
                upsert=True,
            )
            writeback_entries.append(str(entry.get("memory_id") or ""))

    payload = {
        "schema_version": "1.0",
        "tool": MFE_TOOL,
        "run_id": run_id,
        "docs_version": resolved_version,
        "mode": normalized_mode,
        "generated_at": generated_at,
        "max_turns": guard,
        "turns": turns,
        "inputs": {
            "memory_refs": memory_refs,
            "debug_refs": friction_refs,
            "lighthouse_ref": lighthouse_ref,
            "archive_plan_ref": str((archive_boundary.get("plan") or {}).get("current_version_truth_root", "") or ""),
            "archive_excluded_ref_count": len((archive_boundary.get("plan") or {}).get("excluded_from_current_delivery_refs", []))
            if isinstance(archive_boundary.get("plan"), dict)
            else 0,
        },
        "archive_boundary": archive_boundary,
        "candidates": final_candidates,
        "decision": decision,
        "writeback": {
            "enabled": bool(writeback),
            "memory_ids": [item for item in writeback_entries if item],
        },
    }

    analysis_dir = _analysis_dir(project_root)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    json_path = analysis_dir / f"memory-friction-evolution-{run_id}.json"
    md_path = analysis_dir / f"memory-friction-evolution-{run_id}.md"
    write_json(json_path, payload)
    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    write_json(
        _latest_state_path(project_root),
        {
            "schema_version": "1.0",
            "run_id": run_id,
            "generated_at": generated_at,
            "payload_path": str(json_path.relative_to(project_root)),
            "markdown_path": str(md_path.relative_to(project_root)),
        },
    )
    payload["paths"] = {
        "json": str(json_path.relative_to(project_root)),
        "markdown": str(md_path.relative_to(project_root)),
    }
    return payload


def load_latest_memory_friction_report(project_root: Path) -> dict[str, Any]:
    latest = read_json(_latest_state_path(project_root), {})
    if isinstance(latest, dict):
        payload_path = str(latest.get("payload_path") or "").strip()
        if payload_path:
            candidate = project_root / payload_path
            payload = read_json(candidate, {})
            if isinstance(payload, dict) and payload:
                return payload
    analysis_dir = _analysis_dir(project_root)
    candidates = sorted(analysis_dir.glob("memory-friction-evolution-*.json"))
    if not candidates:
        return {}
    payload = read_json(candidates[-1], {})
    return payload if isinstance(payload, dict) else {}


def render_memory_friction_human(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict) or not payload:
        return "No memory/friction evolution report found."
    lines = [
        "Beacon Memory/Friction Evolution",
        "=" * 32,
        f"run_id           : {payload.get('run_id', '')}",
        f"docs_version     : {payload.get('docs_version', '')}",
        f"mode             : {payload.get('mode', '')}",
        f"generated_at     : {payload.get('generated_at', '')}",
    ]
    inputs = payload.get("inputs") if isinstance(payload.get("inputs"), dict) else {}
    lines.extend(
        [
            f"memory refs      : {len(inputs.get('memory_refs', []))}",
            f"friction refs    : {len(inputs.get('debug_refs', []))}",
            f"lighthouse ref   : {inputs.get('lighthouse_ref', '') or '-'}",
        ]
    )
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), list) else []
    lines.append(f"top candidates   : {len(candidates)}")
    if candidates:
        lines.append("")
        lines.append("Top candidates")
        for row in candidates[:5]:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"{row.get('candidate_id', '')} "
                f"[{row.get('recommendation', '')}] "
                f"score={row.get('score', 0)} "
                f"summary={row.get('friction_summary', '')}"
            )
            lines.append(f"  command: {row.get('recommended_command', '')}")
    paths = payload.get("paths") if isinstance(payload.get("paths"), dict) else {}
    if paths:
        lines.extend(["", f"json report      : {paths.get('json', '')}", f"markdown report  : {paths.get('markdown', '')}"])
    return "\n".join(lines)


def memory_friction_payload_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
