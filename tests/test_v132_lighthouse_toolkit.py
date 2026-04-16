from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from beacon.command_catalog import LABS_COMMANDS, SUPPORTED_SUBCOMMANDS
from beacon.main import app


runner = CliRunner()


def _invoke(args: list[str]):
    return runner.invoke(app, args)


def test_lighthouse_should_be_explicit_labs_surface():
    assert "lighthouse" in LABS_COMMANDS
    assert "lighthouse" in SUPPORTED_SUBCOMMANDS


def test_lighthouse_system_architecture_map_should_write_single_file(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')\n", encoding="utf-8")

    result = _invoke(
        [
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--mode",
            "system-architecture-map",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    output_path = Path(payload["output_path"])
    assert output_path == tmp_path / ".beacon" / "analysis" / "system-architecture-map.md"
    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "# " in text
    assert "## 3. Mermaid Maps" in text
    assert "```mermaid" in text
    assert "## 7. Confirmed Facts" in text
    assert payload["versioned_output_path"] == ""


def test_lighthouse_package_brief_should_write_default_and_versioned_outputs_for_beacon_repo(tmp_path: Path):
    (tmp_path / "beacon").mkdir(parents=True)
    (tmp_path / "beacon" / "__init__.py").write_text('__version__ = "1.3.2"\n', encoding="utf-8")
    (tmp_path / "skills" / "beacon").mkdir(parents=True)
    (tmp_path / "skills" / "beacon" / "SKILL.md").write_text("# Beacon\n", encoding="utf-8")
    (tmp_path / "docs" / "beacon" / "v1.3.2" / "execution").mkdir(parents=True)
    (tmp_path / "docs" / "beacon" / "version-truth.json").write_text(
        json.dumps(
            {
                "runtime_version": "v1.3.2",
                "docs_default_line": "v1.3.2",
                "current_runtime_release_line": "v1.3.2",
                "lines": {"v1.3.2": {"status": "current_runtime_release"}},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (tmp_path / "package_under_test").mkdir()
    (tmp_path / "package_under_test" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "package_under_test" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")

    result = _invoke(
        [
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--mode",
            "package-brief",
            "--target",
            "package_under_test",
            "--version",
            "v1.3.2",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    default_output = Path(payload["output_path"])
    versioned_output = Path(payload["versioned_output_path"])
    assert default_output == tmp_path / ".beacon" / "analysis" / "package-brief-package-under-test.md"
    assert default_output.exists()
    assert versioned_output == tmp_path / "docs" / "beacon" / "v1.3.2" / "execution" / "beacon-toolkit-lighthouse-package-brief-package-under-test.md"
    assert versioned_output.exists()
    text = versioned_output.read_text(encoding="utf-8")
    assert "Package Brief" in text
    assert "## 4. Key Entry Points" in text
    assert "## 8. Inferred Structure" in text


def test_lighthouse_infra_chain_map_should_detect_chain_candidates(tmp_path: Path):
    (tmp_path / "gateway").mkdir()
    (tmp_path / "api").mkdir()
    (tmp_path / "services").mkdir()
    (tmp_path / "worker").mkdir()
    (tmp_path / "storage").mkdir()
    (tmp_path / "docker-compose.yml").write_text("services:\n  api:\n", encoding="utf-8")

    result = _invoke(
        [
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--mode",
            "infra-chain-map",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    output_path = Path(payload["output_path"])
    assert output_path == tmp_path / ".beacon" / "analysis" / "infra-chain-map.md"
    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "Infra Chain Map" in text
    assert "gateway" in text
    assert "service" in text
    assert "queue" in text


def test_lighthouse_feature_slice_should_require_target_and_render_slice(tmp_path: Path):
    feature_dir = tmp_path / "features" / "payments"
    feature_dir.mkdir(parents=True)
    (feature_dir / "__init__.py").write_text("", encoding="utf-8")
    (feature_dir / "service.py").write_text("def run():\n    return True\n", encoding="utf-8")
    (feature_dir / "routes.py").write_text("ROUTES = []\n", encoding="utf-8")
    (feature_dir / "tests.py").write_text("def test_payments():\n    assert True\n", encoding="utf-8")

    missing_target = _invoke(
        [
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--mode",
            "feature-slice",
            "--json",
        ]
    )
    assert missing_target.exit_code != 0

    result = _invoke(
        [
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--mode",
            "feature-slice",
            "--target",
            "features/payments",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    output_path = Path(payload["output_path"])
    assert output_path == tmp_path / ".beacon" / "analysis" / "feature-slice-features-payments.md"
    assert output_path.exists()
    text = output_path.read_text(encoding="utf-8")
    assert "Feature Slice" in text
    assert "features/payments/service.py" in text
    assert "features/payments/routes.py" in text


def test_lighthouse_should_be_available_under_labs_namespace(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = _invoke(
        [
            "labs",
            "lighthouse",
            "--project-root",
            str(tmp_path),
            "--json",
        ]
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["mode"] == "system-architecture-map"
