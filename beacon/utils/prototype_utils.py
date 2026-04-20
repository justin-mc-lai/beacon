"""Requirement-driven wireframe freeze utilities for Beacon prototype."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from beacon.utils.runtime_projection_store import runtime_ledger_root


PROTOTYPE_MODE = "wireframe"
PROTOTYPE_UI_KIT = "wireframe-markdown-v1"
SCHEMA_VERSION = "1.0"
REQUIRED_SOURCE_TYPES = ("user-story", "prd", "test-case")
AC_PATTERN = re.compile(r"\bAC-\d{3}[A-Z]?\b", re.IGNORECASE)
TC_PATTERN = re.compile(r"\bTC-\d{3}(?:-[A-Z]+)?\b", re.IGNORECASE)
PAGE_ORDER_DEFAULT = (
    "home",
    "management-overview",
    "project-detail",
    "runtime-center",
    "recovery-diagnostics",
    "material-viewer",
)

PAGE_CATALOG: dict[str, dict[str, Any]] = {
    "home": {
        "name": "首页",
        "keywords": ("首页", "首页首屏", "主页", "home"),
        "priority": "P0",
        "platforms": ["Web", "PC"],
        "responsibility": "先回答经营判断，展示项目数、阻塞数、当前交付和介入点。",
        "sections": [
            "经营总览条",
            "重点介入区",
            "项目推进摘要",
            "当前交付卡片",
            "下一步建议",
        ],
        "actions": [
            {"label": "查看管理总览", "target": "management-overview", "trigger": "点击项目组合入口"},
            {"label": "进入重点项目", "target": "project-detail", "trigger": "点击重点项目卡片"},
        ],
        "states": [
            {"id": "ready", "label": "正常总览", "description": "展示项目数、阻塞数、当前交付和下一步。"},
            {"id": "blocked", "label": "阻塞高亮", "description": "把阻塞项目和介入点提升到首屏。"},
            {"id": "intervention-needed", "label": "需介入", "description": "强调需要 CEO / 负责人介入的项目。"},
            {"id": "loading", "label": "加载中", "description": "首页摘要数据仍在汇总。"},
            {"id": "empty", "label": "空状态", "description": "当前没有受管项目。"},
            {"id": "error", "label": "错误", "description": "摘要聚合失败，但提示可以进入详情或 doctor。"},
        ],
    },
    "management-overview": {
        "name": "管理总览",
        "keywords": ("管理总览", "总览页", "项目组合概览", "组合概览", "portfolio overview", "overview"),
        "priority": "P0",
        "platforms": ["Web", "PC"],
        "responsibility": "提供多项目密集管理视图，稳定扫描版本、阶段、进度、健康态和下一步。",
        "sections": [
            "筛选与排序条",
            "项目注册表",
            "阶段分布摘要",
            "风险与调试摘要",
            "推荐 skill 区",
        ],
        "actions": [
            {"label": "进入项目详情", "target": "project-detail", "trigger": "点击项目行或卡片"},
            {"label": "返回首页", "target": "home", "trigger": "点击首页导航"},
        ],
        "states": [
            {"id": "ready", "label": "多项目已加载", "description": "密集展示多项目当前状态。"},
            {"id": "filtered", "label": "已筛选", "description": "按阶段、版本、健康态筛选项目。"},
            {"id": "empty", "label": "无项目", "description": "没有任何受管项目进入注册表。"},
            {"id": "loading", "label": "加载中", "description": "项目注册表正在聚合。"},
            {"id": "error", "label": "错误", "description": "总览聚合失败但保留恢复提示。"},
        ],
    },
    "project-detail": {
        "name": "项目详情",
        "keywords": ("项目详情", "详情页", "project detail"),
        "priority": "P0",
        "platforms": ["Web", "PC", "App"],
        "responsibility": "成为接力页，展示版本线、主 PRD、并行 PRD、需求闭环和推荐动作。",
        "sections": [
            "项目头部摘要",
            "版本与分支信息",
            "主 PRD 与并行 PRD",
            "需求物料闭环状态",
            "最近交付与下一步",
            "运行态摘要卡",
        ],
        "actions": [
            {"label": "查看运行中心", "target": "runtime-center", "trigger": "点击运行态摘要"},
            {"label": "查看恢复诊断", "target": "recovery-diagnostics", "trigger": "点击恢复诊断入口"},
            {"label": "查看项目物料", "target": "material-viewer", "trigger": "点击文档查看入口"},
            {"label": "返回管理总览", "target": "management-overview", "trigger": "点击返回"},
        ],
        "states": [
            {"id": "ready", "label": "可接力", "description": "版本、PRD、需求闭环和下一步信息完整。"},
            {"id": "requirement-missing", "label": "需求缺口", "description": "PRD / user-story / test-case 存在缺口。"},
            {"id": "draft", "label": "需求草稿", "description": "需求已建立但未冻结。"},
            {"id": "frozen", "label": "需求冻结", "description": "需求链与 prototype 都已冻结。"},
            {"id": "runtime-active", "label": "运行中", "description": "存在 single / team / ralph 运行摘要。"},
            {"id": "loading", "label": "加载中", "description": "项目详情正在聚合。"},
            {"id": "error", "label": "错误", "description": "详情聚合失败但给出恢复链路。"},
        ],
    },
    "runtime-center": {
        "name": "运行中心",
        "keywords": ("运行中心", "runtime center", "runtime"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "只在这里下钻 single / team / ralph 的 runtime 细节和有限 session metadata。",
        "sections": [
            "运行态摘要头部",
            "single / team / ralph 模式切换",
            "agent/session 引用",
            "artifact 与 linked run",
            "最近结果与 blocker",
        ],
        "actions": [
            {"label": "返回项目详情", "target": "project-detail", "trigger": "点击返回"},
            {"label": "返回管理总览", "target": "management-overview", "trigger": "点击面包屑"},
        ],
        "states": [
            {"id": "single-active", "label": "Single 运行", "description": "展示单进程执行摘要和 linked run。"},
            {"id": "team-active", "label": "Team 运行", "description": "展示 agent 数、角色、状态和 host session metadata。"},
            {"id": "ralph-active", "label": "Ralph 闭环", "description": "展示 round_count、failure_streak、next_action、blocker。"},
            {"id": "idle", "label": "无活跃运行", "description": "当前没有任何 active runtime。"},
            {"id": "loading", "label": "加载中", "description": "运行态数据仍在读取。"},
            {"id": "error", "label": "错误", "description": "运行态投影异常，需要回到诊断页。"},
        ],
    },
    "recovery-diagnostics": {
        "name": "恢复诊断",
        "keywords": ("恢复诊断", "diagnostics", "recovery"),
        "priority": "P2",
        "platforms": ["Web", "PC"],
        "responsibility": "解释 degraded / rebuild / doctor，明确 truth 仍来自 docs/beacon 与 .beacon。",
        "sections": [
            "truth 来源说明",
            "degraded / rebuild / doctor 诊断卡",
            "恢复步骤",
            "风险提示",
        ],
        "actions": [
            {"label": "返回项目详情", "target": "project-detail", "trigger": "点击返回"},
            {"label": "前往运行中心", "target": "runtime-center", "trigger": "点击运行态关联"},
        ],
        "states": [
            {"id": "healthy-warning", "label": "健康但预警", "description": "当前系统可用但存在恢复风险提示。"},
            {"id": "degraded", "label": "降级", "description": "SQLite 或 PocketBase 缺失，但 truth 仍可从文档恢复。"},
            {"id": "rebuild-suggested", "label": "建议重建", "description": "投影层需要重建。"},
            {"id": "doctor-suggested", "label": "建议 doctor", "description": "推荐执行 doctor 修复上下文。"},
            {"id": "loading", "label": "加载中", "description": "诊断结果仍在采集。"},
            {"id": "error", "label": "错误", "description": "诊断页本身无法完成聚合。"},
        ],
    },
    "material-viewer": {
        "name": "项目物料查看器",
        "keywords": ("项目物料查看器", "物料查看器", "文档查看器", "markdown 物料查看器", "markdown viewer", "material viewer"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "按 version -> document type -> feature 提供只读 Markdown 浏览。",
        "sections": [
            "版本树",
            "文档类型列表",
            "feature 目录",
            "文档阅读面板",
            "来源路径信息",
        ],
        "actions": [
            {"label": "打开文档", "target": "material-document-detail", "trigger": "点击文档列表项"},
            {"label": "返回项目详情", "target": "project-detail", "trigger": "点击返回"},
        ],
        "states": [
            {"id": "ready", "label": "可浏览", "description": "版本树和文档列表已加载。"},
            {"id": "document-open", "label": "文档已打开", "description": "右侧阅读区显示当前文档正文。"},
            {"id": "source-missing", "label": "来源缺失", "description": "目标文档不存在或暂不可读。"},
            {"id": "loading", "label": "加载中", "description": "文档列表或内容仍在加载。"},
            {"id": "empty", "label": "空状态", "description": "该版本或类型下没有可读文档。"},
            {"id": "error", "label": "错误", "description": "文档读取失败。"},
        ],
    },
    "material-document-detail": {
        "name": "物料文档详情",
        "keywords": ("物料文档详情", "document detail", "reader state"),
        "priority": "P2",
        "platforms": ["Web", "PC"],
        "responsibility": "冻结文档阅读状态，包括来源路径、版本切换和同类文档切换。",
        "sections": [
            "文档头部信息",
            "版本 / 类型 / feature 面包屑",
            "Markdown 正文区",
            "同类文档切换",
            "来源路径与只读说明",
        ],
        "actions": [
            {"label": "返回物料查看器", "target": "material-viewer", "trigger": "点击返回"},
            {"label": "切换同版本文档", "target": "material-document-detail", "trigger": "点击侧栏文档"},
        ],
        "states": [
            {"id": "ready", "label": "文档已打开", "description": "显示文档正文与来源路径。"},
            {"id": "sibling-switch", "label": "切换同类文档", "description": "在阅读区切换相邻文档。"},
            {"id": "version-switch", "label": "切换版本", "description": "切换到同类型的其他版本文档。"},
            {"id": "source-missing", "label": "来源缺失", "description": "文档不存在或来源路径不可达。"},
        ],
    },
}

TRANSITION_LIBRARY = [
    {"from": "home", "to": "management-overview", "trigger": "点击项目组合入口", "type": "primary"},
    {"from": "home", "to": "project-detail", "trigger": "点击重点项目卡片", "type": "primary"},
    {"from": "management-overview", "to": "project-detail", "trigger": "点击项目行/卡片", "type": "primary"},
    {"from": "management-overview", "to": "home", "trigger": "点击首页导航", "type": "return"},
    {"from": "project-detail", "to": "runtime-center", "trigger": "点击运行态摘要", "type": "drill-down"},
    {"from": "project-detail", "to": "recovery-diagnostics", "trigger": "点击恢复诊断入口", "type": "drill-down"},
    {"from": "project-detail", "to": "material-viewer", "trigger": "点击文档查看入口", "type": "drill-down"},
    {"from": "project-detail", "to": "management-overview", "trigger": "点击返回", "type": "return"},
    {"from": "runtime-center", "to": "project-detail", "trigger": "点击返回", "type": "return"},
    {"from": "recovery-diagnostics", "to": "project-detail", "trigger": "点击返回", "type": "return"},
    {"from": "material-viewer", "to": "material-document-detail", "trigger": "点击文档列表项", "type": "drill-down"},
    {"from": "material-document-detail", "to": "material-viewer", "trigger": "点击返回", "type": "return"},
]

FIELD_PATTERNS = {
    "prototype_archetype": re.compile(r"prototype_archetype\s*[:=]\s*([A-Za-z0-9_-]+)", re.IGNORECASE),
    "theme_primary": re.compile(r"theme_primary\s*[:=]\s*(#[0-9A-Fa-f]{6})", re.IGNORECASE),
    "theme_secondary": re.compile(r"theme_secondary\s*[:=]\s*(#[0-9A-Fa-f]{6})", re.IGNORECASE),
    "route_closure_required": re.compile(r"route_closure_required\s*[:=]\s*(true|false)", re.IGNORECASE),
}


def _stable_hash(payload: Any) -> str:
    return sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify_feature(text: str) -> str:
    raw = (text or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw)
    return slug.strip("-") or "prototype-feature"


def _normalize_feature_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").strip().lower()).strip("-")


def _feature_slug_candidates(feature: str) -> list[str]:
    canonical = slugify_feature(feature)
    raw = re.sub(r"\s+", "-", (feature or "").strip().lower()).strip("-")
    dotted = re.sub(r"\bv(\d+)-(\d+)-(\d+)\b", r"v\1.\2.\3", canonical)
    dashed = re.sub(r"\bv(\d+)\.(\d+)\.(\d+)\b", r"v\1-\2-\3", raw)
    candidates: list[str] = []
    for item in (canonical, raw, dotted, dashed):
        value = str(item or "").strip().strip("-")
        if value and value not in candidates:
            candidates.append(value)
    return candidates or [canonical]


def _resolve_feature_doc_path(directory: Path, feature: str) -> Path:
    candidates = _feature_slug_candidates(feature)
    for candidate in candidates:
        path = directory / f"{candidate}.md"
        if path.exists():
            return path
    normalized_candidates = {_normalize_feature_token(candidate) for candidate in candidates}
    for path in sorted(directory.glob("*.md")):
        if _normalize_feature_token(path.stem) in normalized_candidates:
            return path
    return directory / f"{slugify_feature(feature)}.md"


def prototype_dir(project_root: Path, version: str, feature: str) -> Path:
    return project_root / "docs" / "beacon" / version / "prototype" / slugify_feature(feature)


def prototype_files(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = prototype_dir(project_root, version, feature)
    return {
        "root": root,
        "human_view_dir": root / "human-view",
        "machine_view_dir": root / "machine-view",
        "manifest": root / "manifest.json",
        "prototype_plan": root / "prototype-plan.json",
        "prototype_brief": root / "prototype-brief.json",
        "canonical_envelope": root / "canonical-envelope.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
        "review_json": root / "prototype-review.json",
        "review_md": root / "prototype-review.md",
        "wireframe_summary": root / "wireframe-summary.md",
        "wireframe_manifest": root / "wireframe-manifest.json",
        "navigation_map": root / "navigation-map.json",
        "navigation_map_md": root / "navigation-map.md",
        "state_flow_map": root / "state-flow-map.json",
        "state_flow_map_md": root / "state-flow-map.md",
        "component_catalog": root / "component-catalog.json",
        "component_catalog_md": root / "component-catalog.md",
        "interaction_map": root / "interaction-map.json",
        "coverage_report": root / "coverage-report.json",
        "theme": root / "theme.json",
        "tokens_css": root / "tokens.css",
        "platform_variants": root / "platform-variants.json",
        "implementation_map": root / "implementation-map.json",
        "route_closure_contract": root / "route-closure-contract.json",
        "pages_dir": root / "pages",
        "page_specs_dir": root / "page-specs",
        "index_html": root / "index.html",
    }


def source_doc_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    base = project_root / "docs" / "beacon" / version
    return {
        "user-story": _resolve_feature_doc_path(base / "user-story", feature),
        "prd": _resolve_feature_doc_path(base / "prd", feature),
        "test-case": _resolve_feature_doc_path(base / "qa" / "test-cases", feature),
    }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_source_documents(project_root: Path, version: str, feature: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for doc_type, path in source_doc_paths(project_root, version, feature).items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "type": doc_type,
                "path": path,
                "relative_path": str(path.relative_to(project_root)),
                "text": text,
                "fingerprint": sha256_text(text),
            }
        )
    return docs


def _extract_field(docs: list[dict[str, Any]], field: str, default: str) -> str:
    pattern = FIELD_PATTERNS.get(field)
    if pattern is None:
        return default
    for doc in docs:
        match = pattern.search(doc.get("text", ""))
        if match:
            return match.group(1).strip()
    return default


def _doc_contains(doc: dict[str, Any], keyword: str) -> int:
    text = doc.get("text", "")
    idx = text.lower().find(keyword.lower())
    return idx


def _detect_page_ids(docs: list[dict[str, Any]]) -> tuple[list[str], bool]:
    discovered: list[tuple[int, str]] = []
    for page_id, meta in PAGE_CATALOG.items():
        if page_id == "material-document-detail":
            continue
        positions: list[int] = []
        for keyword in meta["keywords"]:
            for doc in docs:
                idx = _doc_contains(doc, keyword)
                if idx >= 0:
                    positions.append(idx)
        if positions:
            discovered.append((min(positions), page_id))

    fallback_used = False
    if not discovered:
        fallback_used = True
        return list(PAGE_ORDER_DEFAULT), fallback_used

    page_ids = [page_id for _, page_id in sorted(discovered, key=lambda item: item[0])]
    ordered = [page_id for page_id in PAGE_ORDER_DEFAULT if page_id in page_ids]
    if "material-viewer" in ordered and "material-document-detail" not in ordered:
        ordered.append("material-document-detail")
    return ordered, fallback_used


def _build_transition_inventory(page_ids: list[str]) -> list[dict[str, Any]]:
    allowed = set(page_ids)
    transitions = [item for item in TRANSITION_LIBRARY if item["from"] in allowed and item["to"] in allowed]
    if "material-viewer" in allowed and "material-document-detail" not in allowed:
        transitions = [item for item in transitions if item["to"] != "material-document-detail"]
    return transitions


def _build_requirement_refs(docs: list[dict[str, Any]]) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for doc in docs:
        refs[doc["type"]] = [doc["relative_path"]]
    return refs


def _extract_requirement_ids(docs: list[dict[str, Any]]) -> dict[str, list[str]]:
    ac_ids: set[str] = set()
    tc_ids: set[str] = set()
    for doc in docs:
        text = str(doc.get("text") or "")
        ac_ids.update(match.upper() for match in AC_PATTERN.findall(text))
        tc_ids.update(match.upper() for match in TC_PATTERN.findall(text))
    return {
        "ac_ids": sorted(ac_ids),
        "tc_ids": sorted(tc_ids),
    }


def _build_page_specs(page_ids: list[str], docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = _build_requirement_refs(docs)
    transitions = _build_transition_inventory(page_ids)
    outbound: dict[str, list[dict[str, Any]]] = {}
    for transition in transitions:
        outbound.setdefault(transition["from"], []).append(transition)

    page_specs: list[dict[str, Any]] = []
    for page_id in page_ids:
        meta = PAGE_CATALOG[page_id]
        page_specs.append(
            {
                "page_id": page_id,
                "name": meta["name"],
                "priority": meta["priority"],
                "platforms": list(meta["platforms"]),
                "responsibility": meta["responsibility"],
                "sections": list(meta["sections"]),
                "actions": list(meta["actions"]),
                "states": list(meta["states"]),
                "requirement_refs": refs,
                "outbound_transitions": outbound.get(page_id, []),
            }
        )
    return page_specs


def _build_platform_variants(page_specs: list[dict[str, Any]]) -> dict[str, Any]:
    pages = {
        page["page_id"]: {
            "platforms": page["platforms"],
            "notes": (
                ["仅项目详情页支持 App"] if page["page_id"] == "project-detail" and "App" in page["platforms"] else []
            ),
        }
        for page in page_specs
    }
    return {
        "global_platforms": ["Web", "PC"],
        "pages": pages,
        "notes": [
            "默认展示 Web / PC 线框视图。",
            "App 只在真实需求明确要求时保留；当前仅 project-detail 做移动差异提示。",
        ],
    }


def _build_interaction_map(page_specs: list[dict[str, Any]], transitions: list[dict[str, Any]]) -> dict[str, Any]:
    states = sorted({state["id"] for page in page_specs for state in page["states"]})
    ctas = []
    for page in page_specs:
        for action in page["actions"]:
            ctas.append(
                {
                    "page_id": page["page_id"],
                    "label": action["label"],
                    "target": action["target"],
                    "trigger": action["trigger"],
                }
            )
    return {
        "states": states,
        "ctas": ctas,
        "jump_map": [
            {"from": item["from"], "to": item["to"], "trigger": item["trigger"], "type": item["type"]}
            for item in transitions
        ],
    }


def _build_component_catalog(
    page_specs: list[dict[str, Any]],
    requirement_ids: dict[str, list[str]],
) -> dict[str, Any]:
    ac_ids = list(requirement_ids.get("ac_ids") or [])
    tc_ids = list(requirement_ids.get("tc_ids") or [])
    components: list[dict[str, Any]] = []
    for page in page_specs:
        page_id = str(page.get("page_id") or "").strip()
        state_refs = [str(item.get("id") or "").strip() for item in page.get("states", []) if str(item.get("id") or "").strip()]
        actions = list(page.get("actions") or [])
        for index, section in enumerate(page.get("sections", []), start=1):
            component_id = f"{page_id}-component-{index:02d}"
            action = actions[index - 1] if index - 1 < len(actions) else None
            components.append(
                {
                    "component_id": component_id,
                    "page_id": page_id,
                    "name": str(section),
                    "responsibility": f"{section} 模块负责承载 `{page.get('name')}` 的关键信息与操作。",
                    "data_source": [
                        "prototype-plan.page_specs",
                        "source-map.requirement_refs",
                    ],
                    "interaction": (
                        {
                            "label": str(action.get("label") or ""),
                            "trigger": str(action.get("trigger") or ""),
                            "target": str(action.get("target") or ""),
                        }
                        if isinstance(action, dict)
                        else {
                            "label": "无直接动作",
                            "trigger": "被动展示",
                            "target": page_id,
                        }
                    ),
                    "state_refs": state_refs,
                    "ac_refs": ac_ids,
                    "tc_refs": tc_ids,
                    "story_refs": list((page.get("requirement_refs") or {}).get("user-story") or []),
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "component_count": len(components),
        "components": components,
    }


def _render_component_catalog_md(feature: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# 组件契约清单：{feature}",
        "",
        "| Component ID | Page | Name | State Refs | AC Refs | TC Refs |",
        "|---|---|---|---|---|---|",
    ]
    for component in payload.get("components", []):
        lines.append(
            "| `{}` | `{}` | {} | {} | {} | {} |".format(
                component.get("component_id", ""),
                component.get("page_id", ""),
                component.get("name", ""),
                ", ".join(component.get("state_refs", [])[:6]) or "-",
                ", ".join(component.get("ac_refs", [])[:4]) or "-",
                ", ".join(component.get("tc_refs", [])[:4]) or "-",
            )
        )
    lines.extend(
        [
            "",
            "## 说明",
            "- 组件契约用于 requirement freeze，不是最终前端组件实现规范。",
            "- 实现阶段需要保持 component -> state -> AC/TC 的可追踪关系。",
        ]
    )
    return "\n".join(lines)


def _build_state_flow_map(
    page_specs: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    requirement_ids: dict[str, list[str]],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    tc_ids = list(requirement_ids.get("tc_ids") or [])
    for page in page_specs:
        page_id = str(page.get("page_id") or "")
        states = [state for state in page.get("states", []) if isinstance(state, dict)]
        state_ids = [str(state.get("id") or "").strip() for state in states if str(state.get("id") or "").strip()]
        for state in states:
            state_id = str(state.get("id") or "").strip()
            if not state_id:
                continue
            node_key = f"{page_id}:{state_id}"
            nodes.append(
                {
                    "state_key": node_key,
                    "page_id": page_id,
                    "state_id": state_id,
                    "label": str(state.get("label") or state_id),
                    "description": str(state.get("description") or ""),
                }
            )
        if "loading" in state_ids and "ready" in state_ids:
            edges.append(
                {
                    "from": f"{page_id}:loading",
                    "to": f"{page_id}:ready",
                    "event": "data_loaded",
                    "guard": "data_fetch_success",
                    "kind": "intra-page",
                    "fallback": None,
                    "test_refs": tc_ids[:2],
                }
            )
        if "ready" in state_ids and "error" in state_ids:
            fallback_page = "recovery-diagnostics" if page_id != "recovery-diagnostics" else page_id
            edges.append(
                {
                    "from": f"{page_id}:ready",
                    "to": f"{page_id}:error",
                    "event": "data_failure",
                    "guard": "runtime_or_projection_error",
                    "kind": "intra-page",
                    "fallback": f"{fallback_page}:ready",
                    "test_refs": tc_ids[:2],
                }
            )
    for transition in transitions:
        source_page = str(transition.get("from") or "")
        target_page = str(transition.get("to") or "")
        if not source_page or not target_page:
            continue
        edges.append(
            {
                "from": f"{source_page}:ready",
                "to": f"{target_page}:ready",
                "event": str(transition.get("trigger") or "navigate"),
                "guard": "route_allowed",
                "kind": "inter-page",
                "fallback": f"{source_page}:ready",
                "test_refs": tc_ids[:1],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def _render_state_flow_map_md(feature: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# 状态流冻结图：{feature}",
        "",
        "| From | To | Event | Guard | Fallback |",
        "|---|---|---|---|---|",
    ]
    for edge in payload.get("edges", []):
        lines.append(
            "| `{}` | `{}` | {} | {} | {} |".format(
                edge.get("from", ""),
                edge.get("to", ""),
                edge.get("event", ""),
                edge.get("guard", ""),
                edge.get("fallback", "-") or "-",
            )
        )
    lines.extend(
        [
            "",
            "## 说明",
            "- 状态流与导航图共同定义 prototype 冻结语义。",
            "- 每条边都应可追溯到 test-case 场景。",
        ]
    )
    return "\n".join(lines)


def _build_route_closure_contract(page_specs: list[dict[str, Any]], transitions: list[dict[str, Any]], route_closure_required: bool) -> dict[str, Any]:
    closure_cases = []
    for index, transition in enumerate(transitions, start=1):
        closure_cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_page_id": transition["from"],
                "source_label": PAGE_CATALOG[transition["from"]]["name"],
                "target_surface_id": transition["to"],
                "target_label": PAGE_CATALOG[transition["to"]]["name"],
                "trigger": transition["trigger"],
                "type": transition["type"],
            }
        )
    return {
        "required": route_closure_required,
        "closure_cases": closure_cases,
        "notes": "Wireframe freeze 只冻结跳转关系，不冻结最终实现路由。",
    }


def _build_theme_payload(docs: list[dict[str, Any]]) -> dict[str, Any]:
    primary = _extract_field(docs, "theme_primary", "#2563EB")
    secondary = _extract_field(docs, "theme_secondary", "#0F172A")
    archetype = _extract_field(docs, "prototype_archetype", "admin-workbench")
    return {
        "ui_kit": PROTOTYPE_UI_KIT,
        "prototype_archetype": archetype,
        "primary": primary,
        "secondary": secondary,
        "surface_note": "Wireframe freeze uses markdown and metadata only, not high-fidelity HTML surfaces.",
    }


def _build_page_layout(page_id: str) -> list[str]:
    layouts = {
        "home": [
            "+------------------------------------------------------+",
            "| 经营总览条 | 活跃项目 | 阻塞项目 | 活跃 runtime |",
            "+------------------------------------------------------+",
            "| 重点介入区                                      |",
            "+------------------------------------------------------+",
            "| 项目推进摘要列表                                |",
            "+------------------------------------------------------+",
            "| 当前交付 / 下一步                               |",
            "+------------------------------------------------------+",
        ],
        "management-overview": [
            "+--------------------------------------------------------------------+",
            "| 筛选栏 | 版本 | 阶段 | 健康态 | debug | 推荐 skill                |",
            "+--------------------------------------------------------------------+",
            "| 项目注册表：项目名 / 类型 / 当前版本 / 主 feature / 进度 / 下一步 |",
            "+--------------------------------------------------------------------+",
        ],
        "project-detail": [
            "+------------------------------------------------------------+",
            "| 项目头部摘要 | 当前版本 | git/worktree                    |",
            "+------------------------------------------------------------+",
            "| 主 PRD / 并行 PRD | 生命周期 / 总进度                     |",
            "+------------------------------------------------------------+",
            "| prd / user-story / test-case / prototype 冻结状态         |",
            "+------------------------------------------------------------+",
            "| 最近交付 | 下一步 | 推荐 skill | runtime 摘要             |",
            "+------------------------------------------------------------+",
        ],
        "runtime-center": [
            "+-------------------------------------------------------------+",
            "| 模式切换：single | team | ralph                            |",
            "+-------------------------------------------------------------+",
            "| agent/session 引用 | linked run | artifact refs            |",
            "+-------------------------------------------------------------+",
            "| next_action | blocker | recent_result                      |",
            "+-------------------------------------------------------------+",
        ],
        "recovery-diagnostics": [
            "+----------------------------------------------------+",
            "| truth 来源说明：docs/beacon + .beacon              |",
            "+----------------------------------------------------+",
            "| degraded / rebuild / doctor 诊断卡                 |",
            "+----------------------------------------------------+",
            "| 恢复步骤 | 风险提示                                |",
            "+----------------------------------------------------+",
        ],
        "material-viewer": [
            "+----------------------------------------------------------------+",
            "| 版本树 | 文档类型 | feature 列表 | 文档阅读区                |",
            "+----------------------------------------------------------------+",
            "| 来源路径 | 只读说明 | 版本切换                                 |",
            "+----------------------------------------------------------------+",
        ],
        "material-document-detail": [
            "+---------------------------------------------------------------+",
            "| 面包屑：version / document type / feature                    |",
            "+---------------------------------------------------------------+",
            "| Markdown 正文区                                               |",
            "+---------------------------------------------------------------+",
            "| 同类文档切换 | 来源路径 | 只读说明                            |",
            "+---------------------------------------------------------------+",
        ],
    }
    return layouts.get(
        page_id,
        [
            "+-----------------------------+",
            "| 页面头部                    |",
            "+-----------------------------+",
            "| 主体内容                    |",
            "+-----------------------------+",
        ],
    )


def _render_page_markdown(page: dict[str, Any]) -> str:
    lines = [
        f"# 页面线框：{page['name']}",
        "",
        f"**页面 ID**: `{page['page_id']}`",
        f"**平台**: `{', '.join(page['platforms'])}`",
        f"**优先级**: `{page['priority']}`",
        "",
        "## 页面职责",
        f"- {page['responsibility']}",
        "",
        "## 关联 Requirement",
    ]
    for source_type, refs in page["requirement_refs"].items():
        lines.append(f"- `{source_type}`: {', '.join(refs)}")
    lines.extend(
        [
            "",
            "## 布局草图",
            "```text",
            *_build_page_layout(page["page_id"]),
            "```",
            "",
            "## 关键模块",
        ]
    )
    for section in page["sections"]:
        lines.append(f"- {section}")
    lines.extend(
        [
            "",
            "## 用户动作",
        ]
    )
    for action in page["actions"]:
        lines.append(f"- `{action['label']}`: {action['trigger']} -> `{action['target']}`")
    lines.extend(
        [
            "",
            "## 状态说明",
        ]
    )
    for state in page["states"]:
        lines.append(f"- `{state['id']}` / {state['label']}: {state['description']}")
    lines.extend(
        [
            "",
            "## 实现接力备注",
            "- 当前页面是 requirement freeze wireframe，不是高保真视觉稿。",
            "- 实现阶段必须回链本页与 navigation-map / wireframe-summary。",
        ]
    )
    return "\n".join(lines)


def _render_wireframe_summary(plan: dict[str, Any]) -> str:
    lines = [
        f"# 线框草图汇总：{plan['feature']}",
        "",
        f"**Feature**: `{plan['feature_slug']}`",
        f"**Version**: `{plan['version']}`",
        f"**Mode**: `{plan['prototype_mode']}`",
        f"**Generated At**: `{plan['generated_at']}`",
        "",
        "## 页面清单",
        "",
        "| 页面 ID | 页面名称 | 平台 | 优先级 | 页面职责 |",
        "|---------|----------|------|--------|----------|",
    ]
    for page in plan["page_specs"]:
        lines.append(
            f"| `{page['page_id']}` | {page['name']} | {', '.join(page['platforms'])} | {page['priority']} | {page['responsibility']} |"
        )
    lines.extend(
        [
            "",
            "## 跳转关系图",
            "",
            "```text",
        ]
    )
    for transition in plan["navigation"]["transitions"]:
        lines.append(f"[{transition['from']}] -- {transition['trigger']} --> [{transition['to']}]")
    lines.extend(
        [
            "```",
            "",
            "## 冻结检查点",
            "- [ ] 页面清单完整",
            "- [ ] 跳转逻辑完整",
            "- [ ] 单页线框可读",
            "- [ ] 关联 requirement 可追踪",
            "- [ ] 仅保留 wireframe freeze 语义",
        ]
    )
    return "\n".join(lines)


def _render_navigation_map_md(plan: dict[str, Any]) -> str:
    lines = [
        f"# 导航图：{plan['feature']}",
        "",
        f"**Primary Entry**: `{plan['navigation']['primary_entry']}`",
        f"**Primary Exit**: `{plan['navigation']['primary_exit']}`",
        "",
        "## 跳转清单",
    ]
    for transition in plan["navigation"]["transitions"]:
        lines.append(
            f"- `{transition['from']}` -> `{transition['to']}`: {transition['trigger']} ({transition['type']})"
        )
    lines.extend(
        [
            "",
            "## 返回路径",
        ]
    )
    for transition in [item for item in plan["navigation"]["transitions"] if item["type"] == "return"]:
        lines.append(f"- `{transition['from']}` 返回 `{transition['to']}`")
    lines.extend(
        [
            "",
            "## 禁止跳转",
            "- 首页不直接下钻 recovery-diagnostics，避免把机器噪音拉到首屏。",
            "- material-viewer 不直接跳 runtime-center，避免跨上下文误导。",
        ]
    )
    return "\n".join(lines)


def _render_review_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Prototype Review: {payload['feature']}",
        "",
        f"**Overall Status**: `{payload['overall_status']}`",
        f"**Prototype Mode**: `{payload['prototype_mode']}`",
        f"**Human View Status**: `{payload.get('human_view_status', 'unknown')}`",
        f"**Machine Contract Status**: `{payload.get('machine_contract_status', 'unknown')}`",
        f"**SQLite Projection Status**: `{payload.get('sqlite_projection_status', 'unknown')}`",
        f"**Drift Status**: `{payload.get('drift_status', 'unknown')}`",
        f"**Generated At**: `{payload['generated_at']}`",
        "",
        "| Check | Status | Message |",
        "|-------|--------|---------|",
    ]
    for check in payload["checks"]:
        lines.append(f"| `{check['name']}` | `{check['status']}` | {check['message']} |")
    if payload.get("blocking_failures"):
        lines.extend(
            [
                "",
                "## Blocking Failures",
            ]
        )
        for item in payload["blocking_failures"]:
            lines.append(f"- `{item['name']}`: {item['message']}")
    return "\n".join(lines)


def _artifact_fingerprints(files: dict[str, Path], *, include_optional: bool = True) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    for key, path in files.items():
        if key in {"root", "pages_dir", "page_specs_dir"}:
            continue
        if not include_optional and key in {"implementation_map", "index_html"}:
            continue
        if path.exists() and path.is_file():
            fingerprints[str(path.name)] = sha256_file(path)
    for directory_key in ("pages_dir", "page_specs_dir"):
        directory = files[directory_key]
        if directory.exists():
            for child in sorted(directory.glob("*")):
                if child.is_file():
                    fingerprints[str(child.relative_to(files["root"]))] = sha256_file(child)
    return fingerprints


def _prototype_ledger_db_path() -> Path:
    return runtime_ledger_root() / "prototype-ledger.sqlite3"


def _ensure_prototype_projection_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prototype_projection_transactions (
            transaction_id TEXT PRIMARY KEY,
            feature_slug TEXT NOT NULL,
            version TEXT NOT NULL,
            projection_seq TEXT NOT NULL,
            source_hash TEXT NOT NULL,
            committed_at TEXT NOT NULL,
            status TEXT NOT NULL,
            root_path TEXT NOT NULL,
            sink_checksums_json TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_prototype_projection_feature
        ON prototype_projection_transactions(feature_slug, version, committed_at)
        """
    )


def _write_prototype_projection_sqlite(payload: dict[str, Any]) -> dict[str, Any]:
    db_path = _prototype_ledger_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        _ensure_prototype_projection_schema(conn)
        conn.execute(
            """
            INSERT INTO prototype_projection_transactions (
                transaction_id, feature_slug, version, projection_seq, source_hash,
                committed_at, status, root_path, sink_checksums_json, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(transaction_id) DO UPDATE SET
                feature_slug=excluded.feature_slug,
                version=excluded.version,
                projection_seq=excluded.projection_seq,
                source_hash=excluded.source_hash,
                committed_at=excluded.committed_at,
                status=excluded.status,
                root_path=excluded.root_path,
                sink_checksums_json=excluded.sink_checksums_json,
                payload_json=excluded.payload_json
            """,
            (
                str(payload.get("transaction_id") or ""),
                str(payload.get("feature_slug") or ""),
                str(payload.get("version") or ""),
                str(payload.get("projection_seq") or ""),
                str(payload.get("source_hash") or ""),
                str(payload.get("committed_at") or ""),
                str(payload.get("status") or "committed"),
                str(payload.get("root_path") or ""),
                json.dumps(payload.get("sink_checksums") or {}, ensure_ascii=False, sort_keys=True),
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
            ),
        )
        conn.commit()
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:  # noqa: BLE001
            pass
    return {
        "status": "committed",
        "db_path": str(db_path),
    }


def _read_prototype_projection_sqlite(transaction_id: str) -> dict[str, Any]:
    if not transaction_id:
        return {"status": "missing"}
    db_path = _prototype_ledger_db_path()
    if not db_path.exists():
        return {"status": "missing", "db_path": str(db_path)}
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        _ensure_prototype_projection_schema(conn)
        row = conn.execute(
            """
            SELECT transaction_id, feature_slug, version, projection_seq, source_hash,
                   committed_at, status, root_path, sink_checksums_json
            FROM prototype_projection_transactions
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()
    finally:
        try:
            conn.close()  # type: ignore[name-defined]
        except Exception:  # noqa: BLE001
            pass
    if row is None:
        return {"status": "missing", "db_path": str(db_path)}
    sink_checksums: dict[str, Any] = {}
    try:
        sink_checksums = json.loads(str(row["sink_checksums_json"] or "{}"))
    except Exception:  # noqa: BLE001
        sink_checksums = {}
    return {
        "status": "committed",
        "db_path": str(db_path),
        "transaction_id": str(row["transaction_id"]),
        "feature_slug": str(row["feature_slug"]),
        "version": str(row["version"]),
        "projection_seq": str(row["projection_seq"]),
        "source_hash": str(row["source_hash"]),
        "committed_at": str(row["committed_at"]),
        "root_path": str(row["root_path"]),
        "sink_checksums": sink_checksums if isinstance(sink_checksums, dict) else {},
    }


def _build_source_map(project_root: Path, docs: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "feature": plan["feature"],
        "feature_slug": plan["feature_slug"],
        "derived_from": [doc["type"] for doc in docs],
        "sources": [
            {
                "type": doc["type"],
                "path": doc["relative_path"],
                "fingerprint": doc["fingerprint"],
            }
            for doc in docs
        ],
        "page_requirements": [
            {
                "page_id": page["page_id"],
                "refs": page["requirement_refs"],
            }
            for page in plan["page_specs"]
        ],
        "generated_at": plan["generated_at"],
    }


def _build_wireframe_manifest(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "feature": plan["feature"],
        "feature_slug": plan["feature_slug"],
        "version": plan["version"],
        "prototype_mode": plan["prototype_mode"],
        "prototype_type": plan["contract"]["prototype_archetype"],
        "pages": [
            {
                "page_id": page["page_id"],
                "name": page["name"],
                "priority": page["priority"],
                "platforms": page["platforms"],
                "responsibility": page["responsibility"],
                "file": f"pages/{page['page_id']}.md",
            }
            for page in plan["page_specs"]
        ],
        "transitions": plan["navigation"]["transitions"],
    }


def _build_coverage_report(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "feature": plan["feature"],
        "feature_slug": plan["feature_slug"],
        "prototype_mode": plan["prototype_mode"],
        "required_pages": list(plan["required_pages"]),
        "generated_pages": list(plan["required_pages"]),
        "required_states": list(plan["required_states"]),
        "missing_state_variants": [],
        "compact_mode_detected": False,
        "page_count": len(plan["page_specs"]),
        "transition_count": len(plan["navigation"]["transitions"]),
    }


def compile_prototype_plan(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    docs = load_source_documents(project_root, version, feature)
    doc_by_type = {doc["type"]: doc for doc in docs}
    missing = [doc_type for doc_type in REQUIRED_SOURCE_TYPES if doc_type not in doc_by_type]
    if missing:
        raise FileNotFoundError(
            f"prototype requires requirement truth before wireframe freeze, missing: {', '.join(missing)}"
        )

    page_ids, fallback_used = _detect_page_ids(docs)
    if "material-viewer" in page_ids and "material-document-detail" not in page_ids:
        page_ids.append("material-document-detail")
    transitions = _build_transition_inventory(page_ids)
    page_specs = _build_page_specs(page_ids, docs)
    required_states = sorted({state["id"] for page in page_specs for state in page["states"]})
    route_closure_required = _extract_field(docs, "route_closure_required", "false").lower() == "true"
    theme = _build_theme_payload(docs)
    requirement_ids = _extract_requirement_ids(docs)
    plan = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "generated_at": now_iso(),
        "prototype_mode": PROTOTYPE_MODE,
        "ui_kit": PROTOTYPE_UI_KIT,
        "source_documents": [
            {
                "type": doc["type"],
                "path": doc["relative_path"],
                "fingerprint": doc["fingerprint"],
            }
            for doc in docs
        ],
        "required_pages": list(page_ids),
        "required_states": required_states,
        "requirement_ids": requirement_ids,
        "page_specs": page_specs,
        "page_inventory": page_specs,
        "navigation": {
            "primary_entry": page_ids[0],
            "primary_exit": transitions[-1]["to"] if transitions else page_ids[-1],
            "transitions": transitions,
        },
        "platform_variants": _build_platform_variants(page_specs),
        "contract": {
            "prototype_archetype": theme["prototype_archetype"],
            "wireframe_only": True,
            "design_governance_required": False,
            "route_closure_required": route_closure_required,
            "required_files": [
                "wireframe-summary.md",
                "wireframe-manifest.json",
                "navigation-map.md",
                "navigation-map.json",
                "state-flow-map.md",
                "state-flow-map.json",
                "component-catalog.md",
                "component-catalog.json",
                "canonical-envelope.json",
                "pages/*.md",
                "freeze.json",
                "prototype-review.json",
            ],
        },
        "parser": {
            "page_detection": "keyword-catalog",
            "fallback_used": fallback_used,
            "cjk_detected": any(any(ord(ch) > 127 for ch in doc["text"]) for doc in docs),
            "cjk_parse_failed": False,
        },
        "theme": theme,
    }
    return plan


def write_prototype_plan(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    plan = compile_prototype_plan(project_root, version, feature)
    files = prototype_files(project_root, version, feature)
    _write_json(files["prototype_plan"], plan)
    return {"path": files["prototype_plan"], "plan": plan}


def write_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    source_docs = load_source_documents(project_root, version, feature)
    plan = compile_prototype_plan(project_root, version, feature)
    files = prototype_files(project_root, version, feature)
    feature_slug = str(plan["feature_slug"])
    source_hash = _stable_hash([{"type": doc["type"], "fingerprint": doc["fingerprint"]} for doc in source_docs])
    projection_seq = f"pp-{source_hash[:16]}"
    committed_at = now_iso()
    transaction_id = f"tx-{feature_slug}-{projection_seq}"

    theme_payload = plan["theme"]
    transitions = plan["navigation"]["transitions"]
    requirement_ids = plan.get("requirement_ids") if isinstance(plan.get("requirement_ids"), dict) else {}
    interaction_map = _build_interaction_map(plan["page_specs"], transitions)
    state_flow_map = _build_state_flow_map(plan["page_specs"], transitions, requirement_ids)
    component_catalog = _build_component_catalog(plan["page_specs"], requirement_ids)
    route_closure = _build_route_closure_contract(
        plan["page_specs"],
        transitions,
        bool(plan["contract"]["route_closure_required"]),
    )
    coverage = _build_coverage_report(plan)
    source_map = _build_source_map(project_root, source_docs, plan)
    wireframe_manifest = _build_wireframe_manifest(plan)
    canonical_envelope = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": feature_slug,
        "version": version,
        "prototype_mode": PROTOTYPE_MODE,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "transaction_id": transaction_id,
        "committed_at": committed_at,
        "plan": plan,
        "navigation_map": {
            "primary_entry": plan["navigation"]["primary_entry"],
            "primary_exit": plan["navigation"]["primary_exit"],
            "transitions": transitions,
        },
        "state_flow_map": state_flow_map,
        "component_catalog": component_catalog,
        "route_closure_contract": route_closure,
        "coverage_report": coverage,
        "source_map": source_map,
    }

    with tempfile.TemporaryDirectory(prefix=f"prototype-{feature_slug}-") as tmpdir:
        stage_root = Path(tmpdir) / "bundle"
        template_files = prototype_files(stage_root.parent, version, feature)
        template_root = template_files["root"]
        stage_files: dict[str, Path] = {"root": stage_root}
        for key, path in template_files.items():
            if key == "root":
                continue
            stage_files[key] = stage_root / path.relative_to(template_root)
        stage_files["root"].mkdir(parents=True, exist_ok=True)
        stage_files["pages_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["page_specs_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["human_view_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["machine_view_dir"].mkdir(parents=True, exist_ok=True)

        _write_json(stage_files["prototype_plan"], plan)
        _write_json(stage_files["canonical_envelope"], canonical_envelope)
        _write_text(stage_files["wireframe_summary"], _render_wireframe_summary(plan))
        _write_json(stage_files["wireframe_manifest"], wireframe_manifest)
        _write_text(stage_files["navigation_map_md"], _render_navigation_map_md(plan))
        _write_json(
            stage_files["navigation_map"],
            {
                "schema_version": SCHEMA_VERSION,
                "feature": feature,
                "feature_slug": feature_slug,
                "primary_entry": plan["navigation"]["primary_entry"],
                "primary_exit": plan["navigation"]["primary_exit"],
                "jump_map": [
                    {"from": item["from"], "to": item["to"], "trigger": item["trigger"], "type": item["type"]}
                    for item in transitions
                ],
                "transitions": transitions,
            },
        )
        _write_json(stage_files["state_flow_map"], state_flow_map)
        _write_text(stage_files["state_flow_map_md"], _render_state_flow_map_md(feature, state_flow_map))
        _write_json(stage_files["component_catalog"], component_catalog)
        _write_text(stage_files["component_catalog_md"], _render_component_catalog_md(feature, component_catalog))
        _write_json(stage_files["interaction_map"], interaction_map)
        _write_json(stage_files["coverage_report"], coverage)
        _write_json(stage_files["route_closure_contract"], route_closure)
        _write_json(
            stage_files["implementation_map"],
            {
                "schema_version": SCHEMA_VERSION,
                "feature": feature,
                "feature_slug": feature_slug,
                "version": version,
                "prototype_mode": PROTOTYPE_MODE,
                "closure_bindings": [],
                "bound_cases": 0,
                "generated_at": now_iso(),
                "path": str(files["implementation_map"]),
            },
        )
        _write_json(
            stage_files["prototype_brief"],
            {"prototype_mode": PROTOTYPE_MODE, "theme": theme_payload, "page_count": len(plan["page_specs"])},
        )
        _write_json(stage_files["theme"], theme_payload)
        _write_json(stage_files["platform_variants"], plan["platform_variants"])
        _write_text(
            stage_files["tokens_css"],
            "\n".join(
                [
                    ":root {",
                    f"  --wireframe-primary: {theme_payload['primary']};",
                    f"  --wireframe-secondary: {theme_payload['secondary']};",
                    "  --wireframe-note: 'Requirement-driven wireframe freeze';",
                    "}",
                ]
            ),
        )

        for page in plan["page_specs"]:
            _write_text(stage_files["pages_dir"] / f"{page['page_id']}.md", _render_page_markdown(page))
            _write_json(stage_files["page_specs_dir"] / f"{page['page_id']}.json", page)
        _write_json(stage_files["source_map"], source_map)

        _write_json(
            stage_files["human_view_dir"] / "index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "files": [
                    "wireframe-summary.md",
                    "navigation-map.md",
                    "state-flow-map.md",
                    "component-catalog.md",
                    "pages/*.md",
                ],
            },
        )
        _write_json(
            stage_files["machine_view_dir"] / "index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "files": [
                    "canonical-envelope.json",
                    "prototype-plan.json",
                    "wireframe-manifest.json",
                    "navigation-map.json",
                    "state-flow-map.json",
                    "component-catalog.json",
                    "interaction-map.json",
                    "coverage-report.json",
                    "source-map.json",
                    "route-closure-contract.json",
                ],
            },
        )

        machine_fingerprints = {}
        human_fingerprints = {}
        for path in sorted(stage_files["root"].rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(stage_files["root"]))
            fingerprint = sha256_file(path)
            if rel.endswith(".md") or rel.endswith(".css"):
                human_fingerprints[rel] = fingerprint
            if rel.endswith(".json"):
                machine_fingerprints[rel] = fingerprint

        sink_checksums = {
            "human": _stable_hash(human_fingerprints),
            "machine": _stable_hash(machine_fingerprints),
        }
        sqlite_write = {"status": "failed", "error": "not_written"}
        sqlite_payload = {
            "schema_version": SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "feature_slug": feature_slug,
            "version": version,
            "projection_seq": projection_seq,
            "source_hash": source_hash,
            "committed_at": committed_at,
            "status": "committed",
            "root_path": str(files["root"]),
            "sink_checksums": sink_checksums,
        }
        try:
            sqlite_write = _write_prototype_projection_sqlite(sqlite_payload)
            sink_checksums["sqlite"] = _stable_hash(sqlite_payload)
        except Exception as exc:  # noqa: BLE001
            sink_checksums["sqlite"] = "missing"
            sqlite_write = {"status": "failed", "error": str(exc), "db_path": str(_prototype_ledger_db_path())}

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": version,
            "prototype_mode": PROTOTYPE_MODE,
            "ui_kit": PROTOTYPE_UI_KIT,
            "status": "draft",
            "review_status": "missing",
            "design_review_outcome": "pass",
            "prototype_type": plan["contract"]["prototype_archetype"],
            "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
            "transaction": {
                "source_hash": source_hash,
                "projection_seq": projection_seq,
                "transaction_id": transaction_id,
                "committed_at": committed_at,
                "sink_checksums": sink_checksums,
                "sqlite_write": sqlite_write,
            },
            "artifacts": {
                "prototype_plan": str(files["prototype_plan"].relative_to(project_root)),
                "wireframe_summary": str(files["wireframe_summary"].relative_to(project_root)),
                "wireframe_manifest": str(files["wireframe_manifest"].relative_to(project_root)),
                "navigation_map": str(files["navigation_map"].relative_to(project_root)),
                "navigation_map_md": str(files["navigation_map_md"].relative_to(project_root)),
                "state_flow_map": str(files["state_flow_map"].relative_to(project_root)),
                "state_flow_map_md": str(files["state_flow_map_md"].relative_to(project_root)),
                "component_catalog": str(files["component_catalog"].relative_to(project_root)),
                "component_catalog_md": str(files["component_catalog_md"].relative_to(project_root)),
                "interaction_map": str(files["interaction_map"].relative_to(project_root)),
                "coverage_report": str(files["coverage_report"].relative_to(project_root)),
                "route_closure_contract": str(files["route_closure_contract"].relative_to(project_root)),
                "implementation_map": str(files["implementation_map"].relative_to(project_root)),
                "canonical_envelope": str(files["canonical_envelope"].relative_to(project_root)),
                "source_map": str(files["source_map"].relative_to(project_root)),
                "pages_dir": str(files["pages_dir"].relative_to(project_root)),
                "page_specs_dir": str(files["page_specs_dir"].relative_to(project_root)),
                "human_view_dir": str(files["human_view_dir"].relative_to(project_root)),
                "machine_view_dir": str(files["machine_view_dir"].relative_to(project_root)),
                "theme": str(files["theme"].relative_to(project_root)),
                "tokens_css": str(files["tokens_css"].relative_to(project_root)),
                "platform_variants": str(files["platform_variants"].relative_to(project_root)),
                "freeze": str(files["freeze"].relative_to(project_root)),
            },
        }
        _write_json(stage_files["manifest"], manifest)

        freeze_payload = {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": version,
            "prototype_mode": PROTOTYPE_MODE,
            "status": "draft",
            "review_status": "missing",
            "source_fingerprints": manifest["source_fingerprints"],
            "artifact_fingerprints": _artifact_fingerprints(stage_files, include_optional=False),
            "generated_at": plan["generated_at"],
            "transaction": manifest["transaction"],
        }
        _write_json(stage_files["freeze"], freeze_payload)

        review_payload = {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": version,
            "prototype_mode": PROTOTYPE_MODE,
            "generated_at": now_iso(),
            "overall_status": "missing",
            "design_review_outcome": "pass",
            "checks": [],
            "blocking_failures": [],
            "artifacts": {},
            "human_view_status": "unknown",
            "machine_contract_status": "unknown",
            "sqlite_projection_status": "unknown",
            "drift_status": "unknown",
        }
        _write_json(stage_files["review_json"], review_payload)
        _write_text(stage_files["review_md"], "# Prototype Review\n\nReview not yet run.")

        final_root = files["root"]
        final_root.parent.mkdir(parents=True, exist_ok=True)
        if final_root.exists():
            shutil.rmtree(final_root)
        shutil.move(str(stage_files["root"]), str(final_root))

    return {
        "prototype_mode": PROTOTYPE_MODE,
        "contract": plan["contract"],
        "plan": plan,
        "files": files,
    }


def bind_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["route_closure_contract"].exists():
        raise FileNotFoundError("prototype bundle missing route-closure-contract.json; run prototype create first")
    route_payload = _read_json(files["route_closure_contract"])
    closure_cases = route_payload.get("closure_cases") if isinstance(route_payload.get("closure_cases"), list) else []
    bindings = []
    for case in closure_cases:
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("case_id") or "").strip()
        target = str(case.get("target_surface_id") or "").strip()
        if not case_id or not target:
            continue
        bindings.append(
            {
                "case_id": case_id,
                "runtime_target": f"implement:{target}",
                "state_target": target,
                "status": "bound",
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "prototype_mode": PROTOTYPE_MODE,
        "closure_bindings": bindings,
        "bound_cases": len(bindings),
        "generated_at": now_iso(),
        "path": str(files["implementation_map"]),
    }
    _write_json(files["implementation_map"], payload)
    return payload


def _review_check(name: str, status: str, message: str, *, blocking: bool = True) -> dict[str, Any]:
    return {"name": name, "status": status, "message": message, "blocking": blocking}


def review_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["root"].exists():
        raise FileNotFoundError("prototype bundle missing; run prototype create first")

    plan = _read_json(files["prototype_plan"])
    if not plan:
        raise FileNotFoundError("prototype-plan.json missing; run prototype create first")

    manifest = _read_json(files["manifest"])
    source_map = _read_json(files["source_map"])
    canonical_envelope = _read_json(files["canonical_envelope"])
    state_flow_map = _read_json(files["state_flow_map"])
    component_catalog = _read_json(files["component_catalog"])
    route_closure = _read_json(files["route_closure_contract"])
    implementation_map = _read_json(files["implementation_map"])
    page_specs = plan.get("page_specs") if isinstance(plan.get("page_specs"), list) else []
    required_pages = [str(item).strip() for item in (plan.get("required_pages") or []) if str(item).strip()]
    required_states = [str(item).strip() for item in (plan.get("required_states") or []) if str(item).strip()]
    transaction = manifest.get("transaction") if isinstance(manifest.get("transaction"), dict) else {}
    transaction_id = str(transaction.get("transaction_id") or "")
    sqlite_projection = _read_prototype_projection_sqlite(transaction_id)

    checks = [
        _review_check(
            "prototype_mode_wireframe",
            "pass" if str(plan.get("prototype_mode", "")) == PROTOTYPE_MODE else "fail",
            "prototype mode must be wireframe only",
        ),
        _review_check(
            "wireframe_summary_present",
            "pass" if files["wireframe_summary"].exists() else "fail",
            "wireframe-summary.md should exist",
        ),
        _review_check(
            "wireframe_manifest_present",
            "pass" if files["wireframe_manifest"].exists() else "fail",
            "wireframe-manifest.json should exist",
        ),
        _review_check(
            "navigation_map_present",
            "pass" if files["navigation_map"].exists() and files["navigation_map_md"].exists() else "fail",
            "navigation-map.md/json should exist",
        ),
        _review_check(
            "state_flow_map_present",
            "pass" if files["state_flow_map"].exists() and files["state_flow_map_md"].exists() else "fail",
            "state-flow-map.md/json should exist",
        ),
        _review_check(
            "component_catalog_present",
            "pass" if files["component_catalog"].exists() and files["component_catalog_md"].exists() else "fail",
            "component-catalog.md/json should exist",
        ),
        _review_check(
            "pages_directory_present",
            "pass" if files["pages_dir"].exists() else "fail",
            "pages directory should exist",
        ),
        _review_check(
            "interaction_map_present",
            "pass" if files["interaction_map"].exists() else "fail",
            "interaction-map.json should exist",
        ),
        _review_check(
            "coverage_report_present",
            "pass" if files["coverage_report"].exists() else "fail",
            "coverage-report.json should exist",
        ),
        _review_check(
            "canonical_envelope_present",
            "pass" if files["canonical_envelope"].exists() else "fail",
            "canonical-envelope.json should exist",
        ),
        _review_check(
            "page_specs_present",
            "pass" if files["page_specs_dir"].exists() else "fail",
            "page-specs directory should exist",
        ),
        _review_check(
            "html_high_fidelity_removed",
            "pass" if not files["index_html"].exists() else "fail",
            "high-fidelity HTML prototype output must be removed",
        ),
    ]

    missing_pages = [page_id for page_id in required_pages if not (files["pages_dir"] / f"{page_id}.md").exists()]
    checks.append(
        _review_check(
            "required_pages_materialized",
            "pass" if not missing_pages else "fail",
            "all required page markdown files should exist" if not missing_pages else f"missing page files: {missing_pages}",
        )
    )

    missing_states = [page["page_id"] for page in page_specs if not page.get("states")]
    checks.append(
        _review_check(
            "required_states_defined",
            "pass" if required_states and not missing_states else "fail",
            "page states should be frozen for each page"
            if required_states and not missing_states
            else f"missing state definitions for: {missing_states or ['all-pages']}",
        )
    )

    traceability_missing = []
    for page in page_specs:
        refs = page.get("requirement_refs") if isinstance(page.get("requirement_refs"), dict) else {}
        if not all(refs.get(doc_type) for doc_type in REQUIRED_SOURCE_TYPES):
            traceability_missing.append(page["page_id"])
    checks.append(
        _review_check(
            "requirement_traceability_complete",
            "pass" if not traceability_missing else "fail",
            "all pages trace back to prd / user-story / test-case"
            if not traceability_missing
            else f"missing requirement refs for: {traceability_missing}",
        )
    )

    transitions = route_closure.get("closure_cases") if isinstance(route_closure.get("closure_cases"), list) else []
    checks.append(
        _review_check(
            "navigation_transitions_present",
            "pass" if transitions else "fail",
            "route closure / navigation transitions should be frozen",
        )
    )

    if route_closure.get("required") is True:
        bound = implementation_map.get("closure_bindings") if isinstance(implementation_map.get("closure_bindings"), list) else []
        checks.append(
            _review_check(
                "route_closure_binding_complete",
                "pass" if len(bound) >= len(transitions) else "fail",
                "route closure bindings are complete"
                if len(bound) >= len(transitions)
                else "route closure bindings are incomplete",
            )
        )
    else:
        checks.append(
            _review_check(
                "route_closure_binding_complete",
                "pass",
                "route closure binding is optional for current wireframe package",
                blocking=False,
            )
        )

    checks.append(
        _review_check(
            "source_map_present",
            "pass" if bool(source_map.get("sources")) else "fail",
            "source-map.json should record requirement sources",
        )
    )
    state_nodes = state_flow_map.get("nodes") if isinstance(state_flow_map.get("nodes"), list) else []
    state_edges = state_flow_map.get("edges") if isinstance(state_flow_map.get("edges"), list) else []
    checks.append(
        _review_check(
            "state_flow_usable",
            "pass" if state_nodes and state_edges else "fail",
            "state-flow map should contain nodes and edges",
        )
    )
    component_items = component_catalog.get("components") if isinstance(component_catalog.get("components"), list) else []
    requirement_ids = plan.get("requirement_ids") if isinstance(plan.get("requirement_ids"), dict) else {}
    require_ac_refs = bool(requirement_ids.get("ac_ids"))
    require_tc_refs = bool(requirement_ids.get("tc_ids"))
    missing_component_refs = []
    for component in component_items:
        if not isinstance(component, dict):
            continue
        if not component.get("state_refs"):
            missing_component_refs.append(str(component.get("component_id") or "unknown"))
            continue
        if require_ac_refs and not component.get("ac_refs"):
            missing_component_refs.append(str(component.get("component_id") or "unknown"))
            continue
        if require_tc_refs and not component.get("tc_refs"):
            missing_component_refs.append(str(component.get("component_id") or "unknown"))
    checks.append(
        _review_check(
            "component_contract_traceability",
            "pass" if component_items and not missing_component_refs else "fail",
            "component catalog should map state + AC + TC"
            if component_items and not missing_component_refs
            else f"missing component trace refs: {missing_component_refs[:10]}",
        )
    )
    checks.append(
        _review_check(
            "transaction_metadata_present",
            "pass"
            if transaction.get("source_hash")
            and transaction.get("projection_seq")
            and transaction.get("transaction_id")
            and transaction.get("committed_at")
            and isinstance(transaction.get("sink_checksums"), dict)
            else "fail",
            "manifest transaction metadata should include source_hash/projection_seq/transaction_id/committed_at/sink_checksums",
        )
    )
    checks.append(
        _review_check(
            "sqlite_projection_written",
            "pass" if sqlite_projection.get("status") == "committed" else "fail",
            "sqlite projection should record the same transaction",
        )
    )
    sink_checksums = transaction.get("sink_checksums") if isinstance(transaction.get("sink_checksums"), dict) else {}
    checks.append(
        _review_check(
            "transaction_sink_checksum_consistent",
            "pass"
            if isinstance(sink_checksums, dict)
            and sink_checksums.get("sqlite")
            and sink_checksums.get("sqlite") != "missing"
            and sink_checksums.get("machine")
            and sink_checksums.get("human")
            else "fail",
            "sink checksums should include human/machine/sqlite",
        )
    )
    checks.append(
        _review_check(
            "manifest_consistency",
            "pass" if str(manifest.get("prototype_mode", "")) == PROTOTYPE_MODE else "fail",
            "manifest should stay aligned with wireframe mode",
        )
    )
    checks.append(
        _review_check(
            "canonical_manifest_consistency",
            "pass"
            if str(canonical_envelope.get("prototype_mode") or "") == PROTOTYPE_MODE
            and str(canonical_envelope.get("source_hash") or "") == str(transaction.get("source_hash") or "")
            and str(canonical_envelope.get("projection_seq") or "") == str(transaction.get("projection_seq") or "")
            and str(canonical_envelope.get("transaction_id") or "") == str(transaction.get("transaction_id") or "")
            else "fail",
            "canonical envelope and manifest transaction metadata should stay consistent",
        )
    )

    blocking_failures = [item for item in checks if item["blocking"] and item["status"] == "fail"]
    overall_status = "pass" if not blocking_failures else "fail"
    human_view_status = "pass" if files["wireframe_summary"].exists() and files["navigation_map_md"].exists() and files["state_flow_map_md"].exists() and files["component_catalog_md"].exists() else "fail"
    machine_contract_status = "pass" if files["canonical_envelope"].exists() and files["wireframe_manifest"].exists() and files["navigation_map"].exists() and files["state_flow_map"].exists() and files["component_catalog"].exists() and files["coverage_report"].exists() else "fail"
    sqlite_projection_status = "pass" if sqlite_projection.get("status") == "committed" else "fail"
    drift_status = (
        "consistent"
        if human_view_status == "pass" and machine_contract_status == "pass" and sqlite_projection_status == "pass"
        else "drift"
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "prototype_mode": PROTOTYPE_MODE,
        "generated_at": now_iso(),
        "overall_status": overall_status,
        "design_review_outcome": "pass" if overall_status == "pass" else "revise",
        "checks": checks,
        "blocking_failures": blocking_failures,
        "human_view_status": human_view_status,
        "machine_contract_status": machine_contract_status,
        "sqlite_projection_status": sqlite_projection_status,
        "drift_status": drift_status,
        "artifacts": {
            "json": str(files["review_json"].relative_to(project_root)),
            "md": str(files["review_md"].relative_to(project_root)),
        },
    }
    _write_json(files["review_json"], payload)
    _write_text(files["review_md"], _render_review_markdown(payload))

    manifest["review_status"] = overall_status
    manifest["design_review_outcome"] = payload["design_review_outcome"]
    manifest["status"] = "reviewed" if overall_status == "pass" else manifest.get("status", "draft")
    manifest["human_view_status"] = human_view_status
    manifest["machine_contract_status"] = machine_contract_status
    manifest["sqlite_projection_status"] = sqlite_projection_status
    manifest["drift_status"] = drift_status
    _write_json(files["manifest"], manifest)
    return payload


def freeze_prototype(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    review_payload = _read_json(files["review_json"])
    if str(review_payload.get("overall_status", "missing")) != "pass":
        raise ValueError("Prototype review missing or failing; run `prototype review` until pass before freeze")

    manifest = _read_json(files["manifest"])
    transaction = manifest.get("transaction") if isinstance(manifest.get("transaction"), dict) else {}
    transaction_id = str(transaction.get("transaction_id") or "")
    sqlite_projection = _read_prototype_projection_sqlite(transaction_id)
    if sqlite_projection.get("status") != "committed":
        raise ValueError("Prototype sqlite projection missing; review cannot be frozen with cross-sink drift")

    source_docs = load_source_documents(project_root, version, feature)
    current_source_hash = _stable_hash([{"type": doc["type"], "fingerprint": doc["fingerprint"]} for doc in source_docs])
    if str(transaction.get("source_hash") or "") != current_source_hash:
        raise ValueError("Prototype source hash drift detected after create; regenerate and review before freeze")

    sink_checksums = transaction.get("sink_checksums") if isinstance(transaction.get("sink_checksums"), dict) else {}
    if not sink_checksums or sink_checksums.get("sqlite") in {None, "", "missing"}:
        raise ValueError("Prototype sink checksums incomplete; regenerate bundle before freeze")

    status_snapshot = evaluate_prototype_status(project_root, version, feature)
    freeze_payload = {
        "schema_version": SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": slugify_feature(feature),
        "version": version,
        "prototype_mode": PROTOTYPE_MODE,
        "status": "frozen",
        "review_status": "pass",
        "frozen_at": now_iso(),
        "source_fingerprints": {doc["type"]: doc["fingerprint"] for doc in source_docs},
        "artifact_fingerprints": _artifact_fingerprints(files),
        "transaction": transaction,
        "human_view_status": status_snapshot.get("human_view_status"),
        "machine_contract_status": status_snapshot.get("machine_contract_status"),
        "sqlite_projection_status": status_snapshot.get("sqlite_projection_status"),
        "drift_status": status_snapshot.get("drift_status"),
    }
    _write_json(files["freeze"], freeze_payload)

    manifest["status"] = "frozen"
    manifest["review_status"] = "pass"
    manifest["design_review_outcome"] = "pass"
    manifest["frozen_at"] = freeze_payload["frozen_at"]
    manifest["source_fingerprints"] = freeze_payload["source_fingerprints"]
    manifest["human_view_status"] = freeze_payload["human_view_status"]
    manifest["machine_contract_status"] = freeze_payload["machine_contract_status"]
    manifest["sqlite_projection_status"] = freeze_payload["sqlite_projection_status"]
    manifest["drift_status"] = freeze_payload["drift_status"]
    _write_json(files["manifest"], manifest)
    return freeze_payload


def evaluate_prototype_status(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    root = files["root"]
    if not root.exists():
        return {
            "status": "missing",
            "exists": False,
            "frozen": False,
            "stale": False,
            "inconsistent": False,
            "inconsistent_reasons": [],
            "prototype_mode": PROTOTYPE_MODE,
            "ui_kit": PROTOTYPE_UI_KIT,
            "review_status": "missing",
            "design_review_outcome": "missing",
            "gate_ready": False,
            "root": root,
            "files": files,
            "paths": {key: str(path) for key, path in files.items()},
            "source_fingerprints": {},
            "recorded_source_fingerprints": {},
            "human_view_status": "missing",
            "machine_contract_status": "missing",
            "sqlite_projection_status": "missing",
            "drift_status": "missing",
            "transaction": {},
        }

    manifest = _read_json(files["manifest"])
    freeze_payload = _read_json(files["freeze"])
    review_payload = _read_json(files["review_json"])
    plan = _read_json(files["prototype_plan"])
    transaction = manifest.get("transaction") if isinstance(manifest.get("transaction"), dict) else {}
    sqlite_projection = _read_prototype_projection_sqlite(str(transaction.get("transaction_id") or ""))
    current_source = {doc["type"]: doc["fingerprint"] for doc in load_source_documents(project_root, version, feature)}
    recorded_source = freeze_payload.get("source_fingerprints") if isinstance(freeze_payload.get("source_fingerprints"), dict) else {}
    if not recorded_source:
        recorded_source = manifest.get("source_fingerprints") if isinstance(manifest.get("source_fingerprints"), dict) else {}

    stale = bool(recorded_source) and bool(current_source) and recorded_source != current_source
    inconsistent_reasons = []
    required_paths = {
        "manifest": files["manifest"],
        "prototype_plan": files["prototype_plan"],
        "canonical_envelope": files["canonical_envelope"],
        "source_map": files["source_map"],
        "freeze": files["freeze"],
        "wireframe_summary": files["wireframe_summary"],
        "wireframe_manifest": files["wireframe_manifest"],
        "navigation_map": files["navigation_map"],
        "navigation_map_md": files["navigation_map_md"],
        "state_flow_map": files["state_flow_map"],
        "state_flow_map_md": files["state_flow_map_md"],
        "component_catalog": files["component_catalog"],
        "component_catalog_md": files["component_catalog_md"],
        "interaction_map": files["interaction_map"],
        "coverage_report": files["coverage_report"],
        "review_json": files["review_json"],
        "review_md": files["review_md"],
        "pages_dir": files["pages_dir"],
        "human_view_dir": files["human_view_dir"],
        "machine_view_dir": files["machine_view_dir"],
    }
    for key, path in required_paths.items():
        if key.endswith("_dir"):
            if not path.exists() or not path.is_dir():
                inconsistent_reasons.append(f"missing_dir:{key}")
        elif not path.exists():
            inconsistent_reasons.append(f"missing_artifact:{key}")
    if files["index_html"].exists():
        inconsistent_reasons.append("legacy_html_present:index_html")

    required_pages = [str(item).strip() for item in (plan.get("required_pages") or []) if str(item).strip()] if isinstance(plan, dict) else []
    missing_pages = [page_id for page_id in required_pages if not (files["pages_dir"] / f"{page_id}.md").exists()]
    if missing_pages:
        inconsistent_reasons.append(f"missing_pages:{','.join(missing_pages)}")

    review_status = str(review_payload.get("overall_status") or manifest.get("review_status") or "missing")
    design_review_outcome = str(review_payload.get("design_review_outcome") or manifest.get("design_review_outcome") or "missing")
    frozen = str(freeze_payload.get("status") or manifest.get("status") or "").lower() == "frozen"

    human_view_status = (
        "pass"
        if all(
            path.exists()
            for path in (
                files["wireframe_summary"],
                files["navigation_map_md"],
                files["state_flow_map_md"],
                files["component_catalog_md"],
            )
        )
        else "fail"
    )
    machine_contract_status = (
        "pass"
        if all(
            path.exists()
            for path in (
                files["canonical_envelope"],
                files["wireframe_manifest"],
                files["navigation_map"],
                files["state_flow_map"],
                files["component_catalog"],
                files["interaction_map"],
                files["coverage_report"],
                files["source_map"],
            )
        )
        else "fail"
    )
    sqlite_projection_status = "pass" if sqlite_projection.get("status") == "committed" else "fail"
    sink_checksums = transaction.get("sink_checksums") if isinstance(transaction.get("sink_checksums"), dict) else {}
    metadata_ok = (
        bool(transaction.get("source_hash"))
        and bool(transaction.get("projection_seq"))
        and bool(transaction.get("transaction_id"))
        and bool(transaction.get("committed_at"))
        and bool(sink_checksums.get("human"))
        and bool(sink_checksums.get("machine"))
        and bool(sink_checksums.get("sqlite"))
        and sink_checksums.get("sqlite") != "missing"
    )
    drift_status = (
        "consistent"
        if metadata_ok and human_view_status == "pass" and machine_contract_status == "pass" and sqlite_projection_status == "pass"
        else "drift"
    )
    if drift_status != "consistent":
        inconsistent_reasons.append("cross_sink_drift_detected")

    if inconsistent_reasons:
        status = "inconsistent"
    elif stale:
        status = "stale"
    elif frozen:
        status = "frozen"
    else:
        status = "draft"

    gate_ready = status == "frozen" and review_status == "pass"
    return {
        "status": status,
        "exists": True,
        "frozen": frozen,
        "stale": stale,
        "inconsistent": bool(inconsistent_reasons),
        "inconsistent_reasons": inconsistent_reasons,
        "prototype_mode": str(plan.get("prototype_mode") or manifest.get("prototype_mode") or PROTOTYPE_MODE),
        "ui_kit": manifest.get("ui_kit") or PROTOTYPE_UI_KIT,
        "review_status": review_status,
        "design_review_outcome": design_review_outcome,
        "gate_ready": gate_ready,
        "root": root,
        "files": files,
        "paths": {key: str(path) for key, path in files.items()},
        "source_fingerprints": current_source,
        "recorded_source_fingerprints": recorded_source if isinstance(recorded_source, dict) else {},
        "human_view_status": human_view_status,
        "machine_contract_status": machine_contract_status,
        "sqlite_projection_status": sqlite_projection_status,
        "drift_status": drift_status,
        "transaction": transaction if isinstance(transaction, dict) else {},
    }
