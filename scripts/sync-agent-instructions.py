#!/usr/bin/env python3
"""Sync agent adapter files from canonical templates.

Usage:
  python scripts/sync-agent-instructions.py
  python scripts/sync-agent-instructions.py --version 0.1.0
  python scripts/sync-agent-instructions.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS_PACKAGE_JSON = ROOT / "packages/js/package.json"
SKILL_VERSION_TOKEN = "__SKILL_VERSION__"
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([-.][0-9A-Za-z.-]+)?$")

COPIES = [
    (
        ROOT / "skills/envoic/templates/cursor.cursorrules",
        ROOT / ".cursorrules",
    ),
    (
        ROOT / "skills/envoic/templates/copilot-instructions.md",
        ROOT / ".github/copilot-instructions.md",
    ),
    (
        ROOT / "skills/envoic/templates/claude-plugins.yaml",
        ROOT / ".claude-plugin/plugins.yaml",
    ),
    (
        ROOT / "skills/envoic/templates/claude-plugin.json",
        ROOT / ".claude-plugin/plugin.json",
    ),
    (
        ROOT / "skills/envoic/templates/claude-marketplace.json",
        ROOT / ".claude-plugin/marketplace.json",
    ),
    (
        ROOT / "skills/envoic/templates/cursor-rule-envoic.mdc",
        ROOT / ".cursor/rules/envoic.mdc",
    ),
    (
        ROOT / "skills/envoic/templates/copilot-repo.instructions.md",
        ROOT / ".github/instructions/envoic.instructions.md",
    ),
]


def check_only(explicit_version: str | None = None) -> int:
    version = resolve_skill_version(explicit_version)
    print(f"Using skill version: {version}")
    failed = False
    for src, dst in COPIES:
        if not src.exists():
            print(f"missing source template: {src}")
            failed = True
            continue
        if not dst.exists():
            print(f"missing destination file: {dst}")
            failed = True
            continue
        rendered = render_template(src, version)
        if rendered != dst.read_text():
            print(f"out of sync: {dst} (expected to match {src})")
            failed = True
    if failed:
        print("Run: python scripts/sync-agent-instructions.py")
        return 1
    print("Agent instruction files are in sync.")
    return 0


def sync_files(explicit_version: str | None = None) -> int:
    version = resolve_skill_version(explicit_version)
    print(f"Using skill version: {version}")
    for src, dst in COPIES:
        if not src.exists():
            raise FileNotFoundError(f"source template not found: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(render_template(src, version))
        print(f"synced {dst.relative_to(ROOT)}")
    return 0


def parse_release_tag(tag: str) -> str | None:
    if tag.startswith("refs/tags/"):
        tag = tag.removeprefix("refs/tags/")
    if tag.startswith("v"):
        return tag[1:]
    return None


def resolve_skill_version(explicit: str | None = None) -> str:
    if explicit:
        return validate_version(explicit, source="--version")

    for env_key in ("ENVOIC_SKILL_VERSION", "INPUT_VERSION"):
        value = os.getenv(env_key)
        if value:
            return validate_version(value, source=env_key)

    for env_key in ("RELEASE_TAG", "GITHUB_REF_NAME", "GITHUB_REF"):
        value = os.getenv(env_key)
        if not value:
            continue
        parsed = parse_release_tag(value)
        if parsed:
            return validate_version(parsed, source=env_key)

    pkg = json.loads(JS_PACKAGE_JSON.read_text())
    return validate_version(pkg["version"], source=str(JS_PACKAGE_JSON))


def validate_version(value: str, *, source: str) -> str:
    if not SEMVER_PATTERN.match(value):
        raise ValueError(f"invalid skill version from {source}: {value}")
    return value


def render_template(src: Path, version: str) -> str:
    text = src.read_text()
    if SKILL_VERSION_TOKEN in text:
        text = text.replace(SKILL_VERSION_TOKEN, version)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate without writing")
    parser.add_argument(
        "--version",
        help="explicit skill version (semver). If omitted, resolve from env/release tag/package.json",
    )
    args = parser.parse_args()
    if args.check:
        return check_only(args.version)
    return sync_files(args.version)


if __name__ == "__main__":
    raise SystemExit(main())
