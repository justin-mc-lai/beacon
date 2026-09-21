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

from beacon.utils.feature_package import _parse_frontmatter, _read_text, package_paths
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
    "非法转换",
    "invalid / illegal",
    "invalid or illegal",
)
# Short headings that mean the illegal-transition section. Exact match only, so a
# prose section such as `## Invalid inputs` is not mistaken for it.
_ILLEGAL_SECTION_EXACT_TITLES = ("invalid", "illegal")
_ILLEGAL_ARROW_RE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*(?:->|→|-->)\s*([A-Za-z][A-Za-z0-9_]*)")
# Only explicit `illegal: from -> to` (or a from|to table row) is machine syntax.
# Free prose in the illegal section is documentation and must never be parsed as
# an edge — describing an illegal bypass often names a legal pair (#31 P3).
_ILLEGAL_EXPLICIT_RE = re.compile(r"^(?:illegal|非法)\s*[:：]\s*(.+)$", re.IGNORECASE)
_ILLEGAL_TABLE_HEADER_CELLS = {"from", "state", "源", "从", "起始", "起始状态"}
_TERMINAL_RE = re.compile(
    r"(?:(?<!非)终态|(?<![A-Za-z-])terminal(?:\s+states?)?)\s*[:：]\s*([^\n]+)",
    re.IGNORECASE,
)
# Chinese suffix form: `closed/refunded 为终态。` — the canonical gold example uses this.
_TERMINAL_SUFFIX_RE = re.compile(
    r"([A-Za-z][A-Za-z0-9_]*(?:\s*[/、,，]\s*[A-Za-z][A-Za-z0-9_]*)*)\s*为(?:最终状态|终态)",
    re.IGNORECASE,
)
_MERMAID_TERM_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*-->\s*\[\*\]\s*$", re.MULTILINE)


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
    """Collect illegal-transition entries.

    Every entry is kept as documentation. `from`/`to` is populated only for
    explicit machine syntax — `- illegal: a -> b` or a `| a | b | reason |` row —
    so prose describing a bypass never becomes a phantom illegal edge (#31 P3).
    """
    slots: list[dict[str, str]] = []
    for section in _extract_sections(truth_md):
        title = _normalize_heading(section["title"])
        if title not in _ILLEGAL_SECTION_EXACT_TITLES and not any(
            token in title for token in _ILLEGAL_SECTION_TITLES
        ):
            continue
        for line in section["body"].splitlines():
            stripped = line.strip()
            if stripped.startswith("|"):
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                if len(cells) < 2 or not cells[0]:
                    continue
                if set(cells[0]) <= {"-", ":"} or cells[0].lower() in _ILLEGAL_TABLE_HEADER_CELLS:
                    continue
                slots.append({"description": " | ".join(cells), "from": cells[0], "to": cells[1]})
                continue
            if not stripped.startswith(("-", "*", "•")):
                continue
            text = stripped.lstrip("-*• ").strip()
            if not text or set(text) <= {"-", ":", " ", ">"}:
                continue
            from_id = to_id = ""
            explicit = _ILLEGAL_EXPLICIT_RE.match(text)
            if explicit:
                m = _ILLEGAL_ARROW_RE.search(explicit.group(1))
                if m:
                    from_id, to_id = m.group(1), m.group(2)
            slots.append({"description": text, "from": from_id, "to": to_id})
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for item in slots:
        key = item["description"].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
    return uniq


def _collect_terminal_tokens(chunk: str) -> set[str]:
    terminals: set[str] = set()
    for tok in re.split(r"[,/|，、\s]+", chunk):
        tok = tok.strip().strip("`*。；;，,、")
        if tok and len(tok) < 40:
            terminals.add(tok)
    return terminals


def _parse_terminal_states(truth_md: str) -> set[str]:
    terminals: set[str] = set()
    for m in _TERMINAL_RE.finditer(truth_md):
        terminals |= _collect_terminal_tokens(m.group(1))
    for m in _TERMINAL_SUFFIX_RE.finditer(truth_md):
        terminals |= _collect_terminal_tokens(m.group(1))
    # ponytail: mermaid `frozen --> [*]` is the display truth for terminal; treat it as declared terminal
    for m in _MERMAID_TERM_RE.finditer(truth_md):
        tok = m.group(1).strip()
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
    source_states = {str(t.get("state") or "").strip() for t in fsm.get("transitions") or []}
    # Terminal is structural: declared terminals plus any state with no outgoing.
    terminals = set(fsm.get("terminal_states") or []) | {st for st in states if st and st not in source_states}
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
        # A state with outgoing transitions is not a terminal, even if a stale
        # projection or prose once called it one. Keeps the projection table-derived.
        if st in states and st not in source_states:
            lines.append(f"    {st} --> [*]")
    return "\n".join(lines)


def attach_fsm_mermaid(truth_markdown: str) -> dict[str, Any]:
    """Attach or re-sync the mermaid projection block (idempotent, AC-001).

    The projection must follow the five-tuple. A pre-existing block is not a reason
    to skip: a stale projection contradicts the table it is supposed to display.
    """
    md = str(truth_markdown or "")
    fsm = parse_truth_fsm(md)
    if not fsm["five_tuple_present"]:
        return {"changed": False, "reason_code": "no_fsm_five_tuple", "markdown": md}
    block = render_fsm_mermaid(fsm)
    heading = _MERMAID_HEADING.search(md)
    # Only the block that follows the FSM heading is ours to rewrite — never an
    # earlier architecture/diagram mermaid block elsewhere in the document.
    if heading:
        fenced = re.compile(r"```\s*mermaid\s*\n.*?\n?```", re.IGNORECASE | re.DOTALL)
        m = fenced.search(md, heading.end())
        if m:
            current = re.sub(r"^```\s*mermaid\s*\n|\n?```$", "", m.group(0), flags=re.IGNORECASE).strip()
            if current == block.strip():
                return {"changed": False, "reason_code": "mermaid_already_present", "markdown": md}
            resynced = md[: m.start()] + f"```mermaid\n{block}\n```" + md[m.end():]
            return {"changed": True, "reason_code": "mermaid_resynced", "markdown": resynced}
    attached = f"{md.rstrip()}\n\n## FSM mermaid（投影）\n\n```mermaid\n{block}\n```\n"
    return {"changed": True, "reason_code": "mermaid_attached", "markdown": attached}


def validate_truth_fsm(fsm: dict[str, Any], *, truth_markdown: str = "") -> dict[str, Any]:
    """Machine validation: states exist, transitions legal, illegal blocked (AC-002/004).

    A state with no outgoing transition *is* terminal by definition. Declaring it
    explicitly is a completeness acknowledgement, so an undeclared terminal is a
    warning, not a hard block — otherwise the gate rejects the natural way FSMs are
    written and false-blocks packages whose content is correct (#30 / #31 P3).
    """
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
    declared_terminals = set(fsm.get("terminal_states") or [])
    structural_terminals = {st for st in states if st and st not in source_states}
    for t in fsm.get("transitions") or []:
        src = str(t.get("state") or "").strip()
        dst = str(t.get("to") or "").strip()
        if not dst:
            findings.append(
                {
                    "kind": "transition_target_missing",
                    "severity": "error",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition from '{src or '?'}' has no destination state",
                    "state": src,
                }
            )
            continue
        if src and src not in states:
            findings.append(
                {
                    "kind": "state_undefined",
                    "severity": "error",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition source state '{src}' is not declared in FSM states",
                    "state": src,
                }
            )
        if dst and dst not in states:
            findings.append(
                {
                    "kind": "state_undefined",
                    "severity": "error",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition destination state '{dst}' is not declared in FSM states",
                    "state": dst,
                }
            )
        if dst and dst not in source_states and dst not in declared_terminals:
            findings.append(
                {
                    "kind": "terminal_undeclared",
                    "severity": "warning",
                    "reason_code": "",
                    "text": (
                        f"state '{dst}' ends the flow but is not declared terminal; "
                        f"add an illegal-transition entry or declare it (终态: {dst} / {dst} --> [*])"
                    ),
                    "state": dst,
                }
            )
        if not t.get("event"):
            findings.append(
                {
                    "kind": "transition_event_missing",
                    "severity": "error",
                    "reason_code": REASON_TRUTH_FSM_INVALID,
                    "text": f"transition {src or '?'} -> {dst or '?'} has no event",
                }
            )
    for declared in sorted(declared_terminals):
        if declared and declared not in states:
            findings.append(
                {
                    "kind": "terminal_undefined",
                    "severity": "warning",
                    "reason_code": "",
                    "text": f"declared terminal '{declared}' is not a state in the FSM five-tuple (typo?)",
                    "state": declared,
                }
            )
    if states and not (structural_terminals or declared_terminals):
        findings.append(
            {
                "kind": "fsm_terminal_missing",
                "severity": "warning",
                "reason_code": "",
                "text": "no state can end the flow and no terminal state is declared (event-driven workflows may cycle on purpose)",
            }
        )
    illegal = fsm.get("illegal") or []
    if not illegal:
        findings.append(
            {
                "kind": "illegal_slot_missing",
                "severity": "error",
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
                        "severity": "error",
                        "reason_code": REASON_TRUTH_FSM_INVALID,
                        "text": f"explicit illegal transition {src} -> {dst} is also declared as a legal transition",
                        "from": src,
                        "to": dst,
                    }
                )
    blocked = any(str(f.get("severity") or "error") == "error" for f in findings)
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "blocked": blocked,
        "status": "blocked" if blocked else "pass",
        "reason_code": REASON_TRUTH_FSM_INVALID if blocked else "",
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


def domain_required_from_frontmatter(frontmatter: dict[str, Any] | None) -> bool:
    """Single source for the domain opt-in flag shared by truth review and freeze."""
    raw = (frontmatter or {}).get("domain_required")
    if isinstance(raw, bool):
        return raw
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on", "required"}


def build_truth_fsm_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    truth_markdown: str | None = None,
) -> dict[str, Any]:
    """Freeze gate payload (AC-004). Fail-closed with reason_code truth_fsm_invalid.

    The FSM contract is required only for `domain_required: true` packages, matching
    `truth review` Check B — otherwise review and freeze disagree on the same package.
    `truth_markdown` lets callers validate an in-memory variant (e.g. the projected
    mermaid) before persisting it, so a blocked freeze never mutates the package.
    """
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_path = str(paths["truth"].relative_to(project_root)) if paths["truth"].exists() else ""
    truth_md = _read_text(paths["truth"]) if truth_markdown is None else str(truth_markdown)
    if not truth_md.strip():
        return {
            "schema": SCHEMA_TRUTH_FSM,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "truth_path": truth_path,
            "blocked": False,
            "status": "skipped_no_truth",
            "reason_code": "",
            "findings": [],
        }
    frontmatter, _body, _errs = _parse_frontmatter(truth_md)
    if not domain_required_from_frontmatter(frontmatter):
        return {
            "schema": SCHEMA_TRUTH_FSM,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "truth_path": truth_path,
            "blocked": False,
            "status": "skipped_not_domain",
            "reason_code": "",
            "findings": [],
            "recommended_action": "",
        }
    fsm = parse_truth_fsm(truth_md)
    if not fsm["five_tuple_present"]:
        finding = {
            "kind": "fsm_five_tuple_missing",
            "severity": "error",
            "reason_code": REASON_TRUTH_FSM_INVALID,
            "text": "domain package requires an FSM five-tuple (State|Event|Guard|To|Action)",
        }
        return {
            "schema": SCHEMA_TRUTH_FSM,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "truth_path": truth_path,
            "blocked": True,
            "status": "blocked",
            "reason_code": REASON_TRUTH_FSM_INVALID,
            "findings": [finding],
            "projection": fsm,
            "recommended_action": "author_domain_fsm_five_tuple_before_freeze",
        }
    validation = validate_truth_fsm(fsm, truth_markdown=truth_md)
    digest = compute_fsm_digest(fsm)
    return {
        "schema": SCHEMA_TRUTH_FSM,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "truth_path": truth_path,
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
