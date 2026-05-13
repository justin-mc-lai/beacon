"""Requirement material parsing helpers for human-authored Beacon docs."""

from __future__ import annotations

import re
from typing import Any

_SECTION_RE = re.compile(
    r"^##\s+((?:US|RG)-\d{3}|CR-[A-Z0-9-]+)\s*[：:]\s*(.+?)\s*$",
    flags=re.IGNORECASE,
)
_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_HEADING_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*[.)]?\s*")
_RESEARCH_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "architecture": ("architecture", "architecture overview", "system architecture", "架构", "系统架构", "架构概览"),
    "business_flow": ("business flow", "business workflow", "flow", "业务流程", "流程", "业务闭环"),
    "state_machine": ("state machine", "state-machine", "状态机", "状态流转"),
    "decision_priority": ("decision priority", "decision-priority", "priority rules", "决策优先级", "优先级规则"),
    "open_questions": ("open questions", "unresolved", "待确认", "待澄清", "open question"),
}


def extract_explicit_ac_items(content: str, source: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    if not str(content or "").strip():
        return items

    for line in str(content or "").splitlines():
        if "|" not in line:
            continue
        match = re.search(r"\b(AC-\d{3,})\b", line, flags=re.IGNORECASE)
        if not match:
            continue
        ac_id = match.group(1).upper()
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        theme = cells[1] if len(cells) > 1 else ""
        text = cells[2] if len(cells) > 2 else (cells[1] if len(cells) > 1 else line.strip())
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append(
            {
                "ac_id": ac_id,
                "theme": theme,
                "text": text,
                "source": source,
            }
        )

    for match in re.finditer(r"\b(AC-\d{3,})\b[:：]?\s*([^\n]+)", str(content or ""), flags=re.IGNORECASE):
        ac_id = match.group(1).upper()
        text = match.group(2).strip()
        if ac_id in seen:
            continue
        seen.add(ac_id)
        items.append(
            {
                "ac_id": ac_id,
                "theme": "",
                "text": text,
                "source": source,
            }
        )
    return items


def _dedupe_explicit_ac_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        ac_id = str(item.get("ac_id") or "").strip().upper()
        if not ac_id:
            continue
        current = seen.get(ac_id)
        if current is None:
            clone = dict(item)
            clone["ac_id"] = ac_id
            seen[ac_id] = clone
            deduped.append(clone)
            continue
        if not str(current.get("theme") or "").strip() and str(item.get("theme") or "").strip():
            current["theme"] = item.get("theme")
        if not str(current.get("text") or "").strip() and str(item.get("text") or "").strip():
            current["text"] = item.get("text")
    return deduped


def _normalize_heading_title(title: str) -> str:
    text = str(title or "").strip().lower()
    return _HEADING_PREFIX_RE.sub("", text).strip()


def _extract_research_sections(content: str) -> dict[str, list[str]]:
    sections = {key: [] for key in _RESEARCH_SECTION_ALIASES}
    if not str(content or "").strip():
        return sections

    current_key = ""
    in_code_fence = False
    for raw_line in str(content or "").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        heading = _HEADING_RE.match(stripped)
        if heading:
            normalized = _normalize_heading_title(str(heading.group(2) or ""))
            current_key = ""
            for key, aliases in _RESEARCH_SECTION_ALIASES.items():
                if normalized in aliases:
                    current_key = key
                    break
            continue
        if not current_key or not stripped:
            continue
        if stripped.startswith(("-", "*", "+")):
            sections[current_key].append(stripped[1:].strip())
        elif stripped[0].isdigit():
            parts = re.split(r"[.)]\s+", stripped, maxsplit=1)
            sections[current_key].append(parts[1].strip() if len(parts) > 1 else stripped)
    return sections


def extract_research_closure_items(content: str, source: str) -> list[dict[str, Any]]:
    sections = _extract_research_sections(content)
    items: list[dict[str, Any]] = []
    mapping = (
        ("business_flow", "business_flow", "Business flow remains explicit"),
        ("state_machine", "state_machine", "State machine transitions remain explicit"),
        ("decision_priority", "decision_priority", "Decision priority remains deterministic"),
    )
    for section_key, theme, fallback_title in mapping:
        bullets = [str(item).strip() for item in sections.get(section_key, []) if str(item).strip()]
        if not bullets:
            continue
        items.append(
            {
                "theme": theme,
                "text": fallback_title,
                "details": bullets,
                "source": source,
            }
        )
    return items


def _merge_research_closure_items(
    items: list[dict[str, Any]],
    *,
    research_content: str,
    research_source: str,
) -> list[dict[str, Any]]:
    research_items = extract_research_closure_items(research_content, research_source)
    if not research_items:
        return items

    merged = [dict(item) for item in items if isinstance(item, dict)]
    seen_texts = {
        str(item.get("text") or "").strip().lower()
        for item in merged
        if str(item.get("text") or "").strip()
    }
    seen_details = {
        str(detail).strip().lower()
        for item in merged
        for detail in (item.get("details") or [])
        if str(detail).strip()
    }
    next_index = len(merged) + 1
    for research_item in research_items:
        title = str(research_item.get("text") or "").strip()
        details = [
            str(detail).strip()
            for detail in (research_item.get("details") or [])
            if str(detail).strip() and str(detail).strip().lower() not in seen_details
        ]
        if title.lower() in seen_texts and not details:
            continue
        merged.append(
            {
                "ac_id": f"AC-{next_index:03d}",
                "story_id": "",
                "theme": str(research_item.get("theme") or "research"),
                "text": title,
                "details": details,
                "source": str(research_item.get("source") or research_source),
            }
        )
        seen_texts.add(title.lower())
        seen_details.update(detail.lower() for detail in details)
        next_index += 1
    return merged


def extract_story_sections(content: str, source: str) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    if not str(content or "").strip():
        return sections

    current: dict[str, Any] | None = None
    collect_acceptance = False
    for raw_line in str(content or "").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        section_match = _SECTION_RE.match(stripped)
        if section_match:
            if current:
                sections.append(current)
            current = {
                "story_id": section_match.group(1).upper(),
                "title": section_match.group(2).strip(),
                "acceptance_criteria": [],
                "source": source,
            }
            collect_acceptance = False
            continue

        if current is None:
            continue

        if stripped.startswith("## "):
            sections.append(current)
            current = None
            collect_acceptance = False
            continue

        if stripped.startswith("### "):
            collect_acceptance = stripped.startswith("### 验收标准")
            continue

        if collect_acceptance and stripped.startswith("- [ ] "):
            current["acceptance_criteria"].append(stripped[len("- [ ] ") :].strip())
            continue

        if collect_acceptance and stripped.startswith("- "):
            current["acceptance_criteria"].append(stripped[2:].strip())
            continue

    if current:
        sections.append(current)
    return sections


def story_id_from_tc_id(tc_id: str) -> str:
    text = str(tc_id or "").strip().upper()
    match = re.match(r"^TC-US(\d{3})-", text)
    if match:
        return f"US-{match.group(1)}"
    match = re.match(r"^TC-RG(\d{3})-", text)
    if match:
        return f"RG-{match.group(1)}"
    match = re.match(r"^TC-DB(\d{3})-", text)
    if match:
        return f"CR-DB-{match.group(1)}"
    return ""


def extract_qa_case_rows(content: str, source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not str(content or "").strip():
        return rows

    for raw_line in str(content or "").splitlines():
        stripped = raw_line.strip()
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 5:
            continue
        first = cells[0].upper()
        second = cells[1].upper()

        if first.startswith("TC-"):
            tc_id = first
            story_id = story_id_from_tc_id(tc_id)
            rows.append(
                {
                    "tc_id": tc_id,
                    "story_id": story_id,
                    "case_type": cells[1],
                    "scenario": cells[2],
                    "steps": cells[3],
                    "expected_result": cells[4],
                    "execution": cells[5],
                    "source": source,
                }
            )
            continue

        if first.startswith("AC-") and second.startswith("TC-"):
            tc_id = second
            story_id = story_id_from_tc_id(tc_id)
            explicit_evidence_path = cells[5] if len(cells) > 5 else ""
            rows.append(
                {
                    "ac_id": first,
                    "tc_id": tc_id,
                    "story_id": story_id,
                    "case_type": cells[2],
                    "scenario": cells[4],
                    "steps": "",
                    "expected_result": cells[4],
                    "execution": cells[3],
                    "explicit_layer": cells[2],
                    "explicit_command": cells[3],
                    "explicit_assertion": cells[4],
                    "explicit_evidence_path": explicit_evidence_path,
                    "source": source,
                }
            )
    return rows


def build_feature_ac_items(
    *,
    user_story_content: str,
    prd_content: str = "",
    qa_content: str = "",
    research_content: str = "",
    user_story_source: str = "user-story",
    prd_source: str = "prd",
    qa_source: str = "qa:test-cases",
    research_source: str = "research",
) -> list[dict[str, Any]]:
    explicit = extract_explicit_ac_items(user_story_content, user_story_source)
    explicit.extend(extract_explicit_ac_items(prd_content, prd_source))
    if explicit:
        deduped = _dedupe_explicit_ac_items(explicit)
        return _merge_research_closure_items(
            deduped,
            research_content=research_content,
            research_source=research_source,
        )

    sections = extract_story_sections(user_story_content, user_story_source)
    if not sections:
        sections = extract_story_sections(prd_content, prd_source)

    known_story_ids = {str(section.get("story_id") or "").strip().upper() for section in sections}
    for row in extract_qa_case_rows(qa_content, qa_source):
        story_id = str(row.get("story_id") or "").strip().upper()
        if not story_id or story_id in known_story_ids:
            continue
        sections.append(
            {
                "story_id": story_id,
                "title": str(row.get("scenario") or story_id).strip(),
                "acceptance_criteria": [str(row.get("expected_result") or "").strip()] if str(row.get("expected_result") or "").strip() else [],
                "source": qa_source,
            }
        )
        known_story_ids.add(story_id)

    items: list[dict[str, Any]] = []
    for index, section in enumerate(sections, start=1):
        story_id = str(section.get("story_id") or "").strip().upper()
        title = str(section.get("title") or story_id or f"Story {index}").strip()
        acceptance = [str(item).strip() for item in (section.get("acceptance_criteria") or []) if str(item).strip()]
        items.append(
            {
                "ac_id": f"AC-{index:03d}",
                "story_id": story_id,
                "theme": story_id or "general",
                "text": title,
                "details": acceptance,
                "source": str(section.get("source") or user_story_source),
            }
        )
    return _merge_research_closure_items(
        items,
        research_content=research_content,
        research_source=research_source,
    )
