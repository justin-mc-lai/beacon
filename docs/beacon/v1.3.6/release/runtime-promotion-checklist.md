# Beacon v1.3.6 Runtime Promotion Checklist

## Status

- Promotion completed.
- `v1.3.6` is now the current Beacon runtime release line.

## Version Truth

- `beacon/__init__.py`
  - `__version__ == "1.3.6"`
  - `__toolkit_version__ == "v1.3.6"`
- `pyproject.toml`
  - `[project].version == "1.3.6"`
- `beacon/version-truth.json`
  - `package_version == "1.3.6"`
  - `runtime_version == "v1.3.6"`
  - `docs_default_line == "v1.3.6"`
  - `current_runtime_release_line == "v1.3.6"`
  - `lines.v1.3.6.status == "current_runtime_release"`

## Content Gates Closed

1. Requirement command convergence is complete
   - `prd / user-story / test-case / prototype` share the host-native semantic runtime contract.

2. Delivery kernel convergence is complete
   - `implement / qa / release` share one delivery contract and traceability plane.

3. Support/read-model convergence is complete
   - `help / status / doctor` consume the same delivery read model.

4. Host-native LLM priority is enforced
   - Codex / Claude host mode no longer requires `BEACON_LLM_API_KEY` by default.

5. Public docs and skills were rewritten to release phrasing
   - root docs, packaged skills, and `docs/beacon/v1.3.6/` now describe `v1.3.6` as the current runtime line.

## Validation Commands

```bash
python3 -m pytest -q \
  tests/test_docs_current_contract.py \
  tests/test_skill_standard_layout.py \
  tests/test_v131_host_skill_pack.py \
  tests/test_skill_command_alignment.py \
  tests/test_v110_docs_examples_contract.py \
  tests/test_compat_regression_docs_examples.py

python3 -m pytest -q \
  tests/test_v136_delivery_kernel_read_model.py \
  tests/test_v136_host_native_requirement_contracts.py \
  tests/test_v135_transactional_runtime_and_prd_compile.py \
  tests/test_v135_qa_team_run_guards.py \
  tests/test_v132_implement_three_modes_functional.py \
  tests/test_v119_release_scorecard_and_browser_compiler.py \
  tests/test_v133_minimal_hud_help_support.py \
  tests/test_doctor_v2_contract.py \
  tests/test_beacon.py \
  tests/test_llm_loop_orchestration.py \
  tests/test_v120_runtime_release_alignment.py \
  tests/test_v120_release_line_alignment.py

beacon gate check release --project-root . --version v1.3.6 --json
beacon release check v1.3.6 --project .
```

## Done Definition

Promotion is considered complete when:

- version-truth files all point to `1.3.6 / v1.3.6`
- docs and skill packaging describe `v1.3.6` as current
- promotion regression and version-alignment tests pass
- release/gate validation is acceptable for the in-repo `v1.3.6` line
