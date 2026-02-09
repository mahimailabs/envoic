from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, TypedDict, cast, overload


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


EnvTypeValue = Literal["venv", "conda", "dotenv_dir", "unknown"]


class EnvInfoDict(TypedDict):
    path: str
    env_type: EnvTypeValue
    python_version: str | None
    size_bytes: int | None
    created: str | None
    modified: str | None
    package_count: int | None
    is_stale: bool
    has_pyvenv_cfg: bool
    signals: list[str]


class ScanResultDict(TypedDict):
    scan_path: str
    scan_depth: int
    duration_seconds: float
    environments: list[EnvInfoDict]
    total_size_bytes: int
    hostname: str
    timestamp: str


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


def _to_serializable_dict(data: ScanResult | EnvInfo) -> dict[str, Any]:
    return cast(dict[str, Any], _serialize_value(asdict(data)))


@overload
def to_serializable_dict(data: EnvInfo) -> EnvInfoDict: ...


@overload
def to_serializable_dict(data: ScanResult) -> ScanResultDict: ...


def to_serializable_dict(data: EnvInfo | ScanResult) -> EnvInfoDict | ScanResultDict:
    serialized = _to_serializable_dict(data)
    return cast(EnvInfoDict | ScanResultDict, serialized)
