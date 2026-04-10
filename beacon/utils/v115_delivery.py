"""Helpers for Beacon v1.1.5 human/machine layering and eval-lab skeleton."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import machine_execution_dir, machine_qa_dir, qa_docs_dir, uses_machine_surface
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
    by_path: dict[str, dict[str, Any]] = {
        ref_path: item
        for item in entries
        if isinstance(item, dict)
        and (ref_path := str(item.get("path", "")).strip())
        and ref_path != manifest_rel
        and (project_root / ref_path).exists()
        and (project_root / ref_path).is_file()
    }
    for ref in refs:
        ref_path = str(ref or "").strip()
        if not ref_path or ref_path == manifest_rel:
            continue
        full = project_root / ref_path
        if not full.exists() or not full.is_file():
            continue
        by_path[ref_path] = {
            "path": ref_path,
            "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            "updated_at": now_iso(),
        }
    output_payload: dict[str, Any] = {
        "schema_version": "1.0",
        "entries": list(by_path.values()),
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
        p.name for p in qa_docs_dir(project_root, resolved_version).glob("*.md") if p.is_file() and p.name != "index.md"
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

    for path, content in ((execution_index, execution_content), (qa_index, qa_content)):
        changed = (not path.exists()) or path.read_text(encoding="utf-8") != content
        if apply and changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        actions.append(
            {
                "path": str(path.relative_to(project_root)),
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
    actions.extend(index_actions)
    actions.extend(eval_actions)
    if apply:
        manifest_refs = sorted(
            {
                *migrated,
                *[item["path"] for item in index_actions if isinstance(item, dict) and str(item.get("path", "")).strip()],
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
        "actions": actions,
        "notes": [
            "v1.1.5 treats .machine as machine secondary surface",
            "doctor is the authority for repairing old package layout into v1.1.5 structure",
        ],
    }
