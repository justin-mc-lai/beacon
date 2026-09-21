#!/usr/bin/env python3
"""v1.6.14 L1 exec-layer tests: truth FSM mermaid + validate + digest (AC-001..004).

Plain assertion script: extra CLI args (pytest -k style) are ignored.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from beacon.utils.truth_fsm import (
    attach_fsm_mermaid,
    compute_fsm_digest,
    parse_truth_fsm,
    render_fsm_mermaid,
    validate_truth_fsm,
)

TRUTH_PATH = Path(__file__).resolve().parent.parent / "docs/beacon/v1.6.14/features/beacon-v1614-fsm-mermaid-validate/truth.md"

VALID_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | rendered | gen_mermaid |
| rendered | validate | states_ok | validated | run_validator |
| validated | digest | behavior_stable | digest_bound | compute_digest |
| digest_bound | freeze | gate_ok | frozen | set_frozen |

**终态：** frozen

## Illegal transitions

- scaffold -> frozen without validate
- fsm 不合法仍 freeze
"""

INVALID_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| scaffold | render | fsm_present | rendered | gen_mermaid |
| rendered | validate | states_ok | ghost_state | run_validator |

**终态：** rendered
"""

# Valid shape, but the end state is only implicit (no explicit declaration) and the
# illegal section is present: must NOT block, only warn (#30 decision).
UNDECLARED_TERMINAL_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| draft | submit | ok | in_review | x |
| in_review | pass | ok | frozen | x |

### invalid / illegal

- illegal: draft → frozen
"""

NO_TERMINAL_FSM = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | go | ok | b | x |
| b | back | ok | a | x |

### invalid / illegal

- illegal: a → a
"""


def test_mermaid_render() -> None:
    fsm = parse_truth_fsm(VALID_FSM)
    assert fsm["five_tuple_present"], "five-tuple not parsed"
    mermaid = render_fsm_mermaid(fsm)
    assert "stateDiagram-v2" in mermaid, "missing stateDiagram-v2 header"
    assert "scaffold --> rendered" in mermaid, "missing transition edge"
    assert "[*] --> scaffold" in mermaid, "missing initial marker"
    assert "frozen --> [*]" in mermaid, "missing terminal marker"


def test_attach_idempotent() -> None:
    first = attach_fsm_mermaid(VALID_FSM)
    assert first["changed"], "mermaid should attach on first pass"
    assert "stateDiagram-v2" in first["markdown"]
    second = attach_fsm_mermaid(first["markdown"])
    assert not second["changed"], "mermaid attach must be idempotent"


def test_validate_legal() -> None:
    fsm = parse_truth_fsm(VALID_FSM)
    result = validate_truth_fsm(fsm)
    assert not result["blocked"], f"legal FSM should pass: {result['findings']}"
    assert result["status"] == "pass"


def test_undeclared_terminal_warns_not_blocks() -> None:
    result = validate_truth_fsm(parse_truth_fsm(UNDECLARED_TERMINAL_FSM), truth_markdown=UNDECLARED_TERMINAL_FSM)
    assert not result["blocked"], f"undeclared terminal must not block: {result['findings']}"
    warn = [f for f in result["findings"] if f["kind"] == "terminal_undeclared"]
    assert warn and warn[0]["severity"] == "warning", result["findings"]


def test_no_terminal_state_warns() -> None:
    result = validate_truth_fsm(parse_truth_fsm(NO_TERMINAL_FSM), truth_markdown=NO_TERMINAL_FSM)
    assert not result["blocked"], f"non-absorbing FSM must warn, not block: {result['findings']}"
    missing = [f for f in result["findings"] if f["kind"] == "fsm_terminal_missing"]
    assert missing and missing[0]["severity"] == "warning", result["findings"]


def test_illegal_prose_is_not_a_machine_edge() -> None:
    md = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | go | ok | b | act |

### invalid / illegal

- a → b without guard（未过校验直接跳转）
"""
    result = validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)
    assert not result["blocked"], f"prose must not become an illegal edge: {result['findings']}"


def test_terminal_suffix_form_is_recognized() -> None:
    md = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| created | pay | ok | paid | x |
| created | timeout | ok | closed | x |

悬空检查：created 有转出；closed/paid 为终态。

### invalid / illegal

- illegal: paid → created
"""
    result = validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)
    assert not result["blocked"], result["findings"]
    warn = [f for f in result["findings"] if f["kind"] == "terminal_undeclared"]
    assert warn == [], f"closed/paid declared via 为终态: {result['findings']}"


def test_validate_illegal_missing() -> None:
    fsm = parse_truth_fsm(
        "## FSM 五元组\n\n| State | Event | Guard | To | Action |\n|-------|-------|-------|-----|--------|\n| a | go | g | b | act |\n"
    )
    result = validate_truth_fsm(fsm)
    assert result["blocked"], "FSM without illegal transitions should block (fail-closed)"
    assert any(f["kind"] == "illegal_slot_missing" for f in result["findings"])


def test_illegal_declared_as_legal() -> None:
    fsm = parse_truth_fsm(
        """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | go | g | b | act |

## Illegal transitions

- illegal: a -> b
"""
    )
    result = validate_truth_fsm(fsm)
    assert result["blocked"], "illegal transition also declared legal should block"
    assert any(f["kind"] == "illegal_declared_as_legal" for f in result["findings"])


def test_digest_behavior_vs_wording() -> None:
    base = parse_truth_fsm(VALID_FSM)
    base_digest = compute_fsm_digest(base)

    wording_changed = VALID_FSM.replace("gen_mermaid", "render_mermaid_diagram")
    wording_digest = compute_fsm_digest(parse_truth_fsm(wording_changed))
    assert base_digest["behavior_digest"] == wording_digest["behavior_digest"], (
        "wording-only change must keep behavior digest stable"
    )
    assert base_digest["wording_digest"] != wording_digest["wording_digest"], (
        "wording change must change wording digest"
    )

    behavior_changed = VALID_FSM.replace("digest_bound | freeze", "digest_bound | publish")
    behavior_digest = compute_fsm_digest(parse_truth_fsm(behavior_changed))
    assert base_digest["behavior_digest"] != behavior_digest["behavior_digest"], (
        "behavior change must change behavior digest"
    )


def test_freeze_gate_fail_closed(tmp_path=None) -> None:
    """AC-004: FSM invalid => freeze gate blocked; non-domain packages skip."""
    from beacon.utils.truth_fsm import build_truth_fsm_gate_payload

    root = Path(__file__).resolve().parent.parent
    gate = build_truth_fsm_gate_payload(root, version="v1.6.14", feature="beacon-v1614-fsm-mermaid-validate")
    assert not gate["blocked"], f"legal FSM gate should pass: {gate['findings']}"

    header = "---\nslug: x\nversion: v1.6.14\ndomain_required: true\n---\n\n"
    ok_gate = build_truth_fsm_gate_payload(root, version="v1.6.14", feature="x", truth_markdown=header + VALID_FSM)
    assert not ok_gate["blocked"], ok_gate["findings"]
    bad_gate = build_truth_fsm_gate_payload(root, version="v1.6.14", feature="x", truth_markdown=header + "no fsm table here")
    assert bad_gate["blocked"] and bad_gate["reason_code"] == "truth_fsm_invalid", bad_gate


def test_attach_does_not_touch_unrelated_mermaid() -> None:
    md = """## Architecture

```mermaid
sequenceDiagram
  A->>B: hello
```

## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| draft | submit | ok | frozen | x |

**终态：** frozen

## FSM mermaid（投影）

```mermaid
stateDiagram-v2
    draft --> STALE : submit (ok)
```
"""
    out = attach_fsm_mermaid(md)
    assert out["changed"] and out["reason_code"] == "mermaid_resynced"
    assert "sequenceDiagram" in out["markdown"], "unrelated mermaid must be preserved"
    assert "draft --> frozen" in out["markdown"]
    assert "STALE" not in out["markdown"]


def test_declared_terminal_absent_warns() -> None:
    md = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| draft | submit | ok | in_review | x |
| in_review | pass | ok | frozn | x |

**终态：** frozen

### invalid / illegal

- illegal: draft → frozn
"""
    result = validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)
    assert not result["blocked"], f"declared-terminal typo is advisory: {result['findings']}"
    assert any(f["kind"] == "terminal_undefined" and f["severity"] == "warning" for f in result["findings"])


def test_blank_transition_target_blocks() -> None:
    md = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | go | ok |  | act |

**终态：** a

### invalid / illegal

- illegal: a → a
"""
    result = validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)
    assert result["blocked"], result["findings"]
    assert any(f["kind"] == "transition_target_missing" for f in result["findings"])


def test_unrelated_invalid_section_is_not_illegal_transitions() -> None:
    md = """## FSM 五元组

| State | Event | Guard | To | Action |
|-------|-------|-------|-----|--------|
| a | go | ok | b | x |

**终态：** b

## Invalid inputs

- reject malformed payload
"""
    result = validate_truth_fsm(parse_truth_fsm(md), truth_markdown=md)
    assert result["blocked"], "missing illegal-transition section must block"
    assert any(f["kind"] == "illegal_slot_missing" for f in result["findings"])


def test_freezed_truth_has_mermaid() -> None:
    if not TRUTH_PATH.exists():
        return
    md = TRUTH_PATH.read_text(encoding="utf-8")
    assert "stateDiagram-v2" in md, "frozen truth.md must carry a stateDiagram-v2 mermaid block"
    attached = attach_fsm_mermaid(md)
    assert not attached["changed"], "frozen truth mermaid should already be attached"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="keyword", default="")
    args, _ = parser.parse_known_args()
    tests = [
        test_mermaid_render,
        test_attach_idempotent,
        test_validate_legal,
        test_undeclared_terminal_warns_not_blocks,
        test_no_terminal_state_warns,
        test_illegal_prose_is_not_a_machine_edge,
        test_terminal_suffix_form_is_recognized,
        test_attach_does_not_touch_unrelated_mermaid,
        test_declared_terminal_absent_warns,
        test_blank_transition_target_blocks,
        test_unrelated_invalid_section_is_not_illegal_transitions,
        test_validate_illegal_missing,
        test_illegal_declared_as_legal,
        test_digest_behavior_vs_wording,
        test_freeze_gate_fail_closed,
        test_freezed_truth_has_mermaid,
    ]
    if args.keyword:
        kw = args.keyword.lower()

        def _kw_match(fn) -> bool:
            name = fn.__name__.lower()
            if kw in name:
                return True
            if kw.endswith("or") and len(kw) > 2 and kw[:-2] in name:
                return True
            first = kw.split("_")[0]
            return bool(first) and first in name

        tests = [fn for fn in tests if _kw_match(fn)]
        if not tests:
            print(f"no test matches -k {args.keyword}")
            return 1
    failures = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
