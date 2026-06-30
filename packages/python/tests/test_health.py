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


def test_check_environment_health_warns_when_pyvenv_home_missing(
    tmp_path: Path,
) -> None:
    # A relocated or --copies venv keeps a working interpreter even when the
    # recorded base interpreter directory is gone, so this is a WARN, not BROKEN.
    env_path = _make_venv(tmp_path, "old", home=tmp_path / "missing-python")

    check = check_environment_health(_env(env_path))

    assert check.status == "WARN"
    assert check.issues == [f"pyvenv.cfg home not found: {tmp_path / 'missing-python'}"]


def test_check_environment_health_warns_when_pyvenv_cfg_unreadable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # An unreadable pyvenv.cfg does not stop the interpreter from running.
    env_path = _make_venv(tmp_path, "unreadable")

    def fail_parse(_: Path) -> dict[str, str]:
        raise OSError("permission denied")

    monkeypatch.setattr("envoic.health.parse_pyvenv_cfg", fail_parse)

    check = check_environment_health(_env(env_path))

    assert check.status == "WARN"
    assert check.issues == ["pyvenv.cfg unreadable: permission denied"]


def test_check_environment_health_marks_missing_python_executable_broken(
    tmp_path: Path,
) -> None:
    env_path = tmp_path / "noexe" / ".venv"
    env_path.mkdir(parents=True)
    (env_path / "pyvenv.cfg").write_text(
        f"home = {tmp_path}\nversion = 3.12.1\n", encoding="utf-8"
    )
    _touch_executable(env_path / "bin" / "activate")

    check = check_environment_health(_env(env_path))

    assert check.status == "BROKEN"
    assert check.issues == ["missing python executable"]


def test_check_environment_health_marks_missing_env_directory_broken(
    tmp_path: Path,
) -> None:
    env_path = tmp_path / "missing" / ".venv"

    check = check_environment_health(_env(env_path))

    assert check.status == "BROKEN"
    assert check.issues == ["environment directory missing or not a directory"]


def test_check_environment_health_does_not_require_pyvenv_cfg_for_conda(
    tmp_path: Path,
) -> None:
    env_path = tmp_path / "conda-env"
    (env_path / "conda-meta").mkdir(parents=True)
    _touch_executable(env_path / "bin" / "python")

    check = check_environment_health(EnvInfo(path=env_path, env_type=EnvType.CONDA))

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_finds_conda_interpreter_at_env_root(
    tmp_path: Path,
) -> None:
    # Conda keeps the interpreter at the environment root on Windows
    # (<env>/python.exe), not under bin/ or Scripts/.
    env_path = tmp_path / "conda-win"
    (env_path / "conda-meta").mkdir(parents=True)
    _touch_executable(env_path / "python.exe")

    check = check_environment_health(EnvInfo(path=env_path, env_type=EnvType.CONDA))

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_ok_for_venv_without_pyvenv_cfg(
    tmp_path: Path,
) -> None:
    # Legacy virtualenv-created envs have no pyvenv.cfg yet run fine; the
    # detector still classifies them as VENV, so health must not call them BROKEN.
    env_path = tmp_path / "legacy" / ".venv"
    env_path.mkdir(parents=True)
    _touch_executable(env_path / "bin" / "python")
    _touch_executable(env_path / "bin" / "activate")
    (env_path / "lib" / "python3.8" / "site-packages").mkdir(parents=True)

    check = check_environment_health(_env(env_path))

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_skips_checks_for_dotenv_dir(
    tmp_path: Path,
) -> None:
    # A plain `.env` config directory is not an interpreter environment.
    env_path = tmp_path / "project" / ".env"
    env_path.mkdir(parents=True)
    (env_path / "settings").write_text("KEY=value\n", encoding="utf-8")

    check = check_environment_health(
        EnvInfo(path=env_path, env_type=EnvType.DOTENV_DIR)
    )

    assert check.status == "OK"
    assert check.issues == []


def test_check_environment_health_detects_dangling_python_symlink(
    tmp_path: Path,
) -> None:
    # A POSIX venv exposes the interpreter only at bin/python; if that is a
    # dangling symlink the environment is broken.
    env_path = tmp_path / "dangling" / ".venv"
    env_path.mkdir(parents=True)
    (env_path / "pyvenv.cfg").write_text(
        f"home = {tmp_path}\nversion = 3.12.1\n", encoding="utf-8"
    )
    _touch_executable(env_path / "bin" / "activate")
    python_bin = env_path / "bin" / "python"
    python_bin.parent.mkdir(parents=True, exist_ok=True)
    try:
        python_bin.symlink_to(env_path / "bin" / "missing-python")
    except OSError:
        pytest.skip("symlinks are not available on this platform")

    check = check_environment_health(_env(env_path))

    assert check.status == "BROKEN"
    assert check.issues == [f"dangling symlink: {Path('bin') / 'python'}"]


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
    rows = {
        line.split()[0]: line
        for line in report.splitlines()
        if line.startswith(("ok", "warn", "broken"))
    }

    assert "ENVIRONMENT HEALTH CHECK" in report
    assert "OK" in rows["ok"]
    assert "WARN" in rows["warn"]
    assert "missing activate script" in rows["warn"]
    assert "BROKEN" in rows["broken"]
    assert "missing python executable" in rows["broken"]
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


def test_health_command_exits_nonzero_when_environment_broken(
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    from envoic.cli import app

    env_path = tmp_path / "proj" / ".venv"
    env_path.mkdir(parents=True)
    # Discoverable as a venv (pyvenv.cfg present) but the interpreter is gone.
    (env_path / "pyvenv.cfg").write_text(
        f"home = {tmp_path}\nversion = 3.12.1\n", encoding="utf-8"
    )

    result = CliRunner().invoke(app, ["health", str(tmp_path), "--json"])

    assert result.exit_code == 1
    assert '"status": "BROKEN"' in result.stdout


def test_health_command_exits_zero_for_healthy_environment(
    tmp_path: Path,
) -> None:
    from typer.testing import CliRunner

    from envoic.cli import app

    _make_venv(tmp_path, "healthy")

    result = CliRunner().invoke(app, ["health", str(tmp_path), "--json"])

    assert result.exit_code == 0
    assert '"status": "BROKEN"' not in result.stdout
