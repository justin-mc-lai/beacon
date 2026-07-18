---
slug: beacon-v2-version-fleet-ops
version: v2.0.0
status: frozen
revision_id: R1
language: zh
domain_required: false
upstream_ref: docs/beacon/v1.6.8/features/beacon-version-fleet-ops-v168/truth.md
parser_contract: beacon-feature-package-v2
---

# beacon-v2-version-fleet-ops

## 人话

v2/Loom 镜像 v1.6.8 `beacon-version-fleet-ops-v168` 运维哲学；实现可复用 Python 直至 Rust 接线。

- 能做：合同与 reason_code 与 v1.6.8 同源
- 不能做：另起矛盾的运维门；默认 BEACON_V2=1
- 怎样算完：parity 声明 + axis 挂载

## User Intent

Parity with v1.6.8 prod-ops.

## Acceptance Criteria

| AC ID | Theme | Description |
|-------|-------|-------------|
| AC-V2-OPS-001 | parity | maps to beacon-version-fleet-ops-v168 AC semantics |
| AC-V2-OPS-002 | axis | mounted on v2 goalrun axis when program updated |

## Non-Goals

- full Loom CLI dual-install in this package alone
