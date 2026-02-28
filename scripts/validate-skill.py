#!/usr/bin/env python3
"""Validate envoic skill layout and required metadata."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/envoic/SKILL.md"
CODEX_SKILL = ROOT / ".agents/skills/envoic/SKILL.md"
OPENAI_YAML = ROOT / "skills/envoic/agents/openai.yaml"
PYTHON_CLI = ROOT / "packages/python/src/envoic/cli.py"
JS_CLI = ROOT / "packages/js/src/cli.ts"
EXPECTED_COMMANDS = ("scan", "list", "info", "manage", "clean")
REQUIRED_ADAPTERS = (
    ROOT / ".cursorrules",
    ROOT / ".cursor/rules/envoic.mdc",
    ROOT / ".github/copilot-instructions.md",
    ROOT / ".github/instructions/envoic.instructions.md",
    ROOT / ".claude-plugin/plugins.yaml",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".claude-plugin/marketplace.json",
)


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)


def parse_frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail(f"missing YAML frontmatter in {SKILL}")
    return match.group(1)


def ensure_field(frontmatter: str, field: str) -> None:
    if not re.search(rf"(?m)^{re.escape(field)}\s*:\s*", frontmatter):
        fail(f"missing required frontmatter field '{field}' in {SKILL}")


def main() -> int:
    if not SKILL.exists():
        fail(f"missing {SKILL}")

    text = SKILL.read_text()
    frontmatter = parse_frontmatter(text)
    ensure_field(frontmatter, "name")
    ensure_field(frontmatter, "description")

    if not OPENAI_YAML.exists():
        fail(f"missing {OPENAI_YAML}")

    if not CODEX_SKILL.exists():
        fail(
            "missing .agents/skills/envoic/SKILL.md (expected symlink/copy for Codex auto-discovery)"
        )
    for adapter in REQUIRED_ADAPTERS:
        if not adapter.exists():
            fail(f"missing adapter file: {adapter}")

    if not PYTHON_CLI.exists() or not JS_CLI.exists():
        fail("missing Python/JS CLI files for command validation")
    py_text = PYTHON_CLI.read_text()
    js_text = JS_CLI.read_text()
    for command in EXPECTED_COMMANDS:
        py_marker = (
            f'@app.command(name="{command}")'
            if command == "list"
            else f"def {command}("
        )
        js_marker = f'.command("{command}")'
        if py_marker not in py_text:
            fail(f"expected Python command '{command}' not found in {PYTHON_CLI}")
        if js_marker not in js_text:
            fail(f"expected JS command '{command}' not found in {JS_CLI}")

    print("Skill metadata/layout validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
