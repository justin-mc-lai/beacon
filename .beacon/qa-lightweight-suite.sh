#!/bin/sh
set -eu

python3 -m pytest -q \
  tests/test_v112_implementation_plan_runtime.py \
  tests/test_v114_implement_command.py \
  tests/test_v119_feature_qa_closure.py \
  tests/test_v116_navigator_support.py \
  tests/test_v1311_board_launcher.py \
  tests/test_real_project_validation_command.py \
  --junitxml "${BEACON_JUNIT_PATH:-.beacon/junit.xml}"
