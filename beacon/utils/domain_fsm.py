"""Domain FSM + entity-precedence authority for feature packages (v1.6.7).

domain-fsm.v1 and entity-precedence.v1 are package-level freeze/clarity hard gates.
Lifecycle/orchestrator state machines are intentionally out of scope.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.feature_package import _parse_frontmatter, _read_text, package_paths
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import normalize_version, resolve_target_version

SCHEMA_DOMAIN_FSM = "domain-fsm.v1"
SCHEMA_ENTITY_PRECEDENCE = "entity-precedence.v1"
DOMAIN_FSM_SCHEMA_VERSION = "1.0"

REASON_NOT_REQUIRED = ""
REASON_DOMAIN_FSM_MISSING = "domain_fsm_missing"
REASON_ENTITY_PRECEDENCE_MISSING = "entity_precedence_missing"
REASON_ILLEGAL_TRANSITION_SLOT_MISSING = "illegal_transition_slot_missing"
REASON_ORPHAN_AC_WITHOUT_FSM_PATH = "orphan_ac_without_fsm_path"
REASON_DOMAIN_FSM_SCHEMA_INVALID = "domain_fsm_schema_invalid"
REASON_DOMAIN_MODEL_MISSING = "domain_model_missing"
REASON_DOMAIN_FSM_INCOMPLETE = "domain_fsm_incomplete"

_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_AC_ID_RE = re.compile(r"\b(AC-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b", re.IGNORECASE)
_STATE_TOKEN_RE = re.compile(r"\b([a-z][a-z0-9_]{1,40})\b", re.IGNORECASE)

_DOMAIN_MODEL_TITLES = (
    "domain model",
    "domain-model",
    "实体模型",
    "领域模型",
    "entity precedence",
    "entity-precedence",
    "实体前置",
    "实体前置序",
)
_DOMAIN_FSM_TITLES = (
    "domain fsm",
    "domain-fsm",
    "业务状态机",
    "业务域状态机",
    "领域状态机",
    "domain state machine",
)
_ILLEGAL_TITLES = (
    "illegal transition",
    "illegal transitions",
    "非法转移",
    "非法状态转移",
    "illegal path",
)
_AC_SECTION_TITLES = (
    "acceptance criteria",
    "验收标准",
    "接受标准",
)
_BUSINESS_DOMAIN_SIGNALS = (
    "order",
    "product",
    "cart",
    "checkout",
    "payment",
    "inventory",
    "shipment",
    "订单",
    "商品",
    "购物车",
    "支付",
    "库存",
    "结算",
    "下单",
    "聚合根",
)


def _semver_tuple(version: str | None) -> tuple[int, int, int]:
    normalized = normalize_version(version) or "v0.0.0"
    try:
        major, minor, patch = normalized.lstrip("v").split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return 0, 0, 0


def domain_fsm_supported(version: str | None) -> bool:
    return _semver_tuple(version) >= (1, 6, 7)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in {"1", "true", "yes", "y", "on", "required"}


def _normalize_heading(title: str) -> str:
    return re.sub(r"\s+", " ", str(title or "").strip().lower())


def _heading_matches(title: str, candidates: tuple[str, ...]) -> bool:
    normalized = _normalize_heading(title)
    return any(token in normalized for token in candidates)


def _extract_sections(markdown: str) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    current_title = ""
    current_level = 0
    buf: list[str] = []
    for raw in str(markdown or "").splitlines():
        match = _HEADING_RE.match(raw.strip())
        if match:
            if current_title:
                sections.append(
                    {
                        "title": current_title,
                        "level": str(current_level),
                        "body": "\n".join(buf).strip(),
                    }
                )
            current_level = len(match.group(1))
            current_title = str(match.group(2) or "").strip()
            buf = []
            continue
        if current_title:
            buf.append(raw)
    if current_title:
        sections.append(
            {
                "title": current_title,
                "level": str(current_level),
                "body": "\n".join(buf).strip(),
            }
        )
    return sections


def _table_rows(section_body: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in str(section_body or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells:
            continue
        if all(set(cell) <= {"-", ":", " "} for cell in cells if cell):
            continue
        rows.append(cells)
    return rows


def _parse_entity_precedence(sections: list[dict[str, str]]) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    for section in sections:
        if not _heading_matches(section["title"], _DOMAIN_MODEL_TITLES):
            continue
        rows = _table_rows(section["body"])
        if not rows:
            # bullet form: - Product (root) requires -
            for line in section["body"].splitlines():
                stripped = line.strip()
                if not stripped.startswith(("-", "*", "•")):
                    continue
                text = stripped.lstrip("-*• ").strip()
                if not text:
                    continue
                name = text.split(":", 1)[0].split("—", 1)[0].split("(", 1)[0].strip()
                if name:
                    entities.append(
                        {
                            "entity": name,
                            "key": "",
                            "precedence": text,
                            "requires": text,
                        }
                    )
            continue
        header = [cell.lower() for cell in rows[0]]
        # Skip header row if it looks like a header
        start = 1 if any(token in " ".join(header) for token in ("entity", "实体", "key", "precedence", "前置")) else 0
        for row in rows[start:]:
            entity = row[0] if row else ""
            if not entity or entity.lower() in {"entity", "实体", "name"}:
                continue
            key = row[1] if len(row) > 1 else ""
            precedence = row[2] if len(row) > 2 else (row[1] if len(row) > 1 else "")
            entities.append(
                {
                    "entity": entity,
                    "key": key,
                    "precedence": precedence,
                    "requires": precedence,
                }
            )
    return entities


def _parse_aggregate_name(title: str) -> str:
    normalized = str(title or "").strip()
    for sep in ("—", "–", "-", ":", "：", "|"):
        if sep in normalized:
            tail = normalized.split(sep)[-1].strip()
            if tail:
                return tail
    # "Domain FSM Product" → Product
    tokens = normalized.split()
    if tokens:
        return tokens[-1]
    return normalized or "aggregate"


def _parse_fsm_tables(sections: list[dict[str, str]]) -> list[dict[str, Any]]:
    aggregates: list[dict[str, Any]] = []
    for section in sections:
        title = section["title"]
        if not _heading_matches(title, _DOMAIN_FSM_TITLES):
            continue
        name = _parse_aggregate_name(title)
        states: set[str] = set()
        transitions: list[dict[str, str]] = []
        rows = _table_rows(section["body"])
        if rows:
            header = [cell.lower() for cell in rows[0]]
            start = 1 if any(token in " ".join(header) for token in ("state", "from", "to", "状态", "guard")) else 0
            for row in rows[start:]:
                if not row:
                    continue
                # Formats:
                # | State | From | Guard |
                # | to | from | guard | side effects |
                to_state = row[0].strip()
                from_raw = row[1].strip() if len(row) > 1 else ""
                guard = row[2].strip() if len(row) > 2 else ""
                if not to_state or to_state.lower() in {"state", "to", "状态"}:
                    continue
                states.add(to_state)
                if from_raw and from_raw not in {"-", "—", "–", "none", "n/a", ""}:
                    for source in re.split(r"[,/|，、]", from_raw):
                        source_state = source.strip()
                        if not source_state or source_state in {"-", "—"}:
                            continue
                        states.add(source_state)
                        transitions.append(
                            {
                                "from": source_state,
                                "to": to_state,
                                "guard": guard,
                            }
                        )
                else:
                    # initial state row
                    transitions.append({"from": "", "to": to_state, "guard": guard, "initial": "true"})
        else:
            # arrow form: [draft] --x--> [listed]
            for match in re.finditer(
                r"\[(?P<from>[^\]]+)\]\s*--[^>]*-->\s*\[(?P<to>[^\]]+)\]",
                section["body"],
            ):
                source = match.group("from").strip()
                target = match.group("to").strip()
                if source and target:
                    states.add(source)
                    states.add(target)
                    transitions.append({"from": source, "to": target, "guard": ""})
        aggregates.append(
            {
                "name": name,
                "states": sorted(states),
                "transitions": transitions,
            }
        )
    return aggregates


def _parse_illegal_transitions(sections: list[dict[str, str]], body: str) -> list[dict[str, str]]:
    slots: list[dict[str, str]] = []
    bodies: list[str] = []
    for section in sections:
        if _heading_matches(section["title"], _ILLEGAL_TITLES):
            bodies.append(section["body"])
    # Do not fall back to the whole document: meta features may discuss illegal
    # transitions without owning a domain package.
    for chunk in bodies:
        for line in chunk.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("-", "*", "•", "|")):
                text = stripped.lstrip("-*• ").strip().strip("|").strip()
                if not text or set(text) <= {"-", ":", " "}:
                    continue
                if text.lower().startswith("illegal") and len(text.split()) <= 2:
                    continue
                aggregate = ""
                # Order.placed without Product
                if "." in text.split()[0]:
                    aggregate = text.split(".", 1)[0].strip("`")
                slots.append(
                    {
                        "description": text,
                        "aggregate": aggregate,
                        "source": "truth",
                    }
                )
    # de-dupe by description
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for item in slots:
        key = item["description"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _parse_acceptance_criteria(sections: list[dict[str, str]], body: str) -> list[dict[str, str]]:
    acs: list[dict[str, str]] = []
    for section in sections:
        if not _heading_matches(section["title"], _AC_SECTION_TITLES) and "acceptance criteria" not in _normalize_heading(
            section["title"]
        ):
            # still allow "## Acceptance Criteria" variants already covered
            if "ac" not in _normalize_heading(section["title"]) and "验收" not in section["title"]:
                continue
        rows = _table_rows(section["body"])
        start = 0
        if rows:
            header = " ".join(cell.lower() for cell in rows[0])
            if "ac" in header:
                start = 1
        for row in rows[start:]:
            if not row:
                continue
            ac_id = row[0].strip()
            if not _AC_ID_RE.search(ac_id):
                continue
            description = row[-1] if len(row) > 1 else ""
            if len(row) >= 3:
                description = row[2] if row[2] else row[-1]
            acs.append(
                {
                    "ac_id": _AC_ID_RE.search(ac_id).group(1).upper(),  # type: ignore[union-attr]
                    "description": description,
                }
            )
    if acs:
        return acs
    # fallback: any AC ids in body
    for match in _AC_ID_RE.finditer(body):
        acs.append({"ac_id": match.group(1).upper(), "description": ""})
    # de-dupe
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for item in acs:
        if item["ac_id"] in seen:
            continue
        seen.add(item["ac_id"])
        out.append(item)
    return out


def _legal_state_names(aggregates: list[dict[str, Any]]) -> set[str]:
    names: set[str] = set()
    for aggregate in aggregates:
        for state in aggregate.get("states") or []:
            names.add(str(state).lower())
        for transition in aggregate.get("transitions") or []:
            if isinstance(transition, dict):
                if transition.get("from"):
                    names.add(str(transition["from"]).lower())
                if transition.get("to"):
                    names.add(str(transition["to"]).lower())
        if aggregate.get("name"):
            names.add(str(aggregate["name"]).lower())
    return names


def _ac_binds_to_fsm(ac: dict[str, str], aggregates: list[dict[str, Any]], entities: list[dict[str, str]]) -> bool:
    description = str(ac.get("description") or "").lower()
    if not description:
        return False
    # illegal/negative ACs bind via illegal path wording
    if any(token in description for token in ("illegal", "reject", "拒绝", "without", "无商品", "不允许")):
        return True
    legal_names = _legal_state_names(aggregates)
    for name in legal_names:
        if name and name in description:
            return True
    for entity in entities:
        entity_name = str(entity.get("entity") or "").strip().lower()
        if entity_name and entity_name in description:
            return True
    # verb path hints common in commerce-like FSM
    path_verbs = (
        "place",
        "placed",
        "pay",
        "paid",
        "ship",
        "shipped",
        "list",
        "listed",
        "create",
        "draft",
        "cancel",
        "下单",
        "支付",
        "发货",
        "上架",
        "创建",
    )
    if any(verb in description for verb in path_verbs) and aggregates:
        return True
    return False


def parse_domain_fsm_from_truth(truth_markdown: str) -> dict[str, Any]:
    """Parse domain-fsm.v1 + entity-precedence.v1 projection from package truth markdown."""
    frontmatter, body, errors = _parse_frontmatter(str(truth_markdown or ""))
    sections = _extract_sections(body if body else str(truth_markdown or ""))
    entities = _parse_entity_precedence(sections)
    aggregates = _parse_fsm_tables(sections)
    illegal_slots = _parse_illegal_transitions(sections, body if body else str(truth_markdown or ""))
    acceptance = _parse_acceptance_criteria(sections, body if body else str(truth_markdown or ""))

    has_domain_model = any(_heading_matches(s["title"], _DOMAIN_MODEL_TITLES) for s in sections) or bool(entities)
    has_domain_fsm = any(_heading_matches(s["title"], _DOMAIN_FSM_TITLES) for s in sections) or bool(aggregates)
    has_illegal = any(_heading_matches(s["title"], _ILLEGAL_TITLES) for s in sections) or bool(illegal_slots)

    orphan_acs: list[str] = []
    bound_acs: list[str] = []
    if aggregates or entities:
        for ac in acceptance:
            if _ac_binds_to_fsm(ac, aggregates, entities):
                bound_acs.append(ac["ac_id"])
            else:
                orphan_acs.append(ac["ac_id"])

    aggregates_missing_illegal: list[str] = []
    if aggregates:
        # Prefer named aggregate roots; require at least one illegal slot overall and
        # ideally one per aggregate when names can be matched.
        if not illegal_slots:
            aggregates_missing_illegal = [str(item.get("name") or "aggregate") for item in aggregates]
        else:
            covered = {str(item.get("aggregate") or "").lower() for item in illegal_slots if item.get("aggregate")}
            for aggregate in aggregates:
                name = str(aggregate.get("name") or "").strip()
                if not name:
                    continue
                # If aggregate name is generic like "Domain FSM" tail, skip strict per-name match when global slots exist
                lname = name.lower()
                if lname in {"domain", "fsm", "domain fsm", "状态机"}:
                    continue
                if covered and lname not in covered and not any(lname in slot["description"].lower() for slot in illegal_slots):
                    aggregates_missing_illegal.append(name)
            # If no aggregate-named slots but global illegal list exists, treat as covered for the roots
            if not covered and illegal_slots:
                aggregates_missing_illegal = []

    return {
        "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
        "domain_fsm_schema": SCHEMA_DOMAIN_FSM,
        "entity_precedence_schema": SCHEMA_ENTITY_PRECEDENCE,
        "frontmatter": frontmatter if isinstance(frontmatter, dict) else {},
        "frontmatter_errors": errors,
        "has_domain_model_section": has_domain_model,
        "has_domain_fsm_section": has_domain_fsm,
        "has_illegal_transition_section": has_illegal,
        "entities": entities,
        "entity_precedence": entities,
        "aggregates": aggregates,
        "illegal_transition_slots": illegal_slots,
        "acceptance_criteria": acceptance,
        "bound_ac_ids": bound_acs,
        "orphan_ac_ids": orphan_acs,
        "aggregates_missing_illegal_slots": aggregates_missing_illegal,
        "raw_section_titles": [s["title"] for s in sections],
    }


def domain_fsm_is_required(
    *,
    truth_markdown: str,
    frontmatter: dict[str, Any] | None = None,
    diagram_truth: dict[str, Any] | None = None,
    version: str | None = None,
) -> dict[str, Any]:
    """Decide whether domain-fsm authority applies to this package."""
    if version is not None and not domain_fsm_supported(version):
        return {"required": False, "reason": "version_below_v1_6_7"}

    fm = frontmatter if isinstance(frontmatter, dict) else {}
    if not fm:
        parsed_fm, _, _ = _parse_frontmatter(str(truth_markdown or ""))
        fm = parsed_fm if isinstance(parsed_fm, dict) else {}

    explicit = any(
        _truthy(fm.get(key))
        for key in (
            "domain_required",
            "domain_fsm_required",
            "entity_precedence_required",
            "require_domain_fsm",
        )
    )
    lowered = str(truth_markdown or "").lower()
    # Only real markdown headings count as section presence (not AC prose mentioning schemas).
    section_presence = any(
        token in lowered
        for token in (
            "## domain model",
            "## domain fsm",
            "## 领域模型",
            "## 业务状态机",
            "## 业务域状态机",
            "## 实体前置",
            "## entity precedence",
            "## illegal transition",
            "## 非法转移",
        )
    )
    # Explicit partial presence of domain authority sections forces completeness
    parsed = parse_domain_fsm_from_truth(truth_markdown)
    # Partial authority only when Domain Model / Domain FSM / Illegal headings exist.
    # Mentions of domain-fsm in meta requirements must not auto-require a package FSM.
    partial = bool(
        parsed.get("has_domain_model_section")
        or parsed.get("has_domain_fsm_section")
        or parsed.get("has_illegal_transition_section")
    )

    diagram = diagram_truth if isinstance(diagram_truth, dict) else {}
    complexity = bool(diagram.get("required")) or bool(diagram.get("complexity_signals"))
    business_signal = any(
        re.search(rf"(?<![a-z0-9_-]){re.escape(token)}(?![a-z0-9_-])", lowered)
        if re.fullmatch(r"[a-z][a-z0-9_ -]{1,40}", token)
        else token in lowered
        for token in _BUSINESS_DOMAIN_SIGNALS
    )
    fixture_negative = str(fm.get("expected_gate") or "").lower() in {
        "freeze_or_qa_fail",
        "domain_fsm",
        "entity_precedence",
    }

    required = bool(explicit or partial or section_presence or fixture_negative or (complexity and business_signal))
    reason = "not_required"
    if explicit:
        reason = "explicit_domain_mark"
    elif fixture_negative:
        reason = "fixture_expected_domain_gate"
    elif partial or section_presence:
        reason = "domain_section_present"
    elif complexity and business_signal:
        reason = "complexity_with_business_domain"
    return {
        "required": required,
        "reason": reason,
        "explicit": explicit,
        "partial": partial,
        "complexity": complexity,
        "business_signal": business_signal,
    }


def validate_domain_fsm_projection(projection: dict[str, Any], *, required: bool) -> dict[str, Any]:
    """Validate a parsed domain-fsm projection. Fail-closed when required."""
    findings: list[dict[str, Any]] = []
    if not required:
        return {
            "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
            "required": False,
            "blocked": False,
            "status": "not_required",
            "reason_code": REASON_NOT_REQUIRED,
            "findings": [],
            "projection": projection,
        }

    entities = projection.get("entities") if isinstance(projection.get("entities"), list) else []
    aggregates = projection.get("aggregates") if isinstance(projection.get("aggregates"), list) else []
    illegal_slots = (
        projection.get("illegal_transition_slots")
        if isinstance(projection.get("illegal_transition_slots"), list)
        else []
    )
    orphan_acs = projection.get("orphan_ac_ids") if isinstance(projection.get("orphan_ac_ids"), list) else []
    missing_illegal = (
        projection.get("aggregates_missing_illegal_slots")
        if isinstance(projection.get("aggregates_missing_illegal_slots"), list)
        else []
    )

    if not projection.get("has_domain_model_section") and not entities:
        findings.append(
            {
                "kind": "domain_model_missing",
                "reason_code": REASON_DOMAIN_MODEL_MISSING,
                "text": "domain feature requires Domain Model / entity-precedence section",
            }
        )
    if not entities:
        findings.append(
            {
                "kind": "entity_precedence_missing",
                "reason_code": REASON_ENTITY_PRECEDENCE_MISSING,
                "text": "domain feature requires entity-precedence rows (entity order / requires)",
            }
        )
    if not projection.get("has_domain_fsm_section") and not aggregates:
        findings.append(
            {
                "kind": "domain_fsm_missing",
                "reason_code": REASON_DOMAIN_FSM_MISSING,
                "text": "domain feature requires Domain FSM section with states/transitions",
            }
        )
    if aggregates:
        valid_transition_count = 0
        for aggregate in aggregates:
            transitions = aggregate.get("transitions") if isinstance(aggregate.get("transitions"), list) else []
            states = aggregate.get("states") if isinstance(aggregate.get("states"), list) else []
            if not states:
                findings.append(
                    {
                        "kind": "domain_fsm_incomplete",
                        "reason_code": REASON_DOMAIN_FSM_INCOMPLETE,
                        "text": f"aggregate {aggregate.get('name')} has no states",
                        "aggregate": str(aggregate.get("name") or ""),
                    }
                )
            for transition in transitions:
                if not isinstance(transition, dict):
                    continue
                if transition.get("to"):
                    valid_transition_count += 1
        if valid_transition_count == 0:
            findings.append(
                {
                    "kind": "domain_fsm_incomplete",
                    "reason_code": REASON_DOMAIN_FSM_INCOMPLETE,
                    "text": "Domain FSM has aggregates but no parseable transitions/states",
                }
            )
    if not illegal_slots:
        findings.append(
            {
                "kind": "illegal_transition_slot_missing",
                "reason_code": REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
                "text": "each domain package requires at least one illegal-transition TC slot in truth",
            }
        )
    for name in missing_illegal:
        findings.append(
            {
                "kind": "illegal_transition_slot_missing",
                "reason_code": REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
                "text": f"aggregate root missing illegal-transition slot: {name}",
                "aggregate": str(name),
            }
        )
    for ac_id in orphan_acs:
        findings.append(
            {
                "kind": "orphan_ac_without_fsm_path",
                "reason_code": REASON_ORPHAN_AC_WITHOUT_FSM_PATH,
                "text": f"acceptance criterion has no mappable Domain FSM legal path: {ac_id}",
                "ac_id": str(ac_id),
            }
        )

    # Schema contract surface (fields present on projection)
    required_fields = (
        "domain_fsm_schema",
        "entity_precedence_schema",
        "entities",
        "aggregates",
        "illegal_transition_slots",
    )
    for field in required_fields:
        if field not in projection:
            findings.append(
                {
                    "kind": "domain_fsm_schema_invalid",
                    "reason_code": REASON_DOMAIN_FSM_SCHEMA_INVALID,
                    "text": f"domain-fsm projection missing field: {field}",
                    "field": field,
                }
            )

    reason_code = ""
    if findings:
        # Prefer the first domain authority reason
        reason_code = str(findings[0].get("reason_code") or REASON_DOMAIN_FSM_INCOMPLETE)
    return {
        "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
        "required": True,
        "blocked": bool(findings),
        "status": "blocked" if findings else "pass",
        "reason_code": reason_code,
        "findings": findings,
        "projection": projection,
        "summary": {
            "entity_count": len(entities),
            "aggregate_count": len(aggregates),
            "illegal_slot_count": len(illegal_slots),
            "orphan_ac_count": len(orphan_acs),
            "bound_ac_count": len(projection.get("bound_ac_ids") or []),
        },
    }


def evaluate_domain_fsm_authority(
    *,
    truth_markdown: str,
    tests_markdown: str = "",
    version: str | None = None,
    diagram_truth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate domain-fsm authority for a truth package (text-level API for tests/CLI)."""
    projection = parse_domain_fsm_from_truth(truth_markdown)
    requirement = domain_fsm_is_required(
        truth_markdown=truth_markdown,
        frontmatter=projection.get("frontmatter") if isinstance(projection.get("frontmatter"), dict) else {},
        diagram_truth=diagram_truth,
        version=version,
    )
    validation = validate_domain_fsm_projection(projection, required=bool(requirement.get("required")))
    # Optional: tests.md should mention illegal when required
    if bool(requirement.get("required")) and tests_markdown:
        tests_lower = tests_markdown.lower()
        if "illegal" not in tests_lower and "非法" not in tests_markdown:
            finding = {
                "kind": "illegal_transition_slot_missing",
                "reason_code": REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
                "text": "tests.md missing illegal-transition coverage reference",
            }
            validation = {
                **validation,
                "blocked": True,
                "status": "blocked",
                "reason_code": validation.get("reason_code") or REASON_ILLEGAL_TRANSITION_SLOT_MISSING,
                "findings": list(validation.get("findings") or []) + [finding],
            }
    return {
        "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
        "domain_fsm_schema": SCHEMA_DOMAIN_FSM,
        "entity_precedence_schema": SCHEMA_ENTITY_PRECEDENCE,
        "requirement": requirement,
        "required": bool(requirement.get("required")),
        "blocked": bool(validation.get("blocked")),
        "status": validation.get("status"),
        "reason_code": validation.get("reason_code") or "",
        "findings": validation.get("findings") or [],
        "projection": projection,
        "validation": validation,
    }


def build_domain_fsm_gate_payload(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    diagram_truth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project-root gate payload for freeze / requirement_clarity integration."""
    project_root = Path(project_root).expanduser().resolve()
    resolved_version = resolve_target_version(project_root, version)
    slug = feature_slug(feature)
    paths = package_paths(project_root, version=resolved_version, feature=slug)
    truth_md = _read_text(paths["truth"])
    tests_md = _read_text(paths["tests"])
    if not domain_fsm_supported(resolved_version):
        return {
            "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "required": False,
            "blocked": False,
            "status": "not_supported",
            "reason_code": "",
            "findings": [],
            "truth_path": str(paths["truth"].relative_to(project_root)) if paths["truth"].exists() else "",
        }
    if not truth_md.strip():
        # No package truth — do not invent domain requirement
        return {
            "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": slug,
            "version": resolved_version,
            "required": False,
            "blocked": False,
            "status": "skipped_no_truth",
            "reason_code": "",
            "findings": [],
            "truth_path": str(paths["truth"].relative_to(project_root)) if paths["truth"].exists() else "",
        }

    result = evaluate_domain_fsm_authority(
        truth_markdown=truth_md,
        tests_markdown=tests_md,
        version=resolved_version,
        diagram_truth=diagram_truth,
    )
    findings = []
    for item in result.get("findings") or []:
        if not isinstance(item, dict):
            continue
        findings.append(
            {
                **item,
                "file": str(paths["truth"]),
                "line": 1,
            }
        )
    return {
        "schema_version": DOMAIN_FSM_SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slug,
        "version": resolved_version,
        "truth_path": str(paths["truth"].relative_to(project_root)),
        "tests_path": str(paths["tests"].relative_to(project_root)) if paths["tests"].exists() else "",
        "required": bool(result.get("required")),
        "blocked": bool(result.get("blocked")),
        "status": str(result.get("status") or "pass"),
        "reason_code": str(result.get("reason_code") or ""),
        "findings": findings,
        "requirement": result.get("requirement") or {},
        "projection": result.get("projection") or {},
        "validation": result.get("validation") or {},
        "recommended_action": (
            "author_domain_model_domain_fsm_entity_precedence_and_illegal_slots_before_freeze"
            if result.get("blocked")
            else ""
        ),
    }


def domain_fsm_findings(
    project_root: Path,
    *,
    version: str = "auto",
    feature: str,
    diagram_truth: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    gate = build_domain_fsm_gate_payload(
        project_root,
        version=version,
        feature=feature,
        diagram_truth=diagram_truth,
    )
    return list(gate.get("findings") or []) if bool(gate.get("required")) else []


def schema_contract() -> dict[str, Any]:
    """Public field contract for domain-fsm.v1 / entity-precedence.v1 (AC-DFSM-001)."""
    return {
        "domain_fsm": {
            "schema": SCHEMA_DOMAIN_FSM,
            "fields": {
                "aggregates": ["name", "states", "transitions"],
                "transitions": ["from", "to", "guard"],
                "illegal_transition_slots": ["description", "aggregate"],
            },
        },
        "entity_precedence": {
            "schema": SCHEMA_ENTITY_PRECEDENCE,
            "fields": {
                "entities": ["entity", "key", "precedence", "requires"],
            },
        },
        "authority": {
            "truth_sections": ["Domain Model", "Domain FSM", "Illegal transitions"],
            "gates": ["freeze", "requirement_clarity", "truth_integrity"],
            "support_checklists_noncanonical": True,
        },
    }
