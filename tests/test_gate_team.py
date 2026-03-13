"""Tests for beacon gate and team commands"""
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Import commands
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from beacon.commands.gate import (
    GateMode,
    REASON_CODES,
    check_boundaries,
    check_terminal_artifact,
    check_evidence_chain,
    run_gate_checks,
)
from beacon.commands.team import (
    TeamState,
    TerminalStatus,
    RuntimeMode,
    load_team_state,
    save_team_state,
    advance_state,
)


class TestGate:
    """Test gate command"""

    def test_reason_codes_count(self):
        """Test that we have 25+ reason codes"""
        assert len(REASON_CODES) >= 25, f"Expected 25+ reason codes, got {len(REASON_CODES)}"

    def test_gate_modes(self):
        """Test gate modes are defined"""
        assert GateMode.STRICT.value == "strict"
        assert GateMode.NORMAL.value == "normal"
        assert GateMode.DEBUG.value == "debug"
        assert GateMode.DRY_RUN.value == "dry-run"

    def test_check_boundaries_missing(self, tmp_path):
        """Test boundaries check when file is missing"""
        issues = check_boundaries(tmp_path, GateMode.STRICT)
        assert len(issues) == 1
        assert issues[0]["reason_code"] == "boundaries_missing"
        assert issues[0]["blocked"] == True

    def test_check_boundaries_exists(self, tmp_path):
        """Test boundaries check when file exists"""
        docs_dir = tmp_path / "docs" / "beacon" / "v1.0.0" / "execution"
        docs_dir.mkdir(parents=True)
        (docs_dir / "boundaries.md").write_text("# Boundaries")

        issues = check_boundaries(tmp_path, GateMode.STRICT)
        assert len(issues) == 0

    def test_check_terminal_missing(self, tmp_path):
        """Test terminal check when file is missing"""
        issues = check_terminal_artifact(tmp_path, GateMode.STRICT)
        assert len(issues) == 1
        assert issues[0]["reason_code"] == "terminal_artifact_missing"

    def test_check_terminal_invalid_status(self, tmp_path):
        """Test terminal check with invalid status"""
        docs_dir = tmp_path / "docs" / "beacon" / "v1.0.0" / "execution"
        docs_dir.mkdir(parents=True)
        terminal = {"status": "InvalidStatus", "traceability": {}}
        (docs_dir / "terminal.json").write_text(json.dumps(terminal))

        issues = check_terminal_artifact(tmp_path, GateMode.STRICT)
        status_issues = [i for i in issues if i["reason_code"] == "terminal_status_invalid"]
        assert len(status_issues) == 1

    def test_check_terminal_blocking_question(self, tmp_path):
        """Test terminal check with blocking open question"""
        docs_dir = tmp_path / "docs" / "beacon" / "v1.0.0" / "execution"
        docs_dir.mkdir(parents=True)
        terminal = {
            "status": "Pass",
            "traceability": {},
            "open_questions": [{"id": 1, "question": "Test?", "blocking": True}]
        }
        (docs_dir / "terminal.json").write_text(json.dumps(terminal))

        issues = check_terminal_artifact(tmp_path, GateMode.STRICT)
        blocking_issues = [i for i in issues if i["reason_code"] == "blocking_open_question_exists"]
        assert len(blocking_issues) == 1

    def test_run_gate_checks_blocked(self, tmp_path):
        """Test gate checks returns blocked when issues found"""
        result = run_gate_checks("think", GateMode.STRICT, tmp_path, force=False)
        assert result["status"] == "Blocked"
        assert result["blocked_count"] > 0

    def test_run_gate_checks_force(self, tmp_path):
        """Test force mode logs risk"""
        result = run_gate_checks("think", GateMode.STRICT, tmp_path, force=True)
        # Force should log risk but pass
        risk_file = tmp_path / ".beacon" / "risks.json"
        assert risk_file.exists()


class TestTeam:
    """Test team command"""

    def test_team_states(self):
        """Test team states are defined"""
        assert TeamState.TEAM_PLAN.value == "team-plan"
        assert TeamState.TEAM_PRD.value == "team-prd"
        assert TeamState.TEAM_EXEC.value == "team-exec"
        assert TeamState.TEAM_VERIFY.value == "team-verify"
        assert TeamState.TEAM_FIX.value == "team-fix"
        assert TeamState.TERMINAL.value == "terminal"

    def test_terminal_statuses(self):
        """Test terminal statuses are defined"""
        assert TerminalStatus.PASS.value == "Pass"
        assert TerminalStatus.BLOCKED.value == "Blocked"
        assert TerminalStatus.CANCELLED.value == "Cancelled"

    def test_runtime_modes(self):
        """Test runtime modes are defined"""
        assert RuntimeMode.FILE.value == "file"
        assert RuntimeMode.TMUX.value == "tmux"
        assert RuntimeMode.AUTO.value == "auto"

    def test_load_save_team_state(self, tmp_path):
        """Test loading and saving team state"""
        team_name = "test-team"
        state = {
            "active": True,
            "team_name": team_name,
            "task": "Test task",
            "state": "team-plan",
        }

        save_team_state(tmp_path, team_name, state)

        loaded = load_team_state(tmp_path, team_name)
        assert loaded["active"] == True
        assert loaded["task"] == "Test task"

    def test_advance_state_valid_transition(self, tmp_path):
        """Test valid state transition"""
        state = {"state": "team-plan"}
        result = advance_state(tmp_path, "test", state, "team-prd")
        assert result["state"] == "team-prd"

    def test_advance_state_invalid_transition(self, tmp_path):
        """Test invalid state transition"""
        state = {"state": "team-plan"}
        result = advance_state(tmp_path, "test", state, "team-fix")
        # Should return original state (no transition)
        assert result["state"] == "team-plan"

    def test_team_state_with_workers(self, tmp_path):
        """Test team state with workers"""
        team_name = "test-team"
        state = {
            "active": True,
            "team_name": team_name,
            "task": "Test task",
            "state": "team-plan",
            "workers": [
                {"id": "worker-001", "role": "planner", "status": "idle"},
                {"id": "worker-002", "role": "executor", "status": "idle"},
            ]
        }

        save_team_state(tmp_path, team_name, state)
        loaded = load_team_state(tmp_path, team_name)

        assert len(loaded["workers"]) == 2
        assert loaded["workers"][0]["role"] == "planner"

    def test_review_gates(self, tmp_path):
        """Test review gates structure"""
        team_name = "test-team"
        state = {
            "active": True,
            "team_name": team_name,
            "task": "Test task",
            "state": "team-prd",
            "review_gates": {
                "spec": {"status": "pass", "reviewer": "pm"},
                "quality": {"status": None, "reviewer": None},
            }
        }

        save_team_state(tmp_path, team_name, state)
        loaded = load_team_state(tmp_path, team_name)

        assert loaded["review_gates"]["spec"]["status"] == "pass"
        assert loaded["review_gates"]["quality"]["status"] is None
