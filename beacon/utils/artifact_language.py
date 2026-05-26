"""Artifact language policy helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_ARTIFACT_LANGUAGE_POLICY = Path("beacon/artifact-language-policy.json")

_CLASS_LABELS = {
    "human_requirement_docs": "人类主读需求材料",
    "machine_contracts": "机器主读契约与运行工件",
    "human_mirrors_of_machine_contracts": "机器契约的人类中文镜像",
}

_AUDIENCE_LABELS = {
    "human": "人类",
    "machine": "机器",
}

_DEFAULT_RULE_ZH = {
    "Do not rename machine-stable keys for presentation-only localization.": "不得为了展示层本地化而重命名机器稳定主键。"
}

_CLASS_NOTES_ZH = {
    "human_requirement_docs": "面向人类的规划、需求与导航材料默认使用中文。",
    "machine_contracts": "机器契约与运行工件优先保持英文键名与机器友好结构。",
    "human_mirrors_of_machine_contracts": "机器可读契约的人类中文镜像；源机器 artifact 是投影或证据读模型，不是需求真相。",
}

_SYNC_VALUE_ZH = {
    "projection_or_evidence": "投影或证据 artifact",
    "human-readable Chinese markdown": "人类可读中文 Markdown",
    "source JSON artifact": "source JSON artifact",
    "Chinese mirror markdown": "中文镜像 Markdown",
    "shared renderer or deterministic transform": "统一渲染器或确定性转换",
    "render function in source code": "源码中的 render 函数",
    "tests must fail on drift": "若两侧漂移，测试必须失败",
}

_RULES_ZH = {
    "Human-facing planning and requirement materials should default to Chinese.": "面向人类的规划与需求材料应默认使用中文。",
    "Machine-facing contracts and runtime artifacts should default to English or machine-stable keys.": "面向机器的契约与运行工件应默认使用英文或机器稳定主键。",
    "Localization must not change machine field names.": "本地化不得改变机器字段名。",
    "Any new mirrored artifact type must define source JSON, Chinese mirror markdown, render function, and drift test.": "任何新增镜像 artifact 类型都必须同时定义 source JSON、中文镜像 Markdown、render 函数与漂移测试。",
}


def _default_artifact_language_policy() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact": "beacon-artifact-language-policy",
        "description": (
            "Canonical language policy for Beacon artifacts. Human-facing materials default to Chinese; "
            "machine-facing artifacts default to English or machine-stable keys."
        ),
        "default_policy": {
            "human_primary_language": "zh-CN",
            "machine_primary_language": "en",
            "rule": "Do not rename machine-stable keys for presentation-only localization.",
        },
        "artifact_classes": {
            "human_requirement_docs": {
                "scope": ["summary", "prd", "user-story", "qa/test-cases", "execution/index", "execution/contracts"],
                "audience": "human",
                "language": "zh-CN",
                "notes": "Default Chinese for human-readable planning, requirement, and navigation materials.",
            },
            "machine_contracts": {
                "scope": [".machine", "runtime_state", "json_contracts", "evidence_payloads"],
                "audience": "machine",
                "language": "en",
                "notes": "Prefer stable English keys and machine-friendly structures.",
            },
            "human_mirrors_of_machine_contracts": {
                "scope": ["execution/*-contract.md"],
                "audience": "human",
                "language": "zh-CN",
                "notes": "Chinese mirrors of machine-readable contracts; source machine artifacts are projection/evidence read models, not requirement truth.",
            },
        },
        "sync_contract": {
            "source_artifact_role": "projection_or_evidence",
            "mirror": "human-readable Chinese markdown",
            "enforcement": [
                "shared renderer or deterministic transform",
                "tests must fail on drift",
            ],
        },
        "rules": [
            "Human-facing planning and requirement materials should default to Chinese.",
            "Machine-facing contracts and runtime artifacts should default to English or machine-stable keys.",
            "Localization must not change machine field names.",
            "Any new mirrored artifact type must define both source artifact and mirror path plus a drift test.",
        ],
    }


def load_artifact_language_policy(project_root: Path) -> dict[str, Any]:
    path = project_root / _ARTIFACT_LANGUAGE_POLICY
    if not path.exists():
        payload = _default_artifact_language_policy()
        payload["source_path"] = ""
        payload["source_kind"] = "default"
        return payload
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        payload = _default_artifact_language_policy()
        payload["source_path"] = ""
        payload["source_kind"] = "default"
        return payload if isinstance(payload, dict) else _default_artifact_language_policy()
    if not isinstance(payload, dict):
        payload = _default_artifact_language_policy()
    merged = _default_artifact_language_policy()
    for key, value in payload.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    merged["source_path"] = str(_ARTIFACT_LANGUAGE_POLICY)
    merged["source_kind"] = "canonical_file"
    return merged


def render_artifact_language_policy_markdown(policy: dict[str, Any], *, version: str) -> str:
    version_text = str(version or "").strip() or "<version>"
    default_policy = policy.get("default_policy", {}) if isinstance(policy.get("default_policy"), dict) else {}
    lines = [
        "# Beacon 工件语言策略契约",
        "",
        f"- 文档线: `{version_text}`",
        "- 镜像源: `beacon/artifact-language-policy.json`",
        "- 镜像规则: 本文档是机器可读语言策略 artifact 的人类可读中文镜像；两侧必须同步更新。",
        "",
        "## 目的",
        "",
        "为未来所有 Beacon artifact 类型提供统一的“中人 / 英机”生成规范。",
        "",
        "## 默认策略",
        "",
        f"- 人类主语言: `{default_policy.get('human_primary_language', '')}`",
        f"- 机器主语言: `{default_policy.get('machine_primary_language', '')}`",
        f"- 基础规则: {_DEFAULT_RULE_ZH.get(str(default_policy.get('rule', '')).strip(), str(default_policy.get('rule', '')).strip())}",
        "",
        "## 工件类型",
        "",
        "| 类型 | 面向对象 | 默认语言 | 覆盖范围 | 说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    artifact_classes = policy.get("artifact_classes", {}) if isinstance(policy.get("artifact_classes"), dict) else {}
    for class_name, payload in artifact_classes.items():
        if not isinstance(payload, dict):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _CLASS_LABELS.get(class_name, class_name),
                    _AUDIENCE_LABELS.get(str(payload.get("audience", "")).strip(), str(payload.get("audience", "")).strip()),
                    str(payload.get("language", "")).strip(),
                    "`" + json.dumps(payload.get("scope", []), ensure_ascii=False) + "`",
                    _CLASS_NOTES_ZH.get(class_name, str(payload.get("notes", "")).strip()),
                ]
            )
            + " |"
        )

    sync_contract = policy.get("sync_contract", {}) if isinstance(policy.get("sync_contract"), dict) else {}
    lines.extend(
        [
            "",
            "## 镜像同步规则",
            "",
            f"- 源 artifact 角色: `{_SYNC_VALUE_ZH.get(str(sync_contract.get('source_artifact_role', '')).strip(), str(sync_contract.get('source_artifact_role', '')).strip())}`",
            f"- 中文镜像: `{_SYNC_VALUE_ZH.get(str(sync_contract.get('mirror', '')).strip(), str(sync_contract.get('mirror', '')).strip())}`",
            "- enforce:",
        ]
    )
    for item in sync_contract.get("enforcement", []) if isinstance(sync_contract.get("enforcement"), list) else []:
        lines.append(f"  - {_SYNC_VALUE_ZH.get(str(item).strip(), str(item).strip())}")

    lines.extend(["", "## 全局规则", ""])
    rules = policy.get("rules", []) if isinstance(policy.get("rules"), list) else []
    for item in rules:
        lines.append(f"- {_RULES_ZH.get(str(item).strip(), str(item).strip())}")
    return "\n".join(lines) + "\n"
