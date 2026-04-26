"""Shared parsers and derivations for human technical implementation design."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beacon.utils.governance import load_project_mode, takeover_baseline_paths
from beacon.utils.story_state import feature_slug
from beacon.utils.versioning import resolve_target_version


_HEADING_RE = re.compile(r"^(#{2,6})\s+(.+?)\s*$")
_FEATURE_HEADING_RE = re.compile(r"^(?:\d+(?:\.\d+)*)?\s*(F\d+)\s+(.+?)\s*$", flags=re.I)
_BACKTICK_RE = re.compile(r"`([^`]+)`")

_REFRACTOR_SECTION_KEYS = {
    "must change": "must_change",
    "can reuse": "can_reuse",
    "must not change in v1.3.3": "must_not_change",
    "must not change": "must_not_change",
    "compatibility rules": "compatibility_rules",
    "delivery constraints": "delivery_constraints",
    "baseline verdict": "baseline_verdict",
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _normalize_lines(lines: list[str]) -> list[str]:
    return [str(line.rstrip()) for line in lines]


def _heading_level(line: str) -> int | None:
    match = _HEADING_RE.match(str(line or "").strip())
    if not match:
        return None
    return len(match.group(1))


def _heading_title(line: str) -> str:
    match = _HEADING_RE.match(str(line or "").strip())
    return str(match.group(2)).strip() if match else ""


def _section_body(lines: list[str], *, title_matches: set[str]) -> list[str]:
    active = False
    section_level = 0
    body: list[str] = []
    normalized_titles = {title.lower() for title in title_matches}
    for raw in lines:
        level = _heading_level(raw)
        if level is not None:
            title = _heading_title(raw).lower().rstrip(":：")
            if not active and title in normalized_titles:
                active = True
                section_level = level
                continue
            if active and level <= section_level:
                break
        if active:
            body.append(raw)
    return _normalize_lines(body)


def _bullet_lines(lines: list[str]) -> list[str]:
    items: list[str] = []
    for raw in lines:
        stripped = str(raw or "").strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ", "+ ")):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+[.)]\s+", stripped):
            items.append(re.sub(r"^\d+[.)]\s+", "", stripped).strip())
    return items


def _dedupe_preserve(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def extract_prd_feature_sections(content: str) -> list[dict[str, Any]]:
    lines = _normalize_lines(content.splitlines())
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def flush() -> None:
        nonlocal current
        if not current:
            return
        body_lines = [line for line in current.pop("_body", []) if str(line).strip()]
        bullets = _bullet_lines(body_lines)
        paragraphs = [
            str(line).strip()
            for line in body_lines
            if str(line).strip()
            and not str(line).strip().startswith(("- ", "* ", "+ "))
            and not str(line).strip().startswith("|")
        ]
        description = " / ".join(bullets[:3]) if bullets else " ".join(paragraphs[:3]).strip()
        current["bullets"] = bullets
        current["description"] = description or current.get("title", "")
        current["raw_text"] = "\n".join(body_lines).strip()
        sections.append(current)
        current = None

    for raw in lines:
        heading = _HEADING_RE.match(raw.strip())
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            normalized = re.sub(r"^\d+(?:\.\d+)*\s+", "", title).strip()
            feature_match = _FEATURE_HEADING_RE.match(normalized)
            if feature_match:
                flush()
                current = {
                    "feature_id": feature_match.group(1).upper(),
                    "title": feature_match.group(2).strip(),
                    "heading": normalized,
                    "level": level,
                    "_body": [],
                }
                continue
            if current and level <= int(current.get("level", 99)):
                flush()
                current = None
        if current:
            current["_body"].append(raw)
    flush()
    return sections


def parse_current_state_service_map(content: str) -> dict[str, Any]:
    lines = _normalize_lines(content.splitlines())
    primary_body = _section_body(lines, title_matches={"primary systems"})
    entry_points_body = _section_body(lines, title_matches={"current entry points"})
    findings_body = _section_body(lines, title_matches={"takeover findings"})
    handoff_body = _section_body(lines, title_matches={"target handoff for implement"})

    services: dict[str, dict[str, Any]] = {}
    current_service = ""
    for raw in primary_body:
        if raw.startswith("- `"):
            match = re.match(r"^-\s+`([^`]+)`", raw)
            if not match:
                continue
            current_service = match.group(1).strip()
            services.setdefault(current_service, {"service": current_service, "summary": [], "modules": []})
            continue
        if current_service and raw.startswith("  -"):
            services[current_service]["summary"].append(raw.strip()[2:].strip())

    current_fact_body = _section_body(lines, title_matches={"current fact sources"})
    current_service = ""
    for raw in current_fact_body:
        stripped = raw.strip()
        if raw.startswith("- `") and stripped.endswith(":"):
            match = re.match(r"^-\s+`([^`]+)`", raw)
            if not match:
                continue
            current_service = match.group(1).strip()
            services.setdefault(current_service, {"service": current_service, "summary": [], "modules": []})
            continue
        if current_service and raw.startswith("  -"):
            text = raw.strip()[2:].strip()
            modules = [
                token.strip()
                for token in _BACKTICK_RE.findall(text)
                if "/" in token or "\\" in token or "::" in token or token.startswith("App\\") or token.startswith("src/")
            ]
            if modules:
                services[current_service]["modules"].extend(modules)
            else:
                services[current_service]["summary"].append(text)

    for service in services.values():
        service["summary"] = _dedupe_preserve(service.get("summary", []))
        service["modules"] = _dedupe_preserve(service.get("modules", []))

    return {
        "services": list(services.values()),
        "entry_points": _bullet_lines(entry_points_body),
        "takeover_findings": _bullet_lines(findings_body),
        "target_handoff": _bullet_lines(handoff_body),
    }


def parse_refactor_boundaries(content: str) -> dict[str, list[str]]:
    lines = _normalize_lines(content.splitlines())
    parsed: dict[str, list[str]] = {}
    for title, key in _REFRACTOR_SECTION_KEYS.items():
        parsed[key] = _bullet_lines(_section_body(lines, title_matches={title}))
    return parsed


def _service_aliases(service: str, summary: list[str]) -> list[str]:
    normalized = str(service or "").strip().lower()
    aliases = [normalized]
    if normalized == "marketing_sys":
        aliases.extend(["营销后台", "后台", "审批", "分成配置", "关系链", "手机号", "聚合读模型", "看板"])
    elif normalized == "marketing_primary_fe":
        aliases.extend(["营销后台", "后台", "审批页", "配置页", "详情页", "看板"])
    elif normalized == "marketing_distributor_fe":
        aliases.extend(["h5", "合伙人平台", "客户列表", "客户详情", "首页", "前台"])
    elif normalized == "order-svr":
        aliases.extend(["订单", "归因", "outbox", "订单级", "replay", "佣金详情"])
    elif normalized == "commission-svr":
        aliases.extend(["佣金", "奖励", "结算", "收益", "推荐奖励", "下级合伙人业绩奖励", "下游"])
    aliases.extend(item for item in summary if 2 <= len(item) <= 32)
    return _dedupe_preserve(aliases)


def derive_feature_change_surface(
    feature_sections: list[dict[str, Any]],
    *,
    service_catalog: list[dict[str, Any]],
    direct_delivery_services: list[str],
    reference_only_services: list[str],
) -> list[dict[str, Any]]:
    service_map = {str(item.get("service", "")).strip(): item for item in service_catalog if str(item.get("service", "")).strip()}
    surfaces: list[dict[str, Any]] = []
    all_services = _dedupe_preserve(direct_delivery_services + reference_only_services)
    for index, section in enumerate(feature_sections, start=1):
        source_text = " ".join(
            [
                str(section.get("feature_id", "") or ""),
                str(section.get("title", "") or ""),
                str(section.get("description", "") or ""),
                " ".join(str(item) for item in section.get("bullets", []) if str(item).strip()),
            ]
        ).lower()
        matched: list[str] = []
        for service_name, info in service_map.items():
            aliases = _service_aliases(service_name, info.get("summary", []) if isinstance(info.get("summary"), list) else [])
            if any(alias.lower() in source_text for alias in aliases if alias):
                matched.append(service_name)
        if not matched:
            matched = list(direct_delivery_services or all_services or ["."])
        direct_matches = [service for service in matched if service in direct_delivery_services]
        reference_matches = [service for service in matched if service in reference_only_services]
        module_candidates: list[str] = []
        for service_name in direct_matches:
            info = service_map.get(service_name, {})
            module_candidates.extend(info.get("modules", []) if isinstance(info.get("modules"), list) else [])
            if not module_candidates:
                module_candidates.append(service_name)
        target_modules = _dedupe_preserve(module_candidates or direct_matches or list(direct_delivery_services or ["."]))
        surfaces.append(
            {
                "slice_id": str(section.get("feature_id", "") or f"SLICE-{index:03d}"),
                "heading": str(section.get("heading", "") or ""),
                "title": str(section.get("title", "") or ""),
                "description": str(section.get("description", "") or ""),
                "bullets": [str(item) for item in section.get("bullets", []) if str(item).strip()],
                "direct_delivery_services": _dedupe_preserve(direct_matches or list(direct_delivery_services or ["."])),
                "reference_only_services": _dedupe_preserve(reference_matches),
                "target_modules": target_modules,
            }
        )
    return surfaces


def build_technical_delta(
    project_root: Path,
    *,
    version: str,
    feature: str,
    direct_delivery_services: list[str],
    reference_only_services: list[str],
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    docs_root = project_root / "docs" / "beacon" / resolved_version
    slug = feature_slug(feature)
    prd_path = docs_root / "prd" / f"{slug}.md"
    user_story_path = docs_root / "user-story" / f"{slug}.md"
    test_case_path = docs_root / "qa" / "test-cases" / f"{slug}.md"
    takeover_paths = takeover_baseline_paths(project_root, version=resolved_version)
    prd_content = _read_text(prd_path)
    current_state_content = _read_text(takeover_paths["current_state_service_map"])
    refactor_content = _read_text(takeover_paths["refactor_boundaries"])

    feature_sections = extract_prd_feature_sections(prd_content)
    current_state = parse_current_state_service_map(current_state_content) if current_state_content.strip() else {}
    refactor = parse_refactor_boundaries(refactor_content) if refactor_content.strip() else {}
    service_catalog = current_state.get("services") if isinstance(current_state.get("services"), list) else []
    change_surface = derive_feature_change_surface(
        feature_sections,
        service_catalog=service_catalog,
        direct_delivery_services=direct_delivery_services,
        reference_only_services=reference_only_services,
    )

    refs: dict[str, str] = {}
    for key, path in (
        ("prd", prd_path),
        ("user_story", user_story_path),
        ("test_case", test_case_path),
        ("current_state_service_map", takeover_paths["current_state_service_map"]),
        ("refactor_boundaries", takeover_paths["refactor_boundaries"]),
    ):
        if path.exists():
            refs[key] = str(path.relative_to(project_root))

    return {
        "project_mode": load_project_mode(project_root),
        "source_refs": refs,
        "current_state": current_state,
        "refactor_boundaries": refactor,
        "feature_sections": feature_sections,
        "change_surface": change_surface,
    }

