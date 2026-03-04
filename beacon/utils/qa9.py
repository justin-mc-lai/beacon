"""QA9 helpers for Beacon v1.0.2."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

QA9_TYPES: tuple[str, ...] = (
    "unit",
    "interface",
    "contract",
    "integration",
    "smoke",
    "functional",
    "regression",
    "exception",
    "compatibility",
)

PROJECT_TYPES: tuple[str, ...] = (
    "ai-agent-skill",
    "web-app",
    "api-service",
    "sdk-lib",
)

QA_PROFILE_TYPES: dict[str, tuple[str, ...]] = {
    "web-core": ("unit", "interface", "smoke", "functional", "regression", "exception"),
    "web-full": QA9_TYPES,
    "custom": QA9_TYPES,
}

LEGACY_TO_QA_TYPE: dict[str, str] = {
    "ui": "functional",
    "api-curl": "interface",
}

QA_TO_LEGACY_LAYER: dict[str, str] = {
    "functional": "ui",
    "interface": "api-curl",
}


def normalize_qa_type(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    if raw in LEGACY_TO_QA_TYPE:
        return LEGACY_TO_QA_TYPE[raw]
    return raw


def to_legacy_layer(value: str | None) -> str:
    qa_type = normalize_qa_type(value)
    return QA_TO_LEGACY_LAYER.get(qa_type, qa_type)


def parse_qa_types(raw: str | Iterable[str] | None, profile: str = "web-full") -> list[str]:
    profile_norm = str(profile or "web-full").strip().lower()
    default_types = list(QA_PROFILE_TYPES.get(profile_norm, QA_PROFILE_TYPES["web-full"]))

    if raw is None:
        return default_types

    values: list[str] = []
    if isinstance(raw, str):
        values = [x.strip() for x in raw.split(",") if x.strip()]
    else:
        for item in raw:
            text = str(item or "").strip()
            if not text:
                continue
            if "," in text:
                values.extend([x.strip() for x in text.split(",") if x.strip()])
            else:
                values.append(text)

    out: list[str] = []
    for item in values:
        qa_type = normalize_qa_type(item)
        if qa_type not in QA9_TYPES:
            continue
        if qa_type in out:
            continue
        out.append(qa_type)

    return out or default_types


def default_command_for_qa_type(qa_type: str, *, ui_runner: str = "playwright") -> str:
    runner = str(ui_runner or "playwright").strip().lower()
    junit_arg = '--junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"'
    if qa_type == "unit":
        return f"python3 -m pytest -q -k unit {junit_arg}"
    if qa_type == "interface":
        return f"python3 -m pytest -q -k interface {junit_arg}"
    if qa_type == "contract":
        return f"python3 -m pytest -q -k contract {junit_arg}"
    if qa_type == "integration":
        return f"python3 -m pytest -q -k integration {junit_arg}"
    if qa_type == "smoke":
        return f"python3 -m pytest -q -m smoke {junit_arg}"
    if qa_type == "functional":
        if runner == "cypress":
            return "npx cypress run --headless"
        if runner == "browser-use":
            return (
                "python3 -m beacon.adapters.browser_use_runner --mode functional "
                '--fallback-cmd "python3 -m pytest -q -k functional '
                '--junitxml \\"${BEACON_JUNIT_PATH:-.beacon/junit.xml}\\""'
            )
        if runner == "agent-browser":
            return f"python3 -m pytest -q -k functional {junit_arg}"
        if runner == "midscene":
            return "node scripts/midscene-functional.mjs"
        return "npx playwright test"
    if qa_type == "regression":
        return f"python3 -m pytest -q -k regression {junit_arg}"
    if qa_type == "exception":
        return f"python3 -m pytest -q -k exception {junit_arg}"
    if qa_type == "compatibility":
        if runner == "cypress":
            return "npx cypress run --browser chrome"
        if runner == "browser-use":
            return (
                "python3 -m beacon.adapters.browser_use_runner --mode compatibility "
                '--fallback-cmd "python3 -m pytest -q -k compatibility '
                '--junitxml \\"${BEACON_JUNIT_PATH:-.beacon/junit.xml}\\""'
            )
        if runner == "midscene":
            return "node scripts/midscene-compatibility.mjs"
        return "npx playwright test --project=chromium --project=firefox --project=webkit"
    return f"python3 -m pytest -q {junit_arg}"


def default_assertion_for_qa_type(qa_type: str) -> str:
    return {
        "unit": "All unit assertions pass",
        "interface": "HTTP status and schema assertions pass",
        "contract": "Provider/consumer contract assertions pass",
        "integration": "Integration flow assertions pass",
        "smoke": "Critical path assertions pass",
        "functional": "Web UI assertions and key actions pass",
        "regression": "No known behavior regression found",
        "exception": "Negative-path assertions pass",
        "compatibility": "Cross-browser/device assertions pass",
    }.get(qa_type, "assertion defined")


def infer_project_scan(project_root: Path) -> dict[str, object]:
    language = "unknown"
    framework = "unknown"
    frontend = "unknown"

    if (project_root / "pom.xml").exists() or (project_root / "build.gradle").exists():
        language = "java"
        framework = "spring" if (project_root / "src" / "main").exists() else "java-app"
    elif (project_root / "package.json").exists():
        language = "javascript"
        if (project_root / "next.config.js").exists() or (project_root / "next.config.mjs").exists():
            framework = "nextjs"
        elif (project_root / "nuxt.config.ts").exists() or (project_root / "nuxt.config.js").exists():
            framework = "nuxt"
        else:
            framework = "node-web"
        frontend = "web"
    elif (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        language = "python"
        if (project_root / "manage.py").exists():
            framework = "django"
        else:
            framework = "python-app"
    elif (project_root / "go.mod").exists():
        language = "go"
        framework = "go-app"

    api_spec_refs: list[str] = []
    for pattern in ("openapi*.yml", "openapi*.yaml", "swagger*.json", "contracts/**/*.json"):
        api_spec_refs.extend(str(p.relative_to(project_root)) for p in project_root.glob(pattern))
    api_spec_refs = sorted(dict.fromkeys(api_spec_refs))[:20]

    risk_points = [
        "authz/authn boundary",
        "cross-browser ui behavior",
        "api contract drift",
        "exception handling and replay safety",
    ]

    return {
        "language": language,
        "framework": framework,
        "frontend": frontend,
        "api_spec_refs": api_spec_refs,
        "risk_points": risk_points,
    }


def infer_project_type(project_root: Path, project_scan: dict[str, object] | None = None) -> str:
    scan = project_scan or infer_project_scan(project_root)
    framework = str(scan.get("framework") or "").strip().lower()
    frontend = str(scan.get("frontend") or "").strip().lower()
    has_skill_markers = (
        (project_root / "skills").exists()
        or (project_root / "agent-skills").exists()
        or bool(list(project_root.glob("**/SKILL.md")))
        or "skill" in framework
    )
    if has_skill_markers:
        return "ai-agent-skill"
    if frontend == "web":
        return "web-app"
    api_spec_refs = scan.get("api_spec_refs")
    if isinstance(api_spec_refs, list) and api_spec_refs:
        return "api-service"
    return "sdk-lib"


def _build_qa_applicability(project_type: str, *, has_web_ui: bool) -> dict[str, str]:
    if project_type == "ai-agent-skill":
        out = {
            "unit": "required",
            "interface": "required",
            "contract": "required",
            "integration": "required",
            "smoke": "required",
            "functional": "conditional",
            "regression": "required",
            "exception": "required",
            "compatibility": "conditional",
        }
        if has_web_ui:
            out["functional"] = "required"
            out["compatibility"] = "required"
        return out
    if project_type == "web-app":
        return {
            "unit": "required",
            "interface": "required",
            "contract": "conditional",
            "integration": "required",
            "smoke": "required",
            "functional": "required",
            "regression": "required",
            "exception": "required",
            "compatibility": "required",
        }
    if project_type == "api-service":
        return {
            "unit": "required",
            "interface": "required",
            "contract": "required",
            "integration": "required",
            "smoke": "required",
            "functional": "na",
            "regression": "required",
            "exception": "required",
            "compatibility": "na",
        }
    return {
        "unit": "required",
        "interface": "required",
        "contract": "conditional",
        "integration": "conditional",
        "smoke": "required",
        "functional": "na",
        "regression": "required",
        "exception": "required",
        "compatibility": "na",
    }


def _first_existing_relative(project_root: Path, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        for path in sorted(project_root.glob(pattern)):
            if path.is_file():
                return str(path.relative_to(project_root))
    return ""


def command_presets_from_project_scan(
    *,
    project_root: Path,
    project_scan: dict[str, object],
    ui_runner: str,
) -> dict[str, str]:
    presets: dict[str, str] = {}
    api_spec_refs = project_scan.get("api_spec_refs")
    first_api_spec = ""
    if isinstance(api_spec_refs, list):
        for item in api_spec_refs:
            text = str(item or "").strip()
            if text:
                first_api_spec = text
                break

    postman_collection = _first_existing_relative(
        project_root,
        (
            "**/*.postman_collection.json",
            "postman/**/*.json",
            "collections/**/*.json",
        ),
    )
    if postman_collection:
        presets["interface"] = f"npx newman run {postman_collection}"

    if first_api_spec:
        presets["contract"] = f"python -m schemathesis run {first_api_spec}"
        if "interface" not in presets:
            presets["interface"] = f"python -m schemathesis run {first_api_spec} --checks all"

    if (project_root / "docker-compose.test.yml").exists():
        presets["integration"] = "docker compose -f docker-compose.test.yml up --abort-on-container-exit"
    elif (project_root / "testcontainers").exists():
        presets["integration"] = "python -m pytest -q -k integration --maxfail=1"

    for qa_type in QA9_TYPES:
        presets.setdefault(qa_type, default_command_for_qa_type(qa_type, ui_runner=ui_runner))
    return presets


def build_qa_strategy(
    *,
    project_root: Path,
    qa_types: Iterable[str] | None = None,
    ui_runner: str = "playwright",
) -> dict[str, Any]:
    project_scan = infer_project_scan(project_root)
    project_type = infer_project_type(project_root, project_scan)
    has_web_ui = str(project_scan.get("frontend") or "").strip().lower() == "web"
    applicability = _build_qa_applicability(project_type, has_web_ui=has_web_ui)
    selected_types = parse_qa_types(list(qa_types) if qa_types is not None else None, profile="web-full")
    selected_required = [x for x in selected_types if applicability.get(x, "required") != "na"]
    command_presets = command_presets_from_project_scan(
        project_root=project_root,
        project_scan=project_scan,
        ui_runner=ui_runner,
    )
    runner_policy = {
        "functional": {
            "primary": "browser-use" if project_type in {"ai-agent-skill", "web-app"} else "playwright",
            "fallback": ["playwright", "cypress", "agent-browser"],
        },
        "compatibility": {
            "primary": "playwright",
            "fallback": ["cypress"],
        },
        "api_layers": {
            "interface": "schemathesis/newman/pytest",
            "contract": "schemathesis/pact",
            "integration": "pytest+testcontainers",
        },
    }
    return {
        "schema_version": "1.0.2",
        "generated_at": datetime.now().isoformat(),
        "project_type": project_type,
        "project_scan": project_scan,
        "qa_applicability": applicability,
        "qa_required_types": selected_required,
        "runner_policy": runner_policy,
        "command_baseline": {qa: command_presets.get(qa, "") for qa in QA9_TYPES},
        "ui_runner": str(ui_runner or "playwright").strip().lower() or "playwright",
    }


def resolve_llm_mode(mode: str | None) -> str:
    raw = str(mode or "auto").strip().lower()
    if raw in {"rule", "real", "auto"}:
        return raw
    return "auto"


def build_qa_llm_plan(
    *,
    project_root: Path,
    llm_auto: bool,
    llm_mode: str,
    qa_types: list[str],
) -> dict[str, object]:
    resolved_mode = resolve_llm_mode(llm_mode)
    runtime_mode = resolved_mode
    model = "beacon-rule-llm-v1"

    if llm_auto and resolved_mode == "auto":
        real_enabled = str(os.environ.get("BEACON_LLM_MODE", "")).strip().lower() in {"real", "live", "api"}
        has_key = bool(str(os.environ.get("BEACON_LLM_API_KEY", "")).strip())
        runtime_mode = "real" if (real_enabled and has_key) else "rule"

    if runtime_mode == "real":
        model = str(os.environ.get("BEACON_LLM_MODEL", "gpt-4o-mini")).strip() or "gpt-4o-mini"

    if not llm_auto:
        runtime_mode = "rule"
        model = "beacon-rule-llm-v1"

    return {
        "mode": runtime_mode if llm_auto else "disabled",
        "model": model if llm_auto else "none",
        "project_scan": infer_project_scan(project_root),
        "project_type": infer_project_type(project_root),
        "generated_at": datetime.now().isoformat(),
        "prompt_ref": "beacon.qa9.llm.plan.v1.0.2",
        "skip_reason": "" if llm_auto else "llm_auto_disabled",
        "qa_types": list(qa_types),
    }
