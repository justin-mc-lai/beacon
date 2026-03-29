"""Story-scenario expansion helpers for Beacon v1.1.9 QA."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from beacon.utils.artifact_paths import qa_matrix_output
from beacon.utils.qa9 import default_assertion_for_qa_type, default_command_for_qa_type, normalize_qa_type, to_legacy_layer
from beacon.utils.runtime import now_iso, read_json, write_json
from beacon.utils.story_state import feature_slug

SCENARIO_MAP_SCHEMA = "1.0"
DEFAULT_BROWSER_FAMILIES: tuple[str, ...] = (
    "happy",
    "negative",
    "boundary",
    "recovery",
    "compatibility",
)
BROWSER_QA_TYPES: set[str] = {"functional", "compatibility", "smoke"}


def is_browser_relevant_qa_type(qa_type: str) -> bool:
    normalized = normalize_qa_type(qa_type)
    return normalized in BROWSER_QA_TYPES


def scenario_map_path(project_root: Path, *, version: str, feature: str) -> Path:
    return qa_matrix_output(project_root, version, feature_slug(feature), "story-scenario-map")


def load_story_scenario_map(project_root: Path, *, version: str, feature: str) -> dict[str, Any]:
    payload = read_json(scenario_map_path(project_root, version=version, feature=feature), {})
    return payload if isinstance(payload, dict) else {}


def write_story_scenario_map(
    project_root: Path,
    *,
    version: str,
    feature: str,
    payload: dict[str, Any],
) -> Path:
    path = scenario_map_path(project_root, version=version, feature=feature)
    write_json(path, payload)
    return path


def flatten_story_scenarios(payload: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        return []
    return [item for item in scenarios if isinstance(item, dict)]


def _entry_browser_required(entry: dict[str, Any]) -> bool:
    if bool(entry.get("browser_required")):
        return True
    qa_type = normalize_qa_type(str(entry.get("qa_type") or entry.get("layer") or "").strip())
    if qa_type in BROWSER_QA_TYPES:
        return True
    text = " ".join(
        [
            str(entry.get("assertion") or ""),
            str(entry.get("title") or ""),
            str(entry.get("text") or ""),
        ]
    ).lower()
    return any(token in text for token in ("ui", "browser", "page", "form", "click", "login", "dashboard", "页面", "表单", "浏览器", "点击"))


def _scenario_qa_type(base_qa_type: str, family: str) -> str:
    normalized = normalize_qa_type(base_qa_type)
    if family == "compatibility":
        return "compatibility"
    if normalized in {"functional", "compatibility", "smoke"}:
        return "functional"
    return normalized or "contract"


def _scenario_priority(family: str) -> str:
    return {
        "happy": "P0",
        "negative": "P0",
        "boundary": "P1",
        "recovery": "P1",
        "compatibility": "P1",
        "alternate": "P1",
        "permission": "P1",
        "state-data": "P2",
        "primary": "P1",
    }.get(str(family or "").strip().lower(), "P2")


def _scenario_title(*, ac_id: str, family: str, assertion: str) -> str:
    label = {
        "happy": "happy path",
        "negative": "negative path",
        "boundary": "boundary path",
        "recovery": "recovery path",
        "compatibility": "compatibility path",
        "alternate": "alternate path",
        "permission": "permission path",
        "state-data": "state/data path",
        "primary": "primary path",
    }.get(str(family or "").strip().lower(), "scenario")
    return f"{ac_id} {label} :: {assertion[:96]}"


def _scenario_assertion(assertion: str, qa_type: str, family: str) -> str:
    detail = {
        "happy": "happy path completes with expected evidence",
        "negative": "negative path is rejected or handled with explicit evidence",
        "boundary": "boundary path is validated with explicit evidence",
        "recovery": "recovery path survives refresh/back/retry with evidence",
        "compatibility": "compatibility path preserves behavior across browser/device pairs",
        "alternate": "alternate path is supported with evidence",
        "permission": "permission path enforces access boundaries with evidence",
        "state-data": "state/data path preserves expected state with evidence",
        "primary": default_assertion_for_qa_type(qa_type),
    }.get(str(family or "").strip().lower(), default_assertion_for_qa_type(qa_type))
    if assertion and family != "primary":
        return f"{assertion} ({detail})"
    return detail


def _scenario_families(browser_required: bool, scenario_depth: str) -> list[str]:
    if not browser_required:
        return ["primary"]
    families = list(DEFAULT_BROWSER_FAMILIES)
    depth = str(scenario_depth or "standard").strip().lower()
    if depth == "minimal":
        families = families[:2]
    elif depth == "deep":
        families.extend(["alternate", "permission", "state-data"])
    out: list[str] = []
    for family in families:
        if family not in out:
            out.append(family)
    return out


def expand_story_scenarios(
    *,
    feature: str,
    version: str,
    story_sequence: list[dict[str, Any]],
    entries: list[dict[str, Any]],
    expansion_profile: str = "pua-web",
    scenario_depth: str = "standard",
    ui_runner: str = "browser-use",
) -> dict[str, Any]:
    by_ac: dict[str, list[dict[str, Any]]] = {}
    normalized_ui_runner = str(ui_runner or "").strip().lower()
    default_exploratory_runner = normalized_ui_runner if normalized_ui_runner in {"agent-browser", "browser-use"} else "browser-use"
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        ac_id = str(entry.get("ac_id") or "").strip()
        if ac_id:
            by_ac.setdefault(ac_id, []).append(entry)

    scenarios: list[dict[str, Any]] = []
    story_rows: list[dict[str, Any]] = []
    scenario_index = 0
    for item in story_sequence:
        if not isinstance(item, dict):
            continue
        ac_id = str(item.get("ac_id") or "").strip()
        if not ac_id:
            continue
        related = by_ac.get(ac_id, [])
        story_scenarios: list[dict[str, Any]] = []
        for entry in related:
            qa_type = normalize_qa_type(str(entry.get("qa_type") or entry.get("layer") or "contract"))
            browser_required = _entry_browser_required(entry)
            families = _scenario_families(browser_required, scenario_depth)
            source_tc_id = str(entry.get("source_tc_id") or entry.get("tc_id") or "").strip()
            title_seed = str(entry.get("assertion") or item.get("text") or item.get("theme") or ac_id).strip()
            depends_on_seed = ""
            for family in families:
                scenario_index += 1
                scenario_id = f"SC-{scenario_index:03d}"
                executable_tc_id = f"{source_tc_id}-{family.upper()}" if source_tc_id else scenario_id
                scenario_qa_type = _scenario_qa_type(qa_type, family)
                command = str(entry.get("command") or "").strip() or default_command_for_qa_type(scenario_qa_type, ui_runner=ui_runner)
                explore_command = command if browser_required else ""
                replay_command = default_command_for_qa_type(
                    "compatibility" if family == "compatibility" else scenario_qa_type,
                    ui_runner="playwright",
                ) if browser_required else ""
                scenario = {
                    "scenario_id": scenario_id,
                    "source_tc_id": source_tc_id,
                    "tc_id": executable_tc_id,
                    "ac_id": ac_id,
                    "qa_type": scenario_qa_type,
                    "layer": to_legacy_layer(scenario_qa_type),
                    "scenario_family": family,
                    "title": _scenario_title(ac_id=ac_id, family=family, assertion=title_seed),
                    "browser_required": browser_required,
                    "replay_required": browser_required and family in {"happy", "negative", "compatibility"},
                    "exploratory_runner": default_exploratory_runner if browser_required else "native",
                    "deterministic_runner": "playwright" if browser_required else "native",
                    "explore_command": "" if browser_required else explore_command,
                    "replay_command": replay_command,
                    "coverage_axes": [family, scenario_qa_type] + (["browser"] if browser_required else ["non-browser"]),
                    "depends_on": [depends_on_seed] if depends_on_seed and family != "happy" else [],
                    "stop_on_fail": family == "happy",
                    "automation": str(entry.get("automation") or "auto"),
                    "command": command,
                    "assertion": _scenario_assertion(title_seed, scenario_qa_type, family),
                    "priority": _scenario_priority(family),
                    "evidence_path": str(entry.get("evidence_path") or "").replace(
                        str(entry.get("tc_id") or source_tc_id or ""),
                        executable_tc_id,
                    ),
                    "required_files": ["command.txt", "stdout.log", "stderr.log", "result.json", "junit.xml"],
                }
                scenarios.append(scenario)
                story_scenarios.append(
                    {
                        "scenario_id": scenario_id,
                        "source_tc_id": source_tc_id,
                        "tc_id": executable_tc_id,
                        "scenario_family": family,
                        "qa_type": scenario_qa_type,
                        "browser_required": browser_required,
                        "replay_required": bool(scenario["replay_required"]),
                    }
                )
                if not depends_on_seed:
                    depends_on_seed = scenario_id
        story_rows.append(
            {
                "ac_id": ac_id,
                "theme": str(item.get("theme") or ""),
                "text": str(item.get("text") or ""),
                "scenario_ids": [row["scenario_id"] for row in story_scenarios],
                "scenario_families": [row["scenario_family"] for row in story_scenarios],
                "required_families": [
                    row["scenario_family"]
                    for row in story_scenarios
                    if bool(row.get("browser_required"))
                ],
                "scenarios": story_scenarios,
            }
        )

    return {
        "schema_version": SCENARIO_MAP_SCHEMA,
        "feature": feature,
        "feature_slug": feature_slug(feature),
        "version": version,
        "generated_at": now_iso(),
        "expansion_profile": expansion_profile,
        "scenario_depth": scenario_depth,
        "families_required": list(DEFAULT_BROWSER_FAMILIES),
        "stories": story_rows,
        "scenarios": scenarios,
    }
