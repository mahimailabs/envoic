from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .artifacts import calculate_path_size, match_artifact
from .detector import quick_is_environment_dir
from .models import ArtifactInfo

TARGET_DIR_NAMES = {".env", ".venv", "env", "venv", ".virtualenv", "virtualenv"}
SKIP_DIR_NAMES = {"node_modules", ".git", ".hg", ".svn"}
ALLOWED_HIDDEN = {
    ".env",
    ".venv",
    ".virtualenv",
    ".pyenv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".eggs",
    ".ipynb_checkpoints",
}


@dataclass(slots=True)
class ScanDiscovery:
    environments: list[Path]
    artifacts: list[ArtifactInfo] = field(default_factory=list)


def _should_skip(name: str) -> bool:
    if name in SKIP_DIR_NAMES:
        return True
    if name.startswith(".") and name not in ALLOWED_HIDDEN:
        return True
    return False


def scan(
    root: Path,
    max_depth: int = 5,
    *,
    include_artifacts: bool = False,
    deep: bool = False,
) -> ScanDiscovery:
    root = root.resolve()
    found: list[Path] = []
    artifacts: list[ArtifactInfo] = []
    seen: set[Path] = set()
    seen_artifacts: set[Path] = set()

    def walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError:
            return

        for entry in entries:
            if include_artifacts:
                artifact = match_artifact(entry, current)
                if artifact is not None:
                    if artifact.path not in seen_artifacts:
                        if deep:
                            artifact.size_bytes = calculate_path_size(artifact.path)
                        seen_artifacts.add(artifact.path)
                        artifacts.append(artifact)
                    if entry.is_dir(follow_symlinks=False):
                        continue

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
    return ScanDiscovery(
        environments=sorted(found),
        artifacts=sorted(artifacts, key=lambda item: str(item.path)),
    )
