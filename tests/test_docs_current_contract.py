from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_should_describe_current_release_line_and_canonical_docs_root():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert '当前发布线：`v1.1.1`' in text
    assert '`docs/beacon/` 是唯一维护的信息源' in text
    assert '`beacon <subcommand>`' in text
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
    assert 'Skill Version**: v1.1.1' in text
    assert 'CLI Version**: v1.1.1' in text
    assert '- `beacon <subcommand>`（推荐）' in text
    assert 'docs/beacon/{version}/' in text
    assert 'docs/product/{version}' not in text


def test_acceptance_audit_doc_should_be_marked_as_snapshot():
    beacon_doc = (ROOT / 'docs' / 'beacon' / 'v1.1.1' / 'execution' / 'acceptance-regression-audit.md').read_text(encoding='utf-8')
    assert 'snapshot document' in beacon_doc
    assert 'Final regression command:' in beacon_doc


def test_documentation_guidelines_should_exist_for_future_iterations():
    beacon_doc = ROOT / 'docs' / 'beacon' / 'v1.1.1' / 'execution' / 'documentation-versioning-guidelines.md'
    assert beacon_doc.exists()
    text = beacon_doc.read_text(encoding='utf-8')
    assert 'README 只允许保留以下 5 类当前信息' in text
    assert 'docs/beacon/<version>/' in text
    assert 'docs/product/<version>/' not in text
