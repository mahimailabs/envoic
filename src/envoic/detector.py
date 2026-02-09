from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import EnvInfo, EnvType

_PYTHON_DIR_RE = re.compile(r"^python(?P<version>\d+\.\d+)$")


def _existing_paths(path: Path, candidates: list[str]) -> list[Path]:
    found: list[Path] = []
    for candidate in candidates:
        candidate_path = path / candidate
        if candidate_path.exists():
            found.append(candidate_path)
    return found


def parse_pyvenv_cfg(path: Path) -> dict[str, str]:
    cfg_path = path / "pyvenv.cfg"
    if not cfg_path.is_file():
        return {}

    data: dict[str, str] = {}
    for line in cfg_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip().lower()] = value.strip()
    return data


def _find_site_packages_dir(path: Path) -> Path | None:
    direct_candidates = [
        path / "Lib" / "site-packages",
        path / "lib" / "site-packages",
    ]
    for candidate in direct_candidates:
        if candidate.is_dir():
            return candidate

    for lib_root in (path / "lib", path / "Lib"):
        if not lib_root.is_dir():
            continue
        for child in lib_root.iterdir():
            if not child.is_dir():
                continue
            match = _PYTHON_DIR_RE.match(child.name)
            if not match:
                continue
            site_packages = child / "site-packages"
            if site_packages.is_dir():
                return site_packages
    return None


def _extract_python_version(
    path: Path,
    pyvenv_data: dict[str, str],
    *,
    allow_subprocess_probe: bool,
) -> str | None:
    for key in ("version", "version_info", "python-version"):
        value = pyvenv_data.get(key)
        if value:
            return value

    site_packages = _find_site_packages_dir(path)
    if site_packages and site_packages.parent.name.startswith("python"):
        return site_packages.parent.name.removeprefix("python")

    if not allow_subprocess_probe:
        return None

    python_bin = _python_executable(path)
    if python_bin is None:
        return None

    try:
        result = subprocess.run(
            [str(python_bin), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except OSError:
        return None

    output = (result.stdout or result.stderr).strip()
    if not output:
        return None

    parts = output.split()
    if len(parts) >= 2:
        return parts[-1]
    return output


def _python_executable(path: Path) -> Path | None:
    for candidate in (path / "bin" / "python", path / "Scripts" / "python.exe"):
        if candidate.is_file():
            return candidate
    return None


def _has_activate_script(path: Path) -> bool:
    return any(candidate.is_file() for candidate in (path / "bin" / "activate", path / "Scripts" / "activate"))


def _calculate_size_bytes(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for filename in files:
            file_path = Path(root) / filename
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total


def _count_packages(path: Path) -> int | None:
    site_packages = _find_site_packages_dir(path)
    if site_packages is None:
        return None

    count = 0
    for entry in site_packages.iterdir():
        if entry.name.endswith(".dist-info") or entry.name.endswith(".egg-info"):
            count += 1
    return count


def list_top_packages(path: Path, limit: int = 10) -> list[str]:
    site_packages = _find_site_packages_dir(path)
    if site_packages is None:
        return []

    packages: list[str] = []
    for entry in site_packages.iterdir():
        if entry.name.endswith(".dist-info"):
            packages.append(entry.name.split("-", 1)[0])
        elif entry.name.endswith(".egg-info"):
            packages.append(entry.name.removesuffix(".egg-info"))

    unique_sorted = sorted(set(packages))
    return unique_sorted[:limit]


def quick_is_environment_dir(path: Path) -> bool:
    if (path / "pyvenv.cfg").is_file():
        return True
    if (path / "conda-meta").is_dir():
        return True
    if _python_executable(path) and _find_site_packages_dir(path):
        return True
    if _has_activate_script(path):
        return True
    return False


def detect_environment(
    path: Path,
    *,
    deep: bool = False,
    stale_days: int = 90,
    include_dotenv: bool = False,
) -> EnvInfo:
    path = path.resolve()
    signals: list[str] = []

    pyvenv_data = parse_pyvenv_cfg(path)
    has_pyvenv_cfg = bool(pyvenv_data)
    if has_pyvenv_cfg:
        signals.append("pyvenv.cfg")

    conda_meta = (path / "conda-meta").is_dir()
    if conda_meta:
        signals.append("conda-meta")

    has_python_bin = _python_executable(path) is not None
    has_site_packages = _find_site_packages_dir(path) is not None
    if has_python_bin:
        signals.append("python-binary")
    if has_site_packages:
        signals.append("site-packages")
    if has_python_bin and has_site_packages:
        signals.append("python+site-packages")

    if _has_activate_script(path):
        signals.append("activate-script")

    definitive_venv = has_pyvenv_cfg or (has_python_bin and has_site_packages)
    strong_venv = _has_activate_script(path) or has_site_packages

    basename = path.name

    env_type = EnvType.UNKNOWN
    if conda_meta:
        env_type = EnvType.CONDA
    elif definitive_venv or strong_venv:
        env_type = EnvType.VENV
    elif basename == ".env":
        env_type = EnvType.DOTENV_DIR

    now = datetime.now(timezone.utc)
    try:
        stat = path.stat()
        created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    except OSError:
        created = None
        modified = None

    is_stale = False
    if modified is not None:
        is_stale = modified < (now - timedelta(days=stale_days))

    if env_type == EnvType.DOTENV_DIR and not include_dotenv:
        signals.append("dotenv-dir")

    python_version = _extract_python_version(
        path,
        pyvenv_data,
        allow_subprocess_probe=deep,
    )

    size_bytes = _calculate_size_bytes(path) if deep else None
    package_count = _count_packages(path) if deep else None

    return EnvInfo(
        path=path,
        env_type=env_type,
        python_version=python_version,
        size_bytes=size_bytes,
        created=created,
        modified=modified,
        package_count=package_count,
        is_stale=is_stale,
        has_pyvenv_cfg=has_pyvenv_cfg,
        signals=signals,
    )


def activation_hint(path: Path, env_type: EnvType) -> str:
    if env_type == EnvType.CONDA:
        return f"conda activate {path.name}"

    if (path / "Scripts" / "activate").exists():
        return f"{path / 'Scripts' / 'activate'}"
    return f"source {path / 'bin' / 'activate'}"
