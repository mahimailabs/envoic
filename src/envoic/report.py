from __future__ import annotations

from .models import EnvInfo, ScanResult
from .utils import bar_chart, format_age, format_size, shorten_path

REPORT_WIDTH = 58


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


def _table_row(index: int, env: EnvInfo) -> str:
    stale = " STALE" if env.is_stale else ""
    return (
        f"  {index:<3} "
        f"{shorten_path(env.path, 30):<30} "
        f"{(env.python_version or '-'): <8} "
        f"{format_size(env.size_bytes):>6} "
        f"{format_age(env.modified):>5}{stale}"
    )


def _size_distribution(environments: list[EnvInfo]) -> str:
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
            f"  {bar_chart(size, max_size, width=24)} {shorten_path(env.path, 24):<24} {format_size(size):>6}"
        )
    return "\n".join(lines)


def format_report(
    result: ScanResult, *, title: str = "ENVOIC - Python Environment Report"
) -> str:
    stale_count = sum(1 for env in result.environments if env.is_stale)

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
    lines.append(_row("Total Size", format_size(result.total_size_bytes)))
    lines.append(_row("Stale >90d", str(stale_count)))
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
            lines.append(_table_row(index, env))

    lines.append("─" * 58)
    lines.append("")
    lines.append(_size_distribution(result.environments))

    return "\n".join(lines)


def format_list(environments: list[EnvInfo]) -> str:
    lines = [_table_header(), "─" * 58]
    for index, env in enumerate(
        sorted(environments, key=lambda item: str(item.path)), start=1
    ):
        lines.append(_table_row(index, env))
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
