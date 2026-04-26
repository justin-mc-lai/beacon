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


def _grouped_bullet_sections(lines: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    current_title = ""
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines
        if not current_title:
            return
        groups[current_title] = _bullet_lines(current_lines)
        current_lines = []

    for raw in lines:
        level = _heading_level(raw)
        if level is not None:
            flush()
            current_title = _heading_title(raw).strip()
            groups.setdefault(current_title, [])
            continue
        if current_title:
            current_lines.append(raw)
    flush()
    return {key: _dedupe_preserve(value) for key, value in groups.items() if key.strip()}


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

    entry_point_groups = _grouped_bullet_sections(entry_points_body)
    flattened_entry_points = _dedupe_preserve(
        [item for values in entry_point_groups.values() for item in values if str(item).strip()]
    )

    return {
        "services": list(services.values()),
        "entry_points": flattened_entry_points,
        "entry_point_groups": entry_point_groups,
        "takeover_findings": _bullet_lines(findings_body),
        "target_handoff": _bullet_lines(handoff_body),
    }


def parse_refactor_boundaries(content: str) -> dict[str, list[str]]:
    lines = _normalize_lines(content.splitlines())
    parsed: dict[str, list[str]] = {}
    for title, key in _REFRACTOR_SECTION_KEYS.items():
        parsed[key] = _bullet_lines(_section_body(lines, title_matches={title}))
    return parsed


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = str(text or "").lower()
    return any(term.lower() in lowered for term in terms)


def _slice_tags(section: dict[str, Any], matched_services: list[str], reference_services: list[str]) -> set[str]:
    source_text = " ".join(
        [
            str(section.get("feature_id", "") or ""),
            str(section.get("title", "") or ""),
            str(section.get("description", "") or ""),
            " ".join(str(item) for item in section.get("bullets", []) if str(item).strip()),
        ]
    )
    tags: set[str] = set()
    if _has_any(source_text, ("审核", "审批", "partner_level", "推荐合伙人", "直属推荐", "审批页")):
        tags.update({"approval", "admin", "relation"})
    if _has_any(source_text, ("分成", "收益比例", "奖励比例", "编辑开关", "override", "配置中心")):
        tags.update({"commission_config", "admin"})
    if _has_any(
        source_text,
        ("客户状态", "保护期", "可再分配", "直接绑定客户", "间接绑定客户", "归属切换", "转移至b", "客户列表"),
    ):
        tags.update({"state", "customer"})
    if _has_any(source_text, ("手机号", "脱敏", "拨号", "可见")):
        tags.update({"phone", "customer", "h5"})
    if _has_any(source_text, ("h5", "首页", "客户详情", "客户列表", "业绩详情", "看板", "累计业绩", "当月业绩", "详情页")):
        tags.update({"h5", "performance"})
    if _has_any(source_text, ("订单", "成交", "消费", "销售链接", "outbox", "replay", "支付")):
        tags.update({"order"})
    if _has_any(source_text, ("推荐奖励", "下级合伙人", "奖励", "commission-svr", "收益明细")):
        tags.update({"reward"})
    if "marketing_primary_fe" in matched_services:
        tags.add("admin")
    if "marketing_distributor_fe" in matched_services:
        tags.add("h5")
    if "order-svr" in matched_services:
        tags.add("order")
    if "commission-svr" in reference_services:
        tags.add("reward")
    return tags


def _backtick_identifiers(section: dict[str, Any]) -> list[str]:
    raw = " ".join(
        [
            str(section.get("title", "") or ""),
            str(section.get("description", "") or ""),
            " ".join(str(item) for item in section.get("bullets", []) if str(item).strip()),
        ]
    )
    return _dedupe_preserve([token.strip() for token in _BACKTICK_RE.findall(raw) if token.strip()])


def _matching_entry_points(
    *,
    entry_point_groups: dict[str, list[str]],
    tags: set[str],
    matched_services: list[str],
) -> list[str]:
    selected: list[str] = []
    for title, items in entry_point_groups.items():
        normalized_title = str(title or "").lower()
        if ("admin" in tags or "marketing_primary_fe" in matched_services) and (
            "后台" in title or "admin" in normalized_title
        ):
            selected.extend(items[:4])
        if ("h5" in tags or "marketing_distributor_fe" in matched_services) and (
            "h5" in normalized_title or "客户" in title or "首页" in title
        ):
            selected.extend(items[:4])
        if ("order" in tags or "order-svr" in matched_services) and (
            "订单" in title or "分佣" in title or "commission" in normalized_title
        ):
            selected.extend(items[:4])
    if selected:
        return _dedupe_preserve(selected)
    fallback: list[str] = []
    if "admin" in tags:
        fallback.append("后台审批 / 配置入口")
    if "h5" in tags:
        fallback.append("H5 首页 / 客户列表 / 详情入口")
    if "order" in tags or "reward" in tags:
        fallback.append("订单支付 / 佣金回放 / 分佣入口")
    return _dedupe_preserve(fallback)


def _implementation_focus(tags: set[str]) -> list[str]:
    focus: list[str] = []
    if "approval" in tags:
        focus.append("审批合同扩展与直属推荐关系建立")
    if "commission_config" in tags:
        focus.append("四类分成规则合同与个人 override 编辑开关")
    if "state" in tags:
        focus.append("客户归属状态机、保护期与跨合伙人转移投影")
    if "phone" in tags:
        focus.append("手机号可见策略服务端化")
    if "performance" in tags:
        focus.append("H5 / 后台业绩详情聚合读模型")
    if "reward" in tags:
        focus.append("奖励归属口径与 commission-svr 下游事实对齐")
    if "order" in tags:
        focus.append("订单归因快照与收益事件链升级")
    return _dedupe_preserve(focus)


def _write_path(
    *,
    tags: set[str],
    matched_services: list[str],
    reference_services: list[str],
) -> list[str]:
    steps: list[str] = []
    if "approval" in tags:
        steps.append("marketing_primary_fe 审批页 / 配置页提交合同 -> marketing_sys 后台 API -> 合伙人审批域服务 -> 合伙人主数据与推荐关系存储")
    if "commission_config" in tags:
        steps.append("marketing_primary_fe 分成配置操作 -> marketing_sys 配置 API -> 分成规则域服务 -> 全局规则 / 个人 override 存储")
    if "state" in tags:
        steps.append("注册 / 分享 / 绑定触发 -> marketing_sys 绑定上下文与归属域服务 -> 客户归属状态投影 / 保护期结果写入")
    if "order" in tags:
        steps.append("订单支付 / 回放触发 -> order-svr 归因服务 -> 订单归因快照 -> commission outbox / 下游收益事件")
    if "reward" in tags and "commission-svr" in reference_services:
        steps.append("order-svr 收益事件 -> commission-svr 生成奖励类事实 -> 上游仅回读结果不自行重算")
    return _dedupe_preserve(steps)


def _read_path(
    *,
    tags: set[str],
    matched_services: list[str],
    reference_services: list[str],
) -> list[str]:
    steps: list[str] = []
    if "h5" in tags or "marketing_distributor_fe" in matched_services:
        steps.append("marketing_distributor_fe -> marketing_sys 合伙人读接口 -> 客户 / 业绩聚合读模型 -> 返回 H5")
    if "admin" in tags or "marketing_primary_fe" in matched_services:
        steps.append("marketing_primary_fe -> marketing_sys 后台详情 / 配置读接口 -> 聚合配置与看板读模型 -> 返回后台")
    if "performance" in tags and ("order" in tags or "reward" in tags or "commission-svr" in reference_services):
        steps.append("marketing_sys 聚合 order-svr 订单级明细与 commission-svr 奖励类明细 -> 输出 H5 / 后台详情")
    return _dedupe_preserve(steps)


def _storage_changes(section: dict[str, Any], *, tags: set[str]) -> list[str]:
    changes: list[str] = []
    identifiers = _backtick_identifiers(section)
    if "approval" in tags:
        approval_fields = [item for item in identifiers if item in {"partner_level", "recommender_partner_id", "source_type", "sales_person_id"}]
        if approval_fields:
            changes.append(f"合伙人主数据需落库：{', '.join(f'`{item}`' for item in approval_fields)}。")
        else:
            changes.append("合伙人主数据需要补充等级、推荐关系和来源信息存储。")
    if "commission_config" in tags:
        changes.append("分成配置需要从 direct / indirect 双字段升级为四类收益合同，并持久化个人 override 编辑开关。")
    if "state" in tags:
        changes.append("客户归属快照 / 读模型需要补充保护期状态、当前归属状态、转移结果和首单后归属结论。")
    if "phone" in tags:
        changes.append("客户读模型需要显式存储或投影手机号可见策略，不能只返回单一 `phone` 展示值。")
    if "performance" in tags:
        changes.append("业绩详情读模型需要区分订单型明细与奖励型明细来源，并保留允许展示的收益类型结果。")
    return _dedupe_preserve(changes)


def _derived_rules(section: dict[str, Any], *, tags: set[str]) -> list[str]:
    bullets = [str(item).strip() for item in section.get("bullets", []) if str(item).strip()]
    if bullets:
        return _dedupe_preserve(bullets[:6])
    fallback = _implementation_focus(tags)
    return _dedupe_preserve(fallback[:4])


def _downstream_contracts(
    *,
    tags: set[str],
    matched_services: list[str],
    reference_services: list[str],
) -> list[str]:
    contracts: list[str] = []
    if "order" in tags or "order-svr" in matched_services:
        contracts.append("marketing_sys / 前端展示口径必须与 order-svr 订单归因快照一致。")
    if "reward" in tags or "commission-svr" in reference_services:
        contracts.append("奖励类明细以 commission-svr 产出的事实为准，上游不得根据归因或费率自行拼装。")
    if "performance" in tags:
        contracts.append("H5 与后台看板共享金额入口与基础字段结构，但允许详情类型白名单不同。")
    return _dedupe_preserve(contracts)


def _compatibility_notes(refactor: dict[str, list[str]], *, tags: set[str]) -> list[str]:
    notes = refactor.get("compatibility_rules") if isinstance(refactor.get("compatibility_rules"), list) else []
    selected: list[str] = []
    for note in notes:
        text = str(note).strip()
        lowered = text.lower()
        if not text:
            continue
        if ("state" in tags or "order" in tags) and ("direct" in lowered or "indirect" in lowered or "第三状态" in text):
            selected.append(text)
        if ("phone" in tags or "h5" in tags) and ("phone" in lowered or "手机号" in text):
            selected.append(text)
        if ("reward" in tags or "performance" in tags) and ("奖励" in text or "明细" in text):
            selected.append(text)
    return _dedupe_preserve(selected[:4] or notes[:3])


def _rollout_notes(refactor: dict[str, list[str]], *, tags: set[str]) -> list[str]:
    notes = refactor.get("delivery_constraints") if isinstance(refactor.get("delivery_constraints"), list) else []
    selected: list[str] = []
    for note in notes:
        text = str(note).strip()
        lowered = text.lower()
        if not text:
            continue
        if ("commission_config" in tags or "approval" in tags) and (
            "php bin/hyperf.php" in lowered or "双字段" in text or "配置" in text
        ):
            selected.append(text)
        if ("state" in tags or "order" in tags) and ("protect" in lowered or "保护期" in text or "direct/indirect" in lowered or "db:migrate" in lowered):
            selected.append(text)
        if ("reward" in tags or "performance" in tags) and ("接口文档" in text or "对外协同" in text):
            selected.append(text)
    return _dedupe_preserve(selected[:4] or notes[:3])


def _verification_focus(tags: set[str]) -> list[str]:
    checks: list[str] = []
    if "approval" in tags:
        checks.append("审批后等级、推荐关系与默认模板回读必须一致；未选推荐人时不得自动反推。")
    if "commission_config" in tags:
        checks.append("编辑开关关闭时个人配置不可编辑且实际收益继承全局；开启后才允许 override。")
    if "state" in tags:
        checks.append("90 天保护期、间接转直接、可再分配转移到 B 的状态机路径必须全部覆盖。")
    if "phone" in tags:
        checks.append("首单前后手机号可见策略、查看完整号码权限与拨号入口必须一致。")
    if "performance" in tags:
        checks.append("H5 与后台详情的金额入口要一致，但类型白名单需要按冻结需求分别校验。")
    if "reward" in tags:
        checks.append("推荐奖励 / 下级奖励必须来自下游事实，不允许本仓重新计算奖励事件。")
    return _dedupe_preserve(checks)


def _change_axes(tags: set[str]) -> list[str]:
    axes: list[str] = []
    if "approval" in tags or "commission_config" in tags:
        axes.extend(["admin interaction", "write contract", "domain model"])
    if "state" in tags:
        axes.extend(["state machine", "write path", "read model"])
    if "phone" in tags:
        axes.extend(["visibility policy", "read model"])
    if "performance" in tags:
        axes.extend(["read model", "api contract"])
    if "order" in tags or "reward" in tags:
        axes.extend(["event contract", "downstream integration"])
    return _dedupe_preserve(axes)


def _mermaid_chain(
    *,
    tags: set[str],
    matched_services: list[str],
    reference_services: list[str],
) -> str:
    lines = ["```mermaid", "flowchart LR"]
    lines.append('  entry["触发入口"]')
    if "admin" in tags and "marketing_primary_fe" in matched_services:
        lines.append('  primary["marketing_primary_fe\\n后台审批 / 配置页"]')
        lines.append("  entry --> primary")
        previous = "primary"
    elif "h5" in tags and "marketing_distributor_fe" in matched_services:
        lines.append('  distributor["marketing_distributor_fe\\nH5 首页 / 客户列表 / 详情"]')
        lines.append("  entry --> distributor")
        previous = "distributor"
    elif "order" in tags and "order-svr" in matched_services:
        lines.append('  order["order-svr\\n订单归因 / 回放入口"]')
        lines.append("  entry --> order")
        previous = "order"
    else:
        previous = "entry"
    if "marketing_sys" in matched_services:
        lines.append('  marketing["marketing_sys\\n域服务 / 聚合读模型"]')
        lines.append(f"  {previous} --> marketing")
        previous = "marketing"
    if "state" in tags:
        lines.append('  store["客户归属状态 / 保护期投影"]')
        lines.append(f"  {previous} --> store")
        previous = "store"
    elif "approval" in tags or "commission_config" in tags:
        lines.append('  store["合伙人 / 推荐关系 / 分成配置存储"]')
        lines.append(f"  {previous} --> store")
        previous = "store"
    elif "performance" in tags:
        lines.append('  store["业绩聚合读模型"]')
        lines.append(f"  {previous} --> store")
        previous = "store"
    if "order-svr" in matched_services and previous != "order":
        lines.append('  order["order-svr\\n归因快照 / 订单明细"]')
        lines.append(f"  {previous} -.查询 / 事件.-> order")
    if "commission-svr" in reference_services or "reward" in tags:
        lines.append('  commission["commission-svr\\n奖励事实 / 结算明细"]')
        anchor = "order" if "order-svr" in matched_services else previous
        lines.append(f"  {anchor} -.下游收益事件 / 奖励结果.-> commission")
    if "h5" in tags or "performance" in tags or "phone" in tags:
        lines.append('  output["H5 / 后台详情返回"]')
        lines.append(f"  {previous} --> output")
    lines.append("```")
    return "\n".join(lines)


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
    current_state: dict[str, Any],
    refactor: dict[str, list[str]],
    service_catalog: list[dict[str, Any]],
    direct_delivery_services: list[str],
    reference_only_services: list[str],
) -> list[dict[str, Any]]:
    service_map = {str(item.get("service", "")).strip(): item for item in service_catalog if str(item.get("service", "")).strip()}
    surfaces: list[dict[str, Any]] = []
    all_services = _dedupe_preserve(direct_delivery_services + reference_only_services)
    entry_point_groups = {
        str(key): [str(item) for item in values if str(item).strip()]
        for key, values in current_state.get("entry_point_groups", {}).items()
    } if isinstance(current_state.get("entry_point_groups"), dict) else {}
    refactor = refactor if isinstance(refactor, dict) else {}
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
        tags = _slice_tags(section, direct_matches, reference_matches)
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
                "entry_points": _matching_entry_points(
                    entry_point_groups=entry_point_groups,
                    tags=tags,
                    matched_services=direct_matches,
                ),
                "implementation_focus": _implementation_focus(tags),
                "write_path": _write_path(tags=tags, matched_services=direct_matches, reference_services=reference_matches),
                "read_path": _read_path(tags=tags, matched_services=direct_matches, reference_services=reference_matches),
                "storage_changes": _storage_changes(section, tags=tags),
                "derived_rules": _derived_rules(section, tags=tags),
                "downstream_contracts": _downstream_contracts(
                    tags=tags,
                    matched_services=direct_matches,
                    reference_services=reference_matches,
                ),
                "compatibility_notes": _compatibility_notes(refactor, tags=tags),
                "rollout_notes": _rollout_notes(refactor, tags=tags),
                "verification_focus": _verification_focus(tags),
                "change_axes": _change_axes(tags),
                "call_chain_diagram": _mermaid_chain(
                    tags=tags,
                    matched_services=direct_matches,
                    reference_services=reference_matches,
                ),
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
        current_state=current_state,
        refactor=refactor,
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
