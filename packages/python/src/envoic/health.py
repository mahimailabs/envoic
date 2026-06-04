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
    return (path / "bin" / "python", path / "Scripts" / "python.exe")


def _activate_candidates(path: Path) -> tuple[Path, ...]:
    return (path / "bin" / "activate", path / "Scripts" / "activate")


def _relative_issue_path(path: Path, candidate: Path) -> str:
    try:
        return str(candidate.relative_to(path))
    except ValueError:
        return str(candidate)


def _existing_python(path: Path) -> Path | None:
    for candidate in _python_candidates(path):
        if candidate.exists():
            return candidate
    return None


def _python_issues(path: Path) -> list[str]:
    issues: list[str] = []
    for candidate in _python_candidates(path):
        if candidate.is_symlink() and not candidate.exists():
            issues.append(f"dangling symlink: {_relative_issue_path(path, candidate)}")
            return issues

    python_bin = _existing_python(path)
    if python_bin is None:
        issues.append("missing python executable")
    elif not os.access(python_bin, os.X_OK):
        issues.append(f"not executable: {_relative_issue_path(path, python_bin)}")

    return issues


def _pyvenv_issues(path: Path) -> list[str]:
    pyvenv_cfg = path / "pyvenv.cfg"
    if not pyvenv_cfg.is_file():
        return ["missing pyvenv.cfg"]

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

    broken = _python_issues(env.path)
    warnings: list[str] = []
    if env.env_type != EnvType.CONDA:
        broken.extend(_pyvenv_issues(env.path))
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
    return {"path": str(check.path), "status": check.status, "issues": check.issues}


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
