"""Lightweight Beacon skill config reader/writer.

This module intentionally avoids external YAML dependencies. It supports the
small YAML subset needed by Beacon's skill/runner configuration:

- mappings via `key: value` and `key:`
- nested objects by indentation (2+ spaces)
- sequences via `- item`
- quoted/unquoted scalars
- multiline literal blocks via `|`
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SkillConfigError(ValueError):
    """Raised when a config file cannot be parsed."""


@dataclass
class _Parser:
    lines: list[str]
    index: int = 0

    def _peek(self) -> str | None:
        while self.index < len(self.lines):
            line = self.lines[self.index]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                self.index += 1
                continue
            return line
        return None

    @staticmethod
    def _indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse(self) -> dict[str, Any]:
        node = self._parse_block(0)
        if not isinstance(node, dict):
            raise SkillConfigError("Top-level config must be a mapping")
        return node

    def _parse_block(self, indent: int) -> Any:
        line = self._peek()
        if line is None:
            return {}
        current_indent = self._indent(line)
        if current_indent < indent:
            return {}
        stripped = line[current_indent:]
        if stripped.startswith("- "):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    def _parse_mapping(self, indent: int) -> dict[str, Any]:
        out: dict[str, Any] = {}
        while True:
            line = self._peek()
            if line is None:
                break
            current_indent = self._indent(line)
            if current_indent < indent:
                break
            if current_indent > indent:
                raise SkillConfigError(
                    f"Unexpected indentation at line {self.index + 1}: {line!r}"
                )
            stripped = line[current_indent:]
            if stripped.startswith("- "):
                break
            if ":" not in stripped:
                raise SkillConfigError(
                    f"Expected key/value mapping at line {self.index + 1}: {line!r}"
                )
            key, raw_value = stripped.split(":", 1)
            key = key.strip()
            value = raw_value.strip()
            self.index += 1
            if value == "|":
                out[key] = self._parse_literal_block(indent)
                continue
            if value:
                out[key] = _parse_scalar(value)
                continue
            next_line = self._peek()
            if next_line is None:
                out[key] = {}
                continue
            next_indent = self._indent(next_line)
            if next_indent <= current_indent:
                out[key] = {}
                continue
            out[key] = self._parse_block(next_indent)
        return out

    def _parse_sequence(self, indent: int) -> list[Any]:
        items: list[Any] = []
        while True:
            line = self._peek()
            if line is None:
                break
            current_indent = self._indent(line)
            if current_indent < indent:
                break
            if current_indent > indent:
                raise SkillConfigError(
                    f"Unexpected indentation at line {self.index + 1}: {line!r}"
                )
            stripped = line[current_indent:]
            if not stripped.startswith("- "):
                break
            remainder = stripped[2:].strip()
            self.index += 1
            if not remainder:
                next_line = self._peek()
                if next_line is None:
                    items.append({})
                    continue
                next_indent = self._indent(next_line)
                items.append(self._parse_block(next_indent) if next_indent > current_indent else {})
                continue
            if ":" in remainder and not remainder.startswith(("'", '"')):
                key, raw_value = remainder.split(":", 1)
                key = key.strip()
                raw_value = raw_value.strip()
                item: dict[str, Any] = {}
                if raw_value == "|":
                    item[key] = self._parse_literal_block(indent)
                elif raw_value:
                    item[key] = _parse_scalar(raw_value)
                else:
                    next_line = self._peek()
                    if next_line is None:
                        item[key] = {}
                    else:
                        next_indent = self._indent(next_line)
                        item[key] = self._parse_block(next_indent) if next_indent > current_indent else {}
                next_line = self._peek()
                if next_line is not None and self._indent(next_line) > current_indent:
                    nested = self._parse_mapping(self._indent(next_line))
                    item.update(nested)
                items.append(item)
                continue
            items.append(_parse_scalar(remainder))
        return items

    def _parse_literal_block(self, parent_indent: int) -> str:
        chunks: list[str] = []
        while self.index < len(self.lines):
            line = self.lines[self.index]
            stripped = line.strip()
            if not stripped:
                chunks.append("")
                self.index += 1
                continue
            indent = self._indent(line)
            if indent <= parent_indent:
                break
            chunks.append(line[parent_indent + 2 :])
            self.index += 1
        return "\n".join(chunks).rstrip()


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if value.startswith("0") and value != "0" and not value.startswith("0."):
            raise ValueError
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def load_yaml_like(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    parser = _Parser(text.splitlines())
    data = parser.parse()
    return data if isinstance(data, dict) else {}


def _format_scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return '""'
    if any(ch in text for ch in [":", "#", "{", "}", "[", "]"]) or text.strip() != text:
        return f'"{text}"'
    return text


def dump_yaml_like(data: dict[str, Any], *, indent: int = 0) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            if value:
                lines.append(f"{prefix}{key}:")
                lines.append(dump_yaml_like(value, indent=indent + 2))
            else:
                lines.append(f"{prefix}{key}: {{}}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        lines.append(dump_yaml_like(item, indent=indent + 4))
                    else:
                        lines.append(f"{prefix}  - {_format_scalar(item)}")
        elif isinstance(value, str) and "\n" in value:
            lines.append(f"{prefix}{key}: |")
            for block_line in value.splitlines():
                lines.append(f"{prefix}  {block_line}")
        else:
            lines.append(f"{prefix}{key}: {_format_scalar(value)}")
    return "\n".join(lines)


def write_yaml_like(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml_like(data).rstrip() + "\n", encoding="utf-8")
