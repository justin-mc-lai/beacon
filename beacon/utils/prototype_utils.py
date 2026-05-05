"""Requirement-driven wireframe freeze utilities for Beacon prototype."""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request

from beacon.utils.runtime_projection_store import runtime_ledger_root
from beacon.utils.semantic_runtime import (
    build_semantic_capability_snapshot,
    build_mode_contract,
    execute_host_bridge_command,
    llm_unavailable_message,
    load_or_build_semantic_layer,
    load_host_response_json,
    normalize_requested_mode,
    render_semantic_prompt_context,
)


PROTOTYPE_MODE = "wireframe"
PROTOTYPE_UI_KIT = "wireframe-markdown-v1"
DEFAULT_PROTOTYPE_ARCHETYPE = "generic-wireframe"
SCHEMA_VERSION = "1.0"
REQUIRED_SOURCE_TYPES = ("user-story", "prd", "test-case")
AC_PATTERN = re.compile(r"\bAC-\d{3}[A-Z]?\b", re.IGNORECASE)
TC_PATTERN = re.compile(r"\bTC-\d{3}(?:-[A-Z]+)?\b", re.IGNORECASE)
MACHINE_NOISE_PATTERN = re.compile(
    r"(?:sqlite|canonical-envelope|prototype-plan\.json|fingerprint|sink_checksum|transaction_id|projection|machine contract|raw runtime log|host session metadata)",
    re.IGNORECASE,
)
PAGE_ORDER_DEFAULT = (
    "home",
    "management-overview",
    "project-detail",
    "runtime-center",
    "recovery-diagnostics",
    "material-viewer",
)


def _semver_tuple(value: str | None) -> tuple[int, int, int]:
    text = str(value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    parts = text.split(".")
    numbers: list[int] = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits or "0"))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def _prototype_auto_fallback_blocked(version: str, compiler: dict[str, Any] | None) -> bool:
    payload = compiler if isinstance(compiler, dict) else {}
    return (
        _semver_tuple(version) >= (1, 3, 9)
        and str(payload.get("requested_mode") or "").strip().lower() == "auto"
        and bool(str(payload.get("fallback_reason") or "").strip())
    )


def _prototype_auto_fallback_accepted(
    *,
    version: str,
    compiler: dict[str, Any] | None,
    review_status: str,
    frozen: bool,
    supports_ux_truth: bool,
    files: dict[str, Path],
    plan: dict[str, Any] | None,
) -> bool:
    if not _prototype_auto_fallback_blocked(version, compiler):
        return False
    if str(review_status or "").strip().lower() != "pass":
        return False
    if not frozen or not supports_ux_truth:
        return False
    semantic_profile = (plan or {}).get("software_semantic_profile") if isinstance(plan, dict) else {}
    semantic_contract_path = ""
    if isinstance(plan, dict):
        semantic_contract_path = str((((plan.get("semantic_layer") or {}).get("artifacts") or {}).get("semantic_contract") or "")).strip()
    return (
        isinstance(semantic_profile, dict)
        and all(semantic_profile.get(key) for key in ("title_rule", "state_rule", "action_rule", "exception_rule"))
        and files["ux_prd"].exists()
        and files["design_md"].exists()
        and files["preview_html"].exists()
        and files["preview_dark_html"].exists()
        and bool(semantic_contract_path)
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
    "portfolio-board": {
        "name": "项目组合看板",
        "keywords": ("portfolio-board", "项目组合", "组合看板", "项目组合看板"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "汇总当前版本线的 feature 状态、阻塞分布与建议波次，支持先判断先处理哪一组事项。",
        "decision_supported": "当前应先进入阻塞 feature、待验收 feature，还是继续观察整体版本健康态。",
        "sections": ["状态摘要", "阻塞分组", "待验收分组", "下一步动作"],
        "actions": [
            {"label": "进入执行看板", "target": "execution-board", "trigger": "点击执行看板入口"},
            {"label": "进入功能详情", "target": "feature-detail", "trigger": "点击功能项"},
        ],
        "states": [
            {"id": "ready", "label": "可用", "description": "组合状态已汇总，可继续下钻。"},
            {"id": "blocked", "label": "阻塞", "description": "存在需要优先介入的阻塞 feature。"},
            {"id": "needs-review", "label": "待验收", "description": "存在需要进入验收面的 feature。"},
            {"id": "loading", "label": "加载中", "description": "组合状态仍在汇总。"},
            {"id": "error", "label": "错误", "description": "组合聚合失败，必须给出恢复入口。"},
        ],
    },
    "execution-board": {
        "name": "执行看板",
        "keywords": ("execution-board", "执行看板", "运行看板"),
        "priority": "P0",
        "platforms": ["Web", "PC"],
        "responsibility": "先暴露当前运行状态、阻塞项与下一步动作，而不是先展示全量运行历史。",
        "decision_supported": "当前应继续、停止、重试，还是先进入恢复路径。",
        "sections": ["当前状态", "当前阻塞", "下一步动作", "运行分组"],
        "actions": [
            {"label": "进入运行详情", "target": "run-detail", "trigger": "点击运行项"},
            {"label": "进入恢复诊断", "target": "recovery-diagnostics", "trigger": "点击阻塞或异常项"},
            {"label": "进入功能详情", "target": "feature-detail", "trigger": "点击 feature 关联"},
        ],
        "states": [
            {"id": "ready", "label": "可用", "description": "当前运行态完整，可执行继续、停止或重试。"},
            {"id": "blocked", "label": "阻塞", "description": "存在阻塞运行，必须优先判断恢复路径。"},
            {"id": "needs-review", "label": "待验收", "description": "存在待验收运行，需要进入验收面。"},
            {"id": "retry-scheduled", "label": "已排队重试", "description": "存在待重试运行，需确认是否继续。"},
            {"id": "loading", "label": "加载中", "description": "运行状态仍在读取。"},
            {"id": "error", "label": "错误", "description": "运行状态读取失败，必须暴露恢复路径。"},
        ],
    },
    "feature-detail": {
        "name": "功能详情",
        "keywords": ("feature-detail", "功能详情", "feature 详情"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "聚合单个 feature 的基线、依赖、当前状态与建议动作，支持判断是否继续实现或先回修。",
        "decision_supported": "当前 feature 应继续推进、等待依赖，还是进入恢复或验收路径。",
        "sections": ["功能摘要", "依赖与基线", "状态与风险", "下一步动作"],
        "actions": [
            {"label": "进入运行详情", "target": "run-detail", "trigger": "点击关联运行"},
            {"label": "进入验收面", "target": "review-surface", "trigger": "点击验收入口"},
        ],
        "states": [
            {"id": "ready", "label": "可用", "description": "功能状态完整，可判断下一步。"},
            {"id": "blocked", "label": "阻塞", "description": "功能依赖或基线存在阻塞。"},
            {"id": "needs-review", "label": "待验收", "description": "功能已进入待验收状态。"},
            {"id": "error", "label": "错误", "description": "功能状态聚合失败，需进入恢复路径。"},
        ],
    },
    "run-detail": {
        "name": "运行详情",
        "keywords": ("run-detail", "运行详情"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "聚合单次运行的状态时间线、写入范围、证据与建议动作，避免操作者在散落材料中自行拼接上下文。",
        "decision_supported": "当前运行应继续、停止、重试，还是转入 repair handoff。",
        "sections": ["运行状态", "阻塞原因", "建议动作", "二级明细"],
        "actions": [
            {"label": "进入恢复诊断", "target": "recovery-diagnostics", "trigger": "点击阻塞原因"},
            {"label": "进入验收面", "target": "review-surface", "trigger": "点击验收入口"},
        ],
        "states": [
            {"id": "running", "label": "运行中", "description": "当前运行仍在推进。"},
            {"id": "blocked", "label": "阻塞", "description": "当前运行被阻断，必须优先判断恢复动作。"},
            {"id": "needs-review", "label": "待验收", "description": "当前运行等待验收。"},
            {"id": "retry-scheduled", "label": "已排队重试", "description": "当前运行等待重试。"},
            {"id": "error", "label": "错误", "description": "当前运行状态不一致，必须暴露恢复路径。"},
        ],
    },
    "review-surface": {
        "name": "验收面",
        "keywords": ("review-surface", "验收面", "review 面"),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": "集中展示差异入口、验收证据与发布提示，支持判断是否放行或回修。",
        "decision_supported": "当前项应通过验收、回到修复路径，还是继续收集证据。",
        "sections": ["验收状态", "差异入口", "证据入口", "放行建议"],
        "actions": [
            {"label": "返回运行详情", "target": "run-detail", "trigger": "点击返回"},
            {"label": "进入恢复诊断", "target": "recovery-diagnostics", "trigger": "点击回修入口"},
        ],
        "states": [
            {"id": "ready", "label": "可验收", "description": "验收证据完整，可判断是否放行。"},
            {"id": "needs-evidence", "label": "证据不足", "description": "验收证据不足，不能放行。"},
            {"id": "blocked", "label": "阻塞", "description": "验收存在阻塞，必须进入回修路径。"},
            {"id": "error", "label": "错误", "description": "验收聚合失败，需优先给出恢复动作。"},
        ],
    },
}

PAGE_ANALYSIS_CATALOG: dict[str, dict[str, Any]] = {
    "home": {
        "target_user": "Beacon 管理者 / owner / 负责人",
        "decision_focus": [
            "今天先盯哪些项目，而不是先看所有项目明细。",
            "哪些阻塞已经升级成需要人工介入的经营问题。",
            "当前交付是否继续按版本线推进，还是需要下钻到项目详情。",
        ],
        "layout_rules": [
            "首屏先给经营判断，不先铺完整表格。",
            "阻塞与介入信息必须比常规进度更靠上。",
            "runtime 只保留摘要，不在首页展开机器内部细节。",
        ],
        "noise_guardrail": "首页不承载 session、agent、原始 requirement 路径等机器噪音。",
    },
    "management-overview": {
        "target_user": "管理端值守人 / 组合视角负责人",
        "decision_focus": [
            "多项目之间谁健康、谁阻塞、谁接近可发布。",
            "是否需要通过筛选和排序快速收敛到一批项目。",
            "什么时候应该从组合视图下钻到单项目接力页。",
        ],
        "layout_rules": [
            "工具栏必须紧贴项目注册表，减少扫描跳跃。",
            "项目注册表承担密集比较，不承担深度解释。",
            "风险、debug、推荐 skill 放在表格侧边或下方收口，不抢主扫描节奏。",
        ],
        "noise_guardrail": "总览页只展示管理判断信号，不直接展开 doctor 或 runtime 原始上下文。",
    },
    "project-detail": {
        "target_user": "单项目 owner / 接力执行者",
        "decision_focus": [
            "这条版本线当前停在哪个阶段，下一步应该推进哪里。",
            "需求闭环是否完整，是否已经具备 implement / qa 的前提。",
            "应该去 runtime、恢复诊断，还是去看项目物料。",
        ],
        "layout_rules": [
            "项目头部先建立上下文，再展开需求闭环。",
            "主 PRD 与并行 PRD 要并排出现，避免真相散落。",
            "最近交付、下一步、推荐动作要形成明确收口。",
        ],
        "noise_guardrail": "项目详情是接力页，不直接承载底层日志和实现细节。",
    },
    "runtime-center": {
        "target_user": "需要核对运行态的执行者 / 诊断人",
        "decision_focus": [
            "当前到底是 single、team 还是 ralph 在推进。",
            "linked run、artifact、blocker 是否足以解释当前停滞点。",
            "看完运行态后应该回到项目详情还是继续诊断。",
        ],
        "layout_rules": [
            "模式切换必须固定在头部，便于横向比较三种运行形态。",
            "session / artifact 只展示必要引用，不在此页堆底层原文。",
            "最近结果与 blocker 必须直接可读，避免继续翻查多层结构。",
        ],
        "noise_guardrail": "运行中心可以下钻运行信息，但仍要压制无边界的机器内部明细。",
    },
    "recovery-diagnostics": {
        "target_user": "负责恢复上下文的人",
        "decision_focus": [
            "当前是 degraded、rebuild 还是 doctor 场景。",
            "真相是否仍然回到 docs/beacon 与 .beacon。",
            "用户该做哪一步恢复，而不是读一堆诊断术语。",
        ],
        "layout_rules": [
            "先讲 truth 来源，再给诊断卡和恢复步骤。",
            "风险提示要比操作细节更醒目，避免误用恢复动作。",
            "恢复动作要收口成少量步骤，不展开内部实现机制。",
        ],
        "noise_guardrail": "诊断页解释机器状态，但不能反客为主替代 requirement truth。",
    },
    "material-viewer": {
        "target_user": "查看 Beacon 物料的人",
        "decision_focus": [
            "当前要看哪个版本、哪类文档、哪个 feature。",
            "Markdown 物料是否存在，并能否稳定切换浏览。",
            "这只是只读消费面，真相仍在本地 docs/beacon 与 .beacon。",
        ],
        "layout_rules": [
            "左侧负责层级导航，右侧负责稳定阅读，职责不能混乱。",
            "来源路径只做可信来源说明，不压过正文阅读体验。",
            "版本切换要靠近树和目录，不要藏到正文底部。",
        ],
        "noise_guardrail": "物料页必须坚持只读查看，不暴露机器索引或编辑入口。",
    },
    "material-document-detail": {
        "target_user": "需要持续阅读单篇物料的审阅者",
        "decision_focus": [
            "当前读的是哪一版、哪一类、哪个 feature 的文档。",
            "如何在同类文档之间切换，而不丢失阅读上下文。",
            "当来源缺失时，用户如何回退到上层查看器。",
        ],
        "layout_rules": [
            "面包屑和文档头部先稳定上下文，再展开正文。",
            "正文区必须占据视觉主体，切换控件退居辅助位置。",
            "来源路径只作为可信性补充，不与正文争抢注意力。",
        ],
        "noise_guardrail": "详情阅读页不展示机器合同或 requirement 文件路径原文。",
    },
}


class PrototypeLLMCompileError(RuntimeError):
    """Raised when the prototype LLM call or payload extraction fails."""


class PrototypeLLMContractError(ValueError):
    """Raised when the prototype LLM payload violates Beacon wireframe contracts."""

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
    {"from": "runtime-center", "to": "management-overview", "trigger": "点击面包屑", "type": "return"},
    {"from": "recovery-diagnostics", "to": "project-detail", "trigger": "点击返回", "type": "return"},
    {"from": "recovery-diagnostics", "to": "runtime-center", "trigger": "点击运行态关联", "type": "drill-down"},
    {"from": "material-viewer", "to": "project-detail", "trigger": "点击返回", "type": "return"},
    {"from": "material-viewer", "to": "material-document-detail", "trigger": "点击文档列表项", "type": "drill-down"},
    {"from": "material-document-detail", "to": "material-viewer", "trigger": "点击返回", "type": "return"},
]

FIELD_PATTERNS = {
    "prototype_archetype": re.compile(r"prototype_archetype\s*[:=]\s*([A-Za-z0-9_-]+)", re.IGNORECASE),
    "prototype_ux_prd_required": re.compile(r"prototype_ux_prd_required\s*[:=]\s*(true|false)", re.IGNORECASE),
    "product_surface_type": re.compile(r"product_surface_type\s*[:=]\s*([A-Za-z0-9_-]+)", re.IGNORECASE),
    "theme_primary": re.compile(r"theme_primary\s*[:=]\s*(#[0-9A-Fa-f]{6})", re.IGNORECASE),
    "theme_secondary": re.compile(r"theme_secondary\s*[:=]\s*(#[0-9A-Fa-f]{6})", re.IGNORECASE),
    "route_closure_required": re.compile(r"route_closure_required\s*[:=]\s*(true|false)", re.IGNORECASE),
    "target_audience": re.compile(r"target_audience\s*[:=]\s*(.+)", re.IGNORECASE),
    "primary_use_cases": re.compile(r"primary_use_cases\s*[:=]\s*(.+)", re.IGNORECASE),
    "operator_mental_state": re.compile(r"operator_mental_state\s*[:=]\s*(.+)", re.IGNORECASE),
    "usage_environment": re.compile(r"usage_environment\s*[:=]\s*(.+)", re.IGNORECASE),
    "brand_tone": re.compile(r"brand_tone\s*[:=]\s*(.+)", re.IGNORECASE),
    "density_preference": re.compile(r"density_preference\s*[:=]\s*(.+)", re.IGNORECASE),
    "design_preset": re.compile(r"design_preset\s*[:=]\s*([A-Za-z0-9_-]+)", re.IGNORECASE),
    "design_preset_override_reason": re.compile(r"design_preset_override_reason\s*[:=]\s*(.+)", re.IGNORECASE),
}

PAGE_HINT_PATTERN = re.compile(
    r"(?:\bpage\b|\bscreen\b|页面|视图|看板|中心|详情|列表|viewer|dashboard|console|panel)",
    re.IGNORECASE,
)
STOP_PAGE_TOKENS = (
    "需求",
    "测试",
    "验收",
    "状态",
    "路由",
    "组件",
    "流程",
    "说明",
    "冻结",
    "prototype",
    "wireframe",
    "只读查看",
    "映射",
    "网页内",
)
TRANSITION_HINT_PATTERN = re.compile(r"(->|→|=>|跳转|进入|返回|to\b)", re.IGNORECASE)
PAGE_DECLARATION_HINT_PATTERN = re.compile(
    r"(?:^#{1,6}\s+.*(?:pages\b|screens\b|views\b|page inventory\b|页面列表|正式页面|页面名称|required pages)\b|(?:正式页面|页面名称固定为|只允许冻结以下正式页面|required_pages)\s*[:：]?)",
    re.IGNORECASE,
)
FORBIDDEN_PAGE_CONTEXT_PATTERN = re.compile(
    r"(?:不是页面名|禁止作为页面名|不应生成|不得出现|禁止生成|错误提升为页面|不能生成)",
    re.IGNORECASE,
)


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
    human_view_dir = root / "human-view"
    machine_view_dir = root / "machine-view"
    verification_dir = root / "verification"
    assets_dir = root / "assets"
    implementation_dir = root / "implementation"

    def _prefer(primary: Path, *fallbacks: Path) -> Path:
        if primary.exists():
            return primary
        for fallback in fallbacks:
            if fallback.exists():
                return fallback
        return primary

    return {
        "root": root,
        "human_view_dir": human_view_dir,
        "machine_view_dir": machine_view_dir,
        "verification_dir": verification_dir,
        "assets_dir": assets_dir,
        "implementation_dir": implementation_dir,
        "manifest": root / "manifest.json",
        "prototype_plan": root / "prototype-plan.json",
        "prototype_brief": root / "prototype-brief.json",
        "canonical_envelope": root / "canonical-envelope.json",
        "artifact_topology": root / "artifact-topology.json",
        "source_map": root / "source-map.json",
        "freeze": root / "freeze.json",
        "review_json": _prefer(root / "prototype-review.json", verification_dir / "prototype-review.json"),
        "review_md": _prefer(root / "prototype-review.md", verification_dir / "prototype-review.md"),
        "verification_index": verification_dir / "index.json",
        "wireframe_summary": _prefer(root / "wireframe-summary.md", human_view_dir / "wireframe-summary.md"),
        "wireframe_manifest": _prefer(root / "wireframe-manifest.json", machine_view_dir / "wireframe-manifest.json"),
        "navigation_map": _prefer(root / "navigation-map.json", machine_view_dir / "navigation-map.json"),
        "navigation_map_md": _prefer(root / "navigation-map.md", human_view_dir / "navigation-map.md"),
        "state_flow_map": _prefer(root / "state-flow-map.json", machine_view_dir / "state-flow-map.json"),
        "state_flow_map_md": _prefer(root / "state-flow-map.md", human_view_dir / "state-flow-map.md"),
        "component_catalog": _prefer(root / "component-catalog.json", machine_view_dir / "component-catalog.json"),
        "component_catalog_md": _prefer(root / "component-catalog.md", human_view_dir / "component-catalog.md"),
        "automation_priority_matrix": _prefer(
            root / "automation-priority-matrix.json",
            machine_view_dir / "automation-priority-matrix.json",
        ),
        "automation_priority_matrix_md": _prefer(
            root / "automation-priority-matrix.md",
            human_view_dir / "automation-priority-matrix.md",
        ),
        "interaction_map": _prefer(root / "interaction-map.json", machine_view_dir / "interaction-map.json"),
        "coverage_report": _prefer(root / "coverage-report.json", machine_view_dir / "coverage-report.json"),
        "theme": _prefer(root / "theme.json", assets_dir / "theme.json"),
        "tokens_css": _prefer(root / "tokens.css", assets_dir / "tokens.css"),
        "platform_variants": _prefer(root / "platform-variants.json", assets_dir / "platform-variants.json"),
        "implementation_map": _prefer(root / "implementation-map.json", implementation_dir / "implementation-map.json"),
        "implementation_index": implementation_dir / "index.json",
        "route_closure_contract": _prefer(
            root / "route-closure-contract.json",
            machine_view_dir / "route-closure-contract.json",
        ),
        "pages_dir": _prefer(root / "pages", human_view_dir / "wireframes"),
        "page_specs_dir": _prefer(root / "page-specs", machine_view_dir / "page-specs"),
        "design_artifacts_dir": _prefer(root / "design-artifacts", machine_view_dir / "design-artifacts"),
        "ux_prd": _prefer(root / "ux-prd.md", human_view_dir / "ux-prd.md"),
        "design_md": _prefer(root / "DESIGN.md", assets_dir / "DESIGN.md"),
        "preview_html": _prefer(root / "preview.html", assets_dir / "preview.html"),
        "preview_dark_html": _prefer(root / "preview-dark.html", assets_dir / "preview-dark.html"),
        "index_html": root / "index.html",
    }


def _has_named_artifact(directory: Path, name: str, suffix: str) -> bool:
    target = directory / f"{name}{suffix}"
    if target.exists():
        return True
    if not directory.exists() or not directory.is_dir():
        return False
    expected_suffix = f"{name}{suffix}"
    return any(path.is_file() and path.name.endswith(expected_suffix) for path in directory.iterdir())


def source_doc_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    base = project_root / "docs" / "beacon" / version
    return {
        "user-story": _resolve_feature_doc_path(base / "user-story", feature),
        "prd": _resolve_feature_doc_path(base / "prd", feature),
        "test-case": _resolve_feature_doc_path(base / "qa" / "test-cases", feature),
    }


def legacy_prototype_source_path(project_root: Path, version: str, feature: str) -> Path:
    return _resolve_feature_doc_path(project_root / "docs" / "beacon" / version / "prototype", feature)


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


def _copy_json_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return json.loads(json.dumps(value, ensure_ascii=False))


def _current_prototype_source_fingerprints(project_root: Path, version: str, feature: str) -> dict[str, str]:
    return {
        doc["type"]: doc["fingerprint"]
        for doc in load_source_documents(project_root, version, feature)
    }


def _current_prototype_source_hash(project_root: Path, version: str, feature: str) -> str:
    source_docs = load_source_documents(project_root, version, feature)
    return _stable_hash([{"type": doc["type"], "fingerprint": doc["fingerprint"]} for doc in source_docs])


def _collect_runtime_sink_checksums(root: Path) -> dict[str, str]:
    human_fingerprints: dict[str, str] = {}
    machine_fingerprints: dict[str, str] = {}
    if root.exists():
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(root))
            fingerprint = sha256_file(path)
            if rel.endswith((".md", ".css", ".html")):
                human_fingerprints[rel] = fingerprint
            if rel.endswith(".json"):
                machine_fingerprints[rel] = fingerprint
    return {
        "human": _stable_hash(human_fingerprints),
        "machine": _stable_hash(machine_fingerprints),
    }


def _canonical_truth_fields() -> tuple[str, ...]:
    return ("design_context", "design_reasoning", "ux_contract", "software_semantic_profile")


def _load_prototype_canonical_truth(
    files: dict[str, Path],
    *,
    plan: dict[str, Any] | None = None,
    manifest: dict[str, Any] | None = None,
    canonical_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    plan_payload = plan if isinstance(plan, dict) else _read_json(files["prototype_plan"])
    manifest_payload = manifest if isinstance(manifest, dict) else _read_json(files["manifest"])
    canonical_payload = canonical_envelope if isinstance(canonical_envelope, dict) else _read_json(files["canonical_envelope"])
    brief_payload = _read_json(files["prototype_brief"])
    theme_payload = _read_json(files["theme"])

    ordered_sources: list[tuple[str, dict[str, Any]]] = []
    if brief_payload:
        ordered_sources.append(("prototype-brief", brief_payload))
    if manifest_payload:
        ordered_sources.append(("manifest", manifest_payload))
    if canonical_payload:
        ordered_sources.append(("canonical-envelope", canonical_payload))
    if plan_payload:
        ordered_sources.append(("prototype-plan", plan_payload))

    truth_source = ""
    truth_payload: dict[str, Any] = {}
    available = False
    for source_name, source_payload in ordered_sources:
        has_truth = any(
            bool(source_payload.get(field))
            for field in (*_canonical_truth_fields(), "design_context", "design_reasoning", "ux_contract")
        )
        if has_truth:
            truth_source = source_name
            truth_payload = source_payload
            available = True
            break

    merged: dict[str, Any] = {
        "truth_source": truth_source or "prototype-plan",
        "available": available or bool(plan_payload),
    }
    for field in _canonical_truth_fields():
        value: dict[str, Any] = {}
        for source_name, source_payload in ordered_sources:
            if field == "software_semantic_profile":
                candidate = source_payload.get(field)
                if not isinstance(candidate, dict) and source_name == "canonical-envelope":
                    plan_block = source_payload.get("plan") if isinstance(source_payload.get("plan"), dict) else {}
                    candidate = plan_block.get(field)
            else:
                candidate = source_payload.get(field)
                if not isinstance(candidate, dict) and source_name == "canonical-envelope":
                    plan_block = source_payload.get("plan") if isinstance(source_payload.get("plan"), dict) else {}
                    candidate = plan_block.get(field)
            if isinstance(candidate, dict) and candidate:
                value = _copy_json_object(candidate)
                break
        merged[field] = value

    merged_theme = {}
    if theme_payload:
        merged_theme = _copy_json_object(theme_payload)
    else:
        for source_name, source_payload in ordered_sources:
            candidate = source_payload.get("theme")
            if not isinstance(candidate, dict) and source_name == "canonical-envelope":
                plan_block = source_payload.get("plan") if isinstance(source_payload.get("plan"), dict) else {}
                candidate = plan_block.get("theme")
            if isinstance(candidate, dict) and candidate:
                merged_theme = _copy_json_object(candidate)
                break
    merged["theme"] = merged_theme
    merged["source_payload"] = truth_payload
    return merged


def _apply_canonical_truth_to_plan(
    plan: dict[str, Any],
    *,
    canonical_truth: dict[str, Any],
) -> dict[str, Any]:
    updated = _copy_json_object(plan)
    for field in _canonical_truth_fields():
        value = canonical_truth.get(field)
        if isinstance(value, dict) and value:
            updated[field] = _copy_json_object(value)
    theme_value = canonical_truth.get("theme")
    if isinstance(theme_value, dict) and theme_value:
        updated["theme"] = _copy_json_object(theme_value)
    updated["canonical_truth_source"] = str(canonical_truth.get("truth_source") or "prototype-plan")
    return updated


def _prototype_sink_truth_mismatches(
    *,
    plan: dict[str, Any],
    manifest: dict[str, Any],
    canonical_envelope: dict[str, Any],
    canonical_truth: dict[str, Any],
) -> dict[str, list[str]]:
    mismatches: dict[str, list[str]] = {}
    sink_payloads: list[tuple[str, dict[str, Any]]] = [
        ("prototype-plan", plan if isinstance(plan, dict) else {}),
        ("manifest", manifest if isinstance(manifest, dict) else {}),
        ("canonical-envelope", canonical_envelope if isinstance(canonical_envelope, dict) else {}),
    ]
    for sink_name, sink_payload in sink_payloads:
        sink_mismatches: list[str] = []
        for field in _canonical_truth_fields():
            truth_value = canonical_truth.get(field)
            if not isinstance(truth_value, dict) or not truth_value:
                continue
            candidate = sink_payload.get(field)
            if not isinstance(candidate, dict) and sink_name == "canonical-envelope":
                plan_block = sink_payload.get("plan") if isinstance(sink_payload.get("plan"), dict) else {}
                candidate = plan_block.get(field)
            if not isinstance(candidate, dict) or candidate != truth_value:
                sink_mismatches.append(field)
        truth_theme = canonical_truth.get("theme")
        if isinstance(truth_theme, dict) and truth_theme:
            if sink_name == "canonical-envelope":
                plan_block = sink_payload.get("plan") if isinstance(sink_payload.get("plan"), dict) else {}
                candidate_theme = plan_block.get("theme")
            else:
                candidate_theme = sink_payload.get("theme")
            if isinstance(candidate_theme, dict) and candidate_theme != truth_theme:
                sink_mismatches.append("theme")
        if sink_mismatches:
            mismatches[sink_name] = sorted(set(sink_mismatches))
    return mismatches


def _classify_prototype_runtime_drift(
    *,
    current_source: dict[str, str],
    recorded_source: dict[str, Any],
    transaction: dict[str, Any],
    inconsistent_reasons: list[str],
    sqlite_projection_status: str,
    canonical_truth: dict[str, Any],
    sink_truth_mismatches: dict[str, list[str]],
    current_source_hash: str,
) -> dict[str, str]:
    recorded = recorded_source if isinstance(recorded_source, dict) else {}
    transaction_source_hash = str(transaction.get("source_hash") or "").strip()
    has_required_truth = bool(canonical_truth.get("available"))
    if not has_required_truth:
        return {
            "drift_type": "canonical-truth-missing",
            "reason_code": "prototype_canonical_truth_missing",
            "diagnosis": "prototype canonical truth is missing or unreadable",
            "next_action": "prototype create",
            "repair_path": "destructive-recreate-required",
        }
    if any(
        reason.startswith("missing_artifact:manifest")
        or reason.startswith("missing_artifact:prototype_plan")
        or reason.startswith("missing_artifact:canonical_envelope")
        for reason in inconsistent_reasons
    ):
        return {
            "drift_type": "destructive-recreate-required",
            "reason_code": "prototype_destructive_recreate_required",
            "diagnosis": "prototype bundle is missing authoritative core artifacts and cannot be repaired safely",
            "next_action": "prototype create",
            "repair_path": "destructive-recreate-required",
        }
    if sink_truth_mismatches:
        return {
            "drift_type": "sink-drift",
            "reason_code": "prototype_sink_drift",
            "diagnosis": "structured prototype sinks diverged from canonical truth",
            "next_action": "prototype reconcile",
            "repair_path": "nondestructive-reconcile",
        }
    if recorded and current_source and recorded != current_source:
        return {
            "drift_type": "source-drift",
            "reason_code": "prototype_source_drift",
            "diagnosis": "prototype requirement source fingerprints changed after the last recorded freeze or review metadata",
            "next_action": "prototype reconcile",
            "repair_path": "reconcile-then-review",
        }
    if transaction_source_hash and current_source_hash and transaction_source_hash != current_source_hash:
        return {
            "drift_type": "transaction-header-drift",
            "reason_code": "prototype_transaction_header_drift",
            "diagnosis": "prototype transaction headers no longer match the current requirement source hash",
            "next_action": "prototype reconcile",
            "repair_path": "metadata-repair",
        }
    if sqlite_projection_status != "pass" or any(reason.startswith("cross_sink_drift") for reason in inconsistent_reasons):
        return {
            "drift_type": "metadata-only-drift",
            "reason_code": "prototype_metadata_drift",
            "diagnosis": "prototype metadata or cross-sink projection state is incomplete",
            "next_action": "prototype reconcile",
            "repair_path": "metadata-repair",
        }
    return {
        "drift_type": "",
        "reason_code": "",
        "diagnosis": "",
        "next_action": "",
        "repair_path": "",
    }


def reconcile_prototype_bundle(project_root: Path, version: str, feature: str) -> dict[str, Any]:
    files = prototype_files(project_root, version, feature)
    if not files["root"].exists():
        raise FileNotFoundError("prototype bundle missing; run prototype create first")

    plan = _read_json(files["prototype_plan"])
    manifest = _read_json(files["manifest"])
    canonical_envelope = _read_json(files["canonical_envelope"])
    freeze_payload = _read_json(files["freeze"])
    review_payload = _read_json(files["review_json"])
    prototype_brief = _read_json(files["prototype_brief"])
    theme_payload = _read_json(files["theme"])

    if not plan or not manifest or not canonical_envelope:
        raise ValueError("prototype core artifacts missing; run `prototype create` to rebuild the bundle")

    canonical_truth = _load_prototype_canonical_truth(
        files,
        plan=plan,
        manifest=manifest,
        canonical_envelope=canonical_envelope,
    )
    if not canonical_truth.get("available"):
        raise ValueError("prototype canonical truth missing; run `prototype create` to rebuild the bundle")

    source_docs = load_source_documents(project_root, version, feature)
    feature_slug = str(plan.get("feature_slug") or manifest.get("feature_slug") or slugify_feature(feature))
    supports_ux_truth = _supports_ux_truth(version, source_docs)
    current_source_fingerprints = {doc["type"]: doc["fingerprint"] for doc in source_docs}
    current_source_hash = _stable_hash(
        [{"type": doc["type"], "fingerprint": doc["fingerprint"]} for doc in source_docs]
    )
    projection_seq = f"pp-{current_source_hash[:16]}"
    committed_at = now_iso()
    transaction_id = f"tx-{feature_slug}-{projection_seq}"

    plan = _apply_canonical_truth_to_plan(plan, canonical_truth=canonical_truth)
    plan["version"] = version
    plan["feature"] = feature
    plan["feature_slug"] = feature_slug
    if isinstance(theme_payload, dict) and theme_payload:
        plan["theme"] = _copy_json_object(theme_payload)

    source_map = _build_source_map(project_root, source_docs, plan)
    wireframe_manifest = _build_wireframe_manifest(plan)
    coverage = _build_coverage_report(plan)

    canonical_envelope = _copy_json_object(canonical_envelope)
    canonical_envelope.update(
        {
            "schema_version": SCHEMA_VERSION,
            "feature": feature,
            "feature_slug": feature_slug,
            "version": version,
            "prototype_mode": PROTOTYPE_MODE,
            "source_hash": current_source_hash,
            "projection_seq": projection_seq,
            "transaction_id": transaction_id,
            "committed_at": committed_at,
            "plan": plan,
            "source_map": source_map,
            "coverage_report": coverage,
            "design_context": _copy_json_object(canonical_truth.get("design_context")),
            "design_reasoning": _copy_json_object(canonical_truth.get("design_reasoning")),
            "ux_contract": _copy_json_object(canonical_truth.get("ux_contract")),
        }
    )
    if supports_ux_truth:
        canonical_envelope["software_semantic_profile"] = _copy_json_object(
            canonical_truth.get("software_semantic_profile")
        )
    if isinstance(plan.get("theme"), dict) and plan.get("theme"):
        canonical_envelope["theme"] = _copy_json_object(plan.get("theme"))
    if isinstance(canonical_envelope.get("plan"), dict):
        canonical_envelope["plan"] = _apply_canonical_truth_to_plan(
            canonical_envelope["plan"],
            canonical_truth=canonical_truth,
        )
        canonical_envelope["plan"]["version"] = version
        canonical_envelope["plan"]["feature"] = feature
        canonical_envelope["plan"]["feature_slug"] = feature_slug
        canonical_envelope["plan"]["theme"] = _copy_json_object(plan.get("theme"))

    manifest = _copy_json_object(manifest)
    manifest["schema_version"] = SCHEMA_VERSION
    manifest["feature"] = feature
    manifest["feature_slug"] = feature_slug
    manifest["version"] = version
    manifest["prototype_mode"] = PROTOTYPE_MODE
    manifest["source_fingerprints"] = current_source_fingerprints
    manifest["design_context"] = _copy_json_object(canonical_truth.get("design_context"))
    manifest["design_reasoning"] = _copy_json_object(canonical_truth.get("design_reasoning"))
    manifest["ux_contract"] = _copy_json_object(canonical_truth.get("ux_contract"))
    if supports_ux_truth:
        manifest["software_semantic_profile"] = _copy_json_object(canonical_truth.get("software_semantic_profile"))

    prototype_brief = _copy_json_object(prototype_brief)
    prototype_brief["prototype_mode"] = PROTOTYPE_MODE
    prototype_brief["theme"] = _copy_json_object(plan.get("theme"))
    prototype_brief["page_count"] = len(plan.get("page_specs") or [])
    prototype_brief["design_context"] = _copy_json_object(canonical_truth.get("design_context"))
    prototype_brief["design_reasoning"] = _copy_json_object(canonical_truth.get("design_reasoning"))
    prototype_brief["ux_contract"] = _copy_json_object(canonical_truth.get("ux_contract"))
    if supports_ux_truth:
        prototype_brief["software_semantic_profile"] = _copy_json_object(
            canonical_truth.get("software_semantic_profile")
        )

    _write_json(files["prototype_plan"], plan)
    _write_json(files["wireframe_manifest"], wireframe_manifest)
    _write_json(files["source_map"], source_map)
    _write_json(files["coverage_report"], coverage)
    _write_json(files["canonical_envelope"], canonical_envelope)
    _write_json(files["prototype_brief"], prototype_brief)

    for page in plan.get("page_specs") or []:
        if not isinstance(page, dict) or not page.get("page_id"):
            continue
        _write_json(files["page_specs_dir"] / f"{page['page_id']}.json", _serialize_page_spec(page))

    human_machine_checksums = _collect_runtime_sink_checksums(files["root"])
    sqlite_payload = {
        "schema_version": SCHEMA_VERSION,
        "transaction_id": transaction_id,
        "feature_slug": feature_slug,
        "version": version,
        "projection_seq": projection_seq,
        "source_hash": current_source_hash,
        "committed_at": committed_at,
        "status": "committed",
        "root_path": str(files["root"]),
        "sink_checksums": {
            "human": human_machine_checksums.get("human"),
            "machine": human_machine_checksums.get("machine"),
        },
    }
    sqlite_write = {"status": "failed", "error": "not_written"}
    sink_checksums = {
        "human": human_machine_checksums.get("human"),
        "machine": human_machine_checksums.get("machine"),
        "sqlite": "missing",
    }
    try:
        sqlite_write = _write_prototype_projection_sqlite(sqlite_payload)
        sink_checksums["sqlite"] = _stable_hash(sqlite_payload)
    except Exception as exc:  # noqa: BLE001
        sqlite_write = {"status": "failed", "error": str(exc), "db_path": str(_prototype_ledger_db_path())}

    manifest["transaction"] = {
        "source_hash": current_source_hash,
        "projection_seq": projection_seq,
        "transaction_id": transaction_id,
        "committed_at": committed_at,
        "sink_checksums": sink_checksums,
        "sqlite_write": sqlite_write,
    }
    manifest["drift_status"] = "consistent"
    manifest["sqlite_projection_status"] = "pass" if sink_checksums.get("sqlite") != "missing" else "fail"
    manifest["machine_contract_status"] = "pass"
    manifest["human_view_status"] = "pass"
    manifest["status"] = "draft"
    if str(review_payload.get("overall_status") or "") == "pass":
        manifest["review_status"] = "pass"
        manifest["design_review_outcome"] = str(review_payload.get("design_review_outcome") or "pass")
    else:
        manifest["review_status"] = "missing"
        manifest["design_review_outcome"] = "pass"

    _write_json(files["manifest"], manifest)

    if freeze_payload:
        freeze_payload = _copy_json_object(freeze_payload)
        freeze_payload["source_fingerprints"] = current_source_fingerprints
        freeze_payload["artifact_fingerprints"] = _artifact_fingerprints(files)
        freeze_payload["transaction"] = manifest["transaction"]
        freeze_payload["status"] = "draft"
        freeze_payload["review_status"] = manifest["review_status"]
        _write_json(files["freeze"], freeze_payload)

    return {
        "status": "reconciled",
        "feature": feature,
        "feature_slug": feature_slug,
        "version": version,
        "canonical_truth_source": str(canonical_truth.get("truth_source") or "prototype-plan"),
        "source_fingerprints": current_source_fingerprints,
        "transaction": manifest["transaction"],
        "sink_checksums": sink_checksums,
        "repair_path": "nondestructive-reconcile",
        "preserved_outputs": [
            "pages/*.md",
            "preview.html",
            "preview-dark.html",
        ],
        "root": files["root"],
    }


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
    prototype_source = legacy_prototype_source_path(project_root, version, feature)
    if prototype_source.exists() and prototype_source.is_file():
        text = prototype_source.read_text(encoding="utf-8")
        docs.append(
            {
                "type": "prototype-source",
                "path": prototype_source,
                "relative_path": str(prototype_source.relative_to(project_root)),
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


def _extract_list_field(docs: list[dict[str, Any]], field: str, default: list[str]) -> list[str]:
    raw = _extract_field(docs, field, "")
    if not raw:
        return list(default)
    normalized = raw.replace("|", ",").replace(";", ",")
    items = [item.strip(" -") for item in normalized.split(",") if item.strip(" -")]
    return items or list(default)


def _version_supports_ux_truth(version: str) -> bool:
    return _semver_tuple(version) >= (1, 3, 10)


def _supports_ux_truth(version: str, docs: list[dict[str, Any]]) -> bool:
    if _version_supports_ux_truth(version):
        return True
    explicit_flag = _extract_field(docs, "prototype_ux_prd_required", "false").lower() == "true"
    if explicit_flag:
        return True
    explicit_context_fields = [
        _extract_field(docs, "target_audience", ""),
        _extract_field(docs, "primary_use_cases", ""),
        _extract_field(docs, "operator_mental_state", ""),
        _extract_field(docs, "usage_environment", ""),
        _extract_field(docs, "brand_tone", ""),
        _extract_field(docs, "density_preference", ""),
    ]
    return any(bool(value.strip()) for value in explicit_context_fields)


def _explicit_page_label_from_line(line: str) -> str:
    stripped = str(line or "").strip()
    if not stripped:
        return ""
    if re.search(r"\b(?:AC|TC)-\d+\b", stripped, flags=re.IGNORECASE):
        return ""
    if re.match(r"^\s*[-*]\s+", stripped):
        return ""
    if re.match(r"^#{1,6}\s+", stripped):
        return ""
    candidate = _clean_page_label(stripped)
    if not candidate:
        return ""
    if _known_page_id_for_text(candidate):
        return candidate
    if not _looks_like_page_label(candidate):
        return ""
    return candidate


def _is_page_declaration_line(line: str) -> bool:
    return bool(PAGE_DECLARATION_HINT_PATTERN.search(str(line or "").strip()))


def _is_forbidden_page_context_line(line: str) -> bool:
    stripped = str(line or "").strip()
    return bool(FORBIDDEN_PAGE_CONTEXT_PATTERN.search(stripped))


def _doc_contains(doc: dict[str, Any], keyword: str) -> int:
    text = doc.get("text", "")
    idx = text.lower().find(keyword.lower())
    return idx


def _iter_doc_lines(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in docs:
        text = str(doc.get("text") or "")
        doc_type = str(doc.get("type") or "")
        offset = 0
        for line in text.splitlines():
            rows.append({"doc_type": doc_type, "line": line.rstrip(), "offset": offset})
            offset += len(line) + 1
    return rows


def _clean_page_label(raw: str) -> str:
    label = str(raw or "").strip().strip("`'\"")
    label = re.sub(r"^[\-*•>\d\.\)\s]+", "", label)
    label = re.sub(r"\s+", " ", label).strip()
    return label


def _looks_like_page_label(label: str) -> bool:
    cleaned = _clean_page_label(label)
    if len(cleaned) < 2:
        return False
    if len(cleaned) > 48:
        return False
    if re.search(r"[，。！？；;]", cleaned):
        return False
    lowered = cleaned.lower()
    if lowered in {"page", "pages", "screen", "screens", "route", "routes", "route map", "navigation", "navigation map"}:
        return False
    if re.match(r"^(?:us|fr|ac|tc)-\d+", lowered):
        return False
    if re.search(r"\b(?:ac|tc)-\d+\b", lowered):
        return False
    if re.search(r"\b(?:verify|assert|test)\b", lowered):
        return False
    if TRANSITION_HINT_PATTERN.search(cleaned):
        return False
    if re.match(r"^(?:as a|given|when|then|作为|当|如果|打开|查看|点击|页面必须|首页必须)\b", lowered):
        return False
    if len(cleaned.split()) > 8:
        return False
    if re.search(r"页面\s*(?:id|职责|交互|映射|信息|优先级|展示|收口|只读)", cleaned, flags=re.IGNORECASE):
        return False
    if any(token in cleaned for token in STOP_PAGE_TOKENS) or any(token in lowered for token in STOP_PAGE_TOKENS):
        return False
    return bool(PAGE_HINT_PATTERN.search(cleaned))


def _looks_like_declared_page_label(label: str) -> bool:
    cleaned = _clean_page_label(label)
    if len(cleaned) < 2:
        return False
    if len(cleaned) > 64:
        return False
    if re.search(r"[，。！？；;]", cleaned):
        return False
    lowered = cleaned.lower()
    if re.match(r"^(?:us|fr|ac|tc)-\d+", lowered):
        return False
    if re.search(r"\b(?:ac|tc)-\d+\b", lowered):
        return False
    if re.match(r"^(?:as a|given|when|then|作为|当|如果|打开|查看|点击|页面必须|首页必须)\b", lowered):
        return False
    if TRANSITION_HINT_PATTERN.search(cleaned):
        return False
    return True


def _known_page_id_for_text(text: str) -> str:
    lowered = str(text or "").lower()
    for page_id, meta in PAGE_CATALOG.items():
        for keyword in (page_id, *meta["keywords"]):
            keyword_str = str(keyword).strip().lower()
            if keyword_str and keyword_str == lowered:
                return page_id
    return ""


def _known_page_id_from_phrase(text: str) -> str:
    lowered = str(text or "").lower()
    for page_id, meta in PAGE_CATALOG.items():
        for keyword in (page_id, *meta["keywords"]):
            keyword_str = str(keyword).strip().lower()
            if keyword_str and keyword_str in lowered:
                return page_id
    return ""


def _slugify_page_id(label: str, *, ordinal: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", str(label or "").strip().lower()).strip("-")
    if base:
        return base
    digest = hashlib.sha1(str(label or "").encode("utf-8")).hexdigest()[:8]
    return f"page-{ordinal:02d}-{digest}"


def _extract_declared_page_labels(line: str) -> list[str]:
    stripped = str(line or "").strip()
    if not stripped:
        return []
    if re.search(r"\b(?:AC|TC)-\d+\b", stripped, flags=re.IGNORECASE):
        return []
    candidates: list[str] = []
    metadata_match = re.match(
        r"^(required_pages|primary_entry|primary_exit)\s*[:=]\s*(.+)$",
        stripped,
        flags=re.IGNORECASE,
    )
    if metadata_match:
        field_name = metadata_match.group(1).lower()
        raw_value = metadata_match.group(2).strip()
        if field_name == "required_pages":
            candidates.extend(part.strip() for part in raw_value.split(",") if part.strip())
        elif raw_value:
            candidates.append(raw_value)
    bullet = re.match(r"^(\s*)[-*]\s+(.+)$", str(line or ""))
    if bullet:
        indent = bullet.group(1)
        bullet_text = bullet.group(2).strip()
        if indent and len(indent) > 1:
            bullet_text = ""
        if re.search(r"(->|→|=>)", bullet_text):
            for part in re.split(r"(?:->|→|=>)", bullet_text):
                token = part.strip()
                if not token:
                    continue
                token = re.split(r"[:：]", token, maxsplit=1)[0].strip()
                if token:
                    candidates.append(token)
        elif re.search(r"\bto\b", bullet_text, flags=re.IGNORECASE):
            for part in re.split(r"\bto\b", bullet_text, flags=re.IGNORECASE):
                token = part.strip()
                if not token:
                    continue
                token = re.split(r"[:：]", token, maxsplit=1)[0].strip()
                if token:
                    candidates.append(token)
        else:
            candidates.append(bullet_text)
    else:
        explicit = re.search(
            r"(?:页面|page|screen|view|route)\s*[:：\-]\s*([^\|\n]{2,80})",
            stripped,
            flags=re.IGNORECASE,
        )
        if explicit:
            candidates.append(explicit.group(1))
    heading = re.match(r"^#{1,6}\s+(.+)$", stripped)
    if heading:
        candidates.append(heading.group(1))
    cleaned: list[str] = []
    for item in candidates:
        normalized = _clean_page_label(item)
        if _looks_like_declared_page_label(normalized):
            cleaned.append(normalized)
    return cleaned


def _collect_forbidden_page_ids(docs: list[dict[str, Any]]) -> set[str]:
    forbidden_ids: set[str] = set()
    in_forbidden_block = False
    for row in _iter_doc_lines(docs):
        line = str(row.get("line") or "")
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^#{1,6}\s+", stripped):
            in_forbidden_block = _is_forbidden_page_context_line(stripped)
            continue
        if _is_forbidden_page_context_line(stripped):
            in_forbidden_block = True
        if not in_forbidden_block:
            continue
        labels = _extract_declared_page_labels(stripped)
        explicit_label = _explicit_page_label_from_line(stripped)
        if explicit_label:
            labels.append(explicit_label)
        for label in labels:
            mapped_known_id = _known_page_id_from_phrase(label)
            if mapped_known_id:
                forbidden_ids.add(mapped_known_id)
    return forbidden_ids


def _default_custom_page_meta(page_id: str, label: str) -> dict[str, Any]:
    known = PAGE_CATALOG.get(page_id)
    if isinstance(known, dict):
        return dict(known)
    name = _clean_page_label(label) or page_id.replace("-", " ").title()
    return {
        "name": name,
        "keywords": (name, page_id),
        "priority": "P1",
        "platforms": ["Web", "PC"],
        "responsibility": f"定义{name}的页面结构、状态边界与动作收口。",
        "sections": [
            "当前状态",
            "当前阻塞",
            "下一步动作",
            "二级明细",
        ],
        "actions": [],
        "states": [
            {"id": "ready", "label": "可用", "description": "当前状态完整，可执行主要动作。"},
            {"id": "loading", "label": "加载中", "description": "当前信息仍在读取。"},
            {"id": "error", "label": "错误", "description": "当前状态读取失败，必须提示恢复动作。"},
        ],
    }


def _detect_pages_with_meta(docs: list[dict[str, Any]]) -> tuple[list[str], bool, dict[str, dict[str, Any]]]:
    rows = _iter_doc_lines(docs)
    discovered: list[tuple[int, str, str, bool]] = []
    page_meta: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    label_to_page: dict[str, str] = {}
    custom_index = 1
    forbidden_page_ids = _collect_forbidden_page_ids(docs)
    in_page_declaration_block = False
    in_forbidden_block = False

    for row in rows:
        line = str(row.get("line") or "")
        stripped = line.strip()
        if not stripped:
            continue
        offset = int(row.get("offset") or 0)
        if re.match(r"^#{1,6}\s+", stripped):
            in_page_declaration_block = _is_page_declaration_line(stripped)
            in_forbidden_block = _is_forbidden_page_context_line(stripped)
            continue
        if _is_forbidden_page_context_line(stripped):
            in_forbidden_block = True
            in_page_declaration_block = False
        elif _is_page_declaration_line(stripped):
            in_page_declaration_block = True
            in_forbidden_block = False

        if in_forbidden_block:
            continue

        explicit_label = _explicit_page_label_from_line(stripped)
        if explicit_label:
            known_id = _known_page_id_for_text(explicit_label)
            if known_id and known_id not in forbidden_page_ids and known_id not in seen:
                discovered.append((offset, known_id, PAGE_CATALOG[known_id]["name"], False))
                page_meta[known_id] = dict(PAGE_CATALOG[known_id])
                seen.add(known_id)

        labels = _extract_declared_page_labels(line) if in_page_declaration_block else []
        for label in labels:
            mapped_known_id = _known_page_id_for_text(label)
            if mapped_known_id:
                if mapped_known_id in forbidden_page_ids:
                    continue
                if mapped_known_id not in seen:
                    discovered.append((offset, mapped_known_id, PAGE_CATALOG[mapped_known_id]["name"], False))
                    page_meta[mapped_known_id] = dict(PAGE_CATALOG[mapped_known_id])
                    seen.add(mapped_known_id)
                label_to_page[_clean_page_label(label).lower()] = mapped_known_id
                continue

            label_key = _clean_page_label(label).lower()
            existing_page_id = label_to_page.get(label_key)
            if existing_page_id:
                continue

            base_page_id = _slugify_page_id(label, ordinal=custom_index)
            page_id = base_page_id
            duplicate_index = 2
            while page_id in seen:
                page_id = f"{base_page_id}-{duplicate_index:02d}"
                duplicate_index += 1
            custom_index += 1
            if page_id not in seen:
                discovered.append((offset, page_id, label, True))
                page_meta[page_id] = _default_custom_page_meta(page_id, label)
                seen.add(page_id)
                label_to_page[label_key] = page_id

    if not discovered:
        fallback_used = True
        ordered = list(PAGE_ORDER_DEFAULT)
        for page_id in ordered:
            page_meta[page_id] = dict(PAGE_CATALOG[page_id])
        return ordered, fallback_used, page_meta

    fallback_used = False
    filtered_discovered = [item for item in discovered if item[1] not in forbidden_page_ids]
    ordered_discovered = sorted(filtered_discovered, key=lambda item: item[0])
    page_ids = [page_id for _, page_id, _, _ in ordered_discovered]
    ordered_known = [page_id for page_id in PAGE_ORDER_DEFAULT if page_id in page_ids]
    ordered_custom = [page_id for page_id in page_ids if page_id not in ordered_known]
    ordered = ordered_known + ordered_custom
    if "material-viewer" in ordered and "material-document-detail" not in ordered:
        ordered.append("material-document-detail")
        page_meta["material-document-detail"] = dict(PAGE_CATALOG["material-document-detail"])
    page_meta = _overlay_explicit_page_meta(docs, page_meta)
    return ordered, fallback_used, page_meta


def _detect_page_ids(docs: list[dict[str, Any]]) -> tuple[list[str], bool]:
    page_ids, fallback_used, _ = _detect_pages_with_meta(docs)
    return page_ids, fallback_used


def _resolve_page_name(page_id: str, page_meta: dict[str, dict[str, Any]]) -> str:
    meta = page_meta.get(page_id) or PAGE_CATALOG.get(page_id) or {}
    name = str(meta.get("name") or "").strip()
    return name or page_id


def _resolve_page_id_from_label(label: str, page_meta: dict[str, dict[str, Any]]) -> str:
    normalized = _clean_page_label(label).lower()
    if not normalized:
        return ""
    for page_id, meta in page_meta.items():
        tokens = [page_id, str(meta.get("name") or "")]
        tokens.extend(str(keyword) for keyword in (meta.get("keywords") or []) if str(keyword).strip())
        for token in tokens:
            if _clean_page_label(token).lower() == normalized:
                return page_id
    return ""


def _parse_action_specs(raw: str, page_meta: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    normalized = str(raw or "").replace("|", ";")
    for chunk in [item.strip() for item in normalized.split(";") if item.strip()]:
        if "->" in chunk:
            label_raw, target_raw = chunk.split("->", 1)
        elif "→" in chunk:
            label_raw, target_raw = chunk.split("→", 1)
        else:
            continue
        label = _clean_page_label(label_raw)
        target_label = _clean_page_label(target_raw)
        target = _resolve_page_id_from_label(target_label, page_meta)
        if label and target:
            specs.append({"label": label, "target": target, "trigger": f"点击{label}"})
    return specs[:8]


def _humanize_state_label(state_id: str) -> str:
    text = str(state_id or "").strip().replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "State"
    return " ".join(part[:1].upper() + part[1:] for part in text.split(" "))


def _parse_reference_values(raw: str, *, pattern: re.Pattern[str] | None = None) -> list[str]:
    text = str(raw or "").strip()
    if not text:
        return []
    if pattern is not None:
        matches = [match.upper() for match in pattern.findall(text)]
        if matches:
            seen: set[str] = set()
            ordered: list[str] = []
            for match in matches:
                if match in seen:
                    continue
                seen.add(match)
                ordered.append(match)
            return ordered[:8]
    chunks = re.split(r"[,\s;/]+", text)
    seen: set[str] = set()
    normalized: list[str] = []
    for chunk in chunks:
        ref = chunk.strip().upper()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        normalized.append(ref)
    return normalized[:8]


def _parse_state_specs(raw: str) -> list[dict[str, str]]:
    normalized_raw = re.sub(r"^[-*]\s+", "", str(raw or "").strip())
    if not normalized_raw:
        return []
    chunks = [item.strip() for item in normalized_raw.split(";") if item.strip()]
    if not chunks:
        chunks = [normalized_raw]
    states: list[dict[str, str]] = []
    for chunk in chunks[:8]:
        parts = [part.strip() for part in chunk.split("|")]
        extras = parts[3:] if len(parts) >= 4 else []
        if len(parts) >= 3:
            state_id, label, description = parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            state_id, description = parts[0], parts[1]
            label = _humanize_state_label(state_id)
        else:
            state_id = parts[0]
            label = _humanize_state_label(state_id)
            description = f"{label} state should provide explicit business feedback."
        state_slug = slugify_feature(state_id).replace("prototype-feature", "state")
        if not state_slug:
            continue
        state_payload: dict[str, Any] = {
            "id": state_slug,
            "label": label or _humanize_state_label(state_slug),
            "description": description.strip() or f"{label or state_slug} state should provide explicit business feedback.",
        }
        for extra in extras:
            lowered = extra.lower()
            if lowered.startswith("ac_refs="):
                state_payload["ac_refs"] = _parse_reference_values(extra.split("=", 1)[1], pattern=AC_PATTERN)
            elif lowered.startswith("tc_refs="):
                state_payload["tc_refs"] = _parse_reference_values(extra.split("=", 1)[1], pattern=TC_PATTERN)
        states.append(state_payload)
    return states[:8]


def _overlay_explicit_page_meta(docs: list[dict[str, Any]], page_meta: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = _iter_doc_lines(docs)
    current_page_id = ""
    in_actions_block = False
    in_states_block = False
    for row in rows:
        stripped = str(row.get("line") or "").strip()
        if not stripped:
            continue
        heading = re.match(r"^#{3,6}\s+(.+)$", stripped)
        if heading:
            current_page_id = _resolve_page_id_from_label(heading.group(1), page_meta)
            in_actions_block = False
            in_states_block = False
            continue
        if not current_page_id:
            continue
        meta = page_meta.get(current_page_id)
        if not isinstance(meta, dict):
            continue
        normalized = re.sub(r"^[-*]\s+", "", stripped)
        lower = normalized.lower()
        if lower.startswith("responsibility:"):
            meta["responsibility"] = normalized.split(":", 1)[1].strip()
            continue
        if lower.startswith("decision_supported:"):
            meta["decision_supported"] = normalized.split(":", 1)[1].strip()
            continue
        if lower.startswith("sections:"):
            raw_sections = normalized.split(":", 1)[1].strip().replace("|", ",")
            meta["sections"] = [item.strip() for item in raw_sections.split(",") if item.strip()][:6]
            continue
        if lower.startswith("priority:"):
            meta["priority"] = normalized.split(":", 1)[1].strip() or meta.get("priority", "P1")
            continue
        if lower.startswith("platforms:"):
            raw_platforms = normalized.split(":", 1)[1].strip().replace("|", ",").replace("/", ",")
            meta["platforms"] = [item.strip() for item in raw_platforms.split(",") if item.strip()][:4]
            continue
        if lower.startswith("actions:"):
            parsed = _parse_action_specs(normalized.split(":", 1)[1].strip(), page_meta)
            if parsed:
                meta["actions"] = parsed
            in_actions_block = True
            in_states_block = False
            continue
        if lower.startswith("states:"):
            parsed = _parse_state_specs(normalized.split(":", 1)[1].strip())
            if parsed:
                meta["states"] = parsed
            in_actions_block = False
            in_states_block = True
            continue
        if in_actions_block and re.match(r"^[-*]\s+", stripped):
            parsed = _parse_action_specs(normalized, page_meta)
            if parsed:
                meta["actions"] = list(meta.get("actions") or []) + parsed
                continue
        if in_states_block and re.match(r"^[-*]\s+", stripped):
            parsed = _parse_state_specs(normalized)
            if parsed:
                meta["states"] = list(meta.get("states") or []) + parsed
                continue
        in_actions_block = False
        in_states_block = False
    return page_meta


def _line_page_mentions(line: str, page_ids: list[str], page_meta: dict[str, dict[str, Any]]) -> list[str]:
    lowered = str(line or "").lower()
    matched: list[str] = []
    for page_id in page_ids:
        meta = page_meta.get(page_id) or PAGE_CATALOG.get(page_id) or {}
        tokens = [page_id, str(meta.get("name") or "")]
        tokens.extend(str(keyword) for keyword in (meta.get("keywords") or []) if str(keyword).strip())
        for token in tokens:
            tk = str(token).strip().lower()
            if tk and tk in lowered:
                matched.append(page_id)
                break
    return matched


def _build_transition_inventory(page_ids: list[str], docs: list[dict[str, Any]], page_meta: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = set(page_ids)
    static_candidates = [item for item in TRANSITION_LIBRARY if item["from"] in allowed and item["to"] in allowed]
    dynamic_candidates: list[dict[str, Any]] = []

    for row in _iter_doc_lines(docs):
        line = str(row.get("line") or "")
        if not TRANSITION_HINT_PATTERN.search(line):
            continue
        mentions = _line_page_mentions(line, page_ids, page_meta)
        if len(mentions) < 2:
            continue
        source = mentions[0]
        target = mentions[1]
        transition_type = "return" if "返回" in line else "primary"
        trigger = "点击返回" if transition_type == "return" else "点击跳转"
        dynamic_candidates.append(
            {
                "from": source,
                "to": target,
                "trigger": trigger,
                "type": transition_type,
            }
        )

    transitions = list(static_candidates)
    static_pairs = {(item["from"], item["to"]) for item in static_candidates}
    for item in dynamic_candidates:
        pair = (str(item.get("from") or "").strip(), str(item.get("to") or "").strip())
        if not pair[0] or not pair[1] or pair in static_pairs:
            continue
        transitions.append(item)
    if not transitions and len(page_ids) > 1:
        for idx in range(len(page_ids) - 1):
            source = page_ids[idx]
            target = page_ids[idx + 1]
            transitions.append(
                {
                    "from": source,
                    "to": target,
                    "trigger": f"进入{_resolve_page_name(target, page_meta)}",
                    "type": "primary",
                }
            )

    if "material-viewer" in allowed and "material-document-detail" in allowed:
        required_pairs = {
            ("material-viewer", "material-document-detail", "drill-down", "点击文档列表项"),
            ("material-document-detail", "material-viewer", "return", "点击返回"),
        }
        existing_pairs = {(item["from"], item["to"]) for item in transitions}
        for source, target, tp, trigger in required_pairs:
            if (source, target) not in existing_pairs:
                transitions.append({"from": source, "to": target, "type": tp, "trigger": trigger})

    deduped: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    for item in transitions:
        source = str(item.get("from") or "").strip()
        target = str(item.get("to") or "").strip()
        trigger = str(item.get("trigger") or "").strip() or "点击跳转"
        tp = str(item.get("type") or "").strip() or "primary"
        if not source or not target or source not in allowed or target not in allowed:
            continue
        key = (source, target, tp)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append({"from": source, "to": target, "trigger": trigger, "type": tp})
    return deduped


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


def _build_page_specs(
    page_ids: list[str],
    docs: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    page_meta: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    refs = _build_requirement_refs(docs)
    outbound: dict[str, list[dict[str, Any]]] = {}
    for transition in transitions:
        outbound.setdefault(transition["from"], []).append(transition)

    page_specs: list[dict[str, Any]] = []
    for page_id in page_ids:
        meta = page_meta.get(page_id) or PAGE_CATALOG.get(page_id) or _default_custom_page_meta(page_id, page_id)
        actions = list(meta.get("actions") or [])
        filtered_actions = [action for action in actions if str(action.get("target") or "") in set(page_ids)]
        if not filtered_actions:
            filtered_actions = [
                {
                    "label": f"进入{_resolve_page_name(transition['to'], page_meta)}",
                    "target": transition["to"],
                    "trigger": transition["trigger"],
                }
                for transition in outbound.get(page_id, [])
            ]
        page_specs.append(
            {
                "page_id": page_id,
                "name": meta["name"],
                "priority": meta.get("priority", "P1"),
                "platforms": list(meta.get("platforms") or ["Web", "PC"]),
                "responsibility": meta.get(
                    "responsibility", f"冻结 `{meta.get('name', page_id)}` 的页面结构、动作和状态说明。"
                ),
                "decision_supported": str(meta.get("decision_supported") or "").strip(),
                "sections": list(meta.get("sections") or ["页面头部", "关键内容区", "主要操作区", "状态与反馈区"]),
                "actions": filtered_actions,
                "states": [
                    {
                        **state,
                    }
                    for state in list(
                    meta.get("states")
                    or [
                        {"id": "ready", "label": "可用", "description": "页面数据齐备，用户可完成核心操作。"},
                        {"id": "loading", "label": "加载中", "description": "页面数据正在加载。"},
                        {"id": "error", "label": "错误", "description": "页面加载或提交失败，需提示恢复动作。"},
                    ]
                    )
                ],
                "requirement_refs": refs,
                "outbound_transitions": outbound.get(page_id, []),
            }
        )
        page_specs[-1]["analysis"] = PAGE_ANALYSIS_CATALOG.get(page_id, _default_page_analysis(page_specs[-1]))
        page_specs[-1]["visible_contract"] = _build_visible_contract(page_specs[-1])
        page_specs[-1]["internal_governance"] = _build_internal_governance(page_specs[-1])
        page_specs[-1]["ui_copy_projection_contract"] = _build_ui_copy_projection_contract(page_specs[-1])
        for state in page_specs[-1]["states"]:
            state["state_visibility_contract"] = _build_state_visibility_contract(page_specs[-1], state)
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
        states = [state for state in page.get("states", []) if isinstance(state, dict)]
        for index, section in enumerate(page.get("sections", []), start=1):
            component_id = f"{page_id}-component-{index:02d}"
            action = actions[index - 1] if index - 1 < len(actions) else None
            state_feedback_responsibilities = []
            component_ac_refs: list[str] = []
            component_tc_refs: list[str] = []
            for state in states[:6]:
                state_id = str(state.get("id") or "").strip()
                if not state_id:
                    continue
                state_ac_refs = [str(item).strip().upper() for item in (state.get("ac_refs") or []) if str(item).strip()]
                state_tc_refs = [str(item).strip().upper() for item in (state.get("tc_refs") or []) if str(item).strip()]
                if state_id in {"ready", "success", "document-open", "frozen"}:
                    feedback = f"{section} must preserve primary content hierarchy and next-step clarity."
                elif state_id in {"loading"}:
                    feedback = f"{section} must keep visible loading feedback without collapsing layout."
                elif state_id in {"error", "blocked", "stale", "source-missing"}:
                    feedback = f"{section} must show recovery guidance and explicit fallback action."
                elif state_id in {"empty", "idle"}:
                    feedback = f"{section} must explain why content is empty and where to continue."
                else:
                    feedback = str(state.get("description") or "").strip() or f"{section} must reflect `{state_id}` business state."
                state_feedback_responsibilities.append(
                    {
                        "state_id": state_id,
                        "feedback": feedback,
                        "ac_refs": state_ac_refs,
                        "tc_refs": state_tc_refs,
                    }
                )
                component_ac_refs.extend(state_ac_refs)
                component_tc_refs.extend(state_tc_refs)
            if not component_ac_refs:
                component_ac_refs = list(ac_ids)
            if not component_tc_refs:
                component_tc_refs = list(tc_ids)
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
                    "state_feedback_responsibilities": state_feedback_responsibilities,
                    "ac_refs": _parse_reference_values(component_ac_refs, pattern=AC_PATTERN),
                    "tc_refs": _parse_reference_values(component_tc_refs, pattern=TC_PATTERN),
                    "interaction_responsibilities": [
                        {
                            "label": str(action.get("label") or "").strip(),
                            "trigger": str(action.get("trigger") or "").strip(),
                            "target": str(action.get("target") or "").strip(),
                        }
                    ]
                    if isinstance(action, dict)
                    else [],
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
        "| Component ID | Page | Name | State Refs | Feedback Responsibilities | AC Refs | TC Refs |",
        "|---|---|---|---|---|---|---|",
    ]
    for component in payload.get("components", []):
        feedback_summary = ", ".join(
            f"{item.get('state_id')}:{str(item.get('feedback') or '').strip()[:24]}"
            for item in (component.get("state_feedback_responsibilities") or [])[:3]
            if isinstance(item, dict)
        )
        lines.append(
            "| `{}` | `{}` | {} | {} | {} | {} | {} |".format(
                component.get("component_id", ""),
                component.get("page_id", ""),
                component.get("name", ""),
                ", ".join(component.get("state_refs", [])[:6]) or "-",
                feedback_summary or "-",
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
    state_index: dict[tuple[str, str], dict[str, Any]] = {}
    tc_ids = list(requirement_ids.get("tc_ids") or [])
    for page in page_specs:
        page_id = str(page.get("page_id") or "")
        states = [state for state in page.get("states", []) if isinstance(state, dict)]
        state_ids = [str(state.get("id") or "").strip() for state in states if str(state.get("id") or "").strip()]
        for state in states:
            state_id = str(state.get("id") or "").strip()
            if not state_id:
                continue
            state_index[(page_id, state_id)] = state
            node_key = f"{page_id}:{state_id}"
            nodes.append(
                {
                    "state_key": node_key,
                    "page_id": page_id,
                    "state_id": state_id,
                    "label": str(state.get("label") or state_id),
                    "description": str(state.get("description") or ""),
                    "ac_refs": [str(item).strip().upper() for item in (state.get("ac_refs") or []) if str(item).strip()],
                    "tc_refs": [str(item).strip().upper() for item in (state.get("tc_refs") or []) if str(item).strip()],
                }
            )
        if "loading" in state_ids and "ready" in state_ids:
            ready_state = state_index.get((page_id, "ready"), {})
            edges.append(
                {
                    "from": f"{page_id}:loading",
                    "to": f"{page_id}:ready",
                    "event": "data_loaded",
                    "guard": "data_fetch_success",
                    "kind": "intra-page",
                    "fallback": None,
                    "ac_refs": [str(item).strip().upper() for item in (ready_state.get("ac_refs") or []) if str(item).strip()],
                    "test_refs": [str(item).strip().upper() for item in (ready_state.get("tc_refs") or []) if str(item).strip()] or tc_ids[:2],
                }
            )
        if "ready" in state_ids and "error" in state_ids:
            fallback_page = "recovery-diagnostics" if page_id != "recovery-diagnostics" else page_id
            error_state = state_index.get((page_id, "error"), {})
            edges.append(
                {
                    "from": f"{page_id}:ready",
                    "to": f"{page_id}:error",
                    "event": "data_failure",
                    "guard": "runtime_or_projection_error",
                    "kind": "intra-page",
                    "fallback": f"{fallback_page}:ready",
                    "ac_refs": [str(item).strip().upper() for item in (error_state.get("ac_refs") or []) if str(item).strip()],
                    "test_refs": [str(item).strip().upper() for item in (error_state.get("tc_refs") or []) if str(item).strip()] or tc_ids[:2],
                }
            )
        meaningful_states = [state for state in states if str(state.get("id") or "").strip() not in {"ready", "loading", "error"}]
        for state in meaningful_states[:8]:
            state_id = str(state.get("id") or "").strip()
            if not state_id:
                continue
            edges.append(
                {
                    "from": f"{page_id}:ready",
                    "to": f"{page_id}:{state_id}",
                    "event": f"enter_{state_id.replace('-', '_')}",
                    "guard": "business_condition_detected",
                    "kind": "intra-page-business",
                    "fallback": f"{page_id}:ready",
                    "ac_refs": [str(item).strip().upper() for item in (state.get("ac_refs") or []) if str(item).strip()],
                    "test_refs": [str(item).strip().upper() for item in (state.get("tc_refs") or []) if str(item).strip()],
                }
            )
    for transition in transitions:
        source_page = str(transition.get("from") or "")
        target_page = str(transition.get("to") or "")
        if not source_page or not target_page:
            continue
        target_ready_state = state_index.get((target_page, "ready"), {})
        edges.append(
            {
                "from": f"{source_page}:ready",
                "to": f"{target_page}:ready",
                "from_page": source_page,
                "from_state": "ready",
                "to_page": target_page,
                "to_state": "ready",
                "event": str(transition.get("trigger") or "navigate"),
                "guard": "route_allowed",
                "kind": "cross-page-transition",
                "fallback": f"{source_page}:ready",
                "route_or_runtime_evidence": [
                    f"navigation-map:{source_page}->{target_page}",
                    f"implementation:{target_page}",
                ],
                "ac_refs": [str(item).strip().upper() for item in (target_ready_state.get("ac_refs") or []) if str(item).strip()] or list(requirement_ids.get("ac_ids") or [])[:1],
                "test_refs": [str(item).strip().upper() for item in (target_ready_state.get("tc_refs") or []) if str(item).strip()] or tc_ids[:1],
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
        "| From | To | Event | Guard | Fallback | AC Refs | TC Refs |",
        "|---|---|---|---|---|---|---|",
    ]
    for edge in payload.get("edges", []):
        lines.append(
            "| `{}` | `{}` | {} | {} | {} | {} | {} |".format(
                edge.get("from", ""),
                edge.get("to", ""),
                edge.get("event", ""),
                edge.get("guard", ""),
                edge.get("fallback", "-") or "-",
                ", ".join(edge.get("ac_refs", [])[:4]) or "-",
                ", ".join(edge.get("test_refs", [])[:4]) or "-",
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


def _build_automation_priority_matrix(
    page_specs: list[dict[str, Any]],
    state_flow_map: dict[str, Any],
    component_catalog: dict[str, Any],
    design_reasoning: dict[str, Any],
) -> dict[str, Any]:
    page_by_id = {
        str(page.get("page_id") or "").strip(): page
        for page in page_specs
        if isinstance(page, dict) and str(page.get("page_id") or "").strip()
    }
    entries: list[dict[str, Any]] = []

    def _priority_class(page_priority: str, *, has_meaningful_refs: bool, target_type: str, state_id: str = "") -> str:
        normalized = str(page_priority or "P1").strip().upper()
        if normalized == "P0" and has_meaningful_refs:
            return "release-blocker" if target_type in {"transition", "state"} or state_id not in {"ready", ""} else "primary-automation"
        if has_meaningful_refs:
            return "primary-automation"
        if target_type in {"page", "component"}:
            return "smoke-only"
        return "manual-acceptable"

    for page in page_specs:
        if not isinstance(page, dict):
            continue
        page_id = str(page.get("page_id") or "").strip()
        page_priority = str(page.get("priority") or "P1").strip().upper()
        for state in page.get("states", []):
            if not isinstance(state, dict):
                continue
            state_id = str(state.get("id") or "").strip()
            if not state_id:
                continue
            ac_refs = [str(item).strip().upper() for item in (state.get("ac_refs") or []) if str(item).strip()]
            tc_refs = [str(item).strip().upper() for item in (state.get("tc_refs") or []) if str(item).strip()]
            entries.append(
                {
                    "target_id": f"{page_id}:{state_id}",
                    "target_type": "state",
                    "priority_class": _priority_class(page_priority, has_meaningful_refs=bool(ac_refs or tc_refs), target_type="state", state_id=state_id),
                    "reason": str(state.get("description") or "").strip() or "State visibility must stay verifiable.",
                    "product_surface_type": str(design_reasoning.get("product_surface_type") or ""),
                    "page_priority": page_priority,
                    "ac_refs": ac_refs,
                    "tc_refs": tc_refs,
                }
            )

    for edge in (state_flow_map.get("edges") or []):
        if not isinstance(edge, dict):
            continue
        if str(edge.get("kind") or "") != "cross-page-transition":
            continue
        to_page = str(edge.get("to_page") or "").strip() or str(edge.get("to", "")).split(":")[0]
        page_priority = str((page_by_id.get(to_page) or {}).get("priority") or "P1").strip().upper()
        ac_refs = [str(item).strip().upper() for item in (edge.get("ac_refs") or []) if str(item).strip()]
        tc_refs = [str(item).strip().upper() for item in (edge.get("test_refs") or []) if str(item).strip()]
        entries.append(
            {
                "target_id": f"{edge.get('from')}->{edge.get('to')}",
                "target_type": "transition",
                "priority_class": _priority_class(page_priority, has_meaningful_refs=bool(ac_refs or tc_refs), target_type="transition"),
                "reason": f"{edge.get('event', 'navigate')} transition must preserve guard, fallback, and evidence binding.",
                "product_surface_type": str(design_reasoning.get("product_surface_type") or ""),
                "page_priority": page_priority,
                "ac_refs": ac_refs,
                "tc_refs": tc_refs,
            }
        )

    for component in (component_catalog.get("components") or []):
        if not isinstance(component, dict):
            continue
        page_priority = str((page_by_id.get(str(component.get("page_id") or "").strip()) or {}).get("priority") or "P1").strip().upper()
        ac_refs = [str(item).strip().upper() for item in (component.get("ac_refs") or []) if str(item).strip()]
        tc_refs = [str(item).strip().upper() for item in (component.get("tc_refs") or []) if str(item).strip()]
        entries.append(
            {
                "target_id": str(component.get("component_id") or ""),
                "target_type": "component",
                "priority_class": _priority_class(page_priority, has_meaningful_refs=bool(ac_refs or tc_refs), target_type="component"),
                "reason": f"{component.get('name', 'Component')} owns visible state feedback and interaction continuity.",
                "product_surface_type": str(design_reasoning.get("product_surface_type") or ""),
                "page_priority": page_priority,
                "ac_refs": ac_refs,
                "tc_refs": tc_refs,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "entry_count": len(entries),
        "entries": entries,
    }


def _render_automation_priority_matrix_md(feature: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# 自动化优先级矩阵：{feature}",
        "",
        "| Target ID | Target Type | Priority Class | Reason | AC Refs | TC Refs |",
        "|---|---|---|---|---|---|",
    ]
    for item in payload.get("entries", []):
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | {} |".format(
                item.get("target_id", ""),
                item.get("target_type", ""),
                item.get("priority_class", ""),
                item.get("reason", ""),
                ", ".join(item.get("ac_refs", [])[:4]) or "-",
                ", ".join(item.get("tc_refs", [])[:4]) or "-",
            )
        )
    return "\n".join(lines)


def _build_route_closure_contract(page_specs: list[dict[str, Any]], transitions: list[dict[str, Any]], route_closure_required: bool) -> dict[str, Any]:
    name_by_page = {str(page.get("page_id") or ""): str(page.get("name") or page.get("page_id") or "") for page in page_specs}
    closure_cases = []
    for index, transition in enumerate(transitions, start=1):
        source = str(transition.get("from") or "")
        target = str(transition.get("to") or "")
        closure_cases.append(
            {
                "case_id": f"RC-{index:03d}",
                "source_page_id": source,
                "source_label": name_by_page.get(source, source),
                "target_surface_id": target,
                "target_label": name_by_page.get(target, target),
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
    primary = _extract_field(docs, "theme_primary", "#0071E3")
    secondary = _extract_field(docs, "theme_secondary", "#F5F5F7")
    archetype = _extract_field(docs, "prototype_archetype", DEFAULT_PROTOTYPE_ARCHETYPE)
    design_preset = _extract_field(docs, "design_preset", "apple-inspired-design-md")
    product_surface_type = _extract_field(docs, "product_surface_type", "")
    override_reason = _extract_field(docs, "design_preset_override_reason", "")
    return {
        "ui_kit": PROTOTYPE_UI_KIT,
        "design_preset": design_preset,
        "product_surface_type": product_surface_type,
        "design_preset_override_reason": override_reason,
        "design_preset_overridden": bool(override_reason) or design_preset != "apple-inspired-design-md",
        "prototype_archetype": archetype,
        "primary": primary,
        "secondary": secondary,
        "surface_note": "Wireframe freeze uses Apple-inspired quiet neutrals and restrained accent metadata, not high-fidelity HTML surfaces.",
    }


def _build_design_context(
    docs: list[dict[str, Any]],
    page_specs: list[dict[str, Any]],
    theme: dict[str, Any],
) -> dict[str, Any]:
    explicit_target_audience = _extract_field(docs, "target_audience", "")
    explicit_use_cases = _extract_list_field(docs, "primary_use_cases", [])
    explicit_operator_state = _extract_field(docs, "operator_mental_state", "")
    explicit_usage_environment = _extract_field(docs, "usage_environment", "")
    explicit_brand_tone = _extract_list_field(docs, "brand_tone", [])
    explicit_density_preference = _extract_field(docs, "density_preference", "")

    target_audience = explicit_target_audience or "Beacon 管理者 / 需求 owner / 实现协作者"
    use_cases = explicit_use_cases or [
        "快速理解页面先服务哪一个判断",
        "冻结页面下钻路径与状态反馈",
        "为 implement / qa 提供统一的 UX truth",
    ]
    operator_state = explicit_operator_state or "需要在有限时间内完成判断与推进，而不是阅读泛化说明。"
    usage_environment = explicit_usage_environment or "桌面优先的管理工作台与需求协作评审环境。"
    brand_tone = explicit_brand_tone or ["quiet", "precise", "operational", "content-first"]
    density_preference = explicit_density_preference or "workbench-medium"
    explicit_fields: list[str] = []
    if explicit_target_audience:
        explicit_fields.append("target_audience")
    if explicit_use_cases:
        explicit_fields.append("primary_use_cases")
    if explicit_operator_state:
        explicit_fields.append("operator_mental_state")
    if explicit_usage_environment:
        explicit_fields.append("usage_environment")
    if explicit_brand_tone:
        explicit_fields.append("brand_tone")
    if explicit_density_preference:
        explicit_fields.append("density_preference")
    return {
        "target_audience": target_audience,
        "primary_use_cases": use_cases,
        "operator_mental_state": operator_state,
        "usage_environment": usage_environment,
        "brand_tone": brand_tone,
        "density_preference": density_preference,
        "design_preset": str(theme.get("design_preset") or "apple-inspired-design-md"),
        "design_preset_override_reason": str(theme.get("design_preset_override_reason") or ""),
        "explicit_context_fields": explicit_fields,
        "explicit_context_complete": len(explicit_fields) == 6,
        "page_count": len(page_specs),
    }


def _build_software_semantic_profile(semantic_layer: dict[str, Any], page_specs: list[dict[str, Any]]) -> dict[str, Any]:
    official = dict(semantic_layer.get("official_language", {})) if isinstance(semantic_layer, dict) else {}
    return {
        "tone": "formal-restrained-precise",
        "title_rule": "标题仅陈述对象或状态，不解释设计意图。",
        "state_rule": "状态文案必须先说明当前状态，再说明允许动作或禁止动作。",
        "action_rule": "动作名称必须使用可执行动词，不使用泛化 SaaS 词汇。",
        "field_rule": "字段与输入说明必须显式约束类型、非空、枚举或默认值。",
        "exception_rule": "异常文案必须同时给出当前失败与恢复路径。",
        "banned_terms": list(official.get("banned_terms") or []),
        "preferred_terms": list(official.get("preferred_terms") or []),
        "production_banned_copy": [
            "当前状态",
            "下一步动作",
            "恢复路径",
            "design asset catalog",
            "review guidance",
            "why/reasoning",
            "transaction_id",
            "projection_seq",
        ],
        "page_count": len(page_specs),
    }


def _build_ui_copy_projection_contract(page: dict[str, Any]) -> dict[str, Any]:
    visible_contract = page.get("visible_contract") if isinstance(page.get("visible_contract"), dict) else {}
    actions = [str(action.get("label") or "").strip() for action in (page.get("actions") or []) if isinstance(action, dict) and str(action.get("label") or "").strip()]
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "first_screen_copy": {
            "title": str(visible_contract.get("title") or page.get("name") or page.get("page_id") or "").strip(),
            "primary_statement": str(visible_contract.get("subtitle") or page.get("responsibility") or "").strip(),
            "must_show_first": list(visible_contract.get("must_show_sections") or [])[:2],
            "next_actions": actions[:3],
        },
        "secondary_disclosure": [
            "workspace path",
            "artifact path",
            "history timeline",
            "machine trace detail",
        ],
        "forbidden_first_screen_copy": [
            "design asset catalog wording",
            "why/reasoning explanation",
            "review guidance",
            "machine contract detail",
        ],
    }


def _build_surface_profile(page: dict[str, Any], design_reasoning: dict[str, Any]) -> dict[str, Any]:
    actions = [item for item in (page.get("actions") or []) if isinstance(item, dict)]
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "surface_type": str(design_reasoning.get("product_surface_type") or "workbench").strip(),
        "layout_pattern": str(design_reasoning.get("recommended_layout_pattern") or "").strip(),
        "primary_object": str(page.get("name") or page.get("page_id") or "").strip(),
        "primary_responsibility": str(page.get("responsibility") or "").strip(),
        "density": "workbench-medium",
        "action_count": len(actions),
    }


def _build_layout_pattern_artifact(page: dict[str, Any], design_reasoning: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "pattern": str(design_reasoning.get("recommended_layout_pattern") or "").strip(),
        "sections": [str(item).strip() for item in (page.get("sections") or []) if str(item).strip()],
        "layout_rules": list((page.get("analysis") or {}).get("layout_rules") or []),
    }


def _build_component_priority_map(page: dict[str, Any]) -> dict[str, Any]:
    sections = [str(item).strip() for item in (page.get("sections") or []) if str(item).strip()]
    entries: list[dict[str, Any]] = []
    for index, section in enumerate(sections, start=1):
        entries.append(
            {
                "component": section,
                "priority": index,
                "display_zone": _position_label(index - 1, len(sections)),
            }
        )
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "entries": entries,
    }


def _sanitize_production_copy(text: str) -> str:
    value = str(text or "").strip()
    if "\n" in value:
        return "\n".join(_sanitize_production_copy(line) if line.strip() else "" for line in value.splitlines())
    replacements = {
        "当前状态": "状态摘要",
        "下一步动作": "主动作",
        "恢复路径": "恢复入口",
        "why/reasoning": "",
        "review guidance": "",
        "design asset catalog": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"\s+", " ", value).strip(" -:：")
    return value


def _build_production_ui_copy_profile(page: dict[str, Any]) -> dict[str, Any]:
    visible_contract = page.get("visible_contract") if isinstance(page.get("visible_contract"), dict) else {}
    actions = [str(item.get("label") or "").strip() for item in (page.get("actions") or []) if isinstance(item, dict)]
    primary_actions = [_sanitize_production_copy(item) for item in actions[:3] if _sanitize_production_copy(item)]
    if not primary_actions:
        primary_actions = ["查看主体内容"]
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "title": _sanitize_production_copy(str(visible_contract.get("title") or page.get("name") or page.get("page_id") or "").strip()),
        "subtitle": _sanitize_production_copy(str(visible_contract.get("subtitle") or page.get("responsibility") or "").strip()),
        "primary_actions": primary_actions,
        "allowed_recovery_surface_states": ["blocked", "failed", "empty-risk"],
        "forbidden_first_screen_terms": [
            "当前状态",
            "下一步动作",
            "恢复路径",
            "design asset catalog",
            "review guidance",
            "why/reasoning",
        ],
    }


def _build_design_lint_rules(semantic_profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "banned_terms": list(semantic_profile.get("banned_terms") or []),
        "production_banned_copy": list(semantic_profile.get("production_banned_copy") or []),
        "title_rule": str(semantic_profile.get("title_rule") or "").strip(),
        "state_rule": str(semantic_profile.get("state_rule") or "").strip(),
        "action_rule": str(semantic_profile.get("action_rule") or "").strip(),
        "exception_rule": str(semantic_profile.get("exception_rule") or "").strip(),
    }


def _build_design_artifacts(plan: dict[str, Any]) -> dict[str, Any]:
    design_context = plan.get("design_context") if isinstance(plan.get("design_context"), dict) else {}
    design_reasoning = plan.get("design_reasoning") if isinstance(plan.get("design_reasoning"), dict) else {}
    semantic_profile = plan.get("software_semantic_profile") if isinstance(plan.get("software_semantic_profile"), dict) else {}
    page_specs = [item for item in (plan.get("page_specs") or []) if isinstance(item, dict)]
    generated_at = str(plan.get("generated_at") or now_iso())
    source_refs = [str(item.get("path") or "").strip() for item in (plan.get("source_documents") or []) if isinstance(item, dict)]
    source_hash = _stable_hash(source_refs + [generated_at, str(plan.get("feature_slug") or "")])
    return {
        "design-context.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "internal-governance-copy",
            "payload": design_context,
        },
        "surface-profile.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "design-intelligence",
            "pages": [_build_surface_profile(page, design_reasoning) for page in page_specs],
        },
        "layout-pattern.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "design-intelligence",
            "pages": [_build_layout_pattern_artifact(page, design_reasoning) for page in page_specs],
        },
        "component-state-matrix.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "design-intelligence",
            "pages": [
                {
                    "page_id": str(page.get("page_id") or "").strip(),
                    "components": _build_component_priority_map(page).get("entries", []),
                    "states": [state for state in (page.get("states") or []) if isinstance(state, dict)],
                }
                for page in page_specs
            ],
        },
        "ui-copy-policy.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "governed-rendering",
            "pages": [_build_ui_copy_projection_contract(page) for page in page_specs],
        },
        "production-ui-copy-profile.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "production-visible-copy",
            "pages": [_build_production_ui_copy_profile(page) for page in page_specs],
        },
        "style-preset.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "design-style-preset",
            "payload": dict(plan.get("theme") or {}),
        },
        "design-review.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "review-visible-copy",
            "payload": {
                "anti_patterns": list(design_reasoning.get("anti_patterns") or []),
                "design_checklist": list(design_reasoning.get("design_checklist") or []),
            },
        },
        "design-lint-rules.json": {
            "generated_at": generated_at,
            "source_hash": source_hash,
            "source_feature": str(plan.get("feature_slug") or "").strip(),
            "source_requirement_refs": source_refs,
            "projection_role": "governance-lint",
            "payload": _build_design_lint_rules(semantic_profile),
        },
    }


def _review_only_human_artifact_paths(*, supports_ux_truth: bool) -> list[str]:
    files = [
        "prototype-review.md",
        "pages/*.md",
    ]
    if supports_ux_truth:
        files.extend(
            [
                "ux-prd.md",
                "DESIGN.md",
                "preview.html",
                "preview-dark.html",
            ]
        )
    return files


def _allowed_implementation_input_paths(*, supports_ux_truth: bool) -> list[str]:
    allowed = [
        "machine-view/index.json",
        "implementation/index.json",
        "implementation-map.json",
        "route-closure-contract.json",
        "design-artifacts/surface-profile.json",
        "design-artifacts/layout-pattern.json",
        "design-artifacts/component-state-matrix.json",
        "design-artifacts/ui-copy-policy.json",
        "design-artifacts/production-ui-copy-profile.json",
        "design-artifacts/style-preset.json",
        "design-artifacts/design-lint-rules.json",
    ]
    if supports_ux_truth:
        allowed.append("design-artifacts/design-context.json")
    return allowed


def _page_state_category(page: dict[str, Any]) -> str:
    states = {str(item.get("id") or "").strip() for item in (page.get("states") or []) if isinstance(item, dict)}
    if states & {"blocked", "error", "stale", "failed", "rebuild-suggested", "doctor-suggested"}:
        return "blocked"
    if states & {"empty", "idle"}:
        return "empty-risk"
    return "ready"


def _render_preview_page_card(page: dict[str, Any]) -> str:
    copy_profile = page.get("production_ui_copy_profile") if isinstance(page.get("production_ui_copy_profile"), dict) else {}
    actions = [str(item).strip() for item in (copy_profile.get("primary_actions") or []) if str(item).strip()]
    actions_markup = "".join(f'<span class="action-pill">{html.escape(item)}</span>' for item in actions[:3]) or '<span class="muted">无主动作</span>'
    return f"""
            <section class="card">
              <div class="eyebrow">{html.escape(page.get('priority', 'P1'))} · {html.escape(', '.join(page.get('platforms', [])[:3]))}</div>
              <h2>{html.escape(str(copy_profile.get('title') or page.get('name') or page.get('page_id') or 'Page'))}</h2>
              <p>{html.escape(str(copy_profile.get('subtitle') or page.get('responsibility') or ''))}</p>
              <div class="actions">{actions_markup}</div>
            </section>
            """


def _build_first_screen_contract(page: dict[str, Any]) -> dict[str, Any]:
    states = [state for state in (page.get("states") or []) if isinstance(state, dict)]
    actions = [str(action.get("label") or "").strip() for action in (page.get("actions") or []) if isinstance(action, dict) and str(action.get("label") or "").strip()]
    status_state = next((state for state in states if str(state.get("id") or "").strip() in {"ready", "running", "healthy-warning"}), states[0] if states else {})
    blocker_state = next(
        (state for state in states if str(state.get("id") or "").strip() in {"blocked", "error", "degraded", "rebuild-suggested", "doctor-suggested", "needs-review", "retry-scheduled"}),
        states[-1] if states else {},
    )
    return {
        "primary_status": str(status_state.get("description") or "").strip(),
        "primary_blocker": str(blocker_state.get("description") or "").strip(),
        "next_actions": actions[:3] or ["查看主体内容"],
        "recovery_path": "优先进入恢复路径或返回上一层，不允许停留在无动作状态。",
        "secondary_disclosure_only": [
            "run list",
            "workspace path",
            "artifact path",
            "history timeline",
            "machine trace detail",
        ],
    }


def _build_visible_contract(page: dict[str, Any]) -> dict[str, Any]:
    sections = [str(item).strip() for item in (page.get("sections") or []) if str(item).strip()]
    actions = [
        _sanitize_production_copy(str(action.get("label") or "").strip())
        for action in (page.get("actions") or [])
        if isinstance(action, dict) and _sanitize_production_copy(str(action.get("label") or "").strip())
    ]
    states = [
        {
            "id": str(state.get("id") or "").strip(),
            "label": _sanitize_production_copy(str(state.get("label") or state.get("id") or "").strip()),
            "description": _sanitize_production_copy(str(state.get("description") or "").strip()),
        }
        for state in (page.get("states") or [])
        if isinstance(state, dict) and str(state.get("id") or "").strip()
    ]
    subtitle = str(page.get("decision_supported") or "").strip()
    if not subtitle:
        analysis = page.get("analysis") if isinstance(page.get("analysis"), dict) else _default_page_analysis(page)
        subtitle = str((analysis.get("decision_focus") or [page.get("responsibility") or ""])[0]).strip()
    return {
        "title": _sanitize_production_copy(str(page.get("name") or page.get("page_id") or "").strip()),
        "subtitle": _sanitize_production_copy(subtitle or str(page.get("responsibility") or "").strip()),
        "must_show_sections": sections[:3] or ["页面头部", "关键内容区"],
        "primary_actions": actions[:3] or ["查看主体内容"],
        "visible_states": states[:6],
        "secondary_disclosure_only": [
            "run list",
            "workspace path",
            "artifact path",
            "history timeline",
            "machine trace detail",
        ],
    }


def _build_design_reasoning(page_specs: list[dict[str, Any]], theme: dict[str, Any]) -> dict[str, Any]:
    explicit_surface_type = str(theme.get("product_surface_type") or "").strip()
    product_surface_type = explicit_surface_type or ("management-workbench" if len(page_specs) >= 3 else "task-oriented-flow")
    return {
        "product_surface_type": product_surface_type,
        "interaction_model": "recognition-first navigation with low-noise drill-down and explicit recovery paths",
        "recommended_layout_pattern": "header -> primary judgment -> supporting context -> next action",
        "visual_priority_rules": [
            "首屏先回答当前页面最重要的问题，再展示支撑信息。",
            "阻塞、错误、恢复动作优先于普通说明文案。",
            "机器内部元数据只能出现在必要的引用区，不能进入主内容区。",
            "保持 Apple-inspired quiet neutral baseline，强调内容而不是装饰。",
        ],
        "anti_patterns": [
            "marketing hero dashboard",
            "generic blue SaaS shell",
            "machine noise in primary UI copy",
            "用路由或草图替代页面意图说明",
        ],
        "design_checklist": [
            "每个页面都要说明主判断与 first glance 信息。",
            "每个关键状态都要有反馈与恢复动作。",
            "设计资产必须由 canonical truth 单向投影生成。",
            "实现可以换代码结构，但不能重写已冻结的信息层级。",
        ],
        "preset_alignment": {
            "design_preset": str(theme.get("design_preset") or ""),
            "quiet_neutral_surfaces": True,
            "restrained_accent": True,
            "content_first_hierarchy": True,
            "workbench_density": True,
        },
    }


def _build_ux_contract(page_specs: list[dict[str, Any]]) -> dict[str, Any]:
    primary_page = page_specs[0] if page_specs else {}
    primary_name = str(primary_page.get("name") or primary_page.get("page_id") or "当前页面")
    action_hierarchy = [
        str(action.get("label") or "").strip()
        for page in page_specs[:3]
        for action in (page.get("actions") or [])
        if isinstance(action, dict) and str(action.get("label") or "").strip()
    ]
    return {
        "first_glance_question": f"用户进入 {primary_name} 后，第一眼需要先判断什么？",
        "primary_decision": "继续下钻、停留处理当前信息，还是先执行恢复/返回动作。",
        "action_hierarchy": action_hierarchy[:6] or ["查看当前判断", "进入下一层", "返回上层"],
        "recognition_over_recall_rules": [
            "把关键判断放在首屏，不要求用户回忆上一页信息。",
            "使用稳定的页面结构和动作命名，减少重新学习成本。",
            "状态反馈必须直接说明发生了什么以及下一步去哪里。",
        ],
        "error_recovery_policy": [
            "error / blocked / stale 状态必须给出可执行恢复动作。",
            "恢复动作优先回到可信真相或上层页面，而不是停留在死路。",
        ],
        "allowed_machine_noise": [
            "来源路径",
            "文档版本",
            "必要的 runtime 引用",
        ],
        "forbidden_machine_noise": [
            "transaction_id",
            "projection_seq",
            "sink_checksums",
            "canonical-envelope",
            "raw runtime log",
        ],
    }


def _build_page_intent_contract(page: dict[str, Any]) -> dict[str, Any]:
    analysis = page.get("analysis") if isinstance(page.get("analysis"), dict) else _default_page_analysis(page)
    sections = [str(item).strip() for item in (page.get("sections") or []) if str(item).strip()]
    actions = [item for item in (page.get("actions") or []) if isinstance(item, dict)]
    return {
        "why_this_page_exists": str(page.get("responsibility") or "").strip() or f"冻结 `{page.get('name')}` 的判断与动作边界。",
        "decision_supported": str(page.get("decision_supported") or "").strip() or str((analysis.get("decision_focus") or ["完成当前页主判断。"])[0]).strip(),
        "must_show_first": sections[:2] or ["页面头部", "关键内容区"],
        "must_not_show": [
            "transaction_id",
            "projection metadata",
            "无边界 runtime 明细",
        ],
        "entry_conditions": [
            f"用户进入 `{page.get('page_id')}` 需要先获得当前上下文。",
            "当前 requirement truth 已经明确该页承担的主判断。",
        ],
        "exit_actions": [
            {
                "label": str(action.get("label") or "").strip(),
                "target": str(action.get("target") or "").strip(),
            }
            for action in actions[:6]
            if str(action.get("label") or "").strip()
        ] or [{"label": "停留当前页继续阅读", "target": str(page.get("page_id") or "").strip()}],
    }


def _build_internal_governance(page: dict[str, Any]) -> dict[str, Any]:
    analysis = page.get("analysis") if isinstance(page.get("analysis"), dict) else _default_page_analysis(page)
    return {
        "page_intent_contract": _build_page_intent_contract(page),
        "first_screen_contract": _build_first_screen_contract(page),
        "review_principles": list(analysis.get("layout_rules") or []),
        "layout_breakdown": [
            {
                "section": section,
                "purpose": _section_purpose(section),
                "display_zone": _position_label(index, len(page.get("sections") or [])),
            }
            for index, section in enumerate([str(item).strip() for item in (page.get("sections") or []) if str(item).strip()])
        ],
        "interaction_contract": _render_interaction_notes(page),
        "state_contract": _render_state_notes(page),
        "noise_guardrail": str(analysis.get("noise_guardrail") or "").strip(),
    }


def _build_state_visibility_contract(page: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    page_name = str(page.get("name") or page.get("page_id") or "当前页")
    state_id = str(state.get("id") or "").strip()
    description = str(state.get("description") or "").strip()
    ac_refs = [str(item).strip().upper() for item in (state.get("ac_refs") or []) if str(item).strip()]
    tc_refs = [str(item).strip().upper() for item in (state.get("tc_refs") or []) if str(item).strip()]
    primary_actions = [str(action.get("label") or "").strip() for action in (page.get("actions") or []) if isinstance(action, dict) and str(action.get("label") or "").strip()][:3]
    recovery_actions = ["返回上一层", "重试当前动作"]
    forbidden_feedback = ["只显示技术错误码", "隐藏下一步动作"]
    user_question = f"{page_name} 当前发生了什么，我下一步该做什么？"
    required_feedback = [description or f"{state_id} 状态需要有明确反馈。"]
    if state_id == "loading":
        recovery_actions = ["继续等待数据加载", "返回上一层"]
        forbidden_feedback = ["页面结构抖动", "空白无提示"]
    elif state_id in {"empty", "idle"}:
        required_feedback.append("解释为什么为空，以及回到哪里继续。")
    elif state_id in {"error", "blocked", "stale", "source-missing"}:
        required_feedback.append("明确恢复动作与回退路径。")
    elif state_id in {"ready", "success", "document-open", "frozen"}:
        recovery_actions = ["继续主要操作", "进入下一层或返回上层"]
        forbidden_feedback = ["完成状态仍要求用户猜下一步"]
    return {
        "user_question": user_question,
        "required_feedback": required_feedback,
        "primary_actions": primary_actions or ["保持当前页上下文", "执行当前页主动作"],
        "recovery_actions": recovery_actions,
        "acceptance_refs": {
            "ac_refs": ac_refs,
            "tc_refs": tc_refs,
        },
        "forbidden_feedback": forbidden_feedback,
    }


def _build_page_layout(page_id: str, sections: list[str] | None = None) -> list[str]:
    layouts = {
        "home": [
            "+----------------------------------------------------------------------------------+",
            "| 顶栏：Beacon 管理端 | 时间范围 | 视角: CEO / Owner | 进入项目组合总览            |",
            "+----------------------------------------------------------------------------------+",
            "| 指标条: 活跃项目 | 阻塞项目 | 活跃 runtime | 今日交付 | 需介入项目                 |",
            "+----------------------------------------------------------------------------------+",
            "| 重点介入区                                                                       |",
            "| - P0 项目A: 卡在 qa，等待 owner 决策                                              |",
            "| - P1 项目B: docs 缺口，需补 test-case                                             |",
            "| [进入重点项目] [查看全部介入项]                                                   |",
            "+----------------------------------------------------------------------------------+",
            "| 项目推进摘要列表                                                                  |",
            "| 项目 | 当前版本 | 当前阶段 | 健康态 | 当前交付 | blocker | 下一步                 |",
            "| A    | v1.3.6   | prototype | risk   | 首页草图  | qa 缺口 | 进详情               |",
            "| B    | v1.2.4   | implement | good   | 文档查看器 | 无      | 继续验证            |",
            "+----------------------------------------------------------------------------------+",
            "| 当前交付                                      | 下一步建议                         |",
            "| - v1.3.6 首页/总览骨架已冻结                  | - 先处理阻塞项目A                  |",
            "| - 物料查看器只读流已接入                      | - 再进入 management overview 扫描  |",
            "+----------------------------------------------------------------------------------+",
        ],
        "management-overview": [
            "+-----------------------------------------------------------------------------------+",
            "| 顶栏：返回首页 | 管理总览 | 更新时间 | 批量筛选已生效数                            |",
            "+-----------------------------------------------------------------------------------+",
            "| 筛选与排序条: 项目类型 | 当前版本 | 阶段 | 健康态 | debug | 需求物料状态 | 排序    |",
            "+-----------------------------------------------------------------------------------+",
            "| 阶段分布摘要: draft 2 | prototype 3 | implement 4 | qa 1 | release 1              |",
            "+-----------------------------------------------------------------------------------+",
            "| 项目注册表                                                                         |",
            "| 项目 | 类型 | 当前版本 | 主 feature | 阶段 | 进度 | 健康态 | debug | 下一步       |",
            "| A    | 产品 | v1.3.6   | 管理看板   | prototype | 70% | risk | warn | 进详情       |",
            "| B    | 工具 | v1.2.4   | 物料查看器 | implement | 90% | good | ok   | 做验证       |",
            "+-----------------------------------------------------------------------------------+",
            "| 风险与调试摘要                               | 推荐 skill 区                        |",
            "| - 2 个项目存在 blocker                        | - prototype review                  |",
            "| - 1 个项目 debug 态异常                       | - doctor verify-context             |",
            "+-----------------------------------------------------------------------------------+",
        ],
        "project-detail": [
            "+-----------------------------------------------------------------------------------+",
            "| 顶栏：返回总览 | 项目名 | 项目类型 | owner | 当前阶段                               |",
            "+-----------------------------------------------------------------------------------+",
            "| 项目头部摘要                                  | 当前版本 / git / worktree           |",
            "| - 当前目标                                    | - version: v1.3.6                   |",
            "| - 为什么停在这里                              | - branch/worktree 状态              |",
            "+-----------------------------------------------------------------------------------+",
            "| 主 PRD                              | 并行 PRD / 子线                            |",
            "| - 主线 feature                     | - 并行 feature A                           |",
            "| - 当前承诺面                       | - 并行 feature B                           |",
            "+-----------------------------------------------------------------------------------+",
            "| 需求闭环状态: prd | user-story | test-case | prototype | qa 准备度                |",
            "+-----------------------------------------------------------------------------------+",
            "| 最近交付                                      | 下一步 / 推荐动作                     |",
            "| - 最新冻结产物                                | - 继续 implement / qa / review       |",
            "| - 最近一次 review 结论                        | - 推荐 skill                          |",
            "+-----------------------------------------------------------------------------------+",
            "| runtime 摘要卡                                | 文档查看 / 恢复诊断入口               |",
            "| - single/team/ralph 摘要                      | [查看项目物料] [查看恢复诊断]         |",
            "+-----------------------------------------------------------------------------------+",
        ],
        "runtime-center": [
            "+----------------------------------------------------------------------------------+",
            "| 顶栏：返回项目详情 | 运行中心 | 最近刷新时间 | 当前活跃模式                        |",
            "+----------------------------------------------------------------------------------+",
            "| 模式切换： single | team | ralph                                                |",
            "+----------------------------------------------------------------------------------+",
            "| 运行态摘要头部: 当前状态 | round_count | failure_streak | 当前执行目标             |",
            "+----------------------------------------------------------------------------------+",
            "| agent / session 引用                         | linked run / artifact refs           |",
            "| - session id / agent 数                      | - latest run                         |",
            "| - host / lane 摘要                           | - artifact / report                  |",
            "+----------------------------------------------------------------------------------+",
            "| recent_result                                | blocker / next_action                |",
            "| - 最近结果摘要                               | - 当前 blocker                       |",
            "| - 最近一次状态变化                           | - 下一步动作                         |",
            "+----------------------------------------------------------------------------------+",
        ],
        "recovery-diagnostics": [
            "+----------------------------------------------------------------------------------+",
            "| 顶栏：返回项目详情 | 恢复诊断 | 当前环境状态                                      |",
            "+----------------------------------------------------------------------------------+",
            "| truth 来源说明                                                                    |",
            "| - 正式真相来自 docs/beacon + .beacon                                              |",
            "| - 当前页只解释恢复路径，不改写 requirement truth                                   |",
            "+----------------------------------------------------------------------------------+",
            "| 诊断卡： degraded | rebuild | doctor                                              |",
            "| - 当前命中的诊断类型                                                               |",
            "| - 推荐动作与触发条件                                                               |",
            "+----------------------------------------------------------------------------------+",
            "| 恢复步骤                                      | 风险提示                           |",
            "| 1. 校验上下文                                 | - 不要把投影层当真相              |",
            "| 2. 执行 doctor / rebuild                      | - 误修复会导致 drift              |",
            "| 3. 回到项目页验证                             | - 先验证再 freeze                 |",
            "+----------------------------------------------------------------------------------+",
        ],
        "material-viewer": [
            "+-----------------------------------------------------------------------------------+",
            "| 顶栏：返回项目详情 | 项目物料查看器 | 当前项目 | 只读模式                         |",
            "+-----------------------------------------------------------------------------------+",
            "| 左侧导航                                                                           |",
            "| 版本树            | 文档类型列表            | feature / 文档目录                  |",
            "| v1.3.6            | prd                    | beacon-v1.3.6...md                   |",
            "| v1.3.5            | user-story             | ...                                   |",
            "| v1.3.4            | test-case              |                                       |",
            "+-----------------------------------------------------------------------------------+",
            "| 文档阅读面板                                                                       |",
            "| - 文档标题 / 简介                                                                  |",
            "| - Markdown 正文预览                                                                |",
            "+-----------------------------------------------------------------------------------+",
            "| 来源路径信息                                | 只读说明 / 版本切换                  |",
            "| - docs/beacon/...                            | - 真相仍在本地文档树                 |",
            "+-----------------------------------------------------------------------------------+",
        ],
        "material-document-detail": [
            "+-----------------------------------------------------------------------------------+",
            "| 顶栏：返回物料查看器 | 文档详情 | 当前版本 / 类型 / feature                        |",
            "+-----------------------------------------------------------------------------------+",
            "| 文档头部信息                                                                       |",
            "| 标题 | 更新时间 | 来源版本 | 文档类型                                              |",
            "+-----------------------------------------------------------------------------------+",
            "| 面包屑： version / document type / feature / current document                      |",
            "+-----------------------------------------------------------------------------------+",
            "| Markdown 正文区                                                                    |",
            "| # 文档标题                                                                         |",
            "| 段落 / 列表 / 冻结说明 / requirement 内容预览                                     |",
            "+-----------------------------------------------------------------------------------+",
            "| 同类文档切换                               | 来源路径 / 只读说明                    |",
            "| - 上一篇 / 下一篇                          | - docs/beacon/...                     |",
            "| - 同版本相邻文档                           | - 不提供网页内编辑                     |",
            "+-----------------------------------------------------------------------------------+",
        ],
    }
    if page_id in layouts:
        return layouts[page_id]
    dynamic_sections = [str(item).strip() for item in (sections or []) if str(item).strip()] or ["页面头部", "主体内容", "关键操作区"]
    rendered = ["+-----------------------------+"]
    for section in dynamic_sections[:6]:
        rendered.append(f"| {section[:24]:<24} |")
        rendered.append("+-----------------------------+")
    return rendered


def _normalize_priority(value: Any) -> str:
    priority = str(value or "").strip().upper()
    return priority if priority in {"P0", "P1", "P2"} else "P1"


def _normalize_platforms(value: Any, *, default: list[str] | None = None) -> list[str]:
    allowed = {"web": "Web", "pc": "PC", "app": "App", "mobile": "App"}
    normalized: list[str] = []
    for item in _coerce_string_list(value, default=default or ["Web", "PC"], max_items=4):
        resolved = allowed.get(str(item).strip().lower())
        if resolved and resolved not in normalized:
            normalized.append(resolved)
    return normalized or list(default or ["Web", "PC"])


def _contains_machine_noise(text: str) -> bool:
    return bool(MACHINE_NOISE_PATTERN.search(str(text or "").strip()))


def _infer_llm_sections(page_id: str, name: str) -> list[str]:
    lowered = f"{page_id} {name}".lower()
    if any(token in lowered for token in {"home", "首页", "dashboard", "总览"}):
        return ["页面头部", "指标与判断", "重点事项", "下一步动作"]
    if any(token in lowered for token in {"detail", "详情"}):
        return ["头部摘要", "主体详情", "关键动作", "状态与反馈"]
    if any(token in lowered for token in {"viewer", "reader", "物料", "文档"}):
        return ["导航区", "阅读区", "上下文信息", "切换与状态"]
    if any(token in lowered for token in {"runtime", "运行", "diagnostic", "恢复", "recovery"}):
        return ["状态摘要", "核心面板", "异常与恢复", "返回路径"]
    return ["页面头部", "关键内容区", "主要操作区", "状态与反馈区"]


def _default_llm_responsibility(name: str, sections: list[str]) -> str:
    first_section = sections[0] if sections else "当前页面的核心信息"
    return f"先建立 `{name}` 的判断上下文，再通过 `{first_section}` 收口到下一步动作。"


def _build_semantic_layout(
    *,
    page_id: str,
    name: str,
    sections: list[str],
    actions: list[dict[str, str]] | None = None,
) -> list[str]:
    left_sections = sections[:2] or ["页面头部", "主体内容"]
    right_sections = sections[2:4] or ["关键操作区", "状态与反馈区"]
    action_labels = [str(item.get("label") or "").strip() for item in (actions or []) if str(item.get("label") or "").strip()]
    action_text = " | ".join(action_labels[:3]) or "主要动作"
    title = name or page_id.replace("-", " ").title()
    return [
        "+----------------------------------------------------------------------------------+",
        f"| 页头：{title[:18]:<18} | 视角/筛选 | 关键入口 | 返回路径                          |",
        "+----------------------------------------------------------------------------------+",
        f"| {left_sections[0][:30]:<30} | {left_sections[1][:30]:<30} |",
        "| - 当前判断需要先看什么                  | - 哪些信息支持继续下钻                 |",
        "+----------------------------------------------------------------------------------+",
        f"| {right_sections[0][:30]:<30} | {right_sections[1][:30]:<30} |",
        "| - 这里承载主要动作与跳转                | - 这里承载 loading / empty / error     |",
        "+----------------------------------------------------------------------------------+",
        f"| 操作区：{action_text[:68]:<68} |",
        "+----------------------------------------------------------------------------------+",
    ]


def _validate_llm_page_contract(
    *,
    page_specs: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> list[str]:
    issues: list[str] = []
    if len(page_specs) < 2:
        issues.append("llm prototype must contain at least 2 pages")

    page_ids = [str(page.get("page_id") or "").strip() for page in page_specs if str(page.get("page_id") or "").strip()]
    known_pages = set(page_ids)
    inbound_counts = {page_id: 0 for page_id in page_ids}
    for transition in transitions:
        target = str(transition.get("to") or "").strip()
        if target in inbound_counts:
            inbound_counts[target] += 1

    for index, page in enumerate(page_specs, start=1):
        page_id = str(page.get("page_id") or "").strip()
        page_name = str(page.get("name") or "").strip() or page_id
        sections = [str(item).strip() for item in page.get("sections", []) if str(item).strip()]
        actions = [item for item in page.get("actions", []) if isinstance(item, dict)]
        states = [item for item in page.get("states", []) if isinstance(item, dict)]
        layout_lines = [str(item).rstrip() for item in page.get("layout_lines", []) if str(item).strip()]
        analysis = page.get("analysis") if isinstance(page.get("analysis"), dict) else {}

        if len(sections) < 2:
            issues.append(f"{page_id}: requires at least 2 sections")
        if len(layout_lines) < 3:
            issues.append(f"{page_id}: layout is too small for a reviewable wireframe")
        if not states:
            issues.append(f"{page_id}: missing state definitions")
        if index > 1 and inbound_counts.get(page_id, 0) == 0:
            issues.append(f"{page_id}: has no inbound transition")

        human_text_blocks = [
            str(page.get("responsibility") or ""),
            *sections,
            str(analysis.get("target_user") or ""),
            str(analysis.get("noise_guardrail") or ""),
            *[str(item) for item in analysis.get("decision_focus", [])],
            *[str(item) for item in analysis.get("layout_rules", [])],
            *layout_lines,
        ]
        if any(_contains_machine_noise(block) for block in human_text_blocks if str(block).strip()):
            issues.append(f"{page_id}: contains machine/projection noise in human content")

        for action in actions:
            target = str(action.get("target") or "").strip()
            if target and target not in known_pages:
                issues.append(f"{page_id}: action target `{target}` not found in prototype pages")

        state_ids = {str(item.get("id") or "").strip() for item in states if str(item.get("id") or "").strip()}
        if "ready" not in state_ids:
            issues.append(f"{page_id}: missing ready state")
        if not ({"loading", "error"} & state_ids):
            issues.append(f"{page_id}: missing loading/error fallback state")

        if not page_name:
            issues.append(f"{page_id}: missing page name")

    if not transitions:
        issues.append("llm prototype must define at least one transition")
    return issues


def _human_view_files() -> list[str]:
    return [
        "wireframe-summary.md",
        "navigation-map.md",
        "state-flow-map.md",
        "component-catalog.md",
        "automation-priority-matrix.md",
        "pages/*.md",
    ]


def _default_page_analysis(page: dict[str, Any]) -> dict[str, Any]:
    actions = [str(action.get("label") or "").strip() for action in page.get("actions", []) if isinstance(action, dict)]
    governance = page.get("internal_governance") if isinstance(page.get("internal_governance"), dict) else {}
    first_screen = governance.get("first_screen_contract") if isinstance(governance.get("first_screen_contract"), dict) else {}
    return {
        "target_user": "需要完成页面判断与下钻的 Beacon 使用者",
        "decision_focus": [
            str(first_screen.get("primary_status") or page.get("responsibility") or "").strip() or "先建立页面上下文。",
            (
                f"确认是否执行 {actions[0]}。"
                if actions
                else "确认是否继续停留当前页或进入下一层。"
            ),
        ],
        "layout_rules": [
            "首屏先回答当前页最重要的问题。",
            "主体区只保留支撑判断的结构，不展开高保真视觉。",
        ],
        "noise_guardrail": "首屏只保留操作者判断需要的信息；路径、历史与机器材料只能进入二级展开。",
    }


def _position_label(index: int, total: int) -> str:
    if index == 0:
        return "首屏"
    if total <= 2:
        return "主体"
    if index == total - 1:
        return "收口区"
    return "主体区"


def _section_purpose(section: str) -> str:
    lowered = section.lower()
    if "总览" in section or "摘要" in section or "头部" in section:
        return "先建立上下文，让人快速判断当前局面。"
    if "阻塞" in section or "风险" in section or "诊断" in section or "恢复" in section:
        return "集中暴露异常与介入信号，避免风险被正常信息淹没。"
    if "列表" in section or "注册表" in section or "目录" in section or "树" in section:
        return "支持快速扫描和定位下一层下钻入口。"
    if "正文" in section or "阅读" in section or "文档" in section:
        return "稳定承载只读内容，避免把注意力打散到无关控件。"
    if "来源路径" in section or "只读说明" in section:
        return "补充可信来源与边界说明，但不应压过主体内容。"
    if "下一步" in section or "推荐" in section:
        return "把观察收口成明确动作，避免用户看完后不知道去哪里。"
    if "运行" in section or "artifact" in lowered or "session" in lowered:
        return "只展示运行态必要信息，不展开底层机器细节。"
    if "筛选" in section or "排序" in section:
        return "帮助用户先收窄范围，再进入对比与下钻。"
    return "承载该页完成核心判断所需的最小信息块。"


def _render_section_breakdown(page: dict[str, Any]) -> list[str]:
    sections = [str(item).strip() for item in page.get("sections", []) if str(item).strip()]
    total = len(sections)
    lines: list[str] = []
    for index, section in enumerate(sections):
        lines.append(f"- `{section}`: 放在{_position_label(index, total)}，{_section_purpose(section)}")
    return lines


def _render_interaction_notes(page: dict[str, Any]) -> list[str]:
    transitions = {
        str(item.get("to") or ""): str(item.get("type") or "")
        for item in page.get("outbound_transitions", [])
        if isinstance(item, dict)
    }
    notes: list[str] = []
    for action in page.get("actions", []):
        if not isinstance(action, dict):
            continue
        label = str(action.get("label") or "").strip()
        trigger = str(action.get("trigger") or "").strip()
        target = str(action.get("target") or "").strip()
        transition_type = transitions.get(target, "")
        if transition_type == "return":
            notes.append(f"- `{label}`: 通过 {trigger} 回到 `{target}`，用于撤销下钻并保留上层判断。")
        elif transition_type == "drill-down":
            notes.append(f"- `{label}`: 通过 {trigger} 下钻到 `{target}`，只在当前页信息不足时继续展开。")
        elif target == page.get("page_id"):
            notes.append(f"- `{label}`: 通过 {trigger} 留在本页切换阅读对象，避免跳出当前上下文。")
        else:
            notes.append(f"- `{label}`: 通过 {trigger} 进入 `{target}`，把当前判断转交到下一层页面完成。")
    return notes or ["- 当前页没有定义主动跳转，重点是稳定呈现信息。"]


def _render_state_notes(page: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    for state in page.get("states", []):
        if not isinstance(state, dict):
            continue
        state_id = str(state.get("id") or "").strip()
        label = str(state.get("label") or state_id).strip()
        description = str(state.get("description") or "").strip()
        if state_id in {"error", "source-missing"}:
            notes.append(f"- `{label}`: {description} 页面要优先给出回退或恢复入口，而不是只报错。")
        elif state_id == "loading":
            notes.append(f"- `{label}`: {description} 加载态只保留骨架结构，避免造成页面重新排版。")
        elif state_id in {"empty", "idle"}:
            notes.append(f"- `{label}`: {description} 空态要说明为什么为空，以及下一步该回哪里。")
        else:
            notes.append(f"- `{label}`: {description}")
    return notes


def _render_information_priority(page: dict[str, Any], analysis: dict[str, Any]) -> list[str]:
    sections = [str(item).strip() for item in page.get("sections", []) if str(item).strip()]
    priority_lines: list[str] = []
    if sections:
        priority_lines.append(f"- 第一优先看 `{sections[0]}`，因为页面必须先完成第一轮判断。")
    if len(sections) >= 2:
        priority_lines.append(f"- 第二优先看 `{sections[1]}`，用于补足判断依据并决定是否下钻。")
    if sections:
        priority_lines.append(f"- 最后收口到 `{sections[-1]}`，让用户在读完后明确主动作。")
    for rule in analysis.get("layout_rules", [])[:2]:
        priority_lines.append(f"- 审阅原则：{rule}")
    return priority_lines


def _render_page_markdown(page: dict[str, Any]) -> str:
    visible_contract = page.get("visible_contract") if isinstance(page.get("visible_contract"), dict) else {}
    copy_profile = page.get("production_ui_copy_profile") if isinstance(page.get("production_ui_copy_profile"), dict) else {}
    actions = [str(item).strip() for item in (visible_contract.get("primary_actions") or copy_profile.get("primary_actions") or []) if str(item).strip()]
    sections = [str(item).strip() for item in (visible_contract.get("must_show_sections") or page.get("sections") or []) if str(item).strip()]
    states = [state for state in (visible_contract.get("visible_states") or []) if isinstance(state, dict)]
    layout_lines = (
        page.get("layout_lines")
        if isinstance(page.get("layout_lines"), list) and page.get("layout_lines")
        else _build_page_layout(page["page_id"], page.get("sections"))
    )
    lines = [
        f"# 页面：{page['name']}",
        "",
        f"**平台**: `{', '.join(page['platforms'])}`",
        f"**优先级**: `{page['priority']}`",
        "",
        "## 页面文案",
        f"- 标题：{copy_profile.get('title', visible_contract.get('title', page['name']))}",
        f"- 副标题：{copy_profile.get('subtitle', visible_contract.get('subtitle', page['responsibility']))}",
        f"- 主动作：{', '.join(actions[:3]) or '-'}",
        "",
        "## 页面结构",
    ]
    lines.extend(f"- {section}" for section in sections)
    lines.extend(["", "## 页面线框", "```text", *layout_lines, "```"])
    lines.extend(["", "## 页面状态"])
    for state in states:
        label = str(state.get("label") or state.get("id") or "").strip()
        description = str(state.get("description") or "").strip()
        lines.append(f"- {label}：{description}" if description else f"- {label}")
    lines.extend(["", "## 页面跳转"])
    transitions = [item for item in (page.get("actions") or []) if isinstance(item, dict)]
    if transitions:
        for action in transitions[:8]:
            label = str(action.get("label") or "").strip()
            target = str(action.get("target") or "").strip()
            if label and target:
                lines.append(f"- {label} -> `{target}`")
    else:
        lines.append("- 当前页无跨页跳转")
    return _sanitize_production_copy("\n".join(lines))


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


def _render_ux_prd_md(plan: dict[str, Any]) -> str:
    design_context = plan.get("design_context") if isinstance(plan.get("design_context"), dict) else {}
    design_reasoning = plan.get("design_reasoning") if isinstance(plan.get("design_reasoning"), dict) else {}
    ux_contract = plan.get("ux_contract") if isinstance(plan.get("ux_contract"), dict) else {}
    semantic_profile = plan.get("software_semantic_profile") if isinstance(plan.get("software_semantic_profile"), dict) else {}
    lines = [
        f"# UX PRD：{plan['feature']}",
        "",
        f"**Feature**: `{plan['feature_slug']}`",
        f"**Version**: `{plan['version']}`",
        "",
        "## 设计上下文",
        f"- 目标读者：{design_context.get('target_audience', '-')}",
        f"- 主要用例：{', '.join(design_context.get('primary_use_cases', [])[:5]) or '-'}",
        f"- 操作者状态：{design_context.get('operator_mental_state', '-')}",
        f"- 使用环境：{design_context.get('usage_environment', '-')}",
        f"- 语义基调：{', '.join(design_context.get('brand_tone', [])[:5]) or '-'}",
        f"- 信息密度：{design_context.get('density_preference', '-')}",
        "",
        "## 设计原则",
        f"- 产品表面类型：{design_reasoning.get('product_surface_type', '-')}",
        f"- 交互模型：{design_reasoning.get('interaction_model', '-')}",
        f"- 版式模式：{design_reasoning.get('recommended_layout_pattern', '-')}",
        "",
        "## 软件语义规范",
        f"- 标题规则：{semantic_profile.get('title_rule', '-')}",
        f"- 状态规则：{semantic_profile.get('state_rule', '-')}",
        f"- 动作规则：{semantic_profile.get('action_rule', '-')}",
        f"- 异常规则：{semantic_profile.get('exception_rule', '-')}",
        "",
        "## 交互合同",
        f"- 首屏判断问题：{ux_contract.get('first_glance_question', '-')}",
        f"- 主判断：{ux_contract.get('primary_decision', '-')}",
        f"- 动作层级：{', '.join(ux_contract.get('action_hierarchy', [])[:6]) or '-'}",
        "",
        "## 页面意图合同",
    ]
    for page in plan.get("page_specs", []):
        if not isinstance(page, dict):
            continue
        governance = page.get("internal_governance") if isinstance(page.get("internal_governance"), dict) else {}
        intent = governance.get("page_intent_contract") if isinstance(governance.get("page_intent_contract"), dict) else {}
        lines.extend(
            [
                f"### {page.get('name', page.get('page_id', 'page'))}",
                f"- 页面职责：{intent.get('why_this_page_exists', '-')}",
                f"- 支持判断：{intent.get('decision_supported', '-')}",
                f"- 首屏必须展示：{', '.join(intent.get('must_show_first', [])[:4]) or '-'}",
                f"- 首屏禁止展示：{', '.join(intent.get('must_not_show', [])[:4]) or '-'}",
            ]
        )
    lines.append("")
    lines.append("## 状态可见性合同")
    seen_states: set[str] = set()
    for page in plan.get("page_specs", []):
        if not isinstance(page, dict):
            continue
        for state in page.get("states", []):
            if not isinstance(state, dict):
                continue
            state_id = str(state.get("id") or "").strip()
            if not state_id or state_id in seen_states:
                continue
            seen_states.add(state_id)
            contract = state.get("state_visibility_contract") if isinstance(state.get("state_visibility_contract"), dict) else {}
            lines.extend(
                [
                    f"- `{state_id}`：{contract.get('user_question', '-')}",
                    f"  - 必要反馈：{', '.join(contract.get('required_feedback', [])[:4]) or '-'}",
                    f"  - 主动作：{', '.join(contract.get('primary_actions', [])[:4]) or '-'}",
                    f"  - 恢复动作：{', '.join(contract.get('recovery_actions', [])[:4]) or '-'}",
                    f"  - AC Refs: {', '.join(((contract.get('acceptance_refs') or {}).get('ac_refs') or [])[:4]) or '-'}",
                    f"  - TC Refs: {', '.join(((contract.get('acceptance_refs') or {}).get('tc_refs') or [])[:4]) or '-'}",
                ]
            )
    lines.extend(
        [
            "",
            "## Traceability",
            f"- AC Refs: {', '.join((plan.get('requirement_ids') or {}).get('ac_ids', [])[:12]) or '-'}",
            f"- TC Refs: {', '.join((plan.get('requirement_ids') or {}).get('tc_ids', [])[:12]) or '-'}",
        ]
    )
    return "\n".join(lines)


def _render_design_md(plan: dict[str, Any], theme: dict[str, Any]) -> str:
    design_context = plan.get("design_context") if isinstance(plan.get("design_context"), dict) else {}
    design_reasoning = plan.get("design_reasoning") if isinstance(plan.get("design_reasoning"), dict) else {}
    semantic_profile = plan.get("software_semantic_profile") if isinstance(plan.get("software_semantic_profile"), dict) else {}
    return "\n".join(
        [
            f"# DESIGN.md: {plan['feature']}",
            "",
            "## Visual Theme",
            f"- Design Preset: `{theme.get('design_preset', 'apple-inspired-design-md')}`",
            f"- Primary Accent: `{theme.get('primary', '#0071E3')}`",
            f"- Secondary Surface: `{theme.get('secondary', '#F5F5F7')}`",
            "- Atmosphere: quiet neutrals, restrained emphasis, dense but readable workbench hierarchy.",
            "",
            "## Typography",
            "- Bias toward SF Pro / system sans.",
            "- Hero-scale text is disallowed in workbench pages unless a real first-screen signal demands it.",
            "",
            "## Layout Principles",
            f"- Recommended Pattern: {design_reasoning.get('recommended_layout_pattern', '-')}",
            "- First screen answers the main question before secondary detail.",
            "- Keep navigation low-noise and avoid decorative dashboard filler.",
            "",
            "## Component Styling",
            "- Compact toolbars, restrained cards, explicit empty/error/loading states.",
            "- Buttons and controls should privilege recognition over recall.",
            "",
            "## Do",
            "- Show recovery actions when blocked, stale, or error states appear.",
            "- Keep source paths and machine references in secondary disclosure zones only.",
            "",
            "## Don't",
            "- Do not produce a marketing hero dashboard.",
            "- Do not surface transaction metadata in primary UI copy.",
            "- Do not use a generic blue SaaS shell as the default design answer.",
            "",
            "## Responsive",
            "- Preserve hierarchy and next-action clarity on desktop-first workbench layouts.",
            "- Collapse secondary detail before primary judgment content.",
            "",
            "## Agent Prompt Guide",
            f"- Primary audience: {design_context.get('target_audience', '-')}",
            "- Preserve page intent contracts and state visibility contracts during implementation.",
            "- Treat this file as projection from prototype truth, not an editable source of truth.",
            "",
            "## Semantic Guardrail",
            f"- Title Rule: {semantic_profile.get('title_rule', '-')}",
            f"- State Rule: {semantic_profile.get('state_rule', '-')}",
            f"- Action Rule: {semantic_profile.get('action_rule', '-')}",
        ]
    )


def _render_preview_html(plan: dict[str, Any], theme: dict[str, Any], *, dark: bool) -> str:
    bg = "#111111" if dark else "#F5F5F7"
    fg = "#F5F5F7" if dark else "#1D1D1F"
    card = "#1C1C1E" if dark else "#FFFFFF"
    border = "#3A3A3C" if dark else "#D2D2D7"
    accent = str(theme.get("primary") or "#0071E3")
    page_cards = []
    for page in (plan.get("page_specs") or [])[:6]:
        if not isinstance(page, dict):
            continue
        page_cards.append(_render_preview_page_card(page))
    mode = "Dark" if dark else "Light"
    first_page = next((page for page in (plan.get("page_specs") or []) if isinstance(page, dict)), {})
    copy_profile = first_page.get("production_ui_copy_profile") if isinstance(first_page.get("production_ui_copy_profile"), dict) else {}
    feature_title = str(copy_profile.get("title") or first_page.get("name") or plan["feature"]).strip()
    hero_summary = str(copy_profile.get("subtitle") or first_page.get("responsibility") or "").strip()
    page_state = _page_state_category(first_page)
    first_actions = [str(item).strip() for item in (copy_profile.get("primary_actions") or []) if str(item).strip()]
    recovery_panel = ""
    if page_state in {"blocked", "empty-risk"}:
        governance = first_page.get("internal_governance") if isinstance(first_page.get("internal_governance"), dict) else {}
        first_screen = governance.get("first_screen_contract") if isinstance(governance.get("first_screen_contract"), dict) else {}
        recovery_panel = f"""
    <section class="card alert" style="margin-bottom:16px;">
      <div class="eyebrow">恢复判断</div>
      <h2>{html.escape(_sanitize_production_copy(str(first_screen.get('primary_blocker') or '当前存在阻塞')))}</h2>
      <p>{html.escape(_sanitize_production_copy(str(first_screen.get('recovery_path') or '请执行恢复动作后继续。')))}</p>
    </section>
"""
    primary_actions_markup = "".join(
        f'<span class="action-pill">{html.escape(item)}</span>' for item in first_actions[:3]
    ) or '<span class="muted">无主动作</span>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{plan['feature']} Design Preview {mode}</title>
  <style>
    :root {{
      color-scheme: {'dark' if dark else 'light'};
      --bg: {bg};
      --fg: {fg};
      --card: {card};
      --border: {border};
      --accent: {accent};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif; background: var(--bg); color: var(--fg); }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 56px; }}
    .hero {{ display: grid; gap: 12px; margin-bottom: 24px; }}
    .eyebrow {{ font-size: 12px; color: var(--accent); text-transform: uppercase; }}
    h1, h2 {{ margin: 0; font-weight: 600; }}
    p, li {{ line-height: 1.5; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; display: grid; gap: 10px; }}
    .alert {{ border-color: var(--accent); }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .action-pill {{ border: 1px solid var(--border); border-radius: 999px; padding: 6px 10px; font-size: 13px; }}
    .muted {{ color: #6E6E73; font-size: 13px; }}
    ul {{ margin: 0; padding-left: 18px; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">{theme.get('design_preset', 'apple-inspired-design-md')} · {mode} preview</div>
      <h1>{html.escape(feature_title)}</h1>
      <p>{html.escape(hero_summary)}</p>
    </section>
    <section class="card" style="margin-bottom:16px;">
      <div class="eyebrow">主动作</div>
      <div class="actions">{primary_actions_markup}</div>
    </section>
    {recovery_panel}
    <section class="grid">
      {''.join(page_cards)}
    </section>
  </main>
</body>
</html>
"""


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


def _serialize_page_spec(page: dict[str, Any]) -> dict[str, Any]:
    return {
        "page_id": str(page.get("page_id") or "").strip(),
        "name": str(page.get("name") or "").strip(),
        "priority": str(page.get("priority") or "").strip(),
        "platforms": list(page.get("platforms") or []),
        "responsibility": str(page.get("responsibility") or "").strip(),
        "sections": [str(item).strip() for item in (page.get("sections") or []) if str(item).strip()],
        "actions": [item for item in (page.get("actions") or []) if isinstance(item, dict)],
        "states": [item for item in (page.get("states") or []) if isinstance(item, dict)],
        "requirement_refs": page.get("requirement_refs") if isinstance(page.get("requirement_refs"), dict) else {},
        "outbound_transitions": [item for item in (page.get("outbound_transitions") or []) if isinstance(item, dict)],
        "visible_contract": page.get("visible_contract") if isinstance(page.get("visible_contract"), dict) else {},
        "internal_governance": page.get("internal_governance") if isinstance(page.get("internal_governance"), dict) else {},
        "ui_copy_policy": page.get("ui_copy_policy") if isinstance(page.get("ui_copy_policy"), dict) else {},
        "production_ui_copy_profile": page.get("production_ui_copy_profile") if isinstance(page.get("production_ui_copy_profile"), dict) else {},
    }


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


def _estimate_tokens(text: str) -> int:
    return max(1, len((text or "").split()))


def _prototype_llm_disabled() -> bool:
    return str(os.environ.get("BEACON_PROTOTYPE_DISABLE_LLM", "") or "").strip().lower() in {"1", "true", "yes", "on"}


def _prototype_provider_model(model: str) -> str:
    requested = str(model or "").strip()
    if requested and not requested.startswith("beacon-"):
        return requested
    return str(os.environ.get("BEACON_LLM_MODEL", "gpt-4o-mini")).strip() or "gpt-4o-mini"


def _extract_json_blob(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return {}
    candidates = [raw]
    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
    candidates.extend(fenced)
    object_matches = re.findall(r"(\{.*\})", raw, flags=re.DOTALL)
    candidates.extend(object_matches)
    for candidate in candidates:
        snippet = str(candidate or "").strip()
        if not snippet:
            continue
        try:
            payload = json.loads(snippet)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def _prototype_source_context(docs: list[dict[str, Any]]) -> str:
    blocks = []
    for doc in docs:
        blocks.append(f"[{doc['type']}]\n{str(doc.get('text') or '').strip()}")
    return "\n\n".join(blocks)


def _build_prototype_host_bridge_request(
    *,
    feature: str,
    version: str,
    docs: list[dict[str, Any]],
    model: str,
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "command_name": "prototype",
        "request_kind": "prototype-wireframe-compile",
        "feature": feature,
        "version": version,
        "requested_model": model,
        "semantic_layer": semantic_layer if isinstance(semantic_layer, dict) else {},
        "documents": [
            {
                "type": str(doc.get("type") or ""),
                "path": str(doc.get("path") or ""),
                "text": str(doc.get("text") or ""),
            }
            for doc in docs
        ],
    }


def _real_prototype_llm_inference(
    *,
    feature: str,
    version: str,
    docs: list[dict[str, Any]],
    model: str,
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    api_key = str(os.environ.get("BEACON_LLM_API_KEY", "")).strip()
    if not api_key:
        raise PrototypeLLMCompileError("BEACON_LLM_API_KEY missing")

    api_base = str(os.environ.get("BEACON_LLM_API_BASE", "https://api.openai.com/v1")).strip().rstrip("/")
    provider_model = _prototype_provider_model(model)
    timeout_s = float(str(os.environ.get("BEACON_LLM_TIMEOUT", "20")).strip() or "20")
    temperature = float(str(os.environ.get("BEACON_LLM_TEMPERATURE", "0.2")).strip() or "0.2")
    source_context = _prototype_source_context(docs)
    known_page_names = ", ".join(sorted(meta["name"] for meta in PAGE_CATALOG.values()))
    system_prompt = (
        "You are Beacon prototype compiler. "
        "Transform requirement truth into low-fidelity UI wireframe specs. "
        "Return strict compact JSON only. "
        "Do not output prose outside JSON. "
        "Do not output high-fidelity UI. "
        "Respect requirement traceability, keep machine noise out of human page content, "
        "and treat the output template as a shell rather than a source of page semantics."
    )
    user_prompt = f"""
feature={feature}
version={version}
known_page_catalog={known_page_names}
semantic_context:
{render_semantic_prompt_context(semantic_layer)}

Return JSON with this shape:
{{
  "prototype_archetype": "{DEFAULT_PROTOTYPE_ARCHETYPE}|...",
  "theme": {{"primary":"#0071E3","secondary":"#F5F5F7"}},
  "pages": [
    {{
      "page_id": "home",
      "name": "首页",
      "priority": "P0|P1|P2",
      "platforms": ["Web","PC"],
      "responsibility": "...",
      "sections": ["..."],
      "actions": [{{"label":"...","trigger":"...","target":"page-id-or-page-name"}}],
      "states": [{{"id":"ready","label":"...","description":"..."}}],
      "layout": ["ASCII wireframe line 1", "line 2"],
      "analysis": {{
        "target_user": "...",
        "decision_focus": ["..."],
        "layout_rules": ["..."],
        "noise_guardrail": "..."
      }}
    }}
  ],
  "transitions": [
    {{"from":"home","to":"project-detail","trigger":"点击重点项目卡片","type":"primary|drill-down|return"}}
  ]
}}

Constraints:
- Generate low-fidelity wireframe only, using ASCII layout lines.
- Pages must be grounded in the requirement materials below.
- Prefer stable page ids when they clearly match known Beacon pages.
- Actions/transition targets must reference pages from the same payload.
- Each page should include enough sections/states/actions to support review/freeze.
- Keep runtime internals out of home and project-detail unless requirements explicitly demand drill-down.
- Do not mention sqlite/projection/fingerprint/transaction/canonical-envelope/raw runtime log in page copy or layout.

Requirement truth:
{source_context}
""".strip()

    body = {
        "model": provider_model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = request.Request(
        url=f"{api_base}/chat/completions",
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise PrototypeLLMCompileError(f"prototype llm request failed: {exc}") from exc

    choices = payload.get("choices")
    content = ""
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = str(message.get("content", ""))
    parsed = _extract_json_blob(content)
    if not parsed:
        raise PrototypeLLMCompileError("prototype llm response did not contain valid JSON")
    usage = payload.get("usage") if isinstance(payload, dict) else {}
    return {
        "provider_model": provider_model,
        "completion": content,
        "payload": parsed,
        "prompt_tokens": int((usage or {}).get("prompt_tokens", _estimate_tokens(system_prompt + user_prompt))),
        "completion_tokens": int((usage or {}).get("completion_tokens", _estimate_tokens(content))),
    }


def _coerce_string_list(value: Any, *, default: list[str], max_items: int = 8) -> list[str]:
    if isinstance(value, str):
        items = [line.strip() for line in value.splitlines() if line.strip()]
    elif isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
    else:
        items = []
    return items[:max_items] or list(default)


def _coerce_layout_lines(
    value: Any,
    *,
    page_id: str,
    name: str,
    sections: list[str],
    actions: list[dict[str, str]] | None = None,
) -> list[str]:
    if isinstance(value, str):
        lines = [line.rstrip() for line in value.splitlines() if line.strip()]
    elif isinstance(value, list):
        lines = [str(item).rstrip() for item in value if str(item).strip()]
    else:
        lines = []
    if lines:
        return lines[:24]
    return _build_semantic_layout(page_id=page_id, name=name, sections=sections, actions=actions)


def _normalize_action_list(actions: Any) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    if not isinstance(actions, list):
        return normalized
    for item in actions[:8]:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        trigger = str(item.get("trigger") or "").strip() or "点击进入"
        target = str(item.get("target") or "").strip()
        if not label or not target:
            continue
        normalized.append({"label": label, "trigger": trigger, "target": target})
    return normalized


def _normalize_state_list(states: Any) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    if isinstance(states, list):
        for item in states[:8]:
            if not isinstance(item, dict):
                continue
            state_id = slugify_feature(str(item.get("id") or "").strip()).replace("prototype-feature", "state")
            label = str(item.get("label") or state_id).strip()
            description = str(item.get("description") or "").strip() or f"{label} 状态说明待补充。"
            if not state_id:
                continue
            normalized.append(
                {
                    "id": state_id,
                    "label": label,
                    "description": description,
                    "ac_refs": _parse_reference_values(item.get("ac_refs"), pattern=AC_PATTERN),
                    "tc_refs": _parse_reference_values(item.get("tc_refs"), pattern=TC_PATTERN),
                }
            )
    defaults = [
        {"id": "ready", "label": "可用", "description": "页面数据齐备，用户可完成核心操作。", "ac_refs": [], "tc_refs": []},
        {"id": "loading", "label": "加载中", "description": "页面数据正在加载。", "ac_refs": [], "tc_refs": []},
        {"id": "error", "label": "错误", "description": "页面加载或提交失败，需提示恢复动作。", "ac_refs": [], "tc_refs": []},
    ]
    if not normalized:
        return defaults
    existing_ids = {item["id"] for item in normalized}
    for default in defaults:
        if default["id"] not in existing_ids:
            normalized.append(default)
    return normalized[:8]


def _normalize_analysis_payload(page: dict[str, Any]) -> dict[str, Any]:
    analysis = page.get("analysis") if isinstance(page.get("analysis"), dict) else {}
    default_analysis = _default_page_analysis(page)
    return {
        "target_user": str(analysis.get("target_user") or default_analysis["target_user"]).strip(),
        "decision_focus": _coerce_string_list(
            analysis.get("decision_focus"),
            default=default_analysis["decision_focus"],
            max_items=5,
        ),
        "layout_rules": _coerce_string_list(
            analysis.get("layout_rules"),
            default=default_analysis["layout_rules"],
            max_items=4,
        ),
        "noise_guardrail": str(analysis.get("noise_guardrail") or default_analysis["noise_guardrail"]).strip(),
    }


def _assemble_prototype_plan(
    *,
    docs: list[dict[str, Any]],
    version: str,
    feature: str,
    page_specs: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
    theme: dict[str, Any],
    fallback_used: bool,
    parser_mode: str,
    requested_mode: str,
    effective_mode: str,
    generator_mode: str,
    model: str,
    fallback_reason: str,
    capability_snapshot: dict[str, Any],
    semantic_layer: dict[str, Any] | None = None,
    llm_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    route_closure_required = _extract_field(docs, "route_closure_required", "false").lower() == "true"
    requirement_ids = _extract_requirement_ids(docs)
    page_ids = [str(page.get("page_id") or "").strip() for page in page_specs if str(page.get("page_id") or "").strip()]
    required_states = sorted({state["id"] for page in page_specs for state in page["states"]})
    semantic_payload = semantic_layer if isinstance(semantic_layer, dict) else {}
    theme_payload = dict(theme)
    supports_ux_truth = _supports_ux_truth(version, docs)
    design_context = _build_design_context(docs, page_specs, theme_payload) if supports_ux_truth else {}
    design_reasoning = _build_design_reasoning(page_specs, theme_payload) if supports_ux_truth else {}
    ux_contract = _build_ux_contract(page_specs) if supports_ux_truth else {}
    software_semantic_profile = _build_software_semantic_profile(semantic_payload, page_specs) if supports_ux_truth else {}
    return {
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
        "required_pages": page_ids,
        "required_states": required_states,
        "requirement_ids": requirement_ids,
        "page_specs": page_specs,
        "page_inventory": page_specs,
        "navigation": {
            "primary_entry": page_ids[0],
            "primary_exit": transitions[-1]["to"] if transitions else page_ids[-1],
            "transitions": transitions,
        },
        "design_context": design_context,
        "design_reasoning": design_reasoning,
        "ux_contract": ux_contract,
        "software_semantic_profile": software_semantic_profile,
        "semantic_layer": {
            "artifacts": dict(semantic_payload.get("artifacts", {})),
            "default_design_bridge": dict(semantic_payload.get("default_design_bridge", {})),
            "official_language": dict(semantic_payload.get("official_language", {})),
        },
        "platform_variants": _build_platform_variants(page_specs),
        "contract": {
            "prototype_archetype": theme["prototype_archetype"],
            "wireframe_only": True,
            "ux_truth_required": supports_ux_truth,
            "design_governance_required": bool(semantic_payload),
            "semantic_governance_required": bool(semantic_payload),
            "semantic_contract_path": str((semantic_payload.get("artifacts") or {}).get("semantic_contract", "")),
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
                "automation-priority-matrix.md",
                "automation-priority-matrix.json",
                "canonical-envelope.json",
                "pages/*.md",
                "freeze.json",
                "prototype-review.json",
                *(
                    [
                        "ux-prd.md",
                        "DESIGN.md",
                        "preview.html",
                        "preview-dark.html",
                    ]
                    if supports_ux_truth
                    else []
                ),
            ],
        },
        "parser": {
            "page_detection": parser_mode,
            "fallback_used": fallback_used,
            "discovered_page_count": len(page_ids),
            "custom_page_count": len([page_id for page_id in page_ids if page_id not in PAGE_CATALOG]),
            "cjk_detected": any(any(ord(ch) > 127 for ch in doc["text"]) for doc in docs),
            "cjk_parse_failed": False,
        },
        "compiler": {
            **build_mode_contract(
                requested_mode=requested_mode,
                effective_mode=effective_mode,
                fallback_reason=fallback_reason,
                capability_snapshot=capability_snapshot,
            ),
            "model": model,
            "llm_trace": llm_trace or {},
            "downgraded_from_auto": requested_mode == "auto" and bool(fallback_reason),
            "downgrade_blocking": requested_mode == "auto" and bool(fallback_reason) and _semver_tuple(version) >= (1, 3, 9),
        },
        "theme": theme_payload,
    }


def _compile_prototype_plan_rule(
    project_root: Path,
    version: str,
    feature: str,
    docs: list[dict[str, Any]],
    *,
    requested_mode: str,
    model: str,
    fallback_reason: str,
    capability_snapshot: dict[str, Any],
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    page_ids, fallback_used, page_meta = _detect_pages_with_meta(docs)
    if "material-viewer" in page_ids and "material-document-detail" not in page_ids:
        page_ids.append("material-document-detail")
        page_meta["material-document-detail"] = dict(PAGE_CATALOG["material-document-detail"])
    transitions = _build_transition_inventory(page_ids, docs, page_meta)
    page_specs = _build_page_specs(page_ids, docs, transitions, page_meta)
    theme = _build_theme_payload(docs)
    for page in page_specs:
        page["analysis"] = PAGE_ANALYSIS_CATALOG.get(page["page_id"], _default_page_analysis(page))
        page["layout_lines"] = _build_page_layout(page["page_id"], page.get("sections"))
    return _assemble_prototype_plan(
        docs=docs,
        version=version,
        feature=feature,
        page_specs=page_specs,
        transitions=transitions,
        theme=theme,
        fallback_used=fallback_used,
        parser_mode="requirement-driven-parser",
        requested_mode=requested_mode,
        effective_mode="rule",
        generator_mode="rule",
        model=model,
        fallback_reason=fallback_reason,
        capability_snapshot=capability_snapshot,
        semantic_layer=semantic_layer,
    )


def _prototype_inference_payload(inference: dict[str, Any]) -> dict[str, Any]:
    payload = inference.get("payload")
    if isinstance(payload, dict):
        return payload
    prototype_payload = inference.get("prototype")
    if isinstance(prototype_payload, dict):
        return prototype_payload
    return inference if isinstance(inference, dict) else {}


def _compile_prototype_plan_from_inference(
    *,
    version: str,
    feature: str,
    docs: list[dict[str, Any]],
    inference: dict[str, Any],
    requested_mode: str,
    effective_mode: str,
    model: str,
    capability_snapshot: dict[str, Any],
    inference_mode: str,
    parser_mode: str,
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _prototype_inference_payload(inference)
    raw_pages = payload.get("pages")
    if not isinstance(raw_pages, list) or not raw_pages:
        raise PrototypeLLMCompileError("prototype llm payload missing pages")

    normalized_pages: list[dict[str, Any]] = []
    page_aliases: dict[str, str] = {}
    seen_page_ids: set[str] = set()
    for index, raw_page in enumerate(raw_pages, start=1):
        if not isinstance(raw_page, dict):
            continue
        raw_name = str(raw_page.get("name") or "").strip()
        raw_page_id = str(raw_page.get("page_id") or "").strip()
        candidate_id = raw_page_id or _known_page_id_for_text(raw_name) or _slugify_page_id(raw_name, ordinal=index)
        page_id = candidate_id
        suffix = 2
        while page_id in seen_page_ids:
            page_id = f"{candidate_id}-{suffix:02d}"
            suffix += 1
        seen_page_ids.add(page_id)
        name = raw_name or PAGE_CATALOG.get(page_id, {}).get("name") or page_id.replace("-", " ").title()
        sections = _coerce_string_list(
            raw_page.get("sections"),
            default=_infer_llm_sections(page_id, name),
            max_items=8,
        )
        actions = _normalize_action_list(raw_page.get("actions"))
        page = {
            "page_id": page_id,
            "name": name,
            "priority": _normalize_priority(raw_page.get("priority")),
            "platforms": _normalize_platforms(
                raw_page.get("platforms"),
                default=list((PAGE_CATALOG.get(page_id) or {}).get("platforms") or ["Web", "PC"]),
            ),
            "responsibility": str(
                raw_page.get("responsibility")
                or _default_llm_responsibility(name, sections)
            ).strip(),
            "sections": sections,
            "actions": actions,
            "states": _normalize_state_list(raw_page.get("states")),
            "layout_lines": _coerce_layout_lines(
                raw_page.get("layout"),
                page_id=page_id,
                name=name,
                sections=sections,
                actions=actions,
            ),
            "requirement_refs": _build_requirement_refs(docs),
            "outbound_transitions": [],
        }
        page["analysis"] = _normalize_analysis_payload(
            {
                **page,
                "analysis": raw_page.get("analysis"),
            }
        )
        page["visible_contract"] = _build_visible_contract(page)
        page["internal_governance"] = _build_internal_governance(page)
        for state in page["states"]:
            state["state_visibility_contract"] = _build_state_visibility_contract(page, state)
        normalized_pages.append(page)
        page_aliases[page_id.lower()] = page_id
        page_aliases[name.lower()] = page_id

    transitions: list[dict[str, Any]] = []
    raw_transitions = payload.get("transitions") if isinstance(payload.get("transitions"), list) else []
    for raw_transition in raw_transitions[:24]:
        if not isinstance(raw_transition, dict):
            continue
        source = page_aliases.get(str(raw_transition.get("from") or "").strip().lower(), "")
        target = page_aliases.get(str(raw_transition.get("to") or "").strip().lower(), "")
        if not source or not target:
            continue
        transitions.append(
            {
                "from": source,
                "to": target,
                "trigger": str(raw_transition.get("trigger") or "点击进入").strip(),
                "type": str(raw_transition.get("type") or "primary").strip(),
            }
        )
    if not transitions:
        for page in normalized_pages:
            for action in page["actions"]:
                target = page_aliases.get(str(action.get("target") or "").strip().lower(), "")
                if not target:
                    continue
                transition_type = "return" if "返回" in str(action.get("label") or "") or "返回" in str(action.get("trigger") or "") else "primary"
                if target == page["page_id"]:
                    transition_type = "stay"
                elif target not in {"home", "management-overview"} and transition_type != "return":
                    transition_type = "drill-down"
                transitions.append(
                    {
                        "from": page["page_id"],
                        "to": target,
                        "trigger": str(action.get("trigger") or "点击进入").strip(),
                        "type": transition_type,
                    }
                )
    deduped_transitions: list[dict[str, Any]] = []
    seen_transition_keys: set[tuple[str, str, str, str]] = set()
    for transition in transitions:
        source = str(transition.get("from") or "").strip()
        target = str(transition.get("to") or "").strip()
        trigger = str(transition.get("trigger") or "").strip() or "点击进入"
        tp = str(transition.get("type") or "").strip() or "primary"
        if not source or not target:
            continue
        key = (source, target, trigger, tp)
        if key in seen_transition_keys:
            continue
        seen_transition_keys.add(key)
        deduped_transitions.append({"from": source, "to": target, "trigger": trigger, "type": tp})
    transitions = deduped_transitions
    outbound: dict[str, list[dict[str, Any]]] = {}
    for transition in transitions:
        outbound.setdefault(transition["from"], []).append(transition)
    for page in normalized_pages:
        resolved_actions: list[dict[str, str]] = []
        for action in page["actions"]:
            target = page_aliases.get(str(action.get("target") or "").strip().lower(), "")
            if not target:
                continue
            resolved_actions.append(
                {
                    "label": str(action.get("label") or "").strip(),
                    "trigger": str(action.get("trigger") or "点击进入").strip(),
                    "target": target,
                }
            )
        page["actions"] = resolved_actions or [
            {
                "label": f"进入{next((item['name'] for item in normalized_pages if item['page_id'] == transition['to']), transition['to'])}",
                "trigger": transition["trigger"],
                "target": transition["to"],
            }
            for transition in outbound.get(page["page_id"], [])
        ]
        page["outbound_transitions"] = outbound.get(page["page_id"], [])

    if not normalized_pages:
        raise PrototypeLLMCompileError("prototype llm payload did not yield valid pages")

    contract_issues = _validate_llm_page_contract(page_specs=normalized_pages, transitions=transitions)
    if contract_issues:
        raise PrototypeLLMContractError("; ".join(contract_issues[:8]))

    llm_theme = payload.get("theme") if isinstance(payload.get("theme"), dict) else {}
    base_theme = _build_theme_payload(docs)
    theme = {
        **base_theme,
        "prototype_archetype": str(payload.get("prototype_archetype") or llm_theme.get("prototype_archetype") or base_theme["prototype_archetype"]).strip(),
        "primary": str(llm_theme.get("primary") or base_theme["primary"]).strip(),
        "secondary": str(llm_theme.get("secondary") or base_theme["secondary"]).strip(),
    }
    llm_trace = {
        "inference_mode": inference_mode,
        "provider_model": str(inference.get("provider_model") or inference.get("model") or ""),
        "prompt_tokens": int(inference.get("prompt_tokens") or 0),
        "completion_tokens": int(inference.get("completion_tokens") or 0),
        "validated_page_count": len(normalized_pages),
        "validated_transition_count": len(transitions),
    }
    if inference_mode.startswith("host"):
        llm_trace["host_runtime"] = str(capability_snapshot.get("host_runtime") or "")
        llm_trace["host_response_source"] = str(capability_snapshot.get("host_response_source") or "")
        llm_trace["host_transport"] = str(capability_snapshot.get("host_transport") or "")
    return _assemble_prototype_plan(
        docs=docs,
        version=version,
        feature=feature,
        page_specs=normalized_pages,
        transitions=transitions,
        theme=theme,
        fallback_used=False,
        parser_mode=parser_mode,
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        generator_mode=effective_mode,
        model=model,
        fallback_reason="",
        capability_snapshot=capability_snapshot,
        semantic_layer=semantic_layer,
        llm_trace=llm_trace,
    )


def _compile_prototype_plan_llm(
    *,
    version: str,
    feature: str,
    docs: list[dict[str, Any]],
    requested_mode: str,
    model: str,
    capability_snapshot: dict[str, Any],
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inference = _real_prototype_llm_inference(
        feature=feature,
        version=version,
        docs=docs,
        model=model,
        semantic_layer=semantic_layer,
    )
    return _compile_prototype_plan_from_inference(
        version=version,
        feature=feature,
        docs=docs,
        inference=inference,
        requested_mode=requested_mode,
        effective_mode="llm",
        model=model,
        capability_snapshot=capability_snapshot,
        inference_mode="real",
        parser_mode="llm-wireframe-compiler",
        semantic_layer=semantic_layer,
    )


def _compile_prototype_plan_host(
    *,
    version: str,
    feature: str,
    docs: list[dict[str, Any]],
    requested_mode: str,
    model: str,
    capability_snapshot: dict[str, Any],
    semantic_layer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inference = {}
    inference_mode = "host-bridge"
    parser_mode = "host-wireframe-compiler"
    bridge_request = _build_prototype_host_bridge_request(
        feature=feature,
        version=version,
        docs=docs,
        model=model,
        semantic_layer=semantic_layer,
    )
    inference, _ = execute_host_bridge_command("prototype", bridge_request)
    if not inference:
        inference, _ = load_host_response_json("prototype")
    if not inference:
        if not bool(capability_snapshot.get("provider_available")):
            raise PrototypeLLMCompileError("prototype host response missing or provider-backed host compile unavailable")
        inference = _real_prototype_llm_inference(
            feature=feature,
            version=version,
            docs=docs,
            model=model,
            semantic_layer=semantic_layer,
        )
        inference_mode = "host-provider"
        parser_mode = "host-provider-wireframe-compiler"
    return _compile_prototype_plan_from_inference(
        version=version,
        feature=feature,
        docs=docs,
        inference=inference,
        requested_mode=requested_mode,
        effective_mode="host",
        model=model,
        capability_snapshot=capability_snapshot,
        inference_mode=inference_mode,
        parser_mode=parser_mode,
        semantic_layer=semantic_layer,
    )


def compile_prototype_plan(
    project_root: Path,
    version: str,
    feature: str,
    *,
    mode: str = "auto",
    model: str = "beacon-prototype-compiler",
) -> dict[str, Any]:
    docs = load_source_documents(project_root, version, feature)
    doc_by_type = {doc["type"]: doc for doc in docs}
    missing = [doc_type for doc_type in REQUIRED_SOURCE_TYPES if doc_type not in doc_by_type]
    if missing:
        raise FileNotFoundError(
            f"prototype requires requirement truth before wireframe freeze, missing: {', '.join(missing)}"
        )
    requested_mode = normalize_requested_mode(mode)
    capability_snapshot = build_semantic_capability_snapshot(
        "prototype",
        disable_env="BEACON_PROTOTYPE_DISABLE_LLM",
    )
    semantic_layer = load_or_build_semantic_layer(
        project_root,
        version=version,
        feature=feature,
        stage="prototype",
        capability_snapshot=capability_snapshot,
    )
    if requested_mode == "rule":
        return _compile_prototype_plan_rule(
            project_root,
            version,
            feature,
            docs,
            requested_mode=requested_mode,
            model=model,
            fallback_reason="",
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )
    if bool(capability_snapshot.get("llm_disabled")):
        if requested_mode == "llm":
            raise ValueError("Prototype LLM compile disabled by BEACON_PROTOTYPE_DISABLE_LLM.")
        return _compile_prototype_plan_rule(
            project_root,
            version,
            feature,
            docs,
            requested_mode=requested_mode,
            model=model,
            fallback_reason="llm_disabled",
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )
    if bool(capability_snapshot.get("host_semantic_ready")):
        try:
            return _compile_prototype_plan_host(
                version=version,
                feature=feature,
                docs=docs,
                requested_mode=requested_mode,
                model=model,
                capability_snapshot=capability_snapshot,
                semantic_layer=semantic_layer,
            )
        except PrototypeLLMContractError as exc:
            if not bool(capability_snapshot.get("provider_available")):
                if requested_mode == "llm":
                    raise ValueError(f"Prototype LLM compile failed: {exc}") from exc
                return _compile_prototype_plan_rule(
                    project_root,
                    version,
                    feature,
                    docs,
                    requested_mode=requested_mode,
                    model=model,
                    fallback_reason="host_contract_validation_failed",
                    capability_snapshot=capability_snapshot,
                    semantic_layer=semantic_layer,
                )
        except Exception as exc:  # noqa: BLE001
            if not bool(capability_snapshot.get("provider_available")):
                if requested_mode == "llm":
                    raise ValueError(f"Prototype LLM compile failed: {exc}") from exc
                return _compile_prototype_plan_rule(
                    project_root,
                    version,
                    feature,
                    docs,
                    requested_mode=requested_mode,
                    model=model,
                    fallback_reason="host_compile_failed",
                    capability_snapshot=capability_snapshot,
                    semantic_layer=semantic_layer,
                )
    if not bool(capability_snapshot.get("provider_available")):
        if requested_mode == "llm":
            raise ValueError(llm_unavailable_message("Prototype LLM compile"))
        return _compile_prototype_plan_rule(
            project_root,
            version,
            feature,
            docs,
            requested_mode=requested_mode,
            model=model,
            fallback_reason="llm_unavailable",
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )
    try:
        return _compile_prototype_plan_llm(
            version=version,
            feature=feature,
            docs=docs,
            requested_mode=requested_mode,
            model=model,
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )
    except PrototypeLLMContractError as exc:
        if requested_mode == "llm":
            raise ValueError(f"Prototype LLM compile failed: {exc}") from exc
        return _compile_prototype_plan_rule(
            project_root,
            version,
            feature,
            docs,
            requested_mode=requested_mode,
            model=model,
            fallback_reason="llm_contract_validation_failed",
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )
    except Exception as exc:  # noqa: BLE001
        if requested_mode == "llm":
            raise ValueError(f"Prototype LLM compile failed: {exc}") from exc
        return _compile_prototype_plan_rule(
            project_root,
            version,
            feature,
            docs,
            requested_mode=requested_mode,
            model=model,
            fallback_reason="llm_compile_failed",
            capability_snapshot=capability_snapshot,
            semantic_layer=semantic_layer,
        )


def write_prototype_plan(
    project_root: Path,
    version: str,
    feature: str,
    *,
    mode: str = "auto",
    model: str = "beacon-prototype-compiler",
) -> dict[str, Any]:
    plan = compile_prototype_plan(project_root, version, feature, mode=mode, model=model)
    files = prototype_files(project_root, version, feature)
    _write_json(files["prototype_plan"], plan)
    return {"path": files["prototype_plan"], "plan": plan}


def write_prototype_bundle(
    project_root: Path,
    version: str,
    feature: str,
    *,
    mode: str = "auto",
    model: str = "beacon-prototype-compiler",
) -> dict[str, Any]:
    source_docs = load_source_documents(project_root, version, feature)
    plan = compile_prototype_plan(project_root, version, feature, mode=mode, model=model)
    files = prototype_files(project_root, version, feature)
    feature_slug = str(plan["feature_slug"])
    semantic_layer = plan.get("semantic_layer", {}) if isinstance(plan.get("semantic_layer"), dict) else {}
    design_context = plan.get("design_context", {}) if isinstance(plan.get("design_context"), dict) else {}
    design_reasoning = plan.get("design_reasoning", {}) if isinstance(plan.get("design_reasoning"), dict) else {}
    ux_contract = plan.get("ux_contract", {}) if isinstance(plan.get("ux_contract"), dict) else {}
    supports_ux_truth = _supports_ux_truth(version, source_docs)
    source_hash = _stable_hash([{"type": doc["type"], "fingerprint": doc["fingerprint"]} for doc in source_docs])
    projection_seq = f"pp-{source_hash[:16]}"
    committed_at = now_iso()
    transaction_id = f"tx-{feature_slug}-{projection_seq}"

    theme_payload = plan["theme"]
    design_artifacts = _build_design_artifacts(plan) if supports_ux_truth else {}
    production_copy_by_page = {
        str(item.get("page_id") or "").strip(): item
        for item in ((design_artifacts.get("production-ui-copy-profile.json") or {}).get("pages") or [])
        if isinstance(item, dict)
    }
    ui_copy_policy_by_page = {
        str(item.get("page_id") or "").strip(): item
        for item in ((design_artifacts.get("ui-copy-policy.json") or {}).get("pages") or [])
        if isinstance(item, dict)
    }
    for page in plan["page_specs"]:
        if not isinstance(page, dict):
            continue
        page_id = str(page.get("page_id") or "").strip()
        page["production_ui_copy_profile"] = production_copy_by_page.get(page_id, {})
        page["ui_copy_policy"] = ui_copy_policy_by_page.get(page_id, {})
    transitions = plan["navigation"]["transitions"]
    requirement_ids = plan.get("requirement_ids") if isinstance(plan.get("requirement_ids"), dict) else {}
    interaction_map = _build_interaction_map(plan["page_specs"], transitions)
    state_flow_map = _build_state_flow_map(plan["page_specs"], transitions, requirement_ids)
    component_catalog = _build_component_catalog(plan["page_specs"], requirement_ids)
    cross_page_transition_contracts = [
        edge for edge in (state_flow_map.get("edges") or []) if isinstance(edge, dict) and str(edge.get("kind") or "") == "cross-page-transition"
    ]
    automation_priority_matrix = _build_automation_priority_matrix(
        plan["page_specs"],
        state_flow_map,
        component_catalog,
        design_reasoning,
    )
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
        "component_state_contracts": component_catalog.get("components", []),
        "cross_page_transition_contracts": cross_page_transition_contracts,
        "automation_priority_matrix": automation_priority_matrix,
        "route_closure_contract": route_closure,
        "coverage_report": coverage,
        "source_map": source_map,
        "design_context": design_context,
        "design_reasoning": design_reasoning,
        "ux_contract": ux_contract,
        "semantic_layer": semantic_layer,
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
        stage_files["design_artifacts_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["human_view_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["machine_view_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["verification_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["assets_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["implementation_dir"].mkdir(parents=True, exist_ok=True)
        stage_files["theme"].parent.mkdir(parents=True, exist_ok=True)

        _write_json(stage_files["prototype_plan"], plan)
        _write_json(stage_files["canonical_envelope"], canonical_envelope)
        _write_text(stage_files["wireframe_summary"], _render_wireframe_summary(plan))
        if supports_ux_truth:
            _write_text(stage_files["ux_prd"], _render_ux_prd_md(plan))
            _write_text(stage_files["design_md"], _render_design_md(plan, theme_payload))
            _write_text(stage_files["preview_html"], _render_preview_html(plan, theme_payload, dark=False))
            _write_text(stage_files["preview_dark_html"], _render_preview_html(plan, theme_payload, dark=True))
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
        _write_json(stage_files["automation_priority_matrix"], automation_priority_matrix)
        _write_text(
            stage_files["automation_priority_matrix_md"],
            _render_automation_priority_matrix_md(feature, automation_priority_matrix),
        )
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
                "default_consumption_entry": {
                    "surface": "implementation-default",
                    "mode": "fail-closed",
                    "allowed_inputs": _allowed_implementation_input_paths(supports_ux_truth=supports_ux_truth),
                    "blocked_human_inputs": _review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth),
                },
            },
        )
        _write_json(
            stage_files["artifact_topology"],
            {
                "schema_version": SCHEMA_VERSION,
                "feature": feature,
                "feature_slug": feature_slug,
                "version": version,
                "prototype_mode": PROTOTYPE_MODE,
                "generated_at": now_iso(),
                "layers": {
                    "authoring": [
                        "prototype-plan.json",
                        "canonical-envelope.json",
                        "manifest.json",
                        "source-map.json",
                    ],
                    "review": _review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth)
                    + [
                        "wireframe-summary.md",
                        "navigation-map.md",
                        "state-flow-map.md",
                        "component-catalog.md",
                        "automation-priority-matrix.md",
                        "verification/index.json",
                    ],
                    "projection": [
                        "page-specs/*.json",
                        "design-artifacts/ui-copy-policy.json",
                        "design-artifacts/production-ui-copy-profile.json",
                        "preview.html" if supports_ux_truth else "",
                        "preview-dark.html" if supports_ux_truth else "",
                    ],
                    "implementation": [
                        "machine-view/index.json",
                        "implementation/index.json",
                        "implementation-map.json",
                        *[item for item in _allowed_implementation_input_paths(supports_ux_truth=supports_ux_truth) if item != "implementation/index.json"],
                    ],
                },
                "default_execution_surface": "implementation",
                "review_only_surface": "review",
            },
        )
        _write_json(
            stage_files["prototype_brief"],
            {
                "prototype_mode": PROTOTYPE_MODE,
                "theme": theme_payload,
                "page_count": len(plan["page_specs"]),
                "design_context": design_context,
                "design_reasoning": design_reasoning,
                "ux_contract": ux_contract,
                "design_assets": {
                    "ux_prd": "ux-prd.md" if supports_ux_truth else "",
                    "design_md": "DESIGN.md" if supports_ux_truth else "",
                    "preview_html": "preview.html" if supports_ux_truth else "",
                    "preview_dark_html": "preview-dark.html" if supports_ux_truth else "",
                },
            },
        )
        _write_json(stage_files["theme"], theme_payload)
        _write_json(stage_files["platform_variants"], plan["platform_variants"])
        for artifact_name, artifact_payload in design_artifacts.items():
            _write_json(stage_files["design_artifacts_dir"] / artifact_name, artifact_payload)
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
            _write_json(stage_files["page_specs_dir"] / f"{page['page_id']}.json", _serialize_page_spec(page))
        _write_json(stage_files["source_map"], source_map)

        _write_json(
            stage_files["human_view_dir"] / "index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "surface": "human-review",
                "review_only": True,
                "files": _human_view_files() + (["ux-prd.md"] if supports_ux_truth else []),
            },
        )
        _write_json(
            stage_files["machine_view_dir"] / "index.json",
            {
                "schema_version": SCHEMA_VERSION,
                "surface": "implementation-readable",
                "files": [
                    "canonical-envelope.json",
                    "prototype-plan.json",
                    "wireframe-manifest.json",
                    "navigation-map.json",
                    "state-flow-map.json",
                    "component-catalog.json",
                    "automation-priority-matrix.json",
                    "interaction-map.json",
                    "coverage-report.json",
                    "source-map.json",
                    "route-closure-contract.json",
                    "design-artifacts/design-context.json",
                    "design-artifacts/surface-profile.json",
                    "design-artifacts/layout-pattern.json",
                    "design-artifacts/component-state-matrix.json",
                    "design-artifacts/ui-copy-policy.json",
                    "design-artifacts/production-ui-copy-profile.json",
                    "design-artifacts/style-preset.json",
                    "design-artifacts/design-review.json",
                    "design-artifacts/design-lint-rules.json",
                    str((semantic_layer.get("artifacts") or {}).get("semantic_contract", "")),
                ],
            },
        )
        _write_json(
            stage_files["verification_index"],
            {
                "schema_version": SCHEMA_VERSION,
                "surface": "review-only",
                "review_only": True,
                "files": [
                    "prototype-review.json",
                    "prototype-review.md",
                    *_review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth),
                ],
            },
        )
        _write_json(
            stage_files["implementation_index"],
            {
                "schema_version": SCHEMA_VERSION,
                "surface": "implementation-default",
                "mode": "fail-closed",
                "allowed_inputs": _allowed_implementation_input_paths(supports_ux_truth=supports_ux_truth),
                "blocked_human_inputs": _review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth),
            },
        )

        machine_fingerprints = {}
        human_fingerprints = {}
        for path in sorted(stage_files["root"].rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(stage_files["root"]))
            fingerprint = sha256_file(path)
            if rel.endswith(".md") or rel.endswith(".css") or rel.endswith(".html"):
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
            "compiler": plan.get("compiler", {}),
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
                "automation_priority_matrix": str(files["automation_priority_matrix"].relative_to(project_root)),
                "automation_priority_matrix_md": str(files["automation_priority_matrix_md"].relative_to(project_root)),
                "interaction_map": str(files["interaction_map"].relative_to(project_root)),
                "coverage_report": str(files["coverage_report"].relative_to(project_root)),
                "route_closure_contract": str(files["route_closure_contract"].relative_to(project_root)),
                "implementation_map": str(files["implementation_map"].relative_to(project_root)),
                "canonical_envelope": str(files["canonical_envelope"].relative_to(project_root)),
                "source_map": str(files["source_map"].relative_to(project_root)),
                "pages_dir": str(files["pages_dir"].relative_to(project_root)),
                "page_specs_dir": str(files["page_specs_dir"].relative_to(project_root)),
                "design_artifacts_dir": str(files["design_artifacts_dir"].relative_to(project_root)),
                "human_view_dir": str(files["human_view_dir"].relative_to(project_root)),
                "machine_view_dir": str(files["machine_view_dir"].relative_to(project_root)),
                "theme": str(files["theme"].relative_to(project_root)),
                "tokens_css": str(files["tokens_css"].relative_to(project_root)),
                "platform_variants": str(files["platform_variants"].relative_to(project_root)),
                "ux_prd": str(files["ux_prd"].relative_to(project_root)),
                "design_md": str(files["design_md"].relative_to(project_root)),
                "preview_html": str(files["preview_html"].relative_to(project_root)),
                "preview_dark_html": str(files["preview_dark_html"].relative_to(project_root)),
                "freeze": str(files["freeze"].relative_to(project_root)),
                "semantic_contract": str((semantic_layer.get("artifacts") or {}).get("semantic_contract", "")),
                "semantic_dictionary": str((semantic_layer.get("artifacts") or {}).get("semantic_dictionary", "")),
                "semantic_usage_guidelines": str((semantic_layer.get("artifacts") or {}).get("semantic_usage_guidelines", "")),
                "semantic_review": str((semantic_layer.get("artifacts") or {}).get("semantic_review", "")),
            },
            "design_context": design_context,
            "design_reasoning": design_reasoning,
            "ux_contract": ux_contract,
            "semantic_layer": semantic_layer,
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
            "semantic_layer": semantic_layer,
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
        "semantic_layer": semantic_layer,
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
    automation_priority_matrix = _read_json(files["automation_priority_matrix"])
    route_closure = _read_json(files["route_closure_contract"])
    implementation_map = _read_json(files["implementation_map"])
    artifact_topology = _read_json(files["artifact_topology"])
    implementation_index = _read_json(files["implementation_index"])
    verification_index = _read_json(files["verification_index"])
    canonical_truth = _load_prototype_canonical_truth(
        files,
        plan=plan,
        manifest=manifest,
        canonical_envelope=canonical_envelope,
    )
    page_specs = plan.get("page_specs") if isinstance(plan.get("page_specs"), list) else []
    required_pages = [str(item).strip() for item in (plan.get("required_pages") or []) if str(item).strip()]
    required_states = [str(item).strip() for item in (plan.get("required_states") or []) if str(item).strip()]
    source_docs = load_source_documents(project_root, version, feature)
    forbidden_page_ids = _collect_forbidden_page_ids(source_docs)
    transaction = manifest.get("transaction") if isinstance(manifest.get("transaction"), dict) else {}
    transaction_id = str(transaction.get("transaction_id") or "")
    sqlite_projection = _read_prototype_projection_sqlite(transaction_id)
    supports_ux_truth = _supports_ux_truth(version, source_docs)
    design_context = canonical_truth.get("design_context") if isinstance(canonical_truth.get("design_context"), dict) else {}
    design_reasoning = canonical_truth.get("design_reasoning") if isinstance(canonical_truth.get("design_reasoning"), dict) else {}
    ux_contract = canonical_truth.get("ux_contract") if isinstance(canonical_truth.get("ux_contract"), dict) else {}
    plan = _apply_canonical_truth_to_plan(plan, canonical_truth=canonical_truth)
    governed_rendering_enforced = _semver_tuple(version) >= (1, 3, 11)

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
            "automation_priority_matrix_present",
            "pass" if files["automation_priority_matrix"].exists() and files["automation_priority_matrix_md"].exists() else "fail",
            "automation-priority-matrix.md/json should exist",
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

    missing_pages = [page_id for page_id in required_pages if not _has_named_artifact(files["pages_dir"], page_id, ".md")]
    checks.append(
        _review_check(
            "required_pages_materialized",
            "pass" if not missing_pages else "fail",
            "all required page markdown files should exist" if not missing_pages else f"missing page files: {missing_pages}",
        )
    )
    forbidden_pages_present = [page_id for page_id in required_pages if page_id in forbidden_page_ids]
    checks.append(
        _review_check(
            "forbidden_page_inventory_clear",
            "pass" if not forbidden_pages_present else "fail",
            "required page inventory excludes forbidden pages"
            if not forbidden_pages_present
            else f"forbidden pages detected in required inventory: {forbidden_pages_present}",
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
    topology_layers = artifact_topology.get("layers") if isinstance(artifact_topology.get("layers"), dict) else {}
    checks.append(
        _review_check(
            "artifact_topology_present",
            "pass"
            if all(layer in topology_layers for layer in ("authoring", "review", "projection", "implementation"))
            else "fail",
            "artifact-topology.json must declare authoring/review/projection/implementation layers",
        )
    )
    impl_allowed_inputs = implementation_index.get("allowed_inputs") if isinstance(implementation_index.get("allowed_inputs"), list) else []
    blocked_human_inputs = implementation_index.get("blocked_human_inputs") if isinstance(implementation_index.get("blocked_human_inputs"), list) else []
    checks.append(
        _review_check(
            "implementation_default_entry_present",
            "pass"
            if impl_allowed_inputs
            and "machine-view/index.json" in impl_allowed_inputs
            and "implementation-map.json" in impl_allowed_inputs
            else "fail",
            "implementation index must expose a fail-closed default entry rooted in machine-view and implementation-map",
        )
    )
    checks.append(
        _review_check(
            "review_only_materials_demoted",
            "pass"
            if verification_index.get("review_only") is True
            and all(item in blocked_human_inputs for item in _review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth))
            and all(item not in impl_allowed_inputs for item in _review_only_human_artifact_paths(supports_ux_truth=supports_ux_truth))
            else "fail",
            "review-only human-readable materials must be demoted out of the default implementation surface",
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
        if not component.get("state_feedback_responsibilities"):
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
    cross_page_transition_items = [
        edge for edge in state_edges if isinstance(edge, dict) and str(edge.get("kind") or "") == "cross-page-transition"
    ]
    missing_transition_contracts = []
    for edge in cross_page_transition_items:
        required_keys = ("from_page", "from_state", "to_page", "to_state", "event", "guard", "fallback", "route_or_runtime_evidence")
        if not all(edge.get(key) for key in required_keys):
            missing_transition_contracts.append(f"{edge.get('from')}->{edge.get('to')}")
            continue
        if require_ac_refs and not edge.get("ac_refs"):
            missing_transition_contracts.append(f"{edge.get('from')}->{edge.get('to')}")
            continue
        if require_tc_refs and not edge.get("test_refs"):
            missing_transition_contracts.append(f"{edge.get('from')}->{edge.get('to')}")
    checks.append(
        _review_check(
            "cross_page_transition_contract_complete",
            "pass" if cross_page_transition_items and not missing_transition_contracts else "fail",
            "cross-page business transitions should expose explicit state/event/fallback/evidence contracts"
            if cross_page_transition_items and not missing_transition_contracts
            else f"missing cross-page transition contracts: {missing_transition_contracts[:10]}",
        )
    )
    priority_entries = automation_priority_matrix.get("entries") if isinstance(automation_priority_matrix.get("entries"), list) else []
    priority_classes = {str(item.get("priority_class") or "") for item in priority_entries if isinstance(item, dict)}
    checks.append(
        _review_check(
            "automation_priority_matrix_complete",
            "pass"
            if priority_entries
            and all(str(item.get("priority_class") or "").strip() for item in priority_entries if isinstance(item, dict))
            and priority_classes <= {"release-blocker", "primary-automation", "smoke-only", "manual-acceptable"}
            else "fail",
            "automation priority matrix should assign valid priority classes to generated targets",
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
    if supports_ux_truth:
        explicit_fields = list(design_context.get("explicit_context_fields") or [])
        required_context_fields = [
            "target_audience",
            "primary_use_cases",
            "operator_mental_state",
            "usage_environment",
            "brand_tone",
            "density_preference",
        ]
        missing_context_fields = [
            field
            for field in required_context_fields
            if not design_context.get(field)
        ]
        checks.extend(
            [
                _review_check(
                    "design_context_complete",
                    "pass" if not missing_context_fields else "fail",
                    "design context must include all required fields"
                    if not missing_context_fields
                    else f"missing design context fields: {missing_context_fields}",
                ),
                _review_check(
                    "design_context_explicit",
                    "pass" if bool(design_context.get("explicit_context_complete")) else "fail",
                    "design context is explicitly frozen in requirement truth"
                    if bool(design_context.get("explicit_context_complete"))
                    else f"explicit design context incomplete: {explicit_fields}",
                ),
                _review_check(
                    "design_reasoning_complete",
                    "pass"
                    if all(
                        design_reasoning.get(key)
                        for key in (
                            "product_surface_type",
                            "interaction_model",
                            "recommended_layout_pattern",
                            "visual_priority_rules",
                            "anti_patterns",
                            "design_checklist",
                        )
                    )
                    else "fail",
                    "design reasoning must freeze layout logic, anti-patterns, and review checklist",
                ),
                _review_check(
                    "ux_contract_complete",
                    "pass"
                    if all(
                        ux_contract.get(key)
                        for key in (
                            "first_glance_question",
                            "primary_decision",
                            "action_hierarchy",
                            "recognition_over_recall_rules",
                            "error_recovery_policy",
                            "allowed_machine_noise",
                            "forbidden_machine_noise",
                        )
                    )
                    else "fail",
                    "ux contract must freeze first glance, decision, action hierarchy, and machine-noise boundary",
                ),
                _review_check(
                    "ux_prd_present",
                    "pass" if files["ux_prd"].exists() else "fail",
                    "ux-prd.md should exist",
                ),
                _review_check(
                    "design_assets_present",
                    "pass"
                    if files["design_md"].exists() and files["preview_html"].exists() and files["preview_dark_html"].exists()
                    else "fail",
                    "DESIGN.md and preview assets should exist",
                ),
                _review_check(
                    "default_design_preset_stable",
                    "pass"
                    if str((plan.get("theme") or {}).get("design_preset") or "") == "apple-inspired-design-md"
                    or bool((plan.get("theme") or {}).get("design_preset_override_reason"))
                    else "fail",
                    "design preset must default to apple-inspired-design-md or record an explicit override reason",
                ),
                _review_check(
                    "semantic_profile_complete",
                    "pass"
                    if all(
                        (plan.get("software_semantic_profile") or {}).get(key)
                        for key in ("title_rule", "state_rule", "action_rule", "exception_rule")
                    )
                    else "fail",
                    "software semantic profile must freeze title, state, action, and exception rules",
                ),
                _review_check(
                    "design_artifacts_present",
                    "pass"
                    if not governed_rendering_enforced
                    or all(
                        (files["design_artifacts_dir"] / name).exists()
                        for name in (
                            "design-context.json",
                            "surface-profile.json",
                            "layout-pattern.json",
                            "component-state-matrix.json",
                            "ui-copy-policy.json",
                            "production-ui-copy-profile.json",
                            "style-preset.json",
                            "design-review.json",
                            "design-lint-rules.json",
                        )
                    )
                    else "fail",
                    "design artifact contract should emit the required structured artifacts",
                    blocking=governed_rendering_enforced,
                ),
            ]
        )
        page_intent_missing = []
        visible_contract_missing = []
        state_contract_missing = []
        production_copy_missing = []
        for page in page_specs:
            if not isinstance(page, dict):
                continue
            visible_contract = page.get("visible_contract") if isinstance(page.get("visible_contract"), dict) else {}
            governance = page.get("internal_governance") if isinstance(page.get("internal_governance"), dict) else {}
            intent = governance.get("page_intent_contract") if isinstance(governance.get("page_intent_contract"), dict) else {}
            first_screen = governance.get("first_screen_contract") if isinstance(governance.get("first_screen_contract"), dict) else {}
            copy_profile = page.get("production_ui_copy_profile") if isinstance(page.get("production_ui_copy_profile"), dict) else {}
            if not all(
                visible_contract.get(key)
                for key in (
                    "title",
                    "subtitle",
                    "must_show_sections",
                    "primary_actions",
                    "visible_states",
                )
            ):
                visible_contract_missing.append(str(page.get("page_id") or "unknown"))
            if not all(
                intent.get(key)
                for key in (
                    "why_this_page_exists",
                    "decision_supported",
                    "must_show_first",
                    "must_not_show",
                    "entry_conditions",
                    "exit_actions",
                )
            ) or not all(first_screen.get(key) for key in ("primary_status", "primary_blocker", "next_actions", "recovery_path")):
                page_intent_missing.append(str(page.get("page_id") or "unknown"))
            if not copy_profile.get("title") or not copy_profile.get("subtitle") or not list(copy_profile.get("primary_actions") or []):
                production_copy_missing.append(str(page.get("page_id") or "unknown"))
            for state in page.get("states", []):
                if not isinstance(state, dict):
                    continue
                contract = state.get("state_visibility_contract") if isinstance(state.get("state_visibility_contract"), dict) else {}
                if not all(
                    contract.get(key)
                    for key in (
                        "user_question",
                        "required_feedback",
                        "recovery_actions",
                        "forbidden_feedback",
                    )
                ):
                    state_contract_missing.append(f"{page.get('page_id')}:{state.get('id')}")
        checks.extend(
            [
                _review_check(
                    "visible_contract_complete",
                    "pass" if not visible_contract_missing else "fail",
                    "every page exposes a visible_contract"
                    if not visible_contract_missing
                    else f"visible contract missing for: {visible_contract_missing[:10]}",
                    blocking=governed_rendering_enforced,
                ),
                _review_check(
                    "page_intent_contract_complete",
                    "pass" if not page_intent_missing else "fail",
                    "every page exposes an internal governance contract"
                    if not page_intent_missing
                    else f"internal governance missing for: {page_intent_missing[:10]}",
                ),
                _review_check(
                    "state_visibility_contract_complete",
                    "pass" if not state_contract_missing else "fail",
                    "every state exposes a state_visibility_contract"
                    if not state_contract_missing
                    else f"state visibility contract missing for: {state_contract_missing[:10]}",
                ),
                _review_check(
                    "production_ui_copy_profile_complete",
                    "pass" if (not governed_rendering_enforced or not production_copy_missing) else "fail",
                    "every page exposes a production_ui_copy_profile"
                    if (not governed_rendering_enforced or not production_copy_missing)
                    else f"production UI copy missing for: {production_copy_missing[:10]}",
                    blocking=governed_rendering_enforced,
                ),
            ]
        )
        preview_html_text = files["preview_html"].read_text(encoding="utf-8", errors="ignore") if files["preview_html"].exists() else ""
        governance_hits = [
            term
            for term in ("当前状态", "下一步动作", "恢复路径", "design asset catalog", "review guidance", "why/reasoning")
            if term.lower() in preview_html_text.lower()
        ]
        forbidden_page_terms = []
        explanation_heading_hits = []
        if files["pages_dir"].exists():
            for page_file in sorted(files["pages_dir"].glob("*.md")):
                text = page_file.read_text(encoding="utf-8", errors="ignore")
                hits = [term for term in ("当前状态", "下一步动作", "恢复路径") if term in text]
                if hits:
                    forbidden_page_terms.append(f"{page_file.name}:{','.join(hits)}")
                heading_hits = [term for term in ("## 页面意图", "## 布局草图", "## 版面拆解", "## 信息优先级", "## 审阅边界", "## 关键交互", "审阅原则", "why_this_page_exists") if term in text]
                if heading_hits:
                    explanation_heading_hits.append(f"{page_file.name}:{','.join(heading_hits)}")
        heuristic_checks = [
            (
                "heuristic_system_status",
                all(any(str(state.get("id") or "").strip() in {"loading", "error", "ready"} for state in page.get("states", [])) for page in page_specs),
                "pages should expose visible status transitions",
            ),
            (
                "heuristic_real_world_match",
                all(not _contains_machine_noise(str((page.get("analysis") or {}).get("target_user") or "")) for page in page_specs),
                "page analysis should describe human goals rather than machine internals",
            ),
            (
                "heuristic_user_control",
                any(any(str(action.get("target") or "").strip() != str(page.get("page_id") or "").strip() for action in page.get("actions", [])) for page in page_specs),
                "prototype should offer controlled next-step or return actions",
            ),
            (
                "heuristic_recognition_over_recall",
                bool(ux_contract.get("recognition_over_recall_rules")),
                "recognition-over-recall rules should be explicitly frozen",
            ),
            (
                "heuristic_minimalist_discipline",
                "marketing hero dashboard" in [str(item) for item in design_reasoning.get("anti_patterns", [])],
                "design reasoning should explicitly block generic marketing-dashboard answers",
            ),
            (
                "heuristic_error_recovery_clarity",
                any(
                    any(str(state.get("id") or "").strip() in {"error", "blocked", "stale"} for state in page.get("states", []))
                    for page in page_specs
                ),
                "prototype should define error/blocked/stale recovery semantics",
            ),
            (
                "heuristic_preview_not_asset_catalog",
                "design asset catalog" not in files["preview_html"].read_text(encoding="utf-8", errors="ignore").lower() if files["preview_html"].exists() else False,
                "preview must render operator workbench judgment, not a design asset catalog",
            ),
            (
                "heuristic_first_screen_contract",
                all(
                    isinstance((page.get("internal_governance") or {}).get("first_screen_contract"), dict)
                    and all(
                        ((page.get("internal_governance") or {}).get("first_screen_contract") or {}).get(key)
                        for key in ("primary_status", "primary_blocker", "next_actions", "recovery_path")
                    )
                    for page in page_specs
                ),
                "every page should freeze first-screen status, blocker, next action, and recovery path",
            ),
            (
                "governance_copy_leak",
                (not governed_rendering_enforced) or not governance_hits,
                "preview must not render governance copy or explanatory contract wording in first-screen UI",
            ),
            (
                "first_screen_over_explanation",
                (not governed_rendering_enforced) or ("当前阻塞与下一步动作" not in preview_html_text and "首屏判断" not in preview_html_text),
                "preview first screen should not default to explanation panels",
            ),
            (
                "page_explanation_section_leak",
                (not governed_rendering_enforced) or not explanation_heading_hits,
                "page markdown must not render explanation sections or governance headings",
            ),
            (
                "review_copy_rendered_as_production_ui",
                (not governed_rendering_enforced) or not forbidden_page_terms,
                "page markdown should render production-visible copy, not review or recovery explanation blocks",
            ),
            (
                "design_context_explicit_block",
                (not governed_rendering_enforced) or bool(design_context.get("explicit_context_complete")),
                "design context must stay explicit before production rendering can proceed",
            ),
        ]
        for name, passed, message in heuristic_checks:
            checks.append(_review_check(name, "pass" if passed else "fail", message, blocking=governed_rendering_enforced or name.startswith("heuristic_")))

    blocking_failures = [item for item in checks if item["blocking"] and item["status"] == "fail"]
    overall_status = "pass" if not blocking_failures else "fail"
    human_view_status = (
        "pass"
        if files["wireframe_summary"].exists()
        and files["navigation_map_md"].exists()
        and files["state_flow_map_md"].exists()
        and files["component_catalog_md"].exists()
        and files["automation_priority_matrix_md"].exists()
        and (
            not supports_ux_truth
            or (files["ux_prd"].exists() and files["design_md"].exists() and files["preview_html"].exists() and files["preview_dark_html"].exists())
        )
        else "fail"
    )
    machine_contract_status = (
        "pass"
        if files["canonical_envelope"].exists()
        and files["wireframe_manifest"].exists()
        and files["navigation_map"].exists()
        and files["state_flow_map"].exists()
        and files["component_catalog"].exists()
        and files["automation_priority_matrix"].exists()
        and files["coverage_report"].exists()
        else "fail"
    )
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
        "canonical_truth_source": str(canonical_truth.get("truth_source") or "prototype-plan"),
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
    status_snapshot = evaluate_prototype_status(project_root, version, feature)
    reason_code = str(status_snapshot.get("reason_code") or "")
    repair_path = str(status_snapshot.get("repair_path") or "")
    if reason_code in {"prototype_canonical_truth_missing", "prototype_destructive_recreate_required"}:
        raise ValueError(str(status_snapshot.get("diagnosis") or "prototype bundle requires recreate before freeze"))
    if repair_path and repair_path != "destructive-recreate-required":
        reconcile_prototype_bundle(project_root, version, feature)
        review_prototype_bundle(project_root, version, feature)
        status_snapshot = evaluate_prototype_status(project_root, version, feature)

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
        raise ValueError("Prototype source hash drift remains after reconcile; rerun prototype review before freeze")

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
        "canonical_truth_source": status_snapshot.get("canonical_truth_source"),
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
    source_docs = load_source_documents(project_root, version, feature)
    supports_ux_truth = _supports_ux_truth(version, source_docs)
    legacy_source_path = legacy_prototype_source_path(project_root, version, feature)
    if not root.exists():
        legacy_source_exists = legacy_source_path.exists() and legacy_source_path.is_file()
        return {
            "status": "legacy_source_only" if legacy_source_exists else "missing",
            "exists": legacy_source_exists,
            "frozen": False,
            "stale": False,
            "inconsistent": False,
            "inconsistent_reasons": [],
            "prototype_mode": PROTOTYPE_MODE,
            "ui_kit": PROTOTYPE_UI_KIT,
            "compiler": {},
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
            "legacy_source_status": "present" if legacy_source_exists else "missing",
            "legacy_source_path": legacy_source_path,
        }

    manifest = _read_json(files["manifest"])
    freeze_payload = _read_json(files["freeze"])
    review_payload = _read_json(files["review_json"])
    plan = _read_json(files["prototype_plan"])
    canonical_envelope = _read_json(files["canonical_envelope"])
    compiler = plan.get("compiler") if isinstance(plan.get("compiler"), dict) else {}
    transaction = manifest.get("transaction") if isinstance(manifest.get("transaction"), dict) else {}
    sqlite_projection = _read_prototype_projection_sqlite(str(transaction.get("transaction_id") or ""))
    current_source = {doc["type"]: doc["fingerprint"] for doc in source_docs}
    current_source_hash = _current_prototype_source_hash(project_root, version, feature)
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
        "automation_priority_matrix": files["automation_priority_matrix"],
        "automation_priority_matrix_md": files["automation_priority_matrix_md"],
        "interaction_map": files["interaction_map"],
        "coverage_report": files["coverage_report"],
        "review_json": files["review_json"],
        "review_md": files["review_md"],
        "pages_dir": files["pages_dir"],
        "human_view_dir": files["human_view_dir"],
        "machine_view_dir": files["machine_view_dir"],
    }
    if supports_ux_truth:
        required_paths.update(
            {
                "design_artifacts_dir": files["design_artifacts_dir"],
                "ux_prd": files["ux_prd"],
                "design_md": files["design_md"],
                "preview_html": files["preview_html"],
                "preview_dark_html": files["preview_dark_html"],
            }
        )
    for key, path in required_paths.items():
        if key.endswith("_dir"):
            if not path.exists() or not path.is_dir():
                inconsistent_reasons.append(f"missing_dir:{key}")
        elif not path.exists():
            inconsistent_reasons.append(f"missing_artifact:{key}")
    if files["index_html"].exists():
        inconsistent_reasons.append("legacy_html_present:index_html")

    required_pages = [str(item).strip() for item in (plan.get("required_pages") or []) if str(item).strip()] if isinstance(plan, dict) else []
    missing_pages = [page_id for page_id in required_pages if not _has_named_artifact(files["pages_dir"], page_id, ".md")]
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
                files["automation_priority_matrix_md"],
                *(
                    (
                        files["ux_prd"],
                        files["design_md"],
                        files["preview_html"],
                        files["preview_dark_html"],
                    )
                    if supports_ux_truth
                    else ()
                ),
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
                files["automation_priority_matrix"],
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
    auto_fallback_accepted = _prototype_auto_fallback_accepted(
        version=version,
        compiler=compiler,
        review_status=review_status,
        frozen=frozen,
        supports_ux_truth=supports_ux_truth,
        files=files,
        plan=plan if isinstance(plan, dict) else {},
    )
    if drift_status != "consistent":
        inconsistent_reasons.append("cross_sink_drift_detected")
    if _prototype_auto_fallback_blocked(version, compiler) and not auto_fallback_accepted:
        inconsistent_reasons.append("auto_mode_fixed_template_downgrade_blocked")

    canonical_truth = {
        "truth_source": "prototype-plan",
        "available": bool(plan),
    }
    sink_truth_mismatches: dict[str, list[str]] = {}
    drift_diagnosis = {
        "drift_type": "",
        "reason_code": "",
        "diagnosis": "",
        "next_action": "",
        "repair_path": "",
    }
    if _semver_tuple(version) >= (1, 3, 11):
        canonical_truth = _load_prototype_canonical_truth(
            files,
            plan=plan if isinstance(plan, dict) else None,
            manifest=manifest if isinstance(manifest, dict) else None,
            canonical_envelope=canonical_envelope if isinstance(canonical_envelope, dict) else None,
        )
        sink_truth_mismatches = _prototype_sink_truth_mismatches(
            plan=plan if isinstance(plan, dict) else {},
            manifest=manifest if isinstance(manifest, dict) else {},
            canonical_envelope=canonical_envelope if isinstance(canonical_envelope, dict) else {},
            canonical_truth=canonical_truth,
        )
        drift_diagnosis = _classify_prototype_runtime_drift(
            current_source=current_source,
            recorded_source=recorded_source if isinstance(recorded_source, dict) else {},
            transaction=transaction if isinstance(transaction, dict) else {},
            inconsistent_reasons=inconsistent_reasons,
            sqlite_projection_status=sqlite_projection_status,
            canonical_truth=canonical_truth,
            sink_truth_mismatches=sink_truth_mismatches,
            current_source_hash=current_source_hash,
        )
        stale = stale or drift_diagnosis.get("drift_type") == "source-drift"
        drift_type = str(drift_diagnosis.get("drift_type") or "")
        if drift_type in {
            "sink-drift",
            "metadata-only-drift",
            "transaction-header-drift",
            "canonical-truth-missing",
            "destructive-recreate-required",
        } and not any(
            reason == str(drift_diagnosis.get("reason_code") or "")
            for reason in inconsistent_reasons
        ):
            inconsistent_reasons.append(str(drift_diagnosis.get("reason_code") or "prototype_artifact_inconsistent"))

    if inconsistent_reasons:
        status = "inconsistent"
    elif stale:
        status = "stale"
    elif frozen:
        status = "frozen"
    else:
        status = "draft"

    gate_ready = status == "frozen" and review_status == "pass" and (
        not _prototype_auto_fallback_blocked(version, compiler) or auto_fallback_accepted
    )
    return {
        "status": status,
        "exists": True,
        "frozen": frozen,
        "stale": stale,
        "inconsistent": bool(inconsistent_reasons),
        "inconsistent_reasons": inconsistent_reasons,
        "prototype_mode": str(plan.get("prototype_mode") or manifest.get("prototype_mode") or PROTOTYPE_MODE),
        "ui_kit": manifest.get("ui_kit") or PROTOTYPE_UI_KIT,
        "compiler": compiler,
        "compiler_fallback_accepted": auto_fallback_accepted,
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
        "canonical_truth_source": str(canonical_truth.get("truth_source") or "prototype-plan"),
        "drift_type": str(drift_diagnosis.get("drift_type") or ""),
        "reason_code": str(drift_diagnosis.get("reason_code") or ""),
        "diagnosis": str(drift_diagnosis.get("diagnosis") or ""),
        "next_action": str(drift_diagnosis.get("next_action") or ""),
        "repair_path": str(drift_diagnosis.get("repair_path") or ""),
        "sink_truth_mismatches": sink_truth_mismatches,
        "transaction": transaction if isinstance(transaction, dict) else {},
        "legacy_source_status": "present" if legacy_source_path.exists() and legacy_source_path.is_file() else "missing",
        "legacy_source_path": legacy_source_path,
    }
