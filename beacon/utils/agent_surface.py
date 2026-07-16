"""Project-local agent surface materialization for Beacon host-visible skills."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json
from beacon.utils.workspace_admission import (
    GIT_ADMISSION_SKILLS,
    TIER_A_SKILLS,
    TRUTH_AUTHORING_SKILLS,
    inject_git_admission_into_skill_text,
)

_RULE_BLOCK_START = "<!-- BEACON:AGENT_SURFACE:START -->"
_RULE_BLOCK_END = "<!-- BEACON:AGENT_SURFACE:END -->"
_STATE_PATH = Path(".beacon") / "state" / "agent-surfaces.json"
_V160_TAXONOMY_VERSION = "v1.6.0"
_V160_HARNESSES = {"planner", "generator", "evaluator", "governor"}
_V160_HARNESS_CODES = {
    "pln": "planner",
    "gen": "generator",
    "eval": "evaluator",
    "gov": "governor",
}
_V160_RESEARCH_REQUIRED_FIELDS = (
    "outcome",
    "lake_or_ocean",
    "truth_refs",
    "source_refs",
    "evidence_refs",
    "truth_gap",
    "test_gap",
    "implementation_risk",
    "verification_risk",
    "recommended_route",
    "user_decision",
    "promotion_ref",
)
_V160_ALLOWED_RESEARCH_STATUSES = {"queued", "routeable", "promoted", "rejected", "deferred"}
_V160_PROMOTED_DECISIONS = {"accepted", "promoted"}
_V160_NO_FAKE_DELIVERY_TERMS = (
    "placeholder implementation",
    "docs-only completion",
    "fake runner evidence",
    "zero assertions",
    "placeholder evidence",
)
_V160_PACKAGE_SOURCE_KINDS = {
    "generated_v160_harness_taxonomy",
    "generated_v160_harness_taxonomy_fallback",
    "migrated_v160_harness_taxonomy_preserve_skill_content",
}
_V160_PUBLIC_PLANNER_SKILLS = (
    "beacon-pln-brainstorm",
    "beacon-pln-source",
    "beacon-pln-review",
    "beacon-pln-friction",
    "beacon-pln-program",
    "beacon-pln-program-auto",
    "beacon-pln-program-interactive",
)
_V160_PUBLIC_EVALUATOR_SKILLS = (
    "beacon-eval-agent",
)
_V160_PUBLIC_GOVERNOR_SKILLS = (
    "beacon-loop-goal",
)


@dataclass(frozen=True)
class SkillProjection:
    """Version-selected host-visible skill projection."""

    id: str
    source_path: str
    source_hash: str
    source_kind: str
    content: str | None = None
    source_dir: Path | None = None
    files: dict[str, str] | None = None


@dataclass(frozen=True)
class AgentSurfaceTarget:
    """Resolved project-local surface target for one agent host."""

    agent: str
    skills_root: Path
    rules_path: Path | None = None
    rules_kind: str = ""


def packaged_beacon_skill_root() -> Path:
    """Return the packaged Beacon skill-pack root shipped with the repo/runtime."""
    return (Path(__file__).resolve().parents[2] / "skills" / "beacon").resolve()


_V160_RENAME_MATRIX: tuple[tuple[str, str, str, str], ...] = (
    ("beacon-brainstorm", "beacon-pln-brainstorm", "planner", "粗提示词拆分、湖海判断与路由收敛"),
    ("beacon-source-driven", "beacon-pln-source", "planner", "源码和证据锚定分析"),
    ("beacon-review", "beacon-pln-review", "planner", "多角度 planner review、意图保真、source parity 和状态机审查"),
    ("beacon-friction-intake", "beacon-pln-friction", "planner", "摩擦记录、排队与只读治理"),
    ("beacon-truth", "beacon-gen-truth", "generator", "package-authoritative 需求真相总入口"),
    ("beacon-prd-bootstrap", "beacon-gen-truth-init", "generator", "需求真相包初始化"),
    ("beacon-change", "beacon-gen-change", "generator", "受治理的需求真相变更"),
    ("beacon-change-refreeze", "beacon-gen-refreeze", "generator", "受治理的需求重冻结"),
    ("beacon-prototype", "beacon-gen-prototype", "generator", "已接受 UI/UX 原型结果绑定"),
    ("beacon-implement", "beacon-gen-implement", "generator", "实现计划与执行"),
    ("beacon-design", "beacon-gen-design", "generator", "设计支持总入口"),
    ("beacon-design-bootstrap", "beacon-gen-design-init", "generator", "设计能力准入"),
    ("beacon-design-explore", "beacon-gen-design-explore", "generator", "UI 方向探索"),
    ("beacon-design-system", "beacon-gen-design-system", "generator", "组件系统规划"),
    ("beacon-design-polish", "beacon-gen-design-polish", "generator", "UI 打磨支持"),
    ("beacon-qa", "beacon-eval-qa", "evaluator", "验收证据验证"),
    ("beacon-qa-evo-deep", "beacon-eval-qa-deep", "evaluator", "深度 QA findings"),
    ("beacon-release", "beacon-eval-release", "evaluator", "发布就绪判断"),
    ("beacon-real-project-validation", "beacon-eval-real-project", "evaluator", "真实项目发布证明"),
    ("beacon-design-library", "beacon-gov-library", "governor", "设计参考检索"),
    ("beacon-design-extract", "beacon-gov-extract", "governor", "截图和参考抽取"),
    ("beacon-doctor", "beacon-gov-doctor", "governor", "上下文和环境修复"),
    ("beacon-debug-recovery", "beacon-gov-debug", "governor", "阻断恢复"),
    ("beacon-status", "beacon-gov-status", "governor", "状态和看板可见性"),
    ("beacon-help", "beacon-gov-help", "governor", "下一步指导"),
    ("beacon-archive", "beacon-gov-archive", "governor", "历史需求隔离"),
    ("beacon-learn", "beacon-gov-learn", "governor", "受治理学习"),
    ("beacon-project-hooks", "beacon-gov-hooks", "governor", "生命周期 hook 合约"),
    ("beacon-toolkit-automation", "beacon-gov-automation", "governor", "自动化资产"),
    ("beacon-toolkit-branch-governance", "beacon-gov-branch", "governor", "分支和工作区治理"),
    ("beacon-toolkit-lighthouse", "beacon-gov-lighthouse", "governor", "快速源码和仓库分析"),
    ("beacon-toolkit-metadata", "beacon-gov-metadata", "governor", "确定性 metadata 工具"),
    ("using-beacon", "beacon-gov-router", "governor", "host 级路由提示"),
)

_V160_PREVIOUS_LONG_ALIAS_IDS = {
    "beacon-planner-brainstorm",
    "beacon-planner-deep-analysis",
    "beacon-planner-friction-intake",
    "beacon-planner-founder-review",
    "beacon-planner-design-review",
    "beacon-planner-security-review",
    "beacon-planner-performance-review",
    "beacon-planner-doubt-review",
    "beacon-planner-source-driven",
    "beacon-planner-context-engineering",
    "beacon-planner-design-simplify",
    "beacon-planner-documentation-adr",
    "beacon-generator-truth-package",
    "beacon-generator-truth-bootstrap",
    "beacon-generator-truth-change",
    "beacon-generator-truth-refreeze",
    "beacon-generator-prototype-binding",
    "beacon-generator-implementation",
    "beacon-generator-design-support",
    "beacon-generator-design-bootstrap",
    "beacon-generator-design-explore",
    "beacon-generator-design-system",
    "beacon-generator-design-polish",
    "beacon-evaluator-qa",
    "beacon-evaluator-qa-deep",
    "beacon-evaluator-release",
    "beacon-evaluator-real-project",
    "beacon-governor-design-library",
    "beacon-governor-design-extract",
    "beacon-governor-doctor",
    "beacon-governor-debug-recovery",
    "beacon-governor-status",
    "beacon-governor-help",
    "beacon-governor-archive",
    "beacon-governor-learn",
    "beacon-governor-hooks",
    "beacon-governor-automation",
    "beacon-governor-branch",
    "beacon-governor-lighthouse",
    "beacon-governor-metadata",
    "beacon-governor-router",
}

_V160_REMOVED_OLD_ALIASES = {
    "beacon-prd",
    "beacon-user-story",
    "beacon-test-case",
}
_V160_INTERNAL_PLANNER_ALIAS_REWRITE_MAP = {
    "beacon-deep": "beacon-pln-review",
    "beacon-ceo-review": "beacon-pln-review",
    "beacon-design-review": "beacon-pln-review",
    "beacon-security-review": "beacon-pln-review",
    "beacon-performance-review": "beacon-pln-review",
    "beacon-doubt-review": "beacon-pln-review",
    "beacon-context-engineering": "beacon-pln-review",
    "beacon-design-simplify": "beacon-pln-review",
    "beacon-documentation-adr": "beacon-pln-review",
    "beacon-planner-deep-analysis": "beacon-pln-review",
    "beacon-planner-founder-review": "beacon-pln-review",
    "beacon-planner-design-review": "beacon-pln-review",
    "beacon-planner-security-review": "beacon-pln-review",
    "beacon-planner-performance-review": "beacon-pln-review",
    "beacon-planner-doubt-review": "beacon-pln-review",
    "beacon-planner-context-engineering": "beacon-pln-review",
    "beacon-planner-design-simplify": "beacon-pln-review",
    "beacon-planner-documentation-adr": "beacon-pln-review",
    "beacon-pln-deep": "beacon-pln-review",
    "beacon-pln-founder": "beacon-pln-review",
    "beacon-pln-design": "beacon-pln-review",
    "beacon-pln-security": "beacon-pln-review",
    "beacon-pln-performance": "beacon-pln-review",
    "beacon-pln-doubt": "beacon-pln-review",
    "beacon-pln-context": "beacon-pln-review",
    "beacon-pln-simplify": "beacon-pln-review",
    "beacon-pln-adr": "beacon-pln-review",
}
_V160_OLD_ALIAS_IDS = (
    {row[0] for row in _V160_RENAME_MATRIX}
    | _V160_REMOVED_OLD_ALIASES
    | _V160_PREVIOUS_LONG_ALIAS_IDS
    | set(_V160_INTERNAL_PLANNER_ALIAS_REWRITE_MAP)
)
_V160_PREVIOUS_LONG_ALIAS_REWRITE_MAP = {
    "beacon-planner-brainstorm": "beacon-pln-brainstorm",
    "beacon-planner-friction-intake": "beacon-pln-friction",
    "beacon-planner-source-driven": "beacon-pln-source",
    "beacon-generator-truth-package": "beacon-gen-truth",
    "beacon-generator-truth-bootstrap": "beacon-gen-truth-init",
    "beacon-generator-truth-change": "beacon-gen-change",
    "beacon-generator-truth-refreeze": "beacon-gen-refreeze",
    "beacon-generator-prototype-binding": "beacon-gen-prototype",
    "beacon-generator-implementation": "beacon-gen-implement",
    "beacon-generator-design-support": "beacon-gen-design",
    "beacon-generator-design-bootstrap": "beacon-gen-design-init",
    "beacon-generator-design-explore": "beacon-gen-design-explore",
    "beacon-generator-design-system": "beacon-gen-design-system",
    "beacon-generator-design-polish": "beacon-gen-design-polish",
    "beacon-evaluator-qa": "beacon-eval-qa",
    "beacon-evaluator-qa-deep": "beacon-eval-qa-deep",
    "beacon-evaluator-release": "beacon-eval-release",
    "beacon-evaluator-real-project": "beacon-eval-real-project",
    "beacon-governor-design-library": "beacon-gov-library",
    "beacon-governor-design-extract": "beacon-gov-extract",
    "beacon-governor-doctor": "beacon-gov-doctor",
    "beacon-governor-debug-recovery": "beacon-gov-debug",
    "beacon-governor-status": "beacon-gov-status",
    "beacon-governor-help": "beacon-gov-help",
    "beacon-governor-archive": "beacon-gov-archive",
    "beacon-governor-learn": "beacon-gov-learn",
    "beacon-governor-hooks": "beacon-gov-hooks",
    "beacon-governor-automation": "beacon-gov-automation",
    "beacon-governor-branch": "beacon-gov-branch",
    "beacon-governor-lighthouse": "beacon-gov-lighthouse",
    "beacon-governor-metadata": "beacon-gov-metadata",
    "beacon-governor-router": "beacon-gov-router",
}
_V160_ROUTE_REWRITE_MAP = {
    **{old: new for old, new, _harness, _role in _V160_RENAME_MATRIX},
    **{
        "beacon-prd": "beacon-gen-truth",
        "beacon-user-story": "beacon-gen-truth",
        "beacon-test-case": "beacon-gen-truth",
    },
    **_V160_INTERNAL_PLANNER_ALIAS_REWRITE_MAP,
    **_V160_PREVIOUS_LONG_ALIAS_REWRITE_MAP,
    "beacon-eval-qa-evo-deep": "beacon-eval-qa-deep",
    "beacon-gen-change-refreeze": "beacon-gen-refreeze",
}
_V160_ROUTE_REWRITE_ORDER = tuple(sorted(_V160_ROUTE_REWRITE_MAP, key=len, reverse=True))
_V160_ROUTE_REFERENCE_ALLOW_MARKERS = (
    "migrated from",
    "来源迁移",
)
_V160_FORBIDDEN_ROUTE_PHRASES = (
    "old public skill names remain",
    "use the old skill names",
    "compatibility aliases remain available",
)
_BEACON_SKILL_BACKUP_PREFIXES = (
    ".beacon-v160-legacy-backup",
    ".beacon-v160-planner-deprecated-cleanup",
    ".beacon-legacy-cleanup",
)
_GLOBAL_LEGACY_SKILL_ROOTS = (
    "claude",
    "codex",
    "agents",
)

_V160_SHARED_PREAMBLE = """## Beacon v1.6.0 共享 Preamble

1. 先判断湖还是海：湖要煮干；海要拆分、标超纲或延后。
2. 先搜再造：推理前先读取 resolver 选中的 truth、source、evidence 和相关 memory。
3. 用户主权：Beacon 推荐路由；是否接受范围或把 queue item 升级为 truth/change 由用户决定。
4. 不假交付：placeholder implementation、docs-only completion、fake runner、zero assertions 或 placeholder evidence 不能算闭环。
5. Harness 边界：planner 不实现；generator 不裁决自身完成；evaluator 不改写 truth；governor 不成为主生命周期阶段。
"""

_V160_HARD_GATES = {
    "planner": """HARD GATE:
你正在运行 planner skill。
禁止调用 implementation/generator/evaluator/release 类 skill。
禁止写代码、搭脚手架、修改 package truth、修改 `.machine/`、给 QA/release verdict。
你的唯一产出是 research/planning artifact、gap/risk 分析、湖/海判断和 route recommendation。
如需进入 truth/change/refreeze/generate/evaluate，必须停止并路由，等待用户确认。""",
    "generator": """HARD GATE:
你正在运行 generator skill。
禁止自证完成，禁止给 QA/release verdict，禁止把 placeholder/docs-only/fake-runner/zero-assertion/placeholder-evidence 当成交付闭环。
只能在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact。
如需判断是否通过，必须路由到 evaluator。""",
    "evaluator": """HARD GATE:
你正在运行 evaluator skill。
禁止改写 requirement truth，禁止修复 implementation，禁止把 verdict 和 repair 混在同一动作里。
你的唯一产出是 evidence verdict、finding、reason code、block/pass/route recommendation。
如需修复，必须路由到 generator 或 truth/change。""",
    "governor": """HARD GATE:
你正在运行 governor skill。
禁止定义 requirement truth，禁止执行 implementation，禁止给 QA/release verdict，禁止成为主生命周期 stage。
你的唯一产出是 context/metadata/archive/hooks/automation/status/diagnostic support。
如发现 truth、implementation 或 gate 问题，只能路由。""",
}

_V160_REQUIRED_GATE_TERMS = {
    "planner": ("禁止调用", "implementation", "generator", "evaluator", "release", "禁止写代码", "搭脚手架", "package truth", ".machine", "QA/release verdict", "唯一产出"),
    "generator": ("禁止自证完成", "禁止给 QA/release verdict", "placeholder", "docs-only", "fake-runner", "zero-assertion", "placeholder-evidence", "resolver-selected truth", "只能在", "truth 或 delivery artifact", "evaluator"),
    "evaluator": ("禁止改写 requirement truth", "禁止修复 implementation", "verdict", "repair", "唯一产出", "reason code", "block/pass/route recommendation"),
    "governor": ("禁止定义 requirement truth", "禁止执行 implementation", "禁止给 QA/release verdict", "禁止成为主生命周期 stage", "唯一产出", "context/metadata/archive/hooks/automation/status/diagnostic support"),
}


def _semver_tuple(value: str | None) -> tuple[int, int, int]:
    text = str(value or "").strip().lower()
    if text.startswith("v"):
        text = text[1:]
    numbers: list[int] = []
    for part in text.split(".")[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits or "0"))
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers[:3])


def _uses_v160_taxonomy(docs_version: str | None, runtime_version: str | None = None) -> bool:
    target = docs_version or runtime_version
    return _semver_tuple(target) >= (1, 6, 0)


def _v160_rows() -> list[dict[str, str]]:
    return [
        {"old": old, "new": new, "harness": harness, "role": role}
        for old, new, harness, role in _V160_RENAME_MATRIX
    ]


def v160_rename_matrix() -> list[dict[str, str]]:
    """Return the public v1.6.0 old-to-new skill rename matrix."""
    return _v160_rows()


def default_v160_skill_package_root(project_root: Path | str, version: str = _V160_TAXONOMY_VERSION) -> Path:
    """Return the default versioned v1.6.0 generated skill package root."""
    return Path(project_root).resolve() / "docs" / "beacon" / version / ".generated" / "skills" / "beacon"


def _harness_from_skill_id(skill_id: str) -> str:
    if skill_id in _V160_PUBLIC_GOVERNOR_SKILLS:
        return "governor"
    parts = skill_id.split("-")
    if len(parts) < 3 or parts[0] != "beacon":
        return ""
    return _V160_HARNESS_CODES.get(parts[1], "")


def _v160_frontmatter_name(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        return ""
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return ""


def _render_v160_skill(row: dict[str, str]) -> str:
    skill_id = row["new"]
    old_id = row["old"]
    harness = row["harness"]
    role = row["role"]
    gate = _V160_HARD_GATES[harness]
    title = skill_id.replace("-", " ").title()
    return f"""---
name: {skill_id}
description: Beacon v1.6.0 {harness} skill。用于{role}；必须遵守共享 preamble 和 HARD GATE，不能越过本 harness 边界。
---

# {title}

{_V160_SHARED_PREAMBLE}
{gate}

## 职责

- Harness：`{harness}`。
- 来源迁移：`{old_id}` -> `{skill_id}`。
- 主要作用：{role}。
- 默认语言：中文为主；英文只用于稳定术语、路径、命令或协议标识。

## 边界

- Planner 只产出 research/planning artifact 和 route recommendation，不写 truth、implementation、QA verdict 或 release verdict。
- Generator 只在 resolver-selected truth、用户已接受 scope 和本 skill authority 内写 truth 或 delivery artifact，不自证完成。
- Evaluator 只产出 evidence verdict、finding、reason code 和 route recommendation，不改 truth、不修 implementation。
- Governor 只维护 context、metadata、archive、hooks、automation、status 和 diagnostic support，不成为主生命周期 stage。

## 路由

- 粗提示词先归约为 outcome、truth/source/evidence refs、湖/海、truth_gap、test_gap、implementation_risk、verification_risk 和 recommended_route。
- `docs/beacon/<version>/research/<feature-slug>.md` 是 planner `support_advisory` artifact；没有用户确认和 `promotion_ref`，不能升级为 requirement truth。
- 需要跨 harness 时，停止当前动作，输出 route recommendation，并等待用户确认。
	"""


def _v160_allows_legacy_route_reference(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in _V160_ROUTE_REFERENCE_ALLOW_MARKERS)


def _replace_exact_skill_id(text: str, old: str, new: str) -> str:
    pattern = rf"(?<![A-Za-z0-9_-]){re.escape(old)}(?![A-Za-z0-9_-])"
    return re.sub(pattern, new, text)


def normalize_v160_skill_content(text: str) -> str:
    """Rewrite v1.6.0 host-visible route references to compact canonical skill names."""
    normalized_lines: list[str] = []
    for raw_line in text.splitlines(keepends=True):
        line = raw_line.rstrip("\n")
        newline = raw_line[len(line):]
        if _v160_allows_legacy_route_reference(line):
            normalized_lines.append(raw_line)
            continue
        normalized = line
        normalized = normalized.replace("## Compatibility Aliases", "## Canonical v1.6.0 Routes")
        normalized = normalized.replace("Compatibility aliases remain available", "Canonical v1.6.0 routes")
        normalized = normalized.replace("compatibility aliases remain available", "canonical v1.6.0 routes")
        normalized = normalized.replace("Compatibility aliases are", "Canonical v1.6.0 routes are")
        normalized = normalized.replace("compatibility aliases are", "canonical v1.6.0 routes are")
        normalized = normalized.replace("Compatibility alias:", "Canonical v1.6.0 route:")
        normalized = normalized.replace("compatibility alias:", "canonical v1.6.0 route:")
        normalized = normalized.replace("compatibility alias", "canonical v1.6.0 route")
        normalized = normalized.replace(
            "`beacon-gen-truth`, `beacon-gen-truth`, `beacon-gen-truth`, and `beacon-gen-change`",
            "`beacon-gen-truth` for truth definition/acceptance/coverage and `beacon-gen-change` for truth changes",
        )
        normalized = normalized.replace(
            "`beacon-gen-truth`, `beacon-gen-truth`, or `beacon-gen-truth`",
            "`beacon-gen-truth`",
        )
        normalized = normalized.replace(
            "Use the old skill names when invoking stable compatibility surfaces.",
            "Use compact skill names for host-visible routing; use CLI commands only for stable compatibility command surfaces.",
        )
        normalized = normalized.replace(
            "Old public skill names remain canonical v1.6.0 routees and must continue to work.",
            "Old public skill names do not remain host-visible routees in v1.6.0; compact names are canonical.",
        )
        normalized = normalized.replace(
            "route back to `implement`, `test-case`, or `change`",
            "route to `beacon-gen-implement`, `beacon-gen-truth` for coverage, or `beacon-gen-change`",
        )
        normalized = normalized.replace("route back to `implement`", "route to `beacon-gen-implement`")
        normalized = normalized.replace("route to `change`", "route to `beacon-gen-change`")
        normalized = normalized.replace("route to `test-case`", "route to `beacon-gen-truth` for coverage")
        normalized = normalized.replace("handing off to `release`", "handing off to `beacon-eval-release`")
        normalized = normalized.replace(
            "blocks `implement` / `qa` / `release`",
            "blocks `beacon-gen-implement` / `beacon-eval-qa` / `beacon-eval-release`",
        )
        for old in _V160_ROUTE_REWRITE_ORDER:
            normalized = _replace_exact_skill_id(normalized, old, _V160_ROUTE_REWRITE_MAP[old])
        normalized_lines.append(normalized + newline)
    normalized_text = "".join(normalized_lines)
    for route in sorted(set(_V160_ROUTE_REWRITE_MAP.values())):
        duplicate = f"- `{route}`\n- `{route}`\n"
        while duplicate in normalized_text:
            normalized_text = normalized_text.replace(duplicate, f"- `{route}`\n")
    return normalized_text


def _v160_skill_content_route_errors(text: str) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if _v160_allows_legacy_route_reference(line):
            continue
        lowered = line.lower()
        for phrase in _V160_FORBIDDEN_ROUTE_PHRASES:
            if phrase in lowered:
                errors.append(f"line {line_number}: stale route phrase `{phrase}` must use compact canonical route language")
        for old in _V160_ROUTE_REWRITE_ORDER:
            if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(old)}(?![A-Za-z0-9_-])", line):
                replacement = _V160_ROUTE_REWRITE_MAP[old]
                errors.append(f"line {line_number}: stale route reference `{old}` should be `{replacement}`")
    return errors


def _write_projected_skill(destination: Path, content: str, files: dict[str, str] | None = None) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "SKILL.md").write_text(content, encoding="utf-8")
    for relative, file_content in (files or {}).items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_content, encoding="utf-8")


def _copy_projected_skill(destination: Path, projection: SkillProjection) -> None:
    skill_content = projection.content
    if skill_content is not None:
        skill_content = inject_git_admission_into_skill_text(projection.id, skill_content)
    if projection.source_dir is not None:
        shutil.copytree(projection.source_dir, destination)
        if skill_content is not None:
            (destination / "SKILL.md").write_text(skill_content, encoding="utf-8")
        for relative, file_content in (projection.files or {}).items():
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file_content, encoding="utf-8")
        return
    if skill_content is not None:
        _write_projected_skill(destination, skill_content, projection.files)
        return
    raise ValueError(f"skill projection {projection.id} has no source")


def _hash_projected_source_dir(source_dir: Path, *, skill_text: str) -> str:
    digest = hashlib.sha256()
    files = sorted(node for node in source_dir.rglob("*") if node.is_file())
    for file_path in files:
        relative = file_path.relative_to(source_dir).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        if relative == "SKILL.md":
            digest.update(skill_text.encode("utf-8"))
        else:
            digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _projected_content_hash(skill_id: str, content: str, files: dict[str, str] | None = None) -> str:
    digest = hashlib.sha256()
    digest.update(b"SKILL.md\0")
    digest.update(content.encode("utf-8"))
    digest.update(b"\0")
    for relative, file_content in sorted((files or {}).items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_content.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _v160_extra_skill_files(skill_id: str) -> dict[str, str]:
    if skill_id != "beacon-gen-implement":
        return {}
    return {
        "references/implement-single.md": """# Implement Single Mode

## Purpose

Use `single` for small, low-risk, clearly scoped implementation under `beacon-gen-implement`.

## Admission

- Requirement truth is frozen.
- Scope is narrow and low-risk.
- Role separation is not needed.
- Multi-round closure control is not needed.

## Command

```bash
beacon implement run "<feature>" --project . --version <version> --mode single
```

## Evidence

- Implementation summary.
- Changed file list.
- QA handoff when implementation evidence is ready.

## Boundary

Single mode cannot rewrite frozen truth, run QA, pass release, or override gate verdicts.
""",
        "references/implement-team.md": """# Implement Team Mode

## Purpose

Use `team` for complex implementation that benefits from role separation, subagent lanes, or parallel evidence.

## Admission

- Requirement truth is frozen.
- Implementation spans multiple modules or concerns.
- Planner / implementer / reviewer / tester separation is useful.
- QA handoff needs role-specific context.

## Command

```bash
beacon implement run "<feature>" --project . --version <version> --mode team
```

## Evidence

- Team plan and role evidence.
- Implementation handoff.
- Review or QA readiness notes.

## Boundary

Team mode remains internal runtime behavior under `beacon-gen-implement`; it is not a public lifecycle skill and does not produce QA or release verdicts.
""",
        "references/implement-ralph.md": """# Implement Ralph Mode

## Purpose

Use `ralph` as a closure controller when team or complex implementation evidence needs multi-round repair routing toward review, QA, or release.

## Admission

- Requirement truth is frozen.
- Team or complex implementation has produced evidence, but closure is not authoritative.
- Review quality, QA, or release next action must be routed.
- Ralph can record blocker, next action, round trace, and evidence refs.

## Command

```bash
beacon implement run "<feature>" --project . --version <version> --mode ralph
```

## Evidence

- Ralph round trace.
- Current blocker and next action.
- Recommended command for implement repair, QA, or release.

## Boundary

Ralph routes next action and evidence only; it never replaces QA, release, gate, or frozen truth.
""",
    }


def _v160_skill_projections() -> list[SkillProjection]:
    projections: list[SkillProjection] = []
    source_root = packaged_beacon_skill_root()
    for row in _v160_rows():
        source_skill = source_root / row["new"]
        if (source_skill / "SKILL.md").exists():
            normalized_content = normalize_v160_skill_content((source_skill / "SKILL.md").read_text(encoding="utf-8"))
            normalized_content = inject_git_admission_into_skill_text(row["new"], normalized_content)
            projections.append(
                SkillProjection(
                    id=row["new"],
                    source_path=str(source_skill.relative_to(source_root)),
                    source_hash=_hash_projected_source_dir(source_skill, skill_text=normalized_content),
                    source_kind="migrated_v160_harness_taxonomy_preserve_skill_content",
                    content=normalized_content,
                    source_dir=source_skill,
                )
            )
            continue
        content = _render_v160_skill(row)
        content = inject_git_admission_into_skill_text(row["new"], content)
        extra_files = _v160_extra_skill_files(row["new"])
        projections.append(
            SkillProjection(
                id=row["new"],
                source_path=row["old"],
                source_hash=_projected_content_hash(row["new"], content, extra_files),
                source_kind="generated_v160_harness_taxonomy_fallback",
                content=content,
                files=extra_files,
            )
        )
    projections = _append_v160_native_packaged_projections(projections, source_root, _V160_PUBLIC_PLANNER_SKILLS)
    projections = _append_v160_native_packaged_projections(projections, source_root, _V160_PUBLIC_EVALUATOR_SKILLS)
    projections = _append_v160_native_packaged_projections(projections, source_root, _V160_PUBLIC_GOVERNOR_SKILLS)
    return sorted(projections, key=lambda item: item.id)


def _append_v160_native_packaged_projections(
    projections: list[SkillProjection],
    source_root: Path,
    skill_ids: tuple[str, ...],
) -> list[SkillProjection]:
    """Include net-new packaged skills under skills/beacon/ but absent from rename matrix."""
    existing_ids = {item.id for item in projections}
    extra: list[SkillProjection] = []
    for skill_id in skill_ids:
        if skill_id in existing_ids:
            continue
        source_skill = source_root / skill_id
        if not (source_skill / "SKILL.md").exists():
            continue
        normalized_content = normalize_v160_skill_content((source_skill / "SKILL.md").read_text(encoding="utf-8"))
        normalized_content = inject_git_admission_into_skill_text(skill_id, normalized_content)
        extra.append(
            SkillProjection(
                id=skill_id,
                source_path=str(source_skill.relative_to(source_root)),
                source_hash=_hash_projected_source_dir(source_skill, skill_text=normalized_content),
                source_kind="migrated_v160_harness_taxonomy_preserve_skill_content",
                content=normalized_content,
                source_dir=source_skill,
            )
        )
    return projections + extra


def v160_skill_package_projection() -> list[SkillProjection]:
    """Return generated v1.6.0 host-visible skill projections."""
    return _v160_skill_projections()


def _legacy_skill_projections(source_root: Path) -> list[SkillProjection]:
    projections: list[SkillProjection] = []
    for source_skill in list_host_visible_skills(source_root):
        projections.append(
            SkillProjection(
                id=source_skill.name,
                source_path=str(source_skill.relative_to(source_root)),
                source_hash=_hash_directory(source_skill),
                source_kind="packaged_skill_directory",
                source_dir=source_skill,
            )
        )
    return projections


def _expected_skill_projections(source_root: Path, *, runtime_version: str, docs_version: str | None = None) -> list[SkillProjection]:
    if _uses_v160_taxonomy(docs_version, runtime_version):
        return _v160_skill_projections()
    return _legacy_skill_projections(source_root)


def _verify_v160_skill_content(skill_id: str, text: str) -> list[str]:
    errors: list[str] = []
    harness = _harness_from_skill_id(skill_id)
    if harness not in _V160_HARNESSES:
        errors.append("skill name must match beacon-(pln|gen|eval|gov)-<function>")
    if _v160_frontmatter_name(text) != skill_id:
        errors.append("frontmatter name must match directory name")
    preamble_index = text.find(_V160_SHARED_PREAMBLE)
    if preamble_index < 0:
        errors.append("shared preamble missing")
    gate = _V160_HARD_GATES.get(harness, "")
    gate_index = text.find(gate) if gate else -1
    if gate_index < 0:
        errors.append("harness HARD GATE missing or mismatched")
    elif preamble_index >= 0 and gate_index < preamble_index + len(_V160_SHARED_PREAMBLE):
        errors.append("HARD GATE must appear after shared preamble")
    for term in _V160_REQUIRED_GATE_TERMS.get(harness, ()):
        if term not in text:
            errors.append(f"HARD GATE missing required term: {term}")
    if skill_id in TIER_A_SKILLS:
        if "GIT_ADMISSION" not in text or "workspace admit" not in text:
            errors.append("GIT_ADMISSION preamble missing for Tier A skill")
    if skill_id in TRUTH_AUTHORING_SKILLS:
        if "GIT_ADMISSION" not in text or "truth_canonical" not in text:
            errors.append("GIT_ADMISSION preamble missing for truth authoring skill")
    return errors


def _is_beacon_skill_backup_dir(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in _BEACON_SKILL_BACKUP_PREFIXES)


def _collect_beacon_skill_backup_dirs(skills_root: Path) -> list[Path]:
    if not skills_root.exists():
        return []
    return sorted(
        (item for item in skills_root.iterdir() if item.is_dir() and _is_beacon_skill_backup_dir(item.name)),
        key=lambda item: item.name,
    )


def _remove_beacon_skill_backup_dirs(skills_root: Path, *, dry_run: bool) -> list[str]:
    removed: list[str] = []
    for backup_dir in _collect_beacon_skill_backup_dirs(skills_root):
        removed.append(str(backup_dir))
        if not dry_run:
            shutil.rmtree(backup_dir)
    return removed


def _remove_skill_path(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)
        return
    if path.exists():
        path.unlink()


def global_claude_skills_root(home: Path | None = None) -> Path:
    """Return Claude Code global skill discovery root."""
    return (home or Path.home()).expanduser() / ".claude" / "skills"


def install_global_claude_beacon_skills(
    *,
    beacon_root: Path | str | None = None,
    dry_run: bool = False,
    home: Path | None = None,
) -> dict[str, Any]:
    """Install flat ~/.claude/skills/beacon-* symlinks required for Claude Code discovery."""
    skills_source = packaged_beacon_skill_root()
    default_repo_root = skills_source.parent.parent.resolve()
    repo_root = default_repo_root
    if beacon_root is not None:
        candidate = Path(beacon_root).resolve()
        if (candidate / "skills" / "beacon").exists():
            repo_root = candidate
    claude_dir = global_claude_skills_root(home)
    source_skills = list_host_visible_skills(skills_source)
    installed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    if not dry_run:
        claude_dir.mkdir(parents=True, exist_ok=True)

    canonical = claude_dir / "beacon"
    canonical_action = "unchanged"
    if not canonical.exists():
        canonical_action = "planned" if dry_run else "created"
        if not dry_run:
            if canonical.is_symlink() or canonical.exists():
                _remove_skill_path(canonical)
            canonical.symlink_to(repo_root)
    elif canonical.is_symlink() and canonical.resolve() != repo_root.resolve():
        canonical_action = "planned" if dry_run else "updated"
        if not dry_run:
            canonical.unlink()
            canonical.symlink_to(repo_root)
    installed.append(
        {
            "id": "beacon",
            "path": str(canonical),
            "target": str(repo_root),
            "action": canonical_action,
        }
    )

    for source_skill in source_skills:
        skill_id = source_skill.name
        destination = claude_dir / skill_id
        source_path = (skills_source / skill_id).resolve()
        action = "unchanged"
        if not destination.exists():
            action = "planned" if dry_run else "created"
        elif destination.is_symlink() and destination.resolve() != source_path:
            action = "planned" if dry_run else "updated"
        elif destination.is_dir() and not destination.is_symlink():
            skipped.append({"id": skill_id, "path": str(destination), "reason": "unmanaged_existing_directory"})
            continue

        if action != "unchanged":
            if not dry_run:
                if destination.exists() or destination.is_symlink():
                    _remove_skill_path(destination)
                destination.symlink_to(source_path)
        installed.append(
            {
                "id": skill_id,
                "path": str(destination),
                "target": str(source_path),
                "action": action,
            }
        )

    return {
        "skills_root": str(claude_dir),
        "repo_root": str(repo_root),
        "source_root": str(skills_source),
        "installed": installed,
        "skipped": skipped,
        "installed_count": len(installed),
        "skipped_count": len(skipped),
        "dry_run": dry_run,
    }


def verify_global_claude_beacon_skills(*, home: Path | None = None) -> dict[str, Any]:
    """Verify Claude Code global flat beacon-* symlinks match packaged host-visible skills."""
    skills_source = packaged_beacon_skill_root()
    repo_root = skills_source.parent.parent.resolve()
    claude_dir = global_claude_skills_root(home)
    expected_ids = {item.name for item in list_host_visible_skills(skills_source)}
    missing: list[str] = []
    wrong_target: list[dict[str, str]] = []

    canonical = claude_dir / "beacon"
    canonical_ok = canonical.is_symlink() and canonical.resolve() == repo_root
    if not canonical_ok:
        missing.append("beacon")

    for skill_id in sorted(expected_ids):
        link = claude_dir / skill_id
        expected_path = (skills_source / skill_id).resolve()
        if not link.is_symlink():
            missing.append(skill_id)
            continue
        if link.resolve() != expected_path:
            wrong_target.append(
                {
                    "id": skill_id,
                    "path": str(link),
                    "expected": str(expected_path),
                    "actual": str(link.resolve()),
                }
            )

    status = "pass" if canonical_ok and not missing and not wrong_target else "fail"
    return {
        "status": status,
        "ok": status == "pass",
        "skills_root": str(claude_dir),
        "expected_count": len(expected_ids) + 1,
        "missing": missing,
        "wrong_target": wrong_target,
    }


def _remove_global_canonical_beacon_duplicates(skills_root: Path, *, dry_run: bool) -> list[str]:
    """Drop materialized beacon-* copies when a global host root already keeps canonical `beacon`."""
    removed: list[str] = []
    if not skills_root.exists():
        return removed
    canonical = skills_root / "beacon"
    if not (canonical.is_symlink() or canonical.is_dir()):
        return removed
    for child in sorted(skills_root.iterdir(), key=lambda item: item.name):
        name = child.name
        if name == "beacon" or not name.startswith("beacon-"):
            continue
        if not (child.is_dir() or child.is_symlink()):
            continue
        removed.append(str(child))
        if not dry_run:
            _remove_skill_path(child)
    return removed


def _global_legacy_skill_roots(home: Path | None = None) -> dict[str, Path]:
    base = (home or Path.home()).expanduser()
    return {
        "claude": base / ".claude" / "skills",
        "codex": base / ".codex" / "skills",
        "agents": base / ".agents" / "skills",
    }


def cleanup_legacy_beacon_skills(
    project_root: Path | str,
    *,
    agent: str = "all",
    scope: str = "all",
    runtime_version: str,
    docs_version: str | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Remove v1.6.0 backup trees and pre-taxonomy Beacon skill aliases from agent skill roots."""
    root = Path(project_root).resolve()
    source_skills = _expected_skill_projections(
        packaged_beacon_skill_root(),
        runtime_version=runtime_version,
        docs_version=docs_version,
    )
    expected_ids = {item.id for item in source_skills}
    v160_taxonomy = _uses_v160_taxonomy(docs_version, runtime_version)
    targets: list[tuple[str, Path]] = []

    normalized_scope = str(scope or "all").strip().lower()
    normalized_agent = str(agent or "all").strip().lower()
    if normalized_scope in {"project", "all"}:
        agents = ("trae", "claude", "codex", "cursor", "windsurf") if normalized_agent == "all" else (normalized_agent,)
        for agent_name in agents:
            target = resolve_agent_surface_target(root, agent_name)
            targets.append((f"project:{agent_name}", target.skills_root))
    if normalized_scope in {"global", "all"}:
        for label, skills_root in _global_legacy_skill_roots().items():
            if normalized_agent not in {"all", label, "codex"}:
                continue
            if normalized_agent == "codex" and label not in {"codex", "agents"}:
                continue
            targets.append((f"global:{label}", skills_root))

    removed: list[dict[str, Any]] = []
    for target_label, skills_root in targets:
        if not skills_root.exists():
            continue
        for backup_dir in _collect_beacon_skill_backup_dirs(skills_root):
            removed.append({"target": target_label, "path": str(backup_dir), "kind": "backup"})
            if not dry_run:
                shutil.rmtree(backup_dir)
        if target_label.startswith("global:"):
            host_kind = target_label.split(":", 1)[1]
            # Claude Code only discovers first-level ~/.claude/skills/beacon-* symlinks.
            if host_kind != "claude":
                for duplicate_path in _remove_global_canonical_beacon_duplicates(skills_root, dry_run=dry_run):
                    removed.append(
                        {"target": target_label, "path": duplicate_path, "kind": "global_materialized_duplicate"}
                    )
        if not v160_taxonomy:
            continue
        for child in sorted(skills_root.iterdir(), key=lambda item: item.name):
            name = child.name
            if name == "beacon":
                continue
            if child.is_file():
                if force and (name.startswith("beacon-") or name in {"using-beacon", "beacon-cli"}):
                    removed.append({"target": target_label, "path": str(child), "kind": "legacy_file"})
                    if not dry_run:
                        _remove_skill_path(child)
                continue
            if not (child.is_dir() or child.is_symlink()):
                continue
            stale = name in _V160_OLD_ALIAS_IDS or name == "using-beacon"
            unexpected = (name.startswith("beacon-") or name == "using-beacon") and name not in expected_ids
            if stale or (force and unexpected):
                removed.append({"target": target_label, "path": str(child), "kind": "legacy_alias" if stale else "unexpected"})
                if not dry_run:
                    _remove_skill_path(child)

    return {
        "project_root": str(root),
        "scope": normalized_scope,
        "agent": normalized_agent,
        "dry_run": dry_run,
        "force": force,
        "taxonomy_version": _V160_TAXONOMY_VERSION if v160_taxonomy else "",
        "removed": removed,
        "removed_count": len(removed),
    }


def _verify_v160_surface(target: AgentSurfaceTarget, expected_ids: list[str]) -> dict[str, Any]:
    backup_dirs = sorted(item.name for item in _collect_beacon_skill_backup_dirs(target.skills_root))
    unexpected = sorted(
        item.name
        for item in target.skills_root.iterdir()
        if (item.is_dir() or item.is_symlink())
        and (item.name.startswith("beacon-") or item.name == "using-beacon")
        and item.name not in expected_ids
    ) if target.skills_root.exists() else []
    old_aliases = sorted(
        item.name
        for item in target.skills_root.iterdir()
        if (item.is_dir() or item.is_symlink()) and item.name in _V160_OLD_ALIAS_IDS
    ) if target.skills_root.exists() else []
    wrong_names = [skill_id for skill_id in expected_ids if _harness_from_skill_id(skill_id) not in _V160_HARNESSES]
    gate_errors: dict[str, list[str]] = {}
    route_errors: dict[str, list[str]] = {}
    for skill_id in expected_ids:
        skill_file = target.skills_root / skill_id / "SKILL.md"
        if not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8")
        errors = _verify_v160_skill_content(skill_id, text)
        if errors:
            gate_errors[skill_id] = errors
        stale_route_errors = _v160_skill_content_route_errors(text)
        if stale_route_errors:
            route_errors[skill_id] = stale_route_errors
    return {
        "backup_dirs": backup_dirs,
        "unexpected": unexpected,
        "old_aliases": old_aliases,
        "wrong_names": wrong_names,
        "gate_errors": gate_errors,
        "route_errors": route_errors,
    }


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def materialize_v160_skill_package(
    project_root: Path | str,
    *,
    output_root: Path | str | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Materialize the generated v1.6.0 breaking skill package into a versioned package root."""
    root = Path(project_root).resolve()
    package_root = Path(output_root).resolve() if output_root else default_v160_skill_package_root(root)
    projections = _v160_skill_projections()
    expected_ids = [item.id for item in projections]
    installed: list[dict[str, Any]] = []
    removed: list[str] = []
    skipped: list[dict[str, Any]] = []
    warnings: list[str] = []

    if not dry_run:
        package_root.mkdir(parents=True, exist_ok=True)

    if package_root.exists():
        for child in sorted(package_root.iterdir(), key=lambda item: item.name):
            if not child.is_dir():
                continue
            if child.name in expected_ids:
                continue
            if child.name in _V160_OLD_ALIAS_IDS or child.name.startswith("beacon-") or child.name == "using-beacon":
                if force or child.name in _V160_OLD_ALIAS_IDS:
                    removed.append(_relative_or_absolute(child, root))
                    if not dry_run:
                        shutil.rmtree(child)
                else:
                    skipped.append({"id": child.name, "path": str(child), "reason": "unexpected_existing_directory"})
                    warnings.append(f"{child.name} exists in v1.6.0 package but is not expected")

    for projection in projections:
        destination = package_root / projection.id
        existed = destination.exists()
        current_hash = _hash_directory(destination) if existed else ""
        if existed and current_hash and current_hash != projection.source_hash and not force:
            skipped.append({"id": projection.id, "path": str(destination), "reason": "existing_directory_differs_use_force"})
            warnings.append(f"{projection.id} skipped because generated output differs and --force was not used")
            continue
        action = "unchanged"
        if not existed:
            action = "planned" if dry_run else "created"
        elif current_hash != projection.source_hash:
            action = "planned" if dry_run else "updated"
        if action != "unchanged" and not dry_run:
            if destination.exists():
                shutil.rmtree(destination)
            _copy_projected_skill(destination, projection)
        installed.append(
            {
                "id": projection.id,
                "path": str(destination),
                "action": action,
                "source_path": projection.source_path,
                "source_kind": projection.source_kind,
                "source_hash": projection.source_hash,
            }
        )

    metadata = {
        "schema_version": "1.0",
        "name": "beacon",
        "version": _V160_TAXONOMY_VERSION,
        "source_kind": "migrated_v160_harness_taxonomy_preserve_skill_content",
        "generated_at": now_iso(),
        "expected_skill_count": len(expected_ids),
        "host_visible_skill_names": expected_ids,
        "old_aliases_removed": sorted(_V160_OLD_ALIAS_IDS),
        "rename_matrix": _v160_rows(),
        "authority": "generated_skill_package",
        "truth_ref": "docs/beacon/v1.6.0/features/beacon-skill-harness-taxonomy-v160/truth.md",
        "content_preservation": {
            "policy": "compact harness skill directories preserve full pre-v1.6.0 SKILL.md body plus v1.6.0 preamble and HARD GATE",
            "baseline_ref": "main:skills/beacon",
            "legacy_truth_refs": [
                "skills/beacon/beacon-gen-truth/references/legacy-beacon-prd.md",
                "skills/beacon/beacon-gen-truth/references/legacy-beacon-user-story.md",
                "skills/beacon/beacon-gen-truth/references/legacy-beacon-test-case.md",
            ],
        },
    }
    metadata_path = package_root / "metadata.json"
    if not dry_run:
        write_json(metadata_path, metadata)

    if dry_run:
        verify = {
            "schema_version": "1.0",
            "status": "planned",
            "ok": True,
            "package_root": str(package_root),
            "checks": [],
        }
        status = "planned" if not skipped else "warn"
    else:
        verify = verify_v160_skill_package(root, package_root=package_root, strict=True)
        status = "pass" if verify["ok"] and not skipped else "warn" if verify["ok"] else "fail"
    return {
        "schema_version": "1.0",
        "status": status,
        "ok": status != "fail",
        "project_root": str(root),
        "package_root": str(package_root),
        "metadata_path": str(metadata_path),
        "dry_run": dry_run,
        "force": force,
        "installed": installed,
        "removed": removed,
        "skipped": skipped,
        "warnings": warnings,
        "verify": verify,
    }


def verify_v160_skill_package(
    project_root: Path | str,
    *,
    package_root: Path | str | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """Verify a versioned v1.6.0 host-visible skill package."""
    root = Path(project_root).resolve()
    resolved_package_root = Path(package_root).resolve() if package_root else default_v160_skill_package_root(root)
    projections = _v160_skill_projections()
    expected_ids = [item.id for item in projections]
    target = AgentSurfaceTarget(agent="skill-package", skills_root=resolved_package_root)
    missing: list[str] = []
    drifted: list[str] = []
    for projection in projections:
        destination = resolved_package_root / projection.id
        if not destination.exists():
            missing.append(projection.id)
            continue
        if projection.source_hash != _hash_directory(destination):
            drifted.append(projection.id)
    v160_surface = _verify_v160_surface(target, expected_ids)
    metadata_path = resolved_package_root / "metadata.json"
    metadata: dict[str, Any] = {}
    metadata_errors: list[str] = []
    if metadata_path.exists():
        try:
            loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata = loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            metadata_errors.append("metadata_json_invalid")
    else:
        metadata_errors.append("metadata_missing")
    if metadata and str(metadata.get("version") or "") != _V160_TAXONOMY_VERSION:
        metadata_errors.append("metadata_version_mismatch")
    if metadata and str(metadata.get("source_kind") or "") not in _V160_PACKAGE_SOURCE_KINDS:
        metadata_errors.append("metadata_source_kind_mismatch")

    checks = [
        {
            "name": "package_root_present",
            "status": "pass" if resolved_package_root.exists() else "fail",
            "details": {"path": str(resolved_package_root), "exists": resolved_package_root.exists()},
        },
        {
            "name": "v160_expected_skills_present",
            "status": "pass" if not missing else "fail",
            "details": {"expected": expected_ids, "missing": missing},
        },
        {
            "name": "v160_generated_skill_drift",
            "status": "pass" if not drifted else ("fail" if strict else "warn"),
            "details": {"drifted": drifted},
        },
        {
            "name": "v160_harness_skill_names",
            "status": "pass" if not v160_surface["wrong_names"] else "fail",
            "details": {"wrong_names": v160_surface["wrong_names"]},
        },
        {
            "name": "v160_no_old_host_visible_aliases",
            "status": "pass" if not v160_surface["old_aliases"] and not v160_surface["unexpected"] else "fail",
            "details": {"old_aliases": v160_surface["old_aliases"], "unexpected": v160_surface["unexpected"]},
        },
        {
            "name": "v160_shared_preamble_and_hard_gates",
            "status": "pass" if not v160_surface["gate_errors"] else "fail",
            "details": {"gate_errors": v160_surface["gate_errors"]},
        },
        {
            "name": "v160_canonical_route_references",
            "status": "pass" if not v160_surface["route_errors"] else "fail",
            "details": {"route_errors": v160_surface["route_errors"]},
        },
        {
            "name": "v160_package_metadata",
            "status": "pass" if not metadata_errors else "fail",
            "details": {"path": str(metadata_path), "errors": metadata_errors},
        },
    ]
    status = "pass"
    if any(str(item.get("status")) == "fail" for item in checks):
        status = "fail"
    elif any(str(item.get("status")) == "warn" for item in checks):
        status = "warn"
    return {
        "schema_version": "1.0",
        "status": status,
        "ok": status != "fail",
        "project_root": str(root),
        "package_root": str(resolved_package_root),
        "strict": strict,
        "taxonomy_version": _V160_TAXONOMY_VERSION,
        "expected_skill_count": len(expected_ids),
        "checks": checks,
    }


def _parse_markdown_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        normalized = line.lstrip("-*").strip()
        if ":" in normalized:
            key, value = normalized.split(":", 1)
        elif "：" in normalized:
            key, value = normalized.split("：", 1)
        else:
            continue
        key = key.strip().strip("`").lower().replace("-", "_").replace(" ", "_")
        values[key] = value.strip().strip("`")
    return values


def _field_has_value(values: dict[str, str], field: str) -> bool:
    value = values.get(field, "").strip()
    return bool(value) and value.lower() not in {"n/a", "na", "none", "null", "todo", "tbd", "未定", "待定", "-"}


def _field_present(values: dict[str, str], field: str) -> bool:
    return field in values


def validate_v160_research_artifact(
    project_root: Path | str,
    *,
    version: str,
    feature: str,
    research_path: Path | str | None = None,
) -> dict[str, Any]:
    """Validate the v1.6.0 planner research support_advisory contract."""
    root = Path(project_root).resolve()
    path = Path(research_path).resolve() if research_path else root / "docs" / "beacon" / version / "research" / f"{feature}.md"
    issues: list[dict[str, str]] = []
    values: dict[str, str] = {}
    if not path.exists():
        issues.append({"code": "research_artifact_missing", "message": "planner research artifact missing"})
    else:
        text = path.read_text(encoding="utf-8")
        values = _parse_markdown_key_values(text)
        authority = values.get("authority", "").strip()
        if authority != "support_advisory":
            issues.append({"code": "authority_not_support_advisory", "message": "research authority must be support_advisory"})
        status = values.get("status", "").strip()
        if status and status not in _V160_ALLOWED_RESEARCH_STATUSES:
            issues.append({"code": "invalid_research_status", "message": f"research status must be one of {sorted(_V160_ALLOWED_RESEARCH_STATUSES)}"})
        for field in _V160_RESEARCH_REQUIRED_FIELDS:
            if field == "promotion_ref":
                valid = _field_present(values, field)
            else:
                valid = _field_has_value(values, field)
            if not valid:
                issues.append({"code": f"missing_{field}", "message": f"research field `{field}` is required"})
    promotion = _evaluate_v160_research_promotion(values)
    return {
        "schema_version": "1.0",
        "status": "pass" if not issues else "fail",
        "ok": not issues,
        "authority": "support_advisory",
        "truth_authority": False,
        "project_root": str(root),
        "version": version,
        "feature": feature,
        "research_path": str(path),
        "fields": values,
        "issues": issues,
        "promotion_gate": promotion,
    }


def _evaluate_v160_research_promotion(values: dict[str, str]) -> dict[str, Any]:
    decision = values.get("user_decision", "").strip().lower()
    promotion_ref = values.get("promotion_ref", "").strip()
    allowed = decision in _V160_PROMOTED_DECISIONS and bool(promotion_ref)
    reason_codes: list[str] = []
    if decision not in _V160_PROMOTED_DECISIONS:
        reason_codes.append("user_decision_not_accepted_or_promoted")
    if not promotion_ref:
        reason_codes.append("promotion_ref_missing")
    return {
        "status": "pass" if allowed else "blocked",
        "allowed": allowed,
        "decision": decision,
        "promotion_ref": promotion_ref,
        "reason_codes": reason_codes,
        "allowed_next": "truth/change/refreeze/generate/evaluate" if allowed else "queue/defer/await_user_decision",
    }


def verify_v160_research_promotion(
    project_root: Path | str,
    *,
    version: str,
    feature: str,
    research_path: Path | str | None = None,
) -> dict[str, Any]:
    """Verify whether a planner research artifact may be promoted into the main Beacon chain."""
    contract = validate_v160_research_artifact(project_root, version=version, feature=feature, research_path=research_path)
    gate = contract["promotion_gate"]
    status = "pass" if contract["ok"] and gate["allowed"] else "fail"
    return {
        "schema_version": "1.0",
        "status": status,
        "ok": status == "pass",
        "contract_status": contract["status"],
        "promotion_gate": gate,
        "issues": contract["issues"],
        "research_path": contract["research_path"],
        "authority": "support_advisory",
        "truth_authority": False,
    }


def build_v160_rough_prompt_route(
    prompt: str,
    *,
    truth_refs: list[str] | None = None,
    source_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic v1.6.0 rough prompt routing envelope."""
    text = " ".join(str(prompt or "").split())
    lowered = text.lower()
    broad_markers = ("整体", "完整", "全量", "重构", "全部", "everything", "whole", "all", "architecture")
    risky_markers = ("实现", "开发", "代码", "提交", "release", "发布", "qa", "验收")
    lake_or_ocean = "ocean" if any(marker in lowered for marker in broad_markers) or len(text) > 180 else "lake"
    route = "beacon-pln-brainstorm" if lake_or_ocean == "ocean" else "beacon-pln-source"
    if any(marker in lowered for marker in risky_markers):
        route = "beacon-pln-source"
    truth_gap = not truth_refs
    test_gap = not evidence_refs
    return {
        "schema_version": "1.0",
        "outcome": text or "未提供明确 outcome",
        "truth_refs": truth_refs or [],
        "source_refs": source_refs or [],
        "evidence_refs": evidence_refs or [],
        "lake_or_ocean": {
            "classification": lake_or_ocean,
            "reason": "范围较大或需要拆分" if lake_or_ocean == "ocean" else "范围可在单个受控链路内煮干",
        },
        "truth_gap": truth_gap,
        "test_gap": test_gap,
        "implementation_risk": "medium" if any(marker in lowered for marker in risky_markers) else "low",
        "verification_risk": "medium" if test_gap else "low",
        "recommended_route": route,
        "harness": "planner",
        "route_status": "routeable",
        "authority": "support_advisory",
    }


def verify_v160_no_fake_delivery(payload: dict[str, Any]) -> dict[str, Any]:
    """Reject fake-delivery signals as implementation, QA, or release closure."""
    text = json.dumps(payload, ensure_ascii=False).lower()
    detected: list[str] = []
    patterns = {
        "placeholder_implementation": r"placeholder[- ]implementation|占位实现|假实现",
        "placeholder_acceptance": r"placeholder[- ]acceptance|占位验收|placeholder ac|stub-only closure",
        "docs_only_completion": r"(?<!非)(?<!不)docs[- ]only[- ]completion|(?<!非)(?<!不)docs[- ]only(?!\s*闭环)|只写文档|文档完成",
        "fake_runner_evidence": r"fake[- ]runner[- ]evidence|fake[- ]runner|假 runner|假运行器",
        "zero_assertions": r"zero[- ]assertions|0 assertions|0 个断言|零断言",
        "placeholder_evidence": r"placeholder[- ]evidence|占位证据|假证据",
        "soft_test_only": r"soft[- ]test[- ]only|软占位验证",
        "pending_deferral": r"user_decision:\s*pending|\|\s*pending\s*\|",
        "implementation_claim_without_evidence": r"implementation claim without evidence|无证据声称完成",
    }
    for code, pattern in patterns.items():
        if re.search(pattern, text):
            detected.append(code)
    status = "fail" if detected else "pass"
    return {
        "schema_version": "1.0",
        "status": status,
        "ok": status == "pass",
        "closure_allowed": not detected,
        "detected": detected,
        "policy_terms": list(_V160_NO_FAKE_DELIVERY_TERMS),
        "reason_code": "fake_delivery_closure_blocked" if detected else "",
    }


# Canonical list of supported host agents. Single source of truth — post-release
# hook and other surfaces should iterate this, not hardcode a subset.
SUPPORTED_HOST_AGENTS: tuple[str, ...] = ("trae", "claude", "codex", "cursor", "windsurf")


def resolve_agent_surface_target(project_root: Path | str, agent: str) -> AgentSurfaceTarget:
    """Resolve project-local installation target for one supported agent."""
    root = Path(project_root).resolve()
    normalized = str(agent or "").strip().lower()
    if normalized == "winsurf":
        normalized = "windsurf"
    if normalized == "trae":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".trae" / "skills",
            rules_path=root / ".trae" / "rules" / "project_rules.md",
            rules_kind="markdown",
        )
    if normalized == "claude":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".claude" / "skills",
        )
    if normalized == "codex":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".agents" / "skills",
        )
    if normalized == "cursor":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".cursor" / "skills",
            rules_path=root / ".cursor" / "rules" / "beacon-agent-surface.mdc",
            rules_kind="cursor-mdc",
        )
    if normalized == "windsurf":
        return AgentSurfaceTarget(
            agent=normalized,
            skills_root=root / ".windsurf" / "skills",
            rules_path=root / ".windsurf" / "workflows" / "beacon-agent-surface.md",
            rules_kind="windsurf-workflow",
        )
    raise ValueError("agent must be one of: trae, claude, codex, cursor, windsurf")


def list_host_visible_skills(skill_root: Path | None = None) -> list[Path]:
    """List packaged Beacon host-visible skill directories."""
    base = (skill_root or packaged_beacon_skill_root()).resolve()
    skills = [
        child
        for child in base.iterdir()
        if child.is_dir() and (child / "SKILL.md").exists()
    ]
    return sorted(skills, key=lambda item: item.name)


def _hash_directory(path: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(node for node in path.rglob("*") if node.is_file())
    for file_path in files:
        relative = file_path.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_state(project_root: Path) -> dict[str, Any]:
    state_path = project_root / _STATE_PATH
    if not state_path.exists():
        return {"schema_version": "1.0", "agents": {}}
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": "1.0", "agents": {}}
    if not isinstance(payload, dict):
        return {"schema_version": "1.0", "agents": {}}
    agents = payload.get("agents")
    if not isinstance(agents, dict):
        payload["agents"] = {}
    return payload


def _write_state(project_root: Path, payload: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    state_path = project_root / _STATE_PATH
    existed = state_path.exists()
    current = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    next_content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    changed = current != next_content
    if not dry_run:
        write_json(state_path, payload)
    return {
        "path": str(state_path),
        "action": "planned" if dry_run else "updated" if existed else "created",
        "changed": changed or not existed,
    }


def _managed_skill_ids(agent_state: dict[str, Any]) -> set[str]:
    skills = agent_state.get("installed_skills")
    if not isinstance(skills, list):
        return set()
    return {
        str(item.get("id", "")).strip()
        for item in skills
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }


def _merge_managed_block(existing_content: str, managed_block: str) -> tuple[str, str]:
    current = existing_content or ""
    if not current.strip():
        return managed_block, "created"

    start_count = current.count(_RULE_BLOCK_START)
    end_count = current.count(_RULE_BLOCK_END)
    if start_count == 1 and end_count == 1:
        start_idx = current.find(_RULE_BLOCK_START)
        end_idx = current.find(_RULE_BLOCK_END) + len(_RULE_BLOCK_END)
        if current.lstrip().startswith("---") and managed_block.lstrip().startswith("---"):
            prefix = current[:start_idx].lstrip()
            if prefix.startswith("---") and prefix.count("---") >= 2:
                start_idx = 0
        return f"{current[:start_idx]}{managed_block}{current[end_idx:]}", "replaced"

    preserved = current.strip("\n")
    return f"{managed_block}\n\n{preserved}\n", "prepended"


def _skill_lines(skill_ids: list[str]) -> str:
    return "\n".join(f"- `{skill_id}`" for skill_id in skill_ids)


def _build_trae_rules_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    body = (
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Trae Project Rules\n\n"
        "- Prefer project-local Beacon skills under `.trae/skills/`.\n"
        "- Prefer `beacon <subcommand>` as the stable execution entry.\n"
        "- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "- If skill materialization drifts, run `beacon doctor setup-agent-surface --project-root . --agent trae`.\n"
        "- Verify Trae skill availability with `beacon doctor verify-agent-surface --project-root . --agent trae --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )
    return body


def _build_cursor_rules_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    return (
        "---\n"
        f"description: Beacon {runtime_version} agent skill surface and routing\n"
        "alwaysApply: true\n"
        "---\n"
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Cursor Agent Surface\n\n"
        "- Beacon skills are materialized under `.cursor/skills/`.\n"
        "- Use `beacon <subcommand>` as the stable local execution surface.\n"
        "- Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "- Refresh with `beacon doctor setup-agent-surface --project-root . --agent cursor`.\n"
        "- Verify with `beacon doctor verify-agent-surface --project-root . --agent cursor --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )


def _build_windsurf_workflow_block(runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    return (
        "---\n"
        f"description: Beacon {runtime_version} agent skill surface and routing\n"
        "---\n"
        f"{_RULE_BLOCK_START}\n"
        f"<!-- BEACON:VERSION:{runtime_version} -->\n"
        f"<!-- BEACON:DOCS_VERSION:{docs_version} -->\n"
        "# Beacon Windsurf Agent Surface\n\n"
        "Use this workflow to discover and route to project-local Beacon skills.\n\n"
        "1. Prefer project-local Beacon skills under `.windsurf/skills/`.\n"
        "2. Use `beacon <subcommand>` as the stable local execution surface.\n"
        "3. Treat `docs/beacon/global-boundaries.md` and `docs/beacon/<version>/` as canonical truth.\n"
        "4. Refresh with `beacon doctor setup-agent-surface --project-root . --agent windsurf`.\n"
        "5. Verify with `beacon doctor verify-agent-surface --project-root . --agent windsurf --strict`.\n"
        "\n## Installed Beacon Skills\n\n"
        f"{_skill_lines(skill_ids)}\n"
        f"{_RULE_BLOCK_END}\n"
    )


def _build_rules_block(target: AgentSurfaceTarget, runtime_version: str, docs_version: str, skill_ids: list[str]) -> str:
    if target.rules_kind == "cursor-mdc":
        return _build_cursor_rules_block(runtime_version, docs_version, skill_ids)
    if target.rules_kind == "windsurf-workflow":
        return _build_windsurf_workflow_block(runtime_version, docs_version, skill_ids)
    return _build_trae_rules_block(runtime_version, docs_version, skill_ids)


def _sync_rules_file(target: AgentSurfaceTarget, runtime_version: str, docs_version: str, skill_ids: list[str], *, dry_run: bool) -> dict[str, Any] | None:
    if target.rules_path is None:
        return None
    existed = target.rules_path.exists()
    current = target.rules_path.read_text(encoding="utf-8") if target.rules_path.exists() else ""
    managed = _build_rules_block(target, runtime_version, docs_version, skill_ids)
    merged, merge_mode = _merge_managed_block(current, managed)
    changed = current != merged
    if not dry_run:
        target.rules_path.parent.mkdir(parents=True, exist_ok=True)
        target.rules_path.write_text(merged, encoding="utf-8")
    return {
        "path": str(target.rules_path),
        "action": "planned" if dry_run else "updated" if existed else "created",
        "merge_mode": merge_mode,
        "changed": changed or not existed,
    }


def setup_agent_surface(
    project_root: Path | str,
    *,
    agent: str,
    runtime_version: str,
    docs_version: str,
    dry_run: bool,
    force: bool = False,
) -> dict[str, Any]:
    """Materialize Beacon host-visible skills into a project-local agent surface."""
    root = Path(project_root).resolve()
    target = resolve_agent_surface_target(root, agent)
    source_root = packaged_beacon_skill_root()
    source_skills = _expected_skill_projections(source_root, runtime_version=runtime_version, docs_version=docs_version)
    state = _load_state(root)
    agents_state = state.setdefault("agents", {})
    agent_state = agents_state.get(target.agent) if isinstance(agents_state.get(target.agent), dict) else {}
    previously_managed = _managed_skill_ids(agent_state)
    v160_taxonomy = _uses_v160_taxonomy(docs_version, runtime_version)

    installed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    removed: list[str] = []
    warnings: list[str] = []

    if not dry_run:
        target.skills_root.mkdir(parents=True, exist_ok=True)

    removed.extend(_remove_beacon_skill_backup_dirs(target.skills_root, dry_run=dry_run))

    source_names = {item.id for item in source_skills}
    stale_ids = sorted(previously_managed - source_names)
    if v160_taxonomy and target.skills_root.exists():
        stale_ids = sorted(set(stale_ids) | {
            item.name
            for item in target.skills_root.iterdir()
            if item.is_dir() and item.name in _V160_OLD_ALIAS_IDS
        })
    for skill_id in stale_ids:
        stale_path = target.skills_root / skill_id
        if not stale_path.exists():
            continue
        removed.append(str(stale_path))
        if not dry_run:
            shutil.rmtree(stale_path)

    installed_state: list[dict[str, Any]] = []
    for source_skill in source_skills:
        skill_id = source_skill.id
        destination = target.skills_root / skill_id
        source_hash = source_skill.source_hash
        destination_exists = destination.exists()
        destination_hash = _hash_directory(destination) if destination_exists else ""
        managed_existing = skill_id in previously_managed

        if destination_exists and not managed_existing and not force and destination_hash and destination_hash != source_hash:
            skipped.append(
                {
                    "id": skill_id,
                    "path": str(destination),
                    "reason": "unmanaged_existing_directory",
                }
            )
            warnings.append(f"{skill_id} skipped because destination already exists and is unmanaged")
            continue

        action = "unchanged"
        if not destination_exists:
            action = "planned" if dry_run else "created"
        elif destination_hash != source_hash:
            action = "planned" if dry_run else "updated"

        if action != "unchanged":
            if not dry_run:
                if destination.exists():
                    shutil.rmtree(destination)
                _copy_projected_skill(destination, source_skill)
        installed.append(
            {
                "id": skill_id,
                "path": str(destination),
                "action": action,
                "source_hash": source_hash,
                "source_kind": source_skill.source_kind,
            }
        )
        installed_state.append(
            {
                "id": skill_id,
                "path": str(destination.relative_to(root)),
                "source_path": source_skill.source_path,
                "source_kind": source_skill.source_kind,
                "source_hash": source_hash,
            }
        )

    skill_ids = [item.id for item in source_skills]
    rules_result = _sync_rules_file(target, runtime_version, docs_version, skill_ids, dry_run=dry_run)
    state_payload = {
        **state,
        "updated_at": now_iso(),
        "runtime_version": runtime_version,
        "docs_version": docs_version,
        "agents": {
            **agents_state,
            target.agent: {
                "agent": target.agent,
                "surface_root": str(target.skills_root.relative_to(root)),
                "rules_path": str(target.rules_path.relative_to(root)) if target.rules_path else "",
                "source_root": str(source_root.relative_to(root)) if source_root.is_relative_to(root) else str(source_root),
                "source_kind": (
                    source_skills[0].source_kind if v160_taxonomy and source_skills else "packaged_skill_directory"
                ),
                "taxonomy_version": _V160_TAXONOMY_VERSION if v160_taxonomy else "",
                "installed_skills": installed_state,
            },
        },
    }
    state_result = _write_state(root, state_payload, dry_run=dry_run)

    return {
        "project_root": str(root),
        "agent": target.agent,
        "surface_root": str(target.skills_root),
        "rules_path": str(target.rules_path) if target.rules_path else "",
        "installed": installed,
        "skipped": skipped,
        "removed": removed,
        "warnings": warnings,
        "state": state_result,
        "rules": rules_result,
    }


def verify_agent_surface(
    project_root: Path | str,
    *,
    agent: str,
    runtime_version: str,
    docs_version: str | None = None,
    strict: bool,
) -> dict[str, Any]:
    """Verify project-local agent surface materialization against packaged Beacon skills."""
    root = Path(project_root).resolve()
    target = resolve_agent_surface_target(root, agent)
    source_root = packaged_beacon_skill_root()
    source_skills = _expected_skill_projections(source_root, runtime_version=runtime_version, docs_version=docs_version)
    expected_ids = [item.id for item in source_skills]
    v160_taxonomy = _uses_v160_taxonomy(docs_version, runtime_version)
    missing: list[str] = []
    drifted: list[str] = []

    for source_skill in source_skills:
        destination = target.skills_root / source_skill.id
        if not destination.exists():
            missing.append(source_skill.id)
            continue
        if source_skill.source_hash != _hash_directory(destination):
            drifted.append(source_skill.id)

    checks: list[dict[str, Any]] = [
        {
            "name": "agent_supported",
            "status": "pass",
            "details": {"agent": target.agent},
        },
        {
            "name": "surface_root_present",
            "status": "pass" if target.skills_root.exists() else "fail",
            "details": {"path": str(target.skills_root), "exists": target.skills_root.exists()},
        },
        {
            "name": "host_visible_skills_present",
            "status": "pass" if not missing else "fail",
            "details": {"expected": expected_ids, "missing": missing},
        },
        {
            "name": "host_visible_skills_drift",
            "status": "pass" if not drifted else ("fail" if strict else "warn"),
            "details": {"drifted": drifted},
        },
    ]

    if v160_taxonomy:
        v160_surface = _verify_v160_surface(target, expected_ids)
        checks.extend(
            [
                {
                    "name": "v160_harness_skill_names",
                    "status": "pass" if not v160_surface["wrong_names"] else "fail",
                    "details": {"wrong_names": v160_surface["wrong_names"]},
                },
                {
                    "name": "v160_no_skill_backup_directories",
                    "status": "pass" if not v160_surface["backup_dirs"] else "fail",
                    "details": {"backup_dirs": v160_surface["backup_dirs"]},
                },
                {
                    "name": "v160_no_old_host_visible_aliases",
                    "status": "pass" if not v160_surface["old_aliases"] and not v160_surface["unexpected"] else "fail",
                    "details": {"old_aliases": v160_surface["old_aliases"], "unexpected": v160_surface["unexpected"]},
                },
                {
                    "name": "v160_shared_preamble_and_hard_gates",
                    "status": "pass" if not v160_surface["gate_errors"] else "fail",
                    "details": {"gate_errors": v160_surface["gate_errors"]},
                },
                {
                    "name": "v160_canonical_route_references",
                    "status": "pass" if not v160_surface["route_errors"] else "fail",
                    "details": {"route_errors": v160_surface["route_errors"]},
                },
            ]
        )

    if target.rules_path is not None:
        rules_exists = target.rules_path.exists()
        rules_text = target.rules_path.read_text(encoding="utf-8") if rules_exists else ""
        checks.append(
            {
                "name": "agent_rules_managed_block",
                "status": "pass" if rules_exists and _RULE_BLOCK_START in rules_text and _RULE_BLOCK_END in rules_text else "fail",
                "details": {"path": str(target.rules_path), "exists": rules_exists},
            }
        )

    state_path = root / _STATE_PATH
    state_exists = state_path.exists()
    checks.append(
        {
            "name": "agent_surface_state_projection",
            "status": "pass" if state_exists else ("fail" if strict else "warn"),
            "details": {"path": str(state_path), "exists": state_exists},
        }
    )

    if target.agent == "cursor":
        hook_script = root / ".cursor/hooks/beacon-workspace-admission-gate.py"
        hook_registered = False
        hooks_config = root / ".cursor/hooks.json"
        if hooks_config.is_file():
            try:
                hooks_payload = json.loads(hooks_config.read_text(encoding="utf-8"))
                pre_hooks = hooks_payload.get("hooks", {}).get("preToolUse", [])
                if isinstance(pre_hooks, list):
                    for entry in pre_hooks:
                        if not isinstance(entry, dict):
                            continue
                        command = str(entry.get("command") or "")
                        matcher = str(entry.get("matcher") or "")
                        if "beacon-workspace-admission-gate.py" in command and "Write" in matcher:
                            hook_registered = True
                            break
            except json.JSONDecodeError:
                hook_registered = False
        checks.append(
            {
                "name": "workspace_admission_hook",
                "status": "pass" if hook_script.is_file() and hook_registered else "warn",
                "details": {
                    "script": str(hook_script),
                    "script_exists": hook_script.is_file(),
                    "registered_in_hooks_json": hook_registered,
                },
            }
        )

    status = "pass"
    if any(str(item.get("status")) == "fail" for item in checks):
        status = "fail"
    elif any(str(item.get("status")) == "warn" for item in checks):
        status = "warn"

    return {
        "project_root": str(root),
        "agent": target.agent,
        "surface_root": str(target.skills_root),
        "runtime_version": runtime_version,
        "docs_version": docs_version or runtime_version,
        "taxonomy_version": _V160_TAXONOMY_VERSION if v160_taxonomy else "",
        "strict": strict,
        "status": status,
        "ok": status != "fail",
        "checks": checks,
    }
