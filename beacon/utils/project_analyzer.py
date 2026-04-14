"""Static project feature detection for Beacon v1.2.0 skill discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _exists(root: Path, *parts: str) -> bool:
    return root.joinpath(*parts).exists()


def _glob_exists(root: Path, pattern: str) -> bool:
    return any(root.glob(pattern))


def analyze_project(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    indicators: dict[str, bool] = {
        "package_json": _exists(root, "package.json"),
        "package_lock": _exists(root, "package-lock.json"),
        "yarn_lock": _exists(root, "yarn.lock"),
        "pnpm_lock": _exists(root, "pnpm-lock.yaml"),
        "requirements_txt": _exists(root, "requirements.txt"),
        "pyproject_toml": _exists(root, "pyproject.toml"),
        "gemfile": _exists(root, "Gemfile"),
        "go_mod": _exists(root, "go.mod"),
        "cargo_toml": _exists(root, "Cargo.toml"),
        "pom_xml": _exists(root, "pom.xml"),
        "gradle": _exists(root, "build.gradle") or _exists(root, "build.gradle.kts"),
        "dotnet": _glob_exists(root, "*.csproj") or _glob_exists(root, "**/*.csproj"),
        "dockerfile": _exists(root, "Dockerfile"),
        "compose": _exists(root, "docker-compose.yml") or _exists(root, "compose.yaml"),
        "github_actions": _exists(root, ".github", "workflows"),
        "tests_dir": _exists(root, "tests") or _exists(root, "test"),
        "frontend_src": _exists(root, "src") or _exists(root, "app"),
        "ios_dir": _exists(root, "ios"),
        "android_dir": _exists(root, "android"),
        "flutter": _exists(root, "pubspec.yaml"),
        "dbt": _exists(root, "dbt_project.yml"),
        "airflow": _exists(root, "airflow.cfg") or _exists(root, "dags"),
        "notebooks": _exists(root, "notebooks") or _glob_exists(root, "*.ipynb"),
    }

    languages: list[str] = []
    package_managers: list[str] = []
    frameworks: list[str] = []

    if indicators["package_json"]:
        languages.append("nodejs")
        if indicators["package_lock"]:
            package_managers.append("npm")
        if indicators["yarn_lock"]:
            package_managers.append("yarn")
        if indicators["pnpm_lock"]:
            package_managers.append("pnpm")
        package_json = (root / "package.json").read_text(encoding="utf-8", errors="ignore")
        if '"react"' in package_json:
            frameworks.append("react")
        if '"vue"' in package_json:
            frameworks.append("vue")
        if '"next"' in package_json:
            frameworks.append("nextjs")
        if '"express"' in package_json:
            frameworks.append("express")
        if '"react-native"' in package_json:
            frameworks.append("react-native")
    if indicators["requirements_txt"] or indicators["pyproject_toml"]:
        languages.append("python")
        package_managers.append("pip")
        py_text = ""
        if indicators["requirements_txt"]:
            py_text += (root / "requirements.txt").read_text(encoding="utf-8", errors="ignore")
        if indicators["pyproject_toml"]:
            py_text += "\n" + (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
        lowered = py_text.lower()
        if "typer" in lowered or "click" in lowered:
            frameworks.append("python-cli")
        if "django" in lowered:
            frameworks.append("django")
        if "fastapi" in lowered:
            frameworks.append("fastapi")
        if "flask" in lowered:
            frameworks.append("flask")
        if "torch" in lowered:
            frameworks.append("pytorch")
        if "tensorflow" in lowered:
            frameworks.append("tensorflow")
    if indicators["gemfile"]:
        languages.append("ruby")
        package_managers.append("bundler")
        gemfile_text = (root / "Gemfile").read_text(encoding="utf-8", errors="ignore")
        if "rails" in gemfile_text.lower():
            frameworks.append("rails")
    if indicators["go_mod"]:
        languages.append("go")
        package_managers.append("go")
    if indicators["cargo_toml"]:
        languages.append("rust")
        package_managers.append("cargo")
    if indicators["pom_xml"] or indicators["gradle"]:
        languages.append("java")
        package_managers.append("maven" if indicators["pom_xml"] else "gradle")
        if indicators["gradle"]:
            frameworks.append("gradle")
        if indicators["pom_xml"]:
            frameworks.append("maven")
    if indicators["dotnet"]:
        languages.append("dotnet")
        package_managers.append("dotnet")
    if indicators["flutter"]:
        languages.append("dart")
        package_managers.append("flutter")
        frameworks.append("flutter")

    frontend = any(name in frameworks for name in {"react", "vue", "nextjs"}) or (
        indicators["package_json"] and indicators["frontend_src"]
    )
    mobile = indicators["flutter"] or indicators["ios_dir"] or indicators["android_dir"] or "react-native" in frameworks
    data_pipeline = indicators["dbt"] or indicators["airflow"]
    ml = indicators["notebooks"] or any(name in frameworks for name in {"pytorch", "tensorflow"})
    backend = any(name in languages for name in {"python", "ruby", "go", "java", "dotnet"}) or "express" in frameworks

    project_types: list[str] = []
    if mobile:
        project_types.append("mobile-app")
    if ml:
        project_types.append("ml-model")
    if data_pipeline:
        project_types.append("data-pipeline")
    if "python-cli" in frameworks:
        project_types.append("python-cli")
    if frontend and backend:
        project_types.append("web-fullstack")
    elif backend:
        project_types.append("api-service")
    elif frontend:
        project_types.append("web-frontend")
    if indicators["pyproject_toml"] and _exists(root, "skills"):
        project_types.append("agent-workflow")
    if not project_types:
        project_types.append("generic")

    evidence = [key for key, exists in indicators.items() if exists]
    return {
        "schema_version": "1.0",
        "project_name": root.name,
        "project_root": str(root),
        "languages": sorted(dict.fromkeys(languages)),
        "package_managers": sorted(dict.fromkeys(package_managers)),
        "frameworks": sorted(dict.fromkeys(frameworks)),
        "project_types": project_types,
        "tests_present": bool(indicators["tests_dir"]),
        "docker_present": bool(indicators["dockerfile"] or indicators["compose"]),
        "ci_present": bool(indicators["github_actions"]),
        "indicators": indicators,
        "source_evidence": evidence,
    }
