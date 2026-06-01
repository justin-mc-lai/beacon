"""Beacon PRD command surface."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from beacon.utils.artifact_paths import machine_root
from beacon.utils.diagram_truth import normalize_diagram_types, normalize_state_axes, render_diagram_truth_section
from beacon.utils.markdown_first_freeze import (
    build_markdown_first_compile_payload,
    build_markdown_first_legacy_prd_payload,
    build_markdown_first_prd_canonical,
    markdown_first_freeze_supported,
    stable_text_hash,
    stable_text_hash_uri,
)
from beacon.utils.project_metadata import metadata_machine_path, resolve_project_metadata_view
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.semantic_runtime import (
    build_mode_contract,
    build_semantic_capability_snapshot,
    execute_host_bridge_command,
    load_host_response_json,
    normalize_requested_mode,
)
from beacon.utils.skill_decision_surface import attach_skill_decision_surface
from beacon.utils.versioning import resolve_operational_docs_version, resolve_target_version
from beacon.utils.truth_template import render_prd_template as _render_prd_template

app = typer.Typer(name="prd", help="Generate Product Requirements Document")


def _with_prd_surface(
    payload: dict[str, object],
    *,
    reason_code: str = "",
    recommended_command: str = "",
    blocked: bool = False,
) -> dict[str, object]:
    return attach_skill_decision_surface(
        payload,
        stage="prd",
        reason_code=reason_code,
        recommended_command=recommended_command,
        blocked=blocked,
        dual_read_required=True,
    )

_TOOLING_KEYWORDS = (
    "toolkit",
    "skill",
    "friction",
    "generation",
    "generator",
    "template",
    "bootstrap",
    "doctor",
    "surface",
    "surfacing",
    "memory",
)
_RUNTIME_KEYWORDS = (
    "runtime",
    "projection",
    "control-plane",
    "control_plane",
    "pocketbase",
    "sqlite",
    "ledger",
    "board",
    "dashboard",
    "multi-project",
)


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", str(value or "").strip().lower())
    return text.strip("-") or "untitled-prd"


def _resolve_existing_prd_slug(project_root: Path, *, version: str, feature: str) -> str:
    direct = str(feature or "").strip()
    if direct:
        direct_path = project_root / "docs" / "beacon" / version / "prd" / f"{direct}.md"
        if direct_path.exists():
            return direct
    slug = _slugify(feature)
    slug_path = project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"
    if slug_path.exists():
        return slug
    return slug


def _stable_hash(payload: object) -> str:
    if isinstance(payload, str):
        encoded = payload.encode("utf-8")
    else:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _is_llm_disabled() -> bool:
    return str(os.environ.get("BEACON_PRD_DISABLE_LLM", "") or "").strip().lower() in {"1", "true", "yes", "on"}


def _semver_tuple(version: str) -> tuple[int, int, int]:
    normalized = str(version or "").strip().lower().lstrip("v")
    try:
        major, minor, patch = normalized.split(".")
        return int(major), int(minor), int(patch)
    except Exception:  # noqa: BLE001
        return (0, 0, 0)


def _source_refs(project_root: Path, version: str, existing_prds: list[str]) -> list[str]:
    refs: list[Path] = [
        project_root / "docs" / "beacon" / "global-boundaries.md",
        project_root / "docs" / "beacon" / version / "SUMMARY.md",
        project_root / "docs" / "beacon" / version / "execution" / "index.md",
    ]
    refs.extend(project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md" for slug in existing_prds)
    debug_index = project_root / ".beacon" / "debug" / "index.json"
    if debug_index.exists():
        refs.append(debug_index)
    metadata_path = metadata_machine_path(project_root)
    if metadata_path.exists():
        refs.append(metadata_path)
    output: list[str] = []
    for path in refs:
        if path.exists():
            output.append(str(path.relative_to(project_root)))
    return output


def _semantic_label(family: str) -> str:
    if family == "runtime_control_plane":
        return "运行态投影治理"
    if family == "tooling_surface":
        return "命令与技能面治理"
    return "通用需求治理"


def _render_semantic_prd(
    feature: str,
    *,
    version: str,
    track: str,
    family: str,
    existing_prds: list[str],
    slug: str,
) -> str:
    """v1.4.12+: truth_template-aligned semantic-compiled PRD (no section numbering)."""
    anchor = f"`{existing_prds[0]}`" if existing_prds else "`none`"
    semantic = _semantic_label(family)
    is_parallel = track == "parallel"
    relationship_section: list[str] = []
    if is_parallel:
        relationship_section = [
            "## Related PRDs",
            "",
            f"- 主线锚点：{anchor}",
            "- 本并行线只补强主线已承诺能力，不单独定义产品真相。",
            "- 需求、实现、验收均回写同一版本包，避免并行线漂移。",
        ]
    else:
        relationship_section = [
            "## Related PRDs",
            "",
            "- 当前主线依赖真实项目输入与已有版本包约束。",
            "- 并行修复项应回挂到本主线，不新增一级主命令。",
            "- 后续扩展保持 canonical-first 与 requirement traceability。",
        ]

    lines = [
        f"# PRD: {feature}",
        "",
        f"**Feature**: `{slug}`",
        f"**Version**: `{version}`",
        f"**Status**: `draft semantic-compiled`",
        f"**Date**: `{datetime.now().strftime('%Y-%m-%d')}`",
        "**Language**: `zh`",
        f"**Track**: `{track}`",
        f"**Semantic Label**: `{semantic}`",
        "",
        "## Overview",
        "",
        f"本 PRD 定义 `{semantic}` 在当前版本线 `{version}` 的 requirement truth，",
        "覆盖问题定义、目标、设计原则、范围、功能需求、契约边界与验收标准。",
        "",
        "## Outline",
        "",
        "<!-- FILL: Mermaid diagram showing the feature's core flow or state transitions.",
        "     Use flowchart TD/LR for procedural features, stateDiagram-v2 for stateful features. -->",
        "",
        "```mermaid",
        "flowchart TD",
        "    A[Truth Definition] --> B[Contract Boundary]",
        "    B --> C[Acceptance Verification]",
        "    C --> D[Release Gate]",
        "```",
        "",
        "## Context",
        "",
        "- Global boundaries: `docs/beacon/global-boundaries.md`",
        f"- Version summary: `docs/beacon/{version}/SUMMARY.md`",
        f"- Execution index: `docs/beacon/{version}/execution/index.md`",
        f"- Existing PRDs in line: {', '.join(f'`{name}`' for name in existing_prds) if existing_prds else 'none'}",
        "",
        "## Problem",
        "",
        "### 当前断层",
        f"- 当前 `{semantic}` 仍存在 requirement truth 与投影/执行结果之间的稳定性缺口。",
        "",
        "### 触发信号",
        "- 真实项目运行中出现状态噪音、证据链断点或命令语义漂移，需要在版本包内正式收敛。",
        "",
        "### 为什么现在做",
        "- 若不在本版本修复，后续 prototype/implement/qa/release 会继续放大漂移风险。",
        "",
        "## Goals",
        "",
        "### 主要目标",
        "- 把本需求的边界、分层、恢复策略和验收链固化为可执行 contract。",
        "",
        "### 非目标",
        "- 不新增公开一级主命令，不改写 Beacon 既有主流程心智面。",
        "",
        "## Design Principles",
        "",
        "### Canonical First",
        "- 先形成 canonical 输入，再投影到 human/machine/runtime 各面，禁止多源并写。",
        "",
        "### Transaction First",
        "- 写入流程遵循 prepare/validate/stage/commit/publish/verify，失败必须显式可观测。",
        "",
        "### Truth Boundary",
        "- 正式真相保持在 `docs/beacon/<version>/` 与 `.beacon/`，投影层仅做管理与观察。",
        "",
        "## Scope",
        "",
        "### In Scope",
        "- 本 feature 的需求冻结、执行约束、验收闭环与证据写回。",
        "- 与主线一致的 gate/review/doctor/status 判定口径。",
        "",
        "### Out of Scope",
        "- UI 高保真实现与非本版本产品化扩展能力。",
        "- 与本 feature 无关的跨域重构。",
        "",
        "## Functional Requirements",
        "",
        "### FR-001 输入与输出 contract",
        "- 需求输入、执行状态与交付证据必须可追溯，并可被机器校验。",
        "",
        "### FR-002 失败语义与恢复策略",
        "- 任一关键写入失败必须留下失败记录并阻断关键 gate，恢复路径可执行。",
        "",
        "### FR-003 验收链路一致",
        "- `prd -> user-story -> test-case -> implement -> qa -> release` 的映射关系持续一致。",
        "",
        "## Source Contract",
        "",
        "### 边界",
        "- 人类面用于评审与决策，机器面用于校验与自动化，不允许相互反向漂移。",
        "",
        "### 分层",
        "- requirement layer 负责定义承诺；execution layer 负责实现；qa/release layer 负责验证与准入。",
        "",
        "### 恢复策略",
        "- 事务失败后优先重建 canonical 投影，再重跑 gate/review；禁止带病继续发布。",
        "",
        "## Risks",
        "",
        "| 风险 | 影响 | 缓解 |",
        "|------|------|------|",
        "| 需求语义退化为模板占位 | 高 | 增加 contract 校验与 machine 编译证据，失败时降级并记录原因 |",
        "| 多写入点状态不一致 | 高 | 事务元数据统一并在 gate/review/release 阶段强校验 |",
        "",
        "## Acceptance Criteria",
        "",
        "### AC-001 主路径验收",
        "- 关键功能按 requirement chain 全量可追溯，且存在对应测试与证据。",
        "",
        "### AC-002 失败可恢复",
        "- 失败事务可被显式识别并触发恢复流程，关键 gate 会阻断。",
        "",
        "### AC-003 文档与实现一致",
        "- PRD、User Story、Test Case 与实现证据之间无结构性漂移。",
        "",
        "### AC-004 风险可审计",
        "- 所有降级、fallback 与未决项都在 machine 证据中可查询。",
        "",
        "## Non-Goals",
        "",
        "<!-- FILL: Explicitly excluded items beyond scope. -->",
        "",
        "## Success Metrics",
        "",
        "- 主指标：关键 gate 阻断原因可解释且可复现。",
        "- 辅指标：版本线 requirement closure 与执行证据一致性持续提升。",
        "",
        *relationship_section,
        "",
    ]
    if str(os.environ.get("BEACON_PRD_FORCE_INVALID_LLM_OUTPUT", "") or "").strip().lower() in {"1", "true", "yes", "on"}:
        lines.append("TBD")
    return "\n".join(lines)


def _validate_contract(content: str, *, require_no_placeholders: bool) -> dict[str, object]:
    # v1.4.12+: 7 mandatory heading slots (new/legacy, one from each pair).
    # Pairings follow the canonical spec — they are intentionally non-semantic
    # to decouple validation from heading-name semantics.
    _heading_pairs = [
        ("## Context", "## 1. 问题"),
        ("## Problem", "## 2. 目标"),
        ("## Goals", "## 3. 设计原则"),
        ("## Design Principles", "## 4. 范围"),
        ("## Scope", "## 5. 功能需求"),
        ("## Functional Requirements", "## 8. 验收标准"),
        ("## Acceptance Criteria", None),
    ]
    missing: list[str] = []
    for new_h, legacy_h in _heading_pairs:
        found_new = new_h and new_h in content
        found_legacy = legacy_h and legacy_h in content
        if not found_new and not found_legacy:
            missing.append(new_h or legacy_h)
    placeholder_patterns = [r"\bTBD\b", r"\bTODO\b", r"\?\?\?", r"待补充"]
    placeholder_hits: list[str] = []
    for pattern in placeholder_patterns:
        if re.search(pattern, content, flags=re.IGNORECASE):
            placeholder_hits.append(pattern)
    semantic_hits = {
        "boundary": "边界" in content,
        "layering": "分层" in content,
        "recovery": "恢复" in content,
        "acceptance": "验收" in content,
        "risk_mitigation": "风险" in content and "缓解" in content,
    }
    ok = not missing and all(bool(v) for v in semantic_hits.values())
    if require_no_placeholders and placeholder_hits:
        ok = False
    return {
        "ok": ok,
        "missing_headings": missing,
        "placeholder_hits": placeholder_hits,
        "semantic_hits": semantic_hits,
    }


def _extract_host_prd_markdown() -> str:
    payload, _ = load_host_response_json("prd")
    if not payload:
        return ""
    candidates = [
        payload.get("markdown"),
        payload.get("content"),
    ]
    nested = payload.get("payload")
    if isinstance(nested, dict):
        candidates.extend([nested.get("markdown"), nested.get("content")])
    for item in candidates:
        text = str(item or "").strip()
        if text:
            return text
    return ""


def _load_bridge_payload(payload_json: str = "") -> dict[str, object]:
    raw = str(payload_json or "").strip()
    if not raw:
        raw = sys.stdin.read().strip()
    if not raw:
        raise typer.BadParameter("bridge payload missing")
    try:
        payload = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        raise typer.BadParameter(f"invalid bridge payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise typer.BadParameter("bridge payload must be a JSON object")
    return payload


def _build_prd_host_bridge_request(
    *,
    feature: str,
    version: str,
    track: str,
    family: str,
    existing_prds: list[str],
    slug: str,
) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "command_name": "prd",
        "request_kind": "prd-semantic-compile",
        "feature": feature,
        "version": version,
        "track": track,
        "family": family,
        "existing_prds": list(existing_prds),
        "slug": slug,
    }


def _extract_host_prd_markdown_with_bridge(request_payload: dict[str, object]) -> str:
    payload, _ = execute_host_bridge_command("prd", request_payload)
    candidates: list[object] = []
    if isinstance(payload, dict):
        candidates.extend([payload.get("markdown"), payload.get("content")])
        nested = payload.get("payload")
        if isinstance(nested, dict):
            candidates.extend([nested.get("markdown"), nested.get("content")])
    if not payload:
        return _extract_host_prd_markdown()
    for item in candidates:
        text = str(item or "").strip()
        if text:
            return text
    return _extract_host_prd_markdown()


@app.command("host-bridge", hidden=True)
def host_bridge(
    payload_json: str = typer.Argument("", help="Optional bridge request JSON; default reads stdin"),
):
    """Hidden host-native bridge endpoint for PRD semantic compile."""
    try:
        payload = _load_bridge_payload(payload_json)
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2) from exc

    if str(payload.get("request_kind") or "").strip() != "prd-semantic-compile":
        typer.echo("unsupported prd bridge request_kind", err=True)
        raise typer.Exit(2)

    markdown = _render_semantic_prd(
        str(payload.get("feature") or "").strip(),
        version=str(payload.get("version") or "").strip(),
        track=str(payload.get("track") or "main").strip() or "main",
        family=str(payload.get("family") or "general").strip() or "general",
        existing_prds=[str(item).strip() for item in (payload.get("existing_prds") or []) if str(item).strip()],
        slug=str(payload.get("slug") or "").strip() or _slugify(str(payload.get("feature") or "")),
    )
    typer.echo(json.dumps({"markdown": markdown, "model": "beacon-prd-host-bridge"}, ensure_ascii=False))


def _machine_prd_dir(project_root: Path, version: str) -> Path:
    return machine_root(project_root, version) / "prd"


def _legacy_prd_path(project_root: Path, slug: str) -> Path:
    return project_root / ".beacon" / "prd" / f"{slug}.json"


def _legacy_prd_transaction_path(project_root: Path, slug: str) -> Path:
    return project_root / ".beacon" / "transactions" / f"prd-{slug}.json"


def _prd_transaction_dir(project_root: Path) -> Path:
    return project_root / ".beacon" / "state" / "prd-transactions"


def _latest_prd_transaction_path(project_root: Path, slug: str) -> Path:
    return _prd_transaction_dir(project_root) / f"latest-{slug}.json"


def _read_json_dict(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(content, encoding="utf-8")
    temp.replace(path)


def _write_outputs_transactional(outputs: dict[Path, str]) -> None:
    backups: dict[Path, str] = {}
    created: list[Path] = []
    for path in outputs:
        if path.exists():
            backups[path] = path.read_text(encoding="utf-8")
        else:
            created.append(path)
    try:
        for path, content in outputs.items():
            _write_text_atomic(path, content)
    except Exception:  # noqa: BLE001
        for path, content in backups.items():
            _write_text_atomic(path, content)
        for path in created:
            if path.exists():
                path.unlink(missing_ok=True)
        raise


def _project_metadata_context(project_root: Path, *, version: str) -> dict[str, object]:
    metadata_path = metadata_machine_path(project_root)
    return {
        "metadata_ref": str(metadata_path.relative_to(project_root)) if metadata_path.exists() else "",
        "resolved_metadata_view": resolve_project_metadata_view(project_root, version=version),
    }


def _persist_prd_projection(
    *,
    project_root: Path,
    output_path: Path,
    compile_path: Path,
    canonical_path: Path,
    feature: str,
    slug: str,
    version: str,
    template: dict[str, str],
    requested_mode: str,
    effective_mode: str,
    generator_mode: str,
    fallback_reason: str,
    capability_snapshot: dict[str, object],
    model: str,
    requested_diagrams: list[str],
    requested_state_axes: list[str],
    md_content: str,
    contract: dict[str, object],
    source_refs: list[str],
    project_metadata_context: dict[str, object],
) -> dict[str, object]:
    markdown_first = markdown_first_freeze_supported(version)
    mode_contract = build_mode_contract(
        requested_mode=requested_mode,
        effective_mode=effective_mode,
        fallback_reason=fallback_reason,
        capability_snapshot=capability_snapshot,
    )
    if markdown_first:
        canonical = build_markdown_first_prd_canonical(
            feature=feature,
            slug=slug,
            version=version,
            template=template,
            mode_contract=mode_contract,
            model=model,
            requested_diagrams=requested_diagrams,
            requested_state_axes=requested_state_axes,
            source_refs=source_refs,
            project_metadata_context=project_metadata_context,
            contract=contract,
            md_content=md_content,
        )
    else:
        canonical = {
            "schema_version": "1.0",
            "feature": feature,
            "feature_slug": slug,
            "version": version,
            "track": template["track"],
            "family": template["family"],
            "label": template["label"],
            **mode_contract,
            "model": model,
            "diagram_truth_request": {
                "diagram_types": requested_diagrams,
                "state_axes": requested_state_axes,
            },
            "source_refs": source_refs,
            "project_metadata_context": project_metadata_context,
            "contract": contract,
            "markdown": md_content,
        }
    source_hash = _stable_hash(canonical)
    projection_seq = f"prd-{source_hash[:16]}"
    transaction_id = f"tx-prd-{slug}-{projection_seq}"
    latest_pointer_path = _latest_prd_transaction_path(project_root, slug)
    previous_latest = _read_json_dict(latest_pointer_path)
    previous_transaction_id = str(previous_latest.get("transaction_id") or "").strip()
    previous_projection_seq = str(previous_latest.get("projection_seq") or "").strip()
    previous_source_hash = str(previous_latest.get("source_hash") or "").strip()
    supersedes_transaction_id = previous_transaction_id if previous_transaction_id and previous_transaction_id != transaction_id else ""
    supersedes_projection_seq = previous_projection_seq if supersedes_transaction_id else ""
    supersedes_source_hash = previous_source_hash if supersedes_transaction_id else ""

    canonical["transaction"] = {
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "committed_at": "",
        "sink_checksums": {
            "human": "missing",
            "machine": "missing",
        },
        "status": "pending",
        "supersedes_transaction_id": supersedes_transaction_id,
        "supersedes_projection_seq": supersedes_projection_seq,
        "supersedes_source_hash": supersedes_source_hash,
    }

    transaction_record = {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "feature_slug": slug,
        "version": version,
        "requested_mode": requested_mode,
        "effective_mode": effective_mode,
        "generator_mode": generator_mode,
        "fallback_reason": fallback_reason,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "status": "failed_transaction",
        "committed_at": "",
        "sink_checksums": {
            "human": "missing",
            "machine": "missing",
        },
        "source_refs": source_refs,
        "error": "",
        "supersedes_transaction_id": supersedes_transaction_id,
        "supersedes_projection_seq": supersedes_projection_seq,
        "supersedes_source_hash": supersedes_source_hash,
    }
    tx_record_path = _prd_transaction_dir(project_root) / f"{transaction_id}.json"
    tx_record_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        _write_outputs_transactional(
            {
                output_path: md_content,
                canonical_path: json.dumps(canonical, ensure_ascii=False, indent=2),
            }
        )
        sink_checksums = {
            "human": _stable_hash(output_path.read_text(encoding="utf-8")),
            "machine": _stable_hash(canonical_path.read_text(encoding="utf-8")),
        }
        committed_at = now_iso()
        if markdown_first:
            compile_payload = build_markdown_first_compile_payload(
                feature=feature,
                slug=slug,
                version=version,
                md_content=md_content,
                contract=contract,
                transaction_id=transaction_id,
                source_hash=source_hash,
                projection_seq=projection_seq,
                committed_at=committed_at,
                sink_checksums=sink_checksums,
                requested_mode=requested_mode,
                effective_mode=effective_mode,
                generator_mode=generator_mode,
                fallback_reason=fallback_reason,
                capability_snapshot=capability_snapshot,
                source_refs=source_refs,
                project_metadata_context=project_metadata_context,
                model=model,
                requested_diagrams=requested_diagrams,
                requested_state_axes=requested_state_axes,
                supersedes_transaction_id=supersedes_transaction_id,
                supersedes_projection_seq=supersedes_projection_seq,
            )
        else:
            compile_payload = {
                "schema_version": "1.0",
                "feature": feature,
                "feature_slug": slug,
                "version": version,
                "effective_mode": effective_mode,
                "generator_mode": generator_mode,
                "requested_mode": requested_mode,
                "model": model,
                "diagram_truth_request": {
                    "diagram_types": requested_diagrams,
                    "state_axes": requested_state_axes,
                },
                "fallback_reason": fallback_reason,
                "capability_snapshot": capability_snapshot,
                "source_refs": source_refs,
                "project_metadata_context": project_metadata_context,
                "constraint_hits": contract.get("semantic_hits", {}),
                "missing_headings": contract.get("missing_headings", []),
                "open_questions": contract.get("placeholder_hits", []),
                "contract_ok": bool(contract.get("ok", False)),
                "compile_hash": _stable_hash(md_content),
                "source_hash": source_hash,
                "projection_seq": projection_seq,
                "transaction_id": transaction_id,
                "committed_at": committed_at,
                "sink_checksums": sink_checksums,
                "status": "applied",
                "supersedes_transaction_id": supersedes_transaction_id,
                "supersedes_projection_seq": supersedes_projection_seq,
            }
        write_json(compile_path, compile_payload)
        canonical["transaction"] = {
            "transaction_id": transaction_id,
            "source_hash": source_hash,
            "projection_seq": projection_seq,
            "committed_at": committed_at,
            "sink_checksums": sink_checksums,
            "status": "applied",
            "supersedes_transaction_id": supersedes_transaction_id,
            "supersedes_projection_seq": supersedes_projection_seq,
            "supersedes_source_hash": supersedes_source_hash,
        }
        write_json(canonical_path, canonical)
        transaction_record.update(
            {
                "status": "applied",
                "committed_at": committed_at,
                "sink_checksums": sink_checksums,
            }
        )
    except Exception as exc:  # noqa: BLE001
        transaction_record.update({"error": str(exc)})
        write_json(tx_record_path, transaction_record)
        raise

    write_json(tx_record_path, transaction_record)
    legacy_machine_path = _legacy_prd_path(project_root, slug)
    legacy_machine_path.parent.mkdir(parents=True, exist_ok=True)
    if markdown_first:
        legacy_machine_payload = build_markdown_first_legacy_prd_payload(
            feature=feature,
            slug=slug,
            version=version,
            template=template,
            requested_mode=requested_mode,
            effective_mode=effective_mode,
            generator_mode=generator_mode,
            fallback_reason=fallback_reason,
            md_content=md_content,
            transaction=canonical["transaction"],
        )
    else:
        legacy_machine_payload = {
            "metadata": {
                "feature": feature,
                "feature_slug": slug,
                "version": version,
            },
            "content": md_content,
            "markdown": md_content,
            "semantic_payload": {
                "track": template["track"],
                "family": template["family"],
                "label": template["label"],
            },
            "mode_contract": {
                "compilation_mode": requested_mode,
                "effective_mode": effective_mode,
                "generator_mode": generator_mode,
                "fallback_reason": fallback_reason,
            },
            "transaction": canonical["transaction"],
        }
    write_json(legacy_machine_path, legacy_machine_payload)
    legacy_transaction_path = _legacy_prd_transaction_path(project_root, slug)
    legacy_transaction_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        legacy_transaction_path,
        {
            "canonical_envelope": canonical,
            "sinks": [
                {"path": str(output_path.relative_to(project_root)), "kind": "human"},
                {"path": str(legacy_machine_path.relative_to(project_root)), "kind": "machine"},
            ],
            "latest_transaction_id": transaction_id,
            "supersedes_transaction_id": supersedes_transaction_id,
        },
    )
    latest_pointer = {
        "schema_version": "1.0",
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "transaction_id": transaction_id,
        "source_hash": source_hash,
        "projection_seq": projection_seq,
        "canonical_path": str(canonical_path.relative_to(project_root)),
        "compile_path": str(compile_path.relative_to(project_root)),
        "legacy_machine_path": str(legacy_machine_path.relative_to(project_root)),
        "updated_at": str(canonical["transaction"].get("committed_at") or now_iso()),
        "supersedes_transaction_id": supersedes_transaction_id,
        "supersedes_projection_seq": supersedes_projection_seq,
        "supersedes_source_hash": supersedes_source_hash,
        "status": "applied",
    }
    write_json(latest_pointer_path, latest_pointer)
    return {
        "canonical": canonical,
        "compile_path": compile_path,
        "canonical_path": canonical_path,
        "transaction_path": tx_record_path,
        "legacy_machine_path": legacy_machine_path,
        "legacy_transaction_path": legacy_transaction_path,
        "latest_transaction_path": latest_pointer_path,
        "transaction_id": transaction_id,
        "projection_seq": projection_seq,
        "source_hash": source_hash,
    }


def _build_prd_audit_payload(project_root: Path, *, version: str, feature: str) -> dict[str, object]:
    slug = _resolve_existing_prd_slug(project_root, version=version, feature=feature)
    prd_path = project_root / "docs" / "beacon" / version / "prd" / f"{slug}.md"
    payload: dict[str, object] = {
        "feature": feature,
        "feature_slug": slug,
        "version": version,
        "prd_path": str(prd_path),
        "exists": prd_path.exists(),
        "checks": [],
        "failure_codes": [],
        "status": "missing",
        "contract": {},
    }
    if not prd_path.exists():
        payload["failure_codes"] = ["human_prd_missing"]
        return payload
    markdown = prd_path.read_text(encoding="utf-8")
    contract = _validate_contract(markdown, require_no_placeholders=False)
    markdown_first = markdown_first_freeze_supported(version)
    payload["contract"] = contract
    checks: list[dict[str, object]] = [
        {
            "name": "markdown_contract",
            "status": "pass" if bool(contract.get("ok")) else "fail",
            "details": {
                "missing_headings": contract.get("missing_headings", []),
                "placeholder_hits": contract.get("placeholder_hits", []),
                "semantic_hits": contract.get("semantic_hits", {}),
            },
        }
    ]
    failure_codes: list[str] = []

    def _append_check(name: str, ok: bool, **details: object) -> None:
        checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})
        if not ok:
            failure_codes.append(name)

    legacy_path = _legacy_prd_path(project_root, slug)
    legacy_payload = _read_json_dict(legacy_path)
    legacy_markdown = str(legacy_payload.get("content") or legacy_payload.get("markdown") or "")
    legacy_hash = str(legacy_payload.get("markdown_hash") or "").strip()
    legacy_source_path = ""
    if isinstance(legacy_payload.get("source_paths"), dict):
        legacy_source_path = str(legacy_payload["source_paths"].get("prd") or "").strip()
    legacy_ok = (
        legacy_path.exists()
        and (
            (legacy_hash == stable_text_hash_uri(markdown) and legacy_source_path.endswith(f"/prd/{slug}.md"))
            if markdown_first
            else legacy_markdown.strip() == markdown.strip()
        )
    )
    _append_check(
        "legacy_machine_mirror_sync",
        legacy_ok,
        path=str(legacy_path.relative_to(project_root)) if legacy_path.exists() else str(legacy_path),
        exists=legacy_path.exists(),
        markdown_hash=legacy_hash,
        expected_markdown_hash=stable_text_hash_uri(markdown) if markdown_first else "",
        mode="markdown_first_state" if markdown_first else "fulltext_mirror",
    )

    canonical_path = _machine_prd_dir(project_root, version) / f"{slug}.canonical.json"
    canonical_payload = _read_json_dict(canonical_path)
    canonical_markdown = str(canonical_payload.get("markdown") or "")
    canonical_hash = str(canonical_payload.get("markdown_hash") or "").strip()
    canonical_source_path = ""
    if isinstance(canonical_payload.get("source_paths"), dict):
        canonical_source_path = str(canonical_payload["source_paths"].get("prd") or "").strip()
    canonical_ok = (
        canonical_path.exists()
        and (
            (canonical_hash == stable_text_hash_uri(markdown) and canonical_source_path.endswith(f"/prd/{slug}.md"))
            if markdown_first
            else canonical_markdown.strip() == markdown.strip()
        )
    )
    _append_check(
        "canonical_machine_mirror_sync",
        canonical_ok,
        path=str(canonical_path.relative_to(project_root)) if canonical_path.exists() else str(canonical_path),
        exists=canonical_path.exists(),
        markdown_hash=canonical_hash,
        expected_markdown_hash=stable_text_hash_uri(markdown) if markdown_first else "",
        mode="markdown_first_state" if markdown_first else "fulltext_mirror",
    )

    compile_path = _machine_prd_dir(project_root, version) / f"{slug}.compile.json"
    compile_payload = _read_json_dict(compile_path)
    compile_hash = str(compile_payload.get("compile_hash") or "").strip()
    _append_check(
        "compile_machine_mirror_sync",
        compile_path.exists() and compile_hash == stable_text_hash(markdown) and bool(compile_payload.get("contract_ok", False)) == bool(contract.get("ok", False)),
        path=str(compile_path.relative_to(project_root)) if compile_path.exists() else str(compile_path),
        exists=compile_path.exists(),
        compile_hash=compile_hash,
        expected_compile_hash=stable_text_hash(markdown),
        compile_contract_ok=bool(compile_payload.get("contract_ok", False)),
        current_contract_ok=bool(contract.get("ok", False)),
    )

    latest_pointer_path = _latest_prd_transaction_path(project_root, slug)
    latest_pointer = _read_json_dict(latest_pointer_path)
    canonical_transaction = canonical_payload.get("transaction") if isinstance(canonical_payload.get("transaction"), dict) else {}
    latest_tx_id = str(latest_pointer.get("transaction_id") or "").strip()
    canonical_tx_id = str(canonical_transaction.get("transaction_id") or "").strip()
    _append_check(
        "latest_transaction_pointer_sync",
        latest_pointer_path.exists()
        and bool(latest_tx_id)
        and latest_tx_id == canonical_tx_id
        and str(latest_pointer.get("source_hash") or "").strip() == str(canonical_transaction.get("source_hash") or "").strip(),
        path=str(latest_pointer_path.relative_to(project_root)) if latest_pointer_path.exists() else str(latest_pointer_path),
        exists=latest_pointer_path.exists(),
        latest_transaction_id=latest_tx_id,
        canonical_transaction_id=canonical_tx_id,
    )

    overall_ok = bool(contract.get("ok")) and not failure_codes
    payload["checks"] = checks
    payload["failure_codes"] = failure_codes
    payload["status"] = "pass" if overall_ok else ("contract_invalid" if not bool(contract.get("ok")) else "drift")
    return payload


def _existing_prd_names(project_root: Path, version: str, *, exclude_slug: str) -> list[str]:
    prd_dir = project_root / "docs" / "beacon" / version / "prd"
    if not prd_dir.exists():
        return []
    names: list[str] = []
    for path in sorted(prd_dir.glob("*.md")):
        if path.stem == exclude_slug:
            continue
        names.append(path.stem)
    return names


def _classify_prd(feature: str, *, existing_prds: list[str]) -> dict[str, str]:
    slug = _slugify(feature)
    track = "parallel" if existing_prds else "main"

    if any(keyword in slug for keyword in _TOOLING_KEYWORDS):
        family = "tooling_surface"
    elif any(keyword in slug for keyword in _RUNTIME_KEYWORDS):
        family = "runtime_control_plane"
    else:
        family = "general"

    label = {
        ("main", "runtime_control_plane"): "主 PRD / runtime-control-plane",
        ("parallel", "runtime_control_plane"): "并行 PRD / runtime-control-plane",
        ("main", "tooling_surface"): "主 PRD / tooling-surface",
        ("parallel", "tooling_surface"): "并行 PRD / tooling-surface",
        ("main", "general"): "主 PRD / general",
        ("parallel", "general"): "并行 PRD / general",
    }[(track, family)]
    return {"track": track, "family": family, "label": label, "slug": slug}


def _context_block(version: str, *, existing_prds: list[str]) -> str:
    existing = ", ".join(f"`{name}`" for name in existing_prds) if existing_prds else "none"
    return "\n".join(
        [
            "## Context",
            "",
            f"- Global boundaries: `docs/beacon/global-boundaries.md`",
            f"- Version summary: `docs/beacon/{version}/SUMMARY.md`",
            f"- Execution index: `docs/beacon/{version}/execution/index.md`",
            f"- Existing PRDs in line: {existing}",
            "",
        ]
    )


def _main_problem_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 1. 问题",
            "",
            "### 1.1 当前运行态 / requirement 断层",
            "- 待补充：当前版本线为什么需要引入 runtime / projection / control-plane 能力。",
            "",
            "### 1.2 真实环境触发信号",
            "- 待补充：列出来自真实项目、真实 run、真实 debug 的摩擦输入。",
            "",
            "### 1.3 为什么现在做",
            "- 待补充：说明若不处理会如何影响版本主线与后续验收。",
            "",
        ]
    return [
        "## 1. 问题",
        "",
        "### 1.1 当前缺口",
        "- 待补充：当前 Beacon / 项目在 requirement、实现或交付上的真实缺口。",
        "",
        "### 1.2 触发背景",
        "- 待补充：为什么这个问题在当前版本线被正式提出。",
        "",
        "### 1.3 为什么现在做",
        "- 待补充：说明延期的代价、当前窗口期与版本必要性。",
        "",
    ]


def _parallel_problem_lines(family: str, existing_prds: list[str]) -> list[str]:
    anchor = f"`{existing_prds[0]}`" if existing_prds else "`<main-prd>`"
    if family == "tooling_surface":
        return [
            "## 1. 问题",
            "",
            f"本并行 PRD 依附主线 {anchor}，用于补齐命令面、skill surface、模板生成或 friction repair 的结构性缺口。",
            "",
            "### 1.1 当前断层",
            "- 待补充：当前命令行为 / skill 暴露 / 文档承诺之间的不一致。",
            "",
            "### 1.2 为什么不能继续人工兜底",
            "- 待补充：说明 generic template、隐藏入口或恢复策略不清带来的真实成本。",
            "",
            "### 1.3 本线与主 PRD 的边界",
            "- 待补充：明确这是补强主线，不是另起一条产品真相。",
            "",
        ]
    return [
        "## 1. 问题",
        "",
        f"本并行 PRD 依附主线 {anchor}，用于补齐一个必须单独冻结的实现/治理切面。",
        "",
        "### 1.1 当前补强点",
        "- 待补充：这条并行线解决的具体缺口。",
        "",
        "### 1.2 与主 PRD 的冲突风险",
        "- 待补充：若该线不冻结，主线会出现什么漂移或落空。",
        "",
        "### 1.3 为什么独立成并行 PRD",
        "- 待补充：说明为什么它不能只作为主 PRD 的一小段备注。",
        "",
    ]


def _goal_lines(family: str) -> list[str]:
    base = [
        "## 2. 目标",
        "",
        "### 2.1 主要目标",
        "- 待补充：定义本 PRD 真正要关闭的业务/产品/系统缺口。",
        "",
        "### 2.2 非目标",
        "- 待补充：明确当前版本不会承担的内容，防止范围漂移。",
        "",
    ]
    if family == "runtime_control_plane":
        base.extend(
            [
                "### 2.3 Truth 与 Projection 边界",
                "- 待补充：明确 docs/.beacon 与投影层的职责边界。",
                "",
            ]
        )
    elif family == "tooling_surface":
        base.extend(
            [
                "### 2.3 命令面 / skill 面一致性目标",
                "- 待补充：说明哪些 surface 需要被正式补齐并保持一致。",
                "",
            ]
        )
    return base


def _principle_lines(family: str) -> list[str]:
    lines = [
        "## 3. 设计原则",
        "",
        "### 3.1 保持产品边界稳定",
        "- 待补充：说明哪些东西必须保留为正式真相，哪些只能做投影或辅助面。",
        "",
        "### 3.2 机器复杂度默认内收",
        "- 待补充：优先把复杂度放在系统内部，不把治理成本长期转嫁给人类操作。",
        "",
    ]
    if family == "runtime_control_plane":
        lines.extend(
            [
                "### 3.3 Projection 必须确定性且可解释",
                "- 待补充：明确 normalize / preflight / write 的链路与回退策略。",
                "",
            ]
        )
    elif family == "tooling_surface":
        lines.extend(
            [
                "### 3.3 文档承诺必须有可达入口",
                "- 待补充：进入版本包叙事的 toolkit / skill / command 必须保持宿主可达。",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "### 3.3 最小闭环优先",
                "- 待补充：优先交付能被真实项目验证的最小闭环，而不是铺大面。",
                "",
            ]
        )
    return lines


def _scope_lines(family: str) -> list[str]:
    in_scope = [
        "- 待补充：当前版本必须交付的最小正确能力。",
        "- 待补充：需要被纳入真实验收的关键路径。",
    ]
    out_scope = [
        "- 待补充：不在当前版本承担的扩展项。",
        "- 待补充：应继续留在兼容层或后续版本处理的事项。",
    ]
    if family == "tooling_surface":
        in_scope.insert(0, "- 待补充：命令面、skill 暴露、模板骨架与文档的一致性修复。")
    elif family == "runtime_control_plane":
        in_scope.insert(0, "- 待补充：project/run/status/projection 的最小管理与观察闭环。")
    return [
        "## 4. 范围",
        "",
        "### In scope",
        *in_scope,
        "",
        "### Out of scope",
        *out_scope,
        "",
    ]


def _functional_requirement_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 5. 功能需求",
            "",
            "### FR-001 真实项目输入必须可被注册 / 投影",
            "- 待补充：说明项目注册、workspace 边界和 runtime 来源。",
            "",
            "### FR-002 Projection 写入前必须预校验",
            "- 待补充：说明 truth snapshot、preflight、drift check 与失败语义。",
            "",
            "### FR-003 人类看板必须优先呈现生命周期进度",
            "- 待补充：说明 overview/detail/runtime drilldown 的展示优先级。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 5. 功能需求",
            "",
            "### FR-001 `prd create` 必须生成结构化骨架",
            "- 待补充：说明版本感知、场景感知与 Beacon 风格章节要求。",
            "",
            "### FR-002 已承诺 toolkit 必须有宿主可达入口",
            "- 待补充：说明 skill surface、命令路由和 optional 定位。",
            "",
            "### FR-003 文档与 skill surface 必须保持一致",
            "- 待补充：说明如何避免再次出现承诺/入口漂移。",
            "",
        ]
    return [
        "## 5. 功能需求",
        "",
        "### FR-001 主路径能力",
        "- 待补充：定义当前版本最关键的功能闭环。",
        "",
        "### FR-002 稳定性 / 恢复能力",
        "- 待补充：说明异常、断点恢复、回退和继续执行要求。",
        "",
        "### FR-003 可观测与验收面",
        "- 待补充：说明人类如何确认当前能力真的交付完成。",
        "",
    ]


def _data_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 6. 数据 / 状态 / 集成",
            "",
            "### 6.1 Truth 来源",
            "- 待补充：docs/beacon、.beacon、git/worktree、session 引用等来源。",
            "",
            "### 6.2 Projection Envelope",
            "- 待补充：统一字段、确定性生成规则、source priority 与回退状态。",
            "",
            "### 6.3 外部集成",
            "- 待补充：SQLite、PocketBase、备份与恢复链路。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 6. 数据 / 状态 / 集成",
            "",
            "### 6.1 模板输入",
            "- 待补充：feature、version、existing PRDs、memory context 等输入项。",
            "",
            "### 6.2 输出物",
            "- 待补充：PRD 骨架、skill surface、测试覆盖与文档更新。",
            "",
            "### 6.3 演进接口",
            "- 待补充：后续如何继续增加模板或 toolkit，而不重写主命令。",
            "",
        ]
    return [
        "## 6. 数据 / 状态 / 集成",
        "",
        "### 6.1 输入",
        "- 待补充：当前能力依赖的主要输入与上下文。",
        "",
        "### 6.2 输出",
        "- 待补充：当前能力最终产出的文档、状态或接口。",
        "",
        "### 6.3 集成点",
        "- 待补充：外部系统、CLI surface、脚本或数据流。",
        "",
    ]


def _risk_lines() -> list[str]:
    return [
        "## 7. 风险与缓解",
        "",
        "| 风险 | 影响 | 缓解 |",
        "|------|------|------|",
        "| 待补充 | 中 | 待补充 |",
        "",
    ]


def _acceptance_lines(family: str) -> list[str]:
    if family == "runtime_control_plane":
        return [
            "## 8. 验收标准",
            "",
            "### AC-001 真实项目态可被正确投影",
            "- 待补充：至少列出需要通过的真实项目与展示语义。",
            "",
            "### AC-002 Projection 多写不漂移",
            "- 待补充：同一 truth snapshot 写入结果必须稳定可解释。",
            "",
            "### AC-003 缺失投影层时仍可继续",
            "- 待补充：明确断库、恢复、重新开始的验收口径。",
            "",
        ]
    if family == "tooling_surface":
        return [
            "## 8. 验收标准",
            "",
            "### AC-001 `prd create` 不再输出 generic 模板",
            "- 待补充：新 PRD 必须直接包含 Beacon 风格结构化章节。",
            "",
            "### AC-002 生成器能区分主 PRD / 并行 PRD",
            "- 待补充：说明 track 判定和骨架差异的验收方式。",
            "",
            "### AC-003 toolkit skill 在宿主面可发现",
            "- 待补充：说明 host-visible skill、optional 定位和回归检查。",
            "",
        ]
    return [
        "## 8. 验收标准",
        "",
        "### AC-001 主路径通过",
        "- 待补充：说明用户/项目如何确认主路径已闭环。",
        "",
        "### AC-002 异常路径可恢复",
        "- 待补充：说明关键异常或中断下的恢复口径。",
        "",
        "### AC-003 文档与实现一致",
        "- 待补充：说明如何验证 requirement 与实际交付没有漂移。",
        "",
    ]


def _metric_lines() -> list[str]:
    return [
        "## 9. 成功指标",
        "",
        "- 待补充：1 个能反映真实闭环的主指标。",
        "- 待补充：1 个能反映稳定性/效率改善的辅助指标。",
        "",
    ]


def _relationship_lines(track: str, existing_prds: list[str]) -> list[str]:
    if track == "parallel":
        anchor = f"`{existing_prds[0]}`" if existing_prds else "`<main-prd>`"
        return [
            "## 10. 与主 PRD 的关系",
            "",
            f"- 主线锚点：{anchor}",
            "- 待补充：说明本并行 PRD 补强哪一段主线能力。",
            "- 待补充：说明哪些内容回写主 PRD，哪些保持独立冻结。",
            "",
        ]
    return [
        "## 10. 依赖与开放问题",
        "",
        "- 待补充：当前主线依赖的外部条件、真实项目输入或待确认问题。",
        "- 待补充：需要后续并行 PRD 单独冻结的切面。",
        "",
    ]


def _render_prd(
    feature: str,
    *,
    version: str,
    memory_context_path: str,
    track: str,
    family: str,
    label: str,
    existing_prds: list[str],
    slug: str,
) -> str:
    # v1.4.12+: use fixed English template with mermaid Outline
    from beacon.utils.versioning import normalize_version
    _normalized = normalize_version(version) or version
    try:
        _parts = _normalized.lstrip("v").split(".")
        if (int(_parts[0]), int(_parts[1]), int(_parts[2])) >= (1, 4, 12):
            return _render_prd_template(feature_slug=slug, version=version, lang="en")
    except Exception:
        pass
    sections: list[str] = [
        f"# PRD：{feature}",
        "",
        f"**Feature**: `{slug}`  ",
        f"**Version**: `{version}`  ",
        f"**Date**: `{datetime.now().strftime('%Y-%m-%d')}`  ",
        f"**Status**: `draft skeleton`  ",
        f"**Track**: `{track}`  ",
        f"**Scenario**: `{family}`  ",
        f"**Template**: `{label}`  ",
        "",
        _context_block(version, existing_prds=existing_prds),
    ]

    sections.extend(_main_problem_lines(family) if track == "main" else _parallel_problem_lines(family, existing_prds))
    sections.extend(_goal_lines(family))
    sections.extend(_principle_lines(family))
    sections.extend(_scope_lines(family))
    sections.extend(_functional_requirement_lines(family))
    sections.extend(_data_lines(family))
    sections.extend(_risk_lines())
    sections.extend(_acceptance_lines(family))
    sections.extend(_metric_lines())
    sections.extend(_relationship_lines(track, existing_prds))
    sections.extend(
        [
            "---",
            "",
            f"**Created**: {datetime.now().strftime('%Y-%m-%d')}  ",
            f"**Version**: {version}  ",
            f"**Status**: draft skeleton  ",
            f"**Memory Context**: {memory_context_path or 'N/A'}",
            "",
        ]
    )
    return "\n".join(sections)


@app.command()
def create(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    semantic: bool = typer.Option(False, "--semantic", help="Legacy compatibility flag for semantic compilation."),
    track: Optional[str] = typer.Option(None, "--track", help="Legacy compatibility override for track."),
    family: Optional[str] = typer.Option(None, "--family", help="Legacy compatibility override for family."),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: auto/llm/rule"),
    model: str = typer.Option("beacon-prd-compiler", "--model", help="Compiler model label for evidence"),
    include_diagrams: list[str] = typer.Option(None, "--include-diagrams", help="Repeatable diagram truth types"),
    state_axis: list[str] = typer.Option(None, "--state-axis", help="Repeatable explicit state axis"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Create a PRD"""
    project_root = Path(project) if project else Path.cwd()
    if version == "auto" and (project_root / ".beacon" / "prd").exists():
        typer.echo("version is required for legacy PRD surface compatibility.", err=True)
        raise typer.Exit(2)
    try:
        resolved_version = resolve_operational_docs_version(
            project_root,
            version,
            command_name="prd create",
        )
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(2)

    memory_context_path = os.environ.get("BEACON_STAGE_CONTEXT_PATH", "").strip()
    requested_diagrams = normalize_diagram_types(list(include_diagrams or []))
    requested_state_axes = normalize_state_axes(list(state_axis or []))
    slug = _slugify(feature)
    existing_prds = _existing_prd_names(project_root, resolved_version, exclude_slug=slug)
    template = _classify_prd(feature, existing_prds=existing_prds)
    if track:
        if track not in {"main", "parallel"}:
            typer.echo("Invalid --track. Use main/parallel.", err=True)
            raise typer.Exit(2)
        template["track"] = track
    if family:
        template["family"] = family
        template["label"] = family
    try:
        requested_mode = normalize_requested_mode(mode)
    except ValueError:
        typer.echo("Invalid --mode. Use auto/llm/rule.", err=True)
        raise typer.Exit(2)
    if semantic and requested_mode == "auto":
        requested_mode = "llm"
    capability_snapshot = build_semantic_capability_snapshot(
        "prd",
        disable_env="BEACON_PRD_DISABLE_LLM",
    )

    # Wire host bridge transport before capability snapshot (v1.4.11 fix).
    # Without this, host_semantic_ready is always false when no LLM API key is set,
    # because ensure_default_host_bridge_env was never called.
    from beacon.utils.semantic_runtime import ensure_default_host_bridge_env as _ensure_bridge
    _ensure_bridge("prd", host_runtime=capability_snapshot.get("host_runtime"))
    capability_snapshot = build_semantic_capability_snapshot(
        "prd",
        disable_env="BEACON_PRD_DISABLE_LLM",
    )

    # Fix: legacy_line_force_rule must use Beacon's own version, not the project
    # version (resolved_version). Using resolved_version caused every project with
    # docs/beacon/<version> < 1.3.5 to be forced into rule mode with
    # fallback_reason "legacy_line_default_rule", regardless of host runtime.
    from beacon import __version__ as _beacon_version
    legacy_line_force_rule = requested_mode == "auto" and _semver_tuple(_beacon_version) < (1, 3, 5)
    fallback_reason = ""
    effective_mode = requested_mode
    generator_mode = requested_mode
    llm_disabled = bool(capability_snapshot.get("llm_disabled"))

    if requested_mode == "rule" or legacy_line_force_rule:
        effective_mode = "rule"
        generator_mode = "rule"
        if legacy_line_force_rule:
            fallback_reason = "legacy_line_default_rule"
        md_content = _render_prd(
            feature,
            version=resolved_version,
            memory_context_path=memory_context_path,
            track=template["track"],
            family=template["family"],
            label=template["label"],
            existing_prds=existing_prds,
            slug=slug,
        )
        contract = _validate_contract(md_content, require_no_placeholders=False)
    else:
        if llm_disabled:
            if requested_mode == "llm":
                typer.echo("LLM compile disabled by BEACON_PRD_DISABLE_LLM.", err=True)
                raise typer.Exit(2)
            effective_mode = "rule"
            generator_mode = "rule"
            fallback_reason = "llm_disabled"
            md_content = _render_prd(
                feature,
                version=resolved_version,
                memory_context_path=memory_context_path,
                track=template["track"],
                family=template["family"],
                label=template["label"],
                existing_prds=existing_prds,
                slug=slug,
            )
            contract = _validate_contract(md_content, require_no_placeholders=False)
        else:
            host_markdown = ""
            if bool(capability_snapshot.get("host_semantic_ready")):
                host_markdown = _extract_host_prd_markdown_with_bridge(
                    _build_prd_host_bridge_request(
                        feature=feature,
                        version=resolved_version,
                        track=template["track"],
                        family=template["family"],
                        existing_prds=existing_prds,
                        slug=slug,
                    )
                )
                if host_markdown:
                    effective_mode = "host"
                else:
                    fallback_reason = "host_compile_failed"
            if host_markdown:
                md_content = host_markdown
            else:
                effective_mode = "llm"
                md_content = _render_semantic_prd(
                    feature,
                    version=resolved_version,
                    track=template["track"],
                    family=template["family"],
                    existing_prds=existing_prds,
                    slug=slug,
                )
            contract = _validate_contract(md_content, require_no_placeholders=True)
            generator_mode = effective_mode
            if not bool(contract.get("ok")):
                failed_mode = effective_mode
                if requested_mode == "llm":
                    typer.echo("LLM compile output failed contract validation.", err=True)
                    raise typer.Exit(2)
                effective_mode = "rule"
                generator_mode = "rule"
                fallback_reason = (
                    "host_contract_validation_failed"
                    if failed_mode == "host"
                    else "llm_contract_validation_failed"
                )
                md_content = _render_prd(
                    feature,
                    version=resolved_version,
                    memory_context_path=memory_context_path,
                    track=template["track"],
                    family=template["family"],
                    label=template["label"],
                    existing_prds=existing_prds,
                    slug=slug,
                )
                contract = _validate_contract(md_content, require_no_placeholders=False)

    diagram_truth_section = render_diagram_truth_section(
        include_diagrams=requested_diagrams,
        state_axes=requested_state_axes,
    )
    if diagram_truth_section and "## 11. Diagram Truth Layer" not in md_content:
        md_content = md_content.rstrip() + "\n" + diagram_truth_section
        contract = _validate_contract(md_content, require_no_placeholders=effective_mode in {"host", "llm"})

    if output:
        output_path = Path(output)
    else:
        output_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
    machine_dir = _machine_prd_dir(project_root, resolved_version)
    compile_path = machine_dir / f"{slug}.compile.json"
    canonical_path = machine_dir / f"{slug}.canonical.json"
    source_refs = _source_refs(project_root, resolved_version, existing_prds)
    project_metadata_context = _project_metadata_context(project_root, version=resolved_version)
    try:
        projection = _persist_prd_projection(
            project_root=project_root,
            output_path=output_path,
            compile_path=compile_path,
            canonical_path=canonical_path,
            feature=feature,
            slug=slug,
            version=resolved_version,
            template=template,
            requested_mode=requested_mode,
            effective_mode=effective_mode,
            generator_mode=generator_mode,
            fallback_reason=fallback_reason,
            capability_snapshot=capability_snapshot,
            model=model,
            requested_diagrams=requested_diagrams,
            requested_state_axes=requested_state_axes,
            md_content=md_content,
            contract=contract,
            source_refs=source_refs,
            project_metadata_context=project_metadata_context,
        )
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"PRD transaction failed: {exc}", err=True)
        raise typer.Exit(2)
    if json_output:
        payload = _with_prd_surface(
            {
                "status": "ok",
                "feature": feature,
                "feature_slug": slug,
                "version": resolved_version,
                "effective_mode": effective_mode,
                "generator_mode": generator_mode,
                "requested_mode": requested_mode,
                "fallback_reason": fallback_reason,
                "capability_snapshot": capability_snapshot,
                "contract_ok": bool(contract.get("ok", False)),
                "output_path": str(output_path),
                "compile_path": str(projection["compile_path"]),
                "canonical_path": str(projection["canonical_path"]),
                "transaction_path": str(projection["transaction_path"]),
                "latest_transaction_path": str(projection["latest_transaction_path"]),
            },
            recommended_command=f'beacon prd create "{feature}" --project-root {project_root} --version {resolved_version}',
            blocked=False,
        )
        typer.echo(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    typer.echo(f"✓ PRD created: {output_path}")


@app.command("reconcile")
def reconcile_prd(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON payload"),
):
    """Re-project the current human PRD markdown into machine mirrors."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    slug = _resolve_existing_prd_slug(project_root, version=resolved_version, feature=feature)
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
    if not prd_path.exists():
        typer.echo(f"PRD not found: {prd_path}", err=True)
        raise typer.Exit(2)
    md_content = prd_path.read_text(encoding="utf-8")
    contract = _validate_contract(md_content, require_no_placeholders=False)
    if not bool(contract.get("ok")):
        payload = _with_prd_surface(
            {
                "status": "blocked",
                "reason_code": "contract_invalid",
                "feature": feature,
                "version": resolved_version,
                "missing_headings": contract.get("missing_headings", []),
                "semantic_hits": contract.get("semantic_hits", {}),
            },
            reason_code="contract_invalid",
            recommended_command=f'beacon prd reconcile "{feature}" --project-root {project_root} --version {resolved_version} --json',
            blocked=True,
        )
        typer.echo(
            json.dumps(payload, ensure_ascii=False, indent=2)
            if json_output
            else f"Contract invalid: missing_headings={contract.get('missing_headings', [])} semantic_hits={contract.get('semantic_hits', {})}",
            err=True,
        )
        raise typer.Exit(2)

    machine_dir = _machine_prd_dir(project_root, resolved_version)
    canonical_path = machine_dir / f"{slug}.canonical.json"
    existing_prds = _existing_prd_names(project_root, resolved_version, exclude_slug=slug)
    template = _classify_prd(feature, existing_prds=existing_prds)
    requested_mode = "rule"
    effective_mode = "rule"
    generator_mode = "rule"
    fallback_reason = ""
    capability_snapshot = build_semantic_capability_snapshot("prd", disable_env="BEACON_PRD_DISABLE_LLM")
    model = "beacon-prd-compiler"
    requested_diagrams: list[str] = []
    requested_state_axes: list[str] = []
    feature_display = feature
    existing_canonical = _read_json_dict(canonical_path)
    if existing_canonical:
        feature_display = str(existing_canonical.get("feature") or feature).strip() or feature
        template = {
            "track": str(existing_canonical.get("track") or template["track"]),
            "family": str(existing_canonical.get("family") or template["family"]),
            "label": str(existing_canonical.get("label") or template["label"]),
        }
        requested_mode = str(existing_canonical.get("requested_mode") or requested_mode)
        effective_mode = str(existing_canonical.get("effective_mode") or effective_mode)
        generator_mode = str(existing_canonical.get("generator_mode") or generator_mode)
        fallback_reason = str(existing_canonical.get("fallback_reason") or fallback_reason)
        capability_snapshot = existing_canonical.get("capability_snapshot") if isinstance(existing_canonical.get("capability_snapshot"), dict) else capability_snapshot
        model = str(existing_canonical.get("model") or model)
        diagram_truth_request = existing_canonical.get("diagram_truth_request") if isinstance(existing_canonical.get("diagram_truth_request"), dict) else {}
        requested_diagrams = normalize_diagram_types(list(diagram_truth_request.get("diagram_types") or []))
        requested_state_axes = normalize_state_axes(list(diagram_truth_request.get("state_axes") or []))

    output_path = prd_path
    compile_path = machine_dir / f"{slug}.compile.json"
    source_refs = _source_refs(project_root, resolved_version, existing_prds)
    project_metadata_context = _project_metadata_context(project_root, version=resolved_version)
    try:
        projection = _persist_prd_projection(
            project_root=project_root,
            output_path=output_path,
            compile_path=compile_path,
            canonical_path=canonical_path,
            feature=feature_display,
            slug=slug,
            version=resolved_version,
            template=template,
            requested_mode=requested_mode,
            effective_mode=effective_mode,
            generator_mode=generator_mode,
            fallback_reason=fallback_reason,
            capability_snapshot=capability_snapshot,
            model=model,
            requested_diagrams=requested_diagrams,
            requested_state_axes=requested_state_axes,
            md_content=md_content,
            contract=contract,
            source_refs=source_refs,
            project_metadata_context=project_metadata_context,
        )
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"PRD reconcile failed: {exc}", err=True)
        raise typer.Exit(2)

    if json_output:
        payload = _with_prd_surface(
            {
                "status": "ok",
                "feature": feature_display,
                "feature_slug": slug,
                "version": resolved_version,
                "output_path": str(output_path),
                "compile_path": str(projection["compile_path"]),
                "canonical_path": str(projection["canonical_path"]),
                "transaction_path": str(projection["transaction_path"]),
                "latest_transaction_path": str(projection["latest_transaction_path"]),
            },
            recommended_command=f'beacon prd reconcile "{feature_display}" --project-root {project_root} --version {resolved_version}',
            blocked=False,
        )
        typer.echo(
            json.dumps(payload, ensure_ascii=False, indent=2)
        )
        return
    typer.echo(f"✓ PRD reconciled: {output_path}")


@app.command("validate")
def validate_prd(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Validate PRD markdown against the public PRD contract."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    slug = _resolve_existing_prd_slug(project_root, version=resolved_version, feature=feature)
    prd_path = project_root / "docs" / "beacon" / resolved_version / "prd" / f"{slug}.md"
    if not prd_path.exists():
        typer.echo(f"PRD not found: {prd_path}", err=True)
        raise typer.Exit(2)
    contract = _validate_contract(prd_path.read_text(encoding="utf-8"), require_no_placeholders=False)
    if not bool(contract.get("ok")):
        typer.echo(f"Contract invalid: {contract.get('issues', [])}", err=True)
        raise typer.Exit(2)
    typer.echo(f"Contract valid: {prd_path}")


@app.command("audit")
def audit_prd(
    feature: str = typer.Argument(..., help="Feature name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """Audit PRD markdown against all machine mirrors to detect drift."""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    payload = _build_prd_audit_payload(project_root, version=resolved_version, feature=feature)
    if not bool(payload.get("exists")):
        typer.echo(f"PRD not found: {payload.get('prd_path')}", err=True)
        raise typer.Exit(2)
    if str(payload.get("status")) == "contract_invalid":
        contract = payload.get("contract") if isinstance(payload.get("contract"), dict) else {}
        typer.echo(
            f"Contract invalid: missing_headings={contract.get('missing_headings', [])} semantic_hits={contract.get('semantic_hits', {})}",
            err=True,
        )
        raise typer.Exit(2)
    if str(payload.get("status")) != "pass":
        typer.echo(f"Drift detected: {', '.join(str(item) for item in payload.get('failure_codes', []))}", err=True)
        raise typer.Exit(2)
    typer.echo("No drift detected")


@app.command("list")
def list_prds(
    project: Optional[str] = typer.Option(None, "--project", "-p", "--project-root", help="Project root"),
    version: str = typer.Option("auto", "--version", "-v", help="Version (auto=largest docs semver)"),
):
    """List all PRDs"""
    project_root = Path(project) if project else Path.cwd()
    resolved_version = resolve_target_version(project_root, version)
    roots = [project_root / "docs" / "beacon" / resolved_version / "prd"]
    prds = []
    for prds_dir in roots:
        if prds_dir.exists():
            prds.extend(prds_dir.glob("*.md"))
    if not prds:
        typer.echo("No PRDs found")
        return
    unique = {p.name: p for p in prds}
    typer.echo(f"PRDs ({len(unique)} found):")
    for prd in sorted(unique.values(), key=lambda p: p.name):
        typer.echo(f"  - {prd.name}")


if __name__ == "__main__":
    app()
