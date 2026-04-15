"""Helpers for Beacon Toolkit Lighthouse single-file analysis artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import human_execution_file
from beacon.utils.versioning import resolve_target_version

LIGHTHOUSE_TOOL = "beacon-toolkit-lighthouse"
SUPPORTED_LIGHTHOUSE_MODES = (
    "system-architecture-map",
    "package-brief",
    "infra-chain-map",
    "feature-slice",
)
_IGNORE_DIRS = {
    ".git",
    ".beacon",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}
_ENTRYPOINT_FILES = (
    "README.md",
    "pyproject.toml",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "Dockerfile",
    "docker-compose.yml",
    "main.py",
    "app.py",
    "manage.py",
    "__init__.py",
    "index.js",
    "index.ts",
    "index.tsx",
)
_DEPENDENCY_FILES = (
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "go.mod",
    "Cargo.toml",
    "Gemfile",
    "Dockerfile",
    "docker-compose.yml",
    ".github/workflows",
)
_INFRA_LAYERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("gateway", ("gateway", "ingress", "nginx", "proxy", "api-gateway")),
    ("api-bff", ("bff", "api", "graphql", "rest", "openapi")),
    ("service", ("service", "services", "app", "core", "backend")),
    ("queue", ("queue", "queues", "mq", "kafka", "rabbit", "celery", "worker", "jobs")),
    ("storage", ("storage", "db", "database", "postgres", "mysql", "redis", "s3", "bucket")),
)
_FEATURE_HINT_FILES = (
    "__init__.py",
    "main.py",
    "service.py",
    "controller.py",
    "routes.py",
    "router.py",
    "api.py",
    "schema.py",
    "models.py",
    "tests.py",
)


def lighthouse_analysis_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "analysis"


def slugify(value: str) -> str:
    pieces = [
        "".join(char for char in token.lower() if char.isalnum() or char in {"-", "_"}).strip("-_")
        for token in str(value or "").replace("/", " ").replace("\\", " ").split()
    ]
    normalized = [piece.replace("_", "-") for piece in pieces if piece]
    return "-".join(normalized) or "lighthouse-map"


def default_lighthouse_output_path(project_root: Path, slug: str) -> Path:
    return lighthouse_analysis_dir(project_root) / f"{slug}.md"


def default_lighthouse_versioned_output_path(project_root: Path, version: str, slug: str) -> Path:
    return human_execution_file(project_root, version, f"beacon-toolkit-lighthouse-{slug}.md")


def is_beacon_source_repo(project_root: Path) -> bool:
    return (
        (project_root / "beacon" / "__init__.py").exists()
        and (project_root / "skills" / "beacon" / "SKILL.md").exists()
        and (project_root / "docs" / "beacon").exists()
    )


def resolve_lighthouse_target(project_root: Path, target: str | None, mode: str) -> tuple[Path, str]:
    raw = str(target or "").strip()
    if not raw:
        if mode in {"package-brief", "feature-slice"}:
            raise ValueError(f"{mode} mode requires a target path inside the project")
        return project_root, project_root.name or "project-root"
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (project_root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if not candidate.exists():
        raise ValueError(f"analysis target does not exist: {raw}")
    return candidate, str(candidate.relative_to(project_root)) if candidate != project_root and candidate.is_relative_to(project_root) else candidate.name


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _visible_children(root: Path, *, limit: int = 10) -> list[Path]:
    if not root.is_dir():
        return []
    children = [
        child
        for child in sorted(root.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        if child.name not in _IGNORE_DIRS and (not child.name.startswith(".") or child.name == ".github")
    ]
    return children[:limit]


def _count_files(path: Path) -> int:
    if path.is_file():
        return 1
    count = 0
    for entry in path.rglob("*"):
        if any(part in _IGNORE_DIRS for part in entry.parts):
            continue
        if entry.is_file():
            count += 1
    return count


def _detect_entry_points(scope_root: Path, project_root: Path) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for name in _ENTRYPOINT_FILES:
        path = scope_root / name
        if path.exists():
            candidates.append({"path": _relative(path, project_root), "reason": "top-level entry or manifest"})
    if scope_root.is_dir():
        for nested in ("src/main.py", "lib/main.rb", "cmd/main.go"):
            path = scope_root / nested
            if path.exists():
                candidates.append({"path": _relative(path, project_root), "reason": "nested executable entrypoint"})
    if scope_root == project_root:
        extra = (
            ("beacon/main.py", "CLI module entrypoint"),
            ("beacon/cli_factory.py", "command registration"),
            ("beacon/commands", "primary command surface"),
            ("tests", "verification surface"),
        )
        for raw_path, reason in extra:
            path = project_root / raw_path
            if path.exists():
                candidates.append({"path": _relative(path, project_root), "reason": reason})
    return candidates[:8]


def _detect_dependency_refs(scope_root: Path, project_root: Path) -> list[str]:
    refs: list[str] = []
    for name in _DEPENDENCY_FILES:
        path = scope_root / name
        if path.exists():
            refs.append(_relative(path, project_root))
    return refs[:8]


def _detect_infra_refs(scope_root: Path, project_root: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    for child in _visible_children(scope_root, limit=20):
        lowered = child.name.lower()
        for layer, hints in _INFRA_LAYERS:
            if any(hint in lowered for hint in hints):
                refs.append({"path": _relative(child, project_root), "layer": layer})
                break
    if scope_root == project_root:
        for raw in ("docker-compose.yml", "Dockerfile", ".github/workflows", "docs", "k8s", "helm"):
            path = project_root / raw
            if path.exists():
                refs.append({"path": _relative(path, project_root), "layer": "infra-config"})
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in refs:
        marker = f"{item['layer']}::{item['path']}"
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
    return deduped[:10]


def _layer_node_id(name: str) -> str:
    return slugify(name.replace("/", "-")) or "layer"


def _render_mermaid_infra_chain(scope_root: Path, project_root: Path) -> str:
    refs = _detect_infra_refs(scope_root, project_root)
    by_layer: dict[str, list[str]] = {layer: [] for layer, _ in _INFRA_LAYERS}
    extras: list[str] = []
    for item in refs:
        path = item["path"]
        layer = item["layer"]
        if layer in by_layer:
            by_layer[layer].append(path)
        else:
            extras.append(path)
    lines = ["```mermaid", "graph LR"]
    ordered_layers = [layer for layer, _ in _INFRA_LAYERS]
    previous_node = ""
    for layer in ordered_layers:
        label = layer
        sample = ", ".join(by_layer[layer][:2]) or "未显式识别"
        node = _layer_node_id(layer)
        lines.append(f'  {node}["{label}\\n{sample}"]')
        if previous_node:
            lines.append(f"  {previous_node} --> {node}")
        previous_node = node
    if extras:
        lines.append(f'  infraextra["infra-config\\n{", ".join(extras[:2])}"]')
        if previous_node:
            lines.append(f"  {previous_node} --> infraextra")
    lines.append("```")
    return "\n".join(lines)


def _render_mermaid_feature_slice(scope_root: Path, project_root: Path) -> str:
    label = _relative(scope_root, project_root)
    lines = ["```mermaid", "graph TD", f'  feature["{label}"]']
    if scope_root.is_file():
        lines.append("```")
        return "\n".join(lines)
    for child in _visible_children(scope_root, limit=6):
        node = slugify(child.name) or f"node-{len(lines)}"
        child_label = f"{child.name}/" if child.is_dir() else child.name
        lines.append(f'  feature --> {node}["{child_label}"]')
    lines.append("```")
    return "\n".join(lines)


def _detect_feature_entry_points(scope_root: Path, project_root: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if scope_root.is_file():
        entries.append({"path": _relative(scope_root, project_root), "reason": "explicit feature target"})
        sibling_dir = scope_root.parent
    else:
        sibling_dir = scope_root
    for name in _FEATURE_HINT_FILES:
        path = sibling_dir / name
        if path.exists():
            entries.append({"path": _relative(path, project_root), "reason": "feature-slice hint file"})
    if scope_root.is_dir():
        for child in _visible_children(scope_root, limit=8):
            if child.is_file() and any(token in child.name.lower() for token in ("route", "controller", "service", "handler", "view", "test")):
                entries.append({"path": _relative(child, project_root), "reason": "direct feature file"})
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in entries:
        if item["path"] in seen:
            continue
        seen.add(item["path"])
        deduped.append(item)
    return deduped[:8]


def _render_mermaid_system_map(scope_root: Path, project_root: Path) -> str:
    root_label = _relative(scope_root, project_root) if scope_root != project_root else project_root.name
    lines = ["```mermaid", "graph TD", f'  root["{root_label}"]']
    for child in _visible_children(scope_root, limit=8):
        label = f"{child.name}/" if child.is_dir() else child.name
        node = slugify(child.name) or f"node-{len(lines)}"
        lines.append(f'  root --> {node}["{label}"]')
    lines.append("```")
    return "\n".join(lines)


def _render_mermaid_package_brief(scope_root: Path, project_root: Path) -> str:
    label = _relative(scope_root, project_root)
    lines = ["```mermaid", "graph TD", f'  pkg["{label}"]']
    if scope_root.is_file():
        lines.append("```")
        return "\n".join(lines)
    for child in _visible_children(scope_root, limit=6):
        node = slugify(child.name) or f"node-{len(lines)}"
        child_label = f"{child.name}/" if child.is_dir() else child.name
        lines.append(f'  pkg --> {node}["{child_label}"]')
    lines.append("```")
    return "\n".join(lines)


def _summarize_top_level(scope_root: Path, project_root: Path) -> list[str]:
    items = []
    for child in _visible_children(scope_root, limit=6):
        if child.is_dir():
            items.append(
                f"`{_relative(child, project_root)}` contains about `{_count_files(child)}` files and looks like a standalone subsystem."
            )
        else:
            items.append(f"`{_relative(child, project_root)}` is a top-level file that likely anchors runtime or documentation behavior.")
    return items


def _summarize_package_children(scope_root: Path, project_root: Path) -> list[str]:
    if scope_root.is_file():
        return [f"`{_relative(scope_root, project_root)}` is a single-file target, so the package brief focuses on direct responsibilities instead of submodules."]
    items = []
    for child in _visible_children(scope_root, limit=6):
        rel = _relative(child, project_root)
        if child.is_dir():
            items.append(f"`{rel}` looks like a nested module boundary with `{_count_files(child)}` files.")
        else:
            items.append(f"`{rel}` is a direct implementation file under this package slice.")
    return items


def _summarize_infra_chain(scope_root: Path, project_root: Path) -> list[str]:
    refs = _detect_infra_refs(scope_root, project_root)
    if not refs:
        return ["当前范围下没有识别到明确的 gateway / service / queue / storage 命名节点，可能需要显式指定更贴近部署面的目录。"]
    return [f"`{item['path']}` currently looks like the `{item['layer']}` layer candidate." for item in refs[:6]]


def _summarize_feature_slice(scope_root: Path, project_root: Path) -> list[str]:
    if scope_root.is_file():
        return [f"`{_relative(scope_root, project_root)}` is the explicit feature file; continue by reading callers and adjacent tests."]
    return _summarize_package_children(scope_root, project_root)


def _confirmed_facts(mode: str, scope_root: Path, project_root: Path, entry_points: list[dict[str, str]], dependency_refs: list[str]) -> list[str]:
    facts = [
        f"分析模式为 `{mode}`。",
        f"分析目标是 `{_relative(scope_root, project_root) if scope_root != project_root else '.'}`。",
        f"目标类型是 `{'directory' if scope_root.is_dir() else 'file'}`。",
    ]
    if entry_points:
        facts.append(f"检测到 `{len(entry_points)}` 个关键入口/清单文件。")
    if dependency_refs:
        facts.append(f"检测到 `{len(dependency_refs)}` 个依赖或基础设施相关引用。")
    if scope_root.is_dir():
        facts.append(f"目标范围下约有 `{_count_files(scope_root)}` 个文件。")
    return facts


def _inferred_structure(mode: str, scope_root: Path, project_root: Path) -> list[str]:
    rel = _relative(scope_root, project_root) if scope_root != project_root else "."
    inferred: list[str] = []
    if (scope_root / "tests").exists() or (project_root / "tests").exists():
        inferred.append("仓库很可能把实现与验证留在同一代码库内演进。")
    if (project_root / "docs").exists():
        inferred.append("文档目录存在，说明这条线倾向于把认知材料和代码一起版本化。")
    if mode == "system-architecture-map" and (project_root / "skills").exists():
        inferred.append("看起来存在面向宿主或 AI 入口的 skill / prompt 适配层。")
    if mode == "package-brief":
        if scope_root.is_dir() and any(child.name == "__init__.py" for child in scope_root.iterdir()):
            inferred.append(f"`{rel}` 更像一个显式 package 边界，而不是松散脚本集合。")
        else:
            inferred.append(f"`{rel}` 当前更像实现切片，需要继续结合入口文件确认对外 API。")
    if mode == "infra-chain-map":
        inferred.append("当前 infra 链路是按目录/文件命名启发式推断的，真正的数据流和控制流还需要结合部署配置验证。")
    if mode == "feature-slice":
        inferred.append(f"`{rel}` 当前被当作一个 feature 边界切片，但上下游入口还需要从调用点和测试覆盖继续收口。")
    return inferred or ["当前推断较轻，仍需要继续阅读关键入口文件来确认职责边界。"]


def _open_questions(mode: str, scope_root: Path, project_root: Path) -> list[str]:
    rel = _relative(scope_root, project_root) if scope_root != project_root else "."
    if mode == "package-brief":
        return [
            f"`{rel}` 的正式对外入口是否只通过一个聚合文件暴露，还需要读 README 或上层调用点确认。",
            f"`{rel}` 与相邻模块的写入/调用边界是否稳定，还需要查看集成测试或调用链。",
        ]
    if mode == "infra-chain-map":
        return [
            "当前链路图是否真的覆盖了所有 gateway / worker / storage 层，还需要核对部署配置和运行时环境变量。",
            "队列与存储节点目前主要来自命名推断，是否存在托管服务或外部 SaaS 还没有证据。",
        ]
    if mode == "feature-slice":
        return [
            f"`{rel}` 的真正 feature 入口是否来自路由、任务调度或事件消费，还需要继续向上游追调用点。",
            f"`{rel}` 的测试覆盖是否完整，还需要检查相关测试文件和集成场景。",
        ]
    return [
        "当前地图基于目录和关键文件启发式生成，跨进程/跨服务调用关系还需要继续读实现细节确认。",
        "如果项目依赖运行时动态注册或插件发现机制，单次静态扫描可能看不到全部边界。",
    ]


def _recommended_next_steps(mode: str, scope_root: Path, project_root: Path) -> list[str]:
    rel = _relative(scope_root, project_root) if scope_root != project_root else "."
    steps = [f"先读 `Key Entry Points` 里的文件，确认 `{rel}` 的正式入口和初始化顺序。"]
    if mode == "system-architecture-map":
        steps.append("如果需要正式需求或实现闭环，再显式把这份 Lighthouse 工件作为 PRD / implement / QA 的输入。")
    elif mode == "infra-chain-map":
        steps.append("下一步最好补充部署配置、环境变量或运行拓扑，验证 gateway → service → queue → storage 的真实顺序。")
    elif mode == "feature-slice":
        steps.append("下一步从这个切片的上游调用点和测试文件继续挖，补齐完整 feature path。")
    else:
        steps.append("如果要继续深挖调用链，下一步补一份 feature-slice 或 infra-chain-map 会更有效。")
    return steps


def _render_markdown(
    *,
    title: str,
    mode: str,
    project_root: Path,
    scope_root: Path,
    summary: str,
    mermaid_block: str,
    entry_points: list[dict[str, str]],
    module_lines: list[str],
    dependency_refs: list[str],
    confirmed_facts: list[str],
    inferred_structure: list[str],
    open_questions: list[str],
    next_steps: list[str],
) -> str:
    scope_label = _relative(scope_root, project_root) if scope_root != project_root else "."
    lines = [
        f"# {title}",
        "",
        "## 1. Summary",
        f"- {summary}",
        "",
        "## 2. Scope",
        f"- mode: `{mode}`",
        f"- project_root: `{project_root}`",
        f"- target: `{scope_label}`",
        "",
        "## 3. Mermaid Maps",
        mermaid_block,
        "",
        "## 4. Key Entry Points",
    ]
    if entry_points:
        for item in entry_points:
            lines.append(f"- `{item['path']}`: {item['reason']}")
    else:
        lines.append("- 暂未识别到明确入口文件，需要人工补充范围或切换模式。")
    lines.extend(["", "## 5. Key Modules / Subsystems"])
    for item in module_lines or ["当前范围较小，没有可拆成多个子系统的明显边界。"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 6. Dependencies / Infra Chain"])
    if dependency_refs:
        for item in dependency_refs:
            lines.append(f"- `{item}`")
    else:
        lines.append("- 当前范围下未发现明显的依赖清单或基础设施配置文件。")
    lines.extend(["", "## 7. Confirmed Facts"])
    for item in confirmed_facts:
        lines.append(f"- {item}")
    lines.extend(["", "## 8. Inferred Structure"])
    for item in inferred_structure:
        lines.append(f"- {item}")
    lines.extend(["", "## 9. Open Questions / Risks"])
    for item in open_questions:
        lines.append(f"- {item}")
    lines.extend(["", "## 10. Recommended Next Steps"])
    for item in next_steps:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def generate_lighthouse_artifact(
    project_root: Path,
    *,
    target: str | None,
    mode: str,
    version: str,
    output_path: str | None = None,
    write_versioned_output: bool | None = None,
) -> dict[str, Any]:
    normalized_mode = str(mode or "").strip().lower()
    if normalized_mode not in SUPPORTED_LIGHTHOUSE_MODES:
        raise ValueError(f"unsupported lighthouse mode: {mode}")
    resolved_version = resolve_target_version(project_root, version)
    scope_root, target_label = resolve_lighthouse_target(project_root, target, normalized_mode)
    scope_label = _relative(scope_root, project_root) if scope_root != project_root else project_root.name
    if normalized_mode == "system-architecture-map":
        slug = "system-architecture-map"
        top_children = ", ".join(child.name for child in _visible_children(scope_root, limit=3)) or "当前范围"
        summary = f"`{project_root.name}` 的主结构以 `{top_children}` 为主，适合先从入口文件和顶层子系统开始建立心智模型。"
        mermaid_block = _render_mermaid_system_map(scope_root, project_root)
        module_lines = _summarize_top_level(scope_root, project_root)
        title = f"{project_root.name} Lighthouse Map"
        entry_points = _detect_entry_points(scope_root, project_root)
        dependency_refs = _detect_dependency_refs(scope_root, project_root)
    elif normalized_mode == "package-brief":
        slug = slugify(f"package-brief-{target_label}")
        summary = f"`{scope_label}` 是当前 package-brief 的分析目标，先抓直接文件、子模块和依赖清单，再决定是否继续做 feature-slice。"
        mermaid_block = _render_mermaid_package_brief(scope_root, project_root)
        module_lines = _summarize_package_children(scope_root, project_root)
        title = f"{target_label} Package Brief"
        entry_points = _detect_entry_points(scope_root, project_root)
        dependency_refs = _detect_dependency_refs(scope_root, project_root)
    elif normalized_mode == "infra-chain-map":
        slug = "infra-chain-map" if scope_root == project_root else slugify(f"infra-chain-map-{target_label}")
        summary = f"`{scope_label}` 的 infra-chain-map 会优先按 `gateway → api/bff → service → queue → storage` 这条骨架输出，用来快速核对部署和数据路径。"
        mermaid_block = _render_mermaid_infra_chain(scope_root, project_root)
        module_lines = _summarize_infra_chain(scope_root, project_root)
        title = f"{target_label} Infra Chain Map"
        entry_points = _detect_entry_points(scope_root, project_root)
        dependency_refs = [item["path"] for item in _detect_infra_refs(scope_root, project_root)]
    else:
        slug = slugify(f"feature-slice-{target_label}")
        summary = f"`{scope_label}` 的 feature-slice 会先抓入口文件、直接模块和相邻测试，帮助快速界定这个功能切片。"
        mermaid_block = _render_mermaid_feature_slice(scope_root, project_root)
        module_lines = _summarize_feature_slice(scope_root, project_root)
        title = f"{target_label} Feature Slice"
        entry_points = _detect_feature_entry_points(scope_root, project_root)
        dependency_refs = _detect_dependency_refs(scope_root, project_root)
    markdown = _render_markdown(
        title=title,
        mode=normalized_mode,
        project_root=project_root,
        scope_root=scope_root,
        summary=summary,
        mermaid_block=mermaid_block,
        entry_points=entry_points,
        module_lines=module_lines,
        dependency_refs=dependency_refs,
        confirmed_facts=_confirmed_facts(normalized_mode, scope_root, project_root, entry_points, dependency_refs),
        inferred_structure=_inferred_structure(normalized_mode, scope_root, project_root),
        open_questions=_open_questions(normalized_mode, scope_root, project_root),
        next_steps=_recommended_next_steps(normalized_mode, scope_root, project_root),
    )

    output = Path(output_path).expanduser().resolve() if output_path else default_lighthouse_output_path(project_root, slug)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")

    should_write_versioned = is_beacon_source_repo(project_root) if write_versioned_output is None else bool(write_versioned_output)
    versioned_output = ""
    if should_write_versioned:
        versioned_path = default_lighthouse_versioned_output_path(project_root, resolved_version, slug)
        versioned_path.parent.mkdir(parents=True, exist_ok=True)
        versioned_path.write_text(markdown, encoding="utf-8")
        versioned_output = str(versioned_path)

    payload = {
        "schema_version": "1.0",
        "tool": LIGHTHOUSE_TOOL,
        "status": "ok",
        "mode": normalized_mode,
        "docs_version": resolved_version,
        "project_root": str(project_root),
        "target_path": str(scope_root),
        "target_label": target_label,
        "slug": slug,
        "output_path": str(output),
        "versioned_output_path": versioned_output,
        "beacon_source_repo": is_beacon_source_repo(project_root),
        "entry_points": entry_points,
        "dependency_refs": dependency_refs,
    }
    return payload


def render_lighthouse_human(payload: dict[str, Any], *, project_root: Path) -> str:
    output_path = str(payload.get("output_path", "") or "")
    versioned_output_path = str(payload.get("versioned_output_path", "") or "")
    lines = [
        "Beacon Toolkit Lighthouse",
        "=" * 26,
        f"mode              : {payload.get('mode', '')}",
        f"target            : {payload.get('target_label', '')}",
        f"docs version      : {payload.get('docs_version', '')}",
        f"output            : {output_path}",
    ]
    if versioned_output_path:
        lines.append(f"versioned output  : {versioned_output_path}")
    entry_points = payload.get("entry_points", [])
    if isinstance(entry_points, list) and entry_points:
        lines.extend(["", "key entry points"])
        for item in entry_points[:5]:
            if isinstance(item, dict):
                lines.append(f"- {item.get('path', '')}")
    return "\n".join(lines) + "\n"


def payload_to_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
