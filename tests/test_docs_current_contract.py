from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_should_describe_current_release_line_and_canonical_docs_root():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert '当前发布线：`v1.1.7`' in text
    assert '`docs/beacon/` 是唯一维护的信息源' in text
    assert '`.beacon/` 是运行时状态，不替代正式交付文档' in text
    assert 'pypi.org/project/beacon/' in text
    assert 'pip install beacon' in text
    assert 'pip install beacon-cli' not in text
    assert '`beacon <subcommand>`' in text
    assert '`skills/beacon/`' in text
    assert '### v1.0.0 功能特性' not in text
    assert '### v1.0.1 最小补齐' not in text
    assert 'beacon-workflow start' not in text
    assert 'beacon-think start' not in text
    assert 'docs/product/' not in text
    assert '### Quick Start / 30-second path' in text
    assert 'beacon ask "Create a release-ready requirement package" --project-root . --version v1.1.7 --plan-only --json' in text
    assert '### Command Docs / 命令文档入口' in text
    assert 'docs/beacon/v1.1.7/COMMANDS.md' in text
    assert 'docs/beacon/v1.1.7/getting-started-10-minutes.md' in text
    for heading in [
        '## 1. 当前版本是什么',
        '## 2. 当前能力边界',
        '## 3. 当前推荐命令',
        '## 4. 当前交付工件',
        '## 5. 当前验证命令',
        '## 6. 后续迭代版本文档编写约定',
    ]:
        assert heading in text


def test_skill_should_prefer_beacon_subcommand_and_docs_beacon_output():
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    assert 'Skill Version**: v1.1.7' in text
    assert 'CLI Version**: v1.1.7' in text
    assert '- `beacon <subcommand>`（推荐）' in text
    assert 'docs/beacon/{version}/' in text
    assert 'skills/beacon/' in text
    assert 'docs/product/{version}' not in text


def test_claude_should_align_to_current_runtime_version():
    text = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
    assert '<!-- BEACON:VERSION:v1.1.7 -->' in text
    assert 'Runtime target version: `v1.1.7`' in text
    assert '`docs/beacon/<version>/` is the canonical source of truth.' in text
    assert '`beacon skill list`' in text
    assert '`beacon implement list-runners --json`' in text
    assert '`beacon implement run "<feature>" --version <version> --runner <runner>`' in text
    assert 'beacon skill list' in text
    assert 'beacon implement list-runners --json' in text


def test_acceptance_audit_doc_should_be_marked_as_snapshot():
    beacon_doc = ROOT / 'docs' / 'beacon' / 'v1.1.3' / 'execution' / 'readme-rewrite-draft.md'
    text = beacon_doc.read_text(encoding='utf-8')
    assert 'Beacon README 重写草案' in text
    assert '以下是 Beacon 根 README 的 **v1.1.3 草案口径**。' in text


def test_documentation_guidelines_should_exist_for_future_iterations():
    beacon_doc = ROOT / 'docs' / 'beacon' / 'v1.1.3' / 'execution' / 'readme-rewrite-draft.md'
    assert beacon_doc.exists()
    text = beacon_doc.read_text(encoding='utf-8')
    assert '根 README 只保留 5 类当前信息' in text
    assert 'docs/beacon/<version>/' in text
    assert 'docs/product/<version>/' not in text


def test_v115_should_include_current_execution_and_release_docs():
    release = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'release' / 'v1.1.7.md'
    index_doc = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'index.md'
    assert release.exists()
    assert index_doc.exists()
    assert 'v1.1.7' in release.read_text(encoding='utf-8')
    assert '.machine' in index_doc.read_text(encoding='utf-8')


def test_v115_should_include_memory_and_doctor_docs():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'memory-architecture-and-projection.md'
    repair = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'doctor-repair-scope.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'memory' in text.lower()
    assert repair.exists()
    assert '.machine' in repair.read_text(encoding='utf-8')


def test_v115_should_include_eval_lab_docs():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'eval-lab-benchmark-surface.md'
    policy = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'keep-discard-policy.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'benchmark' in text.lower()
    assert policy.exists()
    assert 'keep' in policy.read_text(encoding='utf-8').lower()


def test_v115_should_include_command_reference_and_scenario_quick_reference():
    command_ref = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'command-reference.md'
    scenario_ref = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'scenario-quick-reference.md'
    assert command_ref.exists()
    assert scenario_ref.exists()

    command_text = command_ref.read_text(encoding='utf-8')
    scenario_text = scenario_ref.read_text(encoding='utf-8')

    assert 'Full command tree' in command_text
    assert 'beacon doctor repair-package --project-root . --version v1.1.7 --json' in command_text
    assert 'beacon labs analyze create' in command_text
    assert 'beacon team start' in command_text

    assert 'I need release readiness / gate evidence' in scenario_text
    assert 'beacon workflow start "<feature>" --project . --version v1.1.7' in scenario_text
    assert 'beacon prompt optimize "<goal>" --project-root . --version v1.1.7 --json' in scenario_text


def test_v115_should_include_external_readme_style_and_bilingual_command_guides():
    readme_guide = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'command-guide-readme.md'
    bilingual_guide = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'execution' / 'command-reference-bilingual.md'
    assert readme_guide.exists()
    assert bilingual_guide.exists()

    readme_text = readme_guide.read_text(encoding='utf-8')
    bilingual_text = bilingual_guide.read_text(encoding='utf-8')

    assert 'External-user README-style guide' in readme_text
    assert 'The 5 commands most users need first' in readme_text
    assert 'beacon gate check release --project-root . --version v1.1.7 --json' in readme_text

    assert 'What Beacon is / Beacon 是什么' in bilingual_text
    assert 'High-frequency commands / 高频命令' in bilingual_text
    assert 'Human vs machine reading order / 人类与机器的阅读顺序' in bilingual_text


def test_v115_should_include_commands_hub_and_beginner_quickstart():
    commands_hub = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'COMMANDS.md'
    quickstart = ROOT / 'docs' / 'beacon' / 'v1.1.7' / 'getting-started-10-minutes.md'
    assert commands_hub.exists()
    assert quickstart.exists()

    commands_text = commands_hub.read_text(encoding='utf-8')
    quickstart_text = quickstart.read_text(encoding='utf-8')

    assert 'single human-primary entrypoint' in commands_text
    assert 'getting-started-10-minutes.md' in commands_text
    assert 'execution/command-reference-bilingual.md' in commands_text

    assert 'Getting Started in 10 Minutes' in quickstart_text
    assert 'Minute 8: Check release readiness' in quickstart_text
    assert 'beacon doctor repair-package --project-root . --version v1.1.7 --json' in quickstart_text


def test_v115_should_include_machine_execution_terminal():
    terminal = ROOT / 'docs' / 'beacon' / 'v1.1.7' / '.machine' / 'execution' / 'terminal.json'
    assert terminal.exists()
    text = terminal.read_text(encoding='utf-8')
    assert '"status": "Pass"' in text
    assert '"version": "v1.1.7"' in text


def test_v114_qa_materials_should_only_reference_existing_verification_files():
    targets = [
        ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'prd' / 'beacon-implement-skill-runner.md',
        ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'qa' / 'test-cases' / 'beacon-implement-skill-runner.md',
        ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'qa' / 'test-cases' / 'beacon-implement-skill-runner.ac-test-matrix.json',
        ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'qa' / 'test-cases' / 'beacon-implement-skill-runner.qa9-matrix.json',
    ]
    for doc in targets:
        text = doc.read_text(encoding='utf-8')
        assert 'tests/test_implement_command.py' not in text
        assert 'tests/test_implement_contract.py' not in text
        assert 'tests/test_implement_workflow_integration.py' not in text
        assert 'tests/test_implement_error_paths.py' not in text
        assert 'tests/test_v114_implement_command.py' in text or 'tests/test_v114_workflow_implement_integration.py' in text
