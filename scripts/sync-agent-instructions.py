#!/usr/bin/env python3
"""Sync agent adapter files from canonical templates.

Usage:
  python scripts/sync-agent-instructions.py
  python scripts/sync-agent-instructions.py --check
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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
]


def check_only() -> int:
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
        if src.read_text() != dst.read_text():
            print(f"out of sync: {dst} (expected to match {src})")
            failed = True
    if failed:
        print("Run: python scripts/sync-agent-instructions.py")
        return 1
    print("Agent instruction files are in sync.")
    return 0


def sync_files() -> int:
    for src, dst in COPIES:
        if not src.exists():
            raise FileNotFoundError(f"source template not found: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"synced {dst.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate without writing")
    args = parser.parse_args()
    if args.check:
        return check_only()
    return sync_files()


if __name__ == "__main__":
    raise SystemExit(main())
