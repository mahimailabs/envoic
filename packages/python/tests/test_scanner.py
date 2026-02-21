from pathlib import Path

from envoic.scanner import scan


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def test_scan_finds_named_and_pyvenv_dirs(tmp_path: Path) -> None:
    named = tmp_path / "project" / ".venv"
    named.mkdir(parents=True)
    _touch(named / "bin" / "activate")

    pyvenv_only = tmp_path / "other" / "custom"
    pyvenv_only.mkdir(parents=True)
    (pyvenv_only / "pyvenv.cfg").write_text("version = 3.11.0\n", encoding="utf-8")

    discovery = scan(tmp_path, max_depth=4)
    found = discovery.environments

    assert named.resolve() in found
    assert pyvenv_only.resolve() in found


def test_scan_respects_depth(tmp_path: Path) -> None:
    deep_env = tmp_path / "a" / "b" / "c" / ".venv"
    deep_env.mkdir(parents=True)
    _touch(deep_env / "bin" / "activate")

    shallow = scan(tmp_path, max_depth=2).environments
    deep = scan(tmp_path, max_depth=5).environments

    assert deep_env.resolve() not in shallow
    assert deep_env.resolve() in deep


def test_scan_skips_git_and_node_modules(tmp_path: Path) -> None:
    git_env = tmp_path / ".git" / ".venv"
    git_env.mkdir(parents=True)
    _touch(git_env / "bin" / "activate")

    node_env = tmp_path / "node_modules" / ".venv"
    node_env.mkdir(parents=True)
    _touch(node_env / "bin" / "activate")

    found = scan(tmp_path, max_depth=5).environments

    assert git_env.resolve() not in found
    assert node_env.resolve() not in found
