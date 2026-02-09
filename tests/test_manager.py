from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import typer

from envoic.manager import confirm_deletion, delete_environments
from envoic.models import EnvInfo, EnvType


def _env(path: Path, *, stale: bool = False, size_bytes: int | None = None) -> EnvInfo:
    return EnvInfo(
        path=path,
        env_type=EnvType.VENV,
        is_stale=stale,
        size_bytes=size_bytes,
    )


def test_delete_regular_directory(tmp_path: Path) -> None:
    env_dir = tmp_path / "project" / ".venv"
    env_dir.mkdir(parents=True)
    (env_dir / "file.txt").write_text("abc", encoding="utf-8")

    summary = delete_environments([_env(env_dir)], scan_root=tmp_path)

    assert not env_dir.exists()
    assert summary["deleted_count"] == 1
    assert summary["failed_count"] == 0


def test_delete_symlink_only(tmp_path: Path) -> None:
    target = tmp_path / "target_env"
    target.mkdir()
    (target / "keep.txt").write_text("keep", encoding="utf-8")

    link = tmp_path / "linked_env"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks are not supported in this environment")

    summary = delete_environments([_env(link)], scan_root=tmp_path)

    assert not link.exists()
    assert target.exists()
    assert (target / "keep.txt").exists()
    assert summary["deleted_count"] == 1


def test_permission_error_handling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_dir = tmp_path / "locked" / ".venv"
    env_dir.mkdir(parents=True)

    def _raise_permission(_: Path) -> None:
        raise PermissionError("blocked")

    monkeypatch.setattr(shutil, "rmtree", _raise_permission)
    summary = delete_environments([_env(env_dir)], scan_root=tmp_path)

    assert summary["deleted_count"] == 0
    assert summary["failed_count"] == 1


def test_path_traversal_guard(tmp_path: Path) -> None:
    scan_root = tmp_path / "inside"
    scan_root.mkdir()

    outside = tmp_path / "outside" / ".venv"
    outside.mkdir(parents=True)

    summary = delete_environments([_env(outside)], scan_root=scan_root)

    assert outside.exists()
    assert summary["deleted_count"] == 0
    assert summary["skipped_count"] == 1


def test_dry_run(tmp_path: Path) -> None:
    env_dir = tmp_path / "project" / ".venv"
    env_dir.mkdir(parents=True)
    (env_dir / "f.txt").write_text("abc", encoding="utf-8")

    summary = delete_environments([_env(env_dir)], scan_root=tmp_path, dry_run=True)

    assert env_dir.exists()
    assert summary["deleted_count"] == 0
    assert summary["would_free_bytes"] > 0


def test_confirm_deletion_requires_delete_word(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env = _env(Path("/tmp/project/.venv"), size_bytes=1024)

    monkeypatch.setattr(typer, "prompt", lambda *_args, **_kwargs: "no")
    assert confirm_deletion([env], dry_run=False, skip_confirm=False) is False

    monkeypatch.setattr(typer, "prompt", lambda *_args, **_kwargs: "delete")
    assert confirm_deletion([env], dry_run=False, skip_confirm=False) is True
