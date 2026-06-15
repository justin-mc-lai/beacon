from __future__ import annotations

from pathlib import Path

from beacon.commands.auto_test import (
    _collect_required_file_issues,
    _is_native_compile_test_command,
    _native_toolchain_pass_assertion_count,
    _run_layer_command,
)


def test_is_native_compile_test_command_detects_go_commands():
    assert _is_native_compile_test_command("cd examples/go-todo-crud && go build ./...")
    assert _is_native_compile_test_command("cd pkg && go test -v ./...")
    assert not _is_native_compile_test_command("python3 -m pytest -q")


def test_native_toolchain_pass_assertion_count_for_go_test_ok_line():
    count = _native_toolchain_pass_assertion_count(
        "cd examples/go-todo-crud && go test ./...",
        "ok  \tgithub.com/beacon/examples/go-todo-crud\t(cached)\n",
        "",
    )
    assert count == 1


def _write_minimal_go_module(root: Path) -> None:
    root.joinpath("go.mod").write_text("module example.com/native-toolchain-test\n\ngo 1.22\n", encoding="utf-8")
    root.joinpath("main.go").write_text("package main\n\nfunc main() {}\n", encoding="utf-8")


def test_run_layer_command_writes_synthetic_junit_for_go_build(tmp_path: Path):
    go_dir = tmp_path / "mini-go"
    go_dir.mkdir()
    _write_minimal_go_module(go_dir)
    layer_dir = tmp_path / "contract"
    payload = _run_layer_command(
        layer="contract",
        command=f"cd {go_dir} && go build ./...",
        project_root=tmp_path,
        layer_dir=layer_dir,
        run_id="run-native-toolchain-test",
    )
    assert payload["status"] == "passed"
    assert int(payload.get("assertion_count") or 0) >= 1
    assert payload.get("junit_valid") is True
    junit_path = layer_dir / "junit.xml"
    assert junit_path.exists()
    assert "native_toolchain_pass" in junit_path.read_text(encoding="utf-8")


def test_collect_required_file_issues_ignores_native_contract_pass(tmp_path: Path):
    go_dir = tmp_path / "mini-go"
    go_dir.mkdir()
    _write_minimal_go_module(go_dir)
    layer_dir = tmp_path / "contract"
    payload = _run_layer_command(
        layer="contract",
        command=f"cd {go_dir} && go build ./...",
        project_root=tmp_path,
        layer_dir=layer_dir,
        run_id="run-native-toolchain-issues",
    )
    issues = _collect_required_file_issues(
        project_root=tmp_path,
        layer_results=[payload],
        require_junit=True,
        require_assertion_count=True,
    )
    assert issues == []
