from __future__ import annotations

from pathlib import Path

import pytest

from envoic.health import (
    HealthCheck,
    check_environment_health,
    format_health_report,
    health_to_dict,
)
from envoic.models import EnvInfo, EnvType


def _touch_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    path.chmod(0o755)


def _make_venv(
    tmp_path: Path,
    name: str,
    *,
    home: Path | None = None,
    with_activate: bool = True,
) -> Path:
    env_path = tmp_path / name / ".venv"
    env_path.mkdir(parents=True)
    (env_path / "pyvenv.cfg").write_text(
        f"home = {home or tmp_path}\nversion = 3.12.1\n",
        encoding="utf-8",
    )

    _touch_executable(env_path / "bin" / "python")
    _touch_executable(env_path / "Scripts" / "python.exe")
    (env_path / "lib" / "python3.12" / "site-packages").mkdir(parents=True)
    (env_path / "Lib" / "site-packages").mkdir(parents=True)

    if with_activate:
        _touch_executable(env_path / "bin" / "activate")
        _touch_executable(env_path / "Scripts" / "activate")

    return env_path


def _env(path: Path) -> EnvInfo:
    return EnvInfo(path=path, env_type=EnvType.VENV)


def test_check_environment_health_ok(tmp_path: Path) -> None:
    env_path = _make_venv(tmp_path, "api")

    check = check_environment_health(_env(env_path))

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_warns_when_activate_script_is_missing(
    tmp_path: Path,
) -> None:
    env_path = _make_venv(tmp_path, "worker", with_activate=False)

    check = check_environment_health(_env(env_path))

    assert check.status == "WARN"
    assert check.issues == ["missing activate script"]


def test_check_environment_health_marks_missing_pyvenv_home_broken(
    tmp_path: Path,
) -> None:
    env_path = _make_venv(tmp_path, "old", home=tmp_path / "missing-python")

    check = check_environment_health(_env(env_path))

    assert check.status == "BROKEN"
    assert check.issues == [
        f"pyvenv.cfg home not found: {tmp_path / 'missing-python'}"
    ]


def test_check_environment_health_does_not_require_pyvenv_cfg_for_conda(
    tmp_path: Path,
) -> None:
    env_path = tmp_path / "conda-env"
    (env_path / "conda-meta").mkdir(parents=True)
    _touch_executable(env_path / "bin" / "python")

    check = check_environment_health(EnvInfo(path=env_path, env_type=EnvType.CONDA))

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_detects_dangling_python_symlink(
    tmp_path: Path,
) -> None:
    env_path = _make_venv(tmp_path, "dangling")
    python_bin = env_path / "bin" / "python"
    python_bin.unlink()
    try:
        python_bin.symlink_to(env_path / "bin" / "missing-python")
    except OSError:
        pytest.skip("symlinks are not available on this platform")

    check = check_environment_health(_env(env_path))

    assert check.status == "BROKEN"
    assert "dangling symlink: bin" in check.issues[0]


def test_format_health_report_counts_statuses(tmp_path: Path) -> None:
    checks = [
        HealthCheck(path=tmp_path / "ok" / ".venv", status="OK", issues=[]),
        HealthCheck(
            path=tmp_path / "warn" / ".venv",
            status="WARN",
            issues=["missing activate script"],
        ),
        HealthCheck(
            path=tmp_path / "broken" / ".venv",
            status="BROKEN",
            issues=["missing python executable"],
        ),
    ]

    report = format_health_report(checks, base_path=tmp_path)

    assert "ENVIRONMENT HEALTH CHECK" in report
    assert "ok" in report
    assert "WARN" in report
    assert "BROKEN" in report
    assert "Healthy: 1 | Warnings: 1 | Broken: 1" in report


def test_health_to_dict_serializes_path(tmp_path: Path) -> None:
    check = HealthCheck(
        path=tmp_path / "api" / ".venv",
        status="WARN",
        issues=["missing activate script"],
    )

    assert health_to_dict(check) == {
        "path": str(tmp_path / "api" / ".venv"),
        "status": "WARN",
        "issues": ["missing activate script"],
    }
