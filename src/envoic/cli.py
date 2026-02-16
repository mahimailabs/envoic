from __future__ import annotations

import json
import socket
import time
from datetime import UTC, datetime
from pathlib import Path

import typer

from . import __version__
from .artifacts import summarize_artifacts, summarize_with_empty_patterns
from .detector import activation_hint, detect_environment, list_top_packages
from .manager import (
    confirm_careful_artifacts,
    confirm_deletion,
    delete_environments,
    flatten_artifact_summary,
    interactive_select_with_artifacts,
    print_deletion_report,
)
from .models import (
    ArtifactInfo,
    EnvInfo,
    EnvType,
    SafetyLevel,
    ScanResult,
    to_serializable_dict,
)
from .report import PathMode, format_info, format_list, format_report
from .scanner import scan as scan_paths

app = typer.Typer(help="Discover and report Python virtual environments.")


def _build_scan_result(
    path: Path,
    depth: int,
    *,
    deep: bool,
    stale_days: int,
    include_dotenv: bool,
    include_artifacts: bool = True,
) -> ScanResult:
    start = time.perf_counter()
    discovery = scan_paths(
        path,
        max_depth=depth,
        include_artifacts=include_artifacts,
        deep=deep,
    )

    envs: list[EnvInfo] = []
    for candidate in discovery.environments:
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
    artifacts = discovery.artifacts if include_artifacts else []

    return ScanResult(
        scan_path=path.resolve(),
        scan_depth=depth,
        duration_seconds=duration,
        environments=sorted(envs, key=lambda item: str(item.path)),
        total_size_bytes=total_size_bytes,
        hostname=socket.gethostname(),
        timestamp=datetime.now(UTC),
        artifacts=artifacts,
        artifact_summary=summarize_artifacts(artifacts),
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


def _confirm_and_delete(
    selected: list[EnvInfo | ArtifactInfo],
    *,
    scan_root: Path,
    initial_total: int,
    dry_run: bool,
    yes: bool,
) -> None:
    confirmed = confirm_deletion(
        selected,
        scan_root=scan_root,
        dry_run=dry_run,
        skip_confirm=yes,
    )
    if dry_run:
        summary = delete_environments(
            selected,
            scan_root=scan_root,
            dry_run=True,
            dry_run_echo=False,
        )
        print_deletion_report(summary, initial_total=initial_total)
        raise typer.Exit(0)

    if not confirmed:
        typer.echo("Deletion cancelled.")
        raise typer.Exit(0)

    summary = delete_environments(
        selected,
        scan_root=scan_root,
        dry_run=False,
    )
    print_deletion_report(summary, initial_total=initial_total)


@app.command()
def scan(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    deep: bool = typer.Option(
        False, "--deep", help="Compute size and package metadata."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output JSON report.", rich_help_panel="Output"
    ),
    stale_days: int = typer.Option(
        90, "--stale-days", min=1, help="Mark env as stale after N days."
    ),
    include_dotenv: bool = typer.Option(
        False, "--include-dotenv", help="Include plain .env directories."
    ),
    include_artifacts: bool = typer.Option(
        True,
        "--artifacts/--no-artifacts",
        help="Include Python artifact detection.",
    ),
    path_mode: PathMode = typer.Option(
        "name",
        "--path-mode",
        help="How to render environment path columns: name, relative, absolute.",
    ),
    rich_output: bool = typer.Option(
        False, "--rich", help="Use optional rich-rendered output."
    ),
) -> None:
    """Scan a filesystem path for Python environments."""
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=include_dotenv,
        include_artifacts=include_artifacts,
    )

    if json_output:
        typer.echo(json.dumps(to_serializable_dict(result), indent=2))
        raise typer.Exit(0)

    _print_output(
        format_report(result, path_mode=path_mode, deep=deep),
        use_rich=rich_output,
    )


@app.command(name="list")
def list_environments(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    deep: bool = typer.Option(
        False, "--deep", help="Compute size and package metadata."
    ),
    stale_days: int = typer.Option(
        90, "--stale-days", min=1, help="Mark env as stale after N days."
    ),
    include_dotenv: bool = typer.Option(
        False, "--include-dotenv", help="Include plain .env directories."
    ),
    path_mode: PathMode = typer.Option(
        "name",
        "--path-mode",
        help="How to render environment path columns: name, relative, absolute.",
    ),
    rich_output: bool = typer.Option(
        False, "--rich", help="Use optional rich-rendered output."
    ),
) -> None:
    """Print a compact environments table."""
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=include_dotenv,
        include_artifacts=False,
    )
    _print_output(
        format_list(
            result.environments, path_mode=path_mode, base_path=result.scan_path
        ),
        use_rich=rich_output,
    )


@app.command()
def info(
    env_path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    rich_output: bool = typer.Option(
        False, "--rich", help="Use optional rich-rendered output."
    ),
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


@app.command()
def manage(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    stale_only: bool = typer.Option(
        False, "--stale-only", help="Pre-select only stale environments."
    ),
    stale_days: int = typer.Option(
        90, "--stale-days", min=1, help="Mark env as stale after N days."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deleted without deleting."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip final confirmation (dangerous)."
    ),
    deep: bool = typer.Option(
        False, "--deep", help="Compute size and package metadata for selection view."
    ),
) -> None:
    """Interactively select and delete Python environments."""
    typer.echo(f"Scanning {path.resolve()}...")
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=False,
        include_artifacts=True,
    )
    if not result.environments and not result.artifacts:
        typer.echo("No environments or artifacts found.")
        raise typer.Exit(0)

    typer.echo("")
    typer.echo(
        f"Found {len(result.environments)} Python environments and {len(result.artifacts)} artifacts."
    )

    selected_envs: list[EnvInfo] = []
    selected_artifact_groups = []
    artifact_groups = summarize_with_empty_patterns(result.artifacts)
    while True:
        selected_envs, selected_artifact_groups = interactive_select_with_artifacts(
            result.environments,
            artifact_groups,
            scan_root=result.scan_path,
            stale_only=stale_only,
        )
        if not selected_envs and not selected_artifact_groups:
            typer.echo("Nothing selected.")
            raise typer.Exit(0)
        careful_selected = [
            item
            for item in selected_artifact_groups
            if item.safety == SafetyLevel.CAREFUL
        ]
        if not careful_selected:
            break
        if confirm_careful_artifacts(careful_selected):
            break
        typer.echo("")
        typer.echo("Reopening selection...")
        typer.echo("")

    selected_items: list[EnvInfo | ArtifactInfo] = [
        *selected_envs,
        *flatten_artifact_summary(selected_artifact_groups),
    ]

    _confirm_and_delete(
        selected_items,
        scan_root=result.scan_path,
        initial_total=len(result.environments) + len(result.artifacts),
        dry_run=dry_run,
        yes=yes,
    )


@app.command()
def clean(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, dir_okay=True),
    depth: int = typer.Option(5, "--depth", "-d", min=1, help="Max directory depth."),
    stale_days: int = typer.Option(
        90, "--stale-days", min=1, help="Delete envs older than N days."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deleted without deleting."
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip final confirmation (dangerous)."
    ),
    deep: bool = typer.Option(
        True, "--deep/--no-deep", help="Compute size metadata for stale candidates."
    ),
) -> None:
    """Delete stale environments without interactive selection."""
    typer.echo(f"Scanning {path.resolve()} for stale environments...")
    result = _build_scan_result(
        path,
        depth,
        deep=deep,
        stale_days=stale_days,
        include_dotenv=False,
        include_artifacts=False,
    )
    selected = [env for env in result.environments if env.is_stale]
    if not selected:
        typer.echo("No stale environments found.")
        raise typer.Exit(0)

    typer.echo(f"Found {len(selected)} stale environments.")
    _confirm_and_delete(
        selected,
        scan_root=result.scan_path,
        initial_total=len(result.environments),
        dry_run=dry_run,
        yes=yes,
    )


def main() -> None:
    """Console-script entrypoint."""
    app()


if __name__ == "__main__":
    main()
