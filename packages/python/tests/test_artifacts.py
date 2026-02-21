from __future__ import annotations

from pathlib import Path

from envoic.artifacts import summarize_artifacts
from envoic.models import ArtifactCategory, SafetyLevel
from envoic.scanner import scan


def _write_bytes(path: Path, size: int = 16) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x" * size)


def test_detect_pycache(tmp_path: Path) -> None:
    _write_bytes(tmp_path / "a" / "__pycache__" / "mod.cpython-311.pyc")
    _write_bytes(tmp_path / "a" / "b" / "__pycache__" / "mod.cpython-312.pyc")

    artifacts = scan(tmp_path, max_depth=5, include_artifacts=True).artifacts
    pycache_dirs = [item for item in artifacts if item.pattern_matched == "__pycache__"]
    assert len(pycache_dirs) == 2
    assert all(
        item.category == ArtifactCategory.BYTECODE_CACHE for item in pycache_dirs
    )


def test_detect_tool_caches(tmp_path: Path) -> None:
    (tmp_path / ".mypy_cache").mkdir()
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".ruff_cache").mkdir()

    artifacts = scan(tmp_path, max_depth=3, include_artifacts=True).artifacts
    patterns = {item.pattern_matched for item in artifacts}
    assert ".mypy_cache" in patterns
    assert ".pytest_cache" in patterns
    assert ".ruff_cache" in patterns
    for item in artifacts:
        if item.pattern_matched in {".mypy_cache", ".pytest_cache", ".ruff_cache"}:
            assert item.category == ArtifactCategory.TOOL_CACHE
            assert item.safety == SafetyLevel.ALWAYS_SAFE


def test_detect_tox_nox(tmp_path: Path) -> None:
    (tmp_path / ".tox").mkdir()
    (tmp_path / ".nox").mkdir()

    artifacts = scan(tmp_path, max_depth=3, include_artifacts=True).artifacts
    by_pattern = {item.pattern_matched: item for item in artifacts}
    assert by_pattern[".tox"].safety == SafetyLevel.CAREFUL
    assert by_pattern[".nox"].safety == SafetyLevel.CAREFUL


def test_build_dist_python_project_only(tmp_path: Path) -> None:
    py_proj = tmp_path / "python_proj"
    py_proj.mkdir()
    (py_proj / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (py_proj / "dist").mkdir()

    non_py_proj = tmp_path / "frontend"
    non_py_proj.mkdir()
    (non_py_proj / "dist").mkdir()

    artifacts = scan(tmp_path, max_depth=4, include_artifacts=True).artifacts
    dist_paths = {item.path for item in artifacts if item.pattern_matched == "dist"}
    assert (py_proj / "dist").resolve() in dist_paths
    assert (non_py_proj / "dist").resolve() not in dist_paths


def test_artifacts_inside_venv_excluded(tmp_path: Path) -> None:
    venv = tmp_path / "project" / ".venv"
    venv.mkdir(parents=True)
    (venv / "pyvenv.cfg").write_text("version = 3.12.0\n", encoding="utf-8")
    _write_bytes(venv / "lib" / "python3.12" / "__pycache__" / "x.pyc")

    discovery = scan(tmp_path, max_depth=6, include_artifacts=True)
    artifact_paths = {item.path for item in discovery.artifacts}
    assert (venv / "lib" / "python3.12" / "__pycache__").resolve() not in artifact_paths


def test_egg_info_suffix_match(tmp_path: Path) -> None:
    egg = tmp_path / "pkg" / "mypkg.egg-info"
    egg.mkdir(parents=True)

    artifacts = scan(tmp_path, max_depth=4, include_artifacts=True).artifacts
    egg_infos = [item for item in artifacts if item.pattern_matched == "*.egg-info"]
    assert len(egg_infos) == 1
    assert egg_infos[0].path == egg.resolve()


def test_no_artifacts_flag(tmp_path: Path) -> None:
    (tmp_path / ".mypy_cache").mkdir()
    discovery = scan(tmp_path, max_depth=3, include_artifacts=False)
    assert discovery.artifacts == []


def test_artifact_summary_rollup(tmp_path: Path) -> None:
    for idx in range(5):
        _write_bytes(tmp_path / f"pkg{idx}" / "__pycache__" / "x.pyc", size=8)

    discovery = scan(tmp_path, max_depth=4, include_artifacts=True, deep=True)
    summary = summarize_artifacts(discovery.artifacts)
    pycache = next(item for item in summary if item.pattern == "__pycache__")
    assert pycache.count == 5
    assert pycache.total_size_bytes > 0
