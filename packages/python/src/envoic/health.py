from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict

from .detector import parse_pyvenv_cfg
from .models import EnvInfo, EnvType
from .utils import format_env_display_path

HealthStatus = Literal["OK", "WARN", "BROKEN"]


class HealthCheckDict(TypedDict):
    path: str
    status: HealthStatus
    issues: list[str]


@dataclass(slots=True)
class HealthCheck:
    path: Path
    status: HealthStatus
    issues: list[str]


def _python_candidates(path: Path) -> tuple[Path, ...]:
    return (
        path / "bin" / "python",
        path / "Scripts" / "python.exe",
        # Conda places the interpreter at the environment root on Windows.
        path / "python.exe",
    )


def _activate_candidates(path: Path) -> tuple[Path, ...]:
    return (path / "bin" / "activate", path / "Scripts" / "activate")


def _relative_issue_path(path: Path, candidate: Path) -> str:
    try:
        return str(candidate.relative_to(path))
    except ValueError:
        return str(candidate)


def _existing_python(path: Path) -> Path | None:
    for candidate in _python_candidates(path):
        if candidate.is_file():
            return candidate
    return None


def _python_issues(path: Path) -> list[str]:
    python_bin = _existing_python(path)
    if python_bin is not None:
        if not os.access(python_bin, os.X_OK):
            return [f"not executable: {_relative_issue_path(path, python_bin)}"]
        return []

    # No working interpreter: a dangling symlink explains it better than a
    # bare "missing" message, but only report it once we know nothing works.
    for candidate in _python_candidates(path):
        if candidate.is_symlink():
            return [f"dangling symlink: {_relative_issue_path(path, candidate)}"]

    return ["missing python executable"]


def _pyvenv_warnings(path: Path) -> list[str]:
    pyvenv_cfg = path / "pyvenv.cfg"
    if not pyvenv_cfg.is_file():
        # pyvenv.cfg is optional: legacy virtualenv-created envs run fine
        # without it, and the detector already accepts such environments.
        return []

    try:
        data = parse_pyvenv_cfg(path)
    except OSError as err:
        return [f"pyvenv.cfg unreadable: {err}"]
    home = data.get("home")
    if not home:
        return ["pyvenv.cfg missing home"]

    home_path = Path(home).expanduser()
    if not home_path.exists():
        return [f"pyvenv.cfg home not found: {home}"]

    return []


def _activation_issues(path: Path) -> list[str]:
    if any(candidate.is_file() for candidate in _activate_candidates(path)):
        return []
    return ["missing activate script"]


def check_environment_health(env: EnvInfo) -> HealthCheck:
    if not env.path.is_dir():
        return HealthCheck(
            path=env.path,
            status="BROKEN",
            issues=["environment directory missing or not a directory"],
        )

    # A plain `.env` directory holds dotenv files, not an interpreter, so the
    # venv-shaped checks below do not apply to it.
    if env.env_type == EnvType.DOTENV_DIR:
        return HealthCheck(path=env.path, status="OK", issues=[])

    broken = _python_issues(env.path)
    warnings: list[str] = []
    if env.env_type == EnvType.VENV:
        # pyvenv.cfg and activation scripts are venv concepts; their absence or
        # staleness is informational (WARN), not a broken interpreter (BROKEN).
        warnings.extend(_pyvenv_warnings(env.path))
        warnings.extend(_activation_issues(env.path))

    if broken:
        status: HealthStatus = "BROKEN"
    elif warnings:
        status = "WARN"
    else:
        status = "OK"

    return HealthCheck(path=env.path, status=status, issues=[*broken, *warnings])


def check_environments_health(environments: list[EnvInfo]) -> list[HealthCheck]:
    return [check_environment_health(env) for env in environments]


def health_to_dict(check: HealthCheck) -> HealthCheckDict:
    return {
        "path": str(check.path),
        "status": check.status,
        "issues": list(check.issues),
    }


def _truncate_text(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return f"{text[: width - 3]}..."


def format_health_report(checks: list[HealthCheck], *, base_path: Path) -> str:
    lines = [
        "ENVIRONMENT HEALTH CHECK",
        "-" * 58,
        f"{'Path':<30} {'Status':<6} Issues",
        "-" * 58,
    ]

    for check in sorted(checks, key=lambda item: str(item.path)):
        label = _truncate_text(format_env_display_path(check.path, base_path), 30)
        issues = "; ".join(check.issues) if check.issues else "-"
        lines.append(f"{label:<30} {check.status:<6} {issues}")

    if not checks:
        lines.append("(no environments found)")

    lines.append("-" * 58)
    healthy = sum(1 for check in checks if check.status == "OK")
    warnings = sum(1 for check in checks if check.status == "WARN")
    broken = sum(1 for check in checks if check.status == "BROKEN")
    lines.append(f"Healthy: {healthy} | Warnings: {warnings} | Broken: {broken}")
    return "\n".join(lines)
