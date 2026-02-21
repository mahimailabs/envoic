from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import Literal, TypedDict

from .models import ArtifactCategory, ArtifactInfo, ArtifactSummary, SafetyLevel


class ArtifactPattern(TypedDict, total=False):
    name: str
    suffix: str
    type: Literal["dir", "file"]
    category: ArtifactCategory
    safety: SafetyLevel


ARTIFACT_PATTERNS: list[ArtifactPattern] = [
    {
        "name": "__pycache__",
        "type": "dir",
        "category": ArtifactCategory.BYTECODE_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "suffix": ".pyc",
        "type": "file",
        "category": ArtifactCategory.BYTECODE_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "suffix": ".pyo",
        "type": "file",
        "category": ArtifactCategory.BYTECODE_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": ".mypy_cache",
        "type": "dir",
        "category": ArtifactCategory.TOOL_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": ".pytest_cache",
        "type": "dir",
        "category": ArtifactCategory.TOOL_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": ".ruff_cache",
        "type": "dir",
        "category": ArtifactCategory.TOOL_CACHE,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": ".tox",
        "type": "dir",
        "category": ArtifactCategory.TEST_ENV,
        "safety": SafetyLevel.CAREFUL,
    },
    {
        "name": ".nox",
        "type": "dir",
        "category": ArtifactCategory.TEST_ENV,
        "safety": SafetyLevel.CAREFUL,
    },
    {
        "name": "dist",
        "type": "dir",
        "category": ArtifactCategory.BUILD_ARTIFACT,
        "safety": SafetyLevel.USUALLY_SAFE,
    },
    {
        "name": "build",
        "type": "dir",
        "category": ArtifactCategory.BUILD_ARTIFACT,
        "safety": SafetyLevel.USUALLY_SAFE,
    },
    {
        "name": ".eggs",
        "type": "dir",
        "category": ArtifactCategory.BUILD_ARTIFACT,
        "safety": SafetyLevel.USUALLY_SAFE,
    },
    {
        "suffix": ".egg-info",
        "type": "dir",
        "category": ArtifactCategory.BUILD_ARTIFACT,
        "safety": SafetyLevel.CAREFUL,
    },
    {
        "name": ".ipynb_checkpoints",
        "type": "dir",
        "category": ArtifactCategory.COVERAGE_NOTEBOOK,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": "htmlcov",
        "type": "dir",
        "category": ArtifactCategory.COVERAGE_NOTEBOOK,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
    {
        "name": ".coverage",
        "type": "file",
        "category": ArtifactCategory.COVERAGE_NOTEBOOK,
        "safety": SafetyLevel.ALWAYS_SAFE,
    },
]


PATTERN_ORDER: list[str] = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "dist",
    "build",
    ".eggs",
    "*.egg-info",
    ".ipynb_checkpoints",
    "htmlcov",
    ".coverage",
]

SAFETY_TEXT: dict[SafetyLevel, str] = {
    SafetyLevel.ALWAYS_SAFE: "safe to delete",
    SafetyLevel.USUALLY_SAFE: "usually safe",
    SafetyLevel.CAREFUL: "careful",
}

CAREFUL_NOTES: dict[str, str] = {
    "*.egg-info": "Editable installs (pip install -e .) depend on these.",
    ".tox": "Tox environments take significant time to recreate.",
    ".nox": "Nox environments take significant time to recreate.",
}


def is_python_project_dir(parent: Path) -> bool:
    return any(
        (parent / marker).exists()
        for marker in ("pyproject.toml", "setup.py", "setup.cfg")
    )


def _pattern_name(pattern: ArtifactPattern) -> str:
    if "name" in pattern:
        return pattern["name"]
    suffix = pattern["suffix"]
    return f"*{suffix}"


def _matches_pattern(entry: os.DirEntry[str], pattern: ArtifactPattern) -> bool:
    name = entry.name
    target_type = pattern["type"]
    if target_type == "dir" and not entry.is_dir(follow_symlinks=False):
        return False
    if target_type == "file" and not entry.is_file(follow_symlinks=False):
        return False

    if "name" in pattern and name != pattern["name"]:
        return False
    if "suffix" in pattern and not name.endswith(pattern["suffix"]):
        return False
    return True


def match_artifact(entry: os.DirEntry[str], parent: Path) -> ArtifactInfo | None:
    for pattern in ARTIFACT_PATTERNS:
        if not _matches_pattern(entry, pattern):
            continue

        pattern_name = _pattern_name(pattern)
        if pattern_name in {"build", "dist"} and not is_python_project_dir(parent):
            continue

        return ArtifactInfo(
            path=Path(entry.path).resolve(),
            category=pattern["category"],
            safety=pattern["safety"],
            pattern_matched=pattern_name,
        )
    return None


def calculate_path_size(path: Path) -> int:
    try:
        if path.is_symlink():
            return path.lstat().st_size
        if path.is_file():
            return path.stat().st_size
    except OSError:
        return 0

    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for filename in files:
            file_path = Path(root) / filename
            try:
                if file_path.is_symlink():
                    total += file_path.lstat().st_size
                else:
                    total += file_path.stat().st_size
            except OSError:
                continue
    return total


def summarize_artifacts(artifacts: list[ArtifactInfo]) -> list[ArtifactSummary]:
    grouped: dict[tuple[ArtifactCategory, SafetyLevel, str], list[ArtifactInfo]] = (
        defaultdict(list)
    )
    for item in artifacts:
        key = (item.category, item.safety, item.pattern_matched)
        grouped[key].append(item)

    pattern_position = {pattern: idx for idx, pattern in enumerate(PATTERN_ORDER)}
    summaries: list[ArtifactSummary] = []
    for (category, safety, pattern), items in grouped.items():
        total = sum(item.size_bytes or 0 for item in items)
        summaries.append(
            ArtifactSummary(
                category=category,
                safety=safety,
                count=len(items),
                total_size_bytes=total,
                items=sorted(items, key=lambda item: str(item.path)),
                pattern=pattern,
            )
        )
    return sorted(
        summaries,
        key=lambda item: (
            pattern_position.get(item.pattern, 999),
            item.category.value,
            item.pattern,
        ),
    )


def summarize_with_empty_patterns(
    artifacts: list[ArtifactInfo],
) -> list[ArtifactSummary]:
    by_pattern: dict[str, ArtifactSummary] = {
        summary.pattern: summary for summary in summarize_artifacts(artifacts)
    }
    pattern_by_name = {_pattern_name(item): item for item in ARTIFACT_PATTERNS}
    summaries: list[ArtifactSummary] = []
    for pattern_name in PATTERN_ORDER:
        existing = by_pattern.get(pattern_name)
        if existing is not None:
            summaries.append(existing)
            continue
        pattern = pattern_by_name.get(pattern_name)
        if pattern is None:
            continue
        summaries.append(
            ArtifactSummary(
                category=pattern["category"],
                safety=pattern["safety"],
                count=0,
                total_size_bytes=0,
                items=[],
                pattern=pattern_name,
            )
        )
    return summaries
