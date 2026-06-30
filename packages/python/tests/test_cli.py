from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from envoic.cli import app

runner = CliRunner()


def test_scan_rejects_conflicting_artifact_flags(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--show-artifacts", "--no-artifacts"],
    )

    assert result.exit_code == 1
    assert "cannot be used together" in result.output.lower()


def test_scan_allows_show_artifacts_with_default_artifacts(tmp_path: Path) -> None:
    result = runner.invoke(app, ["scan", str(tmp_path), "--show-artifacts"])

    assert result.exit_code == 0
