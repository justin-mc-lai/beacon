"""v1.4.13 host-response injection tests (issue #3).

Covers the four create-time dispatchers (prd, user-story, test-case,
prototype) and the response-vs-bridge-vs-provider-vs-rule precedence
introduced in v1.4.13.

Six scenarios per command (4 commands × 6 = 24 parametrize cases):

    a. Only ``BEACON_HOST_<CMD>_RESPONSE_JSON`` set, no bridge, no runtime
       -> effective_mode = "host-response", response_used = True
    b. ``BEACON_HOST_<CMD>_RESPONSE_JSON`` AND ``BEACON_HOST_RUNTIME=codex``
       -> effective_mode = "host-response", response_used = True (response wins)
    c. ``BEACON_HOST_<CMD>_RESPONSE_FILE`` set, file path containing valid JSON
       -> effective_mode = "host-response", response_used = True
    d. ``BEACON_HOST_<CMD>_BRIDGE_CMD`` set, no response, runtime supported
       -> effective_mode = "host", response_used = False
    e. Neither response nor bridge, with provider key + runtime supported
       -> effective_mode = "llm" (prd/us/tc) / "host-provider" (prototype),
          response_used = False
    f. Nothing configured (no response, no bridge, no provider, no runtime)
       -> effective_mode = "rule", response_used = False
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from beacon.utils.semantic_runtime import (
    HOST_MODE_BRIDGE,
    HOST_MODE_PROVIDER,
    HOST_MODE_RESPONSE,
    build_semantic_capability_snapshot,
    host_dispatch_decision,
)


# Sentinel that the helper looks for to assert "the response was honoured".
HOST_RESPONSE_SENTINEL = "HOST_RESPONSE_SENTINEL_V1413"
BRIDGE_SENTINEL = "BRIDGE_SENTINEL_V1413"


# Each command maps to the env-var key the dispatcher should consult.
# Note: "prototype" is a single word, so its env key is BEACON_HOST_PROTOTYPE_*.
COMMANDS = ["prd", "user-story", "test-case", "prototype"]


def _command_env_key(command: str) -> str:
    """Map command name to the env-var key fragment beacon uses."""
    return command.upper().replace("-", "_")


def _clear_host_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every BEACON_HOST_* env var the dispatcher may consult."""
    for key in list(os.environ):
        if key.startswith("BEACON_HOST_") or key == "BEACON_LLM_API_KEY":
            monkeypatch.delenv(key, raising=False)


def _set_response_json(monkeypatch: pytest.MonkeyPatch, command: str, payload: dict) -> None:
    key = f"BEACON_HOST_{_command_env_key(command)}_RESPONSE_JSON"
    monkeypatch.setenv(key, json.dumps(payload))


def _set_response_file(monkeypatch: pytest.MonkeyPatch, command: str, payload: dict, tmp_path: Path) -> None:
    key = f"BEACON_HOST_{_command_env_key(command)}_RESPONSE_FILE"
    path = tmp_path / f"response_{command}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv(key, str(path))


def _set_bridge_cmd(
    monkeypatch: pytest.MonkeyPatch, command: str, payload: dict, tmp_path: Path
) -> None:
    """Set BEACON_HOST_<CMD>_BRIDGE_CMD to a python invocation that prints
    the canned bridge payload. We use ``python3 <script>`` rather than a
    shebang so the bridge subprocess does not depend on the script's
    executable bit (which pytest-managed tmp dirs may not have)."""
    key = f"BEACON_HOST_{_command_env_key(command)}_BRIDGE_CMD"
    script = tmp_path / f"beacon_v1413_bridge_{command}.py"
    script.write_text(
        "import json, sys\n"
        f"payload = {json.dumps(payload)}\n"
        "sys.stdout.write(json.dumps(payload))\n"
        "sys.stdout.flush()\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(key, f"{sys.executable} {script}")


def _make_response_payload(command: str) -> dict:
    """Build a payload envelope matching the contract of `command`."""
    sentinel_body = f"# PRD\\n\\n{HOST_RESPONSE_SENTINEL}\\n\\n## 1. 问题\\n- TBD\\n"
    if command == "prd":
        return {"markdown": sentinel_body}
    if command == "user-story":
        return {"story": {"sentinel": HOST_RESPONSE_SENTINEL, "feature": "x"}}
    if command == "test-case":
        return {"test_case": {"sentinel": HOST_RESPONSE_SENTINEL, "rows": []}}
    if command == "prototype":
        return {"sentinel": HOST_RESPONSE_SENTINEL, "frames": []}
    raise AssertionError(f"unknown command {command}")


def _make_bridge_payload(command: str) -> dict:
    """Build a payload envelope that the bridge subprocess will return."""
    body = f"# PRD\\n\\n{BRIDGE_SENTINEL}\\n\\n## 1. 问题\\n- TBD\\n"
    if command == "prd":
        return {"markdown": body}
    if command == "user-story":
        return {"story": {"sentinel": BRIDGE_SENTINEL, "feature": "x"}}
    if command == "test-case":
        return {"test_case": {"sentinel": BRIDGE_SENTINEL, "rows": []}}
    if command == "prototype":
        return {"sentinel": BRIDGE_SENTINEL, "frames": []}
    raise AssertionError(f"unknown command {command}")


# ---------------------------------------------------------------------------
# Per-scenario parametrize
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", COMMANDS)
def test_a_response_json_only_wins(monkeypatch: pytest.MonkeyPatch, command: str) -> None:
    """a. Only response env var set, no bridge, no runtime -> response wins."""
    _clear_host_env(monkeypatch)
    _set_response_json(monkeypatch, command, _make_response_payload(command))

    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    assert decision["mode"] == HOST_MODE_RESPONSE
    assert decision["response_used"] is True
    assert decision["host_transport"] == "injected-response"
    assert decision["response_payload"], "response payload must be non-empty"


@pytest.mark.parametrize("command", COMMANDS)
def test_b_response_with_runtime_still_wins(
    monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    """b. Response env var + BEACON_HOST_RUNTIME=codex both set -> response still wins.

    v1.4.13 regression: pre-fix, the default-bridge subprocess would shadow
    the response. The fix must keep response-first even when the runtime is
    supported and a default bridge is auto-injected.
    """
    _clear_host_env(monkeypatch)
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    _set_response_json(monkeypatch, command, _make_response_payload(command))

    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    assert decision["mode"] == HOST_MODE_RESPONSE
    assert decision["response_used"] is True
    assert decision["host_transport"] == "injected-response"
    # Critically: bridge must NOT have been invoked, even though the snapshot
    # reports host_bridge_command_available=True (the default bridge was
    # auto-injected by ensure_default_host_bridge_env on prd / user_story /
    # test_case create; prototype skips the default to avoid the same bug).
    assert decision["bridge_payload"] == {}
    assert decision["bridge_meta"] == {}


@pytest.mark.parametrize("command", COMMANDS)
def test_c_response_file_wins(
    monkeypatch: pytest.MonkeyPatch, command: str, tmp_path: Path
) -> None:
    """c. Response file path set -> file content used, env-var path bypassed."""
    _clear_host_env(monkeypatch)
    _set_response_file(monkeypatch, command, _make_response_payload(command), tmp_path)

    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    assert decision["mode"] == HOST_MODE_RESPONSE
    assert decision["response_used"] is True
    assert decision["host_transport"] == "injected-response"


@pytest.mark.parametrize("command", COMMANDS)
def test_d_bridge_only_runs_when_no_response(
    monkeypatch: pytest.MonkeyPatch, command: str, tmp_path: Path
) -> None:
    """d. Bridge cmd set, no response -> bridge runs, response_used=False."""
    _clear_host_env(monkeypatch)
    _set_bridge_cmd(monkeypatch, command, _make_bridge_payload(command), tmp_path)
    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    assert decision["mode"] == HOST_MODE_BRIDGE
    assert decision["response_used"] is False
    assert decision["host_transport"] == "command-bridge"
    assert decision["bridge_payload"], "bridge payload must be non-empty"


@pytest.mark.parametrize("command", COMMANDS)
def test_e_no_response_no_bridge_with_provider(
    monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    """e. No response, no bridge, provider key set -> dispatcher reports mode=none.

    The dispatcher itself does NOT call the provider; the provider invocation
    is owned by the command. The helper correctly reports mode=none and lets
    the dispatcher fall through to its own provider branch.
    """
    _clear_host_env(monkeypatch)
    monkeypatch.setenv("BEACON_LLM_API_KEY", "sk-fake-for-test")
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")

    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    # The helper must NOT return a host mode when no response / no bridge.
    # The command's provider branch is the caller's responsibility.
    assert decision["mode"] == "none"
    assert decision["response_used"] is False
    assert decision["response_payload"] == {}
    assert decision["bridge_payload"] == {}


@pytest.mark.parametrize("command", COMMANDS)
def test_f_nothing_configured_yields_none(
    monkeypatch: pytest.MonkeyPatch, command: str
) -> None:
    """f. Nothing configured -> dispatcher returns mode=none (caller falls to rule)."""
    _clear_host_env(monkeypatch)
    # Deliberately do not set BEACON_HOST_RUNTIME either.
    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)

    assert decision["mode"] == "none"
    assert decision["response_used"] is False
    assert decision["response_payload"] == {}
    assert decision["bridge_payload"] == {}
    # And the snapshot itself must report no host transport configured.
    assert snap["host_transport"] == "none"
    assert snap["host_semantic_ready"] is False
    # v1.4.13: response_used must default to False on the snapshot.
    assert snap["response_used"] is False
    # v1.4.13: host_mode_options must be exposed for consumers / docs.
    assert HOST_MODE_RESPONSE in snap["host_mode_options"]
    assert HOST_MODE_BRIDGE in snap["host_mode_options"]
    assert HOST_MODE_PROVIDER in snap["host_mode_options"]


# ---------------------------------------------------------------------------
# Cross-cutting regression: a response injection must NEVER be silently
# shadowed by a bridge invocation, even when the snapshot reports
# host_bridge_command_available=True.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", COMMANDS)
def test_response_never_shadowed_by_default_bridge(
    monkeypatch: pytest.MonkeyPatch, command: str, tmp_path: Path
) -> None:
    """The exact issue #3 regression: ensure the default bridge never
    shadows an injected response."""
    _clear_host_env(monkeypatch)
    # Force the runtime to be supported (so ensure_default_host_bridge_env
    # would inject a default bridge on prd / user_story / test_case).
    monkeypatch.setenv("BEACON_HOST_RUNTIME", "codex")
    # Inject a real response.
    _set_response_json(monkeypatch, command, _make_response_payload(command))

    snap = build_semantic_capability_snapshot(
        command, disable_env=f"BEACON_{_command_env_key(command)}_DISABLE_LLM"
    )
    # Even if the snapshot says a bridge is available, the response wins.
    if snap["host_bridge_command_available"]:
        decision = host_dispatch_decision(command, request_payload={}, capability_snapshot=snap)
        assert decision["mode"] == HOST_MODE_RESPONSE, (
            f"response was shadowed by bridge for {command} (issue #3 regression)"
        )
        assert decision["bridge_payload"] == {}, (
            f"bridge subprocess was invoked despite response for {command}"
        )
