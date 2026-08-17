"""Entrypoint parity tests between beacon.main and beacon package app."""

from __future__ import annotations

from typer.testing import CliRunner

from beacon import __version__, app as package_app


runner = CliRunner()


def test_package_app_version_flag_should_be_boolean_and_eager():
    result = runner.invoke(package_app, ["--version"])
    assert result.exit_code == 0
    assert str(__version__) in result.stdout
