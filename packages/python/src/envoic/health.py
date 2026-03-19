from __future__ import annotations

import os
from pathlib import Path

from .detector import parse_pyvenv_cfg
from .models import HealthResult, HealthStatus


def _python_binary_path(env_path: Path) -> Path | None:
    """Return the path to the Python binary inside the venv, if it exists (not checking validity)."""
    for candidate in (
        env_path / "bin" / "python",
        env_path / "Scripts" / "python.exe",
    ):
        # Use lstat so we detect symlinks without following them
        try:
            candidate.lstat()
            return candidate
        except OSError:
            continue
    return None


def _activate_script_path(env_path: Path) -> Path | None:
    """Return the path to the activate script inside the venv, if it exists."""
    for candidate in (
        env_path / "bin" / "activate",
        env_path / "Scripts" / "activate",
    ):
        if candidate.exists():
            return candidate
    return None


def check_health(env_path: Path) -> HealthResult:
    """
    Run health checks on a single Python virtual environment.

    Checks performed:
    - bin/python (or Scripts\\python.exe) exists and is not a dangling symlink
    - bin/python is executable
    - pyvenv.cfg 'home' path exists on disk
    - bin/activate (or Scripts\\activate) exists

    Returns a HealthResult with an overall status (OK / WARN / BROKEN)
    and a list of human-readable issue strings.
    """
    issues: list[str] = []
    status = HealthStatus.OK

    # ── 1. Python binary checks ────────────────────────────────────────────────
    python_bin = _python_binary_path(env_path)

    if python_bin is None:
        issues.append("python binary not found (bin/python or Scripts/python.exe)")
        status = HealthStatus.BROKEN
    else:
        # Check for dangling symlink: lstat succeeds but stat (follow) fails
        try:
            if python_bin.is_symlink():
                try:
                    python_bin.stat()  # follows the symlink
                except OSError:
                    issues.append(f"dangling symlink: {python_bin.relative_to(env_path)}")
                    status = HealthStatus.BROKEN
            else:
                # Not a symlink – just confirm the file still exists
                python_bin.stat()
        except OSError:
            issues.append(f"python binary unreadable: {python_bin.relative_to(env_path)}")
            status = HealthStatus.BROKEN

        # Check executable bit (POSIX only; on Windows all .exe files are executable)
        if status != HealthStatus.BROKEN and os.name != "nt":
            if not os.access(python_bin, os.X_OK):
                issues.append(
                    f"python binary is not executable: {python_bin.relative_to(env_path)}"
                )
                if status == HealthStatus.OK:
                    status = HealthStatus.BROKEN

    # ── 2. pyvenv.cfg home path check ─────────────────────────────────────────
    cfg_data = parse_pyvenv_cfg(env_path)
    home_value = cfg_data.get("home")
    if home_value:
        home_path = Path(home_value)
        if not home_path.exists():
            issues.append(f"pyvenv.cfg home path does not exist: {home_value}")
            if status == HealthStatus.OK:
                status = HealthStatus.BROKEN

    # ── 3. Python version consistency ─────────────────────────────────────────
    version_value = cfg_data.get("version") or cfg_data.get("version_info")
    if version_value and home_value:
        # If the home path doesn't exist we've already flagged it above.
        # Here we only report version mismatch when the home path IS present.
        home_path = Path(home_value)
        if home_path.exists():
            # Check whether the versioned python binary exists in the home dir
            major_minor = ".".join(version_value.split(".")[:2])
            versioned_bin = home_path / f"python{major_minor}"
            plain_bin = home_path / "python3"
            python_exe = home_path / "python.exe"
            if (
                not versioned_bin.exists()
                and not plain_bin.exists()
                and not python_exe.exists()
            ):
                issues.append(
                    f"python {major_minor} not found in home: {home_value}"
                )
                if status == HealthStatus.OK:
                    status = HealthStatus.BROKEN

    # ── 4. Activate script check ───────────────────────────────────────────────
    if _activate_script_path(env_path) is None:
        issues.append("missing activate script (bin/activate or Scripts/activate)")
        if status == HealthStatus.OK:
            status = HealthStatus.WARN

    return HealthResult(
        path=env_path,
        status=status,
        issues=issues,
    )
