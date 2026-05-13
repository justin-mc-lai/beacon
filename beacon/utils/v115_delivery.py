"""Helpers for Beacon v1.1.5 human/machine layering and eval-lab skeleton."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import (
    execution_file_candidates,
    human_execution_dir,
    machine_execution_dir,
    machine_qa_dir,
    qa_docs_dir,
    uses_machine_surface,
)
from beacon.utils.evidence_manifest import merge_manifest_entries
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.versioning import resolve_target_version


_EXECUTION_MACHINE_FILES = (
    "config.json",
    "source.json",
    "git-alignment.json",
    "change-impact.json",
    "delivery-manifest.json",
    "terminal.json",
)

_QA_MATRIX_SUFFIXES = (".ac-test-matrix.json", ".qa9-matrix.json")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _state_sort_key(path: Path, payload: dict[str, Any]) -> tuple[str, str, str, str, str, str, int, str]:
    return (
        str(payload.get("frozen_at") or ""),
        str(payload.get("accepted_at") or ""),
        str(payload.get("completed_at") or ""),
        str(payload.get("updated_at") or ""),
        str(payload.get("created_at") or ""),
        str(payload.get("written_at") or ""),
        path.stat().st_mtime_ns if path.exists() else 0,
        path.name,
    )


def _latest_version_feature(project_root: Path, *, version: str) -> str:
    machine_exec = machine_execution_dir(project_root, version)
    if machine_exec.exists():
        candidates: list[tuple[Path, dict[str, Any]]] = []
        for path in machine_exec.glob("*.revision.json"):
            payload = _read_json(path)
            if str(payload.get("feature") or "").strip():
                candidates.append((path, payload))
        for path, payload in sorted(candidates, key=lambda item: _state_sort_key(item[0], item[1]), reverse=True):
            feature = str(payload.get("feature") or "").strip()
            if feature:
                return feature

    user_story_dir = project_root / "docs" / "beacon" / version / "user-story"
    if user_story_dir.exists():
        for path in sorted(user_story_dir.glob("*.md"), key=lambda item: (item.stat().st_mtime_ns, item.name), reverse=True):
            if path.name == "index.md":
                continue
            feature = path.stem.strip()
            if feature:
                return feature
    return ""


def _synthetic_run_id(*, version: str) -> str:
    stamp = (
        now_iso()
        .replace("-", "")
        .replace(":", "")
        .replace(".", "")
        .replace("+", "Z")
    )
    return f"repair-{version}-{stamp}"


def _preferred_governance_run_id(project_root: Path, *, version: str, feature: str) -> str:
    auto_test_payload = _read_json(project_root / ".beacon" / "auto-test-status.json")
    auto_test_run_id = str(auto_test_payload.get("run_id") or "").strip()
    auto_test_version = str(auto_test_payload.get("version") or "").strip()
    if auto_test_run_id and auto_test_version == version:
        return auto_test_run_id

    source_payload = next(
        (_read_json(path) for path in execution_file_candidates(project_root, version, "source.json") if path.exists()),
        {},
    )
    source_feature = str(source_payload.get("feature") or "").strip()
    source_run_id = str(source_payload.get("run_id") or "").strip()
    if source_feature == feature and source_run_id:
        return source_run_id

    return _synthetic_run_id(version=version)


def _synthesize_execution_governance(
    project_root: Path,
    *,
    version: str,
    apply: bool,
) -> list[dict[str, str]]:
    feature = _latest_version_feature(project_root, version=version)
    if not feature:
        return [
            {
                "path": f"docs/beacon/{version}/execution",
                "action": "skipped",
                "reason": "feature_missing_for_governance_synthesis",
            }
        ]

    required_files = (
        "boundaries.md",
        "config.json",
        "source.json",
        "git-alignment.json",
        "change-impact.json",
        "delivery-manifest.json",
        "terminal.json",
    )
    missing = [
        filename
        for filename in required_files
        if not any(path.exists() for path in execution_file_candidates(project_root, version, filename))
    ]
    source_payload = next(
        (_read_json(path) for path in execution_file_candidates(project_root, version, "source.json") if path.exists()),
        {},
    )
    source_feature = str(source_payload.get("feature") or "").strip()
    source_run_id = str(source_payload.get("run_id") or "").strip()
    run_id = _preferred_governance_run_id(project_root, version=version, feature=feature)
    stale_feature = bool(source_feature and source_feature != feature)
    stale_run_id = bool(source_feature == feature and source_run_id and source_run_id != run_id)
    if not missing and not stale_feature and not stale_run_id:
        return []
    planned_paths = [
        str((human_execution_dir(project_root, version) / "boundaries.md").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "config.json").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "source.json").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "git-alignment.json").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "change-impact.json").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "delivery-manifest.json").relative_to(project_root)),
        str((machine_execution_dir(project_root, version) / "terminal.json").relative_to(project_root)),
    ]

    if apply:
        from beacon.commands.workflow import (
            _sync_terminal_manifest,
            _write_execution_governance_artifacts,
            _write_workflow_terminal_artifacts,
        )

        _write_execution_governance_artifacts(
            project_root=project_root,
            version=version,
            run_id=run_id,
            feature=feature,
            workflow_status="completed",
        )
        _write_workflow_terminal_artifacts(
            project_root=project_root,
            version=version,
            run_id=run_id,
            feature=feature,
            workflow_status="completed",
            reason="doctor_repair_package",
        )
        _sync_terminal_manifest(project_root, version=version, run_id=run_id)

    action = (
        "rewritten"
        if apply and (stale_feature or stale_run_id)
        else "planned_rewrite"
        if (stale_feature or stale_run_id)
        else "synthesized"
        if apply
        else "planned"
    )
    return [
        {
            "path": path,
            "action": action,
            "source": f"workflow_governance:{feature}",
        }
        for path in planned_paths
    ]


def refresh_evidence_manifest(
    project_root: Path,
    *,
    refs: list[str],
    version: str,
) -> None:
    manifest_path = project_root / ".beacon" / "evidence-manifest.json"
    payload: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                payload = loaded
        except Exception:  # noqa: BLE001
            payload = {}
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    manifest_rel = str(manifest_path.relative_to(project_root))
    output_payload: dict[str, Any] = {
        "schema_version": "1.0",
        "entries": merge_manifest_entries(
            project_root,
            existing_entries=entries,
            evidence_refs=refs,
            exclude_paths={manifest_rel},
        ),
        "updated_at": now_iso(),
        "version": version,
    }
    run_id = str(payload.get("run_id", "") or "").strip()
    if run_id:
        output_payload["run_id"] = run_id
    write_json(manifest_path, output_payload)


def build_first_principles_contract(project_root: Path, *, version: str) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    machine_enabled = uses_machine_surface(resolved_version)
    docs_root = f"docs/beacon/{resolved_version}"
    machine_root = f"{docs_root}/.machine"
    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "enabled": machine_enabled,
        "reasoning_order": [
            "human_needs",
            "machine_needs",
            "beacon_responsibility",
        ],
        "reading_order": [
            f"{docs_root}/SUMMARY.md",
            f"{docs_root}/execution/index.md",
            machine_root if machine_enabled else docs_root,
            ".beacon/memory/",
        ],
        "surface_roles": {
            "human_primary": [
                f"{docs_root}/SUMMARY.md",
                f"{docs_root}/release/",
                f"{docs_root}/execution/index.md",
                f"{docs_root}/qa/test-cases/index.md",
            ],
            "machine_secondary": [
                f"{machine_root}/execution/" if machine_enabled else f"{docs_root}/execution/",
                f"{machine_root}/qa/" if machine_enabled else f"{docs_root}/qa/test-cases/",
            ],
            "runtime_internal": [
                ".beacon/memory/",
                ".beacon/state/",
                ".beacon/runs/",
                ".beacon/implement/",
            ],
        },
        "output_policy": {
            "progressive_disclosure": True,
            "human_default": "conclusion_then_minimal_explanation",
            "machine_details_on_demand": True,
        },
        "clarification_gate": {
            "required_when": [
                "goal_unclear",
                "motivation_unclear",
                "boundary_unclear",
                "success_criteria_unclear",
            ],
            "default_action": "clarify_before_execute",
        },
        "disallowed_defaults": [
            "compatibility_first",
            "fallback_first",
            "overdesign",
            "implicit_goal_assumption",
        ],
        "memory_contract": {
            "layers": [
                "store",
                "workflow_lifecycle",
                "feedback_assimilation",
                "consumption_projection",
            ],
            "human_default": "consumption_projection",
            "machine_default": "store_and_lifecycle",
        },
        "doctor_role": {
            "mode": "destructive_repairer",
            "not_a": "compatibility_layer",
        },
    }


def ensure_human_primary_indexes(project_root: Path, *, version: str, apply: bool = True) -> list[dict[str, str]]:
    resolved_version = resolve_target_version(project_root, version)
    if not uses_machine_surface(resolved_version):
        return []

    actions: list[dict[str, str]] = []
    docs_root = project_root / "docs" / "beacon" / resolved_version
    execution_index = docs_root / "execution" / "index.md"
    qa_index = docs_root / "qa" / "test-cases" / "index.md"
    qa_root = qa_docs_dir(project_root, resolved_version)

    execution_content = "\n".join(
        [
            f"# Execution Index ({resolved_version})",
            "",
            "## Human Primary Surface",
            "",
            "- `boundaries.md`",
            "- Markdown execution notes and release-facing guidance",
            "",
            "## Machine Secondary Surface",
            "",
            f"- `docs/beacon/{resolved_version}/.machine/execution/`",
            "",
            "## Notes",
            "",
            "- `execution/` stays Markdown-first for humans.",
            "- `.beacon/` remains runtime internal state only.",
            "",
        ]
    )
    qa_files = sorted(
        p.name for p in qa_root.glob("*.md") if p.is_file() and p.name != "index.md"
    )
    qa_content = "\n".join(
        [
            f"# QA Test Case Index ({resolved_version})",
            "",
            "## Human Primary Surface",
            "",
            *[f"- `{name}`" for name in qa_files],
            "",
            "## Machine Secondary Surface",
            "",
            f"- `docs/beacon/{resolved_version}/.machine/qa/`",
            "",
        ]
    )

    changed = (not execution_index.exists()) or execution_index.read_text(encoding="utf-8") != execution_content
    if apply and changed:
        execution_index.parent.mkdir(parents=True, exist_ok=True)
        execution_index.write_text(execution_content, encoding="utf-8")
    actions.append(
        {
            "path": str(execution_index.relative_to(project_root)),
            "action": "written" if changed and apply else ("planned" if changed else "unchanged"),
        }
    )

    if not qa_root.exists() and not qa_files:
        return actions

    changed = (not qa_index.exists()) or qa_index.read_text(encoding="utf-8") != qa_content
    if apply and changed:
        qa_index.parent.mkdir(parents=True, exist_ok=True)
        qa_index.write_text(qa_content, encoding="utf-8")
    actions.append(
        {
            "path": str(qa_index.relative_to(project_root)),
            "action": "written" if changed and apply else ("planned" if changed else "unchanged"),
        }
    )
    return actions


def ensure_eval_lab_skeleton(project_root: Path, *, apply: bool = True) -> list[dict[str, str]]:
    eval_root = project_root / ".beacon" / "state" / "eval-lab"
    skeleton: dict[Path, str | None] = {
        eval_root / "experiments": None,
        eval_root / "scores": None,
        eval_root / "drift-audit": None,
        eval_root / "benchmark-surface.json": json.dumps(
            {
                "schema_version": "1.0",
                "benchmarks": [
                    "delivery_closure",
                    "human_machine_layering",
                    "drift_audit",
                    "confidence_audit",
                ],
                "generated_at": now_iso(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        eval_root / "editable-surface.json": json.dumps(
            {
                "schema_version": "1.0",
                "editable_surfaces": [
                    "prompt_policy_layer",
                    "rule_policy_layer",
                    "drift_extractor_layer",
                ],
                "generated_at": now_iso(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        eval_root / "policy.json": json.dumps(
            {
                "schema_version": "1.0",
                "hard_gates": [
                    "verify_materials",
                    "verify_delivery",
                    "status_report_gate_integrity",
                    "machine_artifact_readability",
                    "human_primary_surface_integrity",
                ],
                "soft_scores": [
                    "human_cognitive_load",
                    "drift_detection",
                    "confidence_calibration",
                    "doctor_repair_success",
                    "cost_complexity",
                ],
                "generated_at": now_iso(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        eval_root / "keep-discard-log.jsonl": "",
    }

    actions: list[dict[str, str]] = []
    for path, content in skeleton.items():
        changed = not path.exists()
        if apply:
            if content is None:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if changed:
                    path.write_text(content, encoding="utf-8")
        actions.append(
            {
                "path": str(path.relative_to(project_root)),
                "action": "written" if changed and apply else ("planned" if changed else "unchanged"),
            }
        )
    return actions


def repair_v115_delivery_package(
    project_root: Path,
    *,
    version: str,
    apply: bool = True,
) -> dict[str, Any]:
    resolved_version = resolve_target_version(project_root, version)
    actions: list[dict[str, str]] = []
    if not uses_machine_surface(resolved_version):
        return {
            "schema_version": "1.0",
            "version": resolved_version,
            "applied": apply,
            "migrated": [],
            "indexes": [],
            "eval_lab": [],
            "notes": ["machine surface not enabled for this version"],
        }

    human_exec = project_root / "docs" / "beacon" / resolved_version / "execution"
    machine_exec = machine_execution_dir(project_root, resolved_version)
    machine_qa = machine_qa_dir(project_root, resolved_version)
    human_qa = qa_docs_dir(project_root, resolved_version)

    migrated: list[str] = []
    execution_json_filenames = sorted({path.name for path in human_exec.glob("*.json")} | set(_EXECUTION_MACHINE_FILES))
    for filename in execution_json_filenames:
        src = human_exec / filename
        dst = machine_exec / filename
        if not src.exists():
            continue
        changed = (not dst.exists()) or src.read_bytes() != dst.read_bytes()
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        migrated.append(str(dst.relative_to(project_root)))
        actions.append(
            {
                "path": str(dst.relative_to(project_root)),
                "source": str(src.relative_to(project_root)),
                "action": "moved" if apply else "planned",
            }
        )
        if changed and not apply:
            continue

    for suffix in _QA_MATRIX_SUFFIXES:
        for src in sorted(human_qa.glob(f"*{suffix}")):
            dst = machine_qa / src.name
            if apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
            migrated.append(str(dst.relative_to(project_root)))
            actions.append(
                {
                    "path": str(dst.relative_to(project_root)),
                    "source": str(src.relative_to(project_root)),
                    "action": "moved" if apply else "planned",
                }
            )

    index_actions = ensure_human_primary_indexes(project_root, version=resolved_version, apply=apply)
    eval_actions = ensure_eval_lab_skeleton(project_root, apply=apply)
    governance_actions = _synthesize_execution_governance(project_root, version=resolved_version, apply=apply)
    actions.extend(index_actions)
    actions.extend(eval_actions)
    actions.extend(governance_actions)
    if apply:
        manifest_refs = sorted(
            {
                *migrated,
                *[item["path"] for item in index_actions if isinstance(item, dict) and str(item.get("path", "")).strip()],
                *[item["path"] for item in governance_actions if isinstance(item, dict) and str(item.get("path", "")).strip()],
            }
        )
        refresh_evidence_manifest(project_root, refs=manifest_refs, version=resolved_version)

    return {
        "schema_version": "1.0",
        "version": resolved_version,
        "applied": apply,
        "migrated": migrated,
        "indexes": index_actions,
        "eval_lab": eval_actions,
        "governance": governance_actions,
        "actions": actions,
        "notes": [
            "v1.1.5 treats .machine as machine secondary surface",
            "doctor is the authority for repairing old package layout into v1.1.5 structure",
        ],
    }
