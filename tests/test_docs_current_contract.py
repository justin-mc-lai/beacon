from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_should_describe_current_release_line_and_canonical_docs_root():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert '当前发布线：`v1.1.4`' in text
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
    assert 'Skill Version**: v1.1.4' in text
    assert 'CLI Version**: v1.1.4' in text
    assert '- `beacon <subcommand>`（推荐）' in text
    assert 'docs/beacon/{version}/' in text
    assert 'skills/beacon/' in text
    assert 'docs/product/{version}' not in text


def test_claude_should_align_to_current_runtime_version():
    text = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
    assert '<!-- BEACON:VERSION:v1.1.4 -->' in text
    assert 'Runtime target version: `v1.1.4`' in text
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


def test_v114_should_include_evolution_and_skill_standard_docs():
    changelog = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'release' / 'version-evolution-changelog.md'
    alignment = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'execution' / 'skill-standard-alignment.md'
    assert changelog.exists()
    assert alignment.exists()
    assert 'v1.1.4' in changelog.read_text(encoding='utf-8')
    assert 'skills/beacon/' in alignment.read_text(encoding='utf-8')


def test_v114_should_include_latest_feature_usage_guide():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'execution' / 'latest-feature-usage-guide.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'beacon skill' in text
    assert 'beacon implement' in text
    assert 'omx exec --full-auto --cd' in text
    assert 'skills/beacon/scripts/run_beacon.sh' in text


def test_v114_should_include_real_project_recipes():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'execution' / 'real-project-recipes.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'slow-wp' in text
    assert 'rolo' in text
    assert 'service-slice' in text
    assert 'beacon implement run "<feature>"' in text


def test_v114_should_include_faq_and_troubleshooting():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'execution' / 'faq-and-troubleshooting.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'runner_not_configured' in text
    assert 'runner_result_missing' in text
    assert 'runner_result_invalid' in text
    assert 'slow-wp' in text
    assert 'root `SKILL.md`' in text


def test_v114_should_include_comparison_and_feature_solidification_doc():
    guide = ROOT / 'docs' / 'beacon' / 'v1.1.4' / 'execution' / 'beacon-vs-openspec-gsd-comparison.md'
    assert guide.exists()
    text = guide.read_text(encoding='utf-8')
    assert 'OpenSpec' in text
    assert 'Get Shit Done' in text
    assert 'GSD-2' in text
    assert 'delivery kernel' in text
    assert '固化' in text


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
