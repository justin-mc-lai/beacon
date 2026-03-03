"""Tests for `beacon-<subcommand>` prefixed launcher."""

from __future__ import annotations

import pytest
import typer

from beacon import prefixed


def test_resolve_prefixed_subcommand():
    assert prefixed.resolve_prefixed_subcommand("beacon-think") == "think"
    assert (
        prefixed.resolve_prefixed_subcommand("/usr/local/bin/beacon-user-story")
        == "user-story"
    )


def test_resolve_prefixed_subcommand_rejects_unknown():
    assert prefixed.resolve_prefixed_subcommand("beacon-unknown") is None
    assert prefixed.resolve_prefixed_subcommand("think") is None


def test_build_prefixed_args():
    args = prefixed.build_prefixed_args(
        prog_name="beacon-workflow",
        argv=["beacon-workflow", "start", "登录功能", "--auto"],
    )
    assert args == ["workflow", "start", "登录功能", "--auto"]


def test_build_prefixed_args_raises_on_unknown():
    with pytest.raises(typer.BadParameter):
        prefixed.build_prefixed_args(
            prog_name="beacon-unknown",
            argv=["beacon-unknown"],
        )


def test_main_dispatches_to_beacon_app(monkeypatch):
    captured = {}

    def _fake_invoke(args, prog_name):
        captured["args"] = args
        captured["prog_name"] = prog_name

    monkeypatch.setattr(prefixed, "invoke_beacon_app", _fake_invoke)
    monkeypatch.setattr(prefixed.sys, "argv", ["beacon-think", "start", "登录功能"])

    prefixed.main()

    assert captured["args"] == ["think", "start", "登录功能"]
    assert captured["prog_name"] == "beacon-think"
