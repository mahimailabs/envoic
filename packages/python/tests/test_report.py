from datetime import UTC, datetime, timedelta
from pathlib import Path

from envoic.models import EnvInfo, EnvType, ScanResult
from envoic.report import bar_chart, format_age, format_list, format_report, format_size


def _env(
    name: str,
    *,
    python_version: str | None = "3.12.1",
    size_bytes: int | None = None,
    modified: datetime | None = None,
) -> EnvInfo:
    return EnvInfo(
        path=Path(f"/tmp/{name}/.venv"),
        env_type=EnvType.VENV,
        python_version=python_version,
        size_bytes=size_bytes,
        modified=modified,
    )


def _scan_result(environments: list[EnvInfo]) -> ScanResult:
    return ScanResult(
        scan_path=Path("/tmp"),
        scan_depth=5,
        duration_seconds=1.2,
        environments=environments,
        total_size_bytes=sum(env.size_bytes or 0 for env in environments),
        hostname="host-a",
        timestamp=datetime(2026, 2, 9, 12, 0, 0, tzinfo=UTC),
    )


def _assert_order(text: str, *labels: str) -> None:
    positions = [text.index(label) for label in labels]
    assert positions == sorted(positions)


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


def test_format_list_sorts_by_path() -> None:
    text = format_list([_env("project-z"), _env("project-a")], sort="path")

    _assert_order(text, "project-a", "project-z")


def test_format_list_sorts_by_size() -> None:
    text = format_list(
        [
            _env("small", size_bytes=1024),
            _env("unknown"),
            _env("large", size_bytes=1024 * 1024),
        ],
        sort="size",
    )

    _assert_order(text, "large", "small", "unknown")


def test_format_list_sorts_by_age() -> None:
    text = format_list(
        [
            _env("new", modified=datetime(2026, 2, 9, tzinfo=UTC)),
            _env("unknown"),
            _env("old", modified=datetime(2025, 2, 9, tzinfo=UTC)),
        ],
        sort="age",
    )

    _assert_order(text, "old", "new", "unknown")


def test_format_list_sorts_by_python_version() -> None:
    text = format_list(
        [
            _env("py310", python_version="3.10.0"),
            _env("missing", python_version=None),
            _env("py39", python_version="3.9.18"),
        ],
        sort="python",
    )

    _assert_order(text, "py39", "py310", "missing")


def test_format_report_uses_requested_sort_order() -> None:
    result = _scan_result(
        [
            _env("small", size_bytes=1024),
            _env("large", size_bytes=1024 * 1024),
        ]
    )

    text = format_report(result, sort="size", deep=True)

    _assert_order(text, "large", "small")


def test_format_report_show_artifact_details_false() -> None:
    """Test that artifact details are hidden by default."""
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

    text = format_report(result, show_artifact_details=False)

    assert "ARTIFACT DETAILS" in text
    assert "hidden by default" in text
    assert "run with --show-artifacts" in text.lower()


def test_format_report_show_artifact_details_true() -> None:
    """Test that artifact details are shown when flag is enabled."""
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

    text = format_report(result, show_artifact_details=True)

    assert "ARTIFACTS" in text
    assert "hidden by default" not in text
