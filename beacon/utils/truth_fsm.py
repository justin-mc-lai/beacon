"""Truth FSM projection: mermaid render + machine validate + behavior digest (v1.6.14).

The truth package's FSM 五元组 (State|Event|Guard|To|Action) becomes a first-class
contract: auto-rendered as mermaid (AC-001), machine-validated for
state/transition/illegal soundness (AC-002), behavior-vs-wording change detection
via two digests (AC-003), and a fail-closed freeze gate (AC-004).

Mermaid is a display projection of the FSM table — it never rewrites truth semantics.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.feature_package import _read_text, package_paths
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_review_gate import extract_fsm_five_tuple
from beacon.utils.versioning import resolve_target_version

SCHEMA_TRUTH_FSM = "truth-fsm.v1"
REASON_TRUTH_FSM_INVALID = "truth_fsm_invalid"

_MERMAID_HEADING = re.compile(r"^#{2,6}\s+FSM\s+mermaid[^\n]*$", re.IGNORECASE | re.MULTILINE)
_MERMAID_BLOCK_START = re.compile(r"^```\s*mermaid\s*$", re.IGNORECASE | re.MULTILINE)
_ILLEGAL_SECTION_TITLES = (
    "illegal transition",
    "illegal transitions",
    "非法转移",
    "非法状态转移",
    "invalid / illegal",
    "invalid or illegal",
)
_ILLEGAL_ARROW_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*(?:->|→|-->)\s*([A-Za-z][A-Za-z0-9_]*)")
_TERMINAL_RE = re.compile(r"(?:终态|terminal(?:\s+states?)?)[:：\s]+([^\n]+)", re.IGNORECASE)


def _extract_sections(markdown: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title = ""
    buf: list[str] = []
    for raw in str(markdown or "").splitlines():
        m = re.match(r"^(#{2,6})\s+(.+?)\s*$", raw.strip())
        if m:
            if current_title:
                sections.append({"title": current_title, "body": "\n".join(buf).strip()})
            current_title = str(m.group(2) or "").strip()
            buf = []
            continue
        if current_title:
            buf.append(raw)
    if current_title:
        sections.append({"title": current_title, "body": "\n".join(buf).strip()})
    return sections


def _normalize_heading(title: str) -> str:
    return re.sub(r"\s+", " ", str(title or "").strip().lower())


def _parse_illegal_slots(truth_md: str) -> list[dict[str, str]]:
    slots: list[dict[str, str]] = []
    for section in _extract_sections(truth_md):
        if not any(token in _normalize_heading(section["title"]) for token in _ILLEGAL_SECTION_TITLES):
            continue
        for line in section["body"].splitlines():
            stripped = line.strip()
            if not stripped.startswith(("-", "*", "•")):
                continue
            text = stripped.lstrip("-*• ").strip()
            if not text or set(text) <= {"-", ":", " ", ">"}:
                continue
            m = _ILLEGAL_ARROW_RE.search(text)
            slots.append(
                {
                    "description": text,
                    "from": m.group(1) if m else "",
                    "to": m.group(2) if m else "",
                }
            )
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for item in slots:
        key = item["description"].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
    return uniq


def _parse_terminal_states(truth_md: str) -> set[str]:
    terminals: set[str] = set()
    for m in _TERMINAL_RE.finditer(truth_md):
        for tok in re.split(r"[,/|，、\s]+", m.group(1)):
            tok = tok.strip().strip("`*")
            if tok and len(tok) < 40:
                terminals.add(tok)
    return terminals


def parse_truth_fsm(truth_markdown: str) -> dict[str, Any]:
    """Parse the FSM 五元组 + illegal transitions into a normalized projection."""
    five = extract_fsm_five_tuple(str(truth_markdown or ""))
    transitions = list(five.get("transitions") or [])
    states: set[str] = set()
    for t in transitions:
        if t.get("state"):
            states.add(str(t["state"]).strip())
        if t.get("to"):
            states.add(str(t["to"]).strip())
    illegal = _parse_illegal_slots(str(truth_markdown or ""))
    terminal_explicit = _parse_terminal_states(str(truth_markdown or ""))
    from_states = {str(t.get("state") or "").strip() for t in transitions}
    to_states = {str(t.get("to") or "").strip() for t in transitions if t.get("to")}
    initial = sorted(from_states - to_states)
    terminals = sorted(terminal_explicit)
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "five_tuple_present": bool(five.get("five_tuple_present")),
        "states": sorted(states),
        "transitions": transitions,
        "illegal": illegal,
        "initial_states": initial,
        "terminal_states": terminals,
        "illegal_present": bool(illegal) or bool(five.get("illegal_present")),
    }


def render_fsm_mermaid(fsm: dict[str, Any]) -> str:
    """Render the FSM projection as a stateDiagram-v2 block (AC-001)."""
    lines = ["stateDiagram-v2"]
    states = list(fsm.get("states") or [])
    initial = list(fsm.get("initial_states") or [])
    terminals = set(fsm.get("terminal_states") or [])
    seen_edges: set[str] = set()
    for t in fsm.get("transitions") or []:
        src = str(t.get("state") or "").strip()
        dst = str(t.get("to") or "").strip()
        if not src or not dst:
            continue
        event = str(t.get("event") or "").strip()
        guard = str(t.get("guard") or "").strip()
        edge_key = f"{src}->{dst}"
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        label = event if event else "next"
        if guard:
            label = f"{event or 'next'} ({guard})"
        lines.append(f"    {src} --> {dst} : {label}")
    for st in initial:
        if st in states:
            lines.insert(1, f"    [*] --> {st}")
    for st in sorted(terminals):
        if st in states:
            lines.append(f"    {st} --> [*]")
    return "\n".join(lines)


def attach_fsm_mermaid(truth_markdown: str) -> dict[str, Any]:
    """Attach the mermaid projection block to truth markdown (idempotent, AC-001)."""
    md = str(truth_markdown or "")
    if _MERMAID_HEADING.search(md) and _MERMAID_BLOCK_START.search(md):
        return {"changed": False, "reason_code": "mermaid_already_present", "markdown": md}
    fsm = parse_truth_fsm(md)
    if not fsm["five_tuple_present"]:
        return {"changed": False, "reason_code": "no_fsm_five_tuple", "markdown": md}
    block = render_fsm_mermaid(fsm)
    attached = f"{md.rstrip()}\n\n## FSM mermaid（投影）\n\n```mermaid\n{block}\n```\n"
    return {"changed": True, "reason_code": "mermaid_attached", "markdown": attached}


def validate_truth_fsm(fsm: dict[str, Any], *, truth_markdown: str = "") -> dict[str, Any]:
    """Machine validation: states exist, transitions legal, illegal blocked (AC-002/004)."""
    findings: list[dict[str, Any]] = []
    if not fsm["five_tuple_present"]:
        return {
            "schema": SCHEMA_TRUTH_FSM,
            "blocked": False,
            "status": "not_required",
            "reason_code": "",
            "findings": [],
            "projection": fsm,
        }
    states = {str(s).strip() for s in fsm.get("states") or []}
    source_states = {str(t.get("state") or "").strip() for t in fsm.get("transitions") or []}
    terminal_states = set(fsm.get("terminal_states") or [])
    for t in fsm.get("transitions") or []:
        src = str(t.get("state") or "").strip()
        dst = str(t.get("to") or "").strip()
        if src and src not in states:
            findings.append(
                {
                    "kind": "state_undefined",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition source state '{src}' is not declared in FSM states",
                    "state": src,
                }
            )
        if dst and dst not in states:
            findings.append(
                {
                    "kind": "state_undefined",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition destination state '{dst}' is not declared in FSM states",
                    "state": dst,
                }
            )
        if dst and dst not in source_states and dst not in terminal_states:
            findings.append(
                {
                    "kind": "state_undefined",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"destination state '{dst}' has no outgoing transition and is not a declared terminal state",
                    "state": dst,
                }
            )
        if not t.get("event"):
            findings.append(
                {
                    "kind": "transition_event_missing",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition {src or '?'} -> {dst or '?'} has no event",
                }
            )
    illegal = fsm.get("illegal") or []
    if not illegal:
        findings.append(
            {
                "kind": "illegal_slot_missing",
                "reason_code": REASON_TRUTH_FSM_INVALID,
                "text": "FSM five-tuple requires an Illegal transitions section (fail-closed on missing illegal)",
            }
        )
    else:
        legal_edges = {(str(t.get("state") or "").strip(), str(t.get("to") or "").strip()) for t in fsm.get("transitions") or []}
        for item in illegal:
            src, dst = str(item.get("from") or "").strip(), str(item.get("to") or "").strip()
            if src and dst and (src, dst) in legal_edges:
                findings.append(
                    {
                        "kind": "illegal_declared_as_legal",
                        "reason_code": REASON_TRUTH_FSM_INVALID,
                        "text": f"illegal transition {src} -> {dst} is also declared as a legal transition",
                        "from": src,
                        "to": dst,
                    }
                )
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": REASON_TRUTH_FSM_INVALID if findings else "",
        "findings": findings,
        "projection": fsm,
        "summary": {
            "state_count": len(fsm.get("states") or []),
            "transition_count": len(fsm.get("transitions") or []),
            "illegal_count": len(illegal),
            "initial_states": fsm.get("initial_states") or [],
            "terminal_states": fsm.get("terminal_states") or [],
        },
    }


def compute_fsm_digest(fsm: dict[str, Any]) -> dict[str, Any]:
    """Behavior vs wording digest (AC-003). Wording-only edits keep behavior digest stable."""
    states = sorted(fsm.get("states") or [])
    behavior_transitions = sorted(
        (str(t.get("state") or ""), str(t.get("to") or ""), str(t.get("event") or "")) for t in fsm.get("transitions") or []
    )
    illegal_behavior = sorted(str(i.get("description") or "") for i in fsm.get("illegal") or [])
    behavior_canonical = json.dumps(
        {"states": states, "transitions": behavior_transitions, "illegal": illegal_behavior},
        sort_keys=True,
        ensure_ascii=False,
    )
    wording_canonical = json.dumps(fsm.get("transitions") or [], sort_keys=True, ensure_ascii=False)
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "behavior_digest": hashlib.sha256(behavior_canonical.encode("utf-8")).hexdigest()[:16],
        "wording_digest": hashlib.sha256(wording_canonical.encode("utf-8")).hexdigest()[:16],
        "behavior_stable_when_wording_changes": True,
    }


def build_truth_fsm_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
) -> dict[str, Any]:
    """Freeze gate payload (AC-004). Fail-closed with reason_code truth_fsm_invalid."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_md = _read_text(paths["truth"])
    if not truth_md.strip():
        return {
            "schema": SCHEMA_TRUTH_FSM,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "blocked": False,
            "status": "skipped_no_truth",
            "reason_code": "",
            "findings": [],
        }
    fsm = parse_truth_fsm(truth_md)
    validation = validate_truth_fsm(fsm, truth_markdown=truth_md)
    digest = compute_fsm_digest(fsm)
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "truth_path": str(paths["truth"].relative_to(project_root)),
        "blocked": bool(validation.get("blocked")),
        "status": str(validation.get("status") or "pass"),
        "reason_code": str(validation.get("reason_code") or ""),
        "findings": validation.get("findings") or [],
        "projection": fsm,
        "validation": validation,
        "digest": digest,
        "recommended_action": "repair_fsm_states_or_illegal_transitions" if validation.get("blocked") else "",
    }


def fsm_digest_for_truth(truth_markdown: str) -> dict[str, Any]:
    """Convenience digest API for tests (AC-003)."""
    return compute_fsm_digest(parse_truth_fsm(truth_markdown))
