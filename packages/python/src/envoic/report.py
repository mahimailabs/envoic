from __future__ import annotations

from pathlib import Path
from typing import Literal

from .artifacts import CAREFUL_NOTES, SAFETY_TEXT
from .models import ArtifactSummary, EnvInfo, SafetyLevel, ScanResult
from .utils import (
    VENV_DIR_NAMES,
    bar_chart,
    format_age,
    format_env_display_path,
    format_size,
    shorten_path,
)

REPORT_WIDTH = 58
PathMode = Literal["name", "relative", "absolute"]


def _box_top(width: int = REPORT_WIDTH) -> str:
    return "┌" + ("─" * width) + "┐"


def _box_mid(width: int = REPORT_WIDTH) -> str:
    return "├" + ("─" * width) + "┤"


def _box_bottom(width: int = REPORT_WIDTH) -> str:
    return "└" + ("─" * width) + "┘"


def box_line(text: str, width: int = REPORT_WIDTH) -> str:
    clipped = text[:width]
    return f"│{clipped:<{width}}│"


def _row(label: str, value: str, width: int = REPORT_WIDTH) -> str:
    left = f"  {label:<12}"
    right_width = max(0, width - len(left) - 2)
    value = value[:right_width]
    return box_line(f"{left}{value:>{right_width}}  ", width=width)


def _table_header() -> str:
    return f"  {'#':<3} {'Path':<30} {'Python':<8} {'Size':>6} {'Age':>5}"


def _truncate_text(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    keep = width - 3
    prefix = keep // 2
    suffix = keep - prefix
    return f"{text[:prefix]}...{text[-suffix:]}"


def _environment_label(
    env_path: Path,
    width: int,
    *,
    path_mode: PathMode,
    base_path: Path | None = None,
) -> str:
    if path_mode == "absolute":
        return _truncate_text(str(env_path), width)

    if path_mode == "relative":
        if base_path is not None:
            try:
                return _truncate_text(
                    format_env_display_path(env_path, base_path), width
                )
            except (OSError, ValueError):
                pass
        return _truncate_text(str(env_path), width)

    name = env_path.name
    if name in VENV_DIR_NAMES and env_path.parent.name:
        name = env_path.parent.name
    return _truncate_text(name, width)


def _table_row(
    index: int,
    env: EnvInfo,
    *,
    path_mode: PathMode,
    base_path: Path | None = None,
) -> str:
    stale = " STALE" if env.is_stale else ""
    return (
        f"  {index:<3} "
        f"{_environment_label(env.path, 30, path_mode=path_mode, base_path=base_path):<30} "
        f"{(env.python_version or '-'): <8} "
        f"{format_size(env.size_bytes):>6} "
        f"{format_age(env.modified):>5}{stale}"
    )


def _size_distribution(
    environments: list[EnvInfo], *, path_mode: PathMode, base_path: Path | None = None
) -> str:
    lines: list[str] = ["SIZE DISTRIBUTION"]
    if not environments:
        lines.append("  (no environments)")
        return "\n".join(lines)

    sized = [env for env in environments if env.size_bytes is not None]
    if not sized:
        lines.append("  (run with --deep to include size data)")
        return "\n".join(lines)

    max_size = max((env.size_bytes or 0) for env in sized)
    for env in sized:
        size = env.size_bytes or 0
        lines.append(
            f"  {bar_chart(size, max_size, width=24)} {_environment_label(env.path, 24, path_mode=path_mode, base_path=base_path):<24} {format_size(size):>6}"
        )
    return "\n".join(lines)


def _artifact_table_header(deep: bool) -> str:
    if deep:
        return f"  {'Category':<22} {'Count':>6} {'Size':>8} {'Safety':>16}"
    return f"  {'Category':<22} {'Count':>6} {'Safety':>16}"


def _artifact_row(summary: ArtifactSummary, *, deep: bool) -> str:
    if deep:
        return (
            f"  {summary.pattern:<22} "
            f"{summary.count:>6} "
            f"{format_size(summary.total_size_bytes):>8} "
            f"{SAFETY_TEXT[summary.safety]:>16}"
        )
    return (
        f"  {summary.pattern:<22} {summary.count:>6} {SAFETY_TEXT[summary.safety]:>16}"
    )


def _artifact_distribution(
    artifact_summary: list[ArtifactSummary], *, deep: bool
) -> str:
    lines = ["SIZE DISTRIBUTION (Artifacts)"]
    if not artifact_summary:
        lines.append("  (no artifacts found)")
        return "\n".join(lines)
    if not deep:
        lines.append("  (run with --deep to include size data)")
        return "\n".join(lines)

    sized = [item for item in artifact_summary if item.total_size_bytes > 0]
    if not sized:
        lines.append("  (no artifact size data)")
        return "\n".join(lines)

    max_size = max(item.total_size_bytes for item in sized)
    for item in sized:
        lines.append(
            f"  {bar_chart(item.total_size_bytes, max_size, width=24)} {item.pattern:<20} {format_size(item.total_size_bytes):>6}"
        )
    return "\n".join(lines)


def format_report(
    result: ScanResult,
    *,
    title: str = "ENVOIC - Python Environment Report",
    path_mode: PathMode = "name",
    deep: bool = False,
    show_artifact_details: bool = False,
) -> str:
    stale_count = sum(1 for env in result.environments if env.is_stale)
    artifact_count = sum(item.count for item in result.artifact_summary)
    artifact_total_size = sum(item.total_size_bytes for item in result.artifact_summary)

    lines: list[str] = []
    lines.append(_box_top())
    lines.append(box_line(f"  {title}"))
    lines.append(box_line("  TR-200  Environment Scanner"))
    lines.append(_box_mid())
    lines.append(_row("Date", result.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
    lines.append(_row("Host", result.hostname))
    lines.append(_row("Scan Path", shorten_path(result.scan_path, 36)))
    lines.append(_row("Scan Depth", str(result.scan_depth)))
    lines.append(_row("Duration", f"{result.duration_seconds:.2f}s"))
    lines.append(_box_mid())
    lines.append(_row("Envs Found", str(len(result.environments))))
    lines.append(
        _row("Env Size", format_size(result.total_size_bytes) if deep else "-")
    )
    lines.append(_row("Stale >90d", str(stale_count)))
    lines.append(_row("Artifacts Found", str(artifact_count)))
    lines.append(
        _row("Artifact Size", format_size(artifact_total_size) if deep else "-")
    )
    lines.append(_box_bottom())
    lines.append("")
    lines.append("ENVIRONMENTS")
    lines.append("─" * 58)
    lines.append(_table_header())
    lines.append("─" * 58)

    if not result.environments:
        lines.append("  (no environments found)")
    else:
        sorted_envs = sorted(result.environments, key=lambda item: str(item.path))
        for index, env in enumerate(sorted_envs, start=1):
            lines.append(
                _table_row(
                    index,
                    env,
                    path_mode=path_mode,
                    base_path=result.scan_path,
                )
            )

    lines.append("─" * 58)
    lines.append("")
    if show_artifact_details:
        lines.append("ARTIFACTS")
        lines.append("─" * 58)
        lines.append(_artifact_table_header(deep))
        lines.append("─" * 58)
        if not result.artifact_summary:
            lines.append("  (no artifacts found)")
        else:
            for summary in result.artifact_summary:
                lines.append(_artifact_row(summary, deep=deep))
        lines.append("─" * 58)
        if deep and any(
            item.safety == SafetyLevel.CAREFUL for item in result.artifact_summary
        ):
            careful_patterns = {
                item.pattern
                for item in result.artifact_summary
                if item.safety == SafetyLevel.CAREFUL
            }
            for pattern in sorted(careful_patterns):
                note = CAREFUL_NOTES.get(pattern)
                if note:
                    lines.append(f"  * {pattern}: {note}")
            lines.append("─" * 58)
        if not deep:
            lines.append("  (run with --deep to include size data)")
            lines.append("─" * 58)
        lines.append("")
        lines.append(
            _artifact_distribution(
                result.artifact_summary,
                deep=deep,
            )
        )
        lines.append("")
    else:
        lines.append("ARTIFACT DETAILS")
        lines.append("─" * 58)
        lines.append(
            "  (hidden by default; run with --show-artifacts to show detailed breakdown)"
        )
        lines.append("─" * 58)
        lines.append("")
    lines.append(
        _size_distribution(
            result.environments, path_mode=path_mode, base_path=result.scan_path
        )
    )

    return "\n".join(lines)


def format_list(
    environments: list[EnvInfo],
    *,
    path_mode: PathMode = "name",
    base_path: Path | None = None,
) -> str:
    lines = [_table_header(), "─" * 58]
    for index, env in enumerate(
        sorted(environments, key=lambda item: str(item.path)), start=1
    ):
        lines.append(_table_row(index, env, path_mode=path_mode, base_path=base_path))
    if len(lines) == 2:
        lines.append("  (no environments found)")
    return "\n".join(lines)


def format_info(env: EnvInfo, top_packages: list[str], activation: str) -> str:
    lines: list[str] = []
    lines.append(_box_top())
    lines.append(box_line("  ENVOIC - Environment Detail"))
    lines.append(_box_mid())
    lines.append(_row("Path", str(env.path)))
    lines.append(_row("Type", env.env_type.value))
    lines.append(_row("Python", env.python_version or "-"))
    lines.append(_row("Size", format_size(env.size_bytes)))
    lines.append(_row("Packages", str(env.package_count or 0)))
    lines.append(
        _row(
            "Modified",
            env.modified.strftime("%Y-%m-%d %H:%M:%S") if env.modified else "-",
        )
    )
    lines.append(
        _row(
            "Created", env.created.strftime("%Y-%m-%d %H:%M:%S") if env.created else "-"
        )
    )
    lines.append(_row("Activate", activation))
    lines.append(_box_bottom())
    lines.append("")
    lines.append("TOP PACKAGES")
    lines.append("─" * 58)
    if not top_packages:
        lines.append("  (no package metadata found)")
    else:
        for idx, name in enumerate(top_packages, start=1):
            lines.append(f"  {idx:>2}. {name}")
    lines.append("─" * 58)
    return "\n".join(lines)


__all__ = [
    "box_line",
    "bar_chart",
    "format_age",
    "format_info",
    "format_list",
    "format_report",
    "format_size",
]
