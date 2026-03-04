.PHONY: qa9-strict-acceptance preflight

qa9-strict-acceptance:
	bash scripts/ci/qa9_strict_acceptance.sh

preflight:
	bash scripts/ci/preflight_gate.sh

