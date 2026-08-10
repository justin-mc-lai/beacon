from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from beacon.main import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def _seed_docs(root: Path, version: str = "v1.3.4") -> None:
    base = root / "docs" / "beacon" / version
    (base / "prd").mkdir(parents=True, exist_ok=True)
    (base / "execution").mkdir(parents=True, exist_ok=True)
    (base / "SUMMARY.md").write_text(f"# {version}\n", encoding="utf-8")
    (base / "execution" / "index.md").write_text("# Execution Index\n", encoding="utf-8")


def test_v134_prd_create_should_generate_structured_main_beacon_skeleton(tmp_path: Path) -> None:
    _seed_docs(tmp_path)

    result = _invoke(
        [
            "prd",
            "create",
            "Beacon Runtime Ledger",
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.4",
        ]
    )
    assert result.exit_code == 0, result.stdout

    target = tmp_path / "docs" / "beacon" / "v1.3.4" / "prd" / "beacon-runtime-ledger.md"
    text = target.read_text(encoding="utf-8")
    assert "**Track**: `main`" in text
    assert "## Context" in text
    assert "## 1. 问题" in text
    assert "## 2. 目标" in text
    assert "## 3. 设计原则" in text
    assert "## 4. 范围" in text
    assert "### FR-001" in text
    assert "### AC-001" in text
    assert "## 10. 依赖与开放问题" in text
    assert "## 1. Overview" not in text
    assert "## 8. Timeline" not in text


def test_v134_prd_create_should_generate_parallel_tooling_skeleton_when_line_has_main_prd(tmp_path: Path) -> None:
    _seed_docs(tmp_path)
    existing = (
        tmp_path
        / "docs"
        / "beacon"
        / "v1.3.4"
        / "prd"
        / "beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane.md"
    )
    existing.write_text("# Existing main prd\n", encoding="utf-8")

    feature = "beacon-v1.3.4-structured-prd-generation-and-toolkit-skill-surfacing"
    result = _invoke(
        [
            "prd",
            "create",
            feature,
            "--project",
            str(tmp_path),
            "--version",
            "v1.3.4",
        ]
    )
    assert result.exit_code == 0, result.stdout

    target = (
        tmp_path
        / "docs"
        / "beacon"
        / "v1.3.4"
        / "prd"
        / "beacon-v1-3-4-structured-prd-generation-and-toolkit-skill-surfacing.md"
    )
    text = target.read_text(encoding="utf-8")
    assert "**Track**: `parallel`" in text
    assert "**Scenario**: `tooling_surface`" in text
    assert "命令面、skill surface、模板生成或 friction repair" in text
    assert "## 10. 与主 PRD 的关系" in text
    assert "`beacon-v1-3-4-global-runtime-projection-and-pocketbase-control-plane`" in text
    assert "### FR-001 `prd create` 必须生成结构化骨架" in text
    assert "### AC-003 toolkit skill 在宿主面可发现" in text


def test_v134_skill_pack_should_surface_metadata_toolkit_and_hide_memory_friction_subskill() -> None:
    host_skill = ROOT / "skills" / "beacon" / "SKILL.md"
    text = host_skill.read_text(encoding="utf-8")
    assert "`beacon-toolkit-metadata`" in text
    assert "doctor metadata show" in text
    assert "`beacon-memory-friction-evolution`" not in text

    subskill = ROOT / "skills" / "beacon" / "beacon-toolkit-metadata" / "SKILL.md"
    subskill_text = subskill.read_text(encoding="utf-8")
    assert subskill_text.startswith("---\n")
    assert "name: beacon-toolkit-metadata" in subskill_text
    assert "Keep this skill outside the main workflow by default." in subskill_text
    assert "Do not automatically route into:" in subskill_text

    removed = ROOT / "skills" / "beacon" / "beacon-memory-friction-evolution" / "SKILL.md"
    assert not removed.exists()
