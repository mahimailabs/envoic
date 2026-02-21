from pathlib import Path

from envoic.detector import detect_environment
from envoic.models import EnvType


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def test_detect_with_pyvenv_cfg(tmp_path: Path) -> None:
    env_dir = tmp_path / ".venv"
    env_dir.mkdir()
    (env_dir / "pyvenv.cfg").write_text("version = 3.12.1\n", encoding="utf-8")

    info = detect_environment(env_dir)

    assert info.env_type == EnvType.VENV
    assert info.has_pyvenv_cfg is True
    assert info.python_version == "3.12.1"
    assert "pyvenv.cfg" in info.signals


def test_detect_with_python_and_site_packages(tmp_path: Path) -> None:
    env_dir = tmp_path / "venv"
    _touch(env_dir / "bin" / "python")
    (env_dir / "lib" / "python3.11" / "site-packages").mkdir(parents=True)

    info = detect_environment(env_dir)

    assert info.env_type == EnvType.VENV
    assert "python+site-packages" in info.signals


def test_detect_conda_environment(tmp_path: Path) -> None:
    env_dir = tmp_path / "conda-env"
    (env_dir / "conda-meta").mkdir(parents=True)

    info = detect_environment(env_dir)

    assert info.env_type == EnvType.CONDA
    assert "conda-meta" in info.signals


def test_detect_plain_dotenv_dir(tmp_path: Path) -> None:
    env_dir = tmp_path / ".env"
    env_dir.mkdir()

    info = detect_environment(env_dir)

    assert info.env_type == EnvType.DOTENV_DIR


def test_detect_unknown_for_non_env(tmp_path: Path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()

    info = detect_environment(folder)

    assert info.env_type == EnvType.UNKNOWN
