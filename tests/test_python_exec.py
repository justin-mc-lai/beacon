from pathlib import Path

from beacon.utils.python_exec import (
    ensure_pytest_junit_command,
    normalize_python_invocation,
    normalize_qa_shell_command,
    resolve_python_executable,
)


def test_resolve_python_executable_is_usable() -> None:
    python = resolve_python_executable(Path(__file__).resolve().parents[1])
    assert python
    assert "AI助手" not in python


def test_normalize_python_invocation_rewrites_bare_python() -> None:
    command = normalize_python_invocation("python -m pytest tests/test_truth_integrity.py -q")
    assert command.startswith(resolve_python_executable())
    assert "python -m pytest" not in command or command.startswith(resolve_python_executable())


def test_normalize_qa_shell_command_adds_junit_for_pytest() -> None:
    command = normalize_qa_shell_command("python -m pytest tests/test_truth_integrity.py -q")
    assert "--junitxml" in command
    assert "${BEACON_JUNIT_PATH" in command


def test_ensure_pytest_junit_command_is_idempotent() -> None:
    original = 'python3 -m pytest -q --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"'
    assert ensure_pytest_junit_command(original) == original
