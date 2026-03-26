"""Implementation adapter helpers for Beacon implement command."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except Exception:  # noqa: BLE001
    yaml = None


def _coerce_scalar(value: str) -> Any:
    text = str(value).strip()
    if text == "":
        return ""
    if text.startswith(("'", '"')) and text.endswith(("'", '"')) and len(text) >= 2:
        return text[1:-1]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    try:
        if "." in text:
            return float(text)
        return int(text)
    except Exception:  # noqa: BLE001
        return text


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a minimal YAML subset used by Beacon config examples.

    Supports:
    - nested mappings via indentation
    - lists with `- value`
    - block scalars (`key: |`)
    - scalar values (quoted/unquoted, bool/int/float/null)
    """

    lines = text.splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any, str | None]] = [(-1, root, None)]
    index = 0

    def _clean_line(raw: str) -> str:
        if "#" in raw:
            quote = None
            out: list[str] = []
            for ch in raw:
                if ch in {"'", '"'}:
                    quote = None if quote == ch else (ch if quote is None else quote)
                if ch == "#" and quote is None:
                    break
                out.append(ch)
            return "".join(out).rstrip()
        return raw.rstrip()

    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        if raw.lstrip().startswith("#"):
            index += 1
            continue
        line = _clean_line(raw)
        if not line.strip():
            index += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        container = stack[-1][1]
        parent_key = stack[-1][2]

        stripped = line.strip()
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if not isinstance(container, list):
                new_list: list[Any] = []
                parent_container = stack[-2][1]
                assert isinstance(parent_container, dict)
                assert parent_key is not None
                parent_container[parent_key] = new_list
                stack[-1] = (stack[-1][0], new_list, parent_key)
                container = new_list
            if item_text == "":
                node: dict[str, Any] = {}
                container.append(node)
                stack.append((indent, node, None))
            else:
                container.append(_coerce_scalar(item_text))
            index += 1
            continue

        if ":" not in stripped:
            index += 1
            continue

        key, remainder = stripped.split(":", 1)
        key = key.strip().replace("-", "_")
        remainder = remainder.strip()
        if not isinstance(container, dict):
            index += 1
            continue

        if remainder == "|":
            block_indent = None
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                raw_block = lines[index]
                current_indent = len(raw_block) - len(raw_block.lstrip(" "))
                if raw_block.strip() == "":
                    block_lines.append("")
                    index += 1
                    continue
                if current_indent <= indent:
                    break
                if block_indent is None:
                    block_indent = current_indent
                block_lines.append(raw_block[block_indent:])
                index += 1
            container[key] = "\n".join(block_lines).rstrip("\n")
            continue

        if remainder == "":
            # Decide whether next structure is dict or list based on lookahead.
            next_non_empty = index + 1
            next_value: Any = {}
            while next_non_empty < len(lines):
                candidate = lines[next_non_empty]
                if not candidate.strip() or candidate.lstrip().startswith("#"):
                    next_non_empty += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                candidate_strip = candidate.strip()
                if candidate_indent > indent and candidate_strip.startswith("- "):
                    next_value = []
                break
            container[key] = next_value
            stack.append((indent, next_value, key))
            index += 1
            continue

        container[key] = _coerce_scalar(remainder)
        index += 1

    return root


def load_beacon_config_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return {}
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        pass
    if yaml is not None:
        try:
            loaded = yaml.safe_load(text)
            return loaded if isinstance(loaded, dict) else {}
        except Exception:  # noqa: BLE001
            pass
    try:
        return _parse_simple_yaml(text)
    except Exception:  # noqa: BLE001
        return {}


def project_config_path(project_root: Path) -> Path:
    return project_root / "beacon.config.yaml"


def global_config_path() -> Path:
    return Path.home() / ".config" / "beacon" / "config.yaml"


def load_beacon_config(project_root: Path) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for path in (global_config_path(), project_config_path(project_root)):
        payload = load_beacon_config_file(path)
        if not isinstance(payload, dict):
            continue
        merged = _deep_merge(merged, payload)
    return merged


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _builtin_adapters() -> dict[str, dict[str, Any]]:
    return {
        "omx": {
            "adapter_type": "command-skill",
            "runtime_family": "omx",
            "command": "omx",
            "args": ["exec", "--full-auto", "--cd", "{project_root}", "--skip-git-repo-check", "{task_prompt}"],
            "skill_prefix": "$workflows-work",
            "supports_dry_run": True,
            "result_file": ".beacon/implement/{run_id}/result.json",
            "stdout_file": ".beacon/implement/{run_id}/stdout.log",
            "stderr_file": ".beacon/implement/{run_id}/stderr.log",
            "command_file": ".beacon/implement/{run_id}/command.txt",
        },
        "omc": {
            "adapter_type": "command-skill",
            "runtime_family": "omc",
            "command": "omc",
            "args": ["ask", "claude", "--prompt", "{task_prompt}"],
            "skill_prefix": "autopilot:",
            "supports_dry_run": True,
            "result_file": ".beacon/implement/{run_id}/result.json",
            "stdout_file": ".beacon/implement/{run_id}/stdout.log",
            "stderr_file": ".beacon/implement/{run_id}/stderr.log",
            "command_file": ".beacon/implement/{run_id}/command.txt",
        },
        "gstack": {
            "adapter_type": "handoff",
            "runtime_family": "claude-code",
            "request_file": ".beacon/implement/{run_id}/request.md",
            "result_file": ".beacon/implement/{run_id}/result.json",
            "recommended_flows": ["/review", "/qa", "/ship"],
            "supports_dry_run": True,
        },
        "native-single": {
            "adapter_type": "native",
            "runtime_family": "beacon-native",
            "mode": "single",
            "supports_dry_run": True,
            "result_file": ".beacon/implement/{run_id}/result.json",
        },
        "native-team": {
            "adapter_type": "native",
            "runtime_family": "beacon-native",
            "mode": "team",
            "supports_dry_run": True,
            "result_file": ".beacon/implement/{run_id}/result.json",
        },
    }


def discover_skill_adapters(project_root: Path) -> dict[str, dict[str, Any]]:
    config = load_beacon_config(project_root)
    skill_section = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    implementation_section = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    adapters = _builtin_adapters()
    for source in (
        skill_section.get("adapters") if isinstance(skill_section, dict) else {},
        implementation_section.get("runners") if isinstance(implementation_section, dict) else {},
    ):
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if isinstance(value, dict):
                adapters[str(key)] = _deep_merge(adapters.get(str(key), {}), value)
    return adapters


def adapter_defined_in_config(project_root: Path, adapter_id: str) -> bool:
    config = load_beacon_config(project_root)
    skill_section = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    implementation_section = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    adapters = skill_section.get("adapters") if isinstance(skill_section.get("adapters"), dict) else {}
    runners = implementation_section.get("runners") if isinstance(implementation_section.get("runners"), dict) else {}
    return adapter_id in adapters or adapter_id in runners


def resolve_default_runner(project_root: Path) -> str | None:
    config = load_beacon_config(project_root)
    skill_section = config.get("skill") if isinstance(config.get("skill"), dict) else {}
    implementation_section = config.get("implementation") if isinstance(config.get("implementation"), dict) else {}
    preferred = str(skill_section.get("preferred", "")).strip()
    if preferred:
        return preferred
    default_runner = str(implementation_section.get("default_runner", "")).strip()
    return default_runner or None


def detect_adapter(adapter_id: str, project_root: Path) -> tuple[bool, list[str]]:
    adapter = discover_skill_adapters(project_root).get(adapter_id, {})
    evidence: list[str] = []
    runtime_family = str(adapter.get("runtime_family", adapter_id)).strip()
    if adapter_id in {"native-single", "native-team"}:
        return (True, ["builtin-native"])
    if adapter_id == "gstack":
        candidate_paths = [
            project_root / ".claude" / "skills" / "gstack",
            Path.home() / ".claude" / "skills" / "gstack",
            project_root.parent / "agent-skills" / "gstack",
            project_root.parent / "gstack",
        ]
        for path in candidate_paths:
            if path.exists():
                evidence.append(str(path))
        return (len(evidence) > 0, evidence)
    command = str(adapter.get("command", adapter_id if runtime_family in {"omx", "omc"} else "")).strip()
    if command:
        command_path = _which(command)
        if command_path:
            evidence.append(command_path)
    marker_dir = project_root / f".{runtime_family}"
    if marker_dir.exists():
        evidence.append(str(marker_dir))
    return (len(evidence) > 0, evidence)


def _which(name: str) -> str | None:
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        path = Path(entry) / name
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    return None


def format_template(value: str, context: dict[str, Any]) -> str:
    rendered = str(value or "")
    for key, raw in context.items():
        rendered = rendered.replace("{" + key + "}", str(raw))
    return rendered


def build_default_task_prompt(*, feature: str, version: str, source_of_truth_root: str, feature_slug: str, result_file: str) -> str:
    return (
        "Implement the scoped Beacon feature.\n"
        f"Feature: {feature}\n"
        f"Version: {version}\n"
        "Read Beacon source of truth:\n"
        f"- {source_of_truth_root}/user-story/{feature_slug}.md\n"
        f"- {source_of_truth_root}/prd/{feature_slug}.md\n"
        f"- {source_of_truth_root}/qa/test-cases/{feature_slug}.md\n"
        "Run relevant verification.\n"
        f"Write structured result to {result_file}\n"
    )


def resolve_adapter(project_root: Path, adapter_id: str | None) -> tuple[str | None, dict[str, Any]]:
    adapters = discover_skill_adapters(project_root)
    target = str(adapter_id or "").strip() or resolve_default_runner(project_root) or ""
    if not target:
        return None, {}
    payload = adapters.get(target)
    if not isinstance(payload, dict):
        return None, {}
    return target, payload
