"""GoalRun main-axis generate/validate (v1.6.7 UD-AXIS).

Program-level artifact so change regenerates user journey FSM instead of
feature-slice docs only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from beacon.utils.runtime import now_iso, write_json

GOALRUN_STATES = (
    "created",
    "running",
    "stage_active",
    "host_interrupted",
    "stage_blocked",
    "awaiting_verifier",
    "completed",
    "release_pending",
    "release_confirmed",
)

REQUIRED_SECTIONS = (
    "User intent",
    "GoalRun",
    "Mount table",
    "done_when",
    "Illegal",
    "Wave",
    "Q1",
)

# change types that require regenerate
CHANGE_TRIGGERS = frozenset(
    {
        "ac",
        "promise",
        "acceptance",
        "stage",
        "parallel",
        "subagent",
        "worktree",
        "longrun",
        "driver",
        "supervise",
        "entry",
        "domain_fsm",
        "entity_precedence",
        "dual_install",
    }
)

DEFAULT_DONE_WHEN = ["domain_fsm", "domain_fsm_coverage", "evidence_chain", "continuous_qa"]
DEFAULT_DONE_WHEN_UX = [
    "design_baseline",
    "design_md_lint",
    "domain_fsm",
    "domain_fsm_coverage",
    "evidence_chain",
    "continuous_qa",
]

SUBMACHINES_CANNOT_COMPLETE = (
    "SupervisorSession",
    "AgentDriver",
    "SubagentSession",
    "RalphDelegate",
    "DesignStage",
)

PROGRAM_V167 = "beacon-product-goal-domain-delivery-v167"

# default mount roles when graph lacks summaries
MOUNT_ROLES = {
    "beacon-product-goal-runtime-v167": ("main axis owner", "facade + stages"),
    "beacon-domain-fsm-authority-v167": ("truth hard gate", "L2 business FSM"),
    "beacon-golden-commerce-fixture-v167": ("truth/qa fixture", "negative clamps"),
    "beacon-domain-fsm-qa-gate-v167": ("qa hard gate", "legal/illegal"),
    "beacon-ui-design-ship-gate-v167": ("design/ship", "UX matrix when ux_required"),
    "beacon-ralph-implement-boundary-v167": ("implement delegate", "no verdict write"),
    "beacon-loop-discover-goal-finish-v167": ("support only", "discovery queue"),
    "beacon-goal-durable-supervisor-v167": ("longrun bypass", "SupervisorSession"),
    "beacon-goal-agent-driver-v167": ("longrun bypass", "AgentDriver"),
    "beacon-goalrun-main-axis-v167": ("axis governance", "regenerate on change"),
}


def program_dir(project_root: Path, version: str, program_slug: str) -> Path:
    return Path(project_root) / "docs" / "beacon" / version / "programs" / program_slug


def axis_md_path(project_root: Path, version: str, program_slug: str) -> Path:
    return program_dir(project_root, version, program_slug) / "goalrun-main-axis.md"


def axis_machine_path(project_root: Path, version: str) -> Path:
    return Path(project_root) / "docs" / "beacon" / version / ".machine" / "goalrun" / "main-axis.json"


def feature_graph_path(project_root: Path, version: str, program_slug: str) -> Path:
    return program_dir(project_root, version, program_slug) / "feature-graph.json"


def load_program_lakes(project_root: Path, version: str, program_slug: str) -> list[dict[str, Any]]:
    path = feature_graph_path(project_root, version, program_slug)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    lakes = data.get("lakes") if isinstance(data, dict) else []
    return [x for x in lakes if isinstance(x, dict) and x.get("slug")]


def change_requires_axis_regenerate(change_types: list[str] | None) -> dict[str, Any]:
    types = {str(t).strip().lower() for t in (change_types or []) if str(t).strip()}
    hit = sorted(types & CHANGE_TRIGGERS)
    return {
        "required": bool(hit),
        "matched_triggers": hit,
        "policy": "UD-AXIS-001",
        "blocked_if_skipped": bool(hit),
        "reason_code": "main_axis_regenerate_required" if hit else "",
    }


def default_done_when(*, domain_bearing: bool = True, ux_required: bool = False) -> list[str]:
    base = list(DEFAULT_DONE_WHEN_UX if ux_required else DEFAULT_DONE_WHEN)
    if domain_bearing and "domain_fsm_coverage" not in base:
        base.insert(0, "domain_fsm_coverage")
    return base


def render_axis_markdown(
    *,
    version: str,
    program_slug: str,
    lakes: list[dict[str, Any]],
    intent: str = "",
) -> str:
    intent = intent or "一句话 goal → 按业务序实现 → verifier 验收 → 人工 release"
    lines = [
        f"# GoalRun Main Axis — {program_slug}",
        "",
        f"- **version**: `{version}`",
        f"- **program**: `{program_slug}`",
        f"- **generated_at**: {now_iso()}",
        f"- **policy**: UD-AXIS-001..005 (change must regenerate this artifact)",
        "",
        "## User intent",
        "",
        intent,
        "",
        "## GoalRun (main axis states)",
        "",
        "```text",
        "created → running → stage_active{plan|truth|design?|implement|qa|release}",
        "              ↻ host_interrupted --resume-pack--> stage_active",
        "              → stage_blocked",
        "         → awaiting_verifier → completed (verifier required)",
        "         → release_pending → release_confirmed (human only)",
        "```",
        "",
        "### GoalRun states",
        "",
    ]
    for s in GOALRUN_STATES:
        lines.append(f"- `{s}`")
    lines.extend(
        [
            "",
            "## Mount table (program lakes on GoalRun)",
            "",
            "| Lake | Mount | Role |",
            "|------|-------|------|",
        ]
    )
    for lake in lakes:
        slug = str(lake.get("slug") or "")
        mount, role = MOUNT_ROLES.get(slug, ("program lake", str(lake.get("summary") or "see feature truth")))
        lines.append(f"| `{slug}` | {mount} | {role} |")
    lines.extend(
        [
            "",
            "## done_when",
            "",
            "Default domain-bearing:",
            "",
        ]
    )
    for d in default_done_when(domain_bearing=True):
        lines.append(f"- `{d}`")
    lines.extend(
        [
            "",
            "If `ux_required`: also `design_baseline`, `design_md_lint`.",
            "",
            "## Illegal transitions",
            "",
            "| ID | Illegal |",
            "|----|---------|",
            "| I-AXIS-001 | any → completed without verifier |",
            "| I-AXIS-002 | host_interrupted → completed |",
            "| I-AXIS-003 | stage_blocked → completed without clear |",
            "| I-AXIS-004 | auto release_confirmed |",
            "| I-AXIS-005 | submachine → completed |",
            "",
            "### Submachines cannot complete GoalRun",
            "",
        ]
    )
    for name in SUBMACHINES_CANNOT_COMPLETE:
        lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Wave (implementation order)",
            "",
            "```text",
            "Wave 1   domain-fsm-authority → golden → domain-fsm-qa-gate → ui-ship",
            "Wave 1b  product-goal-runtime (axis owner) + ralph-boundary",
            "Wave 2   loop-discover (support)",
            "Wave 3   durable-supervisor → agent-driver",
            "Wave 4   axis validate on change/freeze",
            "```",
            "",
            "## First-principles exit checklist (Q1–Q6)",
            "",
            "| # | Question |",
            "|---|----------|",
            "| Q1 | 用户成功是否可观测？ |",
            "| Q2 | 是否存在非法 complete/release 捷径？ |",
            "| Q3 | domain-bearing 是否有实体前置+合法 walk？ |",
            "| Q4 | 本 change 是否映射到主轴边/守卫？ |",
            "| Q5 | 实现 Wave 是否依赖未完成 L2/L0？ |",
            "| Q6 | 子机是否可能绕过 awaiting_verifier？ |",
            "",
            "## Refreeze note",
            "",
            "After regenerating this axis for a triggered change, run:",
            "",
            "```text",
            "beacon change \"<feature>\" --project . --version " + version + " --refreeze-chain",
            "# or $beacon-gen-refreeze",
            "```",
            "",
            "Do not implement against stale axis.",
            "",
            "## Shared with v2.0.0",
            "",
            "State names in GoalRun are shared with v2.0.0 / Loom program axis (UD-AXIS-003).",
            "",
        ]
    )
    return "\n".join(lines)


def generate_main_axis(
    project_root: Path,
    *,
    version: str = "v1.6.7",
    program_slug: str = PROGRAM_V167,
    intent: str = "",
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    lakes = load_program_lakes(project_root, version, program_slug)
    if not lakes:
        return {
            "status": "blocked",
            "blocked": True,
            "reason_code": "program_feature_graph_missing",
            "program_slug": program_slug,
            "version": version,
        }
    md = render_axis_markdown(
        version=version,
        program_slug=program_slug,
        lakes=lakes,
        intent=intent,
    )
    md_path = axis_md_path(project_root, version, program_slug)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md, encoding="utf-8")

    machine = {
        "schema_version": "1.0",
        "artifact": "goalrun_main_axis",
        "version": version,
        "program_slug": program_slug,
        "generated_at": now_iso(),
        "goalrun_states": list(GOALRUN_STATES),
        "lakes": [str(x.get("slug")) for x in lakes],
        "done_when_default": default_done_when(domain_bearing=True),
        "submachines_cannot_complete": list(SUBMACHINES_CANNOT_COMPLETE),
        "change_triggers": sorted(CHANGE_TRIGGERS),
        "axis_md": str(md_path.relative_to(project_root)),
        "policy": ["UD-AXIS-001", "UD-AXIS-002", "UD-AXIS-003", "UD-AXIS-004", "UD-AXIS-005"],
    }
    mpath = axis_machine_path(project_root, version)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    write_json(mpath, machine)

    validation = validate_main_axis(project_root, version=version, program_slug=program_slug)
    return {
        "status": "ok" if validation.get("ok") else "generated_with_validation_issues",
        "blocked": not bool(validation.get("ok")),
        "version": version,
        "program_slug": program_slug,
        "axis_md": str(md_path.relative_to(project_root)),
        "axis_machine": str(mpath.relative_to(project_root)),
        "lake_count": len(lakes),
        "validation": validation,
    }


def validate_main_axis(
    project_root: Path,
    *,
    version: str = "v1.6.7",
    program_slug: str = PROGRAM_V167,
) -> dict[str, Any]:
    project_root = Path(project_root).expanduser().resolve()
    md_path = axis_md_path(project_root, version, program_slug)
    missing: list[str] = []
    if not md_path.is_file():
        return {
            "ok": False,
            "blocked": True,
            "reason_code": "main_axis_artifact_missing",
            "missing": ["goalrun-main-axis.md"],
            "path": str(md_path),
        }
    text = md_path.read_text(encoding="utf-8")
    low = text.lower()
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in low and sec not in text:
            missing.append(sec)
    for state in ("created", "awaiting_verifier", "completed", "stage_active"):
        if state not in text:
            missing.append(f"state:{state}")
    lakes = load_program_lakes(project_root, version, program_slug)
    unmounted = []
    for lake in lakes:
        slug = str(lake.get("slug") or "")
        if slug and slug not in text:
            unmounted.append(slug)
    if unmounted:
        missing.append("mount:" + ",".join(unmounted[:8]))
    if "domain_fsm_coverage" not in text and "domain_fsm" not in text:
        missing.append("done_when_domain")
    if "Q1" not in text or "Q6" not in text:
        missing.append("Q1-Q6")
    if "refreeze" not in low:
        missing.append("refreeze_note")
    ok = not missing
    return {
        "ok": ok,
        "blocked": not ok,
        "reason_code": "" if ok else "main_axis_validation_failed",
        "missing": missing,
        "path": str(md_path.relative_to(project_root)),
        "lake_count": len(lakes),
    }


def assert_submachine_cannot_complete(submachine: str, target_status: str) -> dict[str, Any]:
    """Policy helper for tests / runtime guards."""
    sm = str(submachine or "")
    target = str(target_status or "").strip().lower()
    illegal = target in {"completed", "release_confirmed"} and (
        sm in SUBMACHINES_CANNOT_COMPLETE or "driver" in sm.lower() or "subagent" in sm.lower()
    )
    return {
        "allowed": not illegal,
        "blocked": illegal,
        "reason_code": "submachine_cannot_complete_goalrun" if illegal else "",
        "policy": "UD-AXIS-005",
    }
