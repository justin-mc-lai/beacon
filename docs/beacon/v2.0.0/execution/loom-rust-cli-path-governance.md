# Loom Rust CLI PATH governance (v2.0.0)

## Decision

- Production: Python `beacon`
- Evolution: Rust `beacon-v2` + brand alias `loom`
- Python package must **not** register console script `loom` (use `loom-py` only)

## Install

```bash
bash scripts/install-loom-cli.sh
bash scripts/install-loom-skills.sh
pip install -e .
export PATH="$HOME/.local/bin:$PATH"
type -a loom
```

## Verify

```bash
file "$(command -v loom)"    # native binary, not Python
head -1 "$(command -v loom)" | grep -v python || true
loom --help
beacon --version
```
