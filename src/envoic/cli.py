from __future__ import annotations

import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

import typer

from . import __version__
from .detector import activation_hint, detect_environment, list_top_packages
from .models import EnvInfo, EnvType, ScanResult, to_serializable_dict
from .report import format_info, format_list, format_report
from .scanner import scan as scan_paths

app = typer.Typer(help="Discover and report Python virtual environments.")


def _build_scan_result(
    path: Path,
    depth: int,
    *,
    deep: bool,
    stale_days: int,
    include_dotenv: bool,
) -> ScanResult:
    start = time.perf_counter()
    candidates = scan_paths(path, max_depth=depth)

    envs: list[EnvInfo] = []
    for candidate in candidates:
        env_info = detect_environment(
            candidate,
            deep=deep,
            stale_days=stale_days,
            include_dotenv=include_dotenv,
        )
        if env_info.env_type == EnvType.UNKNOWN:
            continue
        if env_info.env_type == EnvType.DOTENV_DIR and not include_dotenv:
            continue
        envs.append(env_info)

    duration = time.perf_counter() - start
    total_size_bytes = sum(env.size_bytes or 0 for env in envs)

    return ScanResult(
        scan_path=path.resolve(),
        scan_depth=depth,
        duration_seconds=duration,
        environments=sorted(envs, key=lambda item: str(item.path)),
        total_size_bytes=total_size_bytes,
        hostname=socket.gethostname(),
        timestamp=datetime.now(timezone.utc),
    )


def _print_output(text: str, use_rich: bool) -> None:
    if use_rich:
        try:
            from rich.console import Console

            Console().print(text)
            return
        except Exception:
            pass
    typer.echo(text)


@app.command()
def scan(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    deep: bool = typer.Option(False, "--deep", help="Compute size and package metadata."),
    json_output: bool = typer.Option(False, "--json", help="Output JSON report.", rich_help_panel="Output"),
    stale_days: int = typer.Option(90, "--stale-days", min=1, help="Mark env as stale after N days."),
    include_dotenv: bool = typer.Option(False, "--include-dotenv", help="Include plain .env directories."),
    rich_output: bool = typer.Option(False, "--rich", help="Use optional rich-rendered output."),
) -> None:
    """Scan a filesystem path for Python environments."""
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=include_dotenv,
    )

    if json_output:
        typer.echo(json.dumps(to_serializable_dict(result), indent=2))
        raise typer.Exit(0)

    _print_output(format_report(result), use_rich=rich_output)


@app.command()
def list(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    deep: bool = typer.Option(False, "--deep", help="Compute size and package metadata."),
    stale_days: int = typer.Option(90, "--stale-days", min=1, help="Mark env as stale after N days."),
    include_dotenv: bool = typer.Option(False, "--include-dotenv", help="Include plain .env directories."),
    rich_output: bool = typer.Option(False, "--rich", help="Use optional rich-rendered output."),
) -> None:
    """Print a compact environments table."""
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=include_dotenv,
    )
    _print_output(format_list(result.environments), use_rich=rich_output)


@app.command()
def info(
    env_path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    rich_output: bool = typer.Option(False, "--rich", help="Use optional rich-rendered output."),
) -> None:
    """Show detailed information for one environment."""
    env = detect_environment(env_path, deep=True)
    if env.env_type == EnvType.UNKNOWN:
        typer.echo(f"Not a recognized Python environment: {env_path}", err=True)
        raise typer.Exit(code=1)

    top_packages = list_top_packages(env.path, limit=10)
    activation = activation_hint(env.path, env.env_type)
    _print_output(format_info(env, top_packages, activation), use_rich=rich_output)


@app.command()
def version() -> None:
    """Print envoic version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
