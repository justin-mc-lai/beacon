# Beacon v1.3.10 Source Architecture Index

## Source Areas

- `beacon/utils/project_metadata.py`
- `beacon/commands/doctor.py`
- `beacon/utils/material_sync.py`
- `beacon/utils/material_audit.py`
- `beacon/utils/help_support.py`
- `beacon/commands/status.py`
- `beacon/commands/report.py`

## Version Focus

`v1.3.10` 重点收口两类源码改动：

1. 项目版本元信息治理与校验
2. requirement package dual-write gate 与 remediation proof 暴露

## Expected Evidence

- metadata CRUD / verify regression tests
- requirement package gate regression tests
- real-project-validation remediation proof regression tests
