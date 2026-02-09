from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class EnvType(str, Enum):
    VENV = "venv"
    CONDA = "conda"
    DOTENV_DIR = "dotenv_dir"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class EnvInfo:
    path: Path
    env_type: EnvType
    python_version: str | None = None
    size_bytes: int | None = None
    created: datetime | None = None
    modified: datetime | None = None
    package_count: int | None = None
    is_stale: bool = False
    has_pyvenv_cfg: bool = False
    signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    scan_path: Path
    scan_depth: int
    duration_seconds: float
    environments: list[EnvInfo]
    total_size_bytes: int
    hostname: str
    timestamp: datetime


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(inner) for key, inner in value.items()}
    return value


def to_serializable_dict(data: ScanResult | EnvInfo) -> dict[str, Any]:
    return _serialize_value(asdict(data))
