"""Natural-language intent router for Beacon skill commands."""

from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
from typing import Any
from urllib import request

from beacon.utils.runtime import now_iso

SUPPORTED_INTENTS = (
    "think",
    "user-story",
    "prd",
    "test-case",
    "workflow",
    "status",
    "resume",
    "gate",
    "release",
    "doctor",
    "prototype",
    "version",
    "test-progress",
    "feedback",
    "remember",
    "recall",
    "report",
    "init",
    "qa",
    "auto-test",
    "debug",
    "analyze",
    "api-design",
    "brainstorm",
    "data-dictionary",
    "design",
    "jtbd",
    "kano",
    "moscow",
    "persona",
    "roadmap",
    "ui-spec",
    "wireframe",
    "run",
    "team",
    "outside-boundary",
)

DEFAULT_ROUTABLE_INTENTS = (
    "think",
    "user-story",
    "prd",
    "test-case",
    "workflow",
    "status",
    "resume",
    "gate",
    "release",
    "doctor",
    "prototype",
    "version",
    "test-progress",
    "feedback",
    "remember",
    "recall",
    "report",
    "init",
    "qa",
    "auto-test",
    "debug",
)

EXPLICIT_ONLY_COMMAND_HINTS: dict[str, tuple[str, ...]] = {
    "analyze": ("beacon analyze",),
    "api-design": ("beacon api-design",),
    "brainstorm": ("beacon brainstorm",),
    "data-dictionary": ("beacon data-dictionary",),
    "design": ("beacon design",),
    "jtbd": ("beacon jtbd",),
    "kano": ("beacon kano",),
    "moscow": ("beacon moscow",),
    "persona": ("beacon persona",),
    "roadmap": ("beacon roadmap",),
    "ui-spec": ("beacon ui-spec",),
    "wireframe": ("beacon wireframe",),
    "run": ("beacon run",),
    "team": ("beacon team",),
}

DEFAULT_INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "think": ("think", "需求", "澄清", "梳理", "分析需求", "方案", "下一版本", "下个版本", "演进", "调研方向", "新方向", "subagent"),
    "user-story": ("user story", "user-story", "用户故事", "验收标准", "ac"),
    "prd": ("prd", "需求文档", "产品文档", "spec", "规格说明", "prd 文档"),
    "test-case": ("test-case", "test case", "测试用例", "测试矩阵", "验收测试", "ac->tc"),
    "workflow": ("workflow", "工作流", "主链", "阶段流程", "全流程"),
    "run": ("run", "执行模式", "dry-run", "strict", "debug 模式", "运行流程"),
    "status": ("status", "状态", "看板", "进度", "当前进展", "workflow status"),
    "resume": ("resume", "续跑", "继续", "恢复", "continue", "接着跑", "继续上次", "继续 workflow"),
    "team": ("team", "多人协作", "并行执行", "executor", "协同"),
    "gate": ("gate", "放行", "门禁", "准入", "验收门"),
    "release": ("release", "发布", "上线", "回滚", "发版"),
    "doctor": ("doctor", "诊断", "环境诊断", "健康检查", "环境检查", "setup", "install", "uninstall", "安装", "升级"),
    "analyze": ("analyze", "竞品", "竞品分析", "竞争分析", "对标分析", "competitor analysis", "benchmark"),
    "api-design": ("api-design", "api design", "接口设计", "api 设计", "openapi", "endpoint design", "接口文档"),
    "data-dictionary": (
        "data-dictionary",
        "data dictionary",
        "数据字典",
        "字段字典",
        "字段定义",
        "schema dictionary",
    ),
    "design": ("design", "design thinking", "设计思维", "同理心", "ideate"),
    "jtbd": ("jtbd", "jobs to be done", "job to be done", "工作待完成", "用户任务分析"),
    "persona": ("persona", "用户画像", "用户角色", "目标用户画像", "人物画像"),
    "roadmap": ("roadmap", "路线图", "产品规划", "里程碑规划", "版本路线图"),
    "ui-spec": ("ui-spec", "ui spec", "ui 规范", "界面规范", "设计规范", "design token"),
    "prototype": ("prototype", "交互原型", "可点击原型", "ui 原型", "单页原型", "html prototype"),
    "wireframe": ("wireframe", "线框图", "低保真", "页面草图", "原型草图", "mockup"),
    "version": (
        "version",
        "版本规划",
        "版本计划",
        "版本迭代",
        "下一版本",
        "下个版本",
        "版本演进",
        "演进方向",
        "新方向",
        "semver",
    ),
    "test-progress": ("test-progress", "test progress", "测试进度", "测试结果汇总", "回归进度"),
    "feedback": ("feedback", "反馈同步", "反馈闭环", "测试反馈", "用户反馈"),
    "remember": ("remember", "记住", "记忆", "记下来", "写入记忆", "保存记忆"),
    "recall": ("recall", "回忆", "检索记忆", "记忆检索", "查看记忆", "memory search"),
    "save": ("save", "保存会话", "保存状态", "存档会话", "session save"),
    "report": ("report", "运行报告", "执行报告", "总结报告", "报告"),
    "init": ("init", "初始化", "初始化项目", "创建 beacon 项目", "bootstrap"),
    "qa": ("qa", "验收", "qa", "浏览器验收", "测试验收", "登录态测试"),
    "auto-test": ("auto-test", "自动测试", "自动化测试", "回归测试", "冒烟测试", "qa 执行"),
}

# Keep public name for backward compatibility with tests/importers.
INTENT_KEYWORDS = DEFAULT_INTENT_KEYWORDS

STAGE_HINTS = ("think", "user-story", "prd", "test-case", "release")

OUTSIDE_BOUNDARY_KEYWORDS = (
    "写代码",
    "编码实现",
    "实现接口",
    "fix bug",
    "fix production bug",
    "修复线上",
    "线上故障",
    "数据库迁移",
    "database migration",
    "db migration",
    "schema migration",
    "deploy production",
    "deploy to production",
    "release to production",
    "deploy to kubernetes",
    "deploy kubernetes",
    "deploy to k8s",
    "kubernetes deployment",
    "terraform",
    "k8s",
    "上线脚本",
)

RELEASE_CREATE_KEYWORDS = ("create", "生成", "准备", "清单")
DOCTOR_SETUP_KEYWORDS = ("setup", "install", "安装")
DOCTOR_UNINSTALL_KEYWORDS = ("uninstall", "卸载")

ROUTER_CONFIG_FILE = "intent-router.json"
DEFAULT_CONFIDENCE_THRESHOLD = 0.62

DEFAULT_INTENT_COMMAND_TEMPLATES: dict[str, Any] = {
    "think": ["think", "start", "{feature}", "--project", "{project_root}", "--version", "{version}"],
    "user-story": [
        "user-story",
        "create",
        "{feature}",
        "--project",
        "{project_root}",
        "--version",
        "{version}",
    ],
    "prd": ["prd", "create", "{feature}", "--project", "{project_root}", "--version", "{version}"],
    "test-case": [
        "test-case",
        "create",
        "{feature}",
        "--project",
        "{project_root}",
        "--version",
        "{version}",
    ],
    "workflow": ["workflow", "start", "{feature}", "--project", "{project_root}", "--version", "{version}"],
    "run": ["run", "workflow", "--feature", "{feature}", "--version", "{version}", "--project-root", "{project_root}"],
    "status": ["status", "--board", "--project-root", "{project_root}"],
    "resume": ["workflow", "continue", "--project", "{project_root}", "--version", "{version}"],
    "team": ["team", "status", "--project", "{project_root}"],
    "gate": ["gate", "check", "{stage}", "--project-root", "{project_root}", "--profile", "auto"],
    "release:create": ["release", "create", "latest", "--project", "{project_root}"],
    "release:check": ["release", "check", "latest", "--project", "{project_root}"],
    "doctor": ["doctor", "--project-root", "{project_root}"],
    "doctor:setup": ["doctor", "setup"],
    "doctor:uninstall": ["doctor", "uninstall"],
    "analyze": ["analyze", "create", "{feature}", "--project", "{project_root}"],
    "api-design": ["api-design", "create", "{feature}", "--project", "{project_root}"],
    "data-dictionary": ["data-dictionary", "create", "{feature}", "--project", "{project_root}"],
    "design": ["design", "create", "{feature}", "--project", "{project_root}"],
    "jtbd": ["jtbd", "create", "{feature}", "--project", "{project_root}"],
    "persona": ["persona", "create", "{feature}", "--project", "{project_root}"],
    "roadmap": ["roadmap", "create", "{feature}", "--project", "{project_root}"],
    "ui-spec": ["ui-spec", "create", "{feature}", "--project", "{project_root}"],
    "prototype": ["prototype", "create", "{feature}", "--project", "{project_root}", "--version", "{version}"],
    "wireframe": ["wireframe", "create", "{feature}", "--project", "{project_root}"],
    "version": ["version", "create", "{feature}", "--project", "{project_root}", "--version", "{version}"],
    "test-progress": ["test-progress", "show", "--project", "{project_root}"],
    "feedback": ["feedback", "sync", "latest", "--project-root", "{project_root}"],
    "remember": ["remember", "add", "{feature}", "--project", "{project_root}"],
    "recall": ["recall", "memory", "{feature}", "--project", "{project_root}"],
    "save": ["save", "run", "--project", "{project_root}"],
    "report": ["report", "generate", "latest", "--project-root", "{project_root}"],
    "init": ["init", "--project-root", "{project_root}", "--dry-run"],
    "qa": ["qa", "run", "all", "--project", "{project_root}", "--version", "{version}"],
    "auto-test": ["auto-test", "create", "all", "--project", "{project_root}", "--version", "{version}"],
    "outside-boundary": ["status", "--board", "--project-root", "{project_root}"],
}

INTENT_PRIORITY: dict[str, int] = {
    "resume": 120,
    "workflow": 100,
    "status": 95,
    "run": 90,
    "gate": 85,
    "release": 85,
    "doctor": 85,
    "qa": 86,
    "auto-test": 85,
    "test-progress": 84,
    "report": 84,
    "feedback": 83,
    "init": 82,
    "save": 82,
    "remember": 82,
    "recall": 82,
    "team": 80,
    "analyze": 79,
    "api-design": 79,
    "data-dictionary": 79,
    "design": 79,
    "jtbd": 79,
    "persona": 79,
    "roadmap": 79,
    "ui-spec": 79,
    "prototype": 79,
    "wireframe": 79,
    "version": 79,
    "user-story": 70,
    "prd": 70,
    "test-case": 70,
    "think": 10,
}

_ARTIFACT_SIGNAL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "think": ("think", "需求", "澄清", "方案", "边界"),
    "user-story": ("user-story", "用户故事", "验收标准", "ac"),
    "prd": ("prd", "需求文档", "规格", "spec"),
    "test-case": ("test-case", "测试用例", "测试矩阵", "ac->tc"),
    "workflow": ("workflow", "工作流", "主链"),
    "qa": ("qa", "验收", "回归", "测试"),
    "auto-test": ("auto-test", "自动测试", "自动化测试"),
    "debug": ("debug", "调试", "路由", "提示词"),
    "doctor": ("doctor", "诊断", "健康检查"),
    "status": ("status", "状态", "看板"),
    "resume": ("resume", "继续", "恢复", "续跑"),
    "gate": ("gate", "放行", "门禁"),
    "release": ("release", "发布", "发版"),
    "version": ("version", "版本", "版本规划", "版本迭代", "下一版本", "演进"),
}

_PROMPT_TEMPLATE_BY_INTENT: dict[str, str] = {
    "think": "请用 Beacon 为「{feature}」做需求澄清，输出 think 产物、关键边界、阻塞项和下一步命令，version={version}。",
    "user-story": "请用 Beacon 为「{feature}」生成 user-story 与验收标准，version={version}。",
    "prd": "请用 Beacon 为「{feature}」生成 PRD，覆盖目标、范围、约束和风险，version={version}。",
    "test-case": "请用 Beacon 为「{feature}」生成测试用例、AC→TC 映射和覆盖缺口，version={version}。",
    "workflow": "请用 Beacon 为「{feature}」启动完整工作流，并告诉我主链下一步该执行什么，version={version}。",
    "status": "请用 Beacon 查看当前 workflow 状态，并说明下一步推荐动作，version={version}。",
    "resume": "请用 Beacon 继续上次 workflow，先识别 run/feature，再输出恢复建议，version={version}。",
    "gate": "请用 Beacon 检查当前 release gate 状态，并说明阻塞项与放行建议，version={version}。",
    "release": "请用 Beacon 检查「{feature}」的 release 准备度，输出 release 风险与缺失工件，version={version}。",
    "doctor": "请用 Beacon 做环境与上下文诊断，输出 doctor 结论、风险和下一步命令，version={version}。",
    "qa": "请用 Beacon 为「{feature}」执行 QA 验收规划或回归分析，version={version}。",
    "auto-test": "请用 Beacon 为「{feature}」生成自动测试/回归执行建议，version={version}。",
    "version": "请用 Beacon 为「{feature}」输出下一版本演进建议、范围边界、候选方向与推荐命令，version={version}。",
    "debug": "请用 Beacon debug 分析这次提示词为什么没有进入正确主链，输出意图、边界、推荐命令和规范化重写建议，version={version}。",
}

RESUME_ACTION_KEYWORDS = ("resume", "continue", "恢复", "继续", "续跑", "接着")
RESUME_CONTEXT_KEYWORDS = ("workflow", "工作流", "上次", "上一轮", "previous", "last", "run-")
VERSION_EVOLUTION_KEYWORDS = (
    "下一版本",
    "下个版本",
    "版本演进",
    "继续演进",
    "演进",
    "演进方向",
    "新方向",
    "路线",
    "roadmap",
)
SUBAGENT_PLANNING_KEYWORDS = (
    "subagent",
    "sub-agent",
    "子代理",
    "multi-agent",
    "multi agent",
    "codex 原生",
    "native-team",
    "native-single",
    "orchestrate",
    "orchestration",
)
CROSS_STAGE_PLANNING_KEYWORDS = (
    "需求",
    "prd",
    "用户故事",
    "story",
    "test",
    "qa",
    "implement",
)


class _SafeFormatMap(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _normalize_text(text: str) -> str:
    return str(text or "").strip().lower().replace("_", "-")


def _extract_feature(goal: str) -> str:
    text = str(goal or "").strip()
    if not text:
        return "Untitled Feature"
    text = re.sub(r"^(请|帮我|帮忙|需要|现在|请你)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(create|generate|build|run)\s+", "", text, flags=re.IGNORECASE)
    text = text.strip("：:。.! ")
    return text[:80] if text else "Untitled Feature"


def _extract_stage_hint(goal: str) -> str:
    text = _normalize_text(goal)
    for stage in STAGE_HINTS:
        if stage in text:
            return stage
    if "需求" in text:
        return "think"
    if "测试" in text:
        return "test-case"
    if "发布" in text or "上线" in text:
        return "release"
    return "release"


def _extract_run_id(goal: str) -> str:
    matched = re.search(r"\b(run-[a-z0-9\-]+)\b", _normalize_text(goal))
    if matched:
        return matched.group(1)
    return ""


def _safe_float(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except Exception:  # noqa: BLE001
        return fallback
    return number


def _keyword_hits(text: str, tokens: tuple[str, ...]) -> list[str]:
    normalized_text = _normalize_text(text)
    return [token for token in tokens if _match_token(normalized_text, token)]


def _match_token(text: str, token: str) -> bool:
    token_norm = re.sub(r"\s+", " ", _normalize_text(token))
    if not token_norm:
        return False
    if re.search(r"[\u4e00-\u9fff]", token_norm):
        return token_norm in text
    if re.fullmatch(r"[a-z0-9\- ]+", token_norm):
        pattern = r"(?<![a-z0-9-])" + re.escape(token_norm).replace(r"\ ", r"\s+") + r"(?![a-z0-9-])"
        return re.search(pattern, text) is not None
    return token_norm in text


def _merge_keywords(overrides: Any) -> dict[str, tuple[str, ...]]:
    merged: dict[str, tuple[str, ...]] = {k: tuple(v) for k, v in DEFAULT_INTENT_KEYWORDS.items()}
    if not isinstance(overrides, dict):
        return merged

    for intent, values in overrides.items():
        normalized_intent = _normalize_text(str(intent))
        if normalized_intent not in SUPPORTED_INTENTS:
            continue
        if not isinstance(values, (list, tuple)):
            continue
        extras: list[str] = []
        for item in values:
            token = _normalize_text(str(item))
            if token:
                extras.append(token)
        if not extras:
            continue
        base = list(merged.get(normalized_intent, ()))
        for token in extras:
            if token not in base:
                base.append(token)
        merged[normalized_intent] = tuple(base)

    return merged


def _merge_outside_keywords(overrides: Any) -> tuple[str, ...]:
    merged = list(OUTSIDE_BOUNDARY_KEYWORDS)
    if isinstance(overrides, (list, tuple)):
        for item in overrides:
            token = _normalize_text(str(item))
            if token and token not in merged:
                merged.append(token)
    return tuple(merged)


def _explicit_intent_override(goal: str) -> str:
    normalized = _normalize_text(goal)
    for intent, hints in EXPLICIT_ONLY_COMMAND_HINTS.items():
        if any(_match_token(normalized, hint) for hint in hints):
            return intent
    return ""


def _load_router_config(project_root: Path) -> dict[str, Any]:
    config_path = Path(project_root) / ".beacon" / ROUTER_CONFIG_FILE
    config_raw: dict[str, Any] = {}
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                config_raw = loaded
        except Exception:  # noqa: BLE001
            config_raw = {}

    threshold = max(
        0.0,
        min(
            1.0,
            _safe_float(config_raw.get("confidence_threshold"), DEFAULT_CONFIDENCE_THRESHOLD),
        ),
    )

    return {
        "config_path": str(config_path),
        "config_loaded": bool(config_raw),
        "confidence_threshold": threshold,
        "intent_keywords": _merge_keywords(config_raw.get("intent_keywords")),
        "outside_boundary_keywords": _merge_outside_keywords(config_raw.get("outside_boundary_keywords")),
        "intent_command_templates": {
            **DEFAULT_INTENT_COMMAND_TEMPLATES,
            **(
                config_raw.get("intent_command_templates")
                if isinstance(config_raw.get("intent_command_templates"), dict)
                else {}
            ),
        },
    }


def _rule_route(goal: str, *, intent_keywords: dict[str, tuple[str, ...]]) -> dict[str, Any]:
    text = _normalize_text(goal)
    if not text:
        return {
            "intent": "think",
            "confidence": 0.35,
            "reason": "empty_input_default_to_think",
            "router_mode": "rule",
        }

    explicit_intent = _explicit_intent_override(goal)
    if explicit_intent:
        return {
            "intent": explicit_intent,
            "confidence": 0.9,
            "reason": f"explicit_command_hint(intent={explicit_intent})",
            "router_mode": "rule",
        }

    scores: dict[str, int] = {
        name: 0 for name in intent_keywords if name in DEFAULT_ROUTABLE_INTENTS
    }
    for intent, keywords in intent_keywords.items():
        if intent not in scores:
            continue
        scores[intent] += len(_keyword_hits(text, keywords))

    if "resume" in scores:
        resume_action_hits = _keyword_hits(text, RESUME_ACTION_KEYWORDS)
        resume_context_hits = _keyword_hits(text, RESUME_CONTEXT_KEYWORDS)
        if resume_action_hits and resume_context_hits:
            scores["resume"] += 2

    version_evolution_hits = _keyword_hits(text, VERSION_EVOLUTION_KEYWORDS)
    subagent_planning_hits = _keyword_hits(text, SUBAGENT_PLANNING_KEYWORDS)
    cross_stage_planning_hits = _keyword_hits(text, CROSS_STAGE_PLANNING_KEYWORDS)
    if "version" in scores and version_evolution_hits:
        scores["version"] += len(version_evolution_hits)
        if subagent_planning_hits:
            scores["version"] += len(subagent_planning_hits)
        if len(cross_stage_planning_hits) >= 2:
            scores["version"] += 3
    if "version" in scores and subagent_planning_hits and len(cross_stage_planning_hits) >= 3:
        scores["version"] += 2

    ranked = sorted(
        scores.items(),
        key=lambda item: (item[1], INTENT_PRIORITY.get(item[0], 0)),
        reverse=True,
    )
    best_intent, best_score = ranked[0] if ranked else ("think", 0)
    if best_score <= 0:
        best_intent = "think"
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    confidence = 0.45
    if best_score > 0:
        confidence = min(0.95, 0.55 + 0.12 * best_score - 0.05 * second_score)

    return {
        "intent": best_intent if best_score > 0 else "think",
        "confidence": round(confidence, 2),
        "reason": f"keyword_rule(best={best_intent},score={best_score})",
        "router_mode": "rule",
    }


def _should_use_llm(mode: str) -> bool:
    mode_norm = _normalize_text(mode)
    if mode_norm == "rule":
        return False
    if mode_norm == "llm":
        return True
    env_mode = _normalize_text(os.environ.get("BEACON_INTENT_ROUTER_MODE", ""))
    return env_mode in {"llm", "real", "api", "auto"}


def _llm_route(goal: str) -> dict[str, Any]:
    api_key = str(os.environ.get("BEACON_LLM_API_KEY", "")).strip()
    if not api_key:
        raise RuntimeError("BEACON_LLM_API_KEY missing")

    api_base = str(os.environ.get("BEACON_LLM_API_BASE", "https://api.openai.com/v1")).strip().rstrip("/")
    model = str(os.environ.get("BEACON_LLM_MODEL", "gpt-4o-mini")).strip()
    timeout_s = float(str(os.environ.get("BEACON_LLM_TIMEOUT", "8")).strip() or "8")

    intent_choices = "|".join(SUPPORTED_INTENTS)
    system_prompt = (
        "You are a beacon CLI intent router. Return compact JSON: "
        + f'{{"intent":"{intent_choices}","confidence":0.0,"reason":"...","stage_hint":"think|user-story|prd|test-case|release"}}'
    )
    body = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"input={goal}"},
        ],
    }
    req = request.Request(
        url=f"{api_base}/chat/completions",
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with request.urlopen(req, timeout=timeout_s) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    content = ""
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first, dict) else {}
        if isinstance(message, dict):
            content = str(message.get("content", "")).strip()

    parsed: dict[str, Any] = {}
    try:
        parsed = json.loads(content) if content else {}
    except Exception:  # noqa: BLE001
        parsed = {}

    intent = str(parsed.get("intent", "")).strip().lower()
    if intent not in SUPPORTED_INTENTS:
        intent = "think"
    confidence = float(parsed.get("confidence", 0.5) or 0.5)
    confidence = max(0.0, min(1.0, confidence))
    return {
        "intent": intent,
        "confidence": round(confidence, 2),
        "reason": str(parsed.get("reason", "")).strip() or "llm_route",
        "stage_hint": str(parsed.get("stage_hint", "")).strip().lower(),
        "router_mode": "llm",
    }


def _apply_boundary_guard(
    goal: str,
    route: dict[str, Any],
    *,
    intent_keywords: dict[str, tuple[str, ...]],
    outside_boundary_keywords: tuple[str, ...],
) -> dict[str, Any]:
    text = _normalize_text(goal)
    outside_hits = _keyword_hits(text, outside_boundary_keywords)

    all_inside_tokens: list[str] = []
    for intent, tokens in intent_keywords.items():
        if intent == "outside-boundary":
            continue
        all_inside_tokens.extend(tokens)
    inside_hits = _keyword_hits(text, tuple(all_inside_tokens))

    boundary_state = "in_scope"
    boundary_reason = "in_scope"
    if outside_hits and inside_hits:
        boundary_state = "mixed_need_confirm"
        boundary_reason = f"mixed_request(outside={outside_hits[:3]},inside={inside_hits[:3]})"
    elif outside_hits:
        boundary_state = "out_of_scope"
        boundary_reason = f"outside_boundary_keywords={outside_hits[:3]}"

    route = dict(route)
    if boundary_state == "out_of_scope":
        route["intent"] = "outside-boundary"
        route["confidence"] = max(float(route.get("confidence", 0.0)), 0.88)
        route["reason"] = f"{route.get('reason', '')};{boundary_reason}".strip(";")
    elif boundary_state == "mixed_need_confirm":
        route["confidence"] = min(float(route.get("confidence", 0.0) or 0.0), 0.59)
        route["reason"] = f"{route.get('reason', '')};{boundary_reason}".strip(";")

    route["boundary"] = {
        "state": boundary_state,
        "in_scope": boundary_state == "in_scope",
        "reason": boundary_reason,
        "outside_hits": outside_hits[:5],
        "inside_hits": inside_hits[:5],
    }
    return route


def _select_template_key(intent: str, goal: str) -> str:
    text = _normalize_text(goal)
    if intent == "release":
        if any(token in text for token in RELEASE_CREATE_KEYWORDS):
            return "release:create"
        return "release:check"
    if intent == "doctor":
        if any(token in text for token in DOCTOR_UNINSTALL_KEYWORDS):
            return "doctor:uninstall"
        if any(token in text for token in DOCTOR_SETUP_KEYWORDS):
            return "doctor:setup"
    return intent


def _render_template(template: Any, *, context: dict[str, str]) -> list[str]:
    formatter = _SafeFormatMap(context)
    if isinstance(template, str):
        rendered = template.format_map(formatter)
        try:
            return [part for part in shlex.split(rendered) if part]
        except Exception:  # noqa: BLE001
            return [rendered]

    if isinstance(template, (list, tuple)):
        rendered_items = []
        for item in template:
            value = str(item).format_map(formatter).strip()
            if value:
                rendered_items.append(value)
        return rendered_items

    return []


def _build_command_plan(
    *,
    intent: str,
    goal: str,
    project_root: Path,
    version: str,
    stage_hint: str,
    command_templates: dict[str, Any],
) -> tuple[list[str], str]:
    feature = _extract_feature(goal)
    root_text = str(project_root)
    version_text = str(version or "auto").strip() or "auto"
    stage = stage_hint if stage_hint in STAGE_HINTS else _extract_stage_hint(goal)
    context = {
        "intent": intent,
        "goal": str(goal),
        "feature": feature,
        "project_root": root_text,
        "version": version_text,
        "stage": stage,
        "stage_hint": stage_hint or stage,
        "run_id": _extract_run_id(goal),
    }

    template_key = _select_template_key(intent, goal)
    template = command_templates.get(template_key) or command_templates.get(intent)
    args = _render_template(template, context=context)

    if not args:
        args = ["status", "--board", "--project-root", root_text]

    command = "beacon " + " ".join(shlex.quote(item) for item in args)
    return args, command


def optimize_prompt_to_plan(
    goal: str,
    *,
    project_root: Path,
    version: str = "auto",
    router_mode: str = "auto",
) -> dict[str, Any]:
    """Route natural language prompt to a normalized beacon command plan."""
    root = Path(project_root)
    router_config = _load_router_config(root)

    route = _rule_route(goal, intent_keywords=router_config["intent_keywords"])
    if _should_use_llm(router_mode):
        try:
            route = _llm_route(goal)
        except Exception as exc:  # noqa: BLE001
            route = dict(route)
            route["router_mode"] = "rule-fallback"
            route["reason"] = f"{route.get('reason', '')};llm_error={exc}".strip(";")

    route = _apply_boundary_guard(
        goal,
        route,
        intent_keywords=router_config["intent_keywords"],
        outside_boundary_keywords=router_config["outside_boundary_keywords"],
    )

    intent = str(route.get("intent", "think"))
    if intent not in SUPPORTED_INTENTS:
        intent = "think"
    stage_hint = str(route.get("stage_hint", "")).strip().lower()
    args, command = _build_command_plan(
        intent=intent,
        goal=goal,
        project_root=root,
        version=version,
        stage_hint=stage_hint,
        command_templates=router_config["intent_command_templates"],
    )

    confidence = float(route.get("confidence", 0.0) or 0.0)
    boundary = route.get("boundary", {"state": "in_scope", "in_scope": True, "reason": "in_scope"})
    boundary_state = str(boundary.get("state", "in_scope"))
    min_confidence = float(router_config["confidence_threshold"])

    risk_hints: list[str] = []
    if intent in {"gate", "release"}:
        risk_hints.append("This command may affect release/go-live decision artifacts.")
    if confidence < min_confidence:
        risk_hints.append(
            f"Intent confidence is low ({round(confidence, 2)} < {round(min_confidence, 2)}); manual confirmation required before execution."
        )

    boundary_hints: list[str] = []
    if boundary_state == "out_of_scope":
        boundary_hints.append("Request is outside Beacon scope (workflow/governance tooling).")
        boundary_hints.append("Use Beacon for requirement/test/release artifacts, not production coding/deploy steps.")
    elif boundary_state == "mixed_need_confirm":
        boundary_hints.append("Mixed request detected: contains Beacon tasks and out-of-scope implementation/deploy actions.")
        boundary_hints.append("Split prompt into Beacon governance intent and non-Beacon engineering intent.")

    fallback = {
        "strategy": "clarify_and_preview" if confidence < min_confidence else "direct_execute_safe",
        "next_commands": [
            f"beacon status --board --project-root {shlex.quote(str(root))}",
            f"beacon workflow status --project {shlex.quote(str(root))}",
        ],
    }

    execution_policy = {
        "min_confidence": round(min_confidence, 2),
        "boundary_state": boundary_state,
        "requires_confirmation": boundary_state == "mixed_need_confirm" or confidence < min_confidence,
        "allow_execute": boundary_state == "in_scope" and confidence >= min_confidence,
    }

    return {
        "schema_version": "1.1",
        "ts": now_iso(),
        "input_goal": goal,
        "intent": intent,
        "confidence": round(confidence, 2),
        "router_mode": route.get("router_mode", "rule"),
        "reason": route.get("reason", ""),
        "boundary": boundary,
        "recommended_subcommand": args[0] if args else "",
        "recommended_args": args,
        "recommended_command": command,
        "risk_hints": risk_hints,
        "boundary_hints": boundary_hints,
        "fallback": fallback,
        "execution_policy": execution_policy,
        "router_config": {
            "config_loaded": bool(router_config.get("config_loaded")),
            "config_path": str(router_config.get("config_path", "")),
        },
    }


def build_prompt_adaptation_pack(
    goal: str,
    *,
    plan: dict[str, Any],
    project_root: Path,
    version: str,
) -> dict[str, Any]:
    """Translate routing output into a user-facing prompt normalization guide."""
    intent = str(plan.get("intent", "think") or "think")
    confidence = round(float(plan.get("confidence", 0.0) or 0.0), 2)
    boundary = plan.get("boundary", {}) if isinstance(plan.get("boundary"), dict) else {}
    boundary_state = str(boundary.get("state", "in_scope") or "in_scope")
    feature = _extract_feature(goal)
    feature_hint = feature if feature and feature != "Untitled Feature" else "<feature>"
    version_text = str(version or "auto").strip() or "auto"
    normalized_prompt = (
        _PROMPT_TEMPLATE_BY_INTENT.get(intent)
        or "请用 Beacon 为「{feature}」输出主链建议、推荐命令与下一步动作，version={version}。"
    ).format(feature=feature_hint, version=version_text)

    goal_text = str(goal or "").strip()
    goal_has_version = re.search(r"\bv?\d+\.\d+\.\d+\b", goal_text) is not None
    artifact_tokens = _ARTIFACT_SIGNAL_KEYWORDS.get(intent, ())
    goal_has_artifact_signal = any(_match_token(_normalize_text(goal_text), token) for token in artifact_tokens)

    normalize_actions: list[str] = []
    missing_fields: list[str] = []
    if not goal_has_artifact_signal:
        missing_fields.append("expected_artifact_or_stage")
        normalize_actions.append("明确说明你要 Beacon 产出哪类工件或当前所处阶段。")
    if not goal_has_version:
        missing_fields.append("target_version")
        normalize_actions.append("补充目标 version，例如 `v1.2.1`。")
    if boundary_state == "mixed_need_confirm":
        missing_fields.append("boundary_split")
        normalize_actions.append("把 Beacon 主链诉求与写代码/部署等非 Beacon 诉求拆成两条输入。")
    elif boundary_state == "out_of_scope":
        missing_fields.append("beacon_scope")
        normalize_actions.append("把需求改写成 requirement / QA / release / debug 这类 Beacon 范围内目标。")

    min_confidence = float(plan.get("execution_policy", {}).get("min_confidence", DEFAULT_CONFIDENCE_THRESHOLD) or DEFAULT_CONFIDENCE_THRESHOLD)
    needs_clarification = bool(
        boundary_state != "in_scope"
        or confidence < min_confidence
        or missing_fields
    )
    if confidence < min_confidence:
        normalize_actions.append("避免只说“帮我搞一下”，要明确 feature、期望工件和执行边界。")

    guidance_lines = [
        f"Beacon prompt adapter: intent={intent}, confidence={confidence}, boundary={boundary_state}.",
        f"Recommended Beacon command: {str(plan.get('recommended_command', '')).strip() or 'beacon help --project-root . --json'}",
        "Guide the user to include: feature context, expected Beacon artifact/stage, target version, and whether Beacon should only plan or also execute.",
    ]
    if normalize_actions:
        guidance_lines.append("Normalization actions: " + " ".join(normalize_actions))
    guidance_lines.append(f'Suggested normalized prompt: "{normalized_prompt}"')

    return {
        "intent": intent,
        "confidence": confidence,
        "boundary_state": boundary_state,
        "needs_clarification": needs_clarification,
        "missing_fields": missing_fields,
        "normalize_actions": normalize_actions,
        "normalized_prompt": normalized_prompt,
        "recommended_command": str(plan.get("recommended_command", "")).strip(),
        "assistant_context": " ".join(line.strip() for line in guidance_lines if line.strip()),
    }
