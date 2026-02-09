from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def format_size(num_bytes: int | None) -> str:
    if num_bytes is None:
        return "-"
    if num_bytes < 1024:
        return f"{num_bytes}B"

    units = ["K", "M", "G", "T"]
    value = float(num_bytes)
    for unit in units:
        value /= 1024.0
        if value < 1024 or unit == units[-1]:
            if value >= 100:
                return f"{value:.0f}{unit}"
            if value >= 10:
                return f"{value:.1f}{unit}".replace(".0", "")
            return f"{value:.1f}{unit}".replace(".0", "")
    return f"{num_bytes}B"


def format_age(moment: datetime | None, now: datetime | None = None) -> str:
    if moment is None:
        return "-"
    if now is None:
        now = datetime.now(UTC)

    delta = now - moment.astimezone(UTC)
    days = max(0, delta.days)
    if days < 30:
        return f"{days}d"
    if days < 365:
        return f"{days // 30}mo"
    return f"{days // 365}y"


def bar_chart(value: int, max_value: int, width: int = 24) -> str:
    if max_value <= 0:
        return "[" + ("░" * width) + "]"
    filled = int(round((value / max_value) * width))
    filled = max(0, min(width, filled))
    return "[" + ("█" * filled) + ("░" * (width - filled)) + "]"


def shorten_path(path: Path, max_len: int = 36) -> str:
    text = str(path)
    home = str(Path.home())
    if text.startswith(home):
        text = "~" + text[len(home) :]

    if len(text) <= max_len:
        return text

    keep = max_len - 3
    prefix = keep // 2
    suffix = keep - prefix
    return f"{text[:prefix]}...{text[-suffix:]}"
