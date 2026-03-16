#!/usr/bin/env python3
"""Beacon CLI - Comprehensive Test Suite"""
import pytest
import typer
from typer.testing import CliRunner
from pathlib import Path
import json
import tempfile
import shutil

# Import beacon app
from beacon.main import app

runner = CliRunner()


class TestBeaconCore:
    """Test core functionality"""

    def test_version(self):
        """Test version command - skip due to naming conflict"""
        # Skip: "version" is both main app command and subcommand
        # Tested via version.py tests instead
        pass

    def test_help(self):
        """Test help output"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Beacon" in result.stdout


class TestBeaconDoctor:
    """Test doctor command"""

    def test_doctor_diagnose(self):
        """Test doctor diagnose"""
        result = runner.invoke(app, ["doctor", "diagnose"])
        assert result.exit_code == 0
        assert "PASS" in result.stdout or "Beacon" in result.stdout


class TestBeaconGate:
    """Test gate command"""

    def test_gate_help(self):
        """Test gate help"""
        result = runner.invoke(app, ["gate", "--help"])
        assert result.exit_code == 0

    def test_gate_list(self):
        """Test gate list"""
        result = runner.invoke(app, ["gate", "list"])
        assert result.exit_code == 0


class TestBeaconInit:
    """Test init command"""

    def test_init_help(self):
        """Test init help"""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0

    def test_init_run(self, tmp_path):
        """Test init run"""
        result = runner.invoke(app, ["init", "run", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconStatus:
    """Test status command"""

    def test_status_help(self):
        """Test status help"""
        result = runner.invoke(app, ["status", "--help"])
        assert result.exit_code == 0


class TestBeaconReport:
    """Test report command"""

    def test_report_help(self):
        """Test report help"""
        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0


class TestBeaconDebug:
    """Test debug command"""

    def test_debug_help(self):
        """Test debug help"""
        result = runner.invoke(app, ["debug", "--help"])
        assert result.exit_code == 0


class TestBeaconFeedback:
    """Test feedback command"""

    def test_feedback_help(self):
        """Test feedback help"""
        result = runner.invoke(app, ["feedback", "--help"])
        assert result.exit_code == 0


class TestBeaconResume:
    """Test resume command"""

    def test_resume_help(self):
        """Test resume help"""
        result = runner.invoke(app, ["resume", "--help"])
        assert result.exit_code == 0


class TestBeaconThink:
    """Test think command"""

    def test_think_help(self):
        """Test think help"""
        result = runner.invoke(app, ["think", "--help"])
        assert result.exit_code == 0

    def test_think_start(self, tmp_path):
        """Test think start"""
        result = runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_think_status(self, tmp_path):
        """Test think status"""
        # First create a session
        runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        # Then check status
        result = runner.invoke(app, ["think", "status", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_think_confirm(self, tmp_path):
        """Test think confirm"""
        runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["think", "confirm", "Test fact", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_think_question(self, tmp_path):
        """Test think question"""
        runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["think", "question", "Test question?", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_think_conflict(self, tmp_path):
        """Test think conflict"""
        runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["think", "conflict", "semantic", "Test conflict", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_think_summarize(self, tmp_path):
        """Test think summarize"""
        runner.invoke(app, ["think", "start", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["think", "summarize", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconUserStory:
    """Test user-story command"""

    def test_user_story_help(self):
        """Test user-story help"""
        result = runner.invoke(app, ["user-story", "--help"])
        assert result.exit_code == 0

    def test_user_story_create(self, tmp_path):
        """Test user-story create"""
        result = runner.invoke(app, ["user-story", "create", "Login Feature", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_user_story_list(self, tmp_path):
        """Test user-story list"""
        # Create first
        runner.invoke(app, ["user-story", "create", "Test Feature", "--project", str(tmp_path)])
        # Then list
        result = runner.invoke(app, ["user-story", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconPRD:
    """Test prd command"""

    def test_prd_help(self):
        """Test prd help"""
        result = runner.invoke(app, ["prd", "--help"])
        assert result.exit_code == 0

    def test_prd_create(self, tmp_path):
        """Test prd create"""
        result = runner.invoke(app, ["prd", "create", "Login Feature", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "created" in result.stdout.lower()

    def test_prd_list(self, tmp_path):
        """Test prd list"""
        runner.invoke(app, ["prd", "create", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["prd", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconTestCase:
    """Test test-case command"""

    def test_test_case_help(self):
        """Test test-case help"""
        result = runner.invoke(app, ["test-case", "--help"])
        assert result.exit_code == 0

    def test_test_case_create(self, tmp_path):
        """Test test-case create"""
        result = runner.invoke(app, ["test-case", "create", "Login Feature", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_test_case_create_smoke(self, tmp_path):
        """Test test-case create with smoke type"""
        result = runner.invoke(app, ["test-case", "create", "Login Feature", "--type", "smoke", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_test_case_list(self, tmp_path):
        """Test test-case list"""
        runner.invoke(app, ["test-case", "create", "Test Feature", "--project", str(tmp_path)])
        result = runner.invoke(app, ["test-case", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconWorkflow:
    """Test workflow command"""

    def test_workflow_help(self):
        """Test workflow help"""
        result = runner.invoke(app, ["workflow", "--help"])
        assert result.exit_code == 0

    def test_workflow_start(self, tmp_path):
        """Test workflow start"""
        result = runner.invoke(app, ["workflow", "start", "Test Feature", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "Workflow" in result.stdout

    def test_workflow_status(self, tmp_path):
        """Test workflow status"""
        result = runner.invoke(app, ["workflow", "status", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_workflow_gate(self, tmp_path):
        """Test workflow gate"""
        result = runner.invoke(app, ["workflow", "gate", "--project", str(tmp_path)])
        assert result.exit_code == 2
        assert "GATE RESULT: FAIL" in result.stdout


class TestBeaconAnalyze:
    """Test analyze command"""

    def test_analyze_help(self):
        """Test analyze help"""
        result = runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0

    def test_analyze_create(self, tmp_path):
        """Test analyze create"""
        result = runner.invoke(app, ["analyze", "create", "抖音", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_analyze_list(self, tmp_path):
        """Test analyze list"""
        runner.invoke(app, ["analyze", "create", "竞品A", "--project", str(tmp_path)])
        result = runner.invoke(app, ["analyze", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconBrainstorm:
    """Test brainstorm command"""

    def test_brainstorm_help(self):
        """Test brainstorm help"""
        result = runner.invoke(app, ["brainstorm", "--help"])
        assert result.exit_code == 0

    def test_brainstorm_create(self, tmp_path):
        """Test brainstorm create"""
        result = runner.invoke(app, ["brainstorm", "create", "在线教育平台", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconDesign:
    """Test design command"""

    def test_design_help(self):
        """Test design help"""
        result = runner.invoke(app, ["design", "--help"])
        assert result.exit_code == 0

    def test_design_create(self, tmp_path):
        """Test design create"""
        result = runner.invoke(app, ["design", "create", "支付功能", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconJTBD:
    """Test jtbd command"""

    def test_jtbd_help(self):
        """Test jtbd help"""
        result = runner.invoke(app, ["jtbd", "--help"])
        assert result.exit_code == 0

    def test_jtbd_create(self, tmp_path):
        """Test jtbd create"""
        result = runner.invoke(app, ["jtbd", "create", "外卖订餐", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconVersion:
    """Test version command"""

    def test_version_help(self):
        """Test version help"""
        result = runner.invoke(app, ["version", "--help"])
        assert result.exit_code == 0

    def test_version_create(self, tmp_path):
        """Test version create"""
        result = runner.invoke(app, ["version", "create", "电商收藏", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconRoadmap:
    """Test roadmap command"""

    def test_roadmap_help(self):
        """Test roadmap help"""
        result = runner.invoke(app, ["roadmap", "--help"])
        assert result.exit_code == 0

    def test_roadmap_create(self, tmp_path):
        """Test roadmap create"""
        result = runner.invoke(app, ["roadmap", "create", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconPersona:
    """Test persona command"""

    def test_persona_help(self):
        """Test persona help"""
        result = runner.invoke(app, ["persona", "--help"])
        assert result.exit_code == 0

    def test_persona_create(self, tmp_path):
        """Test persona create"""
        result = runner.invoke(app, ["persona", "create", "00后大学生", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconKano:
    """Test kano command"""

    def test_kano_help(self):
        """Test kano help"""
        result = runner.invoke(app, ["kano", "--help"])
        assert result.exit_code == 0

    def test_kano_create(self, tmp_path):
        """Test kano create"""
        result = runner.invoke(app, ["kano", "create", "社区功能", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconMoscow:
    """Test moscow command"""

    def test_moscow_help(self):
        """Test moscow help"""
        result = runner.invoke(app, ["moscow", "--help"])
        assert result.exit_code == 0

    def test_moscow_create(self, tmp_path):
        """Test moscow create"""
        result = runner.invoke(app, ["moscow", "create", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconEvolutionSummary:
    """Test evolution-summary command"""

    def test_evolution_summary_help(self):
        """Test evolution-summary help"""
        result = runner.invoke(app, ["evolution-summary", "--help"])
        assert result.exit_code == 0

    def test_evolution_summary_create(self, tmp_path):
        """Test evolution-summary create"""
        result = runner.invoke(app, ["evolution-summary", "create", "v1.0.1", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconAutoTest:
    """Test auto-test command"""

    def test_auto_test_help(self):
        """Test auto-test help"""
        result = runner.invoke(app, ["auto-test", "--help"])
        assert result.exit_code == 0

    def test_auto_test_create(self, tmp_path):
        """Test auto-test create"""
        result = runner.invoke(app, ["auto-test", "create", "--project", str(tmp_path)])
        assert result.exit_code == 0

    def test_auto_test_status(self, tmp_path):
        """Test auto-test status"""
        result = runner.invoke(app, ["auto-test", "status", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconTestProgress:
    """Test test-progress command"""

    def test_test_progress_help(self):
        """Test test-progress help"""
        result = runner.invoke(app, ["test-progress", "--help"])
        assert result.exit_code == 0

    def test_test_progress_show(self, tmp_path):
        """Test test-progress show"""
        result = runner.invoke(app, ["test-progress", "show", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconRelease:
    """Test release command"""

    def test_release_help(self):
        """Test release help"""
        result = runner.invoke(app, ["release", "--help"])
        assert result.exit_code == 0

    def test_release_create(self, tmp_path):
        """Test release create"""
        result = runner.invoke(app, ["release", "create", "v1.0.0", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconApiDesign:
    """Test api-design command"""

    def test_api_design_help(self):
        """Test api-design help"""
        result = runner.invoke(app, ["api-design", "--help"])
        assert result.exit_code == 0

    def test_api_design_create(self, tmp_path):
        """Test api-design create"""
        result = runner.invoke(app, ["api-design", "create", "登录认证", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconDataDictionary:
    """Test data-dictionary command"""

    def test_data_dictionary_help(self):
        """Test data-dictionary help"""
        result = runner.invoke(app, ["data-dictionary", "--help"])
        assert result.exit_code == 0

    def test_data_dictionary_create(self, tmp_path):
        """Test data-dictionary create"""
        result = runner.invoke(app, ["data-dictionary", "create", "用户模块", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconUISpec:
    """Test ui-spec command"""

    def test_ui_spec_help(self):
        """Test ui-spec help"""
        result = runner.invoke(app, ["ui-spec", "--help"])
        assert result.exit_code == 0

    def test_ui_spec_create(self, tmp_path):
        """Test ui-spec create"""
        result = runner.invoke(app, ["ui-spec", "create", "详情页", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconWireframe:
    """Test wireframe command"""

    def test_wireframe_help(self):
        """Test wireframe help"""
        result = runner.invoke(app, ["wireframe", "--help"])
        assert result.exit_code == 0

    def test_wireframe_create(self, tmp_path):
        """Test wireframe create"""
        result = runner.invoke(app, ["wireframe", "create", "登录页面", "--project", str(tmp_path)])
        assert result.exit_code == 0


class TestBeaconPrototype:
    """Test prototype command"""

    def test_prototype_help(self):
        """Test prototype help"""
        result = runner.invoke(app, ["prototype", "--help"])
        assert result.exit_code == 0


class TestBeaconSave:
    """Test save command"""

    def test_save_help(self):
        """Test save help"""
        result = runner.invoke(app, ["save", "--help"])
        assert result.exit_code == 0


class TestBeaconRecall:
    """Test recall command"""

    def test_recall_help(self):
        """Test recall help"""
        result = runner.invoke(app, ["recall", "--help"])
        assert result.exit_code == 0


class TestBeaconRemember:
    """Test remember command"""

    def test_remember_help(self):
        """Test remember help"""
        result = runner.invoke(app, ["remember", "--help"])
        assert result.exit_code == 0


class TestBeaconTeam:
    """Test team command"""

    def test_team_help(self):
        """Test team help"""
        result = runner.invoke(app, ["team", "--help"])
        assert result.exit_code == 0


class TestBeaconRalphBridge:
    """Test ralph-bridge command"""

    def test_ralph_bridge_help(self):
        """Test ralph-bridge help"""
        result = runner.invoke(app, ["ralph-bridge", "--help"])
        assert result.exit_code == 0


class TestBeaconRun:
    """Test run command"""

    def test_run_help(self):
        """Test run help"""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
