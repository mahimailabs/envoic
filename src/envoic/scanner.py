from __future__ import annotations

import os
from pathlib import Path

from .detector import quick_is_environment_dir

TARGET_DIR_NAMES = {".env", ".venv", "env", "venv", ".virtualenv", "virtualenv"}
SKIP_DIR_NAMES = {"node_modules", "__pycache__", ".git", ".hg", ".svn"}
ALLOWED_HIDDEN = {".env", ".venv", ".virtualenv", ".pyenv"}


def _should_skip(name: str) -> bool:
    if name in SKIP_DIR_NAMES:
        return True
    if name.startswith(".") and name not in ALLOWED_HIDDEN:
        return True
    return False


def scan(root: Path, max_depth: int = 5) -> list[Path]:
    root = root.resolve()
    found: list[Path] = []
    seen: set[Path] = set()

    def walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            return

        for entry in entries:
            if not entry.is_dir(follow_symlinks=False):
                continue

            name = entry.name
            if _should_skip(name):
                continue

            dir_path = Path(entry.path)
            is_candidate = (
                name in TARGET_DIR_NAMES
                or (dir_path / "pyvenv.cfg").is_file()
                or (dir_path / "conda-meta").is_dir()
            )

            is_env = quick_is_environment_dir(dir_path)
            if is_candidate or is_env:
                resolved = dir_path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    found.append(resolved)
                if is_env:
                    continue

            walk(dir_path, depth + 1)

    walk(root, 1)
    return sorted(found)
