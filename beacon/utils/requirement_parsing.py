"""Requirement material parsing helpers for human-authored Beacon docs."""

from __future__ import annotations

import re
from typing import Any

_SECTION_RE = re.compile(
    r"^##\s+((?:US|RG)-\d{3}|CR-[A-Z0-9-]+)\s*[：:]\s*(.+?)\s*$",
    flags=re.IGNORECASE,
)


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
        if not stripped.startswith("| TC-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 6:
            continue
        tc_id = cells[0]
        if not tc_id.upper().startswith("TC-"):
            continue
        story_id = story_id_from_tc_id(tc_id)
        rows.append(
            {
                "tc_id": tc_id.upper(),
                "story_id": story_id,
                "case_type": cells[1],
                "scenario": cells[2],
                "steps": cells[3],
                "expected_result": cells[4],
                "execution": cells[5],
                "source": source,
            }
        )
    return rows


def build_feature_ac_items(
    *,
    user_story_content: str,
    prd_content: str = "",
    qa_content: str = "",
    user_story_source: str = "user-story",
    prd_source: str = "prd",
    qa_source: str = "qa:test-cases",
) -> list[dict[str, Any]]:
    explicit = extract_explicit_ac_items(user_story_content, user_story_source)
    explicit.extend(extract_explicit_ac_items(prd_content, prd_source))
    if explicit:
        return _dedupe_explicit_ac_items(explicit)

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
    return items
