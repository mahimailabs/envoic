from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, TypedDict, cast

import typer

from .artifacts import CAREFUL_NOTES, SAFETY_TEXT
from .models import ArtifactInfo, ArtifactSummary, EnvInfo, SafetyLevel
from .utils import format_age, format_env_display_path, format_size


class DeletionSummary(TypedDict):
    selected_count: int
    deleted_count: int
    failed_count: int
    skipped_count: int
    bytes_freed: int
    would_free_bytes: int
    errors: list[str]
    dry_run: bool


def _abs_no_symlink(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _is_within_root(path: Path, scan_root: Path) -> bool:
    path_abs = _abs_no_symlink(path)
    root_abs = _abs_no_symlink(scan_root)
    try:
        path_abs.relative_to(root_abs)
    except ValueError:
        return False
    return True


def _size_for_deletion(path: Path) -> int:
    try:
        if path.is_symlink():
            return path.lstat().st_size
        if path.is_file():
            return path.stat().st_size
        if not path.is_dir():
            return 0
    except OSError:
        return 0

    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for filename in files:
            file_path = Path(root) / filename
            try:
                if file_path.is_symlink():
                    total += file_path.lstat().st_size
                else:
                    total += file_path.stat().st_size
            except OSError:
                continue
    return total


def _column_width(display_paths: list[str]) -> int:
    if not display_paths:
        return 30
    max_path_len = max(len(item) for item in display_paths)
    return min(max(max_path_len + 2, 20), 50)


def _table_header(path_width: int) -> str:
    return f"{'Path':<{path_width}} {'Python':<8} {'Size':>6}  {'Age':>5}"


def _choice_text(env: EnvInfo, *, scan_root: Path, path_width: int) -> str:
    display_path = format_env_display_path(env.path, scan_root)
    stale = "  STALE" if env.is_stale else ""
    return (
        f"{display_path:<{path_width}} "
        f"{(env.python_version or '-'): <8} "
        f"{format_size(env.size_bytes):>6}  "
        f"{format_age(env.modified):>5}{stale}"
    )


def _artifact_label(summary: ArtifactSummary) -> str:
    count_label = f"{summary.count} {'dir' if summary.count == 1 else 'dirs'}"
    if summary.pattern in {"*.pyc", "*.pyo", ".coverage"}:
        count_label = f"{summary.count} {'file' if summary.count == 1 else 'files'}"
    size_text = (
        format_size(summary.total_size_bytes) if summary.total_size_bytes > 0 else "-"
    )
    return f"All {summary.pattern:<18} ({count_label:<8}) {size_text:>6}"


def flatten_artifact_summary(summaries: list[ArtifactSummary]) -> list[ArtifactInfo]:
    items: list[ArtifactInfo] = []
    for summary in summaries:
        items.extend(summary.items)
    return items


def _fallback_select(
    environments: list[EnvInfo], *, scan_root: Path, stale_only: bool = False
) -> list[EnvInfo]:
    typer.echo("")
    typer.echo(
        f"Found {len(environments)} environments. "
        "Enter numbers to delete (comma-separated):"
    )
    typer.echo("")
    display_paths = [
        format_env_display_path(env.path, scan_root) for env in environments
    ]
    path_width = _column_width(display_paths)
    typer.echo(f"      {_table_header(path_width)}")
    typer.echo(f"      {'-' * (path_width + 24)}")
    for idx, env in enumerate(environments, start=1):
        marker = "x" if stale_only and env.is_stale else " "
        typer.echo(
            f"  {idx:<3} [{marker}] "
            f"{_choice_text(env, scan_root=scan_root, path_width=path_width)}"
        )

    default = ""
    if stale_only:
        stale_indexes = [
            str(i) for i, env in enumerate(environments, start=1) if env.is_stale
        ]
        default = ",".join(stale_indexes)

    selection_raw = typer.prompt(
        "Select [e.g. 1,3,5]",
        default=default,
        show_default=bool(default),
    ).strip()
    if not selection_raw:
        return []

    selected_indexes: set[int] = set()
    for part in selection_raw.split(","):
        token = part.strip()
        if not token:
            continue
        if not token.isdigit():
            continue
        idx = int(token)
        if 1 <= idx <= len(environments):
            selected_indexes.add(idx - 1)

    return [environments[i] for i in sorted(selected_indexes)]


def interactive_select(
    environments: list[EnvInfo], *, scan_root: Path, stale_only: bool = False
) -> list[EnvInfo]:
    """Display an interactive checklist and return selected environments."""
    if not environments:
        return []

    display_paths = [
        format_env_display_path(env.path, scan_root) for env in environments
    ]
    path_width = _column_width(display_paths)

    is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if is_interactive:
        try:
            import questionary

            header = _table_header(path_width)
            rule = "-" * (path_width + 24)
            env_choices = [
                questionary.Choice(
                    title=_choice_text(env, scan_root=scan_root, path_width=path_width),
                    value=index,
                    checked=stale_only and env.is_stale,
                )
                for index, env in enumerate(environments)
            ]
            choices = [
                questionary.Separator(f"  {header}"),
                questionary.Separator(f"  {rule}"),
                *env_choices,
            ]
            selected = questionary.checkbox(
                "Select environments to delete",
                choices=choices,
                instruction="Use ↑↓ to move, Space to toggle, Enter to confirm",
            ).ask()
            if not selected:
                return []
            return [environments[i] for i in selected]
        except ImportError:
            pass
        except KeyboardInterrupt as exc:
            raise typer.Abort() from exc
        except Exception:
            typer.echo(
                "(interactive selection unavailable, using text fallback)", err=True
            )

    return _fallback_select(environments, scan_root=scan_root, stale_only=stale_only)


def interactive_select_with_artifacts(
    environments: list[EnvInfo],
    artifact_summary: list[ArtifactSummary],
    *,
    scan_root: Path,
    stale_only: bool = False,
) -> tuple[list[EnvInfo], list[ArtifactSummary]]:
    if not environments and not artifact_summary:
        return [], []

    display_paths = [
        format_env_display_path(env.path, scan_root) for env in environments
    ]
    path_width = _column_width(display_paths)

    is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
    if is_interactive:
        try:
            import questionary

            choices: list[Any] = []
            header = _table_header(path_width)
            rule = "-" * (path_width + 24)
            if environments:
                choices.extend(
                    [
                        questionary.Separator("  Environments:"),
                        questionary.Separator(f"  {header}"),
                        questionary.Separator(f"  {rule}"),
                    ]
                )
                choices.extend(
                    questionary.Choice(
                        title=_choice_text(
                            env, scan_root=scan_root, path_width=path_width
                        ),
                        value=("env", index),
                        checked=stale_only and env.is_stale,
                    )
                    for index, env in enumerate(environments)
                )

            safety_groups = [
                ("Artifacts (safe to delete):", SafetyLevel.ALWAYS_SAFE),
                ("Artifacts (usually safe):", SafetyLevel.USUALLY_SAFE),
                ("Artifacts (careful - slow to recreate):", SafetyLevel.CAREFUL),
            ]
            for group_title, safety in safety_groups:
                group_items = [
                    item for item in artifact_summary if item.safety == safety
                ]
                if not group_items:
                    continue
                choices.append(questionary.Separator(f"  {group_title}"))
                for index, summary in enumerate(group_items):
                    disabled = "none found" if summary.count == 0 else None
                    choices.append(
                        questionary.Choice(
                            title=_artifact_label(summary),
                            value=("artifact", safety.value, index),
                            checked=False,
                            disabled=disabled,
                        )
                    )

            selected = questionary.checkbox(
                "Select items to delete",
                choices=choices,
                instruction="Use ↑↓ to move, Space to toggle, Enter to confirm",
            ).ask()
            if not selected:
                return [], []

            selected_envs: list[EnvInfo] = []
            selected_artifacts: list[ArtifactSummary] = []
            grouped_by_safety = {
                SafetyLevel.ALWAYS_SAFE: [
                    item
                    for item in artifact_summary
                    if item.safety == SafetyLevel.ALWAYS_SAFE
                ],
                SafetyLevel.USUALLY_SAFE: [
                    item
                    for item in artifact_summary
                    if item.safety == SafetyLevel.USUALLY_SAFE
                ],
                SafetyLevel.CAREFUL: [
                    item
                    for item in artifact_summary
                    if item.safety == SafetyLevel.CAREFUL
                ],
            }
            for tag, *rest in selected:
                if tag == "env":
                    selected_envs.append(environments[rest[0]])
                    continue
                safety = SafetyLevel(rest[0])
                index = rest[1]
                selected_artifacts.append(grouped_by_safety[safety][index])

            return selected_envs, selected_artifacts
        except ImportError:
            pass
        except KeyboardInterrupt as exc:
            raise typer.Abort() from exc
        except Exception:
            typer.echo(
                "(interactive selection unavailable, using text fallback)", err=True
            )

    env_selected = _fallback_select(
        environments, scan_root=scan_root, stale_only=stale_only
    )
    typer.echo("")
    typer.echo("Artifact selections (comma-separated indexes, blank to skip):")
    indexed_artifacts = [item for item in artifact_summary if item.count > 0]
    for idx, summary in enumerate(indexed_artifacts, start=1):
        typer.echo(
            f"  {idx:<3} {_artifact_label(summary)} [{SAFETY_TEXT[summary.safety]}]"
        )
    raw = typer.prompt("Select artifact groups", default="", show_default=False).strip()
    if not raw:
        return env_selected, []
    chosen: set[int] = set()
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit():
            num = int(token)
            if 1 <= num <= len(indexed_artifacts):
                chosen.add(num - 1)
    return env_selected, [indexed_artifacts[i] for i in sorted(chosen)]


def confirm_careful_artifacts(selected: list[ArtifactSummary]) -> bool:
    if not selected:
        return True

    typer.echo("")
    typer.echo("⚠ You selected items that may impact your workflow:")
    typer.echo("")
    for item in selected:
        typer.echo(
            f"  {item.pattern} ({item.count} dirs, {format_size(item.total_size_bytes)})"
        )
        note = CAREFUL_NOTES.get(item.pattern)
        if note:
            typer.echo(f"    {note}")
        if item.pattern == "*.egg-info":
            typer.echo(
                "    Deleting them breaks editable install metadata until re-run."
            )
        typer.echo("")

    response = cast(
        str,
        typer.prompt(
            "Continue with these included? [y/N]", default="N", show_default=False
        ),
    )
    return response.strip().lower() in {"y", "yes"}


def confirm_deletion(
    selected: list[EnvInfo | ArtifactInfo],
    *,
    scan_root: Path,
    dry_run: bool = False,
    skip_confirm: bool = False,
) -> bool:
    """Show deletion summary and require explicit confirmation."""
    typer.echo("")
    typer.echo("⚠ The following items will be PERMANENTLY DELETED:")
    typer.echo("")

    display_paths = [format_env_display_path(item.path, scan_root) for item in selected]
    path_width = _column_width(display_paths)

    total = 0
    for idx, item in enumerate(selected, start=1):
        size = item.size_bytes or 0
        total += size
        typer.echo(
            f"  {idx:<3} "
            f"{format_env_display_path(item.path, scan_root):<{path_width}} "
            f"{format_size(size):>6}"
        )

    typer.echo("")
    typer.echo(f"  Total: {format_size(total)} will be freed")

    if dry_run:
        typer.echo("")
        typer.echo("DRY RUN — no files will be deleted.")
        return False

    if skip_confirm:
        return True

    typed = cast(
        str,
        typer.prompt('Type "delete" to confirm', default="", show_default=False),
    )
    return typed.strip() == "delete"


def delete_environments(
    selected: list[EnvInfo | ArtifactInfo],
    *,
    scan_root: Path,
    dry_run: bool = False,
    dry_run_echo: bool = True,
) -> DeletionSummary:
    """Delete selected environments with path guards and symlink safety."""
    summary: DeletionSummary = {
        "selected_count": len(selected),
        "deleted_count": 0,
        "failed_count": 0,
        "skipped_count": 0,
        "bytes_freed": 0,
        "would_free_bytes": 0,
        "errors": [],
        "dry_run": dry_run,
    }

    for item in selected:
        path = item.path

        if not _is_within_root(path, scan_root):
            warning = f"Skipping outside scan path: {path}"
            typer.echo(f"Warning: {warning}", err=True)
            summary["skipped_count"] += 1
            summary["errors"].append(warning)
            continue

        size = _size_for_deletion(path)
        summary["would_free_bytes"] += size

        if dry_run:
            if dry_run_echo:
                typer.echo(
                    f"[dry-run] Would delete {format_env_display_path(path, scan_root)}"
                )
            continue

        if not path.exists() and not path.is_symlink():
            typer.echo(f"Skipping missing path: {path}")
            summary["skipped_count"] += 1
            continue

        typer.echo(
            f"Deleting {format_env_display_path(path, scan_root)} ...",
            nl=False,
        )
        try:
            if path.is_symlink():
                path.unlink()
            else:
                shutil.rmtree(path)
            summary["deleted_count"] += 1
            summary["bytes_freed"] += size
            typer.echo(" done")
        except PermissionError as exc:
            summary["failed_count"] += 1
            summary["errors"].append(str(exc))
            typer.echo(" failed (permission denied)")
        except OSError as exc:
            summary["failed_count"] += 1
            summary["errors"].append(str(exc))
            typer.echo(" failed")

    return summary


def print_deletion_report(summary: DeletionSummary, *, initial_total: int) -> None:
    """Print post-deletion report in compact box style."""
    remaining = max(0, initial_total - summary["deleted_count"])
    freed_value = (
        summary["would_free_bytes"] if summary["dry_run"] else summary["bytes_freed"]
    )

    typer.echo("─" * 58)
    if summary["dry_run"]:
        typer.echo("  DRY RUN SUMMARY")
    typer.echo(f"  Deleted:   {summary['deleted_count']} items")
    typer.echo(f"  Failed:    {summary['failed_count']}")
    typer.echo(f"  Skipped:   {summary['skipped_count']}")
    typer.echo(f"  Freed:     {format_size(freed_value)}")
    typer.echo(f"  Remaining: {remaining} items")
    typer.echo("─" * 58)
