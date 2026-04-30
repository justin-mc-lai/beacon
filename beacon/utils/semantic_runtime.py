"""Shared host-native semantic runtime and internal semantic layer helpers."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_trace_dir
from beacon.utils.project_skills import load_skill_registry
from beacon.utils.runtime import now_iso
from beacon.utils.subagent_readiness import detect_host_runtime
from beacon.utils.workflow_memory import build_stage_context, normalize_workflow_stage, stage_context_path

_SUPPORTED_HOSTS = {"codex", "claude"}
_SUPPORTED_REQUESTED_MODES = {"auto", "llm", "rule"}
_SEMANTIC_SCHEMA_VERSION = "1.0"
_SEMANTIC_STAGE_ORDER = ("prd", "user-story", "test-case", "prototype", "implement", "qa", "release")
_DEFAULT_TASTE_SKILL_REPO = "https://github.com/Leonxlnx/taste-skill"
_DEFAULT_TASTE_SKILL_ID = "taste-skill"
_PAGE_TERM_PATTERN = re.compile(
    r"(首页|管理总览|项目详情|运行中心|恢复诊断|项目物料查看器|物料文档详情|[一-龥A-Za-z0-9]{2,18}(?:看板|工作台|总览|详情|中心|诊断|查看器|页面|列表))"
)
_STATUS_TERM_PATTERN = re.compile(
    r"(正常|阻塞|需介入|加载中|空状态|错误|可接力|需求缺口|需求草稿|需求冻结|运行中|降级|建议重建|建议 doctor|可浏览|无项目|已筛选)"
)
_ACTION_TERM_PATTERN = re.compile(
    r"(查看[一-龥A-Za-z0-9]{0,12}|进入[一-龥A-Za-z0-9]{0,12}|返回[一-龥A-Za-z0-9]{0,12}|切换[一-龥A-Za-z0-9]{0,12}|恢复[一-龥A-Za-z0-9]{0,12}|发布[一-龥A-Za-z0-9]{0,12}|重试[一-龥A-Za-z0-9]{0,12})"
)
_MODULE_TERM_PATTERN = re.compile(
    r"([一-龥A-Za-z0-9]{2,20}(?:摘要|头部|卡片|列表|总览|入口|视图|面板|步骤|信息|状态|反馈|导航|阅读区|文档正文区|文档阅读面板))"
)
_DEFAULT_STATUS_TERMS = ["正常", "阻塞", "加载中", "错误"]
_DEFAULT_ACTION_TERMS = ["查看详情", "进入详情", "返回总览"]
_DEFAULT_MODULE_TERMS = ["头部摘要", "状态反馈", "推荐动作"]
_DEFAULT_BANNED_TERMS = [
    "implementation",
    "verify",
    "review",
    "delivery",
    "machine contract",
    "canonical-envelope",
    "raw runtime log",
    "transaction_id",
    "projection_seq",
]
_PREFERRED_TERM_MAP = [
    {"from": "implementation", "to": "implement", "scope": "stage_vocabulary"},
    {"from": "verify", "to": "qa", "scope": "stage_vocabulary"},
    {"from": "review", "to": "qa", "scope": "stage_vocabulary"},
    {"from": "delivery", "to": "release", "scope": "stage_vocabulary"},
    {"from": "raw runtime log", "to": "运行摘要", "scope": "product_copy"},
    {"from": "machine contract", "to": "机器内部契约", "scope": "product_copy"},
]


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def normalize_requested_mode(value: str) -> str:
    requested_mode = str(value or "auto").strip().lower()
    if requested_mode not in _SUPPORTED_REQUESTED_MODES:
        raise ValueError("mode must be auto/llm/rule")
    return requested_mode


def _command_env_key(command_name: str) -> str:
    return str(command_name or "").strip().upper().replace("-", "_")


def _host_response_env_names(command_name: str) -> tuple[list[str], list[str]]:
    command_key = _command_env_key(command_name)
    json_names = []
    file_names = []
    if command_key:
        json_names.append(f"BEACON_HOST_{command_key}_RESPONSE_JSON")
        file_names.append(f"BEACON_HOST_{command_key}_RESPONSE_FILE")
    json_names.append("BEACON_HOST_SEMANTIC_RESPONSE_JSON")
    file_names.append("BEACON_HOST_SEMANTIC_RESPONSE_FILE")
    return json_names, file_names


def host_response_source(command_name: str) -> dict[str, Any]:
    json_names, file_names = _host_response_env_names(command_name)
    for env_name in json_names:
        raw = str(os.environ.get(env_name, "") or "").strip()
        if raw:
            return {
                "available": True,
                "source": "env_json",
                "env_name": env_name,
                "path": "",
                "raw": raw,
            }
    for env_name in file_names:
        raw_path = str(os.environ.get(env_name, "") or "").strip()
        if not raw_path:
            continue
        path = Path(raw_path)
        if not path.exists():
            continue
        return {
            "available": True,
            "source": "file_json",
            "env_name": env_name,
            "path": str(path),
            "raw": path.read_text(encoding="utf-8"),
        }
    return {
        "available": False,
        "source": "none",
        "env_name": "",
        "path": "",
        "raw": "",
    }


def load_host_response_json(command_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    source = host_response_source(command_name)
    if not bool(source.get("available")):
        return {}, source
    raw = str(source.get("raw") or "").strip()
    if not raw:
        return {}, source
    try:
        payload = json.loads(raw)
    except Exception:  # noqa: BLE001
        return {}, source
    return payload if isinstance(payload, dict) else {}, source


def build_semantic_capability_snapshot(
    command_name: str,
    *,
    disable_env: str,
    host_runtime: str | None = None,
) -> dict[str, Any]:
    resolved_host_runtime = detect_host_runtime(host_runtime)
    response = host_response_source(command_name)
    host_response_available = bool(response.get("available"))
    host_bridge_declared = _truthy(os.environ.get("BEACON_HOST_SEMANTIC_BRIDGE")) or host_response_available
    provider_available = bool(str(os.environ.get("BEACON_LLM_API_KEY", "") or "").strip())
    llm_disabled = _truthy(os.environ.get(disable_env))
    return {
        "schema_version": "1.0",
        "command_name": command_name,
        "host_runtime": resolved_host_runtime,
        "host_bridge_declared": host_bridge_declared,
        "host_response_available": host_response_available,
        "host_response_source": str(response.get("source") or "none"),
        "host_response_path": str(response.get("path") or ""),
        "host_semantic_ready": resolved_host_runtime in _SUPPORTED_HOSTS and host_response_available,
        "provider_available": provider_available,
        "provider_key_present": provider_available,
        "llm_disabled": llm_disabled,
        "disable_env": disable_env,
    }


def build_mode_contract(
    *,
    requested_mode: str,
    effective_mode: str,
    fallback_reason: str,
    capability_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "generator_mode": effective_mode,
        "fallback_reason": fallback_reason,
        "capability_snapshot": capability_snapshot,
    }


def llm_unavailable_message(command_label: str) -> str:
    return f"{command_label} semantic compile requires host semantic response or BEACON_LLM_API_KEY."


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower())
    return text.strip("-") or "semantic-layer"


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    path.write_text(content, encoding="utf-8")


def _relative_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except Exception:  # noqa: BLE001
        return str(path)


def semantic_artifact_dir(project_root: Path, version: str, feature: str) -> Path:
    return machine_trace_dir(project_root, version, "semantic", _slugify(feature))


def semantic_artifact_paths(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    root = semantic_artifact_dir(project_root, version, feature)
    return {
        "root": root,
        "semantic_contract": root / "semantic-contract.json",
        "semantic_dictionary": root / "semantic-dictionary.md",
        "semantic_usage_guidelines": root / "semantic-usage-guidelines.md",
        "semantic_review": root / "semantic-review.json",
    }


def _normalize_feature_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _feature_doc_names(feature: str) -> list[str]:
    raw = str(feature or "").strip().lower()
    return [
        raw,
        raw.replace(".", "-"),
        raw.replace("-", "."),
        _slugify(raw),
    ]


def _resolve_requirement_doc_path(directory: Path, feature: str) -> Path:
    candidates = _feature_doc_names(feature)
    for candidate in candidates:
        path = directory / f"{candidate}.md"
        if path.exists():
            return path
    normalized_candidates = {_normalize_feature_token(candidate) for candidate in candidates}
    for path in sorted(directory.glob("*.md")):
        if _normalize_feature_token(path.stem) in normalized_candidates:
            return path
    return directory / f"{_slugify(feature)}.md"


def _requirement_doc_candidates(project_root: Path, version: str, feature: str) -> dict[str, Path]:
    base = project_root / "docs" / "beacon" / version
    return {
        "prd": _resolve_requirement_doc_path(base / "prd", feature),
        "user-story": _resolve_requirement_doc_path(base / "user-story", feature),
        "test-case": _resolve_requirement_doc_path(base / "qa" / "test-cases", feature),
    }


def _load_requirement_docs(project_root: Path, version: str, feature: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for kind, path in _requirement_doc_candidates(project_root, version, feature).items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "type": kind,
                "path": _relative_path(path, project_root),
                "text": text,
                "fingerprint": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
    return docs


def _dedupe_terms(values: list[str], *, fallback: list[str], limit: int = 12) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw or "").strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        normalized.append(value)
        if len(normalized) >= limit:
            return normalized
    for raw in fallback:
        value = str(raw or "").strip()
        key = value.lower()
        if not value or key in seen:
            continue
        seen.add(key)
        normalized.append(value)
        if len(normalized) >= limit:
            break
    return normalized


def _extract_terms(text: str, pattern: re.Pattern[str], *, fallback: list[str], limit: int = 12) -> list[str]:
    return _dedupe_terms(pattern.findall(text), fallback=fallback, limit=limit)


def _extract_page_terms(text: str, feature: str) -> list[dict[str, str]]:
    labels = _dedupe_terms(_PAGE_TERM_PATTERN.findall(text), fallback=[feature], limit=8)
    return [
        {
            "label": label,
            "slug": _slugify(label),
            "source": "requirement_truth",
        }
        for label in labels
    ]


def _default_design_bridge(project_root: Path) -> dict[str, Any]:
    registry = load_skill_registry(project_root)
    payload = registry.get(_DEFAULT_TASTE_SKILL_ID, {})
    entry = str(payload.get("entry", "") or "").strip()
    install_hint = str(payload.get("install_hint", "") or "").strip() or (
        f"npx skills add {_DEFAULT_TASTE_SKILL_REPO} --skill {_DEFAULT_TASTE_SKILL_ID}"
    )
    return {
        "repo": str(payload.get("repo", _DEFAULT_TASTE_SKILL_REPO) or _DEFAULT_TASTE_SKILL_REPO),
        "skill_id": _DEFAULT_TASTE_SKILL_ID,
        "entry": entry,
        "detected": bool(entry),
        "kind": str(payload.get("kind", "external-default-bridge") or "external-default-bridge"),
        "supported_stages": list(payload.get("supported_stages", ["prototype", "implement"])),
        "capabilities": list(payload.get("capabilities", ["prototype", "implement", "taste-design"])),
        "install_hint": install_hint,
    }


def build_semantic_stage_context(
    project_root: Path,
    *,
    stage: str,
    feature: str,
    version: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    canonical_stage = normalize_workflow_stage(stage)
    if canonical_stage not in _SEMANTIC_STAGE_ORDER:
        canonical_stage = stage if stage in _SEMANTIC_STAGE_ORDER else "prototype"
    if run_id:
        context_path = stage_context_path(project_root, run_id, canonical_stage)
        payload = _read_json(context_path)
        if not payload:
            payload = build_stage_context(
                project_root,
                run_id=run_id,
                stage=canonical_stage,
                feature=feature,
                version=version,
            )
        payload.setdefault("semantic_context_source", "workflow-memory")
        return payload
    docs = _load_requirement_docs(project_root, version, feature)
    return {
        "schema_version": _SEMANTIC_SCHEMA_VERSION,
        "run_id": "",
        "stage": canonical_stage,
        "feature": feature,
        "version": version,
        "generated_at": now_iso(),
        "memory_recall": [],
        "lifecycle_events": [],
        "requirement_refs": [doc["path"] for doc in docs],
        "evidence_refs": [],
        "decision_trace": [],
        "blockers": [],
        "transaction_lineage": {
            "current_transaction_id": "",
            "projection_seq": "",
            "source_hash": "",
            "previous_transaction_id": "",
            "recent_transaction_ids": [],
            "attempt_seq": None,
            "action": "semantic_stage_context",
        },
        "semantic_context_source": "requirement-docs",
    }


def build_semantic_layer(
    project_root: Path,
    *,
    version: str,
    feature: str,
    stage: str,
    run_id: str | None = None,
    capability_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    docs = _load_requirement_docs(project_root, version, feature)
    stage_context = build_semantic_stage_context(
        project_root,
        stage=stage,
        feature=feature,
        version=version,
        run_id=run_id,
    )
    source_text = "\n".join(doc["text"] for doc in docs)
    page_names = _extract_page_terms(source_text, feature)
    status_labels = _extract_terms(source_text, _STATUS_TERM_PATTERN, fallback=_DEFAULT_STATUS_TERMS, limit=8)
    action_labels = _extract_terms(source_text, _ACTION_TERM_PATTERN, fallback=_DEFAULT_ACTION_TERMS, limit=10)
    module_labels = _extract_terms(source_text, _MODULE_TERM_PATTERN, fallback=_DEFAULT_MODULE_TERMS, limit=10)
    bridge = _default_design_bridge(project_root)
    source_fingerprints = {doc["type"]: doc["fingerprint"] for doc in docs}
    semantic_source = {
        "version": version,
        "feature": feature,
        "feature_slug": _slugify(feature),
        "stage": normalize_workflow_stage(stage),
        "requirement_refs": stage_context.get("requirement_refs", []),
        "evidence_refs": stage_context.get("evidence_refs", []),
        "transaction_lineage": stage_context.get("transaction_lineage", {}),
        "source_fingerprints": source_fingerprints,
        "page_names": page_names,
        "status_labels": status_labels,
        "action_labels": action_labels,
        "module_labels": module_labels,
        "preferred_terms": _PREFERRED_TERM_MAP,
        "banned_terms": _DEFAULT_BANNED_TERMS,
        "default_design_bridge": bridge,
    }
    source_hash = _stable_hash(semantic_source)
    projection_seq = f"semantic-{source_hash[:16]}"
    transaction_id = f"tx-semantic-{_slugify(feature)}-{projection_seq}"
    usage_guidelines = [
        "先引用 semantic-contract.json，再进入 prototype 或 implement，不要在阶段内临时翻译需求。",
        "页面名、状态名、模块名优先复用官方词表，避免 implementation / verify / delivery 这类旧阶段词汇出现在前台。",
        "允许 taste-skill 做设计增强，但不得覆盖 requirement truth 或反向改写 semantic contract。",
        "发现语义漂移时，优先重建 semantic layer，再继续 prototype freeze 或 implement delivery。",
    ]
    return {
        "schema_version": _SEMANTIC_SCHEMA_VERSION,
        "semantic_contract_version": _SEMANTIC_SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": _slugify(feature),
        "version": version,
        "stage": normalize_workflow_stage(stage),
        "generated_at": now_iso(),
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "transaction_id": transaction_id,
        "source_documents": [
            {
                "type": doc["type"],
                "path": doc["path"],
                "fingerprint": doc["fingerprint"],
            }
            for doc in docs
        ],
        "stage_context": stage_context,
        "official_language": {
            "page_names": page_names,
            "status_labels": status_labels,
            "module_labels": module_labels,
            "action_labels": action_labels,
            "preferred_terms": _PREFERRED_TERM_MAP,
            "banned_terms": list(_DEFAULT_BANNED_TERMS),
        },
        "usage_guidelines": usage_guidelines,
        "default_design_bridge": bridge,
        "compiler": {
            "semantic_context_source": str(stage_context.get("semantic_context_source", "") or ""),
            "capability_snapshot": capability_snapshot or {},
        },
    }


def _render_semantic_dictionary(contract: dict[str, Any]) -> str:
    official = contract.get("official_language", {}) if isinstance(contract.get("official_language"), dict) else {}
    lines = [
        f"# Semantic Dictionary: {contract['feature']}",
        "",
        "## 官方页面名",
        "",
    ]
    for item in official.get("page_names", []):
        if not isinstance(item, dict):
            continue
        lines.append(f"- {item.get('label', '')}")
    lines.extend(["", "## 官方状态名", ""])
    for item in official.get("status_labels", []):
        lines.append(f"- {item}")
    lines.extend(["", "## 官方模块名", ""])
    for item in official.get("module_labels", []):
        lines.append(f"- {item}")
    lines.extend(["", "## 官方动作名", ""])
    for item in official.get("action_labels", []):
        lines.append(f"- {item}")
    lines.extend(["", "## 禁用词", ""])
    for item in official.get("banned_terms", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _render_semantic_usage_guidelines(contract: dict[str, Any]) -> str:
    bridge = contract.get("default_design_bridge", {}) if isinstance(contract.get("default_design_bridge"), dict) else {}
    lines = [
        f"# Semantic Usage Guidelines: {contract['feature']}",
        "",
        "## 使用规则",
        "",
    ]
    for item in contract.get("usage_guidelines", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## 默认设计桥接",
            "",
            f"- repo: {bridge.get('repo', _DEFAULT_TASTE_SKILL_REPO)}",
            f"- skill: {bridge.get('skill_id', _DEFAULT_TASTE_SKILL_ID)}",
            f"- detected: {'yes' if bridge.get('detected') else 'no'}",
            f"- install: {bridge.get('install_hint', '')}",
            "",
        ]
    )
    return "\n".join(lines)


def write_semantic_layer(
    project_root: Path,
    *,
    version: str,
    feature: str,
    stage: str,
    run_id: str | None = None,
    capability_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    paths = semantic_artifact_paths(project_root, version, feature)
    existing = _read_json(paths["semantic_contract"])
    if existing and str(existing.get("feature", "") or "") == str(feature) and str(existing.get("version", "") or "") == str(version):
        artifacts = {key: _relative_path(path, project_root) for key, path in paths.items() if key != "root"}
        existing["artifacts"] = artifacts
        return existing

    contract = build_semantic_layer(
        project_root,
        version=version,
        feature=feature,
        stage=stage,
        run_id=run_id,
        capability_snapshot=capability_snapshot,
    )
    dictionary_md = _render_semantic_dictionary(contract)
    usage_md = _render_semantic_usage_guidelines(contract)
    review_payload = {
        "schema_version": _SEMANTIC_SCHEMA_VERSION,
        "feature": feature,
        "feature_slug": contract["feature_slug"],
        "version": version,
        "stage": contract["stage"],
        "generated_at": now_iso(),
        "overall_status": "ready",
        "blockers": list((contract.get("stage_context") or {}).get("blockers", [])),
        "default_design_bridge": contract.get("default_design_bridge", {}),
        "transaction_lineage": (contract.get("stage_context") or {}).get("transaction_lineage", {}),
    }

    _write_json(paths["semantic_contract"], contract)
    _write_text(paths["semantic_dictionary"], dictionary_md)
    _write_text(paths["semantic_usage_guidelines"], usage_md)
    _write_json(paths["semantic_review"], review_payload)

    artifacts = {key: _relative_path(path, project_root) for key, path in paths.items() if key != "root"}
    contract["artifacts"] = artifacts
    return contract


def load_or_build_semantic_layer(
    project_root: Path,
    *,
    version: str,
    feature: str,
    stage: str,
    run_id: str | None = None,
    capability_snapshot: dict[str, Any] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    if not persist:
        contract = build_semantic_layer(
            project_root,
            version=version,
            feature=feature,
            stage=stage,
            run_id=run_id,
            capability_snapshot=capability_snapshot,
        )
        contract["artifacts"] = {
            key: _relative_path(path, project_root)
            for key, path in semantic_artifact_paths(project_root, version, feature).items()
            if key != "root"
        }
        return contract
    return write_semantic_layer(
        project_root,
        version=version,
        feature=feature,
        stage=stage,
        run_id=run_id,
        capability_snapshot=capability_snapshot,
    )


def render_semantic_prompt_context(semantic_layer: dict[str, Any] | None) -> str:
    payload = semantic_layer if isinstance(semantic_layer, dict) else {}
    official = payload.get("official_language", {}) if isinstance(payload.get("official_language"), dict) else {}
    page_names = [str(item.get("label", "")).strip() for item in official.get("page_names", []) if isinstance(item, dict)]
    status_labels = [str(item).strip() for item in official.get("status_labels", []) if str(item).strip()]
    action_labels = [str(item).strip() for item in official.get("action_labels", []) if str(item).strip()]
    bridge = payload.get("default_design_bridge", {}) if isinstance(payload.get("default_design_bridge"), dict) else {}
    lines = [
        f"semantic_contract_version={payload.get('semantic_contract_version', _SEMANTIC_SCHEMA_VERSION)}",
        f"official_page_names={', '.join(page_names[:6])}",
        f"official_status_labels={', '.join(status_labels[:6])}",
        f"official_action_labels={', '.join(action_labels[:6])}",
        f"default_design_bridge={bridge.get('skill_id', _DEFAULT_TASTE_SKILL_ID)} @ {bridge.get('repo', _DEFAULT_TASTE_SKILL_REPO)}",
    ]
    return "\n".join(line for line in lines if line.strip())


def evaluate_semantic_contract(
    project_root: Path,
    *,
    version: str,
    feature: str,
) -> dict[str, Any]:
    paths = semantic_artifact_paths(project_root, version, feature)
    artifacts = {key: _relative_path(path, project_root) for key, path in paths.items() if key != "root"}
    missing_artifacts = [key for key, path in paths.items() if key != "root" and not path.exists()]
    if missing_artifacts:
        return {
            "status": "fail",
            "reason_code": "semantic_contract_missing",
            "message": "semantic layer artifacts missing",
            "feature": feature,
            "version": version,
            "artifacts": artifacts,
            "details": {"missing_artifacts": missing_artifacts},
        }

    contract = _read_json(paths["semantic_contract"])
    review = _read_json(paths["semantic_review"])
    official = contract.get("official_language", {}) if isinstance(contract.get("official_language"), dict) else {}
    page_names = official.get("page_names") if isinstance(official.get("page_names"), list) else []
    stage_context = contract.get("stage_context", {}) if isinstance(contract.get("stage_context"), dict) else {}
    bridge = contract.get("default_design_bridge", {}) if isinstance(contract.get("default_design_bridge"), dict) else {}
    transaction_ok = all(
        str(contract.get(field, "") or "").strip()
        for field in ("transaction_id", "source_hash", "projection_seq")
    )
    official_language_ready = bool(page_names) and bool(official.get("status_labels")) and bool(official.get("action_labels"))
    requirement_refs = stage_context.get("requirement_refs") if isinstance(stage_context.get("requirement_refs"), list) else []
    review_status = str(review.get("overall_status", "unknown") or "unknown").strip().lower()
    bridge_ok = (
        str(bridge.get("repo", "") or "").strip() == _DEFAULT_TASTE_SKILL_REPO
        and str(bridge.get("skill_id", "") or "").strip() == _DEFAULT_TASTE_SKILL_ID
    )
    if not transaction_ok:
        return {
            "status": "fail",
            "reason_code": "semantic_transaction_metadata_missing",
            "message": "semantic transaction metadata incomplete",
            "feature": feature,
            "version": version,
            "artifacts": artifacts,
            "details": {"transaction_id": contract.get("transaction_id", ""), "source_hash": contract.get("source_hash", ""), "projection_seq": contract.get("projection_seq", "")},
        }
    if not official_language_ready or not requirement_refs:
        return {
            "status": "fail",
            "reason_code": "semantic_official_language_missing",
            "message": "semantic official language or requirement refs incomplete",
            "feature": feature,
            "version": version,
            "artifacts": artifacts,
            "details": {
                "page_name_count": len(page_names),
                "status_label_count": len(official.get("status_labels", []) or []),
                "action_label_count": len(official.get("action_labels", []) or []),
                "requirement_ref_count": len(requirement_refs),
            },
        }
    if not bridge_ok:
        return {
            "status": "fail",
            "reason_code": "semantic_default_taste_bridge_drift",
            "message": "semantic default design bridge drift detected",
            "feature": feature,
            "version": version,
            "artifacts": artifacts,
            "details": bridge,
        }
    if review_status not in {"ready", "pass", "ok"}:
        return {
            "status": "warn",
            "reason_code": "semantic_review_missing",
            "message": "semantic review not ready",
            "feature": feature,
            "version": version,
            "artifacts": artifacts,
            "details": {"overall_status": review_status or "unknown"},
        }
    return {
        "status": "pass",
        "reason_code": "semantic_contract_ok",
        "message": "semantic contract ready",
        "feature": feature,
        "version": version,
        "artifacts": artifacts,
        "details": {
            "page_name_count": len(page_names),
            "requirement_ref_count": len(requirement_refs),
            "default_design_bridge": bridge,
        },
    }
