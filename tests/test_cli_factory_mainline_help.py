from beacon.cli_factory import build_app


def test_cli_factory_help_should_align_with_current_7_plus_3_boundary():
    app = build_app(package_version="1.3.6")

    assert "Mainline: prd -> user-story -> test-case -> implement -> qa -> release" in app.info.help
    assert "prototype adapts accepted UI/UX results" in app.info.help
    assert "Support: help | status | doctor" in app.info.help
    assert "think -> user-story -> prd" not in app.info.help
    assert "gate -> release" not in app.info.help
