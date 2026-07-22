"""Truth Review Gate (v1.6.10): Plan→Truth mandatory checks A/B/C before freeze.

Check A — Intent Coverage Matrix (must intents not missing)
Check B — FSM five-tuple + hang audit + illegal list (domain_required)
Check C — every AC has ≥1 TC with Command + Assertion

reason_code on fail: truth_review_gate_failed
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_execution_file
from beacon.utils.feature_package import _parse_frontmatter, package_paths
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version

SCHEMA = "truth-review-gate.v1"
REASON_FAILED = "truth_review_gate_failed"
REASON_TRUTH_MISSING = "truth_missing"
REASON_PACKAGE_INCOMPLETE = "feature_package_incomplete"

_AC_ID_RE = re.compile(r"\b(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b", re.IGNORECASE)
_TC_ID_RE = re.compile(r"\b(TC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b", re.IGNORECASE)
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def truth_review_gate_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 10)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on", "required"}


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:  # noqa: BLE001
        return str(path)


def _split_table_row(line: str) -> list[str]:
    """Split a markdown table row on | while ignoring pipes inside backticks."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    buf: list[str] = []
    in_tick = False
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch == "`":
            in_tick = not in_tick
            buf.append(ch)
            i += 1
            continue
        if ch == "|" and not in_tick:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _table_blocks(markdown: str) -> list[list[list[str]]]:
    """Split markdown into contiguous pipe-table blocks (list of cell rows)."""
    blocks: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in str(markdown or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = _split_table_row(stripped)
            if cells and all(set(c) <= {"-", ":", " "} for c in cells if c):
                continue
            current.append(cells)
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def _header_join(row: list[str]) -> str:
    return " ".join(c.lower() for c in row)


def extract_intent_coverage_matrix(truth_md: str) -> list[dict[str, str]]:
    rows_out: list[dict[str, str]] = []
    for block in _table_blocks(truth_md):
        if not block:
            continue
        header = _header_join(block[0])
        if "intent_id" not in header and "intent id" not in header:
            if "intent" not in header or "landing" not in header:
                continue
        headers = [c.lower().replace(" ", "_") for c in block[0]]
        for row in block[1:]:
            if not row:
                continue
            data = {headers[i] if i < len(headers) else f"c{i}": (row[i] if i < len(row) else "") for i in range(max(len(headers), len(row)))}
            intent_id = (
                data.get("intent_id")
                or data.get("intent")
                or (row[0] if row else "")
            ).strip()
            if not intent_id or intent_id.lower() in {"intent_id", "intent id", "intent"}:
                continue
            strength = (data.get("strength") or data.get("优先级") or "").strip().lower()
            landing = (data.get("landing") or data.get("落点") or (row[3] if len(row) > 3 else "")).strip()
            status = (data.get("status") or data.get("状态") or (row[4] if len(row) > 4 else "")).strip().lower()
            source = (data.get("source") or data.get("来源") or (row[1] if len(row) > 1 else "")).strip()
            rows_out.append(
                {
                    "intent_id": intent_id,
                    "source": source,
                    "strength": strength or "must",
                    "landing": landing,
                    "status": status or "covered",
                }
            )
    return rows_out


def extract_acceptance_criteria(truth_md: str) -> list[dict[str, str]]:
    acs: list[dict[str, str]] = []
    for block in _table_blocks(truth_md):
        if not block:
            continue
        header = _header_join(block[0])
        if "ac id" not in header and not (header.startswith("ac ") or header == "ac description" or "ac" in header.split()[:1]):
            # Accept "| AC ID | Description |" or "| AC ID | Theme | Description |"
            if "ac" not in header:
                continue
        for row in block[1:]:
            if not row:
                continue
            m = _AC_ID_RE.search(row[0])
            if not m:
                continue
            ac_id = m.group(1).upper()
            desc = row[1] if len(row) == 2 else (row[2] if len(row) > 2 else (row[1] if len(row) > 1 else ""))
            acs.append({"ac_id": ac_id, "description": desc})
    if acs:
        # de-dupe preserve order
        seen: set[str] = set()
        out: list[dict[str, str]] = []
        for item in acs:
            if item["ac_id"] in seen:
                continue
            seen.add(item["ac_id"])
            out.append(item)
        return out
    # fallback scan
    seen2: set[str] = set()
    for m in _AC_ID_RE.finditer(truth_md):
        ac_id = m.group(1).upper()
        if ac_id in seen2:
            continue
        seen2.add(ac_id)
        acs.append({"ac_id": ac_id, "description": ""})
    return acs


def extract_test_rows(tests_md: str) -> list[dict[str, str]]:
    rows_out: list[dict[str, str]] = []
    for block in _table_blocks(tests_md):
        if not block:
            continue
        first = block[0]
        first_join = " ".join(c.lower() for c in first)
        # Continuation table without header (starts with TC-...)
        if _TC_ID_RE.search(first[0] if first else ""):
            headers = ["tc_id", "ac", "command", "assertion"]
            data_rows = block
        else:
            headers = [c.lower().replace(" ", "_") for c in first]
            header_join = " ".join(headers)
            if "tc" not in header_join and "command" not in header_join:
                continue
            data_rows = block[1:]
        # Map columns
        for row in data_rows:
            if not row:
                continue
            data = {headers[i] if i < len(headers) else f"c{i}": (row[i] if i < len(row) else "") for i in range(len(headers))}
            # Also raw by position for TC | AC | Command | Assertion
            tc_id = (data.get("tc_id") or data.get("tc") or "").strip()
            ac_raw = (data.get("ac") or data.get("ac_id") or "").strip()
            command = (data.get("command") or data.get("planned_command") or "").strip()
            assertion = (data.get("assertion") or data.get("assert") or "").strip()
            if not tc_id and row:
                m_tc = _TC_ID_RE.search(row[0])
                if m_tc:
                    tc_id = m_tc.group(1).upper()
                if len(row) > 1 and not ac_raw:
                    ac_raw = row[1]
                if len(row) > 2 and not command:
                    command = row[2]
                if len(row) > 3 and not assertion:
                    assertion = row[3]
            if not tc_id and not ac_raw:
                continue
            ac_ids = [m.group(1).upper() for m in _AC_ID_RE.finditer(ac_raw)]
            if not ac_ids and ac_raw.upper().startswith("AC-"):
                ac_ids = [ac_raw.upper()]
            if not ac_ids and ac_raw.lower() in {"illegal", "n/a", "-"}:
                ac_ids = []
            rows_out.append(
                {
                    "tc_id": tc_id.upper() if tc_id else "",
                    "ac_raw": ac_raw,
                    "ac_ids": ",".join(ac_ids),
                    "command": command,
                    "assertion": assertion,
                }
            )
    return rows_out


def extract_fsm_five_tuple(truth_md: str) -> dict[str, Any]:
    """Parse State|Event|Guard|To|Action tables (v1.6.10 contract)."""
    transitions: list[dict[str, str]] = []
    for block in _table_blocks(truth_md):
        if not block:
            continue
        header = _header_join(block[0])
        # require state + event + (to or guard)
        if "state" not in header or "event" not in header:
            continue
        if "to" not in header and "guard" not in header:
            continue
        headers = [c.lower().replace(" ", "_") for c in block[0]]
        for row in block[1:]:
            if not row:
                continue
            data = {headers[i] if i < len(headers) else f"c{i}": (row[i] if i < len(row) else "") for i in range(len(headers))}
            state = (data.get("state") or data.get("from") or (row[0] if row else "")).strip()
            event = (data.get("event") or (row[1] if len(row) > 1 else "")).strip()
            guard = (data.get("guard") or (row[2] if len(row) > 2 else "")).strip()
            to_state = (data.get("to") or data.get("to_state") or (row[3] if len(row) > 3 else "")).strip()
            action = (data.get("action") or (row[4] if len(row) > 4 else "")).strip()
            if not state or state.lower() in {"state", "from"}:
                continue
            if not event or event.lower() == "event":
                continue
            transitions.append(
                {
                    "state": state,
                    "event": event,
                    "guard": guard,
                    "to": to_state,
                    "action": action,
                }
            )
    from_states = sorted({t["state"] for t in transitions})
    to_states = sorted({t["to"] for t in transitions if t.get("to")})
    outgoing: dict[str, int] = {}
    for t in transitions:
        outgoing[t["state"]] = outgoing.get(t["state"], 0) + 1
    # Terminal heuristic: appear only as destination, or named in 终态/terminal prose
    terminal_explicit: set[str] = set()
    for m in re.finditer(r"(终态|terminal(?:\s+states?)?)[:：\s]+([^\n]+)", truth_md, re.IGNORECASE):
        chunk = m.group(2)
        for tok in re.split(r"[,/|，、\s]+", chunk):
            tok = tok.strip().strip("`*")
            if tok and len(tok) < 40:
                terminal_explicit.add(tok)
    # states with no outgoing that only appear as To → terminal
    all_states = set(from_states) | set(to_states)
    hanging: list[str] = []
    terminals: list[str] = []
    for st in sorted(all_states):
        out_n = outgoing.get(st, 0)
        if out_n >= 1:
            continue
        # no outgoing
        if st in terminal_explicit or st in to_states:
            terminals.append(st)
        else:
            # mentioned but neither source nor terminal mark → hang
            hanging.append(st)
    # Non-terminal with zero outgoing (should be empty if table well-formed)
    for st, n in outgoing.items():
        if n < 1:
            hanging.append(st)
    illegal_present = bool(
        re.search(r"(?im)^(###?\s+)?(invalid|illegal|非法)", truth_md)
        or re.search(r"(?i)\binvalid\b[:：]", truth_md)
        or re.search(r"(?i)illegal[：:]", truth_md)
    )
    return {
        "transitions": transitions,
        "from_states": from_states,
        "to_states": to_states,
        "outgoing": outgoing,
        "terminals": terminals,
        "hanging_states": sorted(set(hanging)),
        "five_tuple_present": bool(transitions),
        "illegal_present": illegal_present,
    }


def check_a_intent_matrix(
    truth_md: str,
    *,
    domain_required: bool,
    require_matrix: bool,
) -> dict[str, Any]:
    matrix = extract_intent_coverage_matrix(truth_md)
    missing_must: list[dict[str, str]] = []
    for row in matrix:
        strength = (row.get("strength") or "must").lower()
        status = (row.get("status") or "").lower()
        landing = (row.get("landing") or "").strip().lower()
        if strength == "must" and (status == "missing" or landing in {"missing", "—", "-", ""}):
            missing_must.append(row)
    has_matrix_heading = bool(
        re.search(r"(?i)intent\s+coverage\s+matrix|意图覆盖矩阵", truth_md)
    )
    required = require_matrix or domain_required or has_matrix_heading
    if required and not matrix:
        return {
            "pass": False,
            "check": "A",
            "name": "intent_coverage",
            "required": True,
            "matrix_rows": 0,
            "missing_must": [],
            "reason": "intent_matrix_missing",
            "findings": [{"kind": "intent_matrix_missing", "text": "Intent Coverage Matrix required but not found"}],
        }
    if not required and not matrix:
        return {
            "pass": True,
            "check": "A",
            "name": "intent_coverage",
            "required": False,
            "matrix_rows": 0,
            "missing_must": [],
            "reason": "",
            "findings": [],
            "skipped": True,
        }
    ok = len(missing_must) == 0
    return {
        "pass": ok,
        "check": "A",
        "name": "intent_coverage",
        "required": True,
        "matrix_rows": len(matrix),
        "missing_must": missing_must,
        "reason": "must_intent_missing" if not ok else "",
        "findings": (
            [
                {
                    "kind": "must_intent_missing",
                    "text": f"{r.get('intent_id')}: status={r.get('status')} landing={r.get('landing')}",
                }
                for r in missing_must
            ]
            if not ok
            else []
        ),
        "matrix": matrix,
    }


def check_b_fsm_audit(truth_md: str, *, domain_required: bool) -> dict[str, Any]:
    if not domain_required:
        return {
            "pass": True,
            "check": "B",
            "name": "fsm_audit",
            "required": False,
            "skipped": True,
            "reason": "",
            "findings": [],
        }
    fsm = extract_fsm_five_tuple(truth_md)
    findings: list[dict[str, str]] = []
    if not fsm["five_tuple_present"]:
        findings.append({"kind": "fsm_five_tuple_missing", "text": "State|Event|Guard|To|Action table missing"})
    if not fsm["illegal_present"]:
        findings.append({"kind": "illegal_list_missing", "text": "invalid/illegal transition list missing"})
    for st in fsm.get("hanging_states") or []:
        findings.append({"kind": "fsm_hanging_state", "text": f"non-terminal or unknown state without outgoing event: {st}"})
    ok = not findings
    return {
        "pass": ok,
        "check": "B",
        "name": "fsm_audit",
        "required": True,
        "reason": "fsm_audit_failed" if not ok else "",
        "findings": findings,
        "fsm": {
            "transition_count": len(fsm.get("transitions") or []),
            "from_states": fsm.get("from_states"),
            "hanging_states": fsm.get("hanging_states"),
            "terminals": fsm.get("terminals"),
            "illegal_present": fsm.get("illegal_present"),
            "five_tuple_present": fsm.get("five_tuple_present"),
        },
    }


def check_c_testability(truth_md: str, tests_md: str) -> dict[str, Any]:
    acs = extract_acceptance_criteria(truth_md)
    trows = extract_test_rows(tests_md)
    covered: dict[str, list[str]] = {}
    weak: list[dict[str, str]] = []
    for tr in trows:
        ac_ids = [x for x in (tr.get("ac_ids") or "").split(",") if x]
        cmd = (tr.get("command") or "").strip()
        assertion = (tr.get("assertion") or "").strip()
        if not cmd or not assertion:
            weak.append({"tc_id": tr.get("tc_id") or "", "reason": "missing_command_or_assertion"})
            continue
        for ac_id in ac_ids:
            covered.setdefault(ac_id, []).append(tr.get("tc_id") or "anon")
    missing_ac: list[str] = []
    for ac in acs:
        ac_id = ac["ac_id"]
        if ac_id not in covered:
            missing_ac.append(ac_id)
    findings: list[dict[str, str]] = []
    for ac_id in missing_ac:
        findings.append({"kind": "ac_without_tc", "text": f"{ac_id} has no TC with Command+Assertion"})
    for w in weak:
        findings.append({"kind": "tc_weak", "text": f"TC {w.get('tc_id')} missing command or assertion"})
    ok = len(missing_ac) == 0 and len(weak) == 0
    # If no ACs parsed at all, fail closed when tests empty
    if not acs:
        findings.append({"kind": "ac_table_missing", "text": "no acceptance criteria parsed from truth.md"})
        ok = False
    return {
        "pass": ok,
        "check": "C",
        "name": "testability",
        "required": True,
        "reason": "testability_gaps" if not ok else "",
        "findings": findings,
        "ac_count": len(acs),
        "tc_count": len(trows),
        "missing_ac": missing_ac,
        "covered": {k: v for k, v in covered.items()},
    }


def evaluate_truth_review_gate(
    *,
    truth_md: str,
    tests_md: str = "",
    version: str = "v1.6.10",
    feature: str = "",
    domain_required: bool | None = None,
    require_matrix: bool | None = None,
    frontmatter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate Checks A/B/C. Humanizer polish is ordered after pass (not scored here)."""
    fm, _body, _err = _parse_frontmatter(truth_md)
    if frontmatter:
        fm = {**fm, **frontmatter}
    if domain_required is None:
        domain_required = _truthy(fm.get("domain_required"))
    if require_matrix is None:
        # Gold / explicit snapshot / domain packages require matrix
        snap = "truth_review_gate" in truth_md and "required" in truth_md
        require_matrix = domain_required or snap or bool(re.search(r"(?i)intent\s+coverage\s+matrix|意图覆盖矩阵", truth_md))

    check_a = check_a_intent_matrix(truth_md, domain_required=domain_required, require_matrix=bool(require_matrix))
    check_b = check_b_fsm_audit(truth_md, domain_required=domain_required)
    check_c = check_c_testability(truth_md, tests_md)

    checks = [check_a, check_b, check_c]
    overall = all(bool(c.get("pass")) for c in checks)
    findings: list[dict[str, str]] = []
    for c in checks:
        for f in c.get("findings") or []:
            if isinstance(f, dict):
                findings.append(f)

    humanizer_order = {
        "rule": "humanizer_only_after_abc_pass_before_freeze",
        "abc_pass": overall,
        "allowed_now": overall,
        "note": "Polish L0/narrative only; preserve_machine_fields=true",
    }

    return {
        "schema": SCHEMA,
        "schema_version": "1.0",
        "feature": feature_slug(feature) if feature else "",
        "version": version,
        "pass": overall,
        "blocked": not overall,
        "review_gate_pass": overall,
        "reason_code": "" if overall else REASON_FAILED,
        "domain_required": domain_required,
        "checks": {
            "A_intent_coverage": check_a,
            "B_fsm_audit": check_b,
            "C_testability": check_c,
        },
        "findings": findings,
        "humanizer": humanizer_order,
        "evaluated_at": now_iso(),
    }


def truth_review_report_path(project_root: Path, *, version: str, feature: str) -> Path:
    slug = feature_slug(feature)
    return machine_execution_file(project_root, version, f"{slug}.truth-review-gate.json")


def run_truth_review_gate(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    write_report: bool = True,
    domain_required: bool | None = None,
    require_matrix: bool | None = None,
) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    slug = feature_slug(feature)
    paths = package_paths(root, version=resolved, feature=slug)
    truth_path = paths["truth"]
    tests_path = paths["tests"]

    if not truth_path.is_file():
        payload = {
            "schema": SCHEMA,
            "schema_version": "1.0",
            "feature": slug,
            "version": resolved,
            "pass": False,
            "blocked": True,
            "review_gate_pass": False,
            "reason_code": REASON_TRUTH_MISSING,
            "path": _rel(root, truth_path),
            "findings": [{"kind": "truth_missing", "text": str(truth_path)}],
            "evaluated_at": now_iso(),
        }
        if write_report:
            write_json(truth_review_report_path(root, version=resolved, feature=slug), payload)
        return payload

    truth_md = _read(truth_path)
    tests_md = _read(tests_path)
    missing_pkg = [name for name in ("tests", "tasks", "evidence") if not paths[name].is_file()]
    result = evaluate_truth_review_gate(
        truth_md=truth_md,
        tests_md=tests_md,
        version=resolved,
        feature=slug,
        domain_required=domain_required,
        require_matrix=require_matrix,
    )
    result["paths"] = {
        "truth": _rel(root, truth_path),
        "tests": _rel(root, tests_path) if tests_path.is_file() else "",
        "report": _rel(root, truth_review_report_path(root, version=resolved, feature=slug)),
    }
    if missing_pkg:
        result.setdefault("findings", []).append(
            {"kind": "package_incomplete", "text": f"missing package files: {', '.join(missing_pkg)}"}
        )
        # incomplete package does not alone fail A/B/C, but freeze has separate validation

    if write_report:
        report_path = truth_review_report_path(root, version=resolved, feature=slug)
        write_json(report_path, result)
        result["report_path"] = _rel(root, report_path)

    return result


def build_truth_review_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    write_report: bool = True,
) -> dict[str, Any]:
    """Freeze-facing payload; skips hard fail when version < 1.6.10."""
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    if not truth_review_gate_supported(resolved):
        return {
            "schema": SCHEMA,
            "version": resolved,
            "feature": feature_slug(feature),
            "pass": True,
            "blocked": False,
            "review_gate_pass": True,
            "reason_code": "",
            "skipped": True,
            "skip_reason": "version_below_v1.6.10",
        }
    return run_truth_review_gate(
        root,
        version=resolved,
        feature=feature,
        write_report=write_report,
    )


def mark_package_materials_stale(
    project_root: Path,
    *,
    version: str,
    feature: str,
    surfaces: tuple[str, ...] = ("tests", "tasks"),
) -> dict[str, Any]:
    """On reopen/truth change: mark tests/tasks frontmatter materials_status=stale."""
    root = Path(project_root).expanduser().resolve()
    resolved = resolve_target_version(root, version)
    paths = package_paths(root, version=resolved, feature=feature)
    updated: list[str] = []
    for key in surfaces:
        path = paths.get(key)
        if not path or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            # prepend minimal frontmatter
            path.write_text(
                f"---\nslug: {feature_slug(feature)}\nversion: {resolved}\nmaterials_status: stale\n---\n\n{text}",
                encoding="utf-8",
            )
            updated.append(_rel(root, path))
            continue
        end = text.find("\n---", 3)
        if end < 0:
            continue
        fm = text[3:end]
        body = text[end + 4 :]
        if re.search(r"(?m)^materials_status:\s*", fm):
            fm2 = re.sub(r"(?m)^materials_status:\s*.*$", "materials_status: stale", fm)
        else:
            fm2 = fm.rstrip() + "\nmaterials_status: stale\n"
        path.write_text(f"---{fm2}\n---{body}", encoding="utf-8")
        updated.append(_rel(root, path))
    return {"updated": updated, "materials_status": "stale", "feature": feature_slug(feature), "version": resolved}
