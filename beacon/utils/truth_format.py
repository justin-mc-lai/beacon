"""Truth format validation for v1.4.12+.

Validates structure (mandatory sections, no numbering, table columns),
language consistency (content vs Language field), and mermaid block presence.
"""

from __future__ import annotations

import re
from typing import Any


# Mandatory sections for each document type (all use no-numbering English names)
PRD_MANDATORY_SECTIONS = [
    "Overview",
    "Outline",
    "Problem",
    "Goals",
    "Scope",
    "Functional Requirements",
    "Acceptance Criteria",
    "Non-Goals",
    "Success Metrics",
]

USER_STORY_MANDATORY_SECTIONS = [
    "Story",
    "Outline",
    "Acceptance Criteria",
    "Test Story Map",
    "References",
]

TEST_CASE_MANDATORY_SECTIONS = [
    "Outline",
    "Coverage Matrix",
    "Explicit Non Coverage",
]

# Numbering pattern: ## 1. or ### 1.1 etc
_NUMBERING_RE = re.compile(r"^#{2,6}\s+\d+\.")


def _extract_sections(content: str) -> list[str]:
    """Extract all ## level section names from markdown content."""
    sections: list[str] = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## ") and not line.startswith("### "):
            # Remove ## prefix and any trailing content
            title = line[3:].strip()
            sections.append(title)
    return sections


def _has_numbering_prefix(content: str) -> list[str]:
    """Find lines with numbering prefixes like ## 1. or ### 1.1"""
    findings: list[str] = []
    for line in content.split("\n"):
        if _NUMBERING_RE.match(line):
            findings.append(line.strip())
    return findings


def _has_mermaid_block(content: str, section: str = "") -> bool:
    """Check if content contains a ```mermaid code block."""
    return "```mermaid" in content


def _extract_front_matter(content: str) -> dict[str, str]:
    """Extract **Key**: `value` pairs from the beginning of markdown content."""
    result: dict[str, str] = {}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("**") and "**:" in line:
            # Match patterns like **Feature**: `value`
            match = re.match(r"\*\*(\w+)\*\*:\s*`?([^`\n]+?)`?\s*$", line)
            if match:
                result[match.group(1)] = match.group(2).strip()
    return result


def _extract_body_text(content: str) -> str:
    """Extract body text excluding section headers, table headers, code blocks, URLs, file paths."""
    lines: list[str] = []
    in_code_block = False
    in_table_header = False
    for line in content.split("\n"):
        stripped = line.strip()
        # Skip code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # Skip section headers
        if stripped.startswith("## ") or stripped.startswith("### "):
            continue
        # Skip table separator rows
        if stripped.startswith("|") and all(c in "-| " for c in stripped):
            continue
        # Skip FILL comments
        if stripped.startswith("<!-- FILL"):
            continue
        # Skip URLs
        if re.match(r"https?://", stripped):
            continue
        # Skip file paths
        if stripped.startswith("docs/") or stripped.startswith(".machine/"):
            continue
        # Skip front matter
        if stripped.startswith("**") and "**:" in stripped:
            continue
        # Skip empty lines
        if not stripped:
            continue
        lines.append(stripped)
    return " ".join(lines)


def detect_content_language(content: str) -> str:
    """Detect content language by counting Chinese character ratio.
    
    Returns "zh" if Chinese characters > 30%, otherwise "en".
    """
    body = _extract_body_text(content)
    if not body:
        return "en"
    chinese_count = sum(1 for ch in body if "\u4e00" <= ch <= "\u9fff")
    total = len(body)
    if total == 0:
        return "en"
    ratio = chinese_count / total
    return "zh" if ratio > 0.3 else "en"


def validate_prd_format(content: str, *, strict: bool = False) -> dict[str, Any]:
    """Validate PRD format compliance.
    
    Returns dict with status, checks, and issues list.
    """
    issues: list[str] = []

    # Check mandatory sections
    sections = _extract_sections(content)
    section_set = set(sections)
    for mandatory in PRD_MANDATORY_SECTIONS:
        if mandatory not in section_set:
            issues.append(f"missing_mandatory_section: {mandatory}")

    # Check for numbering prefixes
    numbering = _has_numbering_prefix(content)
    for line in numbering:
        issues.append(f"numbering_prefix_not_allowed: {line}")

    # Check front matter
    front_matter = _extract_front_matter(content)
    required_keys = ["Feature", "Version", "Status", "Date", "Language"]
    for key in required_keys:
        if key not in front_matter:
            issues.append(f"missing_front_matter: {key}")
    
    # Check Language value
    lang_value = front_matter.get("Language", "")
    if lang_value not in ("en", "zh", ""):
        issues.append(f"invalid_language_value: {lang_value}")

    # Check Outline has mermaid block
    if "Outline" in section_set:
        outline_section = _extract_section_content(content, "Outline")
        if outline_section and not _has_mermaid_block(outline_section):
            issues.append("missing_mermaid_block: Outline section must contain ```mermaid block")
    elif "Outline" not in section_set:
        # Already reported as missing_mandatory_section
        pass

    # Check FILL placeholders in non-template status
    status = front_matter.get("Status", "")
    if status != "template":
        fill_count = content.count("<!-- FILL:")
        if fill_count > 0:
            issues.append(f"residual_fill_placeholders: {fill_count} FILL comments remain in non-template document")

    # Check language consistency
    if lang_value in ("en", "zh"):
        detected = detect_content_language(content)
        if detected != lang_value:
            severity = "fail" if strict else "warn"
            issues.append(f"content_language_mismatch: declared={lang_value} detected={detected} ({severity})")

    # Check table columns
    if "| FR ID |" not in content and "Functional Requirements" in section_set:
        issues.append("table_column_mismatch: FR table must have columns FR ID | Related AC | Requirement")
    if "| Axis | States | Meaning |" not in content and "State Axes" in section_set:
        issues.append("table_column_mismatch: State Axes table must have columns Axis | States | Meaning")

    status_val = "pass" if not issues else "fail"
    if not strict:
        # Non-strict: only fail on missing mandatory or numbering
        critical_issues = [i for i in issues if i.startswith("missing_mandatory_") or i.startswith("numbering_prefix_") or i.startswith("missing_mermaid_")]
        status_val = "fail" if critical_issues else "pass"

    return {
        "status": status_val,
        "sections_found": sections,
        "mandatory_ok": all(s in section_set for s in PRD_MANDATORY_SECTIONS),
        "no_numbering": len(numbering) == 0,
        "front_matter_ok": all(k in front_matter for k in required_keys),
        "language_ok": lang_value in ("en", "zh"),
        "outline_mermaid_ok": "Outline" in section_set and _has_mermaid_block(_extract_section_content(content, "Outline") or ""),
        "issues": issues,
    }


def validate_user_story_format(content: str, *, strict: bool = False) -> dict[str, Any]:
    """Validate User Story format compliance."""
    issues: list[str] = []
    sections = _extract_sections(content)
    section_set = set(sections)

    for mandatory in USER_STORY_MANDATORY_SECTIONS:
        if mandatory not in section_set:
            issues.append(f"missing_mandatory_section: {mandatory}")

    numbering = _has_numbering_prefix(content)
    for line in numbering:
        issues.append(f"numbering_prefix_not_allowed: {line}")

    front_matter = _extract_front_matter(content)
    required_keys = ["Feature", "Version", "Status", "Date", "Language"]
    for key in required_keys:
        if key not in front_matter:
            issues.append(f"missing_front_matter: {key}")

    # AC table columns
    if "| AC ID | Theme | Description |" not in content:
        issues.append("table_column_mismatch: AC table must have columns AC ID | Theme | Description")

    # Outline mermaid
    if "Outline" in section_set:
        outline_section = _extract_section_content(content, "Outline")
        if outline_section and not _has_mermaid_block(outline_section):
            issues.append("missing_mermaid_block: Outline section must contain ```mermaid block")

    # Status check
    status = front_matter.get("Status", "")
    if status != "template":
        fill_count = content.count("<!-- FILL:")
        if fill_count > 0:
            issues.append(f"residual_fill_placeholders: {fill_count} FILL comments remain")

    # Language consistency
    lang_value = front_matter.get("Language", "")
    if lang_value in ("en", "zh"):
        detected = detect_content_language(content)
        if detected != lang_value:
            severity = "fail" if strict else "warn"
            issues.append(f"content_language_mismatch: declared={lang_value} detected={detected} ({severity})")

    status_val = "pass" if not issues else "fail"
    if not strict:
        critical = [i for i in issues if i.startswith("missing_mandatory_") or i.startswith("numbering_prefix_") or i.startswith("missing_mermaid_")]
        status_val = "fail" if critical else "pass"

    return {
        "status": status_val,
        "sections_found": sections,
        "mandatory_ok": all(s in section_set for s in USER_STORY_MANDATORY_SECTIONS),
        "no_numbering": len(numbering) == 0,
        "issues": issues,
    }


def validate_test_case_format(content: str, *, strict: bool = False) -> dict[str, Any]:
    """Validate Test Case format compliance."""
    issues: list[str] = []
    sections = _extract_sections(content)
    section_set = set(sections)

    for mandatory in TEST_CASE_MANDATORY_SECTIONS:
        if mandatory not in section_set:
            issues.append(f"missing_mandatory_section: {mandatory}")

    numbering = _has_numbering_prefix(content)
    for line in numbering:
        issues.append(f"numbering_prefix_not_allowed: {line}")

    front_matter = _extract_front_matter(content)
    required_keys = ["Feature", "Version", "Status", "Date", "Language"]
    for key in required_keys:
        if key not in front_matter:
            issues.append(f"missing_front_matter: {key}")

    # Coverage Matrix columns
    if "| AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path |" not in content:
        issues.append("table_column_mismatch: Coverage Matrix must have columns AC ID | TC ID | Layer | Planned Command | Assertion | Evidence Path")

    # Outline mermaid
    if "Outline" in section_set:
        outline_section = _extract_section_content(content, "Outline")
        if outline_section and not _has_mermaid_block(outline_section):
            issues.append("missing_mermaid_block: Outline section must contain ```mermaid block")

    # Language consistency
    lang_value = front_matter.get("Language", "")
    if lang_value in ("en", "zh"):
        detected = detect_content_language(content)
        if detected != lang_value:
            severity = "fail" if strict else "warn"
            issues.append(f"content_language_mismatch: declared={lang_value} detected={detected} ({severity})")

    status_val = "pass" if not issues else "fail"
    if not strict:
        critical = [i for i in issues if i.startswith("missing_mandatory_") or i.startswith("numbering_prefix_") or i.startswith("missing_mermaid_")]
        status_val = "fail" if critical else "pass"

    return {
        "status": status_val,
        "sections_found": sections,
        "mandatory_ok": all(s in section_set for s in TEST_CASE_MANDATORY_SECTIONS),
        "no_numbering": len(numbering) == 0,
        "issues": issues,
    }


def _extract_section_content(content: str, section_name: str) -> str | None:
    """Extract content between ## Section and next ## section."""
    lines = content.split("\n")
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if line.strip() == f"## {section_name}":
            in_section = True
            continue
        if in_section and line.strip().startswith("## ") and not line.strip() == f"## {section_name}":
            break
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines) if section_lines else None
