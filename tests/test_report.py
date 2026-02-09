from datetime import UTC, datetime, timedelta
from pathlib import Path

from envoic.models import EnvInfo, EnvType, ScanResult
from envoic.report import bar_chart, format_age, format_list, format_report, format_size


def test_format_size() -> None:
    assert format_size(512) == "512B"
    assert format_size(1024) == "1K"
    assert format_size(1024 * 1024) == "1M"


def test_format_age() -> None:
    now = datetime(2026, 2, 9, tzinfo=UTC)
    assert format_age(now - timedelta(days=12), now=now) == "12d"
    assert format_age(now - timedelta(days=90), now=now) == "3mo"


def test_bar_chart() -> None:
    assert bar_chart(0, 100, width=10) == "[░░░░░░░░░░]"
    assert bar_chart(100, 100, width=10) == "[██████████]"


def test_format_report_structure() -> None:
    env = EnvInfo(
        path=Path("/tmp/project/.venv"),
        env_type=EnvType.VENV,
        python_version="3.12.1",
        size_bytes=1024 * 1024,
        modified=datetime.now(UTC),
    )
    result = ScanResult(
        scan_path=Path("/tmp"),
        scan_depth=5,
        duration_seconds=1.2,
        environments=[env],
        total_size_bytes=1024 * 1024,
        hostname="host-a",
        timestamp=datetime(2026, 2, 9, 12, 0, 0, tzinfo=UTC),
    )

    text = format_report(result)

    assert "ENVOIC - Python Environment Report" in text
    assert "ENVIRONMENTS" in text
    assert "SIZE DISTRIBUTION" in text
    assert "project" in text


def test_format_report_path_modes() -> None:
    env = EnvInfo(
        path=Path("/tmp/project/.venv"),
        env_type=EnvType.VENV,
        python_version="3.12.1",
        size_bytes=1024 * 1024,
        modified=datetime.now(UTC),
    )
    result = ScanResult(
        scan_path=Path("/tmp"),
        scan_depth=5,
        duration_seconds=1.2,
        environments=[env],
        total_size_bytes=1024 * 1024,
        hostname="host-a",
        timestamp=datetime(2026, 2, 9, 12, 0, 0, tzinfo=UTC),
    )

    name_text = format_report(result)
    rel_text = format_report(result, path_mode="relative")
    abs_text = format_report(result, path_mode="absolute")

    assert "project" in name_text
    assert "project" in rel_text
    assert "project/.venv" not in rel_text
    assert "/tmp/project/.venv" in abs_text


def test_format_list_relative_paths() -> None:
    env = EnvInfo(
        path=Path("/tmp/project/.venv"),
        env_type=EnvType.VENV,
        python_version="3.12.1",
    )
    text = format_list([env], path_mode="relative", base_path=Path("/tmp"))
    assert "project" in text
    assert "project/.venv" not in text
