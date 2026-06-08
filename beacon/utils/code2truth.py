"""Code2Truth project intake helpers.

The intake surface reconstructs candidate truth from existing source evidence.
It never promotes candidate truth into package authority by itself.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.lighthouse import generate_lighthouse_artifact
from beacon.utils.runtime import now_iso, write_json
from beacon.utils.source_architecture import current_source_architecture_status
from beacon.utils.story_state import feature_slug
from beacon.utils.truth_map import resolve_truth_map, verify_truth_map
from beacon.utils.versioning import resolve_target_version

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".rb",
    ".php",
    ".sh",
    ".zsh",
    ".bash",
    ".sql",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
}
DOC_NAMES = {"README", "AGENTS", "SKILL", "PRODUCT", "DESIGN"}
PROVIDER_ARTIFACTS = (
    ".understand-anything/intermediate/scan-result.json",
    ".understand-anything/intermediate/import-map.json",
    ".understand-anything/intermediate/batches.json",
    ".understand-anything/intermediate/structure-result.json",
    ".understand-anything/knowledge-graph.json",
    ".understand-anything/graph-build-report.json",
    ".understand-anything/meta.json",
)


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _skip(path: Path) -> bool:
    ignored = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".beacon",
        ".omc",
        ".understand-anything",
    }
    return any(part in ignored for part in path.parts)


def _file_kind(path: Path) -> str:
    name = path.name
    stem = path.stem.upper()
    if name == "SKILL.md":
        return "skill"
    if stem in DOC_NAMES and path.suffix.lower() in {"", ".md"}:
        return "doc"
    if path.name.startswith("test_") or "/tests/" in path.as_posix() or path.name.endswith(".test.ts"):
        return "test"
    if path.suffix.lower() in SOURCE_EXTENSIONS:
        return "source"
    return "other"


def _looks_like_entrypoint(path: Path) -> bool:
    lowered = path.as_posix().lower()
    names = {"main.py", "app.py", "cli.py", "__main__.py", "index.ts", "index.js", "server.ts", "server.js", "skill.md"}
    return path.name.lower() in names or "commands/" in lowered or "bin/" in lowered or "scripts/" in lowered


def _collect_source_inventory(root: Path, *, max_files: int = 500) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    counts = {"source": 0, "doc": 0, "skill": 0, "test": 0, "other": 0}
    entry_points: list[str] = []
    skill_files: list[str] = []
    test_files: list[str] = []
    doc_files: list[str] = []

    for path in sorted(root.rglob("*")):
        if len(files) >= max_files:
            break
        if not path.is_file() or _skip(path):
            continue
        rel = _rel(root, path)
        kind = _file_kind(path)
        if kind == "other" and path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        counts[kind] = counts.get(kind, 0) + 1
        row = {"path": rel, "kind": kind, "entrypoint": _looks_like_entrypoint(path)}
        files.append(row)
        if row["entrypoint"]:
            entry_points.append(rel)
        if kind == "skill":
            skill_files.append(rel)
        elif kind == "test":
            test_files.append(rel)
        elif kind == "doc":
            doc_files.append(rel)

    return {
        "status": "collected",
        "root": str(root),
        "file_count": len(files),
        "counts": counts,
        "files": files,
        "entry_points": entry_points[:50],
        "skill_files": skill_files[:100],
        "test_files": test_files[:100],
        "doc_files": doc_files[:100],
        "truncated": len(files) >= max_files,
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _detect_understand_anything(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for rel in PROVIDER_ARTIFACTS:
        path = root / rel
        row: dict[str, Any] = {
            "path": rel,
            "exists": path.exists(),
            "authority": "support_advisory",
            "provider_role": "deterministic_code_graph_evidence",
        }
        if path.exists():
            row["size_bytes"] = path.stat().st_size
            if path.name.endswith(".json"):
                payload = _read_json(path)
                if payload:
                    row["top_level_keys"] = sorted(str(key) for key in payload.keys())[:20]
        artifacts.append(row)
    available = any(item["exists"] for item in artifacts)
    return {
        "provider": "understand-anything",
        "available": available,
        "authority": "support_advisory",
        "truth_authority": False,
        "skill_ref": "/Users/apple/Developer/Personal/products/justin-mc-lai-skills/skills/qi-dev/qi-dev-understand-anything/SKILL.md",
        "artifacts": artifacts,
        "boundary": "Provider artifacts are source navigation evidence only and cannot override Beacon package truth.",
    }


def _candidate_truth(inventory: dict[str, Any], provider: dict[str, Any]) -> dict[str, Any]:
    claims: list[dict[str, Any]] = []
    entry_points = list(inventory.get("entry_points") or [])
    skill_files = list(inventory.get("skill_files") or [])
    test_files = list(inventory.get("test_files") or [])

    if entry_points:
        claims.append(
            {
                "id": "CLAIM-001",
                "claim": "Project behavior can be reconstructed from detected entry points.",
                "confidence": "medium",
                "source_refs": entry_points[:10],
                "authority": "candidate_only",
            }
        )
    if skill_files:
        claims.append(
            {
                "id": "CLAIM-002",
                "claim": "Skill files provide strong workflow evidence for candidate truth reconstruction.",
                "confidence": "high",
                "source_refs": skill_files[:10],
                "authority": "candidate_only",
            }
        )
    if test_files:
        claims.append(
            {
                "id": "CLAIM-003",
                "claim": "Existing tests can be used as behavior evidence for coverage reconstruction.",
                "confidence": "medium",
                "source_refs": test_files[:10],
                "authority": "candidate_only",
            }
        )
    if bool(provider.get("available")):
        refs = [str(item.get("path")) for item in provider.get("artifacts", []) if item.get("exists")]
        claims.append(
            {
                "id": "CLAIM-004",
                "claim": "Understand-Anything artifacts can enrich source graph navigation.",
                "confidence": "medium",
                "source_refs": refs,
                "authority": "candidate_only",
                "provider_boundary": "evidence_only",
            }
        )

    ambiguity: list[dict[str, str]] = []
    if not claims:
        ambiguity.append(
            {
                "id": "AMB-001",
                "reason": "No strong source evidence was detected.",
                "route": "Ask user for feature scope or run provider analysis before promotion.",
            }
        )
    if not test_files:
        ambiguity.append(
            {
                "id": "AMB-002",
                "reason": "No tests were detected in the intake scope.",
                "route": "Keep coverage claims low-confidence until QA evidence is added.",
            }
        )

    return {
        "status": "candidate",
        "truth_authority": False,
        "formal_truth_rule": "code can propose candidate truth; user-confirmed Beacon package Markdown is formal truth",
        "claims": claims,
        "ambiguity": ambiguity,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    inventory = payload["source_inventory"]
    provider = payload["providers"]["understand_anything"]
    candidate = payload["candidate_truth"]
    lines = [
        f"# Code2Truth Intake: {payload['feature']}",
        "",
        f"- version: `{payload['version']}`",
        f"- target_project: `{payload['target_project_root']}`",
        f"- authority: `support_evidence_only`",
        f"- generated_at: `{payload['generated_at']}`",
        "",
        "## Boundary",
        "",
        "Code and provider graphs can propose candidate truth. User-confirmed Beacon package Markdown is formal truth.",
        "",
        "## Source Inventory",
        "",
        f"- files_scanned: `{inventory['file_count']}`",
        f"- source_files: `{inventory['counts'].get('source', 0)}`",
        f"- skill_files: `{inventory['counts'].get('skill', 0)}`",
        f"- test_files: `{inventory['counts'].get('test', 0)}`",
        f"- doc_files: `{inventory['counts'].get('doc', 0)}`",
        "",
        "### Entry Points",
        "",
    ]
    for ref in inventory.get("entry_points", [])[:20]:
        lines.append(f"- `{ref}`")
    if not inventory.get("entry_points"):
        lines.append("- none detected")

    lines.extend(["", "## Provider Evidence", ""])
    lines.append(f"- understand_anything_available: `{bool(provider.get('available'))}`")
    lines.append("- provider_authority: `support_advisory`")
    lines.append("- truth_authority: `false`")
    for item in provider.get("artifacts", []):
        if item.get("exists"):
            lines.append(f"- `{item.get('path')}`")

    lines.extend(["", "## Candidate Truth", ""])
    for claim in candidate.get("claims", []):
        lines.append(f"- `{claim['id']}` confidence=`{claim['confidence']}` authority=`candidate_only`: {claim['claim']}")
        refs = claim.get("source_refs", [])
        if refs:
            lines.append(f"  - refs: {', '.join(f'`{ref}`' for ref in refs[:5])}")
    if not candidate.get("claims"):
        lines.append("- none")

    lines.extend(["", "## Ambiguity", ""])
    for item in candidate.get("ambiguity", []):
        lines.append(f"- `{item['id']}` {item['reason']} route=`{item['route']}`")
    if not candidate.get("ambiguity"):
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Promotion Route",
            "",
            "Candidate truth can be promoted only through user confirmation and Beacon truth/change/refreeze routing.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_code2truth_intake(
    project_root: Path,
    *,
    target_project_root: Path,
    version: str,
    feature: str,
    provider: str = "auto",
    use_lighthouse: bool = True,
    write: bool = True,
) -> dict[str, Any]:
    """Build source-driven candidate truth evidence for an existing project."""

    root = project_root.expanduser().resolve()
    target = target_project_root.expanduser().resolve()
    resolved_version = resolve_target_version(root, version)
    slug = feature_slug(feature)
    truth_map = resolve_truth_map(root, version=resolved_version, feature=feature)
    truth_verify = verify_truth_map(root, version=resolved_version, feature=feature, strict=False)
    inventory = _collect_source_inventory(target)
    understand_anything = _detect_understand_anything(target)
    output_dir = root / ".beacon" / "code2truth" / slug
    json_path = output_dir / "intake.json"
    markdown_path = output_dir / "intake.md"

    lighthouse_payload: dict[str, Any] = {}
    if use_lighthouse:
        lighthouse_payload = generate_lighthouse_artifact(
            target,
            target=None,
            mode="system-architecture-map",
            version=resolved_version,
            output_path=str(output_dir / "lighthouse-system-architecture-map.md"),
            write_versioned_output=False,
        )

    source_architecture_status = current_source_architecture_status(root, version=resolved_version)
    candidate = _candidate_truth(inventory, understand_anything)
    generated_at = now_iso()

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact": "code2truth-intake",
        "status": "candidate",
        "version": resolved_version,
        "feature": feature,
        "feature_slug": slug,
        "project_root": str(root),
        "target_project_root": str(target),
        "generated_at": generated_at,
        "authority": "support_evidence_only",
        "truth_authority": False,
        "formal_truth_rule": "code can propose candidate truth; user-confirmed Beacon package Markdown is formal truth",
        "source_inventory": inventory,
        "providers": {
            "requested": provider,
            "understand_anything": understand_anything,
        },
        "lighthouse": lighthouse_payload,
        "source_architecture_status": source_architecture_status,
        "candidate_truth": candidate,
        "promotion_gate": {
            "user_confirmation_required": True,
            "direct_package_write_allowed": False,
            "route": "beacon-truth / beacon-change-refreeze",
            "package_truth_paths": truth_map.get("feature_truth", {}).get("source_paths", {}),
        },
        "implementation_closure": {
            "no_op_allowed": True,
            "condition": "Only when frozen ACs are already satisfied by existing behavior and evidence.",
            "task_completion_authority": "execution_progress_not_tasks_md",
        },
        "qa_closure": {
            "must_verify": [
                "truth-map resolution",
                "package coverage",
                "provider evidence boundary",
                "governance/doctor verification",
                "current behavior satisfaction",
            ]
        },
        "truth_map_verify": {
            "status": truth_verify.get("status"),
            "blocked": bool(truth_verify.get("blocked")),
            "diagnostics": truth_verify.get("diagnostics", []),
        },
    }

    if write:
        payload["output_json_path"] = _rel(root, json_path)
        payload["output_markdown_path"] = _rel(root, markdown_path)
        markdown = _render_markdown(payload)
        write_json(json_path, payload)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown, encoding="utf-8")
    return payload
