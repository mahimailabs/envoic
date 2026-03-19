from __future__ import annotations

import sys
from pathlib import Path

import pytest

from envoic.health import check_health
from envoic.models import HealthStatus


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_venv_skeleton(base: Path, *, write_cfg: bool = True, home: str | None = None) -> Path:
    """Create a minimal on-disk venv skeleton under *base* and return its path."""
    venv = base / "testvenv"
    venv.mkdir(parents=True)

    if write_cfg:
        home_value = home if home is not None else str(base)  # default: exists
        # Deliberately omit 'version =' so the version-in-home check is not
        # triggered; tests that need that check write their own pyvenv.cfg.
        cfg_content = (
            f"home = {home_value}\n"
            "implementation = CPython\n"
        )
        (venv / "pyvenv.cfg").write_text(cfg_content, encoding="utf-8")

    return venv


def _add_real_python(venv: Path) -> Path:
    """Add a real (non-symlink) python binary stub and activate script."""
    if sys.platform == "win32":
        scripts = venv / "Scripts"
        scripts.mkdir(exist_ok=True)
        python_bin = scripts / "python.exe"
        python_bin.write_bytes(b"stub")
        (scripts / "activate").write_text("# activate", encoding="utf-8")
    else:
        bin_dir = venv / "bin"
        bin_dir.mkdir(exist_ok=True)
        python_bin = bin_dir / "python"
        python_bin.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        python_bin.chmod(0o755)
        (bin_dir / "activate").write_text("# activate", encoding="utf-8")
    return python_bin


# ── Tests: Healthy environment ─────────────────────────────────────────────────

class TestHealthyEnv:
    def test_status_is_ok(self, tmp_path: Path) -> None:
        """A well-formed venv with a valid python binary reports OK."""
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        _add_real_python(venv)

        result = check_health(venv)

        assert result.status == HealthStatus.OK
        assert result.issues == []

    def test_path_recorded(self, tmp_path: Path) -> None:
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        _add_real_python(venv)

        result = check_health(venv)

        assert result.path == venv


# ── Tests: Broken — dangling symlink ──────────────────────────────────────────

@pytest.mark.skipif(sys.platform == "win32", reason="symlink test is POSIX-only")
class TestDanglingSymlink:
    def test_broken_status(self, tmp_path: Path) -> None:
        """bin/python pointing at a non-existent target → BROKEN."""
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        bin_dir = venv / "bin"
        bin_dir.mkdir()
        python_link = bin_dir / "python"
        python_link.symlink_to("/non/existent/python3.11")
        (bin_dir / "activate").write_text("# activate", encoding="utf-8")

        result = check_health(venv)

        assert result.status == HealthStatus.BROKEN

    def test_issue_message_mentions_dangling(self, tmp_path: Path) -> None:
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        bin_dir = venv / "bin"
        bin_dir.mkdir()
        (bin_dir / "python").symlink_to("/nowhere/python3")
        (bin_dir / "activate").write_text("# activate", encoding="utf-8")

        result = check_health(venv)

        assert any("dangling" in issue for issue in result.issues)


# ── Tests: Broken — missing pyvenv.cfg home path ──────────────────────────────

class TestMissingHome:
    def test_broken_when_home_missing(self, tmp_path: Path) -> None:
        """pyvenv.cfg home= pointing at a path that doesn't exist → BROKEN."""
        venv = _make_venv_skeleton(tmp_path, home="/totally/missing/python/dir")
        _add_real_python(venv)

        result = check_health(venv)

        assert result.status == HealthStatus.BROKEN

    def test_issue_mentions_home(self, tmp_path: Path) -> None:
        venv = _make_venv_skeleton(tmp_path, home="/totally/missing/python/dir")
        _add_real_python(venv)

        result = check_health(venv)

        assert any("home" in issue for issue in result.issues)


# ── Tests: Warning — missing activate script ──────────────────────────────────

class TestMissingActivate:
    def test_warn_status(self, tmp_path: Path) -> None:
        """Python binary OK but activate missing → WARN (not BROKEN)."""
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))

        if sys.platform == "win32":
            scripts = venv / "Scripts"
            scripts.mkdir()
            python_bin = scripts / "python.exe"
            python_bin.write_bytes(b"stub")
            # deliberately omit activate
        else:
            bin_dir = venv / "bin"
            bin_dir.mkdir()
            python_bin = bin_dir / "python"
            python_bin.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            python_bin.chmod(0o755)
            # deliberately omit activate

        result = check_health(venv)

        assert result.status == HealthStatus.WARN

    def test_issue_mentions_activate(self, tmp_path: Path) -> None:
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        if sys.platform == "win32":
            scripts = venv / "Scripts"
            scripts.mkdir()
            (scripts / "python.exe").write_bytes(b"stub")
        else:
            bin_dir = venv / "bin"
            bin_dir.mkdir()
            python_bin = bin_dir / "python"
            python_bin.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            python_bin.chmod(0o755)

        result = check_health(venv)

        assert any("activate" in issue for issue in result.issues)


# ── Tests: Broken — python binary entirely absent ─────────────────────────────

class TestMissingPythonBinary:
    def test_broken_when_no_binary(self, tmp_path: Path) -> None:
        """No python binary at all → BROKEN."""
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))
        # No bin/python or Scripts/python.exe created

        result = check_health(venv)

        assert result.status == HealthStatus.BROKEN

    def test_issue_mentions_not_found(self, tmp_path: Path) -> None:
        venv = _make_venv_skeleton(tmp_path, home=str(tmp_path))

        result = check_health(venv)

        assert any("not found" in issue for issue in result.issues)
